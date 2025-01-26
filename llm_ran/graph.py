import logging
from langgraph.graph.graph import CompiledGraph

_logger = logging.getLogger(__name__)


def run_graph(
        graph: CompiledGraph,
        query: str,
        *,
        propagate_errors: bool = False
    ):
    _logger.info("Query: %s", query)
    try:
        res = graph.invoke({"messages": [("human", query)]})
        return res["messages"][-1].content
    except Exception as e:
        if propagate_errors:
            raise
        _logger.exception(e)
