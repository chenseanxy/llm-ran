import logging
from kubernetes import client, config

from langchain.tools.base import BaseTool
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

_logger = logging.getLogger(__name__)
config.load_kube_config()


class K8sCodeGenExecutionError(Exception):
    def __init__(self, code: str, exception: Exception):
        super().__init__()
        self.code = code
        self.exception = exception


class K8sCodeGenExecutor(BaseTool):
    name: str = "Kubernetes CodeGen Executor"
    description: str = "Executes generated kubernetes python client code"

    def _run(self, code: str):
        _logger.info(f"Executing code: \n{'-'*20}\n{code}\n{'-'*20}")
        globals_ = {"client": client}
        locals_ = {"result": {}}
        try:
            exec(code, globals_, locals_)   # noqa TODO: ACE
            assert locals_["result"], "result is empty"
        except Exception as e:
            _logger.exception(f"Error executing code, exception: {e}")
            raise K8sCodeGenExecutionError(code, exception=e)
        return locals_["result"]


def exception_to_messages(inputs: dict) -> dict:
    exception = inputs.pop("exception")
    inputs["fallback_count"] = inputs.get("fallback_count", 0) + 1
    _logger.info(f"Retry {inputs['fallback_count']} on {exception.__class__.__name__}")
    # print("Exception is", exception, exception.tool_call)

    # Add historical messages to the original input, so the model knows that it made a mistake with the last tool call.
    messages = [
        # *inputs.get("last_output", []),
        HumanMessage(
            content=(
                "The code you last submitted failed to run. Try to fix the errors. Do not repeat mistakes."
                f"The previous code you submitted: \n{exception.code}\n"
                f"Error: {exception.exception}"
            )
        ),
    ]
    # print(messages)
    inputs["last_output"] = messages
    return inputs


K8S_CODE_GEN_SYS_TEMPLATE = '''
You are a Kubernetes expert developing K8s Python client code.
Do NOT import anything, 'client' object is already given to you.
Do NOT use try-catch clauses and do NOT handle exceptions.

Here are some pointers for solving questions:
1. Find out which entities the question is asking for (e.g., pods, services, deployments, etc.)
   If provided with a name, use the name to query the specific entity.
2. Use the V1 Apis provided by the 'client' object to query the entities.
3. Extract the relevant fields the question is asking for, and ONLY extract the fields
   that are explicitly asked for. If the question only ask for the entities, 
   return the names of the entities. Do NOT store the entire entity.
4. Save the results into the 'result' dictionary. Do NOT print them.

Respond ONLY with plain text Python code snippets WITHOUT formatting nor explanations.

You are to answer the following question with code:
'''

K8S_CODE_GEN_RETRIES = 5


def get_kubernetes_chain(model: BaseChatModel):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", K8S_CODE_GEN_SYS_TEMPLATE),
            ("human", "{input}"),
            ("placeholder", "{last_output}"),
        ]
    )
    normal_chain = prompt | model | StrOutputParser() | K8sCodeGenExecutor()
    chain = normal_chain
    chain = chain.with_fallbacks(
        [exception_to_messages | normal_chain] * K8S_CODE_GEN_RETRIES,
        exceptions_to_handle=(K8sCodeGenExecutionError,),
        exception_key="exception",
    )
    return chain


if __name__ == "__main__":
    from .test.tools import setup_harness, test_chain
    _TEST_QUERIES = [
        # "What are the names of the services in the 'monitoring' namespace?",
        # "List all the pod names and their labels in the 'monitoring' namespace.",
        # "List all the nodes.",
        # "Show all the pods in the 'monitoring' namespace that are running on node 'k3d-oran-agent-1'.",
        # '''
        # Given a pod name 'prometheus-monitoring-kube-prometheus-prometheus-0'
        # in the 'monitoring' namespace, get the pod's node name.
        # ''',
        # Cutoff: anything below this ended up being too complicated for one code gen, results are less consistent
        # '''
        # In namespace 'monitoring', list all the pods that are running on same kubernetes node
        # as pod 'prometheus-monitoring-kube-prometheus-prometheus-0'. Return as a list.
        # ''',
        # '''
        # In namespace 'monitoring', find out the node where pod 'prometheus-monitoring-kube-prometheus-prometheus-0' 
        # is deployed on, then use that find all the pods that are running on the same node. Return the names of the pods.
        # '''
    ]
    model = setup_harness()
    test_chain(get_kubernetes_chain(model), _TEST_QUERIES)
