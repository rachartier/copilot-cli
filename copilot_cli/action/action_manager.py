import yaml
from pydantic import BaseModel

from .model import Action


class ActionsYAML(BaseModel):
    actions: dict[str, Action]


class ActionManager:
    def __init__(self, config_path: str):
        self._actions = self.load_actions(config_path)

    def load_actions(self, config_path: str) -> dict[str, Action]:
        """
        Load actions from a YAML file.

        Args:
            config_path: Path to the YAML file.

        Returns:
            dict: A dictionary of actions.
        """
        with open(config_path, "r") as f:
            actions_config = ActionsYAML(**yaml.safe_load(f))

        return actions_config.actions

    def get_action(self, action: str) -> Action:
        """
        Get an action by name.

        Args:
            action: The name of the action.

        Returns:
            Action: The action object.
        """
        if action not in self._actions:
            raise ValueError(f"Invalid action: {action}")

        return self._actions[action]

    def get_actions_list(self) -> list[str]:
        """
        Get a list of all available actions.

        Returns:
            list: A list of action names.
        """
        return list(self._actions.keys())
