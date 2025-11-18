# Data Model: Gemini CLI Custom `/model` Command

**Feature**: Gemini CLI Custom `/model` Command  
**Date**: 2025-11-18

## Overview

This document defines the core entities, their attributes, relationships, and validation rules for the Gemini CLI Custom `/model` Command feature. This extends the existing Vertex Adapter data model with enhanced model metadata and interactive menu state.

## Core Entities

### Extended ModelMetadata

Extends the existing `ModelMetadata` class with additional fields for enhanced model information display in the interactive menu.

**Base Attributes** (from existing ModelMetadata):
- `model_id` (string, required): Model identifier
- `name` (string, required): Human-readable model name
- `provider` (string, required): Provider name (internal use only, not displayed)
- `access_pattern` (string, required): Access pattern (internal use only, not displayed)
- `available_regions` (List[str], required): List of regions where model is available (internal use only, not displayed)
- `default_region` (string, optional): Default region for this model (internal use only, not displayed)
- `latest_version` (string, optional): Latest version identifier
- `versions` (List[str], optional): List of available versions

**New Attributes** (for interactive menu):
- `context_window` (string, optional): Context window size in human-readable format
  - Validation: Must be non-empty string if provided
  - Examples: `"1M tokens"`, `"200K tokens"`, `"128K tokens"`
  - Display: Shown in hover details
  
- `pricing` (Dict[str, float], optional): Pricing per token
  - Format: `{"input": 0.0001, "output": 0.0002}` (per 1K tokens)
  - Validation: Must have "input" and/or "output" keys, values must be >= 0
  - Display: Formatted as "Input: $X.XX/1K, Output: $Y.YY/1K" in hover details
  
- `capabilities` (List[str], optional): Model capabilities and specializations
  - Validation: Must be non-empty list if provided
  - Examples: `["coding", "reasoning", "general-purpose"]`, `["code-generation", "debugging"]`
  - Display: Shown as comma-separated list in hover details
  
- `description` (string, optional): Model description and use cases
  - Validation: Must be non-empty string if provided
  - Examples: `"Best for code generation and debugging tasks"`, `"Optimized for reasoning and analysis"`
  - Display: Shown in hover details

**Relationships**:
- One-to-many with `MenuState`: ModelMetadata used to populate menu
- One-to-one with `CurrentModel`: One model can be current at a time

**State Transitions**: None (immutable after creation)

**Validation Rules**:
- All base attributes must follow existing ModelMetadata validation
- New optional fields can be None or empty
- If provided, new fields must pass their specific validation
- No breaking changes to existing ModelMetadata usage

### MenuState

Represents the current state of the interactive menu, including selection, navigation, and display preferences.

**Attributes**:
- `models` (List[ModelMetadata], required): List of all available models
  - Validation: Must be non-empty list
  - Source: From ModelRegistry.get_available_models()
  
- `current_model_id` (string, optional): Currently active model ID
  - Validation: Must be valid model_id from models list if provided
  - Source: From ConfigurationManager.get_config().model.id
  
- `selected_index` (integer, required): Currently highlighted model index
  - Validation: Must be >= 0 and < len(models)
  - Default: 0 (first model) or index of current_model_id if available
  
- `menu_start_index` (integer, required): First visible model index (for scrolling)
  - Validation: Must be >= 0 and < len(models)
  - Default: 0
  
- `visible_count` (integer, required): Number of models visible in menu
  - Validation: Must be > 0 and <= len(models)
  - Default: Calculated from terminal height
  
- `hover_details_model_id` (string, optional): Model ID for which hover details are displayed
  - Validation: Must be valid model_id from models list if provided
  - Default: None (no hover details) or selected_index model

**Relationships**:
- Many-to-one with ModelMetadata: MenuState contains list of ModelMetadata
- One-to-one with CurrentModel: MenuState tracks current model

**State Transitions**:
- `navigate_up()`: Decrements selected_index (wraps to end)
- `navigate_down()`: Increments selected_index (wraps to start)
- `select_model()`: Sets current_model_id to selected model
- `update_hover()`: Sets hover_details_model_id to selected model

**Validation Rules**:
- selected_index must always be valid
- menu_start_index must keep selected_index visible
- All model IDs must exist in models list

### CurrentModel

Represents the currently active model in the system.

**Attributes**:
- `model_id` (string, required): Active model identifier
  - Validation: Must be valid model_id from ModelRegistry
  - Source: From ConfigurationManager.get_config().model.id
  
- `model_metadata` (ModelMetadata, required): Full metadata for current model
  - Validation: Must be valid ModelMetadata object
  - Source: From ModelRegistry.get_model_metadata(model_id)
  
- `region` (string, required): Active region for current model
  - Validation: Must be valid region from model_metadata.available_regions
  - Source: From ConfigurationManager.get_config().region or model_metadata.default_region
  
- `version` (string, optional): Active model version
  - Validation: Must be valid version from model_metadata.versions if provided
  - Source: From ConfigurationManager.get_config().model.version or model_metadata.latest_version

**Relationships**:
- One-to-one with ModelMetadata: CurrentModel references one ModelMetadata
- One-to-one with Configuration: CurrentModel persisted in config

**State Transitions**:
- `switch_model(new_model_id)`: Updates all attributes to new model
- `update_region(new_region)`: Updates region attribute
- `update_version(new_version)`: Updates version attribute

**Validation Rules**:
- model_id must exist in ModelRegistry
- region must be valid for model
- version must be valid for model if provided

### MenuLayout

Represents the visual layout structure of the interactive menu.

**Attributes**:
- `top_panel_height` (integer, required): Height of top panel (current model indicator)
  - Validation: Must be >= 1
  - Default: 3 lines
  
- `left_panel_width` (integer, required): Width of left panel (model list)
  - Validation: Must be >= 20
  - Default: 40% of terminal width or minimum 30 characters
  
- `right_panel_width` (integer, required): Width of right panel (hover details)
  - Validation: Must be >= 20
  - Default: Remaining width after left panel
  
- `list_item_height` (integer, required): Height of each model item in list
  - Validation: Must be >= 1
  - Default: 2 lines
  
- `terminal_width` (integer, required): Terminal width in characters
  - Validation: Must be > 0
  - Source: From Rich Console.width
  
- `terminal_height` (integer, required): Terminal height in lines
  - Validation: Must be > 0
  - Source: From Rich Console.height

**Relationships**:
- One-to-one with MenuState: MenuLayout used to render MenuState

**State Transitions**: None (calculated from terminal size)

**Validation Rules**:
- All dimensions must be positive
- Sum of panel widths must not exceed terminal width
- Sum of panel heights must not exceed terminal height

### ModelSelectionResult

Represents the result of a model selection operation.

**Attributes**:
- `success` (boolean, required): Whether selection was successful
  - Validation: Must be True or False
  
- `model_id` (string, optional): Selected model ID
  - Validation: Must be valid model_id if success is True
  - Default: None if success is False
  
- `message` (string, required): Result message
  - Validation: Must be non-empty string
  - Examples: `"Model switched to gemini-2-5-pro"`, `"Failed to switch model: authentication error"`
  
- `error` (string, optional): Error message if selection failed
  - Validation: Must be non-empty string if success is False
  - Default: None if success is True

**Relationships**:
- One-to-one with ModelMetadata: ModelSelectionResult references selected ModelMetadata

**State Transitions**: None (immutable result object)

**Validation Rules**:
- If success is True, model_id must be provided
- If success is False, error must be provided
- message must always be provided

## Data Flow

### Menu Initialization Flow

1. Load models from ModelRegistry
2. Load current model from ConfigurationManager
3. Create MenuState with models and current_model_id
4. Calculate MenuLayout from terminal size
5. Initialize selected_index to current model or 0
6. Render menu with MenuState and MenuLayout

### Model Selection Flow

1. User navigates menu (updates MenuState.selected_index)
2. User presses Enter (triggers selection)
3. Get selected model from MenuState.models[selected_index]
4. Validate model availability
5. Switch model using VertexAIClient
6. Update ConfigurationManager with new model
7. Update MenuState.current_model_id
8. Return ModelSelectionResult
9. Display success/error message
10. Refresh menu display

### Hover Details Flow

1. User navigates menu (updates MenuState.selected_index)
2. Update MenuState.hover_details_model_id to selected model
3. Get ModelMetadata for hover model
4. Format hover details (context window, pricing, capabilities, description)
5. Update right panel with formatted details
6. Refresh menu display

## Validation Rules Summary

### ModelMetadata Extension
- All new fields are optional (backward compatible)
- If provided, must pass type and format validation
- context_window: Non-empty string
- pricing: Dict with "input" and/or "output" keys, values >= 0
- capabilities: Non-empty list of strings
- description: Non-empty string

### MenuState
- models list must be non-empty
- selected_index must be valid (0 <= index < len(models))
- menu_start_index must keep selected_index visible
- All model IDs must exist in models list

### CurrentModel
- model_id must exist in ModelRegistry
- region must be valid for model
- version must be valid for model if provided

### MenuLayout
- All dimensions must be positive
- Panel widths must fit in terminal width
- Panel heights must fit in terminal height

### ModelSelectionResult
- success and message always required
- If success: model_id required
- If not success: error required

## Relationships Diagram

```
ModelRegistry
    │
    ├─── ModelMetadata (7 instances)
    │       │
    │       ├─── Extended with: context_window, pricing, capabilities, description
    │       │
    │       └─── Used by: MenuState, CurrentModel
    │
    └─── get_available_models() → List[ModelMetadata]

MenuState
    │
    ├─── Contains: List[ModelMetadata]
    ├─── Tracks: current_model_id, selected_index
    └─── Used by: MenuLayout (for rendering)

CurrentModel
    │
    ├─── References: ModelMetadata (1)
    └─── Persisted in: Configuration

MenuLayout
    │
    ├─── Calculated from: Terminal size
    └─── Used to render: MenuState

ModelSelectionResult
    │
    └─── References: ModelMetadata (selected model)
```

## Migration Notes

### Extending ModelMetadata

**Backward Compatibility**:
- All new fields are optional
- Existing code continues to work without changes
- New fields default to None if not provided
- `to_dict()` method includes new fields if present

**Migration Steps**:
1. Add new optional fields to ModelMetadata class
2. Update MODEL_METADATA dict with new field values
3. Update `to_dict()` method to include new fields
4. No changes needed to existing code using ModelMetadata

### Model List Changes

**Removed Models**:
- All Claude models (claude-4-5-sonnet, claude-3-5-sonnet, claude-3-opus)
- Old Gemini models (gemini-1-5-pro, gemini-1-5-flash)
- Old Qwen models (qwen-coder, qwen-2-5-coder)

**Added Models** (from vertex-config.md):
- deepseek-ai/deepseek-v3.1-maas
- qwen/qwen3-coder-480b-a35b-instruct-maas
- gemini-2.5-pro
- deepseek-ai/deepseek-r1-0528-maas
- moonshotai/kimi-k2-thinking-maas
- openai/gpt-oss-120b-maas
- meta/llama-3.1-405b-instruct-maas

**Migration Impact**:
- Existing configs with removed models will need update
- ModelRegistry will only return 7 supported models
- Error handling for missing models required

