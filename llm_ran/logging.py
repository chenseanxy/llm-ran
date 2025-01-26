import logging
from logging import ERROR, WARNING, INFO, DEBUG

def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level)
