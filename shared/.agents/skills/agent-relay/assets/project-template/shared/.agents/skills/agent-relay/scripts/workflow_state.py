#!/usr/bin/env python3
"""Safe state mutations for Agent Relay repositories.

The runtime deliberately uses only the Python standard library.  Markdown
remains the human-readable source of truth; this helper adds a short-lived
local lock, expected-revision checks, and atomic file replacement.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


ROLE_KEYS = {"planner", "implementer", "reviewer"}
ROLE_LABELS = {key: key.title() for key in ROLE_KEYS}
SCOPES = {"current-task", "project-default", "both"}


class WorkflowError(Exception):
    def __init__(self, message: str, exit_code: int = 2):
        super().__init__(message)
        self.exit_code = exit_code


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def unquote(value: str):
    value = value.strip()
    if value in {"null", "~"}:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def quote(value):
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if value in {
        "idle",
        "running",
        "paused",
        "active",
        "standby",
        "retired",
        "UNSELECTED",
        "USE",
        "DO_NOT_USE",
    }:
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def yaml_block(text: str) -> tuple[str, int, int]:
    match = re.search(r"```yaml\s*\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise WorkflowError("missing YAML block")
    return match.group(1), match.start(1), match.end(1)


def parse_simple_yaml(text: str) -> dict:
    block, _, _ = yaml_block(text)
    result: dict = {}
    current_map: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  ") and current_map:
            match = re.match(r"\s{2}([a-zA-Z0-9_-]+):\s*(.*)$", raw)
            if match:
                result[current_map][match.group(1)] = unquote(match.group(2))
            continue
        match = re.match(r"([a-zA-Z0-9_-]+):\s*(.*)$", raw)
        if not match:
            current_map = None
            continue
        key, value = match.groups()
        if value == "":
            result[key] = {}
            current_map = key
        else:
            result[key] = unquote(value)
            current_map = None
    return result


def replace_yaml_block(text: str, block: str) -> str:
    _, start, end = yaml_block(text)
    return text[:start] + block + text[end:]


def set_scalar(text: str, key: str, value) -> str:
    block, _, _ = yaml_block(text)
    pattern = re.compile(rf"^{re.escape(key)}:\s*.*$", re.MULTILINE)
    replacement = f"{key}: {quote(value)}"
    if not pattern.search(block):
        block = block.rstrip() + "\n" + replacement
    else:
        block = pattern.sub(replacement, block, count=1)
    return replace_yaml_block(text, block)


def set_nested(text: str, section: str, key: str, value, *, after: str | None = None) -> str:
    block, _, _ = yaml_block(text)
    lines = block.splitlines()
    section_index = next((i for i, line in enumerate(lines) if line == f"{section}:"), None)
    if section_index is None:
        insert_at = len(lines)
        if after:
            after_index = next((i for i, line in enumerate(lines) if line == f"{after}:"), None)
            if after_index is not None:
                insert_at = after_index + 1
                while insert_at < len(lines) and lines[insert_at].startswith("  "):
                    insert_at += 1
        lines[insert_at:insert_at] = [f"{section}:", f"  {key}: {quote(value)}"]
    else:
        end = section_index + 1
        found = None
        while end < len(lines) and lines[end].startswith("  "):
            if re.match(rf"\s{{2}}{re.escape(key)}:\s*", lines[end]):
                found = end
            end += 1
        if found is None:
            lines.insert(end, f"  {key}: {quote(value)}")
        else:
            lines[found] = f"  {key}: {quote(value)}"
    return replace_yaml_block(text, "\n".join(lines))


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def lock_paths(repo: Path) -> tuple[Path, Path]:
    """Return canonical and v1.4 legacy lock paths for this checkout."""
    git_path = repo / ".git"
    if git_path.is_dir():
        directory = git_path
        canonical_name = "agent-relay.lock"
        legacy_name = "project-role-workflow.lock"
    elif git_path.is_file():
        first_line = git_path.read_text(encoding="utf-8").splitlines()[0].strip()
        if first_line.startswith("gitdir:"):
            raw_git_dir = first_line.split(":", 1)[1].strip()
            resolved_git_dir = Path(raw_git_dir)
            if not resolved_git_dir.is_absolute():
                resolved_git_dir = (repo / resolved_git_dir).resolve()
            directory = resolved_git_dir
            canonical_name = "agent-relay.lock"
            legacy_name = "project-role-workflow.lock"
        else:
            directory = repo
            canonical_name = ".agent-relay.lock"
            legacy_name = ".project-role-workflow.lock"
    else:
        directory = repo
        canonical_name = ".agent-relay.lock"
        legacy_name = ".project-role-workflow.lock"
    return directory / canonical_name, directory / legacy_name


def lock_path(repo: Path) -> Path:
    return lock_paths(repo)[0]


def existing_locks(repo: Path) -> list[Path]:
    return [path for path in lock_paths(repo) if path.exists()]


@contextmanager
def state_lock(repo: Path, operation: str):
    path = lock_path(repo)
    metadata = {
        "transaction_id": str(uuid.uuid4()),
        "operation": operation,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "created_at": now_iso(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    locked = existing_locks(repo)
    if locked:
        raise WorkflowError(
            "lock already exists: "
            + ", ".join(str(item) for item in locked)
            + "; inspect it and use release-stale-lock only with authorization",
            exit_code=3,
        )
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise WorkflowError(
            f"lock already exists: {path}; inspect it and use release-stale-lock only with authorization",
            exit_code=3,
        ) from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(metadata, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        yield metadata
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def join_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def find_table(text: str, header_first_cell: str) -> tuple[list[str], int, int]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("|") and split_table_row(line)[0] == header_first_cell:
            end = index + 2
            while end < len(lines) and lines[end].startswith("|"):
                end += 1
            return lines, index, end
    raise WorkflowError(f"missing Markdown table: {header_first_cell}")


def registrations(bindings_text: str) -> dict[str, dict[str, str]]:
    lines, start, end = find_table(bindings_text, "Participant ID")
    entries = {}
    for line in lines[start + 2 : end]:
        cells = split_table_row(line)
        if len(cells) >= 6:
            entries[cells[0]] = {
                "tool": cells[1],
                "role": cells[2].lower(),
                "profile": cells[3],
                "status": cells[4].lower(),
            }
    return entries


def default_binding(bindings_text: str, role: str) -> str | None:
    lines, start, end = find_table(bindings_text, "Role")
    label = ROLE_LABELS[role]
    for line in lines[start + 2 : end]:
        cells = split_table_row(line)
        if len(cells) >= 2 and cells[0] == label:
            return None if cells[1] in {"未设置", "Not set", "null"} else cells[1]
    raise WorkflowError(f"missing project default row for {label}")


def set_default_binding(bindings_text: str, role: str, participant: str) -> str:
    lines, start, end = find_table(bindings_text, "Role")
    label = ROLE_LABELS[role]
    for index in range(start + 2, end):
        cells = split_table_row(lines[index])
        if len(cells) >= 2 and cells[0] == label:
            cells[1] = participant
            lines[index] = join_table_row(cells)
            return "\n".join(lines) + ("\n" if bindings_text.endswith("\n") else "")
    raise WorkflowError(f"missing project default row for {label}")


def set_registration_status(bindings_text: str, participant: str, status: str) -> str:
    lines, start, end = find_table(bindings_text, "Participant ID")
    for index in range(start + 2, end):
        cells = split_table_row(lines[index])
        if len(cells) >= 6 and cells[0] == participant:
            cells[4] = status
            lines[index] = join_table_row(cells)
            return "\n".join(lines) + ("\n" if bindings_text.endswith("\n") else "")
    raise WorkflowError(f"participant is not registered: {participant}")


def append_binding_history(
    text: str, transaction_id: str, role: str, old: str | None, new: str, reason: str, authorization: str
) -> str:
    heading = "## Default Binding History"
    header = (
        "| Transaction | Time | Role | From | To | Reason | Authorization |\n"
        "|---|---|---|---|---|---|---|"
    )
    row = join_table_row(
        [transaction_id, now_iso(), ROLE_LABELS[role], old or "null", new, reason, authorization]
    )
    if heading not in text:
        return text.rstrip() + f"\n\n{heading}\n\n{header}\n{row}\n"
    before, after = text.split(heading, 1)
    if "| Transaction |" not in after:
        after = f"\n\n{header}\n{row}\n"
    else:
        after_lines = after.splitlines()
        insert_at = next(
            (i for i, line in enumerate(after_lines) if line.startswith("|---")), None
        )
        if insert_at is None:
            raise WorkflowError("invalid Default Binding History table")
        after_lines.insert(insert_at + 1, row)
        after = "\n".join(after_lines) + ("\n" if text.endswith("\n") else "")
    return before + heading + after


def active_task_context(repo: Path) -> tuple[Path, str, dict, Path, str, dict]:
    project_path = repo / "docs/agent/PROJECT_STATUS.md"
    if not project_path.is_file():
        raise WorkflowError(f"repository is not initialized: {project_path} is missing")
    project_text = project_path.read_text(encoding="utf-8")
    project = parse_simple_yaml(project_text)
    task = project.get("active_task")
    if not task:
        raise WorkflowError("PROJECT_STATUS.active_task is null")
    state_path = repo / "docs/agent/tasks" / str(task) / "STATE.md"
    if not state_path.is_file():
        raise WorkflowError(f"active task STATE is missing: {state_path}")
    state_text = state_path.read_text(encoding="utf-8")
    state = parse_simple_yaml(state_text)
    return project_path, project_text, project, state_path, state_text, state


def next_progress_path(state_path: Path, tool: str) -> Path:
    progress_dir = state_path.parent / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)
    numbers = []
    for path in progress_dir.glob("[0-9][0-9][0-9]-*.md"):
        try:
            numbers.append(int(path.name[:3]))
        except ValueError:
            pass
    number = max(numbers, default=0) + 1
    return progress_dir / f"{number:03d}-agent-replacement-{tool}.md"


def management_record(
    *,
    language: str,
    task: str,
    role: str,
    old: str,
    new: str,
    tool: str,
    scope: str,
    transaction_id: str,
    input_revision: int,
    output_revision: int,
    stage_round: int,
    next_role: str,
    next_participant: str,
    expected_output: str | None,
    replacement_is_current: bool,
    reason: str,
    authorization: str,
    old_writer: str | None,
) -> str:
    if language == "zh-CN":
        actions = "经授权将角色参与者更换，并保留旧身份及历史记录。"
        conclusions = (
            "更换完成；新参与者需另行执行“继续”后才能开始业务写入。"
            if replacement_is_current
            else "更换完成；当前责任参与者保持不变，新绑定在该角色下一次轮到时生效。"
        )
        unresolved = "无；如存在未知副作用，新参与者必须先只读核对。"
    else:
        actions = "Reassigned the role under explicit authorization while preserving the prior identity and history."
        conclusions = (
            "Replacement completed; the new participant must run `continue` before business writes."
            if replacement_is_current
            else "Replacement completed; the current owner is unchanged and the new binding applies when that role is next scheduled."
        )
        unresolved = "None; any unknown side effects must be checked read-only before work resumes."
    return f"""# Agent Replacement

```yaml
task: {task}
kind: MANAGEMENT
role: {role}
participant_id: {new}
tool: {tool}
writer_session: null
stage_round: {stage_round}
input_revision: {input_revision}
output_revision: {output_revision}
transaction_id: {transaction_id}
scope: {scope}
started_at: {now_iso()}
finished_at: {now_iso()}
```

## Inputs Read
- `STATE.md` revision {input_revision}
- `role-bindings.md`

## Actions
- {actions}
- From: `{old}`
- To: `{new}`
- Previous writer session: `{old_writer or 'null'}`
- Reason: {reason}
- Authorization: {authorization}

## Conclusions
- {conclusions}

## Evidence
- Transaction: `{transaction_id}`
- Input revision: `{input_revision}`
- Output revision: `{output_revision}`

## Unresolved
- {unresolved}

## Handoff
- Next role: {next_role}
- Next participant: {next_participant}
- Expected output: {expected_output or 'null'}
- Focus: restore context, inspect the prior participant's evidence, then continue
"""


def update_project_cache(text: str, task: str, revision: int, participant: str | None) -> str:
    lines, start, end = find_table(text, "Task")
    for index in range(start + 2, end):
        cells = split_table_row(lines[index])
        if len(cells) >= 7 and cells[0] == task:
            cells[3] = str(revision)
            if participant is not None:
                cells[5] = participant
            lines[index] = join_table_row(cells)
            updated = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
            return set_scalar(updated, "updated_at", now_iso())
    raise WorkflowError(f"active task is missing from PROJECT_STATUS table: {task}")


def profile_status_update(repo: Path, profile: str, status: str) -> tuple[Path, str] | None:
    path = repo / "docs/agent" / profile
    if not path.is_file():
        return None
    return path, set_scalar(path.read_text(encoding="utf-8"), "status", status)


def participant_referenced(repo: Path, participant: str, bindings_text: str, state_override: tuple[Path, str] | None) -> bool:
    for role in ROLE_KEYS:
        if default_binding(bindings_text, role) == participant:
            return True
    for state_path in (repo / "docs/agent/tasks").glob("*/STATE.md"):
        text = state_override[1] if state_override and state_path == state_override[0] else state_path.read_text(encoding="utf-8")
        data = parse_simple_yaml(text)
        if data.get("status") in {"DONE", "CANCELLED"}:
            continue
        if participant in (data.get("assignments") or {}).values():
            return True
    return False


def command_status(repo: Path) -> dict:
    project_path = repo / "docs/agent/PROJECT_STATUS.md"
    if not project_path.is_file():
        raise WorkflowError(f"repository is not initialized: {project_path} is missing")
    project = parse_simple_yaml(project_path.read_text(encoding="utf-8"))
    payload = {
        "repo": str(repo),
        "active_task": project.get("active_task"),
        "lock_present": bool(existing_locks(repo)),
    }
    if project.get("active_task"):
        _, _, _, _, _, state = active_task_context(repo)
        payload.update(
            {
                "status": state.get("status"),
                "revision": state.get("revision"),
                "stage_round": state.get("stage_round"),
                "current_role": state.get("current_role"),
                "current_participant": state.get("current_participant"),
                "writer_session": state.get("writer_session"),
                "execution": state.get("execution"),
            }
        )
    return payload


def replace_agent(repo: Path, args: argparse.Namespace) -> dict:
    if args.role not in ROLE_KEYS:
        raise WorkflowError(f"unsupported role: {args.role}")
    if args.scope not in SCOPES:
        raise WorkflowError(f"unsupported scope: {args.scope}")
    bindings_path = repo / "docs/agent/role-bindings.md"
    if not bindings_path.is_file():
        raise WorkflowError(f"missing role bindings: {bindings_path}")

    with state_lock(repo, "replace-agent") as transaction:
        bindings_text = bindings_path.read_text(encoding="utf-8")
        entries = registrations(bindings_text)
        target = entries.get(args.to_participant)
        if not target:
            raise WorkflowError(f"participant is not registered: {args.to_participant}")
        if target["role"] != args.role:
            raise WorkflowError(
                f"target participant role mismatch: expected {args.role}, found {target['role']}"
            )
        if target["status"] not in {"active", "standby"}:
            raise WorkflowError(f"target participant is not reusable: status={target['status']}")
        if args.from_participant == args.to_participant:
            raise WorkflowError("replacement source and target are identical")

        affects_task = args.scope in {"current-task", "both"}
        affects_default = args.scope in {"project-default", "both"}
        state_override = None
        progress_path = None
        output_revision = None
        old_writer = None
        project_update = None

        if affects_task:
            project_path, project_text, project, state_path, state_text, state = active_task_context(repo)
            revision = state.get("revision")
            if args.expected_revision is None:
                raise WorkflowError("--expected-revision is required for the current task")
            if revision != args.expected_revision:
                raise WorkflowError(
                    f"revision mismatch: expected {args.expected_revision}, actual {revision}"
                )
            if state.get("status") in {"DONE", "CANCELLED"}:
                raise WorkflowError("cannot replace an assignment in a terminal task")
            assignments = state.get("assignments") or {}
            if assignments.get(args.role) != args.from_participant:
                raise WorkflowError(
                    f"task assignment mismatch: expected {args.from_participant}, actual {assignments.get(args.role)}"
                )
            old_writer = state.get("writer_session")
            if old_writer and not args.confirm_writer_stopped:
                raise WorkflowError(
                    "writer_session is still running; confirm it stopped and pass --confirm-writer-stopped with authorization"
                )

            output_revision = revision + 1
            progress_path = next_progress_path(state_path, target["tool"])
            progress_ref = f"progress/{progress_path.name}"
            new_state = set_nested(state_text, "assignments", args.role, args.to_participant)
            new_state = set_nested(
                new_state,
                "assignment_change_refs",
                args.role,
                progress_ref,
                after="assignments",
            )
            new_state = set_scalar(new_state, "revision", output_revision)
            new_state = set_scalar(new_state, "updated_at", now_iso())
            if state.get("current_role") == args.role:
                new_state = set_scalar(new_state, "stage_round", int(state.get("stage_round")) + 1)
                new_state = set_scalar(new_state, "previous_role", args.role)
                new_state = set_scalar(new_state, "previous_participant", args.from_participant)
                new_state = set_scalar(new_state, "previous_progress", progress_ref)
                new_state = set_scalar(new_state, "current_participant", args.to_participant)
                new_state = set_scalar(new_state, "writer_session", None)
                new_state = set_scalar(new_state, "latest_checkpoint", None)
                execution = "paused" if state.get("status") == "BLOCKED" else "idle"
                new_state = set_scalar(new_state, "execution", execution)
            if args.role == "implementer":
                new_state = set_scalar(new_state, "subagent_policy", "UNSELECTED")
                new_state = set_scalar(new_state, "subagent_decision_ref", None)
            state_override = (state_path, new_state)
            project_update = (
                project_path,
                update_project_cache(
                    project_text,
                    str(project["active_task"]),
                    output_revision,
                    args.to_participant if state.get("current_role") == args.role else None,
                ),
            )

        if affects_default:
            actual_default = default_binding(bindings_text, args.role)
            if actual_default != args.from_participant:
                raise WorkflowError(
                    f"project default mismatch: expected {args.from_participant}, actual {actual_default}"
                )
            bindings_text = set_default_binding(bindings_text, args.role, args.to_participant)
            bindings_text = append_binding_history(
                bindings_text,
                transaction["transaction_id"],
                args.role,
                args.from_participant,
                args.to_participant,
                args.reason,
                args.authorization,
            )

        bindings_text = set_registration_status(bindings_text, args.to_participant, "active")
        if not participant_referenced(repo, args.from_participant, bindings_text, state_override):
            bindings_text = set_registration_status(bindings_text, args.from_participant, "standby")

        profile_updates = []
        refreshed_entries = registrations(bindings_text)
        for participant in {args.from_participant, args.to_participant}:
            entry = refreshed_entries.get(participant)
            if entry:
                update = profile_status_update(repo, entry["profile"], entry["status"])
                if update:
                    profile_updates.append(update)

        if affects_task:
            assert state_override and progress_path and output_revision is not None
            final_state = parse_simple_yaml(state_override[1])
            language = str(final_state.get("language") or "en-US")
            record = management_record(
                language=language,
                task=str(final_state.get("task")),
                role=args.role,
                old=args.from_participant,
                new=args.to_participant,
                tool=target["tool"],
                scope=args.scope,
                transaction_id=transaction["transaction_id"],
                input_revision=args.expected_revision,
                output_revision=output_revision,
                stage_round=int(final_state.get("stage_round")),
                next_role=str(final_state.get("current_role")),
                next_participant=str(final_state.get("current_participant")),
                expected_output=final_state.get("next_expected_output"),
                replacement_is_current=final_state.get("current_participant")
                == args.to_participant,
                reason=args.reason,
                authorization=args.authorization,
                old_writer=old_writer,
            )
            atomic_write(progress_path, record)
            atomic_write(state_override[0], state_override[1])
        atomic_write(bindings_path, bindings_text)
        for path, content in profile_updates:
            atomic_write(path, content)
        if project_update:
            atomic_write(project_update[0], project_update[1])

        return {
            "transaction_id": transaction["transaction_id"],
            "role": args.role,
            "scope": args.scope,
            "from": args.from_participant,
            "to": args.to_participant,
            "output_revision": output_revision,
            "progress": str(progress_path.relative_to(repo)) if progress_path else None,
            "next_command": "$agent-relay continue",
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="initialized repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="read authoritative workflow state")

    replace = subparsers.add_parser("replace-agent", help="safely replace a role participant")
    replace.add_argument("--role", required=True, choices=sorted(ROLE_KEYS))
    replace.add_argument("--from", dest="from_participant", required=True)
    replace.add_argument("--to", dest="to_participant", required=True)
    replace.add_argument("--scope", required=True, choices=sorted(SCOPES))
    replace.add_argument("--expected-revision", type=int)
    replace.add_argument("--reason", required=True)
    replace.add_argument("--authorization", required=True)
    replace.add_argument("--confirm-writer-stopped", action="store_true")

    release = subparsers.add_parser(
        "release-stale-lock", help="remove a lock only after authorized stop confirmation"
    )
    release.add_argument("--authorization")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    try:
        if args.command == "status":
            result = command_status(repo)
        elif args.command == "replace-agent":
            result = replace_agent(repo, args)
        elif args.command == "release-stale-lock":
            if not args.authorization:
                raise WorkflowError("explicit --authorization is required to release a stale lock")
            locked = existing_locks(repo)
            if not locked:
                raise WorkflowError(f"no lock exists: {lock_path(repo)}")
            if len(locked) > 1:
                raise WorkflowError(
                    "both legacy and canonical locks exist; inspect and resolve the conflict manually"
                )
            path = locked[0]
            previous = path.read_text(encoding="utf-8")
            path.unlink()
            result = {
                "released": str(path),
                "authorization": args.authorization,
                "previous_lock": json.loads(previous),
            }
        else:
            parser.error("unknown command")
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except WorkflowError as error:
        print(f"workflow-state error: {error}", file=sys.stderr)
        return error.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
