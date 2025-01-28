
from .logging import setup_logging
setup_logging()

from llm_ran.kubernetes.direct_impl import get_nodes
print(get_nodes())
