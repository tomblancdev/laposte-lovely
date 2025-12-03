"""
Tests for ColorFieldSerializer.

This module tests the DRF serializer field for ColorField including:
- Validation of color formats in API requests
- Serialization and deserialization
- Error messages and validation errors
- Integration with DRF serializers
"""

from __future__ import annotations

import pytest
from rest_framework import serializers

from libs.db.serializers import ColorFieldSerializer


class TestColorFieldSerializer:
    """Test suite for ColorFieldSerializer."""

    def test_valid_hex_color(self):
        """Serializer should accept valid HEX colors."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("#FF5733")
        assert result == "#ff5733"  # Normalized to lowercase

    def test_valid_rgb_color(self):
        """Serializer should accept valid RGB colors."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("rgb(255, 87, 51)")
        assert result == "rgb(255, 87, 51)"

    def test_valid_rgba_color(self):
        """Serializer should accept valid RGBA colors."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("rgba(255, 87, 51, 0.8)")
        assert result == "rgba(255, 87, 51, 0.8)"

    def test_valid_hsl_color(self):
        """Serializer should accept valid HSL colors."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("hsl(9, 100%, 60%)")
        assert result == "hsl(9, 100%, 60%)"

    def test_valid_hsla_color(self):
        """Serializer should accept valid HSLA colors."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("hsla(9, 100%, 60%, 0.8)")
        assert result == "hsla(9, 100%, 60%, 0.8)"

    def test_valid_named_color(self):
        """Serializer should accept CSS named colors."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("red")
        assert result == "red"

    def test_invalid_color_raises_validation_error(self):
        """Serializer should raise ValidationError for invalid colors."""
        field = ColorFieldSerializer()
        with pytest.raises(serializers.ValidationError) as exc_info:
            field.to_internal_value("not-a-color")
        assert "Invalid color format" in str(exc_info.value)

    def test_normalization_to_lowercase(self):
        """Serializer should normalize colors to lowercase."""
        field = ColorFieldSerializer()
        assert field.to_internal_value("#FF5733") == "#ff5733"
        assert field.to_internal_value("RGB(255, 87, 51)") == "rgb(255, 87, 51)"
        assert field.to_internal_value("RED") == "red"

    def test_whitespace_trimming(self):
        """Serializer should trim whitespace from colors."""
        field = ColorFieldSerializer()
        assert field.to_internal_value("  #FF5733  ") == "#ff5733"
        assert field.to_internal_value(" red ") == "red"

    def test_blank_value_when_allowed(self):
        """Serializer should allow blank values when configured."""
        field = ColorFieldSerializer(allow_blank=True)
        result = field.to_internal_value("")
        assert result == ""

    def test_to_representation(self):
        """Serializer should convert internal values to API representation."""
        field = ColorFieldSerializer()
        assert field.to_representation("#ff5733") == "#ff5733"
        assert field.to_representation("red") == "red"
        assert field.to_representation(None) == ""


class TestColorFieldSerializerIntegration:
    """Test ColorFieldSerializer integration with DRF serializers."""

    def test_in_model_serializer(self):
        """ColorFieldSerializer should work in ModelSerializer context."""

        class ThemeSerializer(serializers.Serializer):
            primary_color = ColorFieldSerializer()
            secondary_color = ColorFieldSerializer(allow_blank=True)

        # Valid data
        serializer = ThemeSerializer(
            data={
                "primary_color": "#FF5733",
                "secondary_color": "rgb(100, 150, 200)",
            },
        )
        assert serializer.is_valid()
        assert serializer.validated_data["primary_color"] == "#ff5733"
        assert serializer.validated_data["secondary_color"] == "rgb(100, 150, 200)"

    def test_validation_errors_in_serializer(self):
        """Invalid colors should produce proper validation errors."""

        class ThemeSerializer(serializers.Serializer):
            color = ColorFieldSerializer()

        serializer = ThemeSerializer(data={"color": "invalid-color"})
        assert not serializer.is_valid()
        assert "color" in serializer.errors
        assert "Invalid color format" in str(serializer.errors["color"])

    def test_required_field_validation(self):
        """Required ColorFieldSerializer should reject missing values."""

        class ThemeSerializer(serializers.Serializer):
            color = ColorFieldSerializer(required=True)

        serializer = ThemeSerializer(data={})
        assert not serializer.is_valid()
        assert "color" in serializer.errors

    def test_optional_field_with_default(self):
        """Optional ColorFieldSerializer with default should work."""

        class ThemeSerializer(serializers.Serializer):
            color = ColorFieldSerializer(default="#000000")

        serializer = ThemeSerializer(data={})
        assert serializer.is_valid()
        assert serializer.validated_data["color"] == "#000000"

    def test_multiple_color_fields(self):
        """Multiple ColorFieldSerializer fields should work together."""

        class PaletteSerializer(serializers.Serializer):
            primary = ColorFieldSerializer()
            secondary = ColorFieldSerializer()
            accent = ColorFieldSerializer(allow_blank=True)

        serializer = PaletteSerializer(
            data={
                "primary": "#FF5733",
                "secondary": "rgb(100, 150, 200)",
                "accent": "",
            },
        )
        assert serializer.is_valid()

    def test_partial_update(self):
        """Partial updates should work with ColorFieldSerializer."""

        class ThemeSerializer(serializers.Serializer):
            primary_color = ColorFieldSerializer()
            secondary_color = ColorFieldSerializer()

        # Partial update with only one field
        serializer = ThemeSerializer(
            data={"primary_color": "#FF5733"},
            partial=True,
        )
        assert serializer.is_valid()
        assert serializer.validated_data["primary_color"] == "#ff5733"
        assert "secondary_color" not in serializer.validated_data


class TestColorFieldSerializerEdgeCases:
    """Test edge cases for ColorFieldSerializer."""

    def test_none_value_handling(self):
        """None values should be handled properly."""
        field = ColorFieldSerializer(allow_null=True)
        # DRF handles None differently, test representation
        assert field.to_representation(None) == ""

    def test_empty_string_vs_none(self):
        """Empty string and None should be handled differently."""
        field = ColorFieldSerializer(allow_blank=True, allow_null=False)
        result = field.to_internal_value("")
        assert result == ""

    def test_special_characters_in_color(self):
        """Special characters should be rejected."""
        field = ColorFieldSerializer()
        with pytest.raises(serializers.ValidationError):
            field.to_internal_value("#FF5733!")
        with pytest.raises(serializers.ValidationError):
            field.to_internal_value("rgb(255, 87, 51);")

    def test_transparent_named_color(self):
        """'transparent' named color should work."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("transparent")
        assert result == "transparent"

    def test_case_sensitivity_consistency(self):
        """Color names should be case-insensitive."""
        field = ColorFieldSerializer()
        assert field.to_internal_value("RED") == "red"
        assert field.to_internal_value("Red") == "red"
        assert field.to_internal_value("red") == "red"

    def test_hex_shorthand_normalization(self):
        """HEX shorthand should be preserved."""
        field = ColorFieldSerializer()
        result = field.to_internal_value("#FFF")
        assert result == "#fff"
        # Note: We don't expand #FFF to #FFFFFF, we preserve the format
