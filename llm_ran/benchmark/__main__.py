import argparse
import pandas as pd
from datetime import datetime

from .questions import TEST_CASES
from llm_ran.benchmark.run import run_test_cases, DEFAULT_OUTPUT_PATH
from llm_ran.llm import get_model, unload_model
from llm_ran.k8s.direct import kubernetes_direct_chain
from llm_ran.k8s.codegen import kubernetes_codegen_chain
from llm_ran.logging import setup_logging
import logging

parser = argparse.ArgumentParser(description="Run benchmark tests")
parser.add_argument(
    "--trials",
    type=int,
    required=True,
    help="Number of trials to run for each test case",
)
parser.add_argument(
    "--model",
    type=str,
    required=True,
    help="Model to use for the benchmark tests",
)
parser.add_argument(
    "--scenarios",
    type=str,
    nargs="+",
    default=None,
    help="List of scenarios to run, if not provided, all scenarios will be run",
)
parser.add_argument(
    "--manage-scenarios",
    action="store_true",
    help="Whether to manage scenarios or not",
)
parser.add_argument(
    "--prefix",
    type=str,
    default="",
    help="Prefix for the output files",
)
parser.add_argument(
    "--log-prefix",
    type=str,
    default="",
    help="Prefix for the log files",
)
parser.add_argument(
    "--pull-model",
    action="store_true",
    help="Whether to pull the model from the registry or not",
)
parser.add_argument(
    "--chain",
    type=str,
    choices=["direct", "codegen"],
    required=True,
    help="Chain to use for the benchmark tests",
)
parser.add_argument(
    "--run-id",
    type=str,
    default=None,
    help="Run ID for the benchmark tests",
)
args = parser.parse_args()

trials = args.trials
prefix = args.prefix
log_prefix = args.log_prefix or prefix
run_id = args.run_id or datetime.now().strftime("%m%d%H%M%S")
model_filename = args.model.replace(':', '_').replace('/', '_')
output_file = f"{run_id}_{prefix}_{model_filename}_{args.chain}.csv"

setup_logging(level=logging.INFO, to_file=True, file_prefix=f"{run_id}_{log_prefix}")
logger = logging.getLogger("benchmark_base")

results = []
logger.info("Loading model and compiling graphs...")
model = get_model(args.model, pull=args.pull_model or False)
if args.chain == "direct":
    graph = kubernetes_direct_chain(model=model)
elif args.chain == "codegen":
    graph = kubernetes_codegen_chain(model=model)
else:
    raise ValueError(f"Unknown chain: {args.chain}")

logger.info(
    f"Running benchmark, chain={args.chain}, {model=}, {trials=}, "
    f"{args.scenarios=}, {args.manage_scenarios=}, {prefix=}, {run_id=}, "
    f"{output_file=}"
)
results = run_test_cases(
    graph=graph,
    test_cases=TEST_CASES,
    trials=trials,
    context={"model": args.model, "chain": args.chain, "total_trials": trials},
    result_logger=logging.getLogger("experiment"),
    progress_logger=logging.getLogger("progress"),
    prefix=f"{model_filename}_{args.chain}_{prefix}",
    run_id=run_id,
    manage_scenarios=args.manage_scenarios,
    select_scenarios=args.scenarios,
)
unload_model(model)

df = pd.DataFrame(results)
df.to_csv(
    DEFAULT_OUTPUT_PATH / output_file,
    index=False,
)

# tests
# poetry run python -m llm_ran.benchmark --trials 1 --model qwen2.5:32b --scenarios base --pull-model --chain direct