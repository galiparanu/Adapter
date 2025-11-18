# Interactive Menu API Contract

**Component**: Interactive Model Selection Menu  
**Version**: 1.0.0  
**Date**: 2025-11-18

## Overview

This contract defines the API for the interactive model selection menu component. The menu provides a Rich-based terminal UI for browsing, viewing details, and selecting Vertex AI models.

## Class: ModelInteractiveMenu

### Initialization

```python
class ModelInteractiveMenu:
    def __init__(
        self,
        config_path: Optional[Path] = None,
        console: Optional[Console] = None,
    ) -> None
```

**Parameters**:
- `config_path` (Optional[Path]): Path to Vertex Adapter config file. Defaults to `.specify/config.yaml`.
- `console` (Optional[Console]): Rich Console instance. Defaults to new Console().

**Behavior**:
- Initializes menu with model list from ModelRegistry
- Loads current model from ConfigurationManager
- Sets up keyboard event handlers
- Prepares menu layout

**Raises**:
- `ConfigurationError`: If config file is invalid or missing
- `ModelNotFoundError`: If current model is not available

### Method: run()

```python
def run(self) -> Optional[str]
```

**Description**: Main entry point to run the interactive menu.

**Returns**:
- `Optional[str]`: Selected model ID if user selected a model, None if cancelled.

**Behavior**:
- Enters alternate screen mode
- Displays interactive menu
- Handles keyboard navigation
- Updates hover details in real-time
- Returns selected model ID or None on cancel

**Raises**:
- `KeyboardInterrupt`: If user presses Ctrl+C (handled internally)
- `TerminalError`: If terminal doesn't support required features

**Example**:
```python
menu = ModelInteractiveMenu()
selected_model = menu.run()
if selected_model:
    print(f"Selected: {selected_model}")
```

### Method: _render_menu()

```python
def _render_menu(self) -> None
```

**Description**: Renders the complete menu layout including model list, current model indicator, and hover details.

**Behavior**:
- Clears screen
- Renders top panel (current model)
- Renders left panel (model list with selection)
- Renders right panel (hover details)
- Updates screen display

**Called By**: `run()`, navigation methods

### Method: _handle_keypress()

```python
def _handle_keypress(self, key: str) -> Optional[str]
```

**Description**: Handles keyboard input and updates menu state.

**Parameters**:
- `key` (str): Key pressed by user

**Returns**:
- `Optional[str]`: Model ID if Enter pressed, None otherwise

**Key Bindings**:
- `up` / `down`: Navigate model list
- `enter`: Select current model
- `escape`: Cancel and exit
- `home`: Jump to first model
- `end`: Jump to last model

**Behavior**:
- Updates selected_index based on key
- Updates hover_details_model_id
- Triggers menu re-render
- Returns model ID on Enter, None on Escape

### Method: _format_hover_details()

```python
def _format_hover_details(self, model: ModelMetadata) -> str
```

**Description**: Formats model metadata for hover details display.

**Parameters**:
- `model` (ModelMetadata): Model metadata to format

**Returns**:
- `str`: Formatted string with Rich markup

**Format**:
- Model Name & ID
- Context Window
- Pricing (if available)
- Capabilities
- Status
- Current Model Indicator (✓)
- Description

**Excludes** (per requirements):
- Region
- Access Pattern
- Provider

**Example Output**:
```
┌─ Model Information ──────────────┐
│ Gemini 2.5 Pro                    │
│ ID: gemini-2.5-pro                │
│                                   │
│ Context: 1M tokens                │
│ Pricing: Input $0.50/1M           │
│          Output $1.50/1M          │
│                                   │
│ Capabilities:                     │
│ • General-purpose                 │
│ • Code generation                 │
│ • Reasoning                       │
│                                   │
│ Status: ✓ Available              │
│                                   │
│ Description:                      │
│ Best for general tasks, code      │
│ generation, and complex reasoning │
└───────────────────────────────────┘
```

### Method: _switch_model()

```python
def _switch_model(self, model_id: str) -> ModelSelectionResult
```

**Description**: Switches to the selected model and updates configuration.

**Parameters**:
- `model_id` (str): Model ID to switch to

**Returns**:
- `ModelSelectionResult`: Result of model switch operation

**Behavior**:
1. Validates model exists in ModelRegistry
2. Gets model metadata
3. Switches VertexAIClient to new model
4. Updates ConfigurationManager with new model
5. Saves configuration file
6. Returns success/error result

**Raises**:
- `ModelNotFoundError`: If model_id is invalid
- `ConfigurationError`: If config update fails
- `APIError`: If model switch fails

### Method: _get_current_model()

```python
def _get_current_model(self) -> Optional[str]
```

**Description**: Gets the currently active model ID from configuration.

**Returns**:
- `Optional[str]`: Current model ID or None if not set

**Behavior**:
- Loads config from ConfigurationManager
- Returns config.model.id
- Returns None if config not found

## State Management

### MenuState Attributes

- `models: List[ModelMetadata]` - All available models
- `current_model_id: Optional[str]` - Currently active model
- `selected_index: int` - Currently highlighted model index
- `hover_details_model_id: Optional[str]` - Model for hover details

### State Transitions

1. **Navigation Up**: `selected_index -= 1` (wraps to end)
2. **Navigation Down**: `selected_index += 1` (wraps to start)
3. **Model Selection**: `current_model_id = models[selected_index].model_id`
4. **Hover Update**: `hover_details_model_id = models[selected_index].model_id`

## Error Handling

### Terminal Compatibility

```python
def _check_terminal_support(self) -> bool
```

**Description**: Checks if terminal supports required features.

**Returns**:
- `bool`: True if terminal supports alternate screen, False otherwise

**Behavior**:
- Checks if console.is_terminal is True
- Checks if terminal supports alternate screen
- Returns False if unsupported (triggers fallback)

### Fallback Mode

```python
def _simple_text_menu(self) -> Optional[str]
```

**Description**: Simple text-based menu fallback for unsupported terminals.

**Returns**:
- `Optional[str]`: Selected model ID or None

**Behavior**:
- Displays numbered list of models
- Prompts for selection
- Returns selected model ID
- Used when alternate screen not supported

## Performance Requirements

- Menu rendering: < 50ms
- Hover detail update: < 10ms
- Keyboard response: < 100ms
- Model switch: < 500ms

## Testing Contract

### Unit Tests

- Test menu initialization
- Test keyboard navigation
- Test model selection
- Test hover details formatting
- Test error handling
- Mock Rich Console for testing

### Integration Tests

- Test full menu workflow
- Test model switching
- Test configuration updates
- Test with real terminal

### E2E Tests

- Test complete user journey
- Test error scenarios
- Test cross-platform compatibility

## Example Usage

```python
from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu

# Initialize menu
menu = ModelInteractiveMenu()

# Run interactive menu
selected_model = menu.run()

if selected_model:
    print(f"Successfully switched to: {selected_model}")
else:
    print("Selection cancelled")
```

