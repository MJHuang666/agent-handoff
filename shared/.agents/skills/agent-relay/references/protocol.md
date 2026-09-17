# Agent Relay Protocol

Read this reference before any task or project-state write. The installed repository's `docs/agent/workflow.md`, roles, conventions, and task files contain the project-specific facts; this reference defines how to use them.

## Identity

The project language is read from `PROJECT_STATUS.md`. Use it for all user-facing communication and new task prose. Do not translate stable YAML keys, status enum values, file names, participant IDs, or delivery IDs.

Identity is `(participant_id, tool, role)`. `participant_id` is unique; tool and role are immutable. If the current tool matches more than one active identity, present the matching participant IDs and roles and ask the user to select one. The current STATE does not resolve that ambiguity because doing so would let a session claim whichever role is needed.

Identity status is `active`, `standby`, or `retired`. Active and standby identities may be selected for an authorized replacement; selecting a standby identity reactivates it. Retired identities require an explicit reactivation decision. Never delete or repurpose an identity referenced by history.

If no identity exists, registration is a management operation: ask for the role and tool, choose a unique participant_id, create the Profile from the project template, and register it. Do not register a new identity merely to bypass a wait state.

## Eligibility to Write

Business writes require all of these:

1. The task equals `PROJECT_STATUS.active_task`.
2. This session has a confirmed participant_id.
3. STATE current_participant and current_role match the participant and its immutable registration.
4. The assignment snapshot maps that role to the participant.
5. execution is idle, or this exact session already owns a running writer_session.
6. The workdir, branch, baseline, dirty files, delivery evidence, and relevant prior outputs have been checked.

An Implementer must also have an explicit `STATE.md` `subagent_policy` of `USE` or `DO_NOT_USE` before changing product code. `UNSELECTED` is a hard wait state. Record the user's choice in `subagent_decision_ref` and use subagents only when the policy is `USE` and the tool supports them.

Before starting from idle, record a traceable writer_session, set execution to running, and increment revision. A session ID tracks ownership but does not prevent races; keep one human-coordinated writer.

When the bundled helper is available, use it for participant replacement and revision-sensitive coordination writes. Its short-lived local lock, expected-revision check, and atomic replacement reduce accidental races; they do not lock product files or coordinate different machines/checkouts.

## Wait and Takeover

If any eligibility check fails, remain read-only. Report task, status, current role, participant, tool, writer_session state, and the latest handoff file.

Do not replace a running writer_session based on age, silence, urgency, an obvious fix, or the user's dislike of repeated questions. First use available read-only evidence to confirm the original session stopped. If it cannot be confirmed, ask one focused question. Takeover also requires explicit user authorization, then record a management/repair event, preserve existing changes, assign a new session ID, and increment revision. Never reset or overwrite the old work automatically.

## Role Work

- Planner reads requirements and real project facts, writes requirement/plan/decisions, and records genuine approval. Planner does not modify product code.
- Implementer reads the approved plan, modifies code and tests, writes execution and delivery evidence, and handles rework. Implementer does not close review issues.
- Reviewer independently checks the actual delivery, writes review, verifies fixes, and decides CHANGES_REQUESTED, PLANNING, BLOCKED, VERIFYING, or DONE. Reviewer does not fix product code or accept risk without the authorized reference.

## Delivery Evidence

Committed work uses a full commit ID. Uncommitted work uses a unique delivery_id plus the baseline, changed/deleted/untracked paths, and either SHA-256 content fingerprints or a complete diff snapshot that includes new-file content. Record test commands, results, environment, time, and delivery_id.

Changing only coordination records does not automatically invalidate product tests. Product code, tests, dependencies, build configuration, runtime environment, behavior constraints, or acceptance semantics require an explicit impact assessment and repeated checks where affected.

## Pause and Recovery

A checkpoint belongs to one task, stage_round, role, and participant. Record finished work, unfinished work, changed files, tests, running processes, side effects, and the next safe read-only check. Pausing sets execution=paused and clears writer_session without changing stage_round.

On recovery, compare the checkpoint with disk changes and live processes. Treat uncertain side effects as UNKNOWN and check read-only before repeating them. A checkpoint from another stage round or participant is history, not an instruction.

## Handoff

1. Finish the role deliverable and version evidence.
2. Append a progress record with inputs, actions, conclusions, evidence, unresolved items, and intended next participant.
3. Verify every reference and next participant. Update STATE, increment revision and stage_round, switch stage/participant, point to the new progress record, clear latest_checkpoint and writer_session, and set execution=idle. This STATE write makes the handoff effective.
4. Refresh only the current task cache in PROJECT_STATUS if STATE still has the revision just written.

Files are not transactional. Before the STATE update, the prior participant still owns recovery. After it, the new participant owns normal cache repair. Missing or contradictory references require an explicitly authorized repair session.

## Exceptional States

- CHANGES_REQUESTED returns to Implementer and retains stable review issue IDs.
- A scope or design change returns to Planner and creates a new plan version.
- BLOCKED uses execution=paused, writer_session=null, and records blocked_reason, unblock_condition, resume_status, and responsible participant.
- DONE/CANCELLED use execution=idle and clear current_role, current_participant, writer_session, next_expected_output, latest_checkpoint, and active blocking fields.
- The session entering a terminal state clears active_task only if it still points to that task. It does not choose the next task.

DONE means task acceptance only. It does not authorize merge, release, deployment, deletion, or rollback.

## Repair and Management

Registration, participant replacement, active-task switching, takeover, and state repair are management operations. Perform them only when explicitly requested or necessary to carry out an already explicit request, record the reason and evidence, and do not mix them with product edits.

For participant replacement, choose `current-task`, `project-default`, or `both`. Keep the role fixed and create or reuse a same-role identity. A current responsible participant change increments revision and stage_round, clears writer/checkpoint ownership, and appends a MANAGEMENT record; a non-current task assignment change increments revision only. Implementer replacement resets the subagent decision. Repeated A → B → A changes reuse the immutable identities and create distinct management records.

Do not auto-release a state-helper lock. Confirm the recorded process/session stopped and obtain explicit user authorization. If the helper reports a revision mismatch, discard the stale proposal, re-read all current state, and start a new management transaction.

Waiting participants only report inconsistencies. A prior participant that already handed off may repair missing history only after repair authorization; old role ownership is not continuing write authority.
