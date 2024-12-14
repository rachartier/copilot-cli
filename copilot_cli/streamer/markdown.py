from collections.abc import Iterator
from typing import Any, TypeAlias

from rich.console import Console, ConsoleOptions
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text

StreamOptions: TypeAlias = dict[str, Any]


class MarkdownStreamer:
    """
    A class to handle streaming markdown content with Rich.
    """

    console: Console
    content: str

    def __init__(self, *, color_system: str = "auto", markup: bool = True, highlight: bool = True) -> None:
        """
        Initialize the markdown streamer with custom console options.

        Args:
            color_system: The color system to use ("auto", "standard", "256", "truecolor", None)
            markup: Whether to enable Rich markup
            highlight: Whether to enable syntax highlighting
        """
        self.console = Console(color_system=color_system, markup=markup, highlight=highlight)
        self.content = ""

    def get_console_options(self) -> ConsoleOptions:
        """
        Get the current console options.

        Returns:
            The current console options configuration
        """
        return self.console.options

    def set_console_options(self, **options: Any) -> None:
        """
        Update console options.

        Args:
            **options: Keyword arguments to update console options
        """
        self.console.options.update(**options)

    def stream(self, iterator: Iterator[str], *, refresh_rate: int = 60, vertical_overflow: str = "visible") -> None:
        """
        Stream markdown content without screen clearing or flashing.

        Args:
            iterator: An iterator yielding markdown content chunks
            refresh_rate: Number of refreshes per second
            vertical_overflow: How to handle content that exceeds the terminal height
                             ("visible", "crop", "ellipsis", or "fold")
        """
        with Live(
            console=self.console,
            refresh_per_second=refresh_rate,
            auto_refresh=True,
            vertical_overflow=vertical_overflow,
            transient=False,  # Ensures content remains after streaming ends
        ) as live:
            live.update(Markdown(""))

            # Stream and update content
            for chunk in iterator:
                self.content += chunk
                try:
                    md = Markdown(self.content)
                    live.update(md)
                except Exception:
                    # If markdown parsing fails (incomplete markdown), show as plain text
                    live.update(Text(self.content))

    def clear_content(self) -> None:
        """Clear the current content buffer."""
        self.content = ""

    def get_content(self) -> str:
        """
        Get the current content.

        Returns:
            The accumulated content as a string
        """
        return self.content
