---
name: source-html-to-app-ui
description: Rebuild an approved source HTML application as a real, high-fidelity UI in the target repository. Use for source-to-app design tasks requiring interactive source discovery, authored routes and components, local UI behavior, responsive/theme adaptation, and paired Playwright evidence.
---

# Source HTML To App UI

## 1. Outcome And Boundaries

<task_contract>

Rebuild the approved HTML as a normal, high-fidelity application with real routes, components, styles, assets, and local UI state. Preserve source content, hierarchy, layout, styling, controls, meaningful states, and behavior. Cover every page, readable section, interaction family, represented theme, and applicable desktop/mobile/responsive/scroll/drawer condition.

**IMPORTANT — Immutable reference:** never edit the approved HTML/design JSON or mutate source DOM, CSS, or scripts to make a capture or runtime pass. Note source errors and unavailable states without filtering them; use their declarations for intended target behavior. Do not debug source exceptions, trace handler registration, make diagnostic source packets, or retry a no-op. Capture reachable source views; unavailable ones need complete target visual and real-input proof, not fabricated source screenshots. Target errors remain failures.

**IMPORTANT — UI-only scope:** do not add backend, API, database, persistence, authentication, server, or business logic. Do not embed the source runtime, wrap it in a gallery, invent navigation destinations, or weaken checks. Use the real repository logo when available; disable unsupported destinations.

**IMPORTANT — Phase 0 write boundary:** before its passing decision and transition to Phase 1, keep target implementation, assets, packages/configuration, tests, and generated/build files unchanged. Only the workflow directory may be written. Target-owner research and asset downloads belong to Phase 1; pre-gate downloads may write only source assets inside the workflow. Revert only premature target writes and finish missing source proof—do not discard valid discovery.

Every browser/server/runtime check, including exploratory measurements and diagnostics, uses the unchanged lifecycle helper. Its reference owns the command and safety rules; a green build, path, summary, or earlier `Pass` label is not browser proof.

</task_contract>

## 2. Work Promptly Without Repeating Proof

<delivery_contract>

This is time-bounded delivery, not an exhaustive research exercise. Spend time implementing and fixing actual defects. A run that finds no new defect, repair, or missing proof is not progress.

- **Phases 2–3:** aim for about **15 minutes per phase** as a soft planning guide, never a hard limit or automatic stop. Complete required proof or real repairs that need longer; do not add confidence-only checks or paperwork.
- **Phase 1:** build the design system first, then reusable UI components, shell, and full pages. Work concurrently within each dependency-ready stage; do not preempt visual-comparison phases with control-by-control checks.
- **Source capture belongs to Phase 0.** Establish readable reference images and reusable browser/capture properties there, including materially distinct responsive layouts. Phase 1 implements from that plan; Phases 2–3 reuse it for corresponding target views, not a newly invented capture scheme. Repair a genuinely missing/invalid source item in its owning phase without resetting the task or recapturing the inventory.
- Use judgment to find material differences or missing requirements. Several small deviations caused by one wrong shared rule are material; an isolated harmless pixel/line-wrap variance is not another tuning round.
- Reuse current instructions, code reviews, builds, screenshots, and findings. Refresh only proof affected by a relevant change or contradicted by actual results.

There is no fixed screenshot cap. Scope proof to the actual UI, not every transition, field-value permutation, DOM element, or route × state × viewport matrix. Every required distinct appearance and interaction family still needs its proper evidence.

Recharts is optional. After a successful build, record and accept an oversized lazy-loaded Recharts chart-chunk warning and continue. This exception permits no other warnings/errors and does not weaken warning limits.

</delivery_contract>

## 3. Locate Instructions And Restore Context

<instruction_loading>

Load this skill before work and the relevant reference before its workstream. References are required instructions, not optional expansion material. During uninterrupted work, reuse loaded instructions; a phase transition or failed capture is not a reason to reread them. Phases 2–3 share one reference.

| Workstream | Required reference |
| --- | --- |
| Fresh task, source discovery, or missing source proof | [Phase 0](references/phase-0-source-contract.md) |
| Target implementation | [Phase 1](references/phase-1-ui-implementation.md) |
| Broad comparison and focused signoff | [Phases 2–3](references/phase-2-3-playwright-fidelity.md) |
| Final audit and completion | [Phase 4](references/phase-4-final-audit-completion.md) |
| Any browser/server work, including a Phase 1 probe | [Managed lifecycle](references/playwright-lifecycle.md) |

### After Interruption Or Context Loss

Reload after compaction, resume, retry, reconnect, or a new session:

1. This skill, the compact checkpoint, current marker, and open gaps.
2. The current or earliest failing phase artifact and its required reference; load lifecycle instructions for browser work.
3. Only binding/relevant task inputs, HTML/design excerpts, target files, and evidence linked to the next action.

Preserve this task's work. Use actual durable evidence, not conversation memory or an old passing label. The HTML remains available for targeted inspection; do not copy it into a recovery ledger or reread it end to end by default.

</instruction_loading>

## 4. Workspace And Evidence Homes

<workspace_contract>

### Paths And Fresh Setup

All runtime paths below are relative to **`task-workflow/`** in the target repository. Instruction references and supplied assets are relative to this skill folder.

For a **fresh task only**, remove previous-task workflow state and create:

- `CURRENT_PHASE.txt`, `progress.md`, `open-gaps.md`, and `spec.json`.
- The five phase artifacts listed in the phase map, copied from matching filenames in `assets/templates/`.
- `source-playwright/` and `source/`; `target-playwright/` and `verification/`.
- `runtime/source/`, `runtime/target/`, and `scripts/`.

Copy the checkpoint/gap templates from the same template folder, the approved design JSON byte-for-byte to `spec.json`, and `assets/scripts/playwright-lifecycle.mjs` byte-for-byte to `scripts/playwright-lifecycle.mjs`. Keep generated evidence and notes inside this workspace. A manifest is optional, not a gate requirement.

Preserve the templates' scores, critical requirements, evidence meanings, and decision-before-transition/completion rules. Wording may be shortened without losing an explicit, scorable requirement. Do not add promotion permission tables.

### One Home Per Fact

| Owner | Record once |
| --- | --- |
| Source evidence index | Accepted Phase 0 image paths, compact capture-plan/shared-packet pointer, coverage pointers, and concrete per-image findings |
| Comparison index | Area pass/fail, accepted source/target paths, actual mismatch and brief fix/recheck |
| Phase artifact | Scores, critical outcomes, decision, and pointers to existing proof |
| Open gaps | Only observed unresolved defects/contradictions; evidence pointer, owner, next repair |
| Checkpoint | Current phase, last completed work/evidence pointer, essential constraint/blocker, next action |
| Marker | Current phase only |
| Inputs, code/diff, PNGs, packets, logs | Their original content, values, dimensions, state, command history, and provenance |

Do not duplicate findings, source values, file inventories, command output, metadata, or histories across owners. Planned unattempted work is a next action, not an open failure. Close a gap after replacement proof; retain failure history in its log/finding.

### Update And Freshness Rules

- Update the checkpoint when phase/next action changes, a blocker prevents progress, or work is about to stop—not after each tool call or packet. Keep it sufficient to resume without duplicating work.
- Successful writes need no routine readback. For a failed/uncertain write, read only affected text, repair it, and confirm success. Do not repeatedly guess stale patch lines.
- Reconcile stale notes in place. Record maintenance does not invalidate screenshots, require a build, change a score, or replay a phase.
- Build/check evidence stays current until relevant target code, asset, dependency, or configuration changes. Workflow-note changes do not invalidate it. Browser replacement proof must use the updated served bundle.
- Accepted images/findings remain current until their UI changes or contradictory/missing evidence is found. Keep valid partial results from failed packets; refresh only invalid proof with new paths.

</workspace_contract>

## 5. Five-Phase Protocol

<phase_protocol>

The artifact filename without `.md` is the marker value. Scores below are passing thresholds; each critical requirement must also independently pass.

| Phase | Artifact | Purpose | Gate |
| --- | --- | --- | --- |
| 0 | `phase-0-source-contract.md` | Discover declarations, capture/review source UI, hand off adaptations and intended interactions | `48/50` |
| 1 | `phase-1-ui-implementation.md` | Research target owners; design system → reusable UI → shell → complete pages/local behavior | `48/50` |
| 2 | `phase-2-paired-responsive-proof.md` | Broad source-target page/section layout, shared styling, desktop/mobile parity; fix material broad failures | `48/50` |
| 3 | `phase-3-fidelity-repair-signoff.md` | Judgment-led missing/fine-detail repair; remaining interaction, state, responsive, scroll/drawer/theme proof | Overall `49/50`; desktop/mobile `48/50` each |
| 4 | `phase-4-final-audit-completion.md` | Audit skipped/invalidated requirements, final diff, evidence and completion safety—not a new polish pass | Exactly `50/50` |

### Work And Gate Loop

1. Set the marker at a real transition; use the instructions already loaded or load the newly relevant reference.
2. Work in cohesive implementation/evidence groups, batching independent dependency-ready work. No fixed sequence of individual tool calls is required.
3. Review changed code/focused diffs and newly accepted browser images at readable scale. Record source findings per image in Phase 0, and an immediate area pass/fail at first paired comparison. Collect independent findings, batch related repairs, then recheck affected areas; a mismatch blocks only proof that depends on it, not unrelated comparisons. Phase 2 owns broad failures; record fine-detail findings for Phase 3 without repairing them to unlock Phase 2. Reuse passing areas and group browser work as described in the shared reference.
4. At the gate, score each weighted row and evaluate every critical requirement from current evidence once. Record a passing decision before advancing; on failure, repair its owning work and refresh only affected proof.
5. Continue automatically through Phase 4 while locally unblocked. A phase pass is not task completion. Stop only at the user's request or a proven external blocker with no local recovery; record that blocker and next action.

A routine visual/code correction stays in Phase 2 or 3; refresh affected earlier code/check claims without replaying Phase 1. Missing source proof returns only to its Phase 0 item. Procedural mistakes do not erase valid work, but missing required proof cannot pass.

### Scoring Discipline

- Keep all weighted rubrics and thresholds. Passing with all critical requirements met is sufficient; do not pursue `50/50` in visual phases through harmless adjustments.
- If a subjective deduction is demonstrably too severe, re-review actual evidence and adjust that phase by **at most two points total for the current evidence**. Record original/revised category scores and the concrete reason; do not accumulate adjustments or award points just for being near a threshold.
- Missing evidence, objective failures, broken interactions, and build/check failures cannot be offset. Phase 4 may correct an evidenced scoring mistake, but its audit score is not a discretionary bonus.
- The Agent owns review, scores and decisions. Scripts collect evidence only; do not create scoring, phase-check, closeout, receipt, forced-read, packet-permit, or promotion scripts.

</phase_protocol>

## 6. Completion

<completion_contract>

Use the Phase 4 audit once; its checklist owns the detailed completion checks. Confirm:

- [ ] The marker is Phase 4; every phase decision passes its threshold and independent critical requirements with current concrete evidence.
- [ ] Required reachable source-target comparisons and source-unavailable declaration-to-target proof exist and were opened; final visual/interaction/responsive/scroll/drawer/theme evidence represents final code.
- [ ] No unresolved gap or skipped work remains; the final diff is source-backed and UI-only, and required checks/build are current.
- [ ] The exact command from the task instructions is copied, confirmed unrun, and is the next action only after the audit passes.

Run that supplied command, for example:

```bash
node /workspace/builder/task_complete.mjs --projectId "<projectId>" --taskId "<taskId>" --status completed --summary "<brief summary>"
```

Do not invent identifiers or report completion until its successful result. It need not be the literal final tool call.

</completion_contract>
