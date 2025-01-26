from .utils import semantic_equal
from llm_ran.logging import setup_logging, DEBUG

setup_logging(DEBUG)

assert semantic_equal("a", "a") == True
assert semantic_equal("a", "b") == False
assert semantic_equal(["a"], ["a"]) == True
assert semantic_equal(["a"], ["b"]) == False
assert semantic_equal(["a"], "a") == True
assert semantic_equal(["a"], "b") == False
assert semantic_equal("a", ["a"]) == True
assert semantic_equal("a", ["b"]) == False
assert semantic_equal({"a": "b"}, {"a": "b"}) == True
assert semantic_equal({"a": "b"}, {"a": "c"}) == False
assert semantic_equal({"a": "b"}, {"b": "b"}) == False
assert semantic_equal({"a": "b"}, {"b": "c"}) == False
assert semantic_equal({"a": "b"}, "b") == True
assert semantic_equal({"a": "b"}, "c") == False
assert semantic_equal({"a": "a"}, ["a"]) == True
assert semantic_equal({"a": "a"}, ["b"]) == False
