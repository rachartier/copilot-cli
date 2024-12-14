import argparse
import os
import subprocess

from rich.console import Console
from rich.markdown import Markdown

from copilot_cli.action.action_manager import ActionManager
from copilot_cli.action.model import Action
from copilot_cli.args import Args
from copilot_cli.constants import DEFAULT_SYSTEM_PROMPT
from copilot_cli.copilot import GithubCopilotClient
from copilot_cli.log import CopilotCLILogger
from copilot_cli.streamer.markdown import MarkdownStreamer, StreamOptions


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller

    Args:
        relative_path: The relative path to the resource file

    Returns:
        str: The absolute path to the resource
    """
    base_path: str

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, str(relative_path))


action_manager = ActionManager(resource_path("actions.yml"))


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        capture_output=True,
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for Copilot Chat")
    _ = parser.add_argument(
        "--path",
        type=str,
        help="path to run the action in",
        default=".",
    )
    _ = parser.add_argument(
        "--list",
        action="store_true",
        help="List available actions",
    )
    _ = parser.add_argument(
        "--prompt",
        type=str,
        help="Prompt to send to Copilot Chat",
    )
    _ = parser.add_argument(
        "--model",
        type=str,
        help="Model to use for the chat",
        default="gpt-4o",
    )
    _ = parser.add_argument(
        "--system_prompt",
        type=str,
        help="System prompt to send to Copilot Chat",
        default=DEFAULT_SYSTEM_PROMPT,
    )
    _ = parser.add_argument(
        "--action",
        type=str,
        help="Action to perform",
        choices=action_manager.get_actions_list(),
    )
    _ = parser.add_argument(
        "--nostream",
        action="store_true",
        help="Disable streaming",
    )
    return parser


def process_action_commands(
    action_obj: Action,
    base_prompt: str,
    path: str,
) -> str:
    final_prompt = base_prompt
    commands: dict[str, list[str]] | None = getattr(action_obj, "commands", None)

    if not commands:
        return final_prompt

    for key, cmd in commands.items():
        try:
            cmd_with_path = [c.replace("$path", path) for c in cmd]
            result = run_command(cmd_with_path)
            final_prompt = final_prompt.replace(f"${key}", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Command failed for {key}")
            print(f"Error: {e}")
            raise

    return final_prompt


def create_streamer(options: StreamOptions | None = None) -> MarkdownStreamer:
    """
    Create a configured markdown streamer.

    Args:
        options: Optional dictionary of console options

    Returns:
        Configured MarkdownStreamer instance
    """
    streamer = MarkdownStreamer()
    if options:
        streamer.set_console_options(**options)
    return streamer


def handle_completion(
    client: GithubCopilotClient,
    prompt: str,
    model: str,
    system_prompt: str,
    action_obj: Action | None,
    args: Args,
    stream_options: StreamOptions | None = None,
) -> None:
    if not args.nostream and action_obj and action_obj.stream:
        streamer = create_streamer(stream_options)
        streamer.stream(client.stream_chat_completion(prompt=prompt, model=model, system_prompt=system_prompt))

        response = streamer.get_content()
    else:
        response = client.chat_completion(prompt=prompt, model=model, system_prompt=system_prompt)

    if action_obj:
        if action_obj.output.to_file:
            file = action_obj.output.to_file
            file = file.replace("$path", args.path)

            with open(file, "w") as f:
                _ = f.write(response)
                CopilotCLILogger.log_success(f"Output written to {file}")
        if args.nostream or not action_obj.stream:
            Console().print(Markdown(response))
    else:
        print(response)


def main() -> None:
    args = create_parser().parse_args()
    args = Args(**vars(args))

    client = GithubCopilotClient()

    current_prompt: str = args.prompt or ""
    action_obj: Action | None = None
    system_prompt: str
    model: str

    if args.list:
        print("Available actions:")
        for action in action_manager.get_actions_list():
            print(f"  - {action}: {action_manager.get_action(action).description}")
        return

    if args.action:
        action_obj = action_manager.get_action(args.action)

        current_prompt = action_obj.prompt

        if args.prompt:
            current_prompt += f"\n{args.prompt}"

        system_prompt = action_obj.system_prompt
        model = action_obj.model or args.model

        try:
            current_prompt = process_action_commands(
                action_obj,
                current_prompt,
                args.path,
            )
        except subprocess.CalledProcessError:
            return
    else:
        system_prompt = args.system_prompt
        model = args.model

    handle_completion(
        client,
        current_prompt,
        model,
        system_prompt,
        action_obj,
        args,
    )


if __name__ == "__main__":
    main()
