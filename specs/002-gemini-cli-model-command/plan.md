# Implementation Plan: Gemini CLI Custom `/model` Command

**Branch**: `002-gemini-cli-model-command` | **Date**: 2025-11-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-gemini-cli-model-command/spec.md`

## Summary

Build a custom `/model` command for Gemini CLI that overrides the default command with an interactive menu system. The implementation provides a Rich-based terminal UI with hover details, allowing users to browse, view detailed information, and switch between Vertex AI models (DeepSeek, Qwen, Gemini, Kimi, GPT OSS, Llama) seamlessly within Gemini CLI.

**Technical Approach**: Python-based interactive CLI using Rich library's alternate screen mode for menu navigation. Integrates with existing Vertex Adapter ModelRegistry, extends metadata with context window/pricing/capabilities, and creates Gemini CLI custom command via TOML configuration.

## Technical Context

**Language/Version**: Python 3.9+  
**Primary Dependencies**: 
- rich (existing) - Interactive terminal UI with alternate screen support
- vertex_spec_adapter (existing) - ModelRegistry and VertexAIClient
- pydantic (v2) - Model metadata validation
- pyyaml - Configuration file parsing

**Storage**: 
- Gemini CLI config: `~/.gemini/commands/model.toml`
- Vertex Adapter config: `.specify/config.yaml` (existing)
- Model metadata: Extended ModelRegistry

**Testing**: 
- pytest - Main testing framework
- pytest-cov - Code coverage reporting
- pytest-mock - Mocking Rich console interactions
- pytest-asyncio - Async test support (if needed)
- vcrpy - Record/replay HTTP interactions for integration tests

**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)  
**Project Type**: Extension to existing Vertex Adapter package  
**Performance Goals**: 
- Menu rendering < 50ms
- Hover detail update < 10ms
- Model switch operation < 500ms
- Smooth keyboard navigation (no lag)

**Constraints**: 
- Python 3.9+ required
- Must work within Gemini CLI's command system
- Only models from vertex-config.md supported
- Rich library for UI (already in dependencies)
- Authentication via gcloud auth print-access-token

**Scale/Scope**: 
- Single user CLI tool
- Support for 7 models from vertex-config.md
- Interactive menu with hover details
- Model switching and persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase -1: Pre-Implementation Gates

#### Simplicity Gate (Article VII)

- [x] Using ≤3 projects? → **YES**: Single project (vertex_spec_adapter extension)
- [x] No future-proofing? → **YES**: Only implements required features, no speculative additions

#### Anti-Abstraction Gate (Article VIII)

- [x] Using framework directly? → **YES**: Uses Rich library directly, no custom wrappers
- [x] Single model representation? → **YES**: Extends existing ModelMetadata, no duplicate models

#### Integration-First Gate (Article IX)

- [x] Contracts defined? → **YES**: interactive-menu.md, model-metadata.md, gemini-cli-command.md
- [x] Contract tests planned? → **YES**: Integration tests for Gemini CLI command execution

#### Test-First Gate (Article III)

- [x] Test strategy defined? → **YES**: Unit, integration, and E2E tests planned
- [x] Test scenarios documented? → **YES**: In spec.md and quickstart.md

### Code Quality & Maintainability (Article I)

✅ **PASS**: 
- Modular architecture: Interactive menu component, model metadata extension, Gemini CLI integration
- Clear separation: UI layer (Rich), business logic (ModelRegistry), integration (Gemini CLI TOML)
- Comprehensive docstrings and type hints
- PEP 8 compliance via ruff

### Testing Strategy & Coverage (Article II)

✅ **PASS**: 
- Minimum 80% code coverage target
- Unit tests for menu rendering, navigation logic, metadata formatting
- Integration tests for Gemini CLI command registration
- Mock Rich console for UI testing
- Test keyboard navigation and selection

### Compatibility & Flexibility (Article III)

✅ **PASS**: 
- Works with existing Vertex Adapter
- Extends ModelRegistry without breaking changes
- Compatible with Gemini CLI custom command system
- Cross-platform terminal support

### Security Best Practices (Article IV)

✅ **PASS**: 
- Uses existing authentication (gcloud auth print-access-token)
- No credentials in logs
- Input validation via Pydantic
- Safe file operations for config

### Error Handling & Resilience (Article V)

✅ **PASS**: 
- Graceful handling of missing models
- Error messages for authentication failures
- Fallback for unsupported terminals
- Keyboard interrupt handling

### Performance & Cost Optimization (Article VI)

✅ **PASS**: 
- Efficient menu rendering with Rich
- Lazy loading of model metadata
- Caching of model information
- Minimal API calls

### Developer Experience (Article VII)

✅ **PASS**: 
- Simple installation (single TOML file)
- Clear error messages
- Intuitive keyboard navigation
- Rich visual feedback

### CI/CD & Automation (Article VIII)

✅ **PASS**: 
- Existing CI/CD pipeline
- Automated testing
- Code quality checks
- Documentation generation

## Project Structure

```
vertex_spec_adapter/
├── cli/
│   └── commands/
│       └── model_interactive.py    # Interactive menu implementation
├── core/
│   └── models.py                   # Extended ModelRegistry (add metadata)
└── gemini_cli/
    └── __init__.py                 # Gemini CLI integration helpers
    └── command_installer.py        # Install/update TOML command

specs/002-gemini-cli-model-command/
├── spec.md                         # Feature specification
├── plan.md                         # This file
├── tasks.md                        # Task breakdown
└── contracts/
    └── interactive-menu.md         # Menu UI contract
    └── model-metadata.md           # Extended metadata contract
```

## Implementation Phases

### Phase 0: Research & Design
**Duration**: 1-2 hours

**Objectives**:
- Verify Gemini CLI custom command mechanism
- Design interactive menu UI layout
- Design model metadata extension structure
- Create UI mockups/wireframes

**Deliverables**:
- Research document on Gemini CLI command system
- UI design specification
- Metadata extension schema
- Technical decision document

**Quality Gates**:
- [ ] Gemini CLI command mechanism verified
- [ ] UI design approved
- [ ] Metadata schema defined
- [ ] Technical approach validated

### Phase 1: Extend ModelRegistry with Enhanced Metadata
**Duration**: 2-3 hours

**Objectives**:
- Extend ModelMetadata class with new fields
- Add context window, pricing, capabilities, description
- Update ModelRegistry to load enhanced metadata
- Create metadata for 7 models from vertex-config.md

**Deliverables**:
- Extended ModelMetadata class
- Enhanced ModelRegistry
- Model metadata definitions for all 7 models
- Unit tests for metadata extension

**Quality Gates**:
- [ ] All 7 models have complete metadata
- [ ] Metadata validation works
- [ ] Unit tests pass (80%+ coverage)
- [ ] No breaking changes to existing code

### Phase 2: Interactive Menu Component
**Duration**: 4-5 hours

**Objectives**:
- Implement Rich-based interactive menu
- Add keyboard navigation (arrow keys, Enter, Escape)
- Implement hover details display
- Add current model indicator
- Handle menu state and selection

**Deliverables**:
- Interactive menu class
- Keyboard event handling
- Hover details panel
- Menu rendering logic
- Unit tests for menu component

**Quality Gates**:
- [ ] Menu displays all models correctly
- [ ] Keyboard navigation works smoothly
- [ ] Hover details update in real-time
- [ ] Current model is clearly indicated
- [ ] Unit tests pass (80%+ coverage)

### Phase 3: Model Selection & Switching
**Duration**: 2-3 hours

**Objectives**:
- Implement model selection logic
- Integrate with VertexAIClient for switching
- Update configuration file
- Persist selection across sessions
- Add confirmation feedback

**Deliverables**:
- Model selection handler
- Configuration update logic
- Persistence mechanism
- Success/error feedback
- Integration tests

**Quality Gates**:
- [ ] Model switching works correctly
- [ ] Configuration is updated
- [ ] Selection persists after restart
- [ ] Error handling is robust
- [ ] Integration tests pass

### Phase 4: Gemini CLI Integration
**Duration**: 2-3 hours

**Objectives**:
- Create TOML command file
- Implement command installer script
- Test command registration
- Verify command execution
- Handle command arguments

**Deliverables**:
- `model.toml` command file
- Command installer script
- Integration with Gemini CLI
- Documentation
- Integration tests

**Quality Gates**:
- [ ] Command file is correctly formatted
- [ ] Installer works correctly
- [ ] Command executes in Gemini CLI
- [ ] Arguments are handled properly
- [ ] Integration tests pass

### Phase 5: Error Handling & Edge Cases
**Duration**: 2-3 hours

**Objectives**:
- Handle missing models gracefully
- Handle authentication errors
- Handle unsupported terminals
- Handle keyboard interrupts
- Add helpful error messages

**Deliverables**:
- Error handling implementation
- Error message formatting
- Edge case tests
- User-friendly error messages
- Documentation

**Quality Gates**:
- [ ] All error cases handled
- [ ] Error messages are clear
- [ ] Edge case tests pass
- [ ] User experience is smooth

### Phase 6: Testing & Documentation
**Duration**: 3-4 hours

**Objectives**:
- Write comprehensive unit tests
- Write integration tests
- Write E2E tests
- Update documentation
- Create usage examples

**Deliverables**:
- Complete test suite (80%+ coverage)
- Integration test suite
- E2E test scenarios
- Updated README
- Usage documentation
- Example screenshots/videos

**Quality Gates**:
- [ ] Test coverage ≥ 80%
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Examples work correctly

### Phase 7: Polish & Optimization
**Duration**: 2-3 hours

**Objectives**:
- Optimize menu rendering performance
- Improve hover detail formatting
- Enhance visual design
- Add keyboard shortcuts help
- Performance testing

**Deliverables**:
- Performance optimizations
- Enhanced UI/UX
- Keyboard shortcuts documentation
- Performance benchmarks
- Final polish

**Quality Gates**:
- [ ] Menu rendering < 50ms
- [ ] Hover update < 10ms
- [ ] Visual design is polished
- [ ] Performance meets targets

## Technical Decisions

### TD-001: Interactive Menu Library
**Decision**: Use Rich with `console.screen()` for alternate screen mode

**Rationale**:
- Already in project dependencies
- Supports alternate screen for hover details
- Excellent formatting capabilities
- Cross-platform compatible
- No additional dependencies needed

**Alternatives Considered**:
- Prompt Toolkit: Excellent but not in dependencies
- InquirerPy: Good but no hover support
- Custom implementation: Too complex

### TD-002: Model Metadata Extension
**Decision**: Extend existing ModelMetadata class with optional fields

**Rationale**:
- Maintains backward compatibility
- Uses existing Pydantic validation
- Easy to extend in future
- Type-safe implementation

**Fields Added**:
- `context_window: Optional[str]` - Context window size (e.g., "1M tokens")
- `pricing: Optional[Dict[str, float]]` - Pricing per token (input/output)
- `capabilities: Optional[List[str]]` - Model capabilities
- `description: Optional[str]` - Model description

### TD-003: Gemini CLI Command Format
**Decision**: Use TOML file with shell command execution

**Rationale**:
- Standard Gemini CLI custom command format
- Allows Python script execution
- Supports argument passing
- Easy to install/update

**Format**:
```toml
description = "Manage Vertex AI models"
prompt = """
Execute interactive model selection:
!{python -m vertex_spec_adapter.cli.commands.model_interactive {{args}}}
"""
```

### TD-004: Hover Details Display
**Decision**: Display in right panel (per contracts/interactive-menu.md)

**Rationale**:
- Doesn't interfere with menu navigation
- Easy to read
- Updates smoothly
- Works on different terminal sizes
- Consistent with contract specification

**Layout**:
- Left: Model list (scrollable)
- Right: Hover details panel (per contract)
- Top: Current model indicator

### TD-005: Configuration Persistence
**Decision**: Update `.specify/config.yaml` directly

**Rationale**:
- Uses existing configuration system
- Consistent with Vertex Adapter
- Simple implementation
- No additional config files

## Error Handling Patterns

### EH-001: Missing Model
**Pattern**: Graceful degradation with clear message

```python
try:
    model = registry.get_model_metadata(model_id)
except ModelNotFoundError:
    console.print(f"[red]Model '{model_id}' not found[/]")
    console.print("Available models: ...")
    return None
```

### EH-002: Authentication Failure
**Pattern**: Clear error with troubleshooting steps

```python
try:
    token = get_gcloud_token()
except AuthenticationError as e:
    console.print(f"[red]Authentication failed[/]")
    console.print("Please run: gcloud auth login")
    return None
```

### EH-003: Unsupported Terminal
**Pattern**: Fallback to simple menu

```python
if not console.is_terminal:
    # Fallback to simple text menu
    return simple_text_menu()
```

### EH-004: Keyboard Interrupt
**Pattern**: Clean exit with message

```python
try:
    menu.run()
except KeyboardInterrupt:
    console.print("\n[yellow]Cancelled[/]")
    return None
```

## Logging Strategy

- Use existing `structlog` setup
- Log menu interactions (selection, navigation)
- Log model switches
- Log errors with context
- No sensitive data in logs

## Performance Optimization

1. **Lazy Loading**: Load model metadata only when needed
2. **Caching**: Cache model list and metadata
3. **Efficient Rendering**: Use Rich's efficient update methods
4. **Minimal API Calls**: Cache authentication tokens

## Security Considerations

1. **Authentication**: Use existing gcloud auth (no new credentials)
2. **Input Validation**: Validate all user inputs
3. **File Operations**: Safe file writing with error handling
4. **No Credentials**: Never log or store credentials

## Testing Strategy

### Unit Tests
- Menu rendering
- Keyboard navigation
- Model selection logic
- Metadata formatting
- Error handling

### Integration Tests
- Gemini CLI command registration
- Configuration file updates
- Model switching flow
- End-to-end workflow

### E2E Tests
- Full interactive menu experience
- Model switching and persistence
- Error scenarios
- Cross-platform compatibility

## Deployment

1. **Installation**: Run installer script to create TOML file
2. **Verification**: Test command in Gemini CLI
3. **Documentation**: Update README with usage instructions
4. **Release**: Include in next Vertex Adapter release

## Success Metrics

1. **Functionality**: All 7 models accessible via menu
2. **Performance**: Menu rendering < 50ms, hover < 10ms
3. **Usability**: Smooth navigation, clear feedback
4. **Reliability**: 100% test coverage for critical paths
5. **Documentation**: Complete usage guide

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gemini CLI command system changes | High | Low | Monitor Gemini CLI updates, test regularly |
| Terminal compatibility issues | Medium | Medium | Test on multiple terminals, provide fallback |
| Rich library limitations | Low | Low | Rich is mature and well-maintained |
| Model metadata accuracy | Medium | Low | Validate metadata, provide update mechanism |

## Dependencies

### New Dependencies
- None (using existing Rich library)

### Updated Dependencies
- None

### External Services
- Gemini CLI (user's installation)
- gcloud CLI (user's installation)
- Vertex AI API (existing)

## Timeline Estimate

**Total Duration**: 18-24 hours

- Phase 0: 1-2 hours
- Phase 1: 2-3 hours
- Phase 2: 4-5 hours
- Phase 3: 2-3 hours
- Phase 4: 2-3 hours
- Phase 5: 2-3 hours
- Phase 6: 3-4 hours
- Phase 7: 2-3 hours

## Next Steps

1. Review and approve this plan
2. Create detailed task breakdown (tasks.md)
3. Begin Phase 0: Research & Design
4. Implement phases sequentially
5. Test and validate each phase

