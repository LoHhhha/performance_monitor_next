import os
from collections import defaultdict
import tabulate
import math

from . import settings

tabulate.PRESERVE_WHITESPACE = True


def get_title(s: str):
    return settings.color_chose[0] + s + settings.color_chose[1] + ' ' * (settings.max_key_len + settings.max_val_len + settings.margin_len - len(s))


def get_table(info_list: list):
    return tabulate.tabulate(info_list, tablefmt=settings.tabulate_table_style)


def get_sum(values: list):
    return sum(values)


def get_max(values: list):
    return max(values)


def get_min(values: list):
    return min(values)


def get_avg(values: list):
    return get_sum(values) / len(values)


def get_max_display(value, max_value, postfix=''):
    left = f"{max_value}{postfix}"
    right = f"{value}{postfix}"
    n = settings.max_val_len - len(left) - len(right) - 2
    return f"({left}){' ' * n}{right}"


def get_rate_display(usage: float):
    usage_str = f"{usage:.0f}"
    return settings.left_block + get_diff_color(
        settings.rate_display[(min(100, max(0, math.ceil(usage))) + 4) // 5],
        int(usage)
    ) + settings.right_block + ' ' * (4 - len(usage_str)) + usage_str + settings.rate_postfix


def get_temperature_display(temperature: float, temperature_id: str):
    if not hasattr(get_temperature_display, "prev_temperature_info_dict"):
        get_temperature_display.prev_temperature_info_dict = \
            defaultdict(lambda: [' ' for _ in range(settings.block_len)])
    prev_info = get_temperature_display.prev_temperature_info_dict[temperature_id]
    if len(prev_info) != settings.block_len:
        prev_info = get_temperature_display.prev_temperature_info_dict[temperature_id] = [' ' for _ in range(settings.block_len)]
    
    n = len(settings.temp_display) - 1
    temperature_str = str(int(temperature))
    if temperature < 30:
        cur_temperature_block = ' '
    elif temperature <= 100:
        cur_temperature_block = settings.temp_display[int((temperature - 30) * n / 70)]
    else:
        cur_temperature_block = '█'
    prev_info.insert(0, cur_temperature_block)
    prev_info.pop()
    return settings.left_block + str.join('', prev_info) + settings.right_block + ' ' * (
            4 - len(temperature_str)) + temperature_str + settings.temperature_postfix


def get_each_usage(cpu_usage: list, usage_each_line:int=4):
    assert usage_each_line > 0
    usage_len = len(get_simple_usage_display(0, add_color=False))
    
    def get_line(usage_bag:list):
        block_len = (settings.max_val_len - (usage_len * usage_each_line)) // (usage_each_line - 1)
        if len(usage_bag) == 0:
            return ""
        line = (' '* block_len).join(usage_bag)
        return line.ljust(settings.max_val_len)
    
    n = len(cpu_usage)
    res = ""
    cur = []
    for i in range(0, n):
        if len(cur) >= usage_each_line:
            res += get_line(cur)
            res += '\n'
            cur = []
        cur.append(get_simple_usage_display(int(cpu_usage[i])))
    res += get_line(cur)
    return res


def get_diff_color(s: str, val: int, l0: int = 80, l1: int = 50):
    if val >= l0:
        return "\033[33m" + s + "\033[0m"
    elif val >= l1:
        return "\033[1;33m" + s + "\033[0m"
    return "\033[37m" + s + "\033[0m"


def get_simple_usage_display(u: int, add_color: bool = True):
    usage_format = "{:2d}%"
    u = int(u * 0.99)
    n = len(settings.usage_display) - 1
    if not add_color:
        return settings.each_left_block + settings.usage_display[int((u / 99) * n)] + usage_format.format(u) + settings.each_right_block
    return settings.each_left_block + get_diff_color(settings.usage_display[int((u / 99) * n)], u) + usage_format.format(u) + settings.each_right_block


def get_tuple(_key: str, _val: str):
    return get_key_string(_key), get_val_string(_val)


def get_key_string(_key: str):
    return _key + ' ' * (settings.max_key_len - len(_key))


def get_val_string(_val: str):
    return ' ' * (settings.max_val_len - len(_val)) + _val


def info_display(info: list):
    if not hasattr(info_display, "pre_terminal_col_size"):
        info_display.pre_terminal_col_size = 0
        info_display.pre_terminal_row_size = 0

    out = ""
    for (idx, (group, tables)) in enumerate(info):
        out += get_title(group) + '\n'
        out += tables + '\n'

    # will sub one '\n' later
    cnt = -1
    for c in out:
        if c == '\n':
            cnt += 1

    cur_terminal_col_size = os.get_terminal_size().columns
    cur_terminal_row_size = os.get_terminal_size().lines

    print('\x1B[0;0H', end='')
    if (
            cur_terminal_row_size != info_display.pre_terminal_row_size or
            cur_terminal_col_size != info_display.pre_terminal_col_size
    ):
        info_display.pre_terminal_col_size = cur_terminal_col_size
        info_display.pre_terminal_row_size = cur_terminal_row_size
        settings.reset(cur_terminal_col_size)

    print(out[0:-1], end='')
