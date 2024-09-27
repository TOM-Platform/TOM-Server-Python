from Utilities import format_utility


def test_get_int():
    assert format_utility.get_int("10") == 10


def test_get_float():
    assert format_utility.get_float("10.0") == 10.0


def test_is_empty_if_empty():
    assert format_utility.is_empty("") == True


def test_is_empty_if_none():
    assert format_utility.is_empty(None) == True


def test_is_empty_if_not_empty():
    assert format_utility.is_empty("ANSDLKASNDL") == False


def test_get_text_inside_paranthesis_when_only_paranthesis():
    assert format_utility.get_text_inside_parentheses("[]") == ["[]"]


def test_get_text_inside_paranthesis_for_square_brackets():
    assert format_utility.get_text_inside_parentheses("[hi]") == ["[hi]"]


def test_get_text_inside_paranthesis_for_multiple_square_brackets():
    assert format_utility.get_text_inside_parentheses("[hi][again]") == [
        "[hi]", "[again]"]


def test_get_text_inside_paranthesis_when_no_paranthesis():
    assert format_utility.get_text_inside_parentheses("hi") == []


def test_get_text_inside_paranthesis_when_other_special_characters():
    assert format_utility.get_text_inside_parentheses("#hi#$%%") == []


def get_first_text_inside_paranthesis_without_paranthesis_for_square_brackets():
    assert format_utility.get_first_text_inside_parentheses_without_parentheses(
        "[hi]") == "hi"


def get_first_text_inside_paranthesis_without_paranthesis_when_only_paranthesis():
    assert format_utility.get_first_text_inside_parentheses_without_parentheses(
        "[]") == ""


def get_first_text_inside_paranthesis_without_paranthesis_when_multiple_square_brackets():
    assert format_utility.get_first_text_inside_parentheses_without_parentheses(
        "[hi][again]") == "hi"
