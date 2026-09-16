# Open-Source Release Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Project Role Workflow v1.2.0 ready for an initial public GitHub repository without publishing or pushing it.

**Architecture:** Keep the repository source-only: human-authored templates and documentation are committed, while generated ZIP bundles are GitHub Release assets. GitHub Actions reproduces the release bundle in a temporary directory and validates its structure, language overlays, checksums, and Markdown links.

**Tech Stack:** Git, Markdown, YAML, GitHub Actions, Bash, and Python standard library for CI-only static checks.

**Spec:** `docs/superpowers/specs/2026-09-16-multi-agent-project-state-sharing-design.md`

## Global Constraints

- License: Apache-2.0.
- Default Git branch: `main`; do not create a remote or push.
- Release ZIP and checksum are GitHub Release assets, not tracked source files.
- Ignore `.DS_Store`, `._*`, `.learnings/`, and `dist/`.
- CI must run without changing tracked files and must not depend on a prebuilt local ZIP.
- Automatic initialization excludes `TASK-EXAMPLE-001`; manual source documentation may retain it as an example.

---

### Task 1: Establish repository and community metadata

**Files:**
- Create: `LICENSE`, `.gitignore`, `.gitattributes`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/ISSUE_TEMPLATE/tool-adapter.yml`, `.github/PULL_REQUEST_TEMPLATE.md`

- [x] Add the exact Apache License 2.0 text to `LICENSE`.
- [x] Add source-only ignore and line-ending rules.
- [x] Document contribution boundaries: modify the canonical source, synchronize generated copies, then run the validation command.
- [x] Add issue and pull-request templates specific to workflow protocol and tool adapter changes.

### Task 2: Correct public documentation

**Files:**
- Modify: `README.md`, `distribution/INSTALL.md`, `distribution/INSTALL_PROMPT.md`
- Modify: `docs/superpowers/specs/2026-09-16-multi-agent-project-state-sharing-design.md`
- Create: `README.zh-CN.md`

- [x] Make the English README the GitHub landing page and link the complete Chinese README.
- [x] Clarify that ZIP downloads belong to GitHub Releases and that automatic initialization excludes the example task.
- [x] Change the design specification from a pending implementation claim to an implemented v1.2.0 baseline with stated verification boundaries.

### Task 3: Add reproducible CI validation

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/scripts/validate-release.sh`

- [x] Define failure conditions first: invalid Skill metadata, broken local links, untranslated English overlays, AppleDouble files, example task inside bootstrap assets, or a non-extractable generated archive.
- [x] Implement a shell validator that rebuilds a temporary release ZIP from source and checks its SHA-256 and contents.
- [x] Configure GitHub Actions on pushes, pull requests, and manual dispatch using Python 3.12 for CI-only static checks.

### Task 4: Initialize and verify local Git baseline

**Files:**
- Remove from tracking scope: `.learnings/`, `dist/`, AppleDouble metadata

- [x] Initialize Git with `main` if absent.
- [x] Run `git diff --check`, the CI validation script, and a clean-source status review.
- [x] Create the initial local commit only after all checks pass; do not add a remote or push.
