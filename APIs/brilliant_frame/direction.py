class Direction:
    """
    Class that encapsulates the parameters of the frame's orientation.
    """

    def __init__(self, roll=0.0, pitch=0.0, heading=0.0, amplitude=0.0):
        # Set the initial values using the setter methods to ensure validation
        self.roll = roll
        self.pitch = pitch
        self.heading = heading
        self.amplitude = amplitude

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, value):
        if value < -180 or value > 180:
            raise ValueError("Roll must be between -180 and 180 degrees.")
        self._roll = value

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        if value < -180 or value > 180:
            raise ValueError("Pitch must be between -180 and 180 degrees.")
        self._pitch = value

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        if value < 0 or value > 360:
            raise ValueError("Heading must be between 0 and 360 degrees.")
        self._heading = value

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        if value < 0:
            raise ValueError("Amplitude must be greater than or equal to 0.")
        self._amplitude = value

    def __repr__(self):
        return (f"Direction(roll={self._roll}, pitch={self._pitch}, heading={self._heading}, "
                f"amplitude={self._amplitude})")


if __name__ == '__main__':
    direction = Direction(0, -200, 0, 0)  # Result: Validation error
