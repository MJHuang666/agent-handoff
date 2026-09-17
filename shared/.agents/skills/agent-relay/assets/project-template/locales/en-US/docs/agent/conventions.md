# Conventions

- Use ISO-8601 timestamps with an explicit timezone.
- Keep `participant_id`, tool, and role immutable after registration.
- Profile status is `active`, reusable `standby`, or explicitly reactivated `retired`.
- Use stable task IDs: `TASK-YYYYMMDD-NNN`.
- Keep status enum values, YAML keys, file names, delivery IDs, and review issue IDs unchanged across languages.
- Write all human-facing prose in `PROJECT_STATUS.md.language`.
- Append progress and delivery history; do not rewrite prior evidence.
- A complete commit ID is preferred. Uncommitted delivery evidence must identify every changed, deleted, and untracked file plus fingerprints or a complete diff snapshot.
