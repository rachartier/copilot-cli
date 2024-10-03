from pydantic import BaseModel
from typing_extensions import Callable

from args import Args


class Action(BaseModel):
    description: str
    prompt: str
    system_prompt: str
    model: str
    commands: dict[str, list[str]] | None = None
    on_complete: Callable[[str, Args], None] | None = None
    output_to_stdout: bool = True
