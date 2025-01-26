from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from typing import Literal


def get_model(model: str) -> BaseChatModel:
    if model.startswith("claude"):
        return ChatAnthropic(model=model)
    elif model.startswith("lmstudio:"):
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="api-key",
            model=model.removeprefix("lmstudio:"),
        )
    else:
        return ChatOllama(model=model, base_url="http://localhost:11434")


def unload_model(model: BaseChatModel):
    if isinstance(model, ChatOllama) or model._llm_type == "chat-ollama":
        model.keep_alive = 0
        model.invoke([])


def with_output_mode(model: BaseChatModel, output_mode: Literal['json', '']):
    if isinstance(model, ChatOllama) or model._llm_type == "chat-ollama":
        model.bind(format=output_mode)
        return model
    # raise NotImplementedError("Output mode not supported for this model")
    return model
