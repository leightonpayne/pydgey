"""Form field definitions for pipeline UIs."""

from typing import Any, List, Optional, Tuple

from .elements import UIElement
from .validators import Validator


class Field:
    """Factory methods for creating form field components in the layout.

    The `Field` class provides static methods to define various input widgets,
    such as text boxes, dropdowns, and file uploaders. These definitions are
    used to construct the [UIElement](../api/layout.md#pydgey.layout.elements.UIElement) objects
    required by the layout system.

    Example:
        ```python
        Field.Text("name", "Project Name")
        Field.Int("threads", "Threads", default=4, min=1, max=32)
        ```
    """

    @staticmethod
    def _create(
        type_name: str,
        name: str,
        label: str,
        visible_when: Optional[Tuple[str, str, Any]] = None,
        validators: Optional[List[Validator]] = None,
        **kwargs: Any,
    ) -> UIElement:
        """Internal helper to create field elements."""
        props: dict[str, Any] = {
            "name": name,
            "label": label,
            "type": type_name,
            **kwargs,
        }

        if validators:
            props["validators"] = [v.to_dict() for v in validators]

        return UIElement("field", props=props, visible_when=visible_when)

    @staticmethod
    def Text(
        name: str,
        label: str,
        default: str = "",
        placeholder: str = "",
        description: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
        validators: Optional[List[Validator]] = None,
    ) -> UIElement:
        """Create a simple single-line text input field.

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            default: Initial value.
            placeholder: Text shown when the field is empty.
            description: Helper text displayed below the field.
            visible_when: Conditional visibility rule (see [Layouts Guide](../guides/layouts.md)).
            validators: List of validation rules.

        Returns:
            UIElement: A configured field element.
        """
        return Field._create(
            "text",
            name,
            label,
            default=default,
            placeholder=placeholder,
            description=description,
            visible_when=visible_when,
            validators=validators,
        )

    @staticmethod
    def Int(
        name: str,
        label: str,
        default: int = 0,
        description: str = "",
        min: Optional[int] = None,
        max: Optional[int] = None,
        visible_when: Optional[Tuple[str, str, Any]] = None,
        validators: Optional[List[Validator]] = None,
    ) -> UIElement:
        """Create a numeric input field for integers.

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            default: Initial value.
            description: Helper text displayed below the field.
            min: Minimum allowed value (inclusive).
            max: Maximum allowed value (inclusive).
            visible_when: Conditional visibility rule.
            validators: List of validation rules.
        """
        return Field._create(
            "int",
            name,
            label,
            default=default,
            description=description,
            min=min,
            max=max,
            visible_when=visible_when,
            validators=validators,
        )

    @staticmethod
    def Float(
        name: str,
        label: str,
        default: float = 0.0,
        description: str = "",
        min: Optional[float] = None,
        max: Optional[float] = None,
        step: Optional[float] = None,
        visible_when: Optional[Tuple[str, str, Any]] = None,
        validators: Optional[List[Validator]] = None,
    ) -> UIElement:
        """Create a numeric input field for floating-point numbers.

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            default: Initial value.
            description: Helper text displayed below the field.
            min: Minimum allowed value.
            max: Maximum allowed value.
            step: Step increment for the spinner controls.
            visible_when: Conditional visibility rule.
            validators: List of validation rules.
        """
        return Field._create(
            "float",
            name,
            label,
            default=default,
            description=description,
            min=min,
            max=max,
            step=step,
            visible_when=visible_when,
            validators=validators,
        )

    @staticmethod
    def Switch(
        name: str,
        label: str,
        default: bool = False,
        description: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a boolean toggle switch.

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            default: Initial state (True for on, False for off).
            description: Helper text displayed below the field.
            visible_when: Conditional visibility rule.
        """
        return Field._create(
            "switch",
            name,
            label,
            default=default,
            description=description,
            visible_when=visible_when,
        )

    @staticmethod
    def Select(
        name: str,
        label: str,
        options: List[str],
        default: Optional[str] = None,
        description: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a dropdown selection menu.

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            options: List of string options to choose from.
            default: Default selected option. If None, the first option is used.
            description: Helper text displayed below the field.
            visible_when: Conditional visibility rule.
        """
        return Field._create(
            "select",
            name,
            label,
            options=options,
            default=default or (options[0] if options else ""),
            description=description,
            visible_when=visible_when,
        )

    @staticmethod
    def MultiSelect(
        name: str,
        label: str,
        options: List[str],
        default: Optional[List[str]] = None,
        description: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a multi-select field (e.g., checkboxes or tags input).

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            options: List of available options.
            default: List of initially selected options.
            description: Helper text displayed below the field.
            visible_when: Conditional visibility rule.
        """
        return Field._create(
            "multiselect",
            name,
            label,
            options=options,
            default=default or [],
            description=description,
            visible_when=visible_when,
        )

    @staticmethod
    def File(
        name: str,
        label: str,
        accept: Optional[List[str]] = None,
        multiple: bool = False,
        description: str = "",
        visible_when: Optional[Tuple[str, str, Any]] = None,
        validators: Optional[List[Validator]] = None,
    ) -> UIElement:
        """Create a file picker field.

        The file picker allows users to select files from the server-side filesystem
        (where the Python kernel is running).

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            accept: List of allowed file extensions (e.g., `['.csv', '.txt']`).
            multiple: Whether to allow selecting multiple files.
            description: Helper text displayed below the field.
            visible_when: Conditional visibility rule.
            validators: List of validation rules.
        """
        return Field._create(
            "file",
            name,
            label,
            accept=accept,
            multiple=multiple,
            description=description,
            visible_when=visible_when,
            validators=validators,
        )

    @staticmethod
    def TextArea(
        name: str,
        label: str,
        default: str = "",
        placeholder: str = "",
        description: str = "",
        rows: int = 4,
        visible_when: Optional[Tuple[str, str, Any]] = None,
        validators: Optional[List[Validator]] = None,
    ) -> UIElement:
        """Create a multi-line text area input.

        Args:
            name: Unique identifier for the parameter key.
            label: Display label for the field.
            default: Initial text content.
            placeholder: Text shown when the field is empty.
            description: Helper text displayed below the field.
            rows: Initial height in text rows.
            visible_when: Conditional visibility rule.
            validators: List of validation rules.
        """
        return Field._create(
            "textarea",
            name,
            label,
            default=default,
            placeholder=placeholder,
            description=description,
            rows=rows,
            visible_when=visible_when,
            validators=validators,
        )
