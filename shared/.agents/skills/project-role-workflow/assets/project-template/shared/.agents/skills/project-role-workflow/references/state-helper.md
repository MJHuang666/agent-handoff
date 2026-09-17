# Workflow State Helper

Use `scripts/workflow_state.py` for coordination-state reads and participant replacements. It requires only Python 3's standard library and keeps Markdown as the source of truth.

## Safety Model

- The lock is short-lived and local to one repository checkout: `project-role-workflow.lock` in the resolved Git directory (including worktrees), otherwise `.project-role-workflow.lock` at the repository root.
- `--expected-revision` is a compare-and-swap guard for active-task changes. A mismatch aborts without changing state.
- Files are written through a same-directory temporary file and `os.replace()`.
- The helper protects workflow state, not product code. It does not authorize merge, release, deployment, deletion, rollback, or overwrite.
- A lock is never removed because of age. Inspect its JSON, confirm the recorded process/session stopped, obtain explicit authorization, then use `release-stale-lock`.

## Read Status

```bash
python3 .agents/skills/project-role-workflow/scripts/workflow_state.py \
  --repo . status
```

The JSON result reports the active task, revision, stage round, participant, execution state, writer session, and lock presence.

## Replace a Participant

The target participant must already be registered with the same role and have `active` or `standby` status. Registering a new identity remains a separate authorized management step.

```bash
python3 .agents/skills/project-role-workflow/scripts/workflow_state.py \
  --repo . replace-agent \
  --role implementer \
  --from cursor-impl \
  --to codex-impl \
  --scope current-task \
  --expected-revision 10 \
  --reason "Cursor quota exhausted" \
  --authorization "User approved in the current conversation"
```

Scopes:

- `current-task`: update the active task assignment snapshot only.
- `project-default`: update only the default used when creating future tasks; no revision is required.
- `both`: update the active task and future default.

When the changed role is current, the helper increments `revision` and `stage_round`, clears writer/checkpoint ownership, creates a `MANAGEMENT` progress record, and leaves the new participant idle. A changed non-current assignment increments only `revision`. Changing Implementer resets the task's subagent decision.

If the state still names a writer session, replacement fails. Only after read-only evidence confirms the writer stopped and the user explicitly authorizes takeover may the command include `--confirm-writer-stopped`.

## Repeated Switching and Identity Status

Participant IDs are immutable and reusable. Switching A → B → A reuses the original A identity and creates a new management record and stage round each time. The selected target becomes `active`; a replaced identity becomes `standby` only when no project default or nonterminal task still references it. `retired` identities require an explicit reactivation decision and are not accepted automatically.

## Stale Lock Recovery

```bash
python3 .agents/skills/project-role-workflow/scripts/workflow_state.py \
  --repo . release-stale-lock \
  --authorization "User confirmed the recorded process stopped"
```

Releasing a lock does not change task ownership. Re-read status and revision before attempting the intended operation again.
