import numpy
import base_keys
from DataFormat import datatypes_helper
from Utilities import logging_utility, image_utility, time_utility
from base_component import BaseComponent
from Services.aiget_service import aiget_db
from . import aiget_keys
from .aiget_data_handler import build_aiget_data
from .aiget_service_config import AigetConfig
from .aiget_llm import AigetAI

_logger = logging_utility.setup_logger(__name__)


class AigetService(BaseComponent):
    """
    This service helps users gain new knowledge in their surroundings.
    """

    SUPPORTED_DATATYPES = {
        "AIGET_DATA",
        "AIGET_DATA_REQUEST",
        "AIGET_RESET_REQUEST",
        "GAZE_POINTING_DATA",
        "SPEECH_INPUT_DATA",
    }

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.aiget_ai = AigetAI()
        self.last_frame = None
        self.last_gaze_position = None
        self.last_gaze_time = None
        self.gaze_mode = None
        self.last_aiget_time = 0

    def run(self, raw_data: dict) -> None:
        """
        This function is responsible for running the aiget service.
        Parameters:
        ----------
        raw_data: dict
        """
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]
            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            self._handle_websocket_data(datatype, data)

        # set the camera data frame
        elif origin == base_keys.CAMERA_WIDGET:
            self._handle_camera_data(raw_data)

    def _handle_websocket_data(self, socket_data_type, decoded_data) -> None:
        """
        Process incoming websocket data based on the specified datatype.

        Args:
            socket_data_type (str): The type of data received via websocket.
            decoded_data (object): The decoded data object corresponding to the datatype.

        Returns:
            None
        """
        _logger.debug("Aiget Service: {datatype}", datatype=socket_data_type)

        if socket_data_type == aiget_keys.AIGET_DATA_REQUEST:
            self._handle_aiget_request(decoded_data)
        elif socket_data_type == aiget_keys.AIGET_RESET_REQUEST:
            self._handle_reset_request()
        elif socket_data_type == aiget_keys.GAZE_POINTING_DATA:
            self._handle_gaze_point(decoded_data)
        elif socket_data_type == aiget_keys.SPEECH_INPUT_DATA:
            self._handle_aiget_questions(decoded_data)
        else:
            _logger.error("Unknown websocket type {type} received in Aiget Service", type=socket_data_type)

    def _handle_aiget_questions(self, question_request) -> None:
        """
        Handle user questions and generate corresponding answers.

        Args:
            question_request (object): The user's speech from SpeechData

        Returns:
            None
        """

        speech = question_request.voice
        _logger.debug("[RX] Websocket: Speech= {speech}", speech=speech)

        last_update_time = self.last_aiget_time
        self.last_aiget_time = time_utility.get_current_millis()

        try:
            recent_knowledge = aiget_db.get_recent_knowledge(AigetConfig.NUMBER_OF_NEW_KNOWLEDGE_ROWS)
            formatted_prompt = f"user_question: {speech}\n" f"recent_knowledge: {recent_knowledge}"
            image = self._get_latest_image()
            answer, summarized_answer = self.aiget_ai.generate_answers(
                user_prompt=formatted_prompt, image_png_bytes=image
            )
            _logger.debug("AiGet Answer: {answer}, Summary: {summarized_answer}", answer=answer,
                          summarized_answer=summarized_answer)

            self.last_aiget_time = time_utility.get_current_millis()

            display_duration = AigetConfig.AIGET_DISPLAY_SECONDS
            self._send_websocket_aiget_data(
                text=summarized_answer, image=image, audio_text=answer, display_duration=display_duration
            )

        except Exception:
            self.last_aiget_time = last_update_time
            _logger.error("Error handling Aiget questions")

    def _handle_aiget_request(self, request_data) -> None:
        """
        Process an Aiget data request, generate content, save knowledge, and send response.

        Args:
            request_data (object): The request data object containing details for generating Aiget data.

        Returns:
            None
        """
        _logger.info("Aiget Request Data: {detail}", detail=request_data.detail)

        last_update_time = self.last_aiget_time

        if (time_utility.get_current_millis() - self.last_aiget_time) >= AigetConfig.AIGET_REQUEST_GAP_MILLIS:
            self.last_aiget_time = time_utility.get_current_millis()

            try:
                image = self._get_latest_image()
                aiget_content, summarized_content = self.get_aiget_content_with_summary()
                display_duration = AigetConfig.AIGET_DISPLAY_SECONDS

                # Save aiget content to the database
                aiget_db.save_knowledge(aiget_content)

                self.last_aiget_time = time_utility.get_current_millis()

                self._send_websocket_aiget_data(
                    text=summarized_content, image=image, audio_text=aiget_content, display_duration=display_duration
                )
            except (KeyError, AttributeError, ValueError):
                self.last_aiget_time = last_update_time
                _logger.exception("Error getting aiget data")

    def _send_websocket_aiget_data(
            self, text: str = "", image: bytes = None, audio_text: str = "", display_duration: int = 0
    ) -> None:
        """
        Build and send Aiget data (text, image, audio, display duration) via WebSocket.

        Args:
            text (str): The textual content to send.
            image (Optional[bytes]): PNG image data as bytes; if None, no image is sent.
            audio_text (str): Text to be converted to audio or used as audio description.
            display_duration (int): Duration in seconds for which the content should be displayed.

        Returns:
            None
        """
        websocket_aiget_data = build_aiget_data(
            text=text, image=image, audio_text=audio_text, display_duration=display_duration
        )
        super().send_to_component(websocket_message=websocket_aiget_data)
        _logger.info(
            "Sending Aiget Data (Text: {text}, Image, Audio: {audio_text}, Display_duration: {display_duration} sent to Aiget Scene",
            text=text,
            image=image,
            audio_text=audio_text,
            display_duration=display_duration,
        )

    def _handle_reset_request(self) -> None:
        """
        Handle a reset request by clearing the last frame and sending an empty Aiget data response.

        Returns:
            None
        """
        _logger.debug("Received reset request")
        self.last_frame = None
        self._send_websocket_aiget_data(text="", image=None, audio_text="", display_duration=0)

    def _handle_camera_data(self, raw_data: dict) -> None:
        """
        Store the latest camera frame and its dimensions in shared memory.

        Args:
            raw_data (dict): Dictionary containing camera frame data and metadata.

        Returns:
            None
        """
        super().set_memory_data(base_keys.CAMERA_FRAME, raw_data[base_keys.CAMERA_FRAME])
        super().set_memory_data(base_keys.CAMERA_FRAME_WIDTH, raw_data[base_keys.CAMERA_FRAME_WIDTH])
        super().set_memory_data(base_keys.CAMERA_FRAME_HEIGHT, raw_data[base_keys.CAMERA_FRAME_HEIGHT])

    def _get_latest_image(self) -> bytes:
        """
        Retrieve the latest camera frame from memory and convert it to PNG bytes.

        Returns:
            Optional[bytes]: PNG encoded image bytes if frame exists, otherwise None.
        """
        frame: numpy.ndarray = super().get_memory_data(base_keys.CAMERA_FRAME)
        if frame is None:
            _logger.warning("Camera frame is None, cannot send image.")
            return None
        return image_utility.get_png_image_bytes(frame)

    def get_aiget_content_with_summary(self) -> tuple[str, str]:
        """
        Generate both Aiget content and its summarized version.

        Returns:
            Tuple[str, str]: Generated content and its summary as strings.
        """
        aiget_content, summarized_content = "", ""

        try:
            # Get the current frame from memory
            frame = super().get_memory_data(base_keys.CAMERA_FRAME)
            if frame is None:
                raise RuntimeError("Camera frame is None, cannot generate content")

            # Convert the frame to PNG bytes
            image_png_bytes = image_utility.get_png_image_bytes(frame)
            # Save the frame temporarily
            self.last_frame = frame
            image_utility.save_image_bytes("temp.png", image_png_bytes)

            # Get gaze mode
            gaze_mode = self.gaze_mode if self.gaze_mode else "Quick Browse"
            user_prompt = f"Generate new knowledge based on gaze mode: {gaze_mode}."

            aiget_content, summarized_content = self.aiget_ai.generate_content(
                user_prompt=user_prompt,
                image_png_bytes=image_png_bytes,
            )

            if not aiget_content:
                raise RuntimeError("Generated content is empty")

        except (RuntimeError, ValueError, KeyError, AttributeError):
            _logger.exception("Error in content generation")

        return aiget_content, summarized_content

    def _handle_gaze_point(self, gaze_point_data):
        """
        Process gaze pointing data to update the gaze mode based on velocity.

        Args:
            gaze_point_data (object): An object containing gaze coordinates with attributes `world_x` and `world_y`.

        Returns:
            Optional[str]: The gaze mode ("Saccade", "Quick Browse", "Focus") or None if gaze position is initialized.
        """
        # Extract camera-space gaze position (x, y) from the client data
        current_position = numpy.array([gaze_point_data.world_x, gaze_point_data.world_y])

        # If this is the first gaze point, initialize and return
        if self.last_gaze_position is None:
            self.last_gaze_position = current_position
            self.last_gaze_time = time_utility.get_current_millis() / 1000
            return None

        # Calculate the time difference
        current_time = time_utility.get_current_millis() / 1000
        time_diff = current_time - self.last_gaze_time

        # Calculate the distance between current and last gaze positions
        distance = numpy.linalg.norm(current_position - self.last_gaze_position)

        # Calculate velocity (distance moved per second)
        velocity = distance / time_diff

        # Classify based on velocity and time difference
        if velocity > AigetConfig.SACCADE_VELOCITY_MARGIN:  # Rapid movement -> Saccade
            self.gaze_mode = "Saccade"
        elif velocity > AigetConfig.QUICK_BROWSE_VELOCITY_MARGIN:  # Moderate speed -> Quick Browse
            self.gaze_mode = "Quick Browse"
        else:  # Low velocity -> Focused
            self.gaze_mode = "Focus"

        # Update the gaze state
        self.last_gaze_position = current_position
        self.last_gaze_time = current_time

        _logger.debug(f"Gaze Mode: {self.gaze_mode}")
        return self.gaze_mode
