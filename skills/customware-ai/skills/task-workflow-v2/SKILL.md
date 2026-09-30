---
name: task-workflow
description: Canonical workflow for a task. Read and follow strictly end to end while working on the task.
---

# Task Workflow

## Instruction And Phase Contract

Execute all eight phases in dependency order and satisfy every required quality gate. The phase outcomes, safety boundaries, numeric thresholds, and critical requirements are mandatory. Within a phase, choose efficient tool order and batch independent work; exact tool-call order and repeated paperwork are not quality requirements.

Before implementation, reset only the previous task's `task-workflow/` artifacts, scaffold the new task, complete research, and pass Phases 0–1. On resume of the same task, preserve its artifacts and follow the resume procedure instead of resetting them. Before Phase 0 artifacts exist, identify the repo, read this skill and task, and scaffold; do not inspect or edit implementation files. Do not edit or generate source, tests, package files, build outputs, databases, route types, or migrations before Phase 1 passes. Set the marker to `phase-2-execution` before implementation edits.

Production/live databases are user data, not verification fixtures. The only permitted live-DB action is the repo's required migration command for a real schema change, recorded in its owning phase. No manual query, seed, reset, fixture, direct SQLite, data repair, cleanup, delete, truncate, or debug mutation is allowed. Use isolated repo-owned test/E2E configuration for verification.

Complete through Phase 7 unless the user stops the run or a demonstrated external blocker prevents local progress. Never claim an unperformed check or partial task as complete.

## Core Idea

Implement the actual task, then prove it through second-pass integrity/check/build review, a unit-coverage decision, real browser verification, an E2E-coverage decision, and final audit. Builds, tests, screenshots, and interaction checks prove different claims; none replaces another.

This is time-bounded delivery: spend time implementing and finding/fixing real defects, not maintaining a second description of the repository. Keep enough durable evidence to resume after interruption or compaction without duplicating work. Read-only input files, source/diffs, accepted screenshots, and command logs remain the authorities for facts already available there.

## Repository Adaptation

Use this workflow for both new and existing projects. Discover the actual repository structure, applicable instructions, commands, contracts, compilation/runtime boundaries and connected tests before choosing changes. Reuse its established conventions; do not impose another template's layout, relocate code or redesign a working build merely to match an example. The paths identifying this skill's inputs, references and workflow artifacts are workflow interfaces, not directions for organizing application code.

When changing a contract or state rule, update every affected producer and consumer together. Establish one consistent implementation and prove its connected behavior. Retain a concise explanation of a non-obvious constraint or rejected approach; do not reintroduce an approach already disproved unless new evidence changes that conclusion. Do not repeatedly reinterpret accepted design decisions after checks pass without a concrete defect.

## Evidence And Resume Contract

Each fact has one home:

- Phase artifacts own their plan, findings, scores and evidence pointers. Each required check has one authoritative result entry in its owning phase: command/scope, pass/fail with exact useful output or a durable log pointer, and the relevant implementation/setup state it verified. Update that entry for an affected rerun, retaining useful failure evidence without accumulating another recap. Other phases, gaps and checkpoints cite the entry; never copy test counts, durations, PIDs or command results into additional summaries.
- `progress.md` owns only the current phase/artifact/reference, last passed gate, active work/next action, essential constraints, and a pointer to Phase 1's input manifest. Do not mirror file inventories, comparison tables, command logs, scores, or full phase histories there.
- `CURRENT_PHASE.txt` is a resume pointer, not an additional proof ledger. Write it at actual phase transitions; do not reread it before/after each tool call during uninterrupted work.
- `open-gaps.md` owns real unresolved gaps and a short resolution with an evidence pointer. Do not duplicate the gap's full explanation in every phase. Update the same gap once rather than creating new rows for retries.

Work in cohesive batches. At completion of a meaningful batch, record changed areas, concrete proof, remaining work, and the next action together. Flush the compact checkpoint at batch boundaries, before a long-running command or interruption, on blockers, and at transitions. Do not update it after every read, search, tiny edit, or successful command. A known defect/blocker must be recorded promptly so compaction cannot lose it. Do not wait until the entire implementation is finished to write its evidence.

Trust a successful edit tool's result and shown diff for routine workflow-record updates. Inspect a cohesive implementation diff once before relying on that batch for a gate; do not separately reread every file after each small patch. Failed, partial, missing, or uncertain writes require a targeted read of the affected region, repair, and confirmation. Keep records short and stable so updating a result does not require rewriting several tables. After a failed patch, inspect the current affected region once and repair only changes that have not already landed. Build the next patch from that exact content, not remembered lines; split independent repairs when one stale anchor would block them all. Account for source-changing commands such as automatic lint fixes. Do not re-add existing declarations or edits, attribute your own changes to another writer without evidence, or retry a previously rejected anchor. Successful recovery needs no new read-permission or promotion checklist.

Load a required reference once when entering its workstream. Reuse it across connected phases and local repairs while it remains in context; reread only after compaction/context loss, actual instruction changes, or a specific unresolved instruction question. Apply rules already loaded without another reference read or a read-permission checklist.

Score once at the phase gate from current evidence, after fixes, not after each patch or record update. Record score, critical result, evidence pointers, and `Decision: Pass` together; then update marker/checkpoint and continue. Do not create a second promotion-lock table or reread all earlier artifacts on every transition. Earlier passing results remain valid until their actual inputs or claims change.

Before repeating a command, use its latest authoritative result and identify the specific relevant change **since that successful run**, or the actual missing/failed proof. A fix verified after it was made is not still awaiting verification. Keep this reason with the affected result entry; do not create a separate rerun-permission table. If no relevant change or missing proof exists, reuse the result and continue.

Distinguish record maintenance from invalidation:

- A stale pointer, future-tense historical note, missing link, or duplicated record with existing valid proof is a documentation correction. Reconcile it in the current phase, cite the authoritative result, and continue; do not reset earlier decisions, phase markers, or replay already-passed gates.
- A real missing requirement, missing/unrecoverable check result, failed check, or relevant code/config/test/fixture/build change invalidates only affected claims. Record what changed, return to the earliest owning phase needing real work, repair it, and re-pass affected checks. Advance across unaffected phases using existing evidence in one concise reconciliation; do not replay their tool calls, rescore unchanged gates, or generate new paperwork. A changed test or screenshot does not automatically invalidate unrelated implementation/build proof. Unit-test organization or cleanup affects the relevant unit proof, not unchanged interactive/E2E behavior or responsive evidence. Documentation, marker and score-row corrections do not invalidate code verification. A UI-only fix does not automatically require rerunning unrelated service tests. Real changes to shared inputs or behavior still invalidate every affected claim.
- Never turn an actual missing or failing check into a documentation-only correction. If a claimed result cannot be substantiated, perform the required check in its owning phase.

After compaction, interruption with context loss, or a new coding session: read this skill, the checkpoint and marker, current artifact, gap ledger, and current phase reference; reload binding `AGENTS.md`, task/domain, selected relevant skills, and task-relevant attachments via the Phase 1 input manifest. Use this saved evidence to avoid repeating completed work. A tool retry/reconnect with intact context does not require a full reload. Repair pointer disagreements from substantive evidence, not historical wording. Preserve accepted decisions and the latest successful results through compaction; distinguish work genuinely remaining from historical failures already repaired. A stale summary must not override current concrete proof.

## MITB Workspace Inputs

When running in a MITB sandbox, use these repo-relative workspace inputs:

- workflow skill: `.agents/skills/task-workflow/SKILL.md`
- task body: `.tasks/task.md`
- domain and brand context: `.tasks/domain.md`
- attached task files: `.tasks/files/`
- available skill files: `.agents/skills/`

`AGENTS.md` is the target repo's binding development-instructions file. It defines project-specific rules for architecture, type safety, tests, UX, commands, code style, docs, prohibited patterns, and completion. Phase 1 must extract the task-relevant rules from `AGENTS.md` before planning edits, including any required docs it points to. Later gates must verify the implementation follows those extracted rules.

Phase 1 must read `.tasks/domain.md`. It must enumerate `.tasks/files/` even when the folder is empty, then read or inspect every task attachment/supporting file in that folder before planning.

Available skills are kept under `.agents/skills/`. Discover available skills from the prompt's Skills section and `.agents/skills/`, then read only the selected skill `SKILL.md` files relevant to the current task. Do not bulk-read every skill file in `.agents/skills/`.

All Phase 1 input/reference files are read-only. This includes `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, every file under `.tasks/files/`, and every selected skill file under `.agents/skills/`. Treat files under `.tasks/` as canonical task inputs, not editable workspace artifacts. Do not rewrite, normalize, consolidate, clean up, trim, reformat, or "fix" these files unless the task explicitly asks to update that exact reference file. If a reference file appears inconsistent, record the ambiguity in `task-workflow/phase-1-task-research.md` or `task-workflow/open-gaps.md`; never resolve it by editing the reference input.

Record each attachment/supporting file inspected and selected relevant skill, with its reason, once in Phase 1’s input manifest. `progress.md` points to that manifest for resume; it does not copy it. After context loss, reload the relevant inputs as specified by the Evidence And Resume Contract.

In MITB, `.tasks/task.md` or the prompt always provides the task completion command. Phase 7 must run the exact completed command only after its pre-completion audit is Ready; completion's returned result is recorded afterward, not required before invocation. If a Phase 7 audit check fails, do not run task completion. Apply the Evidence And Resume Contract: reconcile documentation-only issues in place; repair substantive failures in their owning phase and refresh only affected evidence before re-entering Phase 7.

## Mandatory Process Shape

<mandatory_process_shape>

This workflow shape is not optional:

1. Clear old workflow artifacts for this repo and copy fresh artifact templates.
2. Read the task, root `AGENTS.md`, `.tasks/domain.md`, every task attachment/supporting file in `.tasks/files/`, only relevant available skill files from `.agents/skills/`, and relevant project docs. Extract the task-relevant development rules from `AGENTS.md` before planning. These instruction, task, domain, attachment, and skill-reference files are read-only unless the task explicitly asks to edit them.
3. Research the codebase and record the implementation plan.
4. Execute the primary implementation.
5. Execute a second gap-closure pass.
6. Run second-pass integrity review and repo check/lint validation.
7. Make the unit-test coverage decision: add, update, remove, or explicitly skip unit tests.
8. Verify interactively with standalone Playwright scripts.
9. Make the E2E coverage decision: add, update, remove, or explicitly skip E2E tests.
10. Audit each phase’s current proof once and sign off only when all gates pass.

If the work skips one of those phase boundaries, the run is off track.

### Phase Ownership Matrix

| Phase | Owns | Required evidence |
| --- | --- | --- |
| Phase 0 | artifact reset and scaffold | fresh artifacts, helper scripts, marker, no source edits |
| Phase 1 | task intake and research | task/domain/attachments/AGENTS/selected skills read, codebase research, implementation plan |
| Phase 2 | primary implementation | scoped work packets, file evidence, readback/diff/search proof |
| Phase 3 | second execution, integrity, check/lint validation | connected-surface review, repo check, focused lint when useful, build, reusable build evidence |
| Phase 4 | unit-test coverage decision | add/update/remove/skip decision, existing-test inspection, minimal unit command or `N/A` |
| Phase 5 | interactive Playwright verification | Stage 1 behavior proof, Stage 2 UI/responsive proof, screenshots, lifecycle evidence |
| Phase 6 | E2E coverage decision | add/update/remove/skip decision, connected E2E inspection, minimal E2E command or `N/A` |
| Phase 7 | final audit and signoff | artifact integrity review, current evidence, MITB completion command after audit |

</mandatory_process_shape>

## Gates And Continuation

For each phase: load its reference if not already in context, perform the work, record concise evidence, and score against its unchanged threshold and critical criteria. Repair failed requirements, rerun only affected checks, and then rescore. Do not lower thresholds, claim success from a green build alone, or stop at a narrative checkpoint when the next local action is available. User stop instructions take precedence.

At promotion, use the current gate result already established and earlier still-valid results; record the passing decision and update marker/checkpoint together. All required evidence must be concrete, not unfilled template placeholders. Use `N/A` with a reason for conditional requirements, not fabricated evidence. Do not reread unchanged phase artifacts merely to authorize the next action.

Resolve critical gaps before their owning gate passes; deferred non-critical work must have a reason/owner and be reconciled before final signoff. Update the authoritative gap row when resolved; the final audit must not accept contradictions or falsely open resolved gaps. Documentation reconciliation does not require phase replay.

## Autonomous Run Contract

<autonomous_run_contract>

Apply the Evidence And Resume Contract throughout all phases.

### Verification File Rules

- Phase 5 and Phase 6 must review the interactive scripts and E2E tests for fixed waits before passing.
- A fixed wait in interactive verification scripts or repo-discovered E2E tests is a gate failure. Do not justify it. Replace it with deterministic Playwright waits/assertions such as `locator.waitFor(...)`, `expect(locator)...`, `waitForURL(...)`, `waitForResponse(...)`, or persisted-state assertions, then rerun verification.
- Phase 5, Phase 6, and Phase 7 may pass only when their artifacts document that the inspected verification files contain no fixed waits and cite the deterministic waits/assertions used instead.
- If later work reveals missing evidence, first locate existing proof. Repair a missing record/link in place; if the check was actually missed or its result cannot be substantiated, return to its owning phase and refresh the affected gate.

### Write And Command Rules

- Inspect implementation changes as cohesive batches before gate reliance. Successful workflow-record patches need no extra readback; failed or uncertain edits need targeted inspection and repair, as defined by the Evidence And Resume Contract.
- If a write/edit tool reports an invalid write, missing file, failed patch, partial output, or uncertain result, stop that work packet, repair the write with a supported edit method, read it back, and only then continue. Do not proceed as if a failed write happened.
- Commands must be bounded. Do not leave long-lived servers, watchers, or interactive commands running in the foreground as the active tool call.
- Production/live workspace databases must never be used as test or verification state. In this skill, "production database" means any repo-declared live/default user-data database, or any database path used by the normal app outside an isolated test/E2E config. The only allowed action on any production/live database is the repo's required application migration command for a real schema change, run in the phase that owns that migration and recorded as migration evidence. This is a narrow migration-execution exception, not permission to work on the production DB. If the task creates or changes a migration, running the repo's app migration command against the production/live default DB is mandatory after the migration exists and before Phase 3 promotes; the user uses the completed app immediately, so unapplied migrations make the delivered change invisible or broken. No other production/live DB action is allowed: no manual query, data manipulation, seed, reset, fixture, Playwright, E2E, probe, debugging, cleanup, `rm`, truncate, direct SQLite, custom data repair, or data inspection with write risk. If the command might touch production data and the artifact cannot prove it is the repo migration command for a real schema change or an isolated test DB operation, do not run it.
- Outside Phase 5 and Phase 6, if a temporary dev server is needed for an API/runtime probe, use `task-workflow/scripts/server-probe.mjs`. It owns PID capture, readiness, bounded probe commands, runtime logs, and PID-only cleanup. Server readiness is usually 5-10 seconds; use 15-20 seconds as the normal budget and 30 seconds as the maximum startup-readiness limit. Broad process-name cleanup is only for explicit sandbox-owned recovery when PID/port cleanup is impossible and the artifact records why.
- In Phase 5 and Phase 6, the first browser, Playwright, or E2E command that needs a running app must establish lifecycle ownership through `task-workflow/scripts/playwright-lifecycle.mjs` by default. Do not run against an assumed existing server first and then infer that `fetch failed`, stale data, redirects, or wrong build output means manual server management is needed.
- Existing repo E2E tests are not a reason to bypass the helper. Run `pnpm exec playwright test ...` through the helper's `--run` by default. Use native Playwright with repo `webServer` ownership only when the helper cannot own the server for that exact command after a diagnosed reason, and record that reason before running it.
- The helper's `--env` is not a database-path override mechanism. Never set `E2E_DATABASE_FILE_PATH`, `DATABASE_PATH`, `DB_PATH`, or any similar database file/path variable in helper, setup, server, or run commands. The agent must not change the repo's internal E2E/end-to-end database file path. Test database paths must come from the repo's checked-in E2E/end-to-end config or the already-materialized environment. The live/default user-data database is the live workspace/production database; production databases must never be used for testing. Using the live/default user-data database for Playwright, E2E, fixtures, seed, reset, inspection, cleanup, or debugging is a critical failure even if it appears only in `task-workflow/`. The user can lose his job if this database is deleted or corrupted.
- Expected verification lifecycle pattern: discover the repo-owned setup and server commands from `AGENTS.md`, `package.json`, README/docs, Playwright config, and the repo-owned E2E helpers before running Phase 5 or Phase 6. Prefer a repo-owned setup command that prepares isolated E2E/test state by resetting only the test DB, applying test-targeted migrations, and seeding deterministic verification data, plus a repo-owned server command that starts the app against that isolated state. If the target repo has no named scripts for this pattern, simulate the same pattern with the smallest repo-owned/test-only commands and record the mapping before running them; never replace the pattern with production DB writes, raw DB path overrides, or manual cleanup chains.
- Do not compose manual server cleanup, fixed sleep, DB-delete, server-start, and Playwright command chains in Phase 5 or Phase 6. Put pre-server setup such as isolated test DB reset, test migration, test seed, or test database preparation into lifecycle `--setup "..."` for helper-owned runs. Treat setup plus server startup as reusable for the current verification batch: prefer one helper-owned run with the needed script/spec commands, or rerun setup only after code, migrations, fixtures, DB state, build inputs, or the prior setup output changed. Do not repeatedly delete/recreate the DB or restart the server before each targeted script/spec just because another E2E command is next. If cleanup is needed, do it as a separate recorded recovery step before the helper run, then run the helper alone. If server state, database state, port ownership, or build freshness looks wrong, diagnose through the current lifecycle owner logs/readiness first and rerun through that owner after any code/setup fix. If the helper times out or produces no useful output, treat that as lifecycle/setup evidence, inspect `task-workflow/runtime/server.log`, `task-workflow/runtime/setup-*.log`, readiness output, and `task-workflow/runtime/run-*.log`, then change the setup, server command, ready URL, test command, fixture, or diagnostic before rerunning. If the helper fails once or twice with a diagnosed lifecycle/tooling issue after a corrected invocation, record the helper logs and switch to the smallest fallback that can prove the task: repo Playwright `webServer`, explicit PID/port cleanup, or manual server management with captured PID/log/readiness/cleanup evidence. Broad process-name cleanup is only a recorded sandbox recovery after PID/port cleanup is impossible.
- Select a distinct phase-owned runtime location with the helper's `--runtime-dir` before verification begins. Preserve any cited successful logs before a later run could replace them; repeated runs must not destroy still-relevant proof. Logs carry lifecycle details; other phase records cite them. A missing copied link is corrected from existing evidence, not by rerunning a successful check just to recreate bookkeeping.
- Do not run `playwright install`, `playwright install chromium`, or equivalent browser downloads during task verification. The managed lifecycle helper uses the preinstalled browser cache when available and fails early if the project Playwright version does not match the sandbox browser cache.

### Phase-Owned Command Rules

- Phase 2 completes cohesive implementation batches with concrete file/diff/search evidence. When a new or changed cross-boundary contract, shared runtime dependency or compilation path could invalidate the connected batch, use the repository's smallest relevant non-test compile/type diagnostic to establish that specific integration before expanding the implementation; record the reason/result in the same batch entry. This is not permission for routine checks after every edit or a substitute for Phase 3. Routine full check/build, unit, E2E and browser work remains in its owning phase.
- Phase 3 reviews connected places, closes missed implementation gaps, performs implementation integrity review, then owns the ordered check/build checkpoint: repo check, focused lint when useful, and build when the repo has a separate build. Use targeted diagnostics or narrow fix checks only to prove a specific issue group. When a broad check/build command fails, inspect enough output to identify visible issue groups, fix every locally-fixable group before rerunning that broad command, and record only the groups/fixes/rerun reason. Do not rerun a broad command after each tiny fix when other visible issue groups remain. Do not keep huge command logs unless a temporary log is needed for triage; delete temporary full-output logs after extracting issue groups. Record unit/E2E coverage questions for the owning later phase.
- Phase 4 owns unit-test coverage. It decides whether unit, service, component, or integration-style coverage is warranted; then adds, updates, removes, or explicitly skips that coverage. It may remove existing unit tests when they protect non-core, non-complex, obsolete, or convoluted behavior and the artifact explains why removal improves the test suite. Phase 4 does not rerun check, lint, or build when Phase 3 evidence is current.
- Later phases reuse Phase 3 build evidence unless code, config, dependency/build inputs, migrations, generated assets, stale output, or incompatible verification tooling invalidates it. Do not rebuild in Phase 4, Phase 5, Phase 6, or Phase 7 only to prepare, reconfirm, or feel safe.
- Phase 6 owns E2E coverage. It decides whether E2E coverage is warranted; then adds, updates, removes, or explicitly skips that coverage. It may remove existing E2E tests when they protect non-core, non-complex, obsolete, brittle, or convoluted behavior and the artifact explains why removal improves the test suite.
- If unit, E2E, or browser work happens before its owning phase, do not fail the task solely for that timing. Carry the artifact, diff, and command output into the owning phase and make the owning phase's remove/update/add/skip decision current before promotion.

### Minimal Test And Rerun Rules

> Tests are production code. Extra tests are not harmless evidence; they are maintenance load, false confidence risk, and future workflow drag.

Phase 4 and Phase 6 must treat test work as a pruning and minimal-coverage decision, not as a "more tests is safer" step.

| Rule | Required behavior |
| --- | --- |
| Existing tests are not grandfathered | If an older agent added unnecessary, obsolete, brittle, convoluted, duplicated, or non-core tests, the owning phase must remove or simplify them when they are connected to the current changed behavior. |
| New tests are exceptions | Add a new test only after proving the behavior is stable/core and no connected existing test can carry the warranted assertion cleanly. |
| Passing extra tests is not quality evidence | A large passing count does not improve the gate. The gate values necessary coverage, useful assertions, and removal of bad tests. |
| Test bulk is a warning | If added tests cause max-lines, fixture churn, helper churn, slow commands, broad reruns, or new maintenance structure, stop and re-evaluate whether the tests should be merged, reduced, updated in place, or removed. Do not solve self-created test bulk by adding more structure unless the artifact proves every test remains necessary. |
| Every new test needs a burden ledger | For each new unit or E2E test case/file, record the core risk, the connected existing tests inspected, why update/remove/`N/A` was insufficient, why the assertion is minimal, and what cheaper proof was rejected. |

- Keep tests minimal. Prefer the fewest tests that protect core behavior or critical workflows. Too many tests for incidental behavior are a codebase problem, not a quality signal. Necessary distinct regression cases remain justified; there is no target test count to make records match. Correct stale counts in the authoritative record instead of merging, deleting or reorganizing valid tests merely to fit earlier prose.
- For E2E, run only new, changed, or directly connected specs that are warranted by the Phase 6 decision. Never run the unfiltered full E2E suite unless the task explicitly asks for full E2E or a concrete written repo instruction names full E2E/all-spec execution for this exact task; a repo having a Playwright suite, `webServer`, or "run tests" script is not enough. After warranted targeted or connected E2E evidence passes and no related code, test, config, fixture, migration, or build input changed, do not add a full E2E run as final confidence, final signoff, state discovery, or reviewer-satisfaction evidence.
- For a single targeted Playwright script or E2E spec, timeout increases are not a retry strategy. Start with the smallest practical timeout: `15000`-`20000` ms for Phase 5 launch/page-state/custom-script probes and up to `30000` ms for first-run Phase 6 targeted E2E where Playwright runner startup adds overhead. If the run fails with any useful error, assertion output, not-found state, console/runtime error, route error, fixture/DB miss, or helper diagnostic, use that evidence to diagnose; do not retry with a larger timeout. A larger timeout is allowed only when the first run ended only because the timer expired with no useful response or explanation, and only after helper logs, readiness, URL, not-found/error state, required DB/fixture records, server runtime logs, browser console, and network/page state prove the app and test are in the correct state to run. Only then may one rerun use `60000` ms, and never more than `120000` ms for one targeted script/spec. If a single targeted run needs more than two minutes, stop increasing timeouts; split the verifier or diagnose lifecycle, setup, fixture, page-state, console, network, or test-design failure first.
- Do not rerun tests only for confidence. Rerun when quality evidence can change: related implementation changed, the test changed, config/environment changed, previous output was incomplete/stale, or the next run gathers a narrower diagnostic needed to fix a real failure.
- Before rerunning an identical failing test command, record what changed since the previous run or what new evidence the rerun will collect. If nothing changed and the prior output is complete, inspect logs, DOM/state, traces, screenshots, or persisted data first, then change the implementation, test, command scope, or diagnostic strategy before running again. A suspected pre-existing or order-dependent failure is not a reason to broaden to a full suite; prove it with the narrow failing spec/test plus logs/state/trace evidence, then fix it if it is in scope or record it as an unrelated defended gap.
- Phase 5 and Phase 6 artifacts must record timeout values and any quiet-run/timeout triage before the gate can pass. A first-run targeted Playwright command longer than the Phase 5/Phase 6 budgets, or any longer rerun without recorded timer-only failure plus clean state triage, is a gate failure.
- If a command appears hung or idle and the next workflow action is locally available, stop the command, record the evidence in the current phase artifact or gap ledger, and continue with the bounded recovery path.

### Continuation Rules

- Every phase gate is an internal control point, not a user confirmation checkpoint.
- If a phase gate passes, continue directly into the next phase without asking whether to continue.
- If a phase gate fails, rework the phase, rerun the gate, and keep looping without asking the user for permission to continue.
- The purpose of the gate, redo, verification, and rework loop is to remove the need for user confirmation during execution and let the Agent complete the run autonomously.
- A failed phase artifact is a repair ticket, not a stopping point. Do not leave a phase with `Decision: Fail`, `Score: 0/...`, pending gate rows, or unresolved locally-fixable warnings and then produce a final response.
- If a dependency, launch detail, or local setup issue blocks progress, resolve it with the most direct logical solution that preserves the workflow and continue.
- Do not lower the skill's strictness, skip gates, or change direction because of an environment issue that can be solved inside the target repo or sandbox.
- Do not stop after any phase to summarize progress and ask whether to continue.
- Do not stop after implementation, build, lint, tests, Playwright verification, or E2E work if any later phase is still unpassed and locally available.
- Do not assume the user will catch a shortcut. The Agent must prevent the shortcut itself.

</autonomous_run_contract>

## Final Response Guard And Turn Continuity

Continue the next locally available action until all gates pass; do not rescan markers/artifacts after every tool result to decide whether to continue. If the user stops or pauses the run, flush its checkpoint and stop. Otherwise only a demonstrated external blocker permits incomplete delivery; record its evidence and next action without claiming completion.

Perform one final audit in Phase 7 and use that result for final response readiness, not a second audit immediately afterward. It must establish:

1. All eight artifacts exist; Phases 0–6 have passing numeric scores and critical results, and Phase 7's pre-completion audit is ready from concrete current evidence or defended `N/A`. Its completion result and final gate are intentionally pending until the command succeeds; this expected pending state is not missing verification. Check the owning results, not confidence or the checkpoint alone.
2. The final diff follows task scope and binding repo instructions. Changed app/server source uses approved logging, with no lasting `console.*` from Phase 5 debugging.
3. Phase 4/6 decisions, existing-first/pruning/new-test rationale, exact required command output/logs, and test-removal justification are substantiated. Phase 5/6 lifecycle ownership, bounded commands, DB safety, timeout/quiet-run triage, and zero fixed waits are current. Every cited Phase 5 screenshot exists and required functional/responsive proof passes.
4. No critical or stale unresolved gap remains. The compact checkpoint/marker correctly identify Phase 7 and completion readiness. Each final quality category is at least `8/10`.
5. Resolve one final-audit list of actual deficiencies, batch related fixes, and refresh only affected claims. Recheck those resolutions, not a fresh whole-workflow audit after each correction. Once the pre-completion audit is ready, invoke the exact supplied MITB completion command. On success, record its returned outcome once in Phase 7, finalize its unchanged numeric gate and checkpoint, and respond. These final record writes are allowed; no further check/build/test/browser or new audit follows successful completion. If the command fails, diagnose that failure without discarding unrelated passing proof. Never claim completion before success.

Phase 7 cites authoritative earlier evidence; do not copy outputs, fixed-wait reviews, screenshot inventories, or removed-test ledgers into a new set of recaps. Documentation-only corrections stay in Phase 7. Substantive failures follow scoped invalidation, not a blanket replay.

## Critical Output Invariant

These are hard constraints:

- The target app must be a real interactive app, not a static mockup.
- The implementation must be authored in the target repo as real routes, layouts, components, state, styling, backend contracts, services, queries, migrations, and tests when required by Phase 4 or Phase 6 coverage decisions.
- Primary pages or views must be implemented as real router routes or repo-native route modules, not as an in-memory page-state switch inside one large component.
- Visible controls required or implied by the task must become real target controls with matching states and persisted behavior when persistence is required.
- Backend/data work must follow the repo's existing service, contract, query, and persistence boundaries.
- Frontend runtime code must not import server-only runtime modules.
- Reusable UI styling belongs in shared primitives, component-local styling, or existing design tokens, not fake global one-off component classes.
- Phase 3 check/lint evidence, Phase 4 unit-test work, Phase 5 interactive Playwright verification, and Phase 6 E2E work are separate gates. None is a substitute for another.
- The Agent must review the app part by part, route by route, state by state, and flow by flow.
- If a critical visible action, route, data mutation, or verification path remains fake, broken, or unreviewed, the run has not passed.
- Existing tests must not be deleted merely to make the new task pass. If obsolete tests are removed, replace their useful coverage or document why the old coverage no longer applies.
- Type assertions, broad casts, and warning suppression are not acceptable substitutes for correct contracts and narrowed types.
- Final signoff must score at least `8/10` in each quality category: functional result, skill compliance/artifact integrity, code quality/maintainability, test quality, and overall result.

## Reference Loading Rules

<reference_loading_rules>

Do not load every reference file by default.

### Loading And Resume

Follow the Evidence And Resume Contract. Load only the reference owning the current workstream; reuse loaded references across connected phases during uninterrupted work. `references/playwright-interactive.md` is additionally required for Phase 5. A marker change alone is not a reason to reread an already-loaded reference.

After context loss, reload the skill/checkpoint/marker, current artifact/gaps/reference, and binding repo/task/domain/selected-skill inputs from the Phase 1 input manifest. Inspect attachments relevant to the resumed work; the manifest identifies all initial inputs and what was learned. Do not repeat initial codebase research or capture/test work already proven current. If a particular declaration or implementation detail is needed, open the actual file then rather than transcribing it into the ledger.

Phase reference map:

| Current phase marker | Reference to load |
| --- | --- |
| missing `task-workflow/` | `references/phase-0-1-startup-research.md` |
| `phase-0-artifact-reset` | `references/phase-0-1-startup-research.md` |
| `phase-1-task-research` | `references/phase-0-1-startup-research.md` |
| `phase-2-execution` | `references/phase-2-4-execution-integrity.md` |
| `phase-3-second-execution` | `references/phase-2-4-execution-integrity.md` |
| `phase-4-unit-coverage` | `references/phase-2-4-execution-integrity.md` |
| `phase-5-playwright-verification` | `references/phase-5-7-verification-signoff.md` and `references/playwright-interactive.md` |
| `phase-6-e2e-verification` | `references/phase-5-7-verification-signoff.md` |
| `phase-7-final-signoff` | `references/phase-5-7-verification-signoff.md` |

The phase references are grouped by connected workstream, not one file per phase. This matches the reference skill pattern: `SKILL.md` holds the strict global protocol and the reference files hold detailed process for the current workstream.

</reference_loading_rules>

## Operating Modes

<operating_modes>

### Validation Mode

Use this when improving or testing the skill itself.

- Use a throwaway target repo copy.
- Preserve all workflow artifacts.
- Judge repeatability across fresh runs.
- If the same failure repeats, improve the reusable skill before running again.

### Delivery Mode

Use this when the user wants the real target app or task completed.

- Work inside the provided target repo.
- Treat the task file as the source of truth.
- Do not sign off until every gate in this file and the phase references has passed in writing.

</operating_modes>

## Required Artifacts

These are mandatory:

- `task-workflow/`
- `task-workflow/phase-0-artifact-reset.md`
- `task-workflow/phase-1-task-research.md`
- `task-workflow/phase-2-execution.md`
- `task-workflow/phase-3-second-execution.md`
- `task-workflow/phase-4-unit-coverage.md`
- `task-workflow/phase-5-playwright-verification.md`
- `task-workflow/phase-6-e2e-verification.md`
- `task-workflow/phase-7-final-signoff.md`
- `task-workflow/progress.md`
- `task-workflow/open-gaps.md`
- `task-workflow/CURRENT_PHASE.txt`
- `task-workflow/playwright/`
- `task-workflow/screenshots/`
- `task-workflow/scripts/`
- `task-workflow/scripts/playwright-lifecycle.mjs`
- `task-workflow/scripts/server-probe.mjs`
- `task-workflow/runtime/`

Copy the templates in `assets/templates/`. Their sections locate required evidence; each fact is written once and gate rows point to it. Related evidence may be grouped when all required semantic categories remain auditable. Do not create extra recap/checklist/permission tables or transcribe facts already in inputs, code, screenshots, or logs.

## Multi-Phase Protocol

<multi_phase_protocol>

Follow the phases in order:

### Phase 0: Artifact Reset And Scaffolding

Delete the previous task's `task-workflow/` artifacts, recreate the required artifact files from templates, and prove no implementation files were edited.

Detailed process: `references/phase-0-1-startup-research.md`.

### Phase 1: Task Intake And Codebase Research

Read the task, root `AGENTS.md`, `.tasks/domain.md`, every task attachment/supporting file in `.tasks/files/`, only relevant available skill files from `.agents/skills/`, relevant docs, and codebase. Treat `AGENTS.md` as binding development instructions; extract its task-relevant rules before planning. These are reference inputs: read and cite them, but do not edit them. Record task understanding, development rules, task files read or inspected, selected skills, affected files, patterns to reuse, risks, and an ordered implementation plan.

Detailed process: `references/phase-0-1-startup-research.md`.

### Phase 2: Primary Execution

Execute the researched plan in order, keep changes scoped, and record implementation evidence.

Detailed process: `references/phase-2-4-execution-integrity.md`.

### Phase 3: Second Execution, Integrity, And Check/Lint Validation

Review the implementation as a continuation pass, close missing or weak work, propagate consistency to associated UI/API/data surfaces, run implementation integrity review, and complete the ordered check/build checkpoint. Do not write or run unit/Vitest or E2E tests in Phase 3.

Detailed process: `references/phase-2-4-execution-integrity.md`.

### Phase 4: Unit Test Coverage Decision And Verification

Decide whether unit, service, component, or integration-style tests are needed. Add, update, remove, or explicitly skip that coverage, then run only the warranted unit-level commands. Remove tests that are unnecessary, obsolete, convoluted, or protecting non-core/non-complex behavior.

Detailed process: `references/phase-2-4-execution-integrity.md`.

### Phase 5: Interactive Playwright Verification

Use standalone interactive Playwright scripts in two stages. Stage 1 proves the changed behavior works through real user interaction. Stage 2 verifies UI quality: no broken, cramped, overlapping, clipped, ill-placed, or non-responsive UI on the affected surfaces. Treat responsive design as a first-class Phase 5 guarantee, equal to proving the task's functional changes work. Some whitespace is fine, but standard desktop viewports such as `1920x1080` must not look broken, clipped, overlapped, unusable, or excessively sparse. Large desktop viewports such as `2560x1440` may have some extra whitespace, but not broad empty regions that make the UI feel unfinished. Very large 4K/ultrawide whitespace is acceptable when the layout is intentionally constrained and still coherent.

The Phase 4/Phase 6 test-minimality rules do not shrink Phase 5. Phase 5 is the main user-facing verification phase and may take the time needed to cover changed flows, relevant bad cases, surrounding UI, responsive breakpoints, screenshots, and visual correctness. Use multiple focused Playwright scripts, probes, viewport passes, or reruns when needed to prove the affected user experience is correct; keep them scoped to the changed and adjacent surfaces, but do not reduce Phase 5 to a shallow smoke check.

Detailed process: `references/phase-5-7-verification-signoff.md` and `references/playwright-interactive.md`.

### Phase 6: E2E Coverage Decision And Verification

Make the E2E coverage decision. Review existing E2E coverage first, update it when a warranted core flow already belongs there, add new E2E tests only for critical or complex workflows that cannot be cleanly covered by existing tests, remove unwanted E2E tests that protect non-core/non-complex or convoluted flows, and avoid E2E for small, visual-only, or incidental UI changes.

Detailed process: `references/phase-5-7-verification-signoff.md`.

### Phase 7: Final Audit And Signoff

Audit each owning artifact and the final diff once. Record real deficiencies in one resolution batch; repair them together and refresh only affected checks. Reconcile record-only issues in place, cite current results, and review the resolutions rather than restarting the audit. The pre-completion audit becoming ready authorizes the supplied MITB completion command; only its successful result completes Phase 7's final gate.

Phase 7 is an evidence validator for missed work, not a validation rerun phase. If a required check, build, test, Playwright run, E2E run, or other phase-owned command was already completed correctly in its owning phase and the evidence is current, Phase 7 must only verify that evidence. Rerun a command only when the owning phase missed the required command, the recorded evidence is missing/incomplete/stale, or later changes invalidated it; otherwise never rerun checks, builds, tests, Playwright, or E2E in Phase 7.

Detailed process: `references/phase-5-7-verification-signoff.md`.

The phase references are not optional expansion material. They are the detailed execution instructions for the current workstream.

</multi_phase_protocol>

## Disallowed Shortcuts And Automatic Fails

<automatic_fails>

These automatically fail the run:

### Phase Boundary And Artifact Fails

- editing app/source files before Phase 1 passes
- editing app/source files before Phase 0 artifacts exist
- editing implementation/source files while `task-workflow/CURRENT_PHASE.txt` still says `phase-0-artifact-reset` or `phase-1-task-research`
- passing Phase 2 while `task-workflow/phase-2-execution.md` does not record that the marker was set to `phase-2-execution` before source edits
- skipping artifact reset
- failing to copy the artifact templates before implementation work
- failing to create, read after compaction, or keep `task-workflow/progress.md` current enough to resume the run
- after compaction/context loss or a new coding session, continuing work without reloading the skill/checkpoint/marker, current artifact/gaps/reference, and binding/relevant inputs
- doing phase work without its required reference loaded in the current context
- failing to record the Phase 1 input manifest or reload binding/relevant inputs after context loss
- reading `AGENTS.md` only as context instead of extracting and following the task-relevant development rules it defines
- editing `.tasks/task.md`, `.tasks/domain.md`, `.tasks/files/`, selected skill files under `.agents/skills/`, or `AGENTS.md` without the user/task explicitly requesting an edit to that exact reference file
- leaving the checkpoint without a usable current phase/artifact/reference, next action, or input-manifest pointer
- using `task-workflow/progress.md` as a duplicate file inventory instead of pointing to the owning phase artifacts for details
- omitting required semantic evidence from a phase artifact while claiming that phase passed
- advancing `task-workflow/CURRENT_PHASE.txt` while the current or any previous phase artifact still says `Decision: Fail`
- advancing `task-workflow/CURRENT_PHASE.txt` while the current or any previous phase artifact still has placeholder `Pending` gate evidence
- leaving artifact templates mostly blank while claiming success
- passing Phase 5 while any screenshot path cited in the artifact is missing or not verified with existence proof
- passing Phase 6 while required E2E runs are only described and the exact command output is not recorded in the artifact or in a cited repo-local log file
- running Phase 5 or Phase 6 Playwright/E2E commands without the correct lifecycle owner recorded: helper by default, repo Playwright `webServer` or manual fallback only with a recorded reason/diagnostic made before the command
- deleting, resetting, reseeding, truncating, directly modifying, or using the production/live workspace database as test/verification state; this includes repo default user-data DB paths, and any equivalent live DB path
- running any production/live DB action other than the repo's required app migration command for a real schema change; prohibited actions include manual queries, data manipulation, seed, reset, fixture, Playwright, E2E, debug, cleanup, direct SQLite, custom data repair, delete, or truncate against any equivalent live DB path
- running a production database migration except as the app's required migration for a real schema change, in the owning phase, with explicit migration evidence
- passing Phase 3 after creating or changing a migration without applying it through the repo's app migration command against the production/live default DB and recording the target, command, reason, and output

### Test Hygiene And Coverage Fails

- adding or requiring unit tests for small fixes, minor UI adjustments, copy changes, color/style changes, spacing/layout tuning, or simple button wiring without a concrete core-behavior or risk reason
- adding unit tests for trivial component branches, incidental button clicks, visual-only changes, or one-off UI behavior instead of reserving unit tests for core stable behavior
- keeping unnecessary, obsolete, convoluted, or non-core/non-complex unit tests after Phase 4 identifies them as removable
- adding unit tests without a per-test necessity ledger proving existing tests could not be updated, the behavior is stable/core, and every new assertion is minimal
- preserving old agent-created unit tests as "already there" when connected evidence shows they are unnecessary, duplicated, brittle, convoluted, or non-core/non-complex
- adding enough unit tests to require test-file splitting, helper churn, fixture churn, or broad reruns without first reducing or removing unnecessary test coverage and recording why the remaining bulk is necessary
- adding a new E2E test for behavior that is not a critical/core workflow, not a complex flow, or can be cleanly covered by updating existing E2E coverage
- keeping unnecessary, obsolete, brittle, convoluted, or non-core/non-complex E2E tests after Phase 6 identifies them as removable
- adding E2E tests without a per-test necessity ledger proving existing E2E could not be updated, the workflow is critical/core or complex enough for E2E, and every new assertion is minimal
- preserving old agent-created E2E tests as "already there" when connected evidence shows they are unnecessary, duplicated, brittle, convoluted, or non-core/non-complex
- starting with a broad/full unit or Vitest suite in Phase 4 before the warranted targeted/connected unit-level tests, when any are warranted, have passed
- running the full unit/Vitest suite more than once without a concrete artifact reason from target repo instructions, changed global/shared infrastructure, or incomplete/stale output
- running broad/full unit or Vitest without Phase 4 artifact evidence that warranted targeted/connected tests already passed and this is the one final sanity check, or that the task/repo/global change explicitly requires the broader scope
- running routine check, lint, or build after every small Phase 2 edit instead of preserving packet evidence and using Phase 3 as the ordered check/build checkpoint
- running routine full check/build commands in Phase 2 without a concrete connected-integration reason recorded before a narrow diagnostic
- rerunning check, lint, or build before all visible locally-fixable issue groups from the prior output are fixed; truncated `tail`/`head` output alone is not enough if it hides issue groups, and temporary full-output logs must be deleted after extraction
- rerunning build in Phase 4, Phase 5, Phase 6, or Phase 7 when Phase 3 build evidence is current and no invalidating change is recorded

### Playwright And E2E Command Fails

- running native `pnpm exec playwright test ...` in Phase 6 instead of running it through `task-workflow/scripts/playwright-lifecycle.mjs --run ...`, unless repo `webServer` ownership is required and recorded before the command
- running the unfiltered full Playwright/E2E suite when the task did not explicitly ask for full E2E and no concrete written repo instruction names full E2E/all-spec execution for this exact task
- running `rm`, `seed`, `migrate`, `sqlite3`, fixture setup, or any DB cleanup command from Phase 5/6 unless the artifact first proves the command targets an isolated repo-owned test/E2E database and not production/live user data
- starting a first-run targeted Phase 5 Playwright script above `20000` ms or a first-run targeted Phase 6 E2E above `30000` ms without a task-specific artifact reason
- increasing a Playwright/E2E timeout after any useful failure evidence, or increasing it after a timer-only/no-output failure without recorded helper-log/readiness/URL/DB-fixture/server-log/browser-console/network/page-state triage proving the app and test are valid to rerun
- rerunning tests only for confidence, or blindly rerunning the same failing test command without recording a material implementation, test, config, environment, output-staleness, or diagnostic reason
- running `playwright install`, `playwright install chromium`, or equivalent browser downloads during task verification instead of using the sandbox browser cache or recording the helper's browser-preflight mismatch

### Continuity And Evidence Fails

- passing Phase 3 or Phase 7 while changed app/server source still contains `console.*` outside the active Phase 5 debug loop
- producing a final response or stopping summary while `CURRENT_PHASE.txt` is before `phase-7-final-signoff`
- producing a final response or stopping summary while any required artifact still says `Decision: Fail`, has a failing score, or contains pending gate evidence
- ending an OpenCode turn mid-phase while the next workflow action is locally available
- completing meaningful Phase 2 implementation batches without recording their concrete execution evidence
- completing meaningful implementation batches without incremental file/diff evidence and a resumable checkpoint
- omitting required semantic evidence while claiming a passing gate
- skipping the second execution pass
- treating Phase 3 check/lint evidence as a substitute for Phase 4 unit-test coverage decisions, Phase 5 interactive Playwright verification, or Phase 6 E2E coverage decisions
- treating Playwright verification as a substitute for warranted Phase 4 or Phase 6 test work
- running Phase 5 interactive Playwright verification or Phase 6 E2E coverage work as a substitute for completing the Phase 2 gate
- leaving a long-lived dev server, watcher, or interactive command in the foreground until the session stalls
- claiming implementation-batch proof without a current diff/inspection or ignoring failed/uncertain writes
- continuing after a failed, invalid, or uncertain write result without repairing and rereading the target file

### Final Signoff Fails

- signing off while critical open gaps remain
- signing off while `task-workflow/open-gaps.md` contains stale open gaps that a passed later phase claims to have resolved
- signing off while `task-workflow/open-gaps.md` still contains template placeholder rows such as `Pending`
- passing Phase 5, Phase 6, or Phase 7 without recorded fixed-wait review evidence
- passing Phase 5, Phase 6, or Phase 7 while fixed waits remain in interactive verification scripts or repo-discovered E2E tests
- passing Phase 7 without a recorded artifact integrity review of every phase artifact
- signing off while any final quality scorecard category is below `8/10`
- deleting existing tests without equivalent replacement coverage or a written artifact defense
- using broad unsafe casts or warning suppression to bypass the type system without a narrow evidence-backed reason
- relying on conversation memory after compaction instead of using `progress.md` and `CURRENT_PHASE.txt` for status and re-reading this skill, required phase reference files, and artifacts
- failing to enumerate `.tasks/files/` even when it is empty
- failing to read or inspect every task attachment/supporting file in `.tasks/files/` before Phase 1 planning
- bulk-reading every skill file in `.agents/skills/` instead of selecting and reading only task-relevant skills
- planning, implementing, verifying, or signing off work that violates the extracted `AGENTS.md` development rules
- running a MITB task completion command before all Phase 7 audit checks pass
- failing to repair a substantive final-audit failure in its owning phase and refresh affected evidence
- failing to run the required MITB completed command after all Phase 7 audit checks pass
- asking the user whether to continue between phases when the next phase is unblocked

</automatic_fails>

## Reference Map

- `references/phase-0-1-startup-research.md`: artifact reset, template copying, task intake, and codebase research.
- `references/phase-2-4-execution-integrity.md`: primary execution, second execution, gap closure, and integrity checks.
- `references/phase-5-7-verification-signoff.md`: interactive Playwright verification, E2E coverage decisions, and final audit.
- `references/playwright-interactive.md`: how this skill uses standalone interactive Playwright scripts.
- `assets/templates/phase-0-artifact-reset.md`
- `assets/templates/phase-1-task-research.md`
- `assets/templates/phase-2-execution.md`
- `assets/templates/phase-3-second-execution.md`
- `assets/templates/phase-4-unit-coverage.md`
- `assets/templates/phase-5-playwright-verification.md`
- `assets/templates/phase-6-e2e-verification.md`
- `assets/templates/phase-7-final-signoff.md`
- `assets/templates/progress.md`
- `assets/templates/open-gaps.md`
- `assets/scripts/playwright-lifecycle.mjs`: managed server/readiness/Playwright execution helper copied into `task-workflow/scripts/` during Phase 0.
- `assets/scripts/server-probe.mjs`: managed API/runtime server probe helper copied into `task-workflow/scripts/` during Phase 0 for pre-Phase-5 server checks.

## Non-Negotiables

- Use the phase gates exactly.
- Keep the artifacts auditable.
- Repair substantive failures in their owning phase; reconcile record-only issues without invalidating valid proof.
- Do not edit source files before Phase 0 and Phase 1 gates pass.
- Do not sign off before interactive Playwright verification and regression test gates pass.

## Completion Standard

The task is complete only when Phase 7 passes.
If the task cannot be completed, the final artifact must identify the exact blocking condition, the phase where it occurred, commands run, files inspected, and the smallest next action needed.
