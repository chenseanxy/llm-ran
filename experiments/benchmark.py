from llm_ran.benchmark.run import run_test_cases
from llm_ran.k8s.direct import kubernetes_direct_chain
from llm_ran.k8s.codegen import kubernetes_codegen_chain
from llm_ran.benchmark.questions import TEST_CASES
from llm_ran.benchmark.run import DEFAULT_OUTPUT_PATH
from llm_ran.llm import get_model, models
from llm_ran.logging import setup_logging, EXPERIMENT_LOGGER, PROGRESS_LOGGER
import logging
import pandas as pd
from datetime import datetime

run_id = datetime.now().strftime("%m%d_%H%M%S")
setup_logging(to_file=True, file_prefix=run_id)
logger = logging.getLogger("benchmark_base")


TRIALS = 10
MODELS = [
    # Mainline models
    models.QWEN_25_32B,
    models.QWEN_25_CODE_32B,
    models.LLAMA_33_70B,

    # Reasoning models
    models.QWQ,
    models.SKY_T1_32B,
    
    # MOE models
    models.MIXTRAL_7B,
]

CHAINS = [
    (kubernetes_direct_chain, "direct"),
    (kubernetes_codegen_chain, "codegen"),
]
SCENARIOS = [
    "base",
]

all_results = []
trials = TRIALS

for model in MODELS:
    model_filename = model.replace(':', '_').replace('/', '_')
    for chain, chain_name in CHAINS:
        logger.info("Loading model and compiling graphs...")
        graph = chain(model=get_model(model, pull=True))
        prefix = f"{model_filename}_{chain_name}"
        results = run_test_cases(
            graph=graph,
            test_cases=TEST_CASES,
            trials=trials,
            context={"model": model, "chain": chain_name, "total_trials": trials},
            result_logger=logging.getLogger(EXPERIMENT_LOGGER),
            progress_logger=logging.getLogger(PROGRESS_LOGGER),
            manage_scenarios=False,
            select_scenarios=SCENARIOS,
            prefix=prefix,
            run_id=run_id,
        )
        df = pd.DataFrame(results)
        df.to_csv(
            DEFAULT_OUTPUT_PATH / f"{run_id}_{prefix}.csv",
            index=False,
        )
