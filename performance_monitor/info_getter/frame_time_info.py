import csv
import os
import statistics
import subprocess
import threading
import time
import ctypes
from ctypes import wintypes
from typing import Annotated, Optional

from ..third_party import PM_exe_path
from .hardware import GeneralHardware


class FrameTimeInformation(GeneralHardware):
    fps: Annotated[Optional[int], GeneralHardware.SensorValue]
    fps_1_low: Annotated[Optional[int], GeneralHardware.SensorValue]
    target_process: Annotated[Optional[str], GeneralHardware.SensorValue]

    _present_mon_process: subprocess.Popen[str]
    _collect_thread: threading.Thread

    _collect_thread_start_event: threading.Event
    _collect_thread_exit_event: threading.Event

    _data_lock: threading.Lock
    _inner_fps: Optional[float]
    _inner_1_low_fps: Optional[float]
    _inner_samples: int

    def _reset_data(self):
        self._inner_fps = None
        self._inner_1_low_fps = None
        self._inner_samples = 0

    def __init__(self):
        self.clear()
        self.target_process = None

        print("FrameTimeInformation initialization:")
        self._present_mon_process = None
        self._data_lock = threading.Lock()
        self._collect_thread_start_event = threading.Event()
        self._collect_thread_exit_event = threading.Event()
        self._collect_thread = threading.Thread(
            target=self._collect_worker, daemon=True
        )
        self._collect_thread.start()
        print("\tFrameTime Collector Thread started")
        with self._data_lock:
            self._reset_data()
        self._update_target_process(self._pick_target_process())
        print(f"\tMonitoring target process: {self.target_process}")

    __ptp_last_pid = None
    __ptp_last_process_name = None
    __ptp_last_update_time = 0

    def _pick_target_process(self, default_process: str = "dwm.exe") -> str:
        if time.monotonic() - self.__ptp_last_update_time < 2.0:
            return self.__ptp_last_process_name

        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return self.target_process or default_process

        process_id = wintypes.DWORD(0)
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        if process_id.value == 0:
            return self.target_process or default_process

        if self.__ptp_last_pid == process_id.value:
            return self.__ptp_last_process_name

        process_handle = ctypes.windll.kernel32.OpenProcess(
            0x1000, False, process_id.value
        )
        if not process_handle:
            return self.target_process or default_process

        try:
            image_name_buf = ctypes.create_unicode_buffer(1024)
            image_name_size = wintypes.DWORD(len(image_name_buf))
            ok = ctypes.windll.kernel32.QueryFullProcessImageNameW(
                process_handle,
                0,
                image_name_buf,
                ctypes.byref(image_name_size),
            )
            if not ok:
                return self.target_process or default_process

            process_name = os.path.basename(image_name_buf.value).lower()
            if not process_name:
                return self.target_process or default_process

            self.__ptp_last_pid = process_id.value
            self.__ptp_last_process_name = process_name
            self.__ptp_last_update_time = time.monotonic()
            return process_name
        finally:
            ctypes.windll.kernel32.CloseHandle(process_handle)

    def _collect_worker(self):
        frame_times_ms: list[float] = []

        def _update():
            frame_times_ms.sort()
            if frame_times_ms:
                frame_ms = statistics.fmean(frame_times_ms)
                low_1_percent = frame_times_ms[int(0.99 * (len(frame_times_ms) - 1)) :]
                low_1_frame_ms = sum(low_1_percent) / len(low_1_percent)
            else:
                frame_ms = -1
                low_1_frame_ms = -1

            fps = 1000.0 / frame_ms if frame_ms > 0 else None
            fps_1_low = 1000.0 / low_1_frame_ms if low_1_frame_ms > 0 else None
            samples = (
                len(frame_times_ms)
                if (fps is not None) and (fps_1_low is not None)
                else 0
            )

            with self._data_lock:
                if samples == 0:
                    self._reset_data()
                elif self._inner_samples > 0:
                    self._inner_fps = (
                        self._inner_fps * self._inner_samples + fps * samples
                    ) / (self._inner_samples + samples)
                    self._inner_1_low_fps = (
                        self._inner_1_low_fps * self._inner_samples
                        + fps_1_low * samples
                    ) / (self._inner_samples + samples)
                    self._inner_samples += samples
                else:
                    self._inner_fps = fps
                    self._inner_1_low_fps = fps_1_low
                    self._inner_samples = samples

            frame_times_ms.clear()

        while True:
            if self._collect_thread_exit_event.is_set():
                break

            if not self._collect_thread_start_event.is_set():
                self._collect_thread_start_event.wait()
                continue

            # wait for present_mon to start and output data
            if (self._present_mon_process is None) or (
                self._present_mon_process.stdout is None
            ):
                time.sleep(0.2)
                continue

            reader = csv.DictReader(self._present_mon_process.stdout)
            # not ready yet
            if not reader.fieldnames:
                time.sleep(0.2)
                continue

            frame_time_column = None
            for field in reader.fieldnames:
                if "msbetweenpresents" in field.lower():
                    frame_time_column = field
                    break
            if frame_time_column is None:
                raise RuntimeError("Cannot find frame time column in PresentMon output")

            window_start = time.monotonic()
            frame_times_ms.clear()
            try:
                for row in reader:
                    if (
                        not self._collect_thread_start_event.is_set()
                    ) or self._collect_thread_exit_event.is_set():
                        break

                    value = row.get(frame_time_column)
                    if value:
                        try:
                            frame_times_ms.append(float(value))
                        except ValueError:
                            pass

                    now = time.monotonic()
                    if now - window_start < 0.2:
                        continue

                    _update()
                    window_start = now
            except Exception as _:
                pass

    def _update_target_process(self, target_process: Optional[str]):
        if self.target_process == target_process:
            return
        self.target_process = target_process

        self._collect_thread_start_event.clear()
        with self._data_lock:
            self._reset_data()

        if self._present_mon_process is not None:
            self._present_mon_process.terminate()
            self._present_mon_process.wait()
            self._present_mon_process = None

        if self.target_process is None:
            return

        self._present_mon_process = subprocess.Popen(
            [
                PM_exe_path,
                "--process_name",
                self.target_process,
                "--output_stdout",
                "--no_console_stats",
                "--exclude_dropped",
                "--v1_metrics",
                "--stop_existing_session",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1,
        )
        self._collect_thread_start_event.set()

    def clear(self):
        self.fps_1_low = None
        self.fps = None

    def dispose(self):
        if self._present_mon_process is not None:
            self._present_mon_process.terminate()
            self._present_mon_process.wait()
            self._present_mon_process = None

        self._collect_thread_exit_event.set()
        self._collect_thread_start_event.set()  # in case it's waiting
        self._collect_thread.join(timeout=5.0)

    def update(self):
        if not self._collect_thread.is_alive():
            raise RuntimeError("FrameTime collection thread has stopped unexpectedly")

        with self._data_lock:
            self.fps = int(self._inner_fps) if self._inner_fps is not None else None
            self.fps_1_low = (
                int(self._inner_1_low_fps)
                if self._inner_1_low_fps is not None
                else None
            )
            self._reset_data()

        self._update_target_process(self._pick_target_process())
