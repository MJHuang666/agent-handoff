import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "shared/.agents/skills/project-role-workflow/scripts/workflow_state.py"
)


PROJECT_STATUS = """# Project Status

```yaml
project: "Demo"
goal: "Test replacements"
language: en-US
active_task: TASK-001
updated_at: null
```

## Tasks

| Task | Summary | Status Cache | Revision Cache | Current Role | Current Participant | Path |
|---|---|---|---:|---|---|---|
| TASK-001 | Demo | IMPLEMENTING | 7 | Implementer | impl-a | tasks/TASK-001/ |

## Latest Handoff

None.
"""


ROLE_BINDINGS = """# Role Bindings

| Participant ID | Tool | Role | Profile | Status | Created At |
|---|---|---|---|---|---|
| planner-a | codex | Planner | profiles/codex/planner-a.md | active | 2026-01-01T00:00:00Z |
| impl-a | cursor | Implementer | profiles/cursor/impl-a.md | active | 2026-01-01T00:00:00Z |
| impl-b | codex | Implementer | profiles/codex/impl-b.md | standby | 2026-01-01T00:00:00Z |
| reviewer-a | codex | Reviewer | profiles/codex/reviewer-a.md | active | 2026-01-01T00:00:00Z |

## Project Defaults

| Role | Participant ID |
|---|---|
| Planner | planner-a |
| Implementer | impl-a |
| Reviewer | reviewer-a |

## Default Binding History

No changes recorded.
"""


STATE = """# Task State

```yaml
task: "TASK-001"
title: "Demo"
language: "en-US"
status: IMPLEMENTING
revision: 7
stage_round: 3
assignments:
  planner: "planner-a"
  implementer: "impl-a"
  reviewer: "reviewer-a"
assignment_change_refs:
  planner: null
  implementer: null
  reviewer: null
current_role: implementer
current_participant: "impl-a"
writer_session: null
execution: idle
subagent_policy: USE
subagent_decision_ref: "requirement.md#subagents"
previous_role: planner
previous_participant: "planner-a"
previous_progress: progress/001-planning-codex.md
latest_checkpoint: null
plan_version: 1
approval_ref: plan.md#approval-v1
code_delivery_ref: null
next_expected_output: execution.md
blocked_reason: null
unblock_condition: null
resume_status: null
updated_at: "2026-01-01T00:00:00Z"
```
"""


class WorkflowStateTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tempdir.name)
        (self.repo / ".git").mkdir()
        agent_dir = self.repo / "docs/agent"
        task_dir = agent_dir / "tasks/TASK-001"
        (task_dir / "progress").mkdir(parents=True)
        (agent_dir / "profiles/codex").mkdir(parents=True)
        (agent_dir / "profiles/cursor").mkdir(parents=True)
        (agent_dir / "PROJECT_STATUS.md").write_text(PROJECT_STATUS, encoding="utf-8")
        (agent_dir / "role-bindings.md").write_text(ROLE_BINDINGS, encoding="utf-8")
        (task_dir / "STATE.md").write_text(STATE, encoding="utf-8")
        for tool, participant, role, status in (
            ("cursor", "impl-a", "implementer", "active"),
            ("codex", "impl-b", "implementer", "standby"),
        ):
            (agent_dir / f"profiles/{tool}/{participant}.md").write_text(
                f"""# Participant Profile

```yaml
participant_id: "{participant}"
display_name: "{participant}"
tool: "{tool}"
role: "{role}"
role_file: "../../roles/{role}.md"
status: {status}
created_at: "2026-01-01T00:00:00Z"
```
""",
                encoding="utf-8",
            )

    def tearDown(self):
        self.tempdir.cleanup()

    def run_cli(self, *args, expect=0):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo), *args],
            text=True,
            capture_output=True,
        )
        self.assertEqual(
            result.returncode,
            expect,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def replace(self, from_id, to_id, revision, *extra, expect=0):
        return self.run_cli(
            "replace-agent",
            "--role",
            "implementer",
            "--from",
            from_id,
            "--to",
            to_id,
            "--scope",
            "current-task",
            "--expected-revision",
            str(revision),
            "--reason",
            "token budget exhausted",
            "--authorization",
            "user approved in chat",
            *extra,
            expect=expect,
        )

    def state_text(self):
        return (self.repo / "docs/agent/tasks/TASK-001/STATE.md").read_text(
            encoding="utf-8"
        )

    def test_status_reports_authoritative_task_state(self):
        result = self.run_cli("status")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["active_task"], "TASK-001")
        self.assertEqual(payload["revision"], 7)
        self.assertEqual(payload["current_participant"], "impl-a")
        self.assertFalse(payload["lock_present"])

    def test_git_worktree_uses_resolved_git_directory_for_lock(self):
        git_dir = self.repo / ".git"
        git_dir.rmdir()
        worktree_git_dir = self.repo / ".git-worktree"
        worktree_git_dir.mkdir()
        git_dir.write_text("gitdir: .git-worktree\n", encoding="utf-8")
        (worktree_git_dir / "project-role-workflow.lock").write_text(
            '{"transaction_id":"worktree-lock"}', encoding="utf-8"
        )
        payload = json.loads(self.run_cli("status").stdout)
        self.assertTrue(payload["lock_present"])

    def test_current_replacement_updates_state_and_resets_implementer_gate(self):
        result = self.replace("impl-a", "impl-b", 7)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["from"], "impl-a")
        self.assertEqual(payload["to"], "impl-b")
        self.assertEqual(payload["output_revision"], 8)

        state = self.state_text()
        self.assertIn('revision: 8', state)
        self.assertIn('stage_round: 4', state)
        self.assertIn('  implementer: "impl-b"', state)
        self.assertIn('current_participant: "impl-b"', state)
        self.assertIn('previous_participant: "impl-a"', state)
        self.assertIn('subagent_policy: UNSELECTED', state)
        self.assertIn('subagent_decision_ref: null', state)
        self.assertRegex(state, r'  implementer: "progress/001-agent-replacement-codex\.md"')

        progress = self.repo / "docs/agent/tasks/TASK-001/progress/001-agent-replacement-codex.md"
        self.assertTrue(progress.exists())
        progress_text = progress.read_text(encoding="utf-8")
        self.assertIn("token budget exhausted", progress_text)
        self.assertIn("stage_round: 4", progress_text)
        self.assertIn("Next role: implementer", progress_text)
        self.assertIn("Next participant: impl-b", progress_text)

    def test_repeated_switch_can_return_to_previous_participant(self):
        self.replace("impl-a", "impl-b", 7)
        self.replace("impl-b", "impl-a", 8)
        state = self.state_text()
        self.assertIn('revision: 9', state)
        self.assertIn('stage_round: 5', state)
        self.assertIn('current_participant: "impl-a"', state)
        self.assertTrue(
            (self.repo / "docs/agent/tasks/TASK-001/progress/002-agent-replacement-cursor.md").exists()
        )

    def test_project_default_replacement_does_not_mutate_active_task(self):
        before = self.state_text()
        result = self.run_cli(
            "replace-agent",
            "--role",
            "implementer",
            "--from",
            "impl-a",
            "--to",
            "impl-b",
            "--scope",
            "project-default",
            "--reason",
            "future tasks use Codex",
            "--authorization",
            "user approved in chat",
        )
        payload = json.loads(result.stdout)
        self.assertIsNone(payload["output_revision"])
        self.assertEqual(self.state_text(), before)
        bindings = (self.repo / "docs/agent/role-bindings.md").read_text(encoding="utf-8")
        self.assertIn("| Implementer | impl-b |", bindings)
        self.assertIn("future tasks use Codex", bindings)

    def test_non_current_role_replacement_preserves_current_owner_and_round(self):
        state_path = self.repo / "docs/agent/tasks/TASK-001/STATE.md"
        state_path.write_text(
            STATE.replace("status: IMPLEMENTING", "status: REVIEWING")
            .replace("current_role: implementer", "current_role: reviewer")
            .replace('current_participant: "impl-a"', 'current_participant: "reviewer-a"'),
            encoding="utf-8",
        )
        self.replace("impl-a", "impl-b", 7)
        state = self.state_text()
        self.assertIn("stage_round: 3", state)
        self.assertIn("current_role: reviewer", state)
        self.assertIn('current_participant: "reviewer-a"', state)
        progress = (
            self.repo / "docs/agent/tasks/TASK-001/progress/001-agent-replacement-codex.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Next role: reviewer", progress)
        self.assertIn("Next participant: reviewer-a", progress)

    def test_both_scope_updates_task_default_and_identity_lifecycle(self):
        self.run_cli(
            "replace-agent",
            "--role",
            "implementer",
            "--from",
            "impl-a",
            "--to",
            "impl-b",
            "--scope",
            "both",
            "--expected-revision",
            "7",
            "--reason",
            "replace everywhere",
            "--authorization",
            "user approved in chat",
        )
        bindings = (self.repo / "docs/agent/role-bindings.md").read_text(encoding="utf-8")
        self.assertIn("| Implementer | impl-b |", bindings)
        self.assertIn(
            "| impl-a | cursor | Implementer | profiles/cursor/impl-a.md | standby |",
            bindings,
        )
        self.assertIn(
            "| impl-b | codex | Implementer | profiles/codex/impl-b.md | active |",
            bindings,
        )
        old_profile = (self.repo / "docs/agent/profiles/cursor/impl-a.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("status: standby", old_profile)

    def test_stale_revision_is_rejected_without_changes(self):
        before = self.state_text()
        result = self.replace("impl-a", "impl-b", 6, expect=2)
        self.assertIn("revision mismatch", result.stderr)
        self.assertEqual(self.state_text(), before)

    def test_existing_lock_blocks_mutation(self):
        lock = self.repo / ".git/project-role-workflow.lock"
        lock.write_text('{"transaction_id":"other"}', encoding="utf-8")
        before = self.state_text()
        result = self.replace("impl-a", "impl-b", 7, expect=3)
        self.assertIn("lock already exists", result.stderr)
        self.assertEqual(self.state_text(), before)

    def test_running_writer_requires_stopped_confirmation(self):
        path = self.repo / "docs/agent/tasks/TASK-001/STATE.md"
        path.write_text(
            STATE.replace("writer_session: null", 'writer_session: "cursor-session-1"').replace(
                "execution: idle", "execution: running"
            ),
            encoding="utf-8",
        )
        denied = self.replace("impl-a", "impl-b", 7, expect=2)
        self.assertIn("writer_session is still running", denied.stderr)
        self.replace("impl-a", "impl-b", 7, "--confirm-writer-stopped")
        self.assertIn("writer_session: null", self.state_text())

    def test_release_lock_requires_authorization(self):
        lock = self.repo / ".git/project-role-workflow.lock"
        lock.write_text('{"transaction_id":"orphan"}', encoding="utf-8")
        denied = self.run_cli("release-stale-lock", expect=2)
        self.assertIn("authorization", denied.stderr)
        self.run_cli(
            "release-stale-lock",
            "--authorization",
            "user confirmed old process stopped",
        )
        self.assertFalse(lock.exists())


if __name__ == "__main__":
    unittest.main()
