import yaml
from pydantic import BaseModel

from action.model import Action


class ActionsYAML(BaseModel):
    actions: dict[str, Action]


class ActionManager:
    def __init__(self, config_path: str):
        self._actions = self.load_actions(config_path)

    def load_actions(self, config_path: str) -> dict[str, Action]:
        with open(config_path, "r") as f:
            actions_config = ActionsYAML(**yaml.safe_load(f))

        return actions_config.actions

    def get_action(self, action: str) -> Action:
        if action not in self._actions:
            raise ValueError(f"Invalid action: {action}")
        return self._actions[action]

    def get_actions_list(self):
        return list(self._actions.keys())
