from llm_ran.llm import models

TRIALS = 10
MODELS = [
    models.QWEN_25_32B,
    models.QWEN_25_CODE_32B,
    models.SKY_T1_32B,
]
CHAINS = [
    "kubernetes_direct_chain",
    "kubernetes_codegen_chain",
]
run_id = "run-1"

