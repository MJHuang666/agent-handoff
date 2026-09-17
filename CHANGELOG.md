# Changelog

All notable changes to Project Role Workflow are documented here.

## [1.3.0] - 2026-09-17

### Added

- Repeated, scoped Agent replacement commands in Chinese and English for current tasks, future defaults, or both.
- A Python-standard-library state helper with a short-lived local lock, expected-revision validation, atomic file replacement, and authorized stale-lock recovery.
- Per-role assignment change references and append-only MANAGEMENT records for participant changes.

### Changed

- Participant lifecycle now distinguishes `active`, reusable `standby`, and explicitly retired identities.
- Implementer replacement resets the subagent decision so the new participant must choose again.

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
