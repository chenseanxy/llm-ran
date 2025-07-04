import logging
from logging import ERROR, WARNING, INFO, DEBUG
from pathlib import Path

_base_path = Path(__file__).parent.parent / "logs"
_base_path.mkdir(parents=True, exist_ok=True)

EXPERIMENT_LOGGER = "experiment"
PROGRESS_LOGGER = "progress"


def setup_logging(level=logging.INFO, to_file=False, file_prefix=""):
    if file_prefix:
        file_prefix = file_prefix + "_"
    root = logging.getLogger()
    root.setLevel(level)
    root_handler = (
        logging.StreamHandler()
        if not to_file
        else logging.FileHandler(_base_path / f"{file_prefix}llm_ran.log", encoding="utf-8")
    )
    root_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root_handler.setFormatter(root_formatter)
    root.addHandler(root_handler)

    exp = logging.getLogger(EXPERIMENT_LOGGER)
    exp.propagate = False
    exp.setLevel(level)
    exp_handler = logging.FileHandler(_base_path / f"{file_prefix}experiment.log", encoding="utf-8")
    exp_handler.setFormatter(root_formatter)
    exp.addHandler(exp_handler)

    prog = logging.getLogger(PROGRESS_LOGGER)
    prog.propagate = False
    prog.setLevel(level)
    prog_handler = logging.FileHandler(_base_path / f"{file_prefix}progress.log", encoding="utf-8")
    prog_handler.setFormatter(root_formatter)
    prog.addHandler(prog_handler)
