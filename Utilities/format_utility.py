# coding=utf-8

import re

KM_TO_M = 1000
MIN_TO_S = 60


def get_int(string_value):
    return int(string_value)


def get_float(string_value):
    return float(string_value)


def is_empty(string_value):
    return string_value is None or string_value == ""


def is_binary_data(data: str | bytes) -> bool:
    return isinstance(data, (bytes, bytearray))


def get_text_without_parentheses_text(text):
    return re.sub(r"[\(\[].*?[\)\]]", "", text)


def get_text_inside_parentheses(text):
    # return re.findall('\(.*?\)', text)
    return re.findall(r"[\(\[].*?[\)\]]", text)


def get_first_text_inside_parentheses_without_parentheses(text):
    # return re.findall('\(.*?\)', text)
    return re.findall(r"[\(\[].*?[\)\]]", text)[0].replace("[", "").replace("]", "")


def convert_m_s_to_min_km(speed_in_m_s):
    speed_in_min_km = 0
    if speed_in_m_s > 0:
        speed_in_min_km = KM_TO_M / (MIN_TO_S * speed_in_m_s)
    return speed_in_min_km


def truncate_text(text, max_length):
    return text if len(text) <= max_length else text[:max_length] + "..."
