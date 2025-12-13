import os
import time
import argparse

from ..utils import tools, settings
from ..cmd.combiner import Combiner

if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-ft", "--flush_time", default=0.8)
    arguments.add_argument("--exclude-general-gpu", action="store_true", default=False)
    arguments.add_argument("--exclude-nvidia-gpu", action="store_true", default=False)
    args = arguments.parse_args()

    settings.reset(os.get_terminal_size().columns)

    combiner = Combiner(
        general_gpu_enable=not args.exclude_general_gpu,
        nv_gpu_enable=not args.exclude_nvidia_gpu,
    )

    print("\033[?25l")
    while True:
        tools.info_display(combiner.get_info())
        time.sleep(args.flush_time)
