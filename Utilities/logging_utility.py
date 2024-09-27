import shutil
import os
import sys
import logbook
from logbook import Logger, RotatingFileHandler, StreamHandler

_MAX_LOG_SIZE = 50 * 1024 * 1024  # 50 MB
_MAX_BACKUP_COUNT = 2
_DEFAULT_LOG_LEVEL = logbook.DEBUG
_DEFAULT_LOG_FILE = 'logs/logbook.log'
_DEFAULT_LOGGER_NAME = 'DefaultLogger'
_DEFAULT_LOG_FORMAT = '{record.time:%Y-%m-%d %H:%M:%S}|{record.level_name}|{record.channel}|{record.module}|{record.message}'
"""
Logging format string
    {record.time}: The timestamp when the log entry was created. You can format the timestamp as needed, like {record.time:%Y-%m-%d %H:%M:%S}.
    {record.level} or {record.level_name}: The severity level of the log entry. level provides the numeric level, whereas level_name provides the textual representation (e.g., INFO, WARNING).
    {record.channel}: The name of the logger that created the log entry. This is useful in applications with multiple modules or components using different logger instances.
    {record.module}: The name of the module that generated the log entry.
    {record.func} or {record.func_name}: The name of the function that generated the log entry.
    {record.lineno}: The line number in the source code where the log entry was generated.
    {record.message}: The log message.
    {record.thread} or {record.thread_id}: The ID of the thread that generated the log entry. Useful in multi-threaded applications.
    {record.process} or {record.process_id}: The ID of the process that generated the log entry. Particularly useful in multi-process applications.
    {record.extra[<key>]}: Any extra custom attributes that you may have added to the log record. This is accessed via extra which is a dictionary.
"""


class SafeRotatingFileHandler(RotatingFileHandler):
    """
    A custom RotatingFileHandler that overrides the default log rollover behavior.
    """

    def perform_rollover(self):
        """
        Override perform_rollover to handle errors more gracefully.
        """
        try:
            super().perform_rollover()
        except OSError as e:
            print(f"Error during log rollover: {e}")
            # Attempt to delete the old log file if renaming fails
            try:
                old_log = self._filename + ".1"
                if os.path.exists(old_log):
                    os.remove(old_log)
                os.rename(self._filename, old_log)
            except Exception as ex:
                print(f"Failed to rename log file after deletion attempt: {ex}")


def setup_logger(name=_DEFAULT_LOGGER_NAME, log_file=_DEFAULT_LOG_FILE, log_level=_DEFAULT_LOG_LEVEL):
    """
    Return a logger with a file handler and a stream handler

    :param name: the name of the logger
    :param log_file: the location of the logger file
    :param log_level: log level
    :return: logger object which can be used to log messages (logger.info, logger.error, etc. see https://logbook.readthedocs.io/en/stable/api/utilities.html)
    """

    create_log_directory_if_needed(log_file)
    handle_oversize_log_file(log_file)

    logbook.set_datetime_format("local")
    logger = Logger(name)

    try:
        # File handler setup with rotation
        file_handler = SafeRotatingFileHandler(log_file, max_size=_MAX_LOG_SIZE, backup_count=_MAX_BACKUP_COUNT,
                                               level=log_level, bubble=True)
        file_handler.format_string = _DEFAULT_LOG_FORMAT

        # Stream handler for console
        stream_handler = StreamHandler(sys.stdout, level=log_level, bubble=False)
        stream_handler.format_string = _DEFAULT_LOG_FORMAT

        # Attach handlers to the logger
        logger.handlers = []
        logger.handlers.append(file_handler)
        logger.handlers.append(stream_handler)

    except Exception as e:
        print(f"Error setting up logger: {e}")

    return logger


def create_log_directory_if_needed(log_file):
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except Exception as e:
        print(f"Failed to create directory: {log_file}, {e}")


def handle_oversize_log_file(log_file):
    try:
        if os.path.exists(log_file) and os.path.getsize(log_file) >= _MAX_LOG_SIZE:
            # Rename the existing log files up to _MAX_BACKUP_COUNT
            for i in range(_MAX_BACKUP_COUNT, 0, -1):
                src = f"{log_file}.{i}"
                dst = f"{log_file}.{i + 1}"
                if os.path.exists(dst):
                    os.remove(dst)
                if os.path.exists(src):
                    os.rename(src, dst)
            # Copy the current log file to log_file.1
            shutil.copy2(log_file, f"{log_file}.1")
            os.remove(log_file)
    except Exception as e:
        print(f"Failed to handle over-sized log file: {e}")
