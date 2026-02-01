"""Decorators for pipeline definition."""

from typing import Any, Callable


def action(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Mark a method as a UI action handler.

    Actions appear as buttons in the widget UI and can be triggered
    independently of the main pipeline run.

    Args:
        name: Unique identifier for the action.

    Example:
        class MyPipeline(Pipeline):
            @action("install_database")
            def install_db(self, logger):
                logger.info("Installing database...")
                return True
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._is_action = True
        func._action_name = name
        return func

    return decorator
