import logging
from logging import ERROR, WARNING, INFO, DEBUG
from pathlib import Path

_base_path = Path(__file__).parent.parent

def setup_logging(level=logging.INFO, to_file=False):
    logging.basicConfig(
        level=level, 
        filename=_base_path / "logs/llm_ran.log" if to_file else None,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
