import logging
import sys


def create_stdout_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO)
    fh = logging.StreamHandler(sys.stdout)
    fh_formatter = logging.Formatter("%(asctime)s - %(message)s")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger