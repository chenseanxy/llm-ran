import logging
from logging import ERROR, WARNING, INFO, DEBUG
from pathlib import Path

_base_path = Path(__file__).parent.parent

def setup_logging(level=logging.INFO, to_file=False, file_prefix=""):
    if file_prefix:
        file_prefix = file_prefix + "_"
    root = logging.getLogger()
    root.setLevel(level)
    root_handler = (
        logging.StreamHandler()
        if not to_file
        else logging.FileHandler(_base_path / f"logs/{file_prefix}llm_ran.log", encoding="utf-8")
    )
    root_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root_handler.setFormatter(root_formatter)
    root.addHandler(root_handler)

    exp = logging.getLogger("experiment")
    exp.propagate = False
    exp.setLevel(level)
    exp_handler = logging.FileHandler(_base_path / f"logs/{file_prefix}experiment.log", encoding="utf-8")
    exp_handler.setFormatter(root_formatter)
    exp.addHandler(exp_handler)
