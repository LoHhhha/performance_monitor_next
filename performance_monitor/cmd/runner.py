import atexit
import os
import platform
import time
import argparse

from performance_monitor import __version__
from . import tools, settings
from .combiner import Combiner

if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-ft", "--flush_time", type=float, default=0.8)
    arguments.add_argument("--exclude-general-gpu", action="store_true", default=False)
    arguments.add_argument("--exclude-nvidia-gpu", action="store_true", default=False)
    args = arguments.parse_args()

    print(f"Package: performance_monitor-{__version__}")
    print(f"OS: {platform.platform()}")

    settings.reset(os.get_terminal_size().columns)

    combiner = Combiner(
        general_gpu_enable=not args.exclude_general_gpu,
        nv_gpu_enable=not args.exclude_nvidia_gpu,
    )

    # close all after unexpected exit
    atexit.register(combiner.close)

    print("\033[?25l")
    while True:
        # if display failed, we will clear the screen and try to display again
        if tools.info_display(combiner.get_info()):
            time.sleep(args.flush_time)
