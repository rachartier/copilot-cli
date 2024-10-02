import argparse
import subprocess
from typing import Callable

from action import Action, ActionManager
from args import Args
from constants import DEFAULT_SYSTEM_PROMPT
from copilot import GithubCopilotClient

action_manager = ActionManager()


OnCompleteCallable = Callable[[str, Args], None]


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
        "--prompt",
        type=str,
        help="Prompt to send to Copilot Chat",
    )
    _ = parser.add_argument(
        "--model",
        type=str,
        help="Model to use for the chat",
        default="gpt-4",
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
            print(result.stdout)
            print(f"Command failed for {key}")
            print(f"Error: {e}")
            raise

    return final_prompt


def handle_completion(
    client: GithubCopilotClient,
    prompt: str,
    model: str,
    system_prompt: str,
    action_obj: Action | None,
    args: Args,
) -> None:
    response = client.chat_completion(prompt, model, system_prompt)

    if action_obj:
        on_complete: OnCompleteCallable | None = getattr(action_obj, "on_complete", None)
        if on_complete is not None:
            on_complete(response, args)

        if action_obj and action_obj.output_to_stdout:
            print(response)
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

    if args.action:
        action_obj = action_manager.get_action(args.action)

        current_prompt = action_obj.prompt
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

    try:
        handle_completion(
            client,
            current_prompt,
            model,
            system_prompt,
            action_obj,
            args,
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"At line: {e.__traceback__.tb_lineno}")


if __name__ == "__main__":
    main()
