from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from typing import Literal
import logging

_logger = logging.getLogger(__name__)


def get_model(model: str, *, pull=False) -> BaseChatModel:
    if model.startswith("claude"):
        return ChatAnthropic(model=model)
    elif model.startswith("lmstudio:"):
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="api-key",
            model=model.removeprefix("lmstudio:"),
        )
    else:
        _mdl = ChatOllama(
            model=model,
            base_url="http://localhost:11434",
            client_kwargs={"timeout": 120.0},
            num_ctx=32768,  # 32k context for qwen
            timeout=120.0,
        )
        if pull:
            _logger.info(f"Pulling model {model}...")
            _mdl._client.pull(model)

        _logger.info(f"Warming up model {model}...")
        _mdl.invoke([])
        return _mdl


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
