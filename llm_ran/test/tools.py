from llm_ran.logging import setup_logging
from langchain_ollama import ChatOllama
from langchain_core.runnables.base import Runnable

from traceback import print_exc

def setup_harness():
    setup_logging()
    model = ChatOllama(model="llama3.1:8b", base_url="http://localhost:11434")
    return model


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