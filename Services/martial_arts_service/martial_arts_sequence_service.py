import random
from .common_sequences import SEQUENCE_1, SEQUENCE_2
from .martial_arts_keys import MA_SEQUENCE_DATA


class MartialArtsSequenceService:
    """
    The MartialArtsSequenceService is responsible for generating and sending random sequences of martial arts moves to
    the user during a training session.
    """

    def __init__(self, martial_arts_service) -> None:
        self.martial_arts_service = martial_arts_service
        self.sequence_pool = [SEQUENCE_1, SEQUENCE_2]

    def generate_next_sequence(self) -> None:
        # Check if the sequence pool is not empty
        if not self.sequence_pool:
            return

        # Choose a random index from the sequence pool
        random_index = random.randint(0, len(self.sequence_pool) - 1)

        # Get the sequence at the randomly chosen index
        next_sequence = self.sequence_pool[random_index]
        self.martial_arts_service.send_to_component(websocket_message=next_sequence,
                                                    websocket_data_type=MA_SEQUENCE_DATA)
