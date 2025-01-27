import logging
from langgraph.graph.graph import CompiledGraph

_logger = logging.getLogger(__name__)


def run_graph(
        graph: CompiledGraph,
        query: str,
        *,
        propagate_errors: bool = False
    ):
    _logger.info("Running graph with query: %s", query)
    try:
        res = graph.invoke(
            {"messages": [("human", query)]},
        )
        _logger.info("Graph finished executing with %d messages", len(res["messages"]))
        return res["messages"][-1].content
    except Exception:
        _logger.info("Graph failed to execute", exc_info=True)
        if propagate_errors:
            raise
