"""
Color Field Serializer for Django REST Framework

This module provides a serializer field for the ColorField model field.
It handles validation and serialization of color values in REST APIs.

Usage:
    from utils.db.serializers import ColorFieldSerializer

    class MyModelSerializer(serializers.ModelSerializer):
        background_color = ColorFieldSerializer()

        class Meta:
            model = MyModel
            fields = ['id', 'background_color']
"""

from rest_framework import serializers

from libs.db.colors import validate_color


class ColorFieldSerializer(serializers.CharField):
    """
    Serializer field for ColorField with comprehensive validation.

    This field validates color values in multiple formats:
    - HEX: #RGB, #RRGGBB, #RRGGBBAA
    - RGB: rgb(r, g, b)
    - RGBA: rgba(r, g, b, a)
    - HSL: hsl(h, s%, l%)
    - HSLA: hsla(h, s%, l%, a)
    - Named colors: CSS named colors (e.g., "red", "blue")

    The field automatically normalizes colors to lowercase for
    consistent storage and comparison.

    Attributes:
        max_length: Maximum length for the color string (default: 50)
        allow_blank: Whether blank values are allowed (default: True)
        trim_whitespace: Whether to trim whitespace (default: True)

    Examples:
        Basic usage in a serializer:

        >>> class ThemeSerializer(serializers.ModelSerializer):
        ...     primary_color = ColorFieldSerializer(required=True)
        ...     secondary_color = ColorFieldSerializer(allow_blank=True)
        ...
        ...     class Meta:
        ...         model = Theme
        ...         fields = ['primary_color', 'secondary_color']

        Valid inputs:
        >>> serializer = ThemeSerializer(data={
        ...     'primary_color': '#FF5733',
        ...     'secondary_color': 'rgba(255, 87, 51, 0.8)'
        ... })
        >>> serializer.is_valid()
        True

        Invalid inputs:
        >>> serializer = ThemeSerializer(data={
        ...     'primary_color': 'not-a-color'
        ... })
        >>> serializer.is_valid()
        False
        >>> serializer.errors
        {'primary_color': ['Invalid color format. Supported formats: ...']}

    Normalization:
        Colors are automatically normalized to lowercase:
        >>> field = ColorFieldSerializer()
        >>> field.to_internal_value('#FF5733')
        '#ff5733'
        >>> field.to_internal_value('RGB(255, 87, 51)')
        'rgb(255, 87, 51)'
    """

    def __init__(self, **kwargs: dict) -> None:
        """
        Initialize the ColorFieldSerializer.

        Args:
            **kwargs: Additional arguments for CharField
        """
        kwargs.setdefault("max_length", 50)
        kwargs.setdefault("allow_blank", True)
        kwargs.setdefault("trim_whitespace", True)
        super().__init__(**kwargs)

    def to_internal_value(self, data: str) -> str:
        """
        Convert input data to internal Python representation.

        Validates the color format and normalizes it to lowercase.

        Args:
            data: The input color string

        Returns:
            Normalized color string (lowercase)

        Raises:
            serializers.ValidationError: If color format is invalid
        """
        # Call parent to handle basic string validation
        value = super().to_internal_value(data)

        if not value and self.allow_blank:
            return value

        # Normalize to lowercase
        normalized_value = value.strip().lower()

        # Validate color format using the model field validator
        try:
            validate_color(normalized_value)
        except Exception as e:
            # Convert Django ValidationError to DRF ValidationError
            raise serializers.ValidationError(str(e)) from e

        return normalized_value

    def to_representation(self, value: str) -> str:
        """
        Convert internal value to representation for API output.

        Args:
            value: The internal color string

        Returns:
            The color string for API response
        """
        if value is None:
            return ""
        return str(value)


__all__ = ["ColorFieldSerializer"]
