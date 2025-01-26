import logging
from kubernetes import client
from pydantic import BaseModel
from typing import Annotated

from langchain.tools.base import BaseTool
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_experimental.tools.python.tool import sanitize_input
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.prebuilt.tool_node import TOOL_CALL_ERROR_TEMPLATE as GENERIC_TOOL_CALL_ERROR_TEMPLATE


_logger = logging.getLogger(__name__)


class K8sCodeGenExecutionError(Exception):
    def __init__(self, code: str, exception: Exception):
        super().__init__()
        self.code = code
        self.exception = exception


class K8sCodeGenExecutor(BaseTool):
    name: str = "Kubernetes CodeGen Executor"
    description: str = "Executes generated kubernetes python client code"

    def _run(self, code: str):
        code = sanitize_input(code)
        _logger.info(f"Executing code: \n{'-'*20}\n{code}\n{'-'*20}")
        globals_ = {"client": client, "result": {}}
        try:
            exec(code, globals_)   # noqa TODO: ACE
            assert globals_["result"], "result is empty"
        except Exception as e:
            _logger.info(f"Error executing code, exception: {e}", exc_info=True)
            raise K8sCodeGenExecutionError(code, exception=e)
        return globals_["result"]


class K8sCodeGenToolNode(ToolNode):
    self_retry: bool = True
    self_retry_count: int = 5
    
    def _run_one(self, call, config):
        return super()._run_one(call, config)

K8S_CODE_GEN_SYS_PROMPT = '''
You are a Kubernetes expert developing K8s Python client code.
Do NOT import anything, 'client' object is already given to you, 
use it DIRECTLY to query the Kubernetes cluster.
Do NOT use try-catch clauses and do NOT handle exceptions.

Here are some pointers for solving questions:
1. Find out which entities the question is asking for (e.g., pods, services, deployments, etc.)
   If provided with a name, use the name to query the specific entity.
2. Use the V1 Apis provided by the 'client' object to query the entities.
3. Extract the relevant fields the question is asking for, and ONLY extract the fields
   that are explicitly asked for. If the question only ask for the entities, 
   return the names of the entities. Do NOT store the entire entity.
4. Save the results into the 'result' dictionary. Do NOT print them.

Execute the code with the tool we have provided.
After you have executed the code, ONLY return the results as pure plaintext JSON.
You are to answer the following question with code:
'''

K8S_CODE_GEN_ERR_EXEC_PROMPT = '''
The code you last submitted failed to run. Try to fix the errors.
Do not repeat mistakes.
The error message is: {error}
Please update the code and execute it again with the tool we have provided.'''

K8S_CODEGEN_TOOLS = [K8sCodeGenExecutor()]


class _State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    retries: int = 0


def kubernetes_codegen_chain(
        model: BaseChatModel,
        *,
        self_retry: bool = True,
        self_retry_count: int = 5,
    ):
    model_with_tools = model.bind_tools(K8S_CODEGEN_TOOLS)

    def call_llm(state: _State):
        in_messages = [("system", K8S_CODE_GEN_SYS_PROMPT)] + state.messages
        return {"messages": [model_with_tools.invoke(in_messages)]}
    
    def on_tool_error(exception: Exception):
        if isinstance(exception, K8sCodeGenExecutionError):
            return K8S_CODE_GEN_ERR_EXEC_PROMPT.format(error=repr(exception.exception))
        return GENERIC_TOOL_CALL_ERROR_TEMPLATE.format(error=repr(exception))

    graph = StateGraph(_State)
    graph.add_node("call_llm", call_llm)
    tools_node = ToolNode(K8S_CODEGEN_TOOLS, handle_tool_errors=on_tool_error)
    graph.add_node("tools", tools_node)

    graph.add_conditional_edges("call_llm", tools_condition)
    graph.add_edge("tools", "call_llm")
    graph.set_entry_point("call_llm")
    return graph.compile()


if __name__ == "__main__":
    from llm_ran.test.utils import setup_harness, test_graph
    from llm_ran.llm import models
    _TEST_QUERIES = [
        # "What are the names and ports of the services in the 'monitoring' namespace? "
        # "Return name as keys and ports in a list as values",
        # "List all the pod names in the 'monitoring' namespace. Return as a list of pod names.",
        # "List all the nodes.",
        # "Show all the pods in the 'monitoring' namespace that are running on node 'k3d-oran-agent-1'.",
        # '''
        # Given a pod name 'prometheus-monitoring-kube-prometheus-prometheus-0'
        # in the 'monitoring' namespace, get the pod's node name.
        # ''',
        # Cutoff: anything below this ended up being too complicated for one code gen, results are less consistent
        '''
        In namespace 'monitoring', list all the pods that are running on same kubernetes node
        as pod 'prometheus-monitoring-kube-prometheus-prometheus-0' (including this one). Return as a list.
        ''',
        # '''
        # In namespace 'monitoring', find out the node where pod 'prometheus-monitoring-kube-prometheus-prometheus-0' 
        # is deployed on, then use that find all the pods that are running on the same node. Return the names of the pods.
        # '''
    ]
    model = setup_harness(models.QWEN_25_14B)
    test_graph(kubernetes_codegen_chain(model), _TEST_QUERIES)
