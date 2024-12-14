from pydantic import BaseModel, Field
from typing_extensions import Callable

from ..args import Args


class Output(BaseModel):
    to_stdout: bool = Field(default=True)
    to_file: str | None = None


class Options(BaseModel):
    stream: bool = Field(default=True)
    spinner: bool = Field(default=True)


class Action(BaseModel):
    description: str
    prompt: str
    system_prompt: str
    model: str
    commands: dict[str, list[str]] | None = None
    on_complete: Callable[[str, Args], None] | None = None
    output: Output = Field(default_factory=Output)
    options: Options = Field(default_factory=Options)
