class FrameDisplayHeaders:
    """
    Class that encapsulates the various header properties for the frame's display
    """

    def __init__(self, frame_display):
        self.frame_display = frame_display

    def set_line_height(self, line_height: int = 60):
        if line_height < 0:
            raise ValueError("line_height cannot be less than 0")
        self.frame_display.line_height = line_height

    def set_char_width(self, char_width: int = 4):
        self.frame_display.char_width = char_width

    def get_text_width(self, text: str) -> int:  # output in pixels
        # Width is affected by char_width property
        return self.frame_display.getTextWidth(text)

    def get_text_height(self, text: str) -> int:  # output in pixels
        # Height is affected by line_height property
        return self.frame_display.getTextHeight(text)

    def wrap_text(self, text: str, max_width: int) -> str:
        # Does this by inserting line breaks at space characters,
        # returning a string with extra ‘\n’ characters where line wrapping is needed.
        return self.frame_display.wrapText(text, max_width)
