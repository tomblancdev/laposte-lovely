"""
Tests for ColorField model field.

This module tests the ColorField custom Django model field including:
- Validation of various color formats (HEX, RGB, RGBA, HSL, HSLA, named)
- Database storage and retrieval
- Edge cases and error handling
- Normalization and case sensitivity
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from libs.db.colors import CSS_NAMED_COLORS
from libs.db.colors import ColorField
from libs.db.colors import validate_color


class TestColorValidation:
    """Test suite for color validation function."""

    def test_empty_value_is_valid(self):
        """Empty strings should be valid (use blank=False to disallow)."""
        validate_color("")
        validate_color("   ")
        # Should not raise any exception

    def test_hex_3_digit_format(self):
        """3-digit HEX colors should be valid."""
        validate_color("#FFF")
        validate_color("#000")
        validate_color("#a1b")

    def test_hex_6_digit_format(self):
        """6-digit HEX colors should be valid."""
        validate_color("#FFFFFF")
        validate_color("#000000")
        validate_color("#FF5733")
        validate_color("#a1b2c3")

    def test_hex_8_digit_format_with_alpha(self):
        """8-digit HEX colors with alpha channel should be valid."""
        validate_color("#FFFFFFFF")
        validate_color("#FF5733FF")
        validate_color("#FF573380")

    def test_hex_without_hash_is_invalid(self):
        """HEX colors without # prefix should be invalid."""
        with pytest.raises(ValidationError):
            validate_color("FF5733")

    def test_hex_invalid_length(self):
        """HEX colors with invalid length should be invalid."""
        with pytest.raises(ValidationError):
            validate_color("#FF")
        with pytest.raises(ValidationError):
            validate_color("#FFFF")
        with pytest.raises(ValidationError):
            validate_color("#FFFFFFF")

    def test_hex_invalid_characters(self):
        """HEX colors with non-hex characters should be invalid."""
        with pytest.raises(ValidationError):
            validate_color("#GGGGGG")
        with pytest.raises(ValidationError):
            validate_color("#XYZ123")

    def test_rgb_format(self):
        """RGB colors should be valid."""
        validate_color("rgb(0, 0, 0)")
        validate_color("rgb(255, 255, 255)")
        validate_color("rgb(255, 87, 51)")
        validate_color("rgb(100,100,100)")  # No spaces

    def test_rgb_out_of_range(self):
        """RGB values outside 0-255 should be invalid."""
        with pytest.raises(ValidationError) as exc_info:
            validate_color("rgb(256, 0, 0)")
        assert "RGB values must be between 0 and 255" in str(exc_info.value)

        with pytest.raises(ValidationError):
            validate_color("rgb(-1, 100, 100)")

    def test_rgb_invalid_format(self):
        """Malformed RGB colors should be invalid."""
        with pytest.raises(ValidationError):
            validate_color("rgb(100, 100)")
        with pytest.raises(ValidationError):
            validate_color("rgb(100, 100, 100, 100)")

    def test_rgba_format(self):
        """RGBA colors should be valid."""
        validate_color("rgba(0, 0, 0, 0)")
        validate_color("rgba(255, 255, 255, 1)")
        validate_color("rgba(255, 87, 51, 0.8)")
        validate_color("rgba(100,100,100,0.5)")  # No spaces

    def test_rgba_alpha_range(self):
        """RGBA alpha values outside 0-1 should be invalid."""
        with pytest.raises(ValidationError) as exc_info:
            validate_color("rgba(100, 100, 100, 1.5)")
        assert "Alpha 0-1" in str(exc_info.value)

        with pytest.raises(ValidationError):
            validate_color("rgba(100, 100, 100, -0.1)")

    def test_hsl_format(self):
        """HSL colors should be valid."""
        validate_color("hsl(0, 0%, 0%)")
        validate_color("hsl(360, 100%, 100%)")
        validate_color("hsl(9, 100%, 60%)")
        validate_color("hsl(180,50%,50%)")  # No spaces

    def test_hsl_out_of_range(self):
        """HSL values outside valid ranges should be invalid."""
        with pytest.raises(ValidationError) as exc_info:
            validate_color("hsl(361, 50%, 50%)")
        assert "H 0-360" in str(exc_info.value)

        with pytest.raises(ValidationError):
            validate_color("hsl(180, 101%, 50%)")

        with pytest.raises(ValidationError):
            validate_color("hsl(180, 50%, 101%)")

    def test_hsla_format(self):
        """HSLA colors should be valid."""
        validate_color("hsla(0, 0%, 0%, 0)")
        validate_color("hsla(360, 100%, 100%, 1)")
        validate_color("hsla(9, 100%, 60%, 0.8)")
        validate_color("hsla(180,50%,50%,0.5)")  # No spaces

    def test_hsla_alpha_range(self):
        """HSLA alpha values outside 0-1 should be invalid."""
        with pytest.raises(ValidationError) as exc_info:
            validate_color("hsla(180, 50%, 50%, 1.5)")
        assert "Alpha 0-1" in str(exc_info.value)

    def test_named_colors(self):
        """CSS named colors should be valid."""
        validate_color("red")
        validate_color("blue")
        validate_color("transparent")
        validate_color("cornflowerblue")
        validate_color("RED")  # Case insensitive
        validate_color("Blue")

    def test_invalid_named_color(self):
        """Invalid color names should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_color("notacolor")
        assert "Invalid color format" in str(exc_info.value)

    def test_case_insensitive(self):
        """Color validation should be case insensitive."""
        validate_color("#FF5733")
        validate_color("#ff5733")
        validate_color("RGB(255, 87, 51)")
        validate_color("rgb(255, 87, 51)")
        validate_color("RED")
        validate_color("red")

    def test_all_css_named_colors(self):
        """All CSS named colors should be valid."""
        for color_name in CSS_NAMED_COLORS:
            validate_color(color_name)


@pytest.mark.django_db
class TestColorFieldModel:
    """Test suite for ColorField in actual Django models."""

    @pytest.fixture
    def test_model(self, db):
        """Create a test model with ColorField for testing."""

        # Create a test model dynamically
        class TestColorModel(models.Model):  # noqa: DJ008
            color = ColorField(max_length=50, blank=True, default="")

            class Meta:
                app_label = "tests"

        # Don't actually create the table, just use the model
        return TestColorModel

    def test_field_accepts_valid_hex(self, test_model):
        """ColorField should accept valid HEX colors."""
        instance = test_model(color="#FF5733")
        instance.full_clean()  # Validate
        assert instance.color == "#FF5733"

    def test_field_accepts_valid_rgb(self, test_model):
        """ColorField should accept valid RGB colors."""
        instance = test_model(color="rgb(255, 87, 51)")
        instance.full_clean()
        assert instance.color == "rgb(255, 87, 51)"

    def test_field_accepts_valid_rgba(self, test_model):
        """ColorField should accept valid RGBA colors."""
        instance = test_model(color="rgba(255, 87, 51, 0.8)")
        instance.full_clean()
        assert instance.color == "rgba(255, 87, 51, 0.8)"

    def test_field_accepts_valid_hsl(self, test_model):
        """ColorField should accept valid HSL colors."""
        instance = test_model(color="hsl(9, 100%, 60%)")
        instance.full_clean()
        assert instance.color == "hsl(9, 100%, 60%)"

    def test_field_accepts_named_color(self, test_model):
        """ColorField should accept CSS named colors."""
        instance = test_model(color="red")
        instance.full_clean()
        assert instance.color == "red"

    def test_field_rejects_invalid_color(self, test_model):
        """ColorField should reject invalid colors."""
        instance = test_model(color="not-a-color")
        with pytest.raises(ValidationError) as exc_info:
            instance.full_clean()
        assert "Invalid color format" in str(exc_info.value)

    def test_field_normalizes_to_lowercase(self, test_model):
        """ColorField should normalize colors to lowercase."""
        instance = test_model(color="#FF5733")
        # Use get_prep_value to simulate database preparation
        field = instance._meta.get_field("color")  # noqa: SLF001
        prepared = field.get_prep_value("#FF5733")
        assert prepared == "#ff5733"

    def test_field_allows_blank_when_configured(self, test_model):
        """ColorField should allow blank values when blank=True."""
        instance = test_model(color="")
        instance.full_clean()
        assert instance.color == ""

    def test_field_default_value(self):
        """ColorField should use default value when not specified."""

        class TestDefaultModel(models.Model):  # noqa: DJ008
            color = ColorField(default="#000000")

            class Meta:
                app_label = "tests"

        instance = TestDefaultModel()
        assert instance.color == "#000000"


class TestColorFieldDeconstruct:
    """Test ColorField migration support."""

    def test_deconstruct_returns_correct_path(self):
        """Deconstruct should return the correct import path."""
        field = ColorField()
        _name, path, _args, _kwargs = field.deconstruct()
        assert path == "utils.db.colors.ColorField"

    def test_deconstruct_preserves_kwargs(self):
        """Deconstruct should preserve field kwargs."""
        field = ColorField(max_length=100, default="#FFFFFF")
        _name, _path, _args, kwargs = field.deconstruct()
        assert kwargs["max_length"] == 100  # noqa: PLR2004
        assert kwargs["default"] == "#FFFFFF"


class TestColorFieldEdgeCases:
    """Test edge cases and special scenarios."""

    def test_whitespace_handling(self):
        """Color validation should handle whitespace properly."""
        validate_color("  #FF5733  ")
        validate_color(" rgb(255, 87, 51) ")
        validate_color("  red  ")

    def test_mixed_case_normalization(self):
        """Colors should be normalized regardless of case."""
        validate_color("#fF5733")
        validate_color("RGB(255, 87, 51)")
        validate_color("ReD")

    def test_special_named_colors(self):
        """Special named colors like transparent should work."""
        validate_color("transparent")
        validate_color("TRANSPARENT")

    def test_rgba_with_integer_alpha(self):
        """RGBA with integer alpha values (0 or 1) should work."""
        validate_color("rgba(255, 87, 51, 0)")
        validate_color("rgba(255, 87, 51, 1)")

    def test_hsla_with_integer_alpha(self):
        """HSLA with integer alpha values (0 or 1) should work."""
        validate_color("hsla(180, 50%, 50%, 0)")
        validate_color("hsla(180, 50%, 50%, 1)")
