"""
Color Field for Django Models

This module provides a custom Django model field for storing color values
in various formats: HEX, RGBA, HSLA, and named colors.

The ColorField validates color values and stores them as strings in the database.
It supports multiple color formats commonly used in CSS and web development.

Supported Formats:
    - HEX: #RRGGBB or #RRGGBBAA (e.g., "#FF5733", "#FF5733FF")
    - RGB: rgb(r, g, b) (e.g., "rgb(255, 87, 51)")
    - RGBA: rgba(r, g, b, a) (e.g., "rgba(255, 87, 51, 0.8)")
    - HSL: hsl(h, s%, l%) (e.g., "hsl(9, 100%, 60%)")
    - HSLA: hsla(h, s%, l%, a) (e.g., "hsla(9, 100%, 60%, 0.8)")
    - Named colors: CSS named colors (e.g., "red", "blue", "transparent")

Usage in Models:
    from utils.db import ColorField

    class MyModel(models.Model):
        background_color = ColorField(
            max_length=50,
            blank=True,
            default="",
            help_text="Background color in any CSS format"
        )
"""

import re
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# CSS named colors (subset of most commonly used)
# Full list: https://developer.mozilla.org/en-US/docs/Web/CSS/named-color
CSS_NAMED_COLORS = {
    "transparent",
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "black",
    "blanchedalmond",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgrey",
    "darkgreen",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkslategray",
    "darkslategrey",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
    "dimgray",
    "dimgrey",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    "ghostwhite",
    "gold",
    "goldenrod",
    "gray",
    "grey",
    "green",
    "greenyellow",
    "honeydew",
    "hotpink",
    "indianred",
    "indigo",
    "ivory",
    "khaki",
    "lavender",
    "lavenderblush",
    "lawngreen",
    "lemonchiffon",
    "lightblue",
    "lightcoral",
    "lightcyan",
    "lightgoldenrodyellow",
    "lightgray",
    "lightgrey",
    "lightgreen",
    "lightpink",
    "lightsalmon",
    "lightseagreen",
    "lightskyblue",
    "lightslategray",
    "lightslategrey",
    "lightsteelblue",
    "lightyellow",
    "lime",
    "limegreen",
    "linen",
    "magenta",
    "maroon",
    "mediumaquamarine",
    "mediumblue",
    "mediumorchid",
    "mediumpurple",
    "mediumseagreen",
    "mediumslateblue",
    "mediumspringgreen",
    "mediumturquoise",
    "mediumvioletred",
    "midnightblue",
    "mintcream",
    "mistyrose",
    "moccasin",
    "navajowhite",
    "navy",
    "oldlace",
    "olive",
    "olivedrab",
    "orange",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
    "paleturquoise",
    "palevioletred",
    "papayawhip",
    "peachpuff",
    "peru",
    "pink",
    "plum",
    "powderblue",
    "purple",
    "red",
    "rosybrown",
    "royalblue",
    "saddlebrown",
    "salmon",
    "sandybrown",
    "seagreen",
    "seashell",
    "sienna",
    "silver",
    "skyblue",
    "slateblue",
    "slategray",
    "slategrey",
    "snow",
    "springgreen",
    "steelblue",
    "tan",
    "teal",
    "thistle",
    "tomato",
    "turquoise",
    "violet",
    "wheat",
    "white",
    "whitesmoke",
    "yellow",
    "yellowgreen",
}

# Color value constants
RGB_MAX_VALUE = 255
HSL_HUE_MAX = 360
HSL_SATURATION_MAX = 100
HSL_LIGHTNESS_MAX = 100
ALPHA_MAX = 1

# Regex patterns for color formats
HEX_PATTERN = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB_PATTERN = re.compile(r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$")
RGBA_PATTERN = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([0-9]*\.?[0-9]+)\s*\)$",
)
HSL_PATTERN = re.compile(r"^hsl\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*\)$")
HSLA_PATTERN = re.compile(
    r"^hsla\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*,\s*([0-9]*\.?[0-9]+)\s*\)$",
)


def validate_color(value: str) -> None:
    """
    Validate that the value is a valid color in any supported format.

    Args:
        value: The color string to validate

    Raises:
        ValidationError: If the color format is invalid

    Supported Formats:
        - HEX: #RGB, #RRGGBB, #RRGGBBAA
        - RGB: rgb(r, g, b)
        - RGBA: rgba(r, g, b, a)
        - HSL: hsl(h, s%, l%)
        - HSLA: hsla(h, s%, l%, a)
        - Named colors: CSS named colors

    Examples:
        >>> validate_color("#FF5733")  # Valid HEX
        >>> validate_color("rgb(255, 87, 51)")  # Valid RGB
        >>> validate_color("rgba(255, 87, 51, 0.8)")  # Valid RGBA
        >>> validate_color("hsl(9, 100%, 60%)")  # Valid HSL
        >>> validate_color("red")  # Valid named color
        >>> validate_color("invalid")  # Raises ValidationError
    """
    if not value:
        # Empty values are allowed (use blank=False in field to disallow)
        return

    # Strip and normalize before further validation
    value = value.strip()

    # After stripping, check again if empty
    if not value:
        return

    value = value.lower()

    # Check for HEX format
    if HEX_PATTERN.match(value):
        return

    # Check for named colors
    if value in CSS_NAMED_COLORS:
        return

    # Check RGB format
    rgb_match = RGB_PATTERN.match(value)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        if all(0 <= c <= RGB_MAX_VALUE for c in (r, g, b)):
            return
        raise ValidationError(
            _("RGB values must be between 0 and %s") % RGB_MAX_VALUE,
            code="invalid_rgb_range",
        )
    # Check RGBA format
    rgba_match = RGBA_PATTERN.match(value)
    if rgba_match:
        r, g, b, a = rgba_match.groups()
        r, g, b, a = int(r), int(g), int(b), float(a)
        if all(0 <= c <= RGB_MAX_VALUE for c in (r, g, b)) and 0 <= a <= ALPHA_MAX:
            return
        raise ValidationError(
            _("RGBA values must be: RGB 0-%s, Alpha 0-%s") % (RGB_MAX_VALUE, ALPHA_MAX),
            code="invalid_rgba_range",
        )
    # Check HSL format
    hsl_match = HSL_PATTERN.match(value)
    if hsl_match:
        h, s, l = map(int, hsl_match.groups())  # noqa: E741
        if (
            0 <= h <= HSL_HUE_MAX
            and 0 <= s <= HSL_SATURATION_MAX
            and 0 <= l <= HSL_LIGHTNESS_MAX
        ):
            return
        raise ValidationError(
            _("HSL values must be: H 0-%s, S/L 0-%s%%")
            % (HSL_HUE_MAX, HSL_SATURATION_MAX),
            code="invalid_hsl_range",
        )
    # Check HSLA format
    hsla_match = HSLA_PATTERN.match(value)
    if hsla_match:
        h, s, l, a = hsla_match.groups()  # noqa: E741
        h, s, l, a = int(h), int(s), int(l), float(a)  # noqa: E741
        if (
            0 <= h <= HSL_HUE_MAX
            and 0 <= s <= HSL_SATURATION_MAX
            and 0 <= l <= HSL_LIGHTNESS_MAX
            and 0 <= a <= ALPHA_MAX
        ):
            return
        raise ValidationError(
            _("HSLA values must be: H 0-%s, S/L 0-%s%%, Alpha 0-%s")
            % (HSL_HUE_MAX, HSL_SATURATION_MAX, ALPHA_MAX),
            code="invalid_hsla_range",
        )

    # If none of the formats match, raise error
    raise ValidationError(
        _(
            "Invalid color format. Supported formats: "
            "#RRGGBB, #RRGGBBAA, rgb(r,g,b), rgba(r,g,b,a), "
            "hsl(h,s%,l%), hsla(h,s%,l%,a), or CSS named colors",
        ),
        code="invalid_color_format",
    )


class ColorField(models.CharField):
    """
    A Django model field for storing color values.

    This field extends CharField and adds validation for various color formats
    including HEX, RGB, RGBA, HSL, HSLA, and CSS named colors.

    The field stores colors as strings and validates them on save.
    It's compatible with all CharField options and queries.

    Attributes:
        max_length: Maximum length for the color string (default: 50)
        blank: Whether the field can be blank (default: True)
        default: Default value for the field (default: "")
        validators: List of validators including color validation

    Usage:
        class MyModel(models.Model):
            primary_color = ColorField(
                max_length=50,
                blank=True,
                default="#000000",
                help_text="Primary theme color"
            )

            background = ColorField(
                max_length=50,
                blank=False,  # Required field
                help_text="Background color"
            )

    Query Examples:
        # Filter by exact color
        MyModel.objects.filter(primary_color="#FF5733")

        # Filter by color format (contains)
        MyModel.objects.filter(primary_color__startswith="rgb")

        # Exclude specific colors
        MyModel.objects.exclude(primary_color="transparent")

    Serialization:
        Use the ColorFieldSerializer from utils.db.serializers for
        REST API serialization with proper validation.
    """

    description = _("Color value in HEX, RGB, RGBA, HSL, HSLA, or named format")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the ColorField with default values.

        Sets max_length to 50 if not specified, which is sufficient for
        most color formats including verbose ones like:
        "hsla(360, 100%, 100%, 1.0)"

        Args:
            *args: Positional arguments passed to CharField
            **kwargs: Keyword arguments passed to CharField
        """
        kwargs.setdefault("max_length", 50)
        super().__init__(*args, **kwargs)
        # Add color validator to the field's validators
        self.validators.append(validate_color)

    def deconstruct(self) -> tuple[str, str, list, dict]:
        """
        Return a 4-tuple for migrations and serialization.

        This method is used by Django's migration system to understand
        how to recreate this field.

        Returns:
            Tuple of (name, path, args, kwargs) for field reconstruction
        """
        name, _path, args, kwargs = super().deconstruct()
        # Use the ColorField path for migrations
        return name, "utils.db.colors.ColorField", args, kwargs

    def get_prep_value(self, value: Any) -> str | None:
        """
        Prepare the value for database storage.

        Converts the value to lowercase for consistent storage
        and comparison.

        Args:
            value: The color value to prepare

        Returns:
            The prepared value (lowercase string) or None
        """
        value = super().get_prep_value(value)
        if value:
            return value.strip().lower()
        return value

    def from_db_value(
        self,
        value: Any,
        expression: Any,
        connection: Any,
    ) -> str | None:
        """
        Convert value from database to Python object.

        Args:
            value: The value from the database
            expression: The query expression
            connection: The database connection

        Returns:
            The color string or None
        """
        if value is None:
            return value
        return str(value)

    def formfield(self, **kwargs: Any) -> Any:
        """
        Return a form field for this model field.

        Sets up the form field with appropriate widget and validation.

        Args:
            **kwargs: Additional arguments for the form field

        Returns:
            A form field instance for use in Django forms
        """

        defaults = {
            "form_class": forms.CharField,
            "max_length": self.max_length,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


__all__ = [
    "CSS_NAMED_COLORS",
    "ColorField",
    "validate_color",
]
