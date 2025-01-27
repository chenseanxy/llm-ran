import logging
from logging import ERROR, WARNING, INFO, DEBUG
from pathlib import Path

_base_path = Path(__file__).parent.parent

def setup_logging(level=logging.INFO, to_file=False):
    root = logging.getLogger()
    root.setLevel(level)
    root_handler = (
        logging.StreamHandler()
        if not to_file
        else logging.FileHandler(_base_path / "logs/llm_ran.log")
    )
    root_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root_handler.setFormatter(root_formatter)
    root.addHandler(root_handler)

    exp = logging.getLogger("experiment")
    exp.propagate = False
    exp.setLevel(level)
    exp_handler = logging.FileHandler(_base_path / "logs/experiment.log")
    exp_handler.setFormatter(root_formatter)
    exp.addHandler(exp_handler)
