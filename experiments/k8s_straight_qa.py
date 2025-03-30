import pandas as pd
import json
import logging

from llm_ran.llm import get_model, unload_model, models
from llm_ran.test.utils import semantic_equal
from llm_ran.graph import run_graph
from llm_ran.k8s.direct import kubernetes_direct_chain
from llm_ran.k8s.codegen import kubernetes_codegen_chain
from llm_ran.benchmark.test_straight_qa import QUERIES_ANSWERS
from llm_ran.logging import setup_logging

setup_logging(to_file=True)
logger = logging.getLogger("experiment")

REPEATS = 20
models_ = [
    # models.LLAMA_31_8B,
    # models.QWEN_25_7B,
    # models.QWEN_25_14B,
    # models.CLAUDE_BIG,
    # models.QWEN_25_32B,
    # models.LLAMA_33_70B,
    models.QWEN_25_72B,
]
data = []

for model_name in models_:
    model = get_model(model_name)
    graphs = {
        "direct": kubernetes_direct_chain(model),
        "codegen": kubernetes_codegen_chain(model),
    }
    
    for graph_name, graph in graphs.items():
        for qi, (query, answer_func) in enumerate(QUERIES_ANSWERS):
            answer = answer_func()
            print("Graph: ", graph_name)
            print("Query: ", query)
            print("Actual: ", answer)
            for i in range(REPEATS):
                # print(f"Running model {model} repeat {i}")
                try:
                    res = run_graph(graph, query, propagate_errors=True)
                    msg = res["messages"][-1].content
                    loaded = json.loads(msg)
                    this = {
                        "graph": graph_name,
                        "model": model_name,
                        "query_id": qi,
                        "try": i,
                        "success": True,
                        "failed_reason": None,
                        "equal": semantic_equal(loaded, answer),
                    }
                except Exception as e:
                    this = {
                        "graph": graph_name,
                        "model": model_name,
                        "query_id": qi,
                        "try": i,
                        "success": False,
                        "failed_reason": e.__class__.__name__,
                        "equal": False,
                    }
                data.append(this)
                logger.info(this)
                # print(this)
                print("Model: ", )
            # print("")

    # After running the model, unload it to make room for the next one
    unload_model(model)

df = pd.DataFrame(data)
df.to_csv("../data/llm_ran_kubernetes_base.csv", index=False)
