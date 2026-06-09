import json
from collections.abc import Iterator
from typing import Protocol, runtime_checkable

import requests

from .constants import DEFAULT_OLLAMA_HOST


@runtime_checkable
class LLMClient(Protocol):
    def chat_completion(self, prompt: str, model: str, system_prompt: str, reasoning_effort: str | None = None) -> str: ...

    def stream_chat_completion(self, prompt: str, model: str, system_prompt: str, reasoning_effort: str | None = None) -> Iterator[str]: ...


def iter_sse_content(response: requests.Response) -> Iterator[str]:
    """Yields content deltas from an OpenAI-compatible SSE chat stream."""
    for line in response.iter_lines():
        if line and line.startswith(b"data: "):
            json_str = line[6:].decode("utf-8")
            if json_str == "[DONE]":
                break
            chunk: dict = json.loads(json_str)
            if chunk["choices"] and "delta" in chunk["choices"][0]:
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content


def create_client(mode: str, ollama_host: str = DEFAULT_OLLAMA_HOST) -> LLMClient:
    if mode == "ollama":
        from .ollama import OllamaClient

        return OllamaClient(ollama_host)

    from .copilot import GithubCopilotClient

    return GithubCopilotClient()
