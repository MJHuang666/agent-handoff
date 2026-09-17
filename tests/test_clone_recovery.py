import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "shared/.agents/skills/agent-relay/assets/project-template"


class CloneRecoveryTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)

    def test_fresh_clone_recovers_committed_relay_state_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            clone = root / "clone"
            source.mkdir()
            shutil.copytree(TEMPLATE / "shared/docs", source / "docs")
            shutil.copytree(
                TEMPLATE / "shared/.agents/skills/agent-relay",
                source / ".agents/skills/agent-relay",
            )
            shutil.copy(
                TEMPLATE / "adapters/codex/AGENTS.md", source / "AGENTS.md"
            )

            task = source / "docs/agent/tasks/TASK-RECOVERY-001"
            (task / "progress").mkdir(parents=True)
            (task / "STATE.md").write_text(
                """# Task State

```yaml
task: "TASK-RECOVERY-001"
title: "Recover state after clone"
language: "en-US"
status: IMPLEMENTING
revision: 12
stage_round: 4
assignments:
  planner: "planner-main"
  implementer: "implementer-main"
  reviewer: "reviewer-main"
current_role: implementer
current_participant: "implementer-main"
writer_session: null
execution: idle
subagent_policy: DO_NOT_USE
subagent_decision_ref: "requirement.md#subagents"
previous_role: planner
previous_participant: "planner-main"
previous_progress: progress/001-planning.md
latest_checkpoint: null
plan_version: 1
approval_ref: plan.md#approval-v1
code_delivery_ref: null
next_expected_output: execution.md
blocked_reason: null
unblock_condition: null
resume_status: null
updated_at: "2026-09-17T00:00:00Z"
```
""",
                encoding="utf-8",
            )
            (task / "requirement.md").write_text("# Requirement\n", encoding="utf-8")
            (task / "plan.md").write_text("# Plan\n", encoding="utf-8")
            (task / "decisions.md").write_text(
                "# Decisions\n\n- RELAY-DEC-001: keep state in the repository.\n",
                encoding="utf-8",
            )
            (task / "progress/001-planning.md").write_text(
                "# Planning progress\n\nDecision recorded.\n", encoding="utf-8"
            )
            project_status = source / "docs/agent/PROJECT_STATUS.md"
            project_status.write_text(
                """# Project Status

```yaml
project: "Clone recovery fixture"
goal: "Prove state recovery"
language: en-US
active_task: TASK-RECOVERY-001
updated_at: "2026-09-17T00:00:00Z"
```

## Tasks

| Task | Summary | Status Cache | Revision Cache | Current Role | Current Participant | Path |
|---|---|---|---:|---|---|---|
| TASK-RECOVERY-001 | Clone recovery | IMPLEMENTING | 12 | Implementer | implementer-main | tasks/TASK-RECOVERY-001/ |
""",
                encoding="utf-8",
            )
            index = source / "docs/agent/knowledge-index.md"
            index.write_text(
                """# Knowledge Index

| ID | Summary | Scope | Source | Evidence | Status | Last Verified |
|---|---|---|---|---|---|---|
| RELAY-DEC-001 | Repository state is durable | project | [Decision](tasks/TASK-RECOVERY-001/decisions.md) | [Progress](tasks/TASK-RECOVERY-001/progress/001-planning.md) | ACTIVE | 2026-09-17 |
""",
                encoding="utf-8",
            )

            self.run_git(source, "init", "-b", "main")
            self.run_git(source, "config", "user.email", "relay-test@example.invalid")
            self.run_git(source, "config", "user.name", "Relay Test")
            self.run_git(source, "add", ".")
            self.run_git(source, "commit", "-m", "relay recovery fixture")
            (source / "UNCOMMITTED-SENTINEL.txt").write_text("not migrated\n", encoding="utf-8")
            subprocess.run(["git", "clone", str(source), str(clone)], check=True, capture_output=True, text=True)

            helper = clone / ".agents/skills/agent-relay/scripts/workflow_state.py"
            result = subprocess.run(
                [sys.executable, str(helper), "--repo", str(clone), "status"],
                check=True,
                capture_output=True,
                text=True,
            )
            status = json.loads(result.stdout)
            self.assertEqual(status["active_task"], "TASK-RECOVERY-001")
            self.assertEqual(status["revision"], 12)
            self.assertEqual(status["current_role"], "implementer")
            self.assertEqual(status["current_participant"], "implementer-main")
            self.assertIsNone(status["writer_session"])
            self.assertFalse(status["lock_present"])
            self.assertTrue((clone / "AGENTS.md").is_file())
            self.assertTrue((clone / "docs/agent/knowledge-index.md").is_file())
            self.assertTrue((clone / "docs/agent/tasks/TASK-RECOVERY-001/STATE.md").is_file())
            self.assertFalse((clone / "UNCOMMITTED-SENTINEL.txt").exists())
            index_text = (clone / "docs/agent/knowledge-index.md").read_text(encoding="utf-8")
            self.assertNotIn(str(source), index_text)
            self.assertTrue((clone / "docs/agent/tasks/TASK-RECOVERY-001/decisions.md").is_file())
            self.assertTrue((clone / "docs/agent/tasks/TASK-RECOVERY-001/progress/001-planning.md").is_file())


if __name__ == "__main__":
    unittest.main()
