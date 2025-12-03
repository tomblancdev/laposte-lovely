# Utils Package

This package contains reusable utilities for the django_overtuned project.

## ColorField

A Django model field for storing and validating color values in multiple formats.

### Features

- **Multiple Color Formats**: Supports HEX, RGB, RGBA, HSL, HSLA, and CSS named colors
- **Automatic Validation**: Validates color syntax and value ranges
- **Case Normalization**: Automatically normalizes colors to lowercase
- **DRF Integration**: Includes serializer field for REST APIs
- **Comprehensive Tests**: 59 tests covering all formats and edge cases

### Supported Color Formats

| Format | Example | Description |
|--------|---------|-------------|
| HEX (3-digit) | `#FFF` | Short hexadecimal notation |
| HEX (6-digit) | `#FF5733` | Full hexadecimal notation |
| HEX (8-digit) | `#FF5733FF` | Hexadecimal with alpha channel |
| RGB | `rgb(255, 87, 51)` | Red, Green, Blue (0-255) |
| RGBA | `rgba(255, 87, 51, 0.8)` | RGB with alpha (0-1) |
| HSL | `hsl(9, 100%, 60%)` | Hue (0-360), Saturation, Lightness (0-100%) |
| HSLA | `hsla(9, 100%, 60%, 0.8)` | HSL with alpha (0-1) |
| Named Colors | `red`, `blue`, `transparent` | CSS named colors (147 supported) |

### Usage in Models

```python
from django.db import models
from utils.db import ColorField

class Theme(models.Model):
    primary_color = ColorField(
        max_length=50,
        blank=True,
        default="#000000",
        help_text="Primary theme color"
    )
    
    background_color = ColorField( 
        max_length=50,
        blank=False,  # Required field
        help_text="Background color"
    )
```

### Usage in Serializers

```python
from rest_framework import serializers
from utils.db.serializers import ColorFieldSerializer

class ThemeSerializer(serializers.ModelSerializer):
    primary_color = ColorFieldSerializer()
    accent_color = ColorFieldSerializer(allow_blank=True)
    
    class Meta:
        model = Theme
        fields = ['id', 'primary_color', 'accent_color']
```

### Validation Examples

```python
from utils.db.colors import validate_color

# Valid colors
validate_color("#FF5733")                    # ✓ HEX
validate_color("rgb(255, 87, 51)")           # ✓ RGB
validate_color("rgba(255, 87, 51, 0.8)")     # ✓ RGBA
validate_color("hsl(9, 100%, 60%)")          # ✓ HSL
validate_color("hsla(9, 100%, 60%, 0.8)")    # ✓ HSLA
validate_color("red")                         # ✓ Named color
validate_color("")                            # ✓ Empty (if blank=True)

# Invalid colors (raise ValidationError)
validate_color("not-a-color")                # ✗ Invalid format
validate_color("#GGGGGG")                    # ✗ Invalid hex
validate_color("rgb(256, 0, 0)")             # ✗ Out of range
validate_color("rgba(100, 100, 100, 1.5)")   # ✗ Alpha out of range
validate_color("hsl(361, 50%, 50%)")         # ✗ Hue out of range
```

### API Usage Examples

```bash
# Create with HEX color
POST /api/email-folder-personalizations/
{
    "folder": 5,
    "display_name": "Work Stuff",
    "display_color": "#3498db"
}

# Create with RGB color
POST /api/email-folder-personalizations/
{
    "folder": 6,
    "display_name": "Personal",
    "display_color": "rgb(52, 152, 219)"
}

# Create with RGBA color (semi-transparent)
POST /api/email-folder-personalizations/
{
    "folder": 7,
    "display_name": "Archive",
    "display_color": "rgba(100, 100, 100, 0.5)"
}

# Create with named color
POST /api/email-folder-personalizations/
{
    "folder": 8,
    "display_name": "Important",
    "display_color": "red"
}
```

### Database Storage

- Colors are stored as strings in the database
- Automatically normalized to lowercase
- Field uses `CharField` as base, supports all standard CharField options
- Default max_length is 50 characters (sufficient for all formats)

### Validation Rules

| Format | Validation Rules |
|--------|-----------------|
| HEX | Must start with #, followed by 3, 6, or 8 hex digits |
| RGB | Values must be 0-255 for each channel |
| RGBA | RGB values 0-255, Alpha 0-1 |
| HSL | Hue 0-360, Saturation/Lightness 0-100% |
| HSLA | HSL + Alpha 0-1 |
| Named | Must be a valid CSS named color |

### Testing

The ColorField has comprehensive test coverage:

```bash
# Run ColorField tests
cd /app/backend
python -m pytest utils/tests/test_color_field.py -v

# Run ColorFieldSerializer tests
python -m pytest utils/tests/test_color_serializer.py -v

# Run all utils tests
python -m pytest utils/tests/ -v
```

Test coverage includes:

- ✓ All color format validations
- ✓ Range validations (RGB 0-255, HSL 0-360, Alpha 0-1)
- ✓ Case insensitivity
- ✓ Whitespace handling
- ✓ Edge cases (empty values, special characters)
- ✓ Django model field behavior
- ✓ DRF serializer integration
- ✓ Error messages and validation errors

### Migration Support

ColorField properly implements Django's `deconstruct()` method for migrations:

```python
# Generated migration will look like:
migrations.AddField(
    model_name='emailfolderpersonalization',
    name='display_color',
    field=utils.db.colors.ColorField(
        blank=True,
        default='',
        max_length=50,
        help_text='The display color for this email folder...'
    ),
)
```

### Implementation Details

**File Structure:**

```
utils/
├── __init__.py
├── db/
│   ├── __init__.py
│   ├── colors.py              # ColorField model field
│   └── serializers/
│       ├── __init__.py
│       └── color_serializer.py # ColorFieldSerializer for DRF
└── tests/
    ├── __init__.py
    ├── test_color_field.py     # Model field tests
    └── test_color_serializer.py # Serializer tests
```

**Key Components:**

- `validate_color()`: Standalone validation function
- `ColorField`: Django model field class
- `ColorFieldSerializer`: DRF serializer field class
- `CSS_NAMED_COLORS`: Set of 147 supported named colors

### Example: EmailFolderPersonalization

The ColorField is used in the `EmailFolderPersonalization` model:

```python
class EmailFolderPersonalization(models.Model):
    folder = models.OneToOneField(EmailFolder, ...)
    display_name = models.CharField(max_length=255, ...)
    
    display_color = ColorField(
        max_length=50,
        blank=True,
        verbose_name=_("Display Color"),
        help_text=_(
            "The display color for this email folder. "
            "Supports HEX (#RRGGBB), RGB, RGBA, HSL, HSLA, "
            "and CSS named colors."
        ),
        default="",
    )
```

And its serializer:

```python
class EmailFolderPersonalizationSerializer(
    UserTaggitSerializer,
    serializers.ModelSerializer[EmailFolderPersonalization],
):
    tags = UserTagListSerializerField()
    display_color = ColorFieldSerializer()  # Automatic validation!
    
    class Meta:
        model = EmailFolderPersonalization
        fields = ["id", "folder", "display_name", "display_color", "tags"]
```

### Benefits Over Manual Validation

**Before (Manual validation in serializer):**

```python
def validate_display_color(self, value: str) -> str:
    if value and not value.startswith("#"):
        raise serializers.ValidationError("Color must be in HEX format")
    if value and len(value) != 7:
        raise serializers.ValidationError("Color must be 7 characters")
    # Only validates HEX format!
    return value
```

**After (ColorField):**

```python
display_color = ColorField(max_length=50)  # In model
display_color = ColorFieldSerializer()     # In serializer
# Validates HEX, RGB, RGBA, HSL, HSLA, and named colors automatically!
```

### Performance

- Validation uses compiled regex patterns for efficiency
- Minimal overhead compared to CharField
- No external dependencies (pure Python + Django)
- Indexed lookups work normally (same as CharField)

### Future Enhancements

Potential improvements for future versions:

- Color conversion utilities (RGB to HEX, etc.)
- Color manipulation (lighten, darken, etc.)
- Accessibility contrast ratio calculation
- Color palette generation
- Support for CSS `currentColor` keyword
