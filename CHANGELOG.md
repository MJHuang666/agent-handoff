# Changelog

All notable changes to Project Role Workflow are documented here.

## [1.2.0] - 2026-09-16

### Added

- Chinese and English commands for repository initialization and continuation.
- Project-language selection before role-tool assignment, with localized templates for Chinese and English projects.
- Implementer subagent decision gate, recorded in task state before product-code changes.
- A compact `docs/agent/protocol.md` fallback when a host prevents project-level `.agents/` installation.

### Changed

- Automatic initialization now excludes the example task from active project state.
- Project-level Skill installation degrades gracefully when the host sandbox denies `.agents/` writes.

## [1.1.0] - 2026-09-16

### Added

- Initial Planner, Implementer, and Reviewer file-based collaboration workflow.
