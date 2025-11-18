# Feature Specification: Gemini CLI Custom `/model` Command

## Feature Number
002

## Feature Name
Gemini CLI Custom `/model` Command with Interactive Menu

## Status
Draft - Awaiting Approval

## Problem Statement

Currently, Gemini CLI has a built-in `/model` command that allows users to manage models. However, users want to:
1. Override the default `/model` command to use Vertex AI models exclusively
2. Access models from Vertex AI (DeepSeek, Qwen, Gemini, Kimi, GPT OSS, Llama) through a unified interface
3. Have an interactive menu experience with hover details for model selection
4. See comprehensive model information (context window, pricing, capabilities, status) when browsing models

The current implementation doesn't provide:
- Interactive menu for model selection
- Detailed hover information for models
- Integration with Vertex AI model registry
- Visual indication of current active model

## Target Users

1. **Primary**: Developers using Gemini CLI who want to switch between Vertex AI models
2. **Secondary**: Teams managing multiple AI models across different providers
3. **Tertiary**: Users who prefer interactive CLI experiences over command-line arguments

## Core Features

### FR-001: Custom `/model` Command Override
**Priority**: P0 (Critical)

System MUST override Gemini CLI's default `/model` command with a custom implementation that:
- Intercepts `/model` command in Gemini CLI
- Replaces default behavior with Vertex Adapter implementation
- Maintains command compatibility (same command name)
- Works seamlessly within Gemini CLI's command system

**Acceptance Criteria:**
- [ ] `/model` command triggers custom implementation
- [ ] Default Gemini CLI `/model` behavior is completely replaced
- [ ] Command works in both interactive and non-interactive modes
- [ ] No conflicts with other Gemini CLI commands (same command name, no namespace collisions)
- [ ] Integration maintains Gemini CLI command system compatibility (TOML-based custom command format)

### FR-002: Interactive Model Selection Menu
**Priority**: P0 (Critical)

System MUST provide an interactive menu when `/model` is executed that:
- Displays all available Vertex AI models in a scrollable list
- Shows current active model with visual indicator (✓)
- Allows navigation using arrow keys (↑/↓)
- Supports Enter key to select a model
- Supports Escape key to cancel
- Shows model count and current selection position

**Acceptance Criteria:**
- [ ] Menu displays all 7 models from vertex-config.md
- [ ] Current model is clearly marked with visual indicator (✓ symbol, distinct styling)
- [ ] Keyboard navigation works smoothly (< 100ms response time per keypress)
- [ ] Selection is confirmed with Enter
- [ ] Cancellation with Escape works correctly
- [ ] Home/End keys jump to first/last model (optional enhancement)
- [ ] Menu adapts to terminal size (minimum 80x24 characters, graceful degradation for smaller terminals)
- [ ] Long model names/descriptions are truncated or wrapped appropriately (max 40 chars per line, ellipsis for overflow)
- [ ] Keyboard shortcuts help available (press '?' or 'H' to display help, optional enhancement)

### FR-003: Model Hover Details
**Priority**: P0 (Critical)

System MUST display detailed model information when hovering over a model in the menu (displayed in right panel), including:
- **Model Name & ID**: Full name and identifier
- **Context Window**: Maximum token context (e.g., "1M tokens", "200K tokens")
- **Pricing/Cost**: Cost per token for input and output (if available)
- **Capabilities**: Specialization (e.g., "coding-focused", "reasoning", "general-purpose")
- **Status**: Availability status (available/unavailable)
- **Current Model Indicator**: Visual mark (✓) if this is the active model
- **Description**: Brief description of model's strengths and use cases

**Excluded from hover** (as per requirements):
- Region information
- Access pattern (native_sdk/maas)
- Provider information

**Format**: See `contracts/interactive-menu.md` for detailed format specification.

**Acceptance Criteria:**
- [ ] Hover shows all required information fields in right panel
- [ ] Information is formatted clearly and readable (per contract specification)
- [ ] Hover updates in real-time as user navigates (< 10ms update time)
- [ ] No region/access pattern/provider shown in hover
- [ ] Current model indicator is visible

### FR-004: Model List Display
**Priority**: P1 (High)

System MUST list all available models from vertex-config.md:
1. DeepSeek V3.1 (`deepseek-ai/deepseek-v3.1-maas`)
2. Qwen Coder (`qwen/qwen3-coder-480b-a35b-instruct-maas`)
3. Gemini 2.5 Pro (`gemini-2.5-pro`)
4. DeepSeek R1 0528 (`deepseek-ai/deepseek-r1-0528-maas`)
5. Kimi K2 (`moonshotai/kimi-k2-thinking-maas`)
6. GPT OSS 120B (`openai/gpt-oss-120b-maas`)
7. Llama 3.1 (`meta/llama-3.1-405b-instruct-maas`)

**Acceptance Criteria:**
- [ ] All 7 models are displayed
- [ ] Models not in vertex-config.md are excluded
- [ ] Model IDs match exactly with vertex-config.md
- [ ] Models are sorted alphabetically by model name (human-readable name, not model_id)

### FR-005: Model Switching
**Priority**: P0 (Critical)

System MUST allow users to switch the active model by:
- Selecting a model from the interactive menu
- Confirming selection with Enter
- Updating Vertex Adapter configuration
- Persisting selection across Gemini CLI sessions
- Providing confirmation feedback

**Acceptance Criteria:**
- [ ] Model switch is successful
- [ ] Configuration is updated immediately (< 500ms from selection to file write completion)
- [ ] Selection persists after CLI restart
- [ ] User receives clear confirmation message
- [ ] Error handling for invalid selections:
  - Invalid model ID: Clear error with list of available models
  - Authentication failure: Clear error with troubleshooting steps
  - Configuration write failure: Clear error with file path and permissions info
  - ModelRegistry unavailable: Clear error with retry suggestion and fallback behavior
  - Token expired during switch: Automatic token refresh or clear re-authentication prompt

### FR-006: Show Current Model
**Priority**: P1 (High)

System MUST display the currently active model when:
- `/model` command is executed without arguments
- User opens the interactive menu (shown at top of menu)
- User requests current model information

**Acceptance Criteria:**
- [ ] Current model is clearly displayed with visual indicator (✓) and model name
- [ ] Display format follows contract specification (see contracts/interactive-menu.md for format details)
- [ ] Information is accurate and up-to-date (matches ModelRegistry data, updated within 1 second of change)
- [ ] Works in both menu and non-interactive modes

### FR-007: Model Information Display
**Priority**: P1 (High)

**Note**: This requirement is primarily satisfied by FR-003 (Model Hover Details). FR-007 ensures the same information is available programmatically and can be displayed in non-interactive contexts.

System MUST provide detailed model information (same fields as FR-003) including:
- Context window size
- Pricing information (if available)
- Capabilities and specialization
- Description and use cases
- Status and availability

**Acceptance Criteria:**
- [ ] All information fields are populated (same as FR-003)
- [ ] Information is accurate
- [ ] Format is readable and well-structured
- [ ] Available via ModelRegistry API (for programmatic access)
- [ ] Same information as displayed in hover details (FR-003)

### FR-008: Authentication Integration
**Priority**: P0 (Critical)

System MUST use authentication method from vertex-config.md:
- Use `gcloud auth print-access-token` for authentication
- Support GCP project ID configuration
- Handle authentication errors gracefully
- Provide clear error messages for auth failures

**Acceptance Criteria:**
- [ ] Authentication uses gcloud token
- [ ] Project ID is configurable
- [ ] Auth errors are handled properly
- [ ] Error messages are helpful (include troubleshooting steps, list available options)
- [ ] gcloud CLI availability is checked before use
- [ ] Clear error message if gcloud CLI is not installed (with installation instructions)
- [ ] Token expiration during interaction is detected and handled (automatic refresh or re-authentication prompt)
- [ ] Recovery path provided after authentication failure (retry mechanism or user guidance to run `gcloud auth login`)

### FR-009: Model Registry Integration
**Priority**: P0 (Critical)

System MUST integrate with Vertex Adapter's ModelRegistry to:
- Load model metadata
- Validate model availability
- Check model status
- Retrieve model information

**Acceptance Criteria:**
- [ ] ModelRegistry is used for model data
- [ ] Only models from vertex-config.md are included
- [ ] Model metadata is accurate
- [ ] Registry updates are reflected in menu
- [ ] ModelRegistry unavailability is handled gracefully (clear error message, retry suggestion, fallback to cached data if available)
- [ ] Partial metadata loading failures are handled (display available data, indicate missing fields)
- [ ] Zero models available scenario is handled (clear message: "No models available. Check ModelRegistry connection.")
- [ ] All models unavailable scenario is handled (clear message with troubleshooting steps)

### FR-010: Interactive Menu Library
**Priority**: P1 (High)

System MUST use **Rich library** (already in project dependencies) for interactive menu that:
- Supports interactive terminal UI with hover/preview functionality via `console.screen()` alternate screen mode
- Enables keyboard navigation (arrow keys, Enter, Escape)
- Works across platforms (macOS, Linux, Windows)
- Provides smooth user experience

**Acceptance Criteria:**
- [ ] Rich library is used (no additional dependencies)
- [ ] Alternate screen mode works for hover details
- [ ] Keyboard navigation is smooth (< 100ms response time)
- [ ] Works on all supported platforms

**Note**: Implementation details and rationale are documented in plan.md and research.md

### FR-011: Error Handling & Edge Cases
**Priority**: P1 (High)

System MUST handle error scenarios and edge cases gracefully:

**Error Scenarios:**
- ModelRegistry unavailable: Display clear error with retry suggestion, fallback to cached data if available
- gcloud CLI not installed: Display error with installation instructions
- Token expired during interaction: Automatic refresh or clear re-authentication prompt
- Configuration file locked/permission denied: Clear error with file path and permission fix instructions
- Model switching during another operation: Queue operation or display "operation in progress" message

**Edge Cases:**
- Zero models available: Display "No models available" message with troubleshooting steps
- All models unavailable: Display error with ModelRegistry connection check instructions
- Terminal size too small: Graceful degradation (minimum 80x24, fallback to simple text menu if smaller)
- Very long model names/descriptions: Truncate with ellipsis (max 40 chars per line) or wrap appropriately
- Concurrent menu instances: Prevent multiple instances or handle gracefully (lock file or instance check)
- Missing optional metadata fields: Display available data, indicate missing fields with "N/A" or omit gracefully

**Recovery Mechanisms:**
- Transient errors: Retry with exponential backoff (up to 3 retries for network/API errors)
- Authentication failures: Provide clear recovery path (run `gcloud auth login`)
- ModelRegistry errors: Retry with backoff, fallback to cached data

**Acceptance Criteria:**
- [ ] All error scenarios have clear, actionable error messages
- [ ] All edge cases are handled without crashing
- [ ] Recovery mechanisms are defined and implemented
- [ ] Error messages include troubleshooting steps
- [ ] Fallback behaviors are graceful and informative

## User Stories

### US-001: Interactive Model Selection
**As a** developer using Gemini CLI  
**I want to** see an interactive menu when I type `/model`  
**So that** I can easily browse and select models with detailed information

**Acceptance Criteria:**
- [ ] Menu appears when `/model` is executed
- [ ] All available models are listed
- [ ] I can navigate with arrow keys
- [ ] I can see details when hovering
- [ ] I can select with Enter

### US-002: Model Information at a Glance
**As a** developer  
**I want to** see comprehensive model information when hovering  
**So that** I can make informed decisions about which model to use

**Acceptance Criteria:**
- [ ] Hover shows context window
- [ ] Hover shows pricing information
- [ ] Hover shows capabilities
- [ ] Hover shows current model indicator
- [ ] Information is clear and readable

### US-003: Quick Model Switching
**As a** developer  
**I want to** quickly switch between models  
**So that** I can use the best model for each task

**Acceptance Criteria:**
- [ ] I can switch models from the menu
- [ ] Switch is immediate (< 500ms from selection to completion)
- [ ] Selection persists
- [ ] I get confirmation feedback

### US-004: Current Model Visibility
**As a** developer  
**I want to** always know which model is currently active  
**So that** I can verify my configuration

**Acceptance Criteria:**
- [ ] Current model is shown in menu header
- [ ] Current model is marked with indicator
- [ ] I can see current model without opening menu

## Acceptance Criteria Summary

### Functional Requirements
- [ ] `/model` command is fully overridden
- [ ] Interactive menu works correctly (all keyboard navigation, hover details, selection)
- [ ] Hover details show all required information (context, pricing, capabilities, status, description)
- [ ] All 7 models from vertex-config.md are available
- [ ] Model switching works and persists (< 500ms update time)
- [ ] Current model is always visible (with visual indicator ✓)
- [ ] Authentication uses gcloud token (with availability checking)
- [ ] ModelRegistry integration works (with error handling for unavailability)
- [ ] Error handling covers all scenarios (invalid model, auth failure, config write failure, ModelRegistry unavailable)
- [ ] Edge cases are handled gracefully (zero models, terminal size, text overflow, token expiration)

### Non-Functional Requirements
- [ ] Menu is responsive (< 100ms navigation delay) - See T017 and T045 for implementation
- [ ] Hover updates smoothly (< 10ms update time) - See T018 and T046 for implementation
- [ ] Error messages are clear and helpful (include troubleshooting steps, list available options)
- [ ] Works on macOS, Linux, Windows
- [ ] No conflicts with Gemini CLI
- [ ] Performance targets met (menu rendering < 50ms, model switch < 500ms) - See T045, T046, T049
- [ ] Terminal compatibility: Minimum 80x24 characters, graceful degradation for smaller terminals
- [ ] Dependency validation: Check gcloud CLI availability before use
- [ ] Error recovery: Retry mechanism for transient failures (up to 3 retries with exponential backoff)
- [ ] Keyboard shortcuts discoverability: Help available via '?' or 'H' key (optional enhancement)

## Constraints

1. **Model Limitation**: Only models from vertex-config.md are supported
2. **Authentication**: Must use `gcloud auth print-access-token`
3. **Gemini CLI Compatibility**: Must work within Gemini CLI's command system
4. **No Region/Provider Display**: Region, access pattern, and provider info excluded from hover
5. **Python 3.9+**: Must support Python 3.9 and above

## Assumptions

1. **Gemini CLI custom command mechanism** [VALIDATED]: Gemini CLI supports custom command overrides via `~/.gemini/commands/model.toml` (per Gemini CLI documentation, confirmed in research.md)
2. **gcloud CLI availability** [REQUIRES VALIDATION]: User has `gcloud` CLI installed and authenticated
   - **Validation**: System MUST check gcloud availability and provide clear error if missing
3. **Vertex AI model access** [REQUIRES VALIDATION]: User has access to Vertex AI models in their GCP project
   - **Validation**: System MUST validate model access and provide clear error if unavailable
4. **Interactive terminal libraries** [VALIDATED]: Rich library is available (already in project dependencies)
5. **Model metadata extension** [VALIDATED]: Model metadata can be extended with context window, pricing, capabilities (confirmed in data-model.md)

## Exclusions

1. **Model Management**: Adding/removing models (only selection from existing list)
2. **Region Selection**: Region is determined by model (from vertex-config.md)
3. **Provider Information**: Provider details are not shown to users
4. **Access Pattern Details**: Native SDK vs MaaS distinction is hidden
5. **Model Configuration**: Advanced model parameters (temperature, etc.) not in this feature
6. **Batch Operations**: Switching multiple models at once
7. **Model Comparison**: Side-by-side model comparison view

## Dependencies

1. **Vertex Adapter**: Existing ModelRegistry and VertexAIClient
2. **Gemini CLI**: Custom command system (TOML-based, validated in research.md)
3. **gcloud CLI**: For authentication (MUST be checked for availability, error handling required)
4. **Interactive UI Library**: Rich library (already in dependencies, validated)
5. **Python 3.9+**: Runtime requirement

**Dependency Validation Requirements:**
- System MUST check for gcloud CLI availability before use
- System MUST provide clear error messages if dependencies are missing
- System MUST include installation/configuration instructions in error messages

## Success Criteria

1. **SC-001**: Users can override `/model` command successfully
2. **SC-002**: Interactive menu displays all 7 models correctly
3. **SC-003**: Hover shows all required information (context, pricing, capabilities, status, description)
4. **SC-004**: Model switching works and persists
5. **SC-005**: Current model is always visible
6. **SC-006**: Authentication works with gcloud token
7. **SC-007**: No region/provider/access pattern in hover display
8. **SC-008**: Menu navigation is smooth and responsive
9. **SC-009**: All error scenarios are handled gracefully with clear messages
10. **SC-010**: Edge cases (zero models, terminal size, etc.) are handled without crashing
11. **SC-011**: Recovery mechanisms work for transient failures
12. **SC-012**: Dependency validation provides helpful error messages

## Testing Strategy

### Unit Tests
- Model menu rendering
- Hover information formatting
- Model selection logic
- Configuration persistence
- Authentication handling

### Integration Tests
- Gemini CLI command integration
- Vertex Adapter ModelRegistry integration
- gcloud authentication flow
- Configuration file updates

### Manual Tests
- Interactive menu user experience
- Keyboard navigation
- Hover functionality
- Model switching workflow
- Cross-platform compatibility

## Open Questions / Needs Clarification

1. [RESOLVED] Which models to support? → Only models from vertex-config.md
2. [RESOLVED] What information in hover? → Context window, pricing, capabilities, status, description (exclude region, provider, access pattern)
3. [RESOLVED] Authentication method? → gcloud auth print-access-token
4. [RESOLVED] Exact Gemini CLI custom command mechanism? → Use TOML files in `~/.gemini/commands/model.toml` (per Gemini CLI docs)
5. [RESOLVED] Model metadata source? → Need to extend ModelRegistry with context window, pricing, capabilities
6. [RESOLVED] Interactive library choice? → **Rich** (already in dependencies) with `console.screen()` for alternate screen mode to support hover details

## Research Findings Summary

**Note**: Detailed research findings, technology decisions, and implementation approaches are documented in `research.md`. This section provides a high-level summary.

### Key Decisions

1. **Gemini CLI Integration**: Custom command mechanism via TOML files (see research.md for details)
2. **Interactive Menu Library**: Library selected based on dependencies and capabilities (see research.md for analysis)
3. **Model Metadata**: Extended with additional fields for enhanced information display (see data-model.md for schema)

**Rationale**: All technical decisions documented in research.md to maintain spec.md focus on WHAT and WHY, not HOW.

## Related Documents

- `vertex-config.md` - Model configurations and authentication
- `specs/001-vertex-ai-adapter/spec.md` - Base Vertex Adapter specification
- `vertex_spec_adapter/core/models.py` - ModelRegistry implementation
- Gemini CLI documentation - Custom commands

## Requirement Completeness Checklist

**Per Speckit.md Template Requirements**:

- [x] No [NEEDS CLARIFICATION] markers remain (all resolved)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] All user stories have clear acceptance criteria
- [x] Focus on WHAT users need and WHY (not HOW to implement)
- [x] No speculative or "might need" features
- [x] All phases have clear prerequisites and deliverables
- [x] Test scenarios defined for validation
- [x] Constraints and assumptions explicitly stated
- [x] Exclusions clearly documented

**Constitutional Compliance**:

- [x] Article I (Library-First): Feature extends existing library (Vertex Adapter)
- [x] Article II (CLI Interface): Command exposes functionality via CLI
- [x] Article III (Test-First): Test strategy defined in spec
- [x] Article VII (Simplicity): Simple TOML-based command integration
- [x] Article VIII (Anti-Abstraction): Uses Rich library directly
- [x] Article IX (Integration-First): Integration tests defined

## Notes

- This feature extends the existing Vertex Adapter to work as a Gemini CLI command
- Focus is on user experience with interactive menu
- Model information should be comprehensive but exclude technical details (region, provider, access pattern)
- Authentication follows vertex-config.md pattern exactly
- All implementation details are in plan.md and contracts/, not in this spec

