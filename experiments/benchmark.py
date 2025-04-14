from llm_ran.llm import models
from llm_ran.logging import setup_logging
import logging
from datetime import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor

run_id = datetime.now().strftime("%m%d_%H%M%S")
# setup_logging(to_file=True, file_prefix=run_id)
logger = logging.getLogger("benchmark_base")

PARALLELISM = 4
print(f"Running with parallelism: {PARALLELISM}")

TRIALS = 10
print(f"Running {TRIALS} trials")

MODELS = [
    # Mainline models
    models.LLAMA_33_70B,
    models.QWEN_25_32B,
    models.QWEN_25_CODE_32B,

    # Reasoning models
    models.QWQ,
    models.SKY_T1_32B,
    
    # MOE models
    # models.MIXTRAL_7B,
    models.MIXTRAL_22B
]
print(f"Running {len(MODELS)} models: {MODELS}")

CHAINS = [
    (None, "direct"),
    (None, "codegen"),
]
print(f"Running {len(CHAINS)} chains: {[c[1] for c in CHAINS]}")

SCENARIOS = [
    # "base",
    # "resource-constraint",
    # "image-not-found",
    # "liveness-probe",
    "node-affinity",
]
print(f"Running {len(SCENARIOS)} scenarios: {SCENARIOS}")

all_results = []
processes = []


def one_model(model, chains, trials, run_id, scenarios):
    # use popen to run the benchmark in a separate process
    # python -m llm_ran.benchmark --trials 1 --model qwen2.5:32b --scenarios base --pull-model --chain direct --run-id 1012_1230
    for chain in chains:
        command = [
            "poetry",
            "run",
            "python",
            "-m",
            "llm_ran.benchmark",
            "--trials",
            str(trials),
            "--model",
            model,
            "--scenarios",
            *scenarios,
            "--pull-model",
            "--chain",
            chain,
            "--run-id",
            run_id,
        ]
        print(" ".join(command))
        # process = subprocess.Popen(
        #     command,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        # )
        # process.wait()
        # stdout, stderr = process.communicate()
        # print(stdout.decode())
        # print(stderr.decode())
    print()


# with ThreadPoolExecutor(max_workers=PARALLELISM) as executor:
for model in MODELS:
    model_filename = model.replace(':', '_').replace('/', '_')
    one_model(
        model,
        [chain[1] for chain in CHAINS],
        TRIALS,
        run_id,
        SCENARIOS,
    )
    # executor.submit(
    #     one_model,
    #     model,
    #     [chain[1] for chain in CHAINS],
    #     TRIALS,
    #     run_id,
    #     SCENARIOS,
    # )
