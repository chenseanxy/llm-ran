'''
This was an earlier POC to run LLM benchmarks.
Benchmarking was then formally developed with the `llm_ran.benchmark` module
and `experiments/benchmark.py`
'''

import pandas as pd
import json
import logging
from typing import Callable

from llm_ran.llm import get_model, unload_model, models
from llm_ran.test.utils import semantic_equal
from llm_ran.graph import run_graph
from llm_ran.k8s.direct import kubernetes_direct_chain
from llm_ran.k8s.codegen import kubernetes_codegen_chain
from llm_ran.k8s.direct_impl import (
    get_services_in_namespace,
    get_pod_names_in_namespace,
    get_nodes,
    get_pods_on_node_in_namespace,
    get_pod_node,
)
from llm_ran.logging import setup_logging

setup_logging(to_file=True)
logger = logging.getLogger("experiment")

QUERIES_ANSWERS: list[tuple[str, Callable]] = [
    (
        "What are the names and ports of the services in the 'monitoring' namespace? "
        "Return name as keys and ports in a list as values, example {'service1': [80, 443], 'service2': [8080]}",
        lambda: get_services_in_namespace("monitoring")
    ),
    (
        "List all the pod names in the 'monitoring' namespace. Return as a list of pod names. "
        "Example ['pod1', 'pod2']",
        lambda: get_pod_names_in_namespace("monitoring")
    ),
    (
        "List all the nodes. Return as a list of node names. Example ['node1', 'node2']",
        lambda: get_nodes()
    ),
    (
        "Show all the pods in the 'monitoring' namespace that are running on node 'k3d-oran-agent-1'."
        "Return as a list of pod names. Example ['pod1', 'pod2']",
        lambda: get_pods_on_node_in_namespace("k3d-oran-agent-1", "monitoring")
    ),
    (
        "Given a pod name 'prometheus-monitoring-kube-prometheus-prometheus-0' "
        "in the 'monitoring' namespace, get the pod's node name."
        "Example 'node1'",
        lambda: get_pod_node("prometheus-monitoring-kube-prometheus-prometheus-0", "monitoring")
    ),
    # Cutoff: anything below this ended up being too complicated for one code gen, results are less consistent
    (
        "In namespace 'monitoring', list all the pods that are running on same kubernetes node "
        "as pod 'prometheus-monitoring-kube-prometheus-prometheus-0' (including this one). Return as a list. "
        "Example ['pod1', 'pod2']",
        lambda: get_pods_on_node_in_namespace(
            get_pod_node("prometheus-monitoring-kube-prometheus-prometheus-0", "monitoring"),
            "monitoring"
        )
    ),
    (
        "In namespace 'monitoring', find out the node where pod 'prometheus-monitoring-kube-prometheus-prometheus-0' "
        "is deployed on, then use that find all the pods that are running on the same node. Return the names of the pods. "
        "Example ['pod1', 'pod2']",
        lambda: get_pods_on_node_in_namespace(
            get_pod_node("prometheus-monitoring-kube-prometheus-prometheus-0", "monitoring"),
            "monitoring"
        )
    ),
]


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
