import os
from collections import defaultdict
from typing import List, Optional, Tuple
import tabulate
import math
import re
from wcwidth import wcwidth

from . import settings

tabulate.PRESERVE_WHITESPACE = True

_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def get_display_width(s: str):
    plain = _ANSI_ESCAPE_RE.sub("", s)
    width = 0
    for ch in plain:
        w = wcwidth(ch)
        width += 0 if w < 0 else w
    return width


def ljust_display(s: str, target_width: int):
    pad = max(0, target_width - get_display_width(s))
    return s + " " * pad


def rjust_display(s: str, target_width: int):
    pad = max(0, target_width - get_display_width(s))
    return " " * pad + s


def get_title(s: str):
    colored = settings.colors.title + s + settings.colors.END
    width = settings.max_key_len + settings.max_val_len + settings.margin_len
    return ljust_display(colored, width)


def get_table(info_list: List):
    return tabulate.tabulate(info_list, tablefmt=settings.tabulate_table_style)


def get_sum(values: List):
    return sum(values)


def get_max(values: List):
    return max(values)


def get_min(values: List):
    return min(values)


def get_avg(values: List):
    return get_sum(values) / len(values)


def get_clipped_string(s: str, max_len: int):
    if get_display_width(s) <= max_len:
        return s
    clip_width = get_display_width(settings.clip_display)
    if max_len <= clip_width:
        return ""
    assert clip_width <= max_len
    keep_width = max_len - clip_width
    res = ""
    cur = 0
    for ch in s:
        ch_width = wcwidth(ch)
        ch_width = 0 if ch_width < 0 else ch_width
        if cur + ch_width > keep_width:
            break
        res += ch
        cur += ch_width
    return res + settings.clip_display


def wrap_color_by_threshold(s: str, val: int, l0: int = 80, l1: int = 50):
    if val >= l0:
        return settings.colors.warning + s + settings.colors.END
    elif val >= l1:
        return settings.colors.hint + s + settings.colors.END
    return s


def get_pair_display(value, other_value, postfix="", sep: str = "()"):
    left = f"{other_value}{postfix}"
    right = f"{value}{postfix}"

    n = (
        settings.max_val_len
        - get_display_width(left)
        - get_display_width(right)
        - min(get_display_width(sep), 2)
    )
    if n < 0:
        no_left_width = get_display_width(right) + min(get_display_width(sep), 2)
        left = get_clipped_string(left, settings.max_val_len - no_left_width)
        n = settings.max_val_len - get_display_width(left) - no_left_width
    if n < 0:
        return ""

    l_sep = sep[0] if len(sep) > 0 else ""
    r_sep = sep[1] if len(sep) > 1 else ""
    return f"{l_sep}{left}{r_sep}{' ' * max(0, n)}{right}"


def get_rate_display(usage: float):
    return (
        settings.left_block
        + wrap_color_by_threshold(
            settings.rate_display[(min(100, max(0, math.ceil(usage))) + 4) // 5],
            int(usage),
        )
        + settings.right_block
        + f"{int(usage):4d}"
        + settings.rate_postfix
    )


def get_temperature_display(temperature: float, temperature_id: str):
    if not hasattr(get_temperature_display, "prev_temperature_info_dict"):
        get_temperature_display.prev_temperature_info_dict = defaultdict(
            lambda: [" " for _ in range(settings.block_len)]
        )
    prev_info = get_temperature_display.prev_temperature_info_dict[temperature_id]
    if len(prev_info) != settings.block_len:
        prev_info = get_temperature_display.prev_temperature_info_dict[
            temperature_id
        ] = [" " for _ in range(settings.block_len)]

    n = len(settings.temp_display) - 1
    # <=30 is the lowest, >=100 is the highest
    cur_temperature_block = settings.temp_display[
        min(max(0, int((temperature - 30) * n / 70)), n)
    ]

    prev_info.insert(0, cur_temperature_block)
    prev_info.pop()

    return (
        settings.left_block
        + str.join("", prev_info)
        + settings.right_block
        + f"{int(temperature):4d}"
        + settings.temperature_postfix
    )


def get_simple_usage_display(u: int, add_color: bool = True):
    usage_format = "{:2d}%"
    u = max(0, min(100, u))
    u = int(u * 0.99)
    n = len(settings.usage_display) - 1
    if not add_color:
        return (
            settings.each_left_block
            + settings.usage_display[int((u / 99) * n)]
            + usage_format.format(u)
            + settings.each_right_block
        )
    return (
        settings.each_left_block
        + wrap_color_by_threshold(settings.usage_display[int((u / 99) * n)], u)
        + usage_format.format(u)
        + settings.each_right_block
    )


def get_each_usage(cpu_usage: List, usage_each_line: Optional[int] = None):
    # Warning: not need to clip strings in this function, since it has many lines.

    usage_len = len(get_simple_usage_display(0, add_color=False))

    if usage_each_line is None:
        usage_each_line = max(1, (settings.max_val_len + 1) // (usage_len + 1))
    assert usage_each_line > 0

    def get_line(usage_bag: List):
        block_len = (
            (
                (settings.max_val_len - (usage_len * usage_each_line))
                // (usage_each_line - 1)
            )
            if usage_each_line > 1
            else 0
        )
        if len(usage_bag) == 0:
            return ""
        line = (" " * block_len).join(usage_bag)
        return ljust_display(line, settings.max_val_len)

    n = len(cpu_usage)
    res = ""
    cur = []
    for i in range(0, n):
        if len(cur) >= usage_each_line:
            res += get_line(cur)
            res += "\n"
            cur = []
        cur.append(get_simple_usage_display(int((cpu_usage[i]))))
    res += get_line(cur)
    return res


def get_key_string(_key: str, clip_key: bool = True):
    if clip_key:
        _key = get_clipped_string(_key, settings.max_key_len)
    return ljust_display(_key, settings.max_key_len)


def get_val_string(_val: str, clip_val: bool = True):
    if clip_val:
        _val = get_clipped_string(_val, settings.max_val_len)
    return rjust_display(_val, settings.max_val_len)


def get_tuple(_key: str, _val: str, clip_key: bool = True, clip_val: bool = True):
    return get_key_string(_key, clip_key), get_val_string(_val, clip_val)


def info_display(info: List[Tuple[str, List[Tuple[str, str]]]]):
    if not hasattr(info_display, "pre_terminal_col_size"):
        info_display.pre_terminal_col_size = 0
        info_display.pre_terminal_row_size = 0

    out = "\n".join(f"{get_title(group)}\n{tables}" for group, tables in info)

    cur_terminal_col_size = os.get_terminal_size().columns
    cur_terminal_row_size = os.get_terminal_size().lines

    print("\x1b[0;0H", end="")
    if (
        cur_terminal_row_size != info_display.pre_terminal_row_size
        or cur_terminal_col_size != info_display.pre_terminal_col_size
    ):
        info_display.pre_terminal_col_size = cur_terminal_col_size
        info_display.pre_terminal_row_size = cur_terminal_row_size
        settings.reset(cur_terminal_col_size)

    print(out, end="")
