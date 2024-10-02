import os

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


def gitignore_on_complete(content: str, args: Args):
    with open(os.path.join(args.path, ".gitignore"), "w") as f:
        print(f"Writing .gitignore to {args.path}")
        _ = f.write(content)


class ActionManager:
    def __init__(self):
        self._actions = {
            "gitignore": Action(
                description="Generate a .gitignore file",
                prompt="""
# GitHub Copilot .gitignore Generator Prompt

Generate a comprehensive .gitignore file for a [LANGUAGE] project. Include:

1. Language-specific files and directories
2. IDE and editor files (VS Code, IntelliJ, etc.)
3. OS-specific files (macOS, Windows, Linux)
4. Build output and dependency directories
5. Environment and configuration files
6. Temporary and cache files

Additional requirements:
- Add comments explaining each section
- Sort entries alphabetically within sections
- Include commonly used test coverage and documentation tool outputs
- Do not output ``` or code blocks

For multiple languages, replace [LANGUAGE] with a comma-separated list:
Example: Generate a .gitignore for a Python, Node.js project

Usage tips:
1. Create a new file named `.gitignore`
2. Type the prompt at the top as a comment
3. Let Copilot generate the content
4. Review and adjust as needed

Sample prompt for a Python project:
```
# Generate a comprehensive .gitignore file for a Python project
```

Sample prompt for multiple languages:
```
# Generate a comprehensive .gitignore file for a Python, Java, Node.js project
```
""",
                system_prompt="",
                model="gpt-4o",
                on_complete=gitignore_on_complete,
                output_to_stdout=False,
            ),
            "lazygit-commitizen": Action(
                description="Generate a commit message with Commitizen",
                prompt="""
# AI Commit Message Generator

You are an expert Git user with deep experience in writing meaningful, conventional commit messages. Analyze the following diff and generate diverse, high-quality commit message suggestions.


## Input
```diff
$diff
```

## Context (if available)
Recent commits:
```
$logs
```

## Requirements

Convention: Use Conventional Commits format:

<type>(<optional scope>): <description>
Only use these types: feat, fix, docs, style, refactor, perf, test, chore
Scope is optional and should be relevant

Do not output anything other than the commit message.
Generate one message per line, indexed (e.g., 1:, 2:, 3:).


## Quality Criteria:

Be concise yet descriptive (aim for 50-72 characters)
Start with a lowercase verb
Focus on WHY over WHAT when relevant
Synthesize changes to a higher abstraction level
Avoid redundancy between type/scope and description


## Diversity in Suggestions:

Provide different perspectives and abstraction levels
Include both specific and general messages
Consider various impact types (user-facing, dev experience, performance)


## Example Output Format

1: feat(auth): implement OAuth2 login flow
2: fix(api): resolve race condition in data fetching
3: refactor: simplify error handling logic
4: perf(queries): optimize database joins for faster load

## Advanced Tips

Prioritize user impact over implementation details
If multiple changes exist, try both unified and split approaches
Consider future maintainers reading the git history

Remember: It's better to be insightful and occasionally wrong than consistently obvious. Focus on generating your absolute best suggestion, even if others might be less accurate.

Generate a maximum of 10 commit messages following the format above.
Focus on quality over quantity.
""",
                commands={
                    "diff": [
                        "git",
                        "-C",
                        "$path",
                        "diff",
                        "--no-color",
                        "--no-ext-diff",
                        "--cached",
                    ],
                    "logs": [
                        "git",
                        "-C",
                        "$path",
                        "log",
                        "-n",
                        "10",
                        "--pretty=format:'%h %s'",
                    ],
                },
                system_prompt="",
                model="gpt-4o",
            ),
        }

    def get_action(self, action: str) -> Action:
        if action not in self._actions:
            raise ValueError(f"Invalid action: {action}")
        return self._actions[action]

    def get_actions_list(self):
        return list(self._actions.keys())
