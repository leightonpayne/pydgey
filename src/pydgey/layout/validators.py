"""Field validators for layout elements."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """Result of a validation check.

    Attributes:
        valid: True if validation passed.
        message: Error message if validation failed.
    """

    valid: bool
    message: str = ""


@dataclass
class Validator:
    """Validator definition that can be serialized to frontend.

    Attributes:
        type: Validator type (required, minLength, maxLength, range, pattern, email, fileExtension).
        params: Parameters specific to the validator type.
        message: Error message to display on failure.
    """

    type: str
    params: Dict[str, Any]
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "params": self.params,
            "message": self.message,
        }


class Validators:
    """Factory for common validators."""

    @staticmethod
    def required(message: str = "This field is required") -> Validator:
        """Validate that a field has a value.

        Args:
            message: Error message if validation fails.
        """
        return Validator("required", {}, message)

    @staticmethod
    def min_length(length: int, message: str = "") -> Validator:
        """Validate minimum string length.

        Args:
            length: Minimum required length.
            message: Error message if validation fails.
        """
        return Validator(
            "minLength",
            {"length": length},
            message or f"Minimum {length} characters required",
        )

    @staticmethod
    def max_length(length: int, message: str = "") -> Validator:
        """Validate maximum string length.

        Args:
            length: Maximum allowed length.
            message: Error message if validation fails.
        """
        return Validator(
            "maxLength",
            {"length": length},
            message or f"Maximum {length} characters allowed",
        )

    @staticmethod
    def range(
        min_val: float,
        max_val: float,
        message: str = "",
    ) -> Validator:
        """Validate numeric value is within range.

        Args:
            min_val: Minimum allowed value.
            max_val: Maximum allowed value.
            message: Error message if validation fails.
        """
        return Validator(
            "range",
            {"min": min_val, "max": max_val},
            message or f"Must be between {min_val} and {max_val}",
        )

    @staticmethod
    def pattern(regex: str, message: str = "Invalid format") -> Validator:
        """Validate string matches a regex pattern.

        Args:
            regex: Regular expression pattern.
            message: Error message if validation fails.
        """
        return Validator("pattern", {"regex": regex}, message)

    @staticmethod
    def email(message: str = "Invalid email address") -> Validator:
        """Validate email address format.

        Args:
            message: Error message if validation fails.
        """
        return Validator("email", {}, message)

    @staticmethod
    def file_extension(
        extensions: List[str],
        message: str = "",
    ) -> Validator:
        """Validate file has an allowed extension.

        Args:
            extensions: List of allowed extensions (e.g., [".txt", ".csv"]).
            message: Error message if validation fails.
        """
        return Validator(
            "fileExtension",
            {"extensions": extensions},
            message or f"Allowed extensions: {', '.join(extensions)}",
        )

    @staticmethod
    def min_value(value: float, message: str = "") -> Validator:
        """Validate numeric value is at least a minimum.

        Args:
            value: Minimum allowed value.
            message: Error message if validation fails.
        """
        return Validator(
            "minValue",
            {"value": value},
            message or f"Must be at least {value}",
        )

    @staticmethod
    def max_value(value: float, message: str = "") -> Validator:
        """Validate numeric value is at most a maximum.

        Args:
            value: Maximum allowed value.
            message: Error message if validation fails.
        """
        return Validator(
            "maxValue",
            {"value": value},
            message or f"Must be at most {value}",
        )
