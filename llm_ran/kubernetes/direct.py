from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from llm_ran.llm import with_output_mode

from .direct_impl import (
    get_pod_names_in_namespace as _get_pod_names_in_namespace,
    get_services_in_namespace as _get_services_in_namespace,
    get_nodes as _get_nodes,
    get_pods_on_node_in_namespace as _get_pods_on_node_in_namespace,
    get_pod_node as _get_pod_node,
)

get_pod_names_in_namespace = tool(_get_pod_names_in_namespace)
get_services_in_namespace = tool(_get_services_in_namespace)
get_nodes = tool(_get_nodes)
get_pods_on_node_in_namespace = tool(_get_pods_on_node_in_namespace)
get_pod_node = tool(_get_pod_node)

K8S_DIRECT_TOOLS = [
    get_pod_names_in_namespace,
    get_services_in_namespace,
    get_nodes,
    get_pods_on_node_in_namespace,
    get_pod_node,
]

K8S_DIRECT_SYS_PROMPT = '''
You are a Kubernetes expert, and you are asked some questions
about the Kubernetes cluster.
You may have to use multiple tools one after another, in these cases
you need to produce a tool use message for the first tool and then
generate the next tool use message based on the output of the previous tool.

You are to DIRECTLY return the output of the tool.
Do NOT include any additional information or text in your response.
ONLY return a valid JSON output.

The question is as follows:
'''


def kubernetes_direct_chain(model: BaseChatModel):
    agent = create_react_agent(
        model=model,
        # model=with_output_mode(model, "json"),
        tools=K8S_DIRECT_TOOLS,
        state_modifier=K8S_DIRECT_SYS_PROMPT
    )
    return agent


if __name__ == "__main__":
    from llm_ran.test.utils import setup_harness, test_graph
    from llm_ran.llm import models
    _TEST_QUERIES = [
        "In namespace 'monitoring', list all the pods that are running on same kubernetes node "
        "as pod 'prometheus-monitoring-kube-prometheus-prometheus-0' (including this one). Return as a list.",
    ]
    model = setup_harness(models.QWEN_25_14B)
    chain = kubernetes_direct_chain(model)
    test_graph(chain, _TEST_QUERIES)
