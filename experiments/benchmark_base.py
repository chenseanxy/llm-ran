import logging

from llm_ran.benchmark.questions import TEST_CASES
from llm_ran.benchmark.run import run_test_cases
from llm_ran.k8s.direct import kubernetes_direct_chain
from llm_ran.k8s.codegen import kubernetes_codegen_chain
from llm_ran.llm import models

from llm_ran.logging import setup_logging
setup_logging(level=logging.INFO, to_file=True)
logger = logging.getLogger("benchmark_base")

TRIALS = 10
MODELS = [
    models.QWEN_25_32B,
    models.QWEN_25_CODE_32B,
    models.SKY_T1_32B,
]

