# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-01

### Fixed
- **Spec Kit v0.0.55+ Compatibility**: Updated integration logic to properly detect and handle YAML frontmatter in Spec Kit command files
  - Integration directives now correctly insert after frontmatter closing `---` instead of after markdown headings
  - Added fallback for command files without YAML frontmatter
  - Maintains idempotency (no duplicate sections when running `pantheon integrate` multiple times)
  - All integration validation tests updated to match Spec Kit v0.0.55 structure

### Changed
- Integration functions (`integrate_implement_command`, `integrate_plan_command`, `integrate_tasks_command`) now use YAML frontmatter detection instead of markdown heading detection
- Test fixtures updated to match real Spec Kit v0.0.55 command file structure
- Test coverage increased to 92% on `spec_kit.py` (27 tests total, up from 25)

### Technical
- Added edge case tests for files without frontmatter and malformed frontmatter
- Enhanced integration validation with more robust parsing
- Verified end-to-end workflow with actual Spec Kit v0.0.55 installation

## [0.1.0] - 2025-10-01

### Added
- Initial release of Pantheon agents library
- DEV agent with 8-phase quality-focused workflow
- CLI commands: `init`, `integrate`, `rollback`, `list`
- Spec Kit integration with minimal directives approach
- Automatic backup and rollback functionality
- Comprehensive test suite (25 tests, 91% coverage on core)
- Type checking with mypy (strict mode)
- Linting with ruff
- Python 3.9+ support

### Features
- **DEV Agent Workflow**:
  - Phase 1-3: Understand → Plan → Iterate
  - Phase 4: Document with quality standards
  - Phase 5: Implement with TDD support
  - Phase 6-8: Verify → Finalize → Iterate
- **Spec Kit Integration**:
  - `/plan` enhancement with quality standards
  - `/tasks` enhancement with subtask format
  - `/implement` enhancement with DEV delegation
- **Safety Features**:
  - Timestamped backups before integration
  - Easy rollback with `pantheon rollback`
  - Validation of integration success

### Technical
- Built on Claude Code's sub-agent architecture
- Stateless sub-agent invocation pattern
- Separate context windows for clean execution
- Tool scoping for focused agent behavior
- TypedDict for type-safe return values

### Documentation
- Comprehensive README with examples
- API documentation for all functions
- Development setup guide
- Contributing guidelines

[0.1.1]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.1.1
[0.1.0]: https://github.com/alex-abrams711/pantheon/releases/tag/v0.1.0
