from collections.abc import Iterator

import requests
from requests.exceptions import ConnectionError, RequestException

from .client import iter_sse_content
from .exception.api_error import APIError


class OllamaClient:
    """Client for a local Ollama server via its OpenAI-compatible API."""

    def __init__(self, host: str) -> None:
        self._endpoint = f"{host.rstrip('/')}/v1/chat/completions"
        self._host = host

    def _build_body(self, prompt: str, model: str, system_prompt: str, stream: bool) -> dict:
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "model": model,
            "stream": stream,
        }

    def _unreachable_error(self, e: ConnectionError) -> APIError:
        return APIError(f"Could not reach Ollama at {self._host}; is it running?")

    def chat_completion(self, prompt: str, model: str, system_prompt: str, reasoning_effort: str | None = None) -> str:
        try:
            response = requests.post(
                self._endpoint,
                headers={"Content-Type": "application/json"},
                json=self._build_body(prompt, model, system_prompt, False),
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except ConnectionError as e:
            raise self._unreachable_error(e) from e
        except RequestException as e:
            raise APIError(f"Chat completion request failed: {str(e)}") from e

    def stream_chat_completion(self, prompt: str, model: str, system_prompt: str, reasoning_effort: str | None = None) -> Iterator[str]:
        try:
            with requests.post(
                self._endpoint,
                headers={"Content-Type": "application/json"},
                json=self._build_body(prompt, model, system_prompt, True),
                stream=True,
            ) as response:
                response.raise_for_status()
                yield from iter_sse_content(response)
        except ConnectionError as e:
            raise self._unreachable_error(e) from e
        except RequestException as e:
            raise APIError(f"Streaming chat completion request failed: {str(e)}") from e
