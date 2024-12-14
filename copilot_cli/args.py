from dataclasses import dataclass


@dataclass
class Args:
    path: str
    prompt: str | None
    model: str
    system_prompt: str
    action: str | None
    nostream: bool
    list: bool
