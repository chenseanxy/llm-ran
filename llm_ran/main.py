from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatOllama(model="llama3.1:8b")
messages = [
    SystemMessage("Translate the following from English into Italian"),
    HumanMessage("hi!"),
]
print(model.invoke(messages))
