import logging
from langgraph.graph.graph import CompiledGraph

_logger = logging.getLogger(__name__)


def run_graph(
        graph: CompiledGraph,
        query: str,
        *,
        propagate_errors: bool = True,
    ):
    _logger.info("Running graph with query: %s", query)
    res = None
    try:
        for chunk in graph.stream({"messages": [("human", query)]}, stream_mode="values"):
            res = chunk
            # _logger.info("Graph step %s: %s", len(res["messages"]), res["messages"][-1].get("usage_metadata"))
        _logger.info("Graph finished executing with %d messages", len(res["messages"]))
        if not propagate_errors:
            return (res, None)
        return res
        # return res["messages"][-1].content
    except Exception as e:
        _logger.info("Graph failed to execute", exc_info=True)
        if not propagate_errors:
            return (res, e)
        raise