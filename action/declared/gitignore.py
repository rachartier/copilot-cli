import os

from args import Args


def gitignore_on_complete(content: str, args: Args):
    with open(os.path.join(args.path, ".gitignore"), "w") as f:
        print(f"Writing .gitignore to {args.path}")
        _ = f.write(content)
