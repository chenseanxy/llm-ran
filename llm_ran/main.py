from langchain_ollama import ChatOllama

from .logging import setup_logging
from .kubernetes import get_kubernetes_chain

setup_logging()

model = ChatOllama(model="llama3.1:8b", base_url="http://localhost:11434")

get_kubernetes_chain(model).invoke({"input": "Get all pods in the default namespace"})
