# Research & Technology Decisions

**Feature**: Gemini CLI Custom `/model` Command  
**Date**: 2025-11-18  
**Status**: Complete

## Overview

This document consolidates research findings and technology decisions for the Gemini CLI Custom `/model` Command implementation. Research was conducted using Context7 to find best practices for interactive CLI menus, Gemini CLI custom commands, and terminal UI libraries.

## Technology Stack Decisions

### Interactive Menu Library: Rich with Alternate Screen

**Decision**: Use Rich library with `console.screen()` for alternate screen mode.

**Rationale**:
- ✅ Already in project dependencies (no new dependencies)
- ✅ Supports `console.screen()` for alternate screen (enables hover/preview)
- ✅ Rich formatting and styling capabilities
- ✅ Cross-platform compatible (macOS, Linux, Windows)
- ✅ Excellent documentation and community support
- ✅ Performance optimized for terminal rendering

**Research Findings from Context7**:
- Rich supports alternate screen mode via `console.screen()` context manager
- Can dynamically update content with `screen.update()` method
- Supports real-time content updates without scrolling
- Excellent for interactive menus with hover details

**Alternatives Considered**:
- **Prompt Toolkit**: Excellent for interactive prompts, has `choice()` and `radiolist_dialog()`, full-screen application support. However, not in current dependencies and hover details require custom full-screen app implementation.
- **InquirerPy**: Good keyboard navigation, multiple selection support. However, not in dependencies and no built-in hover/preview support.
- **Custom Implementation**: Too complex, would require significant development time.

**Implementation Approach**:
- Use Rich's `console.screen()` for alternate screen mode
- Implement custom interactive menu with keyboard navigation
- Display hover details in side panel or below menu
- Use Rich Layout for structured display

### Gemini CLI Custom Command Mechanism

**Decision**: Use TOML file in `~/.gemini/commands/model.toml` for custom command.

**Research Findings from Context7**:
- Gemini CLI supports custom commands via TOML files in `~/.gemini/commands/` directory
- Command files use `description` and `prompt` fields
- Support `{{args}}` for argument injection
- Can execute shell commands with `!{...}` syntax
- Commands are automatically discovered by Gemini CLI

**Format**:
```toml
description = "Manage Vertex AI models"
prompt = """
Execute interactive model selection:
!{python -m vertex_spec_adapter.cli.commands.model_interactive {{args}}}
"""
```

**Installation**:
- Create TOML file in `~/.gemini/commands/`
- Gemini CLI automatically discovers and loads command
- No restart required (hot reload)

**Alternatives Considered**:
- **Extension System**: More complex, requires extension registration
- **MCP Server**: Overkill for simple command override
- **Direct Integration**: Not possible without modifying Gemini CLI source

### Model Metadata Extension

**Decision**: Extend existing `ModelMetadata` class with optional fields for enhanced information.

**Rationale**:
- Maintains backward compatibility
- Uses existing Pydantic validation
- Easy to extend in future
- Type-safe implementation
- No breaking changes to existing code

**New Fields**:
- `context_window: Optional[str]` - Context window size (e.g., "1M tokens", "200K tokens")
- `pricing: Optional[Dict[str, float]]` - Pricing per token (input/output)
- `capabilities: Optional[List[str]]` - Model capabilities (e.g., ["coding", "reasoning"])
- `description: Optional[str]` - Model description and use cases

**Fields Excluded from Display** (per requirements):
- `region` - Not shown in hover details
- `access_pattern` - Not shown in hover details
- `provider` - Not shown in hover details

**Alternatives Considered**:
- **Separate Metadata Class**: Would require more refactoring
- **Dictionary-based**: Less type-safe, harder to validate
- **External Config File**: More complex, harder to maintain

### Authentication Method

**Decision**: Use `gcloud auth print-access-token` for authentication (per vertex-config.md).

**Rationale**:
- Matches existing vertex-config.md pattern
- Simple and reliable
- No additional credential management needed
- Works with all GCP authentication methods

**Implementation**:
- Execute `gcloud auth print-access-token` command
- Use token for API authentication
- Handle authentication errors gracefully
- Provide clear error messages with troubleshooting steps

**Alternatives Considered**:
- **Service Account Key**: More complex, requires file management
- **Application Default Credentials**: Less explicit, harder to debug
- **API Key**: Not suitable for Vertex AI

### Model List: Only from vertex-config.md

**Decision**: Support only 7 models from vertex-config.md, remove all others.

**Models Supported**:
1. DeepSeek V3.1 (`deepseek-ai/deepseek-v3.1-maas`) - Region: `us-west2`
2. Qwen Coder (`qwen/qwen3-coder-480b-a35b-instruct-maas`) - Region: `us-south1`
3. Gemini 2.5 Pro (`gemini-2.5-pro`) - Region: `global`
4. DeepSeek R1 0528 (`deepseek-ai/deepseek-r1-0528-maas`) - Region: `us-central1`
5. Kimi K2 (`moonshotai/kimi-k2-thinking-maas`) - Region: `global`
6. GPT OSS 120B (`openai/gpt-oss-120b-maas`) - Region: `us-central1`
7. Llama 3.1 (`meta/llama-3.1-405b-instruct-maas`) - Region: `us-central1`

**Models Removed**:
- All Claude models (not in vertex-config.md)
- Old Gemini models (not in vertex-config.md)
- Old Qwen models (not in vertex-config.md)

**Rationale**:
- Simplifies implementation
- Matches user's actual model configuration
- Reduces maintenance burden
- Clear scope definition

## Architecture Decisions

### Interactive Menu Layout

**Decision**: Use Rich Layout with three-panel design.

**Layout Structure**:
- **Top Panel**: Current model indicator (shows active model)
- **Left Panel**: Model list (scrollable, with selection highlight)
- **Right/Bottom Panel**: Hover details (updates when model highlighted)

**Rationale**:
- Clear visual separation
- Doesn't interfere with navigation
- Responsive to terminal size
- Professional appearance

**Alternatives Considered**:
- **Single Column**: Less information visible at once
- **Full Screen Details**: Takes too much space
- **Modal Overlay**: More complex, harder to implement

### Keyboard Navigation

**Decision**: Standard arrow key navigation with Enter for selection.

**Key Bindings**:
- `↑` / `↓`: Navigate up/down
- `Enter`: Select model
- `Escape`: Cancel/exit
- `Home` / `End`: Jump to first/last model

**Rationale**:
- Standard and intuitive
- Works on all platforms
- No learning curve
- Accessible

**Alternatives Considered**:
- **Vim Keys (j/k)**: Less intuitive for non-vim users
- **Mouse Support**: Not available in all terminals
- **Custom Keys**: Requires documentation and learning

### Hover Details Display

**Decision**: Display details in real-time as user navigates (not true hover, but highlight-based).

**Information Displayed**:
- Model Name & ID
- Context Window (e.g., "1M tokens")
- Pricing/Cost (per token, if available)
- Capabilities (e.g., "coding-focused", "reasoning")
- Status (available/unavailable)
- Current Model Indicator (✓)
- Description (use cases and strengths)

**Information Excluded** (per requirements):
- Region
- Access Pattern
- Provider

**Rationale**:
- Real-time feedback
- No need for explicit hover action
- Clear and readable
- Focuses on user-relevant information

**Alternatives Considered**:
- **True Mouse Hover**: Not available in all terminals
- **Separate Info Command**: Less convenient
- **Tooltip**: Complex to implement in terminal

### Configuration Persistence

**Decision**: Update `.specify/config.yaml` directly using existing ConfigurationManager.

**Rationale**:
- Uses existing configuration system
- Consistent with Vertex Adapter
- Simple implementation
- No additional config files needed

**Update Process**:
1. Load current config
2. Update model field
3. Save config file
4. Verify update

**Alternatives Considered**:
- **Separate Config File**: More complex, harder to maintain
- **Environment Variables**: Less persistent
- **Gemini CLI Config**: Not appropriate for Vertex Adapter settings

## Performance Decisions

### Menu Rendering: Optimized Updates

**Decision**: Use Rich's efficient update methods, minimize redraws.

**Optimization Strategies**:
- Only update changed parts of screen
- Cache formatted model information
- Use Rich's Layout for efficient rendering
- Target: < 50ms render time

**Rationale**:
- Smooth user experience
- Responsive navigation
- Professional feel

### Hover Details: Cached Formatting

**Decision**: Cache formatted hover details for each model.

**Optimization Strategies**:
- Pre-format model details on menu load
- Cache formatted strings
- Only update when model highlighted
- Target: < 10ms update time

**Rationale**:
- Instant feedback
- Smooth updates
- Better user experience

## Error Handling Decisions

### Terminal Compatibility: Fallback Mode

**Decision**: Detect terminal capabilities and fallback to simple text menu if needed.

**Detection**:
- Check if terminal supports alternate screen
- Check if Rich can render properly
- Fallback to simple text-based menu

**Rationale**:
- Works on all terminals
- Graceful degradation
- Better user experience

### Authentication Errors: Clear Messages

**Decision**: Provide clear error messages with troubleshooting steps.

**Error Handling**:
- Check gcloud authentication before use
- Show helpful error messages
- Provide actionable troubleshooting steps
- Don't crash on auth errors

**Rationale**:
- Better user experience
- Easier debugging
- Professional error handling

## Testing Strategy Decisions

### UI Testing: Mock Rich Console

**Decision**: Mock Rich console for unit tests.

**Rationale**:
- Fast test execution
- No terminal dependencies
- Easy to verify output
- Reliable test results

**Implementation**:
- Mock `Console` class
- Capture printed output
- Verify formatting
- Test navigation logic

### Integration Testing: Real Terminal

**Decision**: Use real terminal for integration tests.

**Rationale**:
- Tests actual user experience
- Catches terminal-specific issues
- Validates full workflow

**Implementation**:
- Use pytest with real terminal
- Test keyboard navigation
- Test model selection
- Test error handling

## Security Decisions

### Command Execution: Safe Shell Commands

**Decision**: Use safe shell command execution for gcloud auth.

**Rationale**:
- No user input in shell commands
- Prevents command injection
- Safe and reliable

**Implementation**:
- Use `subprocess` with safe arguments
- No user input in commands
- Validate all inputs

## Documentation Decisions

### Usage Documentation: Comprehensive Guide

**Decision**: Create detailed usage guide with examples.

**Content**:
- Installation instructions
- Usage examples
- Keyboard shortcuts
- Troubleshooting guide
- Screenshots/demos

**Rationale**:
- Better user experience
- Easier onboarding
- Reduces support burden

## Summary

All technology decisions have been made based on:
1. Research from Context7 (Gemini CLI, Rich library)
2. Alignment with constitutional principles
3. Project requirements (vertex-config.md models)
4. Developer experience (Rich already in dependencies)
5. Maintainability (extend existing code)

Key decisions:
- ✅ Rich library for interactive menu (already in dependencies)
- ✅ TOML file for Gemini CLI command (standard mechanism)
- ✅ Extend ModelMetadata (backward compatible)
- ✅ gcloud auth (matches vertex-config.md)
- ✅ Only 7 models from vertex-config.md

No "NEEDS CLARIFICATION" items remain. The implementation plan can proceed.

---

## Model Metadata Values Research (T003a)

**Status**: Research Required  
**Source**: Vertex AI Documentation, Model Provider Documentation, Vertex AI Pricing Pages

This section documents the research findings for actual model metadata values that need to be populated in the ModelRegistry for the 7 supported models.

### Research Methodology

1. **Context Window**: Check Vertex AI model documentation for maximum context length
2. **Pricing**: Check Vertex AI pricing pages for per-token costs (input/output)
3. **Capabilities**: Review model provider documentation for specializations
4. **Description**: Compile use cases and strengths from official documentation

### Model Metadata Values

#### 1. DeepSeek V3.1 (`deepseek-ai/deepseek-v3.1-maas`)

**Context Window**: 
- **Research Required**: Check DeepSeek V3.1 documentation for context length
- **Estimated**: TBD (check official docs)
- **Source**: Vertex AI Model Garden / DeepSeek documentation

**Pricing** (per 1M tokens):
- **Input**: TBD (research from Vertex AI pricing)
- **Output**: TBD (research from Vertex AI pricing)
- **Source**: Vertex AI Pricing page for DeepSeek models

**Capabilities**:
- **Research Required**: Review DeepSeek V3.1 capabilities
- **Estimated**: `["general-purpose", "code-generation", "reasoning"]`
- **Source**: DeepSeek V3.1 release notes / documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Advanced general-purpose model optimized for code generation and complex reasoning tasks"
- **Source**: DeepSeek V3.1 release notes / documentation

#### 2. Qwen Coder (`qwen/qwen3-coder-480b-a35b-instruct-maas`)

**Context Window**:
- **Research Required**: Check Qwen Coder documentation
- **Estimated**: TBD (check official docs)
- **Source**: Vertex AI Model Garden / Qwen documentation

**Pricing** (per 1M tokens):
- **Input**: ~$0.10 (from existing metrics.py, verify)
- **Output**: ~$0.40 (from existing metrics.py, verify)
- **Source**: Vertex AI Pricing page for Qwen models

**Capabilities**:
- **Research Required**: Review Qwen Coder specializations
- **Estimated**: `["code-generation", "debugging", "code-analysis"]`
- **Source**: Qwen Coder documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Specialized code generation model optimized for programming tasks, debugging, and code analysis"
- **Source**: Qwen Coder release notes / documentation

#### 3. Gemini 2.5 Pro (`gemini-2.5-pro`)

**Context Window**:
- **Research Required**: Check Gemini 2.5 Pro documentation
- **Estimated**: 1M+ tokens (verify from official docs)
- **Source**: Google AI Studio / Gemini documentation

**Pricing** (per 1M tokens):
- **Input**: ~$0.50 (from existing metrics.py, verify)
- **Output**: ~$1.50 (from existing metrics.py, verify)
- **Source**: Google AI Pricing page

**Capabilities**:
- **Research Required**: Review Gemini 2.5 Pro capabilities
- **Estimated**: `["general-purpose", "code-generation", "reasoning", "multimodal"]`
- **Source**: Gemini 2.5 Pro documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Advanced general-purpose model with strong reasoning capabilities, code generation, and multimodal support"
- **Source**: Gemini 2.5 Pro release notes / documentation

#### 4. DeepSeek R1 0528 (`deepseek-ai/deepseek-r1-0528-maas`)

**Context Window**:
- **Research Required**: Check DeepSeek R1 documentation
- **Estimated**: TBD (check official docs)
- **Source**: Vertex AI Model Garden / DeepSeek R1 documentation

**Pricing** (per 1M tokens):
- **Input**: TBD (research from Vertex AI pricing)
- **Output**: TBD (research from Vertex AI pricing)
- **Source**: Vertex AI Pricing page for DeepSeek R1

**Capabilities**:
- **Research Required**: Review DeepSeek R1 specializations
- **Estimated**: `["reasoning", "problem-solving", "chain-of-thought"]`
- **Source**: DeepSeek R1 documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Reasoning-focused model with advanced chain-of-thought capabilities for complex problem-solving"
- **Source**: DeepSeek R1 release notes / documentation

#### 5. Kimi K2 (`moonshotai/kimi-k2-thinking-maas`)

**Context Window**:
- **Research Required**: Check Kimi K2 documentation
- **Estimated**: TBD (check official docs, may be 200K+ tokens)
- **Source**: Vertex AI Model Garden / Moonshot AI documentation

**Pricing** (per 1M tokens):
- **Input**: TBD (research from Vertex AI pricing)
- **Output**: TBD (research from Vertex AI pricing)
- **Source**: Vertex AI Pricing page for Kimi models

**Capabilities**:
- **Research Required**: Review Kimi K2 specializations
- **Estimated**: `["reasoning", "thinking", "analysis"]`
- **Source**: Kimi K2 documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Thinking-focused model optimized for complex reasoning and analysis tasks"
- **Source**: Kimi K2 release notes / documentation

#### 6. GPT OSS 120B (`openai/gpt-oss-120b-maas`)

**Context Window**:
- **Research Required**: Check GPT OSS 120B documentation
- **Estimated**: TBD (check official docs)
- **Source**: Vertex AI Model Garden / OpenAI OSS documentation

**Pricing** (per 1M tokens):
- **Input**: TBD (research from Vertex AI pricing)
- **Output**: TBD (research from Vertex AI pricing)
- **Source**: Vertex AI Pricing page for GPT OSS models

**Capabilities**:
- **Research Required**: Review GPT OSS 120B capabilities
- **Estimated**: `["general-purpose", "large-scale"]`
- **Source**: GPT OSS 120B documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Large-scale open-source model for general-purpose tasks"
- **Source**: GPT OSS 120B release notes / documentation

#### 7. Llama 3.1 (`meta/llama-3.1-405b-instruct-maas`)

**Context Window**:
- **Research Required**: Check Llama 3.1 405B documentation
- **Estimated**: TBD (check official docs, may be 128K+ tokens)
- **Source**: Vertex AI Model Garden / Meta Llama documentation

**Pricing** (per 1M tokens):
- **Input**: TBD (research from Vertex AI pricing)
- **Output**: TBD (research from Vertex AI pricing)
- **Source**: Vertex AI Pricing page for Llama models

**Capabilities**:
- **Research Required**: Review Llama 3.1 405B capabilities
- **Estimated**: `["general-purpose", "instruction-following", "conversation"]`
- **Source**: Llama 3.1 documentation

**Description**:
- **Research Required**: Compile from official documentation
- **Estimated**: "Large-scale instruction-tuned model optimized for following instructions and general conversation"
- **Source**: Llama 3.1 release notes / documentation

### Research Action Items

1. **Access Vertex AI Documentation**:
   - Visit Vertex AI Model Garden for each model
   - Check model-specific documentation pages
   - Review pricing pages for accurate cost information

2. **Verify Existing Data**:
   - Cross-reference pricing in `vertex_spec_adapter/utils/metrics.py`
   - Update if pricing has changed
   - Add missing models to pricing data

3. **Document Findings**:
   - Update this section with actual values
   - Add source URLs for verification
   - Note any discrepancies or uncertainties

4. **Implementation**:
   - Populate ModelRegistry with researched values
   - Ensure all 7 models have complete metadata
   - Validate data format matches ModelMetadata schema

### Notes

- **Pricing**: Values may change over time, should be updated periodically
- **Context Window**: May vary by region or deployment
- **Capabilities**: Should be based on official model documentation, not assumptions
- **Description**: Should be concise but informative for user decision-making

**Next Steps**: Complete research before Phase 1 implementation to ensure accurate model metadata.

