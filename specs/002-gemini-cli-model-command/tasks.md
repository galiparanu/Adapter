# Task List: Gemini CLI Custom `/model` Command

**Feature**: 002-gemini-cli-model-command  
**Plan**: [plan.md](./plan.md)  
**Spec**: [spec.md](./spec.md)

## Task Status Legend

- [ ] Pending
- [P] Can be parallelized
- [ ] In Progress
- [x] Completed
- [~] Blocked/Deferred

---

## Phase 0: Research & Design

### T001: Research Gemini CLI Custom Command System
**Status**: [ ]  
**Dependencies**: None  
**Description**: 
- Verify custom command mechanism via TOML files
- Test command registration process
- Document command file format and structure
- Test argument passing and execution

**Acceptance**:
- [ ] Gemini CLI command mechanism verified
- [ ] Test command created and working
- [ ] Documentation written

### T002: Design Interactive Menu UI Layout
**Status**: [ ]  
**Dependencies**: T001  
**Description**:
- Design menu layout (list + hover panel)
- Design keyboard navigation flow
- Design visual indicators (current model, selection)
- Create wireframe/mockup

**Acceptance**:
- [ ] UI layout designed
- [ ] Navigation flow documented
- [ ] Visual design approved

### T003: Design Model Metadata Extension Schema
**Status**: [P]  
**Dependencies**: None  
**Description**:
- Design ModelMetadata extension fields
- Define context window format
- Define pricing structure
- Define capabilities format
- Define description format

**Acceptance**:
- [ ] Schema designed
- [ ] Field types defined
- [ ] Validation rules specified

### T004: Create Technical Decision Document
**Status**: [ ]  
**Dependencies**: T001, T002, T003  
**Description**:
- Document all technical decisions
- Document alternatives considered
- Document rationale for each decision

**Acceptance**:
- [ ] All decisions documented
- [ ] Rationale clear
- [ ] Document reviewed

---

## Phase 1: Extend ModelRegistry with Enhanced Metadata

### T003a: Research Model Metadata Values
**Status**: [ ]  
**Dependencies**: T003  
**Description**:
- Research actual context window sizes for all 7 models from Vertex AI documentation
- Research pricing information (per 1K tokens) for input/output
- Research model capabilities and specializations
- Research model descriptions and use cases
- Document findings in research.md or reference data source

**Files**:
- `specs/002-gemini-cli-model-command/research.md`

**Acceptance**:
- [ ] Context window values documented for all 7 models
- [ ] Pricing information documented (if available)
- [ ] Capabilities documented for all models
- [ ] Descriptions documented for all models
- [ ] Data source referenced (Vertex AI docs, vertex-config.md, etc.)

### T014a: Write Test Stubs for Extended ModelMetadata
**Status**: [ ]  
**Dependencies**: T003a  
**Description**:
- Create test file structure for ModelMetadata extension tests
- Write test stubs for new field initialization
- Write test stubs for field validation
- Write test stubs for to_dict() with new fields
- Write test stubs for backward compatibility
- Tests should FAIL initially (Red phase of TDD)

**Files**:
- `tests/unit/test_models.py`

**Acceptance**:
- [ ] Test file created
- [ ] All test stubs written
- [ ] Tests fail as expected (Red phase)
- [ ] Test structure follows TDD principles

### T005: Extend ModelMetadata Class
**Status**: [ ]  
**Dependencies**: T014a  
**Description**:
- Add `context_window: Optional[str]` field
- Add `pricing: Optional[Dict[str, float]]` field
- Add `capabilities: Optional[List[str]]` field
- Add `description: Optional[str]` field
- Update `to_dict()` method
- Add validation for new fields
- Make tests pass (Green phase of TDD)

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] All fields added
- [ ] Validation works
- [ ] Backward compatible
- [ ] Type hints correct
- [ ] All tests from T014a now pass

### T006: Create Model Metadata for DeepSeek V3.1
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `deepseek-ai/deepseek-v3.1-maas`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `us-west2`
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T007: Create Model Metadata for Qwen Coder
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `qwen/qwen3-coder-480b-a35b-instruct-maas`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `us-south1`
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T008: Create Model Metadata for Gemini 2.5 Pro
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `gemini-2.5-pro`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `global` (per vertex-config.md)
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T009: Create Model Metadata for DeepSeek R1 0528
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `deepseek-ai/deepseek-r1-0528-maas`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `us-central1`
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T010: Create Model Metadata for Kimi K2
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `moonshotai/kimi-k2-thinking-maas`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `global` (per vertex-config.md)
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T011: Create Model Metadata for GPT OSS 120B
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `openai/gpt-oss-120b-maas`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `us-central1`
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T012: Create Model Metadata for Llama 3.1
**Status**: [P]  
**Dependencies**: T005, T003a  
**Description**:
- Add metadata for `meta/llama-3.1-405b-instruct-maas`
- Set context window (from T003a research)
- Set pricing (from T003a research)
- Set capabilities (from T003a research)
- Set description (from T003a research)
- Set region: `us-central1`
- Add to MODEL_METADATA dict

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Metadata complete
- [ ] All fields populated
- [ ] Region correct

### T013: Remove Old Model Metadata (Claude, etc.)
**Status**: [ ]  
**Dependencies**: T006-T012  
**Description**:
- Remove Claude models (not in vertex-config.md)
- Remove old Gemini models (not in vertex-config.md)
- Remove old Qwen models (not in vertex-config.md)
- Keep only 7 models from vertex-config.md

**Files**:
- `vertex_spec_adapter/core/models.py`

**Acceptance**:
- [ ] Only 7 models remain
- [ ] All removed models deleted
- [ ] No references to removed models

### T014b: Complete Unit Tests for Extended ModelMetadata
**Status**: [ ]  
**Dependencies**: T005-T013  
**Description**:
- Complete test implementation (Refactor phase of TDD)
- Add edge case tests
- Add integration tests with ModelRegistry
- Verify test coverage ≥ 80%
- Verify backward compatibility

**Files**:
- `tests/unit/test_models.py`

**Acceptance**:
- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] Backward compatibility verified
- [ ] Edge cases covered

---

## Phase 2: Interactive Menu Component

### T015: Create Interactive Menu Base Class
**Status**: [ ]  
**Dependencies**: T002, T014  
**Description**:
- Create `ModelInteractiveMenu` class
- Initialize Rich console with alternate screen
- Set up basic menu structure
- Implement menu state management

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Class created
- [ ] Console initialized
- [ ] Basic structure works

### T016: Implement Model List Rendering
**Status**: [ ]  
**Dependencies**: T015  
**Description**:
- Render list of all available models
- Format model names nicely
- Add current model indicator (✓)
- Add selection highlight
- Support scrolling for long lists

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] List renders correctly
- [ ] Current model marked
- [ ] Selection highlighted
- [ ] Scrolling works

### T017: Implement Keyboard Navigation
**Status**: [ ]  
**Dependencies**: T016  
**Description**:
- Handle arrow up/down keys
- Handle Enter key (selection)
- Handle Escape key (cancel)
- Handle Home/End keys (first/last)
- Smooth navigation without lag

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] All keys work
- [ ] Navigation is smooth
- [ ] No lag or jank

### T018: Implement Hover Details Panel
**Status**: [ ]  
**Dependencies**: T016  
**Description**:
- Display model information when highlighted
- Show context window
- Show pricing (if available)
- Show capabilities
- Show description
- Format nicely with Rich

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Details display correctly
- [ ] Updates in real-time
- [ ] Formatting is clear
- [ ] All fields shown (except region/provider/access_pattern)

### T019: Implement Current Model Display
**Status**: [ ]  
**Dependencies**: T015  
**Description**:
- Display current model at top of menu
- Format clearly with Rich
- Show model name and ID
- Update when model changes

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Current model displayed
- [ ] Format is clear
- [ ] Updates correctly

### T020: Implement Menu Layout with Rich Layout
**Status**: [ ]  
**Dependencies**: T016, T018, T019  
**Description**:
- Use Rich Layout for structured display
- Left panel: Model list
- Right/Bottom panel: Hover details
- Top: Current model indicator
- Responsive to terminal size

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Layout works correctly
- [ ] Responsive to terminal size
- [ ] All panels visible
- [ ] Looks polished

### T021: Write Unit Tests for Menu Component
**Status**: [ ]  
**Dependencies**: T015-T020  
**Description**:
- Test menu initialization
- Test rendering
- Test keyboard navigation
- Test hover details
- Mock Rich console

**Files**:
- `tests/unit/test_model_interactive.py`

**Acceptance**:
- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] Mocks work correctly

---

## Phase 3: Model Selection & Switching

### T022: Implement Model Selection Handler
**Status**: [ ]  
**Dependencies**: T017  
**Description**:
- Handle Enter key press
- Get selected model ID
- Validate model exists
- Return selected model

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Selection works
- [ ] Validation works
- [ ] Returns correct model

### T023: Implement Model Switching Logic
**Status**: [ ]  
**Dependencies**: T022  
**Description**:
- Use VertexAIClient to switch model
- Update client configuration
- Handle switch errors
- Provide feedback

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Switching works
- [ ] Errors handled
- [ ] Feedback provided

### T024: Implement Configuration Update
**Status**: [ ]  
**Dependencies**: T023  
**Description**:
- Update `.specify/config.yaml` with new model
- Use ConfigurationManager
- Preserve other config settings
- Handle file errors

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Config updated
- [ ] Other settings preserved
- [ ] Errors handled

### T025: Implement Selection Persistence
**Status**: [ ]  
**Dependencies**: T024  
**Description**:
- Save selection to config file
- Load selection on startup
- Verify persistence works
- Handle missing config

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Selection persists
- [ ] Loads on startup
- [ ] Handles missing config

### T026: Implement Success/Error Feedback
**Status**: [ ]  
**Dependencies**: T023, T024  
**Description**:
- Show success message after switch
- Show error message on failure
- Format messages nicely with Rich
- Clear and helpful messages

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Messages clear
- [ ] Formatting good
- [ ] Helpful content

### T027: Write Integration Tests for Model Switching
**Status**: [ ]  
**Dependencies**: T022-T026  
**Description**:
- Test full switching flow
- Test configuration update
- Test persistence
- Test error handling

**Files**:
- `tests/integration/test_model_switching.py`

**Acceptance**:
- [ ] All tests pass
- [ ] Full flow tested
- [ ] Error cases covered

---

## Phase 4: Gemini CLI Integration

### T028: Create Gemini CLI Command TOML File
**Status**: [ ]  
**Dependencies**: T015-T027  
**Description**:
- Create `model.toml` file template
- Add description
- Add prompt with Python script call
- Support argument passing

**Files**:
- `vertex_spec_adapter/gemini_cli/model.toml`

**Acceptance**:
- [ ] TOML file created
- [ ] Format correct
- [ ] Script call works

### T029: Create Command Installer Script
**Status**: [ ]  
**Dependencies**: T028  
**Description**:
- Create installer script
- Copy TOML to `~/.gemini/commands/`
- Create directory if needed
- Verify installation
- Provide feedback

**Files**:
- `vertex_spec_adapter/gemini_cli/command_installer.py`
- `scripts/install_gemini_model_command.py`

**Acceptance**:
- [ ] Installer works
- [ ] Directory created
- [ ] File copied
- [ ] Verification works

### T030: Test Command Registration
**Status**: [ ]  
**Dependencies**: T029  
**Description**:
- Run installer
- Verify TOML file in correct location
- Test command in Gemini CLI
- Verify command executes

**Files**:
- Manual testing

**Acceptance**:
- [ ] Command registered
- [ ] Command executes
- [ ] No errors

### T031: Implement Command Argument Handling
**Status**: [ ]  
**Dependencies**: T028  
**Description**:
- Parse `{{args}}` from Gemini CLI
- Support optional arguments
- Handle no arguments (show menu)
- Handle invalid arguments

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Arguments parsed
- [ ] No args shows menu
- [ ] Invalid args handled

### T032: Write Integration Tests for Gemini CLI Integration
**Status**: [ ]  
**Dependencies**: T028-T031  
**Description**:
- Test TOML file format
- Test installer script
- Test command execution
- Mock Gemini CLI if needed

**Files**:
- `tests/integration/test_gemini_cli_integration.py`

**Acceptance**:
- [ ] All tests pass
- [ ] Integration works
- [ ] Edge cases covered

---

## Phase 5: Error Handling & Edge Cases

### T033: Handle Missing Models Gracefully
**Status**: [ ]  
**Dependencies**: T015-T032  
**Description**:
- Check model exists before display
- Show error if model missing
- List available models
- Don't crash on missing model

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Missing model handled
- [ ] Error message clear
- [ ] No crashes

### T034: Handle Authentication Errors
**Status**: [ ]  
**Dependencies**: T015-T032  
**Description**:
- Check gcloud auth before use
- Show clear error if not authenticated
- Provide troubleshooting steps
- Don't crash on auth error

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Auth errors handled
- [ ] Error message helpful
- [ ] Troubleshooting provided

### T035: Handle Unsupported Terminals
**Status**: [ ]  
**Dependencies**: T015-T032  
**Description**:
- Detect terminal support
- Fallback to simple text menu
- Show warning if unsupported
- Still functional

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Terminal detection works
- [ ] Fallback works
- [ ] Warning shown

### T036: Handle Keyboard Interrupts
**Status**: [ ]  
**Dependencies**: T015-T032  
**Description**:
- Catch KeyboardInterrupt
- Clean exit from menu
- Show cancellation message
- Don't leave terminal in bad state

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Interrupts handled
- [ ] Clean exit
- [ ] Terminal state preserved

### T037: Add Helpful Error Messages
**Status**: [ ]  
**Dependencies**: T033-T036  
**Description**:
- Format all error messages with Rich
- Include troubleshooting steps
- Use clear language
- Be helpful and actionable

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Messages clear
- [ ] Troubleshooting included
- [ ] Actionable advice

### T038: Write Tests for Error Cases
**Status**: [ ]  
**Dependencies**: T033-T037  
**Description**:
- Test missing model handling
- Test auth error handling
- Test terminal fallback
- Test keyboard interrupt

**Files**:
- `tests/unit/test_model_interactive_errors.py`

**Acceptance**:
- [ ] All error cases tested
- [ ] Tests pass
- [ ] Coverage good

---

## Phase 6: Testing & Documentation

### T039: Write Comprehensive Unit Tests
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Complete unit test coverage
- Test all menu functions
- Test all model operations
- Mock external dependencies
- Achieve 80%+ coverage

**Files**:
- `tests/unit/test_model_interactive.py`
- `tests/unit/test_models_extended.py`

**Acceptance**:
- [ ] Coverage ≥ 80%
- [ ] All tests pass
- [ ] Mocks work correctly

### T040: Write Integration Tests
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Test full menu workflow
- Test model switching end-to-end
- Test configuration updates
- Test Gemini CLI integration

**Files**:
- `tests/integration/test_model_menu_workflow.py`
- `tests/integration/test_gemini_cli_integration.py`

**Acceptance**:
- [ ] All workflows tested
- [ ] Tests pass
- [ ] Real scenarios covered

### T041: Write E2E Test Scenarios
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Test complete user journey
- Test error scenarios
- Test cross-platform compatibility
- Document test scenarios

**Files**:
- `tests/e2e/test_model_command_e2e.py`

**Acceptance**:
- [ ] Scenarios documented
- [ ] Tests pass
- [ ] User journey works

### T042: Update README with Usage Instructions
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Add section on `/model` command
- Add installation instructions
- Add usage examples
- Add screenshots if possible

**Files**:
- `README.md`

**Acceptance**:
- [ ] Instructions clear
- [ ] Examples work
- [ ] Complete documentation

### T043: Create Usage Documentation
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Create detailed usage guide
- Document keyboard shortcuts
- Document menu features
- Document error handling

**Files**:
- `docs/gemini-cli-model-command.md`

**Acceptance**:
- [ ] Guide complete
- [ ] All features documented
- [ ] Examples included

### T044: Create Example Screenshots/Videos
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Capture menu screenshots
- Show hover details
- Show model switching
- Create demo video (optional)

**Files**:
- `docs/images/model-menu-*.png`

**Acceptance**:
- [ ] Screenshots clear
- [ ] Features visible
- [ ] Good quality

---

## Phase 7: Polish & Optimization

### T045: Optimize Menu Rendering Performance
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Profile menu rendering
- Optimize Rich updates
- Reduce unnecessary redraws
- Achieve < 50ms render time

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Render time < 50ms
- [ ] No unnecessary redraws
- [ ] Smooth performance

### T046: Optimize Hover Detail Updates
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Profile hover updates
- Optimize detail rendering
- Cache formatted details
- Achieve < 10ms update time

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Update time < 10ms
- [ ] Caching works
- [ ] Smooth updates

### T047: Enhance Visual Design
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Improve colors and styling
- Add visual polish
- Improve spacing and layout
- Make it look professional

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`

**Acceptance**:
- [ ] Design polished
- [ ] Looks professional
- [ ] Good UX

### T048: Add Keyboard Shortcuts Help
**Status**: [ ]  
**Dependencies**: All previous phases  
**Description**:
- Display keyboard shortcuts
- Show help in menu
- Document shortcuts
- Make discoverable

**Files**:
- `vertex_spec_adapter/cli/commands/model_interactive.py`
- `docs/gemini-cli-model-command.md`

**Acceptance**:
- [ ] Shortcuts displayed
- [ ] Help accessible
- [ ] Documented

### T049: Performance Testing & Benchmarking
**Status**: [ ]  
**Dependencies**: T045, T046  
**Description**:
- Benchmark menu rendering
- Benchmark hover updates
- Benchmark model switching
- Document performance metrics

**Files**:
- `tests/performance/test_menu_performance.py`

**Acceptance**:
- [ ] Benchmarks created
- [ ] Metrics documented
- [ ] Performance meets targets

### T050: Final Polish & Code Review
**Status**: [ ]  
**Dependencies**: All previous tasks  
**Description**:
- Code review
- Final bug fixes
- Final documentation updates
- Final testing
- Prepare for release

**Files**:
- All files

**Acceptance**:
- [ ] Code reviewed
- [ ] All bugs fixed
- [ ] Documentation complete
- [ ] Ready for release

---

## Summary

**Total Tasks**: 52 (added T003a, T014a, T014b split)  
**Parallelizable Tasks**: T006-T012 (7 tasks)  
**Estimated Duration**: 19-25 hours (added research task)

**Phase Breakdown**:
- Phase 0: 5 tasks (1-2 hours) - Added T003a
- Phase 1: 12 tasks (3-4 hours) - Added T003a, T014a, split T014 to T014b
- Phase 2: 7 tasks (4-5 hours)
- Phase 3: 6 tasks (2-3 hours)
- Phase 4: 5 tasks (2-3 hours)
- Phase 5: 6 tasks (2-3 hours)
- Phase 6: 6 tasks (3-4 hours)
- Phase 7: 6 tasks (2-3 hours)

**Critical Path**: T001 → T002 → T003a → T014a → T005 → T015 → T016 → T017 → T018 → T022 → T023 → T024 → T028 → T029

**Test-First Compliance**: ✅ T014a (test stubs) comes before T005 (implementation), ensuring Article III compliance

**Dependencies**:
- Phase 1 must complete before Phase 2
- Phase 2 must complete before Phase 3
- Phase 3 must complete before Phase 4
- Phases 5-7 can be done in parallel after Phase 4

