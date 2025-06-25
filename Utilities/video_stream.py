# initial source: https://github.com/Interactions-HSG/21-MT-JanickSpirig-HoloLens-ObjectDetection/blob/master/modules/YoloModule/app/VideoStream.py


from __future__ import absolute_import
from threading import Thread, Event
from queue import Queue, Empty
import cv2
from Utilities import logging_utility

_DEFAULT_QUEUE_SIZE = 3
_QUEUE_PUT_TIMEOUT_SECONDS = 1.0
_QUEUE_GET_TIMEOUT_SECONDS = 1.0
_QUEUE_EMPTY_TIMEOUT_SECONDS = 0.1

_STOP_WAIT_TIMEOUT_SECONDS = 1.0

_logger = logging_utility.setup_logger(__name__)


class VideoStream:
    """
    This class reads all the video frames in a separate thread and always attempts to keeps only the latest frame in its
    queue to be grabbed by another thread
    """

    def __init__(self, path, queue_size=_DEFAULT_QUEUE_SIZE):
        _logger.info("=======================\r\nVideoStream::__init__()")
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        self.stop_event = Event()
        self.queue_size = queue_size
        self.Q = Queue(maxsize=queue_size)
        self.thread = None

        if not self.stream.isOpened():
            _logger.error("Failed to open video stream source.")
            raise IOError(f"Could not open video stream at path: {path}")

    def start(self):
        # start a thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        try:
            while not self.stop_event.is_set():
                if not self.Q.full():
                    (grabbed, frame) = self.stream.read()

                    # if the `grabbed` boolean is `False`, then we have
                    # reached the end of the video file
                    if not grabbed:
                        self.stop()
                        return

                    # Put frame in queue, with a timeout to prevent deadlocks
                    try:
                        self.Q.put(frame, timeout=_QUEUE_PUT_TIMEOUT_SECONDS)
                    except Exception as e:
                        _logger.exception(f"Failed to add frame to queue: {e}")
                        continue

                    # Clean the queue to keep only the latest frame
                    while self.Q.qsize() > 1:
                        try:
                            self.Q.get(timeout=_QUEUE_EMPTY_TIMEOUT_SECONDS)
                        except Empty:
                            # Queue emptied by another thread
                            break
                        except Exception as e:
                            _logger.exception(f"Error cleaning queue: {e}")
                            break
        except Exception as e:
            _logger.exception(f"Failed to read stream: {e}")
        finally:
            # Ensure resources are released
            self.stream.release()
            _logger.info("Video stream released")

    def read(self):
        try:
            return self.Q.get(timeout=_QUEUE_GET_TIMEOUT_SECONDS)
        except Empty:
            _logger.warning("Queue is empty, no frames available")
            return None
        except Exception as e:
            _logger.exception(f"Error reading from queue: {e}")
            return None

    def more(self):
        return self.Q.qsize() > 0 and not self.stopped

    def stop(self):
        _logger.info("Stopping video stream")
        self.stopped = True
        self.stop_event.set()

        # Clear the queue to prevent deadlocks
        while not self.Q.empty():
            try:
                self.Q.get(timeout=_QUEUE_EMPTY_TIMEOUT_SECONDS)
            except Empty:  # within 'timeout' seconds
                pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()
        if self.stream is not None:
            self.stream.release()

        # Wait for thread to complete
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=_STOP_WAIT_TIMEOUT_SECONDS)
