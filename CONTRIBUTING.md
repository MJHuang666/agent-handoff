# Contributing

Thank you for improving Project Role Workflow.

## Before editing

- Read `README.md`, `shared/docs/agent/protocol.md`, and the relevant Skill instructions.
- Keep `shared/` as the canonical source. The project-template copies under `shared/.agents/skills/project-role-workflow/assets/project-template/` are generated/distribution-facing mirrors and must stay consistent with their source behavior.
- Do not commit `.DS_Store`, `._*`, `.learnings/`, or `dist/`.

## Change boundaries

- Protocol changes must preserve stable file names, YAML keys, status enums, and identifiers unless the change explicitly documents a migration.
- A tool adapter must be thin: it may provide discovery instructions, but it must not fork the core protocol.
- Changes that affect user-facing workflow must update both Chinese and English initialized-project templates.
- Do not put real credentials, local paths, user data, or private project context in examples.

## Validation

Run the same check used by CI before opening a pull request:

```bash
bash .github/scripts/validate-release.sh
```

The script validates the source tree, language overlays, local Markdown links, bootstrap exclusions, and a freshly built release archive.

## Pull requests

Keep a pull request focused. Explain the workflow behavior changed, the compatibility impact, and the validation output. If an adapter has only been documented but not tested in a fresh tool session, label it as unverified.
