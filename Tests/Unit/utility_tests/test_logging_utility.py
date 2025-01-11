import pytest
from multiprocessing import Process, current_process
import os

from Utilities import logging_utility, file_utility

_log_file1 = os.path.join(file_utility.get_project_root(), "logs", 'multiprocess_logbook.log')
_log_file2 = 'singleprocess_logbook.log'


@pytest.fixture(autouse=True)
def teardown():
    remove_log_file(_log_file1)
    remove_log_file(_log_file2)


def remove_log_file(log_file):
    if os.path.exists(log_file):
        os.remove(log_file)


def worker_process():
    logger = logging_utility.setup_logger(log_file=_log_file1)
    logger.info("Message from {process_name}", process_name=current_process().name)
    logger.error(f"[Avoid F-string] Message from {current_process().name}")


def test_setup_logger():
    remove_log_file(_log_file1)

    processes = [Process(target=worker_process) for _ in range(5)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    assert os.path.exists(_log_file1)


def test_setup_logger_no_log_directory():
    remove_log_file(_log_file2)

    logger = logging_utility.setup_logger(log_file=_log_file2)
    name = current_process().name
    logger.warn(f"Message from {name}", name=name)

    assert os.path.exists(_log_file2)
