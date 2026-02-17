color_chose = ["\033[33m", "\033[0m"]

max_key_len = 15
max_val_len = 27
margin_len = 7  # 7 is table format as "| key | value |"

block_margin_len = 7  # 7 is the length of usage format like "[xxx]  45%"
block_len = max_val_len - block_margin_len
rate_display = [
    "█" * ((block_len * i) // 20) + " " * (block_len - (block_len * i) // 20)
    for i in range(21)
]

temp_display = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
usage_display = [" ", "▏", "▎", "▎", "▌", "▋", "▊", "▉", "█"]

time_fmt = "%Y/%m/%d %H:%M:%S"

tabulate_table_style = "pretty"
byte2mb = 1024 * 1024
byte2kb = 1024
mb_postfix = "MiB"
mb_per_postfix = "MiBps"
kb_per_postfix = "KiBps"
power_postfix = "W"
rate_postfix = "%"
voltage_postfix = "V"
temperature_postfix = "C"
clock_postfix = "MHz"
fan_postfix = "RPM"
bound_sep = " of "
left_block = "|"
right_block = "|"
each_left_block = "["
each_right_block = "]"
clip_display = "…"


def reset(col_size: int):
    col_size -= margin_len
    global max_key_len, max_val_len, block_len, rate_display
    max_key_len = min(col_size // 3, 20)
    max_val_len = col_size - max_key_len

    block_len = max_val_len - block_margin_len
    rate_display = [
        "█" * ((block_len * i) // 20) + " " * (block_len - (block_len * i) // 20)
        for i in range(21)
    ]
