from pydantic import BaseModel
from typing_extensions import Callable

from ..args import Args


class Output(BaseModel):
    to_stdout: bool = False
    to_file: str | None = None
    markdown: bool | None = None


class Action(BaseModel):
    description: str
    prompt: str
    system_prompt: str
    model: str
    commands: dict[str, list[str]] | None = None
    on_complete: Callable[[str, Args], None] | None = None
    output: Output
