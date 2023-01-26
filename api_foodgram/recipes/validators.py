"""Custom validators."""

from re import search

from django.core.exceptions import ValidationError


def validate_hex_format_color(value):
    """Confirm the color HEX format."""
    if not search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", value):
        raise ValidationError(
            "HEX format of color is incorrect",
            params={"value": value},
        )
