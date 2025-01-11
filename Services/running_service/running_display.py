from enum import Enum


class RunningDisplayPosition(Enum):
    """
    Enum representing various positions on the screen for displaying running data.
    """
    Top = 0
    TopLeft = 1
    TopCenter = 2
    TopRight = 3
    BottomLeftTop = 4
    BottomLeftBottom = 5
    BottomRight = 6
    SelectionLeft = 7
    SelectionRight = 8
    Unsupported = 9
