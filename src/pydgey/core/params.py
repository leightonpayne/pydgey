"""Typed parameter configuration.

Provides type-safe access to pipeline parameters using dataclasses.
"""

from dataclasses import field, fields
from typing import Any, Dict, Type, TypeVar, get_type_hints

T = TypeVar("T")


def typed_params(cls: Type[T]) -> Type[T]:
    """Decorator to create a typed parameter configuration class.

    This decorator wraps a `dataclass` to provide helper methods for
    instantiating it from the raw dictionary of values returned by the widget.

    It adds the following features:
    1.  **Type Coercion**: Automatically converts string values from the UI
        (e.g., "1.5", "true") into the correct Python types (`float`, `bool`)
        based on the dataclass type hints.
    2.  **Safe Defaults**: Falls back to dataclass defaults if values are missing.

    Example:
        ```python
        @typed_params
        @dataclass
        class MyParams:
            threads: int = 4
            output_name: str = "results"
            verbose: bool = False

        # In pipeline.run():
        params = MyParams.from_dict(params_dict)
        print(params.threads)  # Type-safe access
        ```

    Args:
        cls: The dataclass to wrap.

    Returns:
        The decorated class with added `from_dict` and `to_dict` methods.
    """

    @classmethod
    def from_dict(cls_: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from a dictionary of raw values.

        Args:
            data: Dictionary of parameter values (usually from the UI).

        Returns:
            An instance of the class with populated fields.
        """
        kwargs = {}

        for f in fields(cls_):
            name = f.name
            if name in data:
                value = data[name]
                kwargs[name] = _coerce_type(value, f.type)
            elif f.default is not field:
                # Use the default from the dataclass
                pass  # Will be set by dataclass
            elif f.default_factory is not field:
                pass  # Will be set by dataclass

        return cls_(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the instance back to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary of field names and values.
        """
        return {f.name: getattr(self, f.name) for f in fields(self)}

    cls.from_dict = from_dict
    cls.to_dict = to_dict

    return cls


def _coerce_type(value: Any, target_type: Any) -> Any:
    """Coerce a value to the target type.

    Handles common type conversions from widget values (which are often strings)
    to Python native types.
    """
    if value is None:
        return None

    # Get the actual type (handle Optional, etc.)
    origin = getattr(target_type, "__origin__", None)
    if origin is type(None):
        return None

    # Handle Optional types
    if origin is type(None) or (
        hasattr(target_type, "__args__") and type(None) in target_type.__args__
    ):
        # It's Optional[X], get X
        args = getattr(target_type, "__args__", ())
        for arg in args:
            if arg is not type(None):
                target_type = arg
                break

    # Already correct type
    if isinstance(value, target_type) if isinstance(target_type, type) else False:
        return value

    # Type coercion
    if target_type is int:
        return int(value) if value != "" else 0
    elif target_type is float:
        return float(value) if value != "" else 0.0
    elif target_type is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)
    elif target_type is str:
        return str(value) if value is not None else ""

    # For other types, return as-is
    return value


class ParamsBase:
    """Base class alternative for typed parameters.

    Instead of using the `@typed_params` decorator, you can subclass this
    convenience class.

    Example:
        ```python
        @dataclass
        class MyParams(ParamsBase):
            threads: int = 4
            output_name: str = "results"
        ```
    """

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from a dictionary of raw values.

        Args:
            data: Dictionary of values.

        Returns:
             Instance of the class.
        """
        kwargs = {}

        # Get type hints for the class
        hints = get_type_hints(cls)

        for f in fields(cls):
            name = f.name
            if name in data:
                value = data[name]
                target_type = hints.get(name, str)
                kwargs[name] = _coerce_type(value, target_type)

        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dict[str, Any]: Encoded dictionary.
        """
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a parameter value with optional default.

        Args:
            key: Parameter name.
            default: Value to return if key is missing.
        """
        return getattr(self, key, default)
