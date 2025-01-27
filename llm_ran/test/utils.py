from langchain_core.runnables.base import Runnable
from langgraph.graph.graph import CompiledGraph
from traceback import print_exc
import logging

from llm_ran.logging import setup_logging
from llm_ran.llm import get_model

_logger = logging.getLogger(__name__)


def setup_harness(model="llama3.1:8b"):
    setup_logging()
    return get_model(model)


def test_chain(chain: Runnable, queries: list[str]):
    for query in queries:
        print("Query:", query)
        try:
            res = chain.invoke({"input": query})
            print("Response:", res)
        except Exception as e:
            print_exc()
            continue
        print("\n")


def test_graph(graph: CompiledGraph, queries):
    for query in queries:
        print("Query:", query)
        try:
            res = graph.stream(
                {"messages": [("human", query)]},
                stream_mode="values",
            )
            for r in res:
                r["messages"][-1].pretty_print()
        except Exception as e:
            print_exc()
            continue
        print("\n")


def semantic_equal(a, b):
    '''
    Check if two objects are semantically equal.

    The objects can be string, list, dict, or any combination of them.
    When the types are different, dicts are casted to lists, etc
    On casts from higher to lower types, if the object only contains one element,
    then the value of that element is used. Otherwise they are not equal.
    For lists, the order of elements is ignored.
    '''
    types = (str, list, dict)
    type_a = types.index(type(a)) if type(a) in types else None
    type_b = types.index(type(b)) if type(b) in types else None
    _logger.debug("Comparing %s and %s, type(a)=%s, type(b)=%s", a, b, type(a), type(b))

    if type_a is None or type_b is None:
        _logger.debug("%s != %s because types can not be found (a=%s,b=%s)", a, b, type_a, type_b)
        return False

    if type_a < type_b:
        return semantic_equal(b, a)

    if type_a > type_b:
        # Cast a from types[type_a] to types[type_b]
        if len(a) > 1:
            # A cannot be casted
            _logger.debug("%s != %s because a can not be casted to %s", a, b, type(b))
            return False

        if type(a) == dict:
            next_a = list(a.values())[0]
        elif type(a) == list:
            next_a = a[0]
        if type(b) == str:
            a = str(next_a)
        elif type(b) == list:
            a = [next_a]

    if type(b) == str:
        _logger.debug("Comparing strings %s and %s => %s", a, b, a == b)
        return a == b
    if type(b) == list:
        if len(a) != len(b):
            return False
        return set(a) == set(b)
    if type(b) == dict:
        if len(a) != len(b):
            return False
        for k, v in a.items():
            if k not in b or not semantic_equal(v, b[k]):
                return False
        return True
