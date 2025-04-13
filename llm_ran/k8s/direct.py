from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from . import direct_impl


for name, func in direct_impl.__dict__.items():
    if callable(func) and name.startswith("get_"):
        globals()[name] = tool(func)

K8S_DIRECT_TOOLS = [
    # tool(sum),
    # tool(len),
    *(
        tool(func)
        for name, func in direct_impl.__dict__.items()
        if callable(func) and name.startswith("get_")
    ),
]

K8S_DIRECT_SYS_PROMPT = '''

You are a Kubernetes expert, and you are asked some questions
about the Kubernetes cluster.
You may have to use multiple tools one after another, in these cases
you need to produce a tool use message for the first tool and then
generate the next tool use message based on the output of the previous tool.

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
        # "List all the non-existing nodes.",
        # "In namespace 'monitoring', list all the pods that are running on same kubernetes node "
        # "as pod 'prometheus-monitoring-kube-prometheus-prometheus-0' (including this one). Return as a list.",
        "Why is my deployment `productcatalogservice` failing?",
        # "Why is pod `productcatalogservice-866656977f-4dcfx` failing?",
    ]
    model = setup_harness(models.QWEN_25_14B)
    chain = kubernetes_direct_chain(model)
    test_graph(chain, _TEST_QUERIES)
