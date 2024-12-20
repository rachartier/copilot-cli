from dataclasses import dataclass


@dataclass
class Args:
    path: str
    prompt: str | None
    model: str
    system_prompt: str
    action: str | None
    no_stream: bool
    no_spinner: bool
    copy_to_clipboard: bool
    list: bool
