# Model Metadata Extension API Contract

**Component**: Extended ModelMetadata  
**Version**: 1.0.0  
**Date**: 2025-11-18

## Overview

This contract defines the API for the extended ModelMetadata class, which adds enhanced model information fields for display in the interactive menu.

## Class: ModelMetadata (Extended)

### Extended Attributes

The existing `ModelMetadata` class is extended with the following optional attributes:

#### context_window

```python
context_window: Optional[str] = None
```

**Type**: `Optional[str]`

**Description**: Context window size in human-readable format.

**Validation**:
- Must be non-empty string if provided
- Should follow format: `"{number}{unit} tokens"` (e.g., "1M tokens", "200K tokens")

**Examples**:
- `"1M tokens"`
- `"200K tokens"`
- `"128K tokens"`
- `"32K tokens"`

**Display**: Shown in hover details panel

**Default**: `None` (not displayed if not provided)

#### pricing

```python
pricing: Optional[Dict[str, float]] = None
```

**Type**: `Optional[Dict[str, float]]`

**Description**: Pricing per token for input and output.

**Validation**:
- Must be dict if provided
- Must have "input" and/or "output" keys
- Values must be >= 0 (representing cost per 1K tokens)

**Format**:
```python
{
    "input": 0.0001,   # Cost per 1K input tokens
    "output": 0.0002  # Cost per 1K output tokens
}
```

**Examples**:
```python
# Both input and output
{"input": 0.0001, "output": 0.0002}

# Input only
{"input": 0.0001}

# Output only
{"output": 0.0002}
```

**Display**: Formatted as "Input: $X.XX/1K, Output: $Y.YY/1K" in hover details

**Default**: `None` (not displayed if not provided)

#### capabilities

```python
capabilities: Optional[List[str]] = None
```

**Type**: `Optional[List[str]]`

**Description**: Model capabilities and specializations.

**Validation**:
- Must be non-empty list if provided
- Each item must be non-empty string

**Examples**:
```python
["coding", "reasoning", "general-purpose"]
["code-generation", "debugging", "refactoring"]
["reasoning", "analysis", "planning"]
["general-purpose", "conversation"]
```

**Display**: Shown as comma-separated list or bullet points in hover details

**Default**: `None` (not displayed if not provided)

#### description

```python
description: Optional[str] = None
```

**Type**: `Optional[str]`

**Description**: Model description and use cases.

**Validation**:
- Must be non-empty string if provided
- Should be concise (1-3 sentences recommended)

**Examples**:
- `"Best for code generation and debugging tasks. Optimized for Python, JavaScript, and TypeScript."`
- `"General-purpose model with strong reasoning capabilities. Excellent for analysis and planning."`
- `"Specialized for code generation. Supports multiple programming languages and frameworks."`

**Display**: Shown in hover details panel

**Default**: `None` (not displayed if not provided)

## Methods

### to_dict() (Extended)

```python
def to_dict(self) -> Dict[str, Any]
```

**Description**: Converts ModelMetadata to dictionary, including new fields.

**Returns**:
- `Dict[str, Any]`: Dictionary with all attributes including new fields

**Behavior**:
- Includes all base ModelMetadata fields
- Includes new fields if they are not None
- Maintains backward compatibility

**Example**:
```python
metadata = ModelMetadata(
    model_id="gemini-2-5-pro",
    name="Gemini 2.5 Pro",
    provider="google",
    access_pattern="native_sdk",
    available_regions=["us-central1"],
    context_window="1M tokens",
    pricing={"input": 0.0001, "output": 0.0002},
    capabilities=["general-purpose", "coding"],
    description="Best for general tasks and code generation"
)

result = metadata.to_dict()
# Returns dict with all fields including new ones
```

## Validation

### Field Validation Rules

1. **context_window**:
   - If provided, must be non-empty string
   - Recommended format: `"{number}{unit} tokens"`

2. **pricing**:
   - If provided, must be dict
   - Must have at least one of: "input" or "output"
   - All values must be >= 0

3. **capabilities**:
   - If provided, must be non-empty list
   - All items must be non-empty strings

4. **description**:
   - If provided, must be non-empty string

### Backward Compatibility

- All new fields are optional
- Existing code continues to work without changes
- New fields default to None
- `to_dict()` includes new fields only if present

## Model Registry Updates

### MODEL_METADATA Dictionary

The `ModelRegistry.MODEL_METADATA` dictionary must be updated with new fields for all 7 models:

```python
MODEL_METADATA: Dict[str, ModelMetadata] = {
    "gemini-2-5-pro": ModelMetadata(
        model_id="gemini-2-5-pro",
        name="Gemini 2.5 Pro",
        provider="google",
        access_pattern="native_sdk",
        available_regions=["us-central1"],
        default_region="us-central1",
        latest_version="latest",
        versions=["latest"],
        # New fields
        context_window="1M tokens",
        pricing={"input": 0.0001, "output": 0.0002},
        capabilities=["general-purpose", "coding", "reasoning"],
        description="Best for general tasks, code generation, and complex reasoning"
    ),
    # ... other models
}
```

## Display Rules

### Hover Details Format

When displaying model information in hover details:

**Included**:
- ✅ Model Name & ID
- ✅ Context Window
- ✅ Pricing (if available)
- ✅ Capabilities
- ✅ Status (available/unavailable)
- ✅ Current Model Indicator (✓)
- ✅ Description

**Excluded** (per requirements):
- ❌ Region
- ❌ Access Pattern
- ❌ Provider

## Migration Guide

### Updating Existing Code

**No Changes Required**:
- Existing code using ModelMetadata continues to work
- New fields are optional and default to None
- No breaking changes

**Optional Updates**:
- Add new fields to MODEL_METADATA dictionary
- Update model metadata with enhanced information
- Use new fields in display/formatting code

### Example: Adding Metadata

```python
# Before (still works)
metadata = ModelMetadata(
    model_id="gemini-2-5-pro",
    name="Gemini 2.5 Pro",
    provider="google",
    access_pattern="native_sdk",
    available_regions=["us-central1"]
)

# After (with new fields)
metadata = ModelMetadata(
    model_id="gemini-2-5-pro",
    name="Gemini 2.5 Pro",
    provider="google",
    access_pattern="native_sdk",
    available_regions=["us-central1"],
    context_window="1M tokens",
    pricing={"input": 0.0001, "output": 0.0002},
    capabilities=["general-purpose", "coding"],
    description="Best for general tasks and code generation"
)
```

## Testing Contract

### Unit Tests

- Test field initialization
- Test field validation
- Test to_dict() with new fields
- Test backward compatibility
- Test None/default values

### Integration Tests

- Test ModelRegistry with extended metadata
- Test menu display with new fields
- Test hover details formatting

