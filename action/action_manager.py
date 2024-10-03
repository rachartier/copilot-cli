from action.declared.gitignore import action as gitignore_action
from action.declared.lazygit_conventional_commit import action as lazygit_conventional_commit_action
from action.model import Action


class ActionManager:
    def __init__(self):
        self._actions = {
            "gitignore": gitignore_action,
            "lazygit-conventional-commit": lazygit_conventional_commit_action,
        }

    def get_action(self, action: str) -> Action:
        if action not in self._actions:
            raise ValueError(f"Invalid action: {action}")
        return self._actions[action]

    def get_actions_list(self):
        return list(self._actions.keys())
