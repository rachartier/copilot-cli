import os

from action.model import Action
from args import Args


def gitignore_on_complete(content: str, args: Args):
    with open(os.path.join(args.path, ".gitignore"), "w") as f:
        print(f"Writing .gitignore to {args.path}")
        _ = f.write(content)


action = Action(
    description="Generate a .gitignore file",
    system_prompt="""
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
    prompt="",
    model="gpt-4o",
    on_complete=gitignore_on_complete,
    output_to_stdout=False,
)
