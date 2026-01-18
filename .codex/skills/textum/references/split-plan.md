# Stage 3a: Split Plan (write JSON split-plan-pack)

Read (minimal, low-noise):
- `docs/prd-slices/index.json`
- `docs/prd-slices/modules.*.json`
- `docs/prd-slices/api_endpoints.*.json` (only if `api.has_api=true`)
- `docs/split-replan-pack.json` (only if exists)
- `docs/split-plan-check-replan-pack.json` (only if exists)
- `docs/split-check1-replan-pack.json` (only if exists)
- `docs/split-check2-replan-pack.json` (only if exists)
- `docs/diagnostics/split-*.md` (only if exists; prefer the matching stage)

Write:
- `docs/split-plan-pack.json` (pure JSON; no ``` blocks)

Goal: write **confirmed planning decisions only** (story boundaries/order, module ownership, API ownership) until the `READY` gate passes.

## Output contract (hard)

Output MUST be exactly one of:

1) `IN_PROGRESS`
   - Output exactly 2 blocks:
     1) This-round change summary (JSONPath list; may be empty; no questions)
     2) Remaining blockers (~8; prioritized)
2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/split-plan-pack.json`
     - `next: Split Generate`

- Never output JSON bodies (including `docs/split-plan-pack.json`)

## No conversation

- Do not ask questions in this stage.
- Use data-driven heuristics from the input JSON; you may write iteratively in `IN_PROGRESS` rounds.

## Blocking prerequisites

Do not write `docs/split-plan-pack.json` unless all are true:
- `docs/prd-slices/index.json` exists
- `docs/prd-slices/modules.*.json` are available (from the slice index)
- If `api.has_api=true`: `docs/prd-slices/api_endpoints.*.json` are available (from the slice index)

## Heuristics (story count + ordering)

Compute `module_count`, `total_feature_points`, and `api_count` (if any) from the slice JSON.

Budget-style targets (soft):
- target `feature_points` per story: ~6 (prefer <=8; avoid >12)
- target APIs per story: ~2 (prefer <=3; avoid >5)

Derive story count:
- `n_fp = ceil(total_feature_points / 6)`
- `n_api = ceil(api_count / 2)` (if `api_count > 0`)
- `N = max(1, n_fp, n_api)`

Then build stories with these rules:
- Ordering: prerequisites/dependencies first; cover P0 modules early.
- Every PRD module id must appear in at least one story `stories[].modules[]`.
- If a module is too large, split it across multiple stories by assigning the same module id to multiple stories (and later distribute feature points round-robin).
- If `api.has_api=true`: assign every PRD `API-###` to exactly one story in `api_assignments[]` and keep per-story API counts within budget.

## Writing rules

- No narration; write facts/decisions only.
- Story numbering must be consecutive: `Story 1..N`.
- `stories[].slug` must be unique kebab-case. Suggested rule: `slug = join(lowercase story.modules, '-')`; if duplicate, suffix `-s<n>`.
- `stories[].modules` must be PRD module ids only (`M-01`), not names.
- If a PRD module is assigned to multiple stories, feature points under that module are distributed round-robin across those stories.
- `api_assignments[]`:
  - If PRD `api.has_api=false`: must be `[]`
  - Else: every PRD `API-###` must appear exactly once.

## Pre-READY minimum

Hard gate: you MUST NOT output `READY` unless these are confirmed and written.
- `stories[]` is non-empty.
- Every story has non-placeholder `slug` and `goal` (no `<<FILL>>`, `TBD`, `TODO`, `[...]`).
- `stories[].n` is consecutive `1..N`, and matches `stories[].story` (`Story <n>`).
- `stories[].modules[]` uses PRD module ids only, and every PRD module is owned by at least one story.

## READY gate (single source of truth)

After each write, execute (agent-run; workspace root):

`uv run --project .codex/skills/textum/scripts textum split plan check`

Only if the output is `PASS`, you may output `READY`.
(`PASS` may include non-blocking `WARN` items unless you run with `--strict`.)

## Start

If `docs/split-plan-pack.json` does not exist, initialize once (agent-run; workspace root):

1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum split plan init`

Then generate the plan using the "Blocking prerequisites" and "Heuristics" sections (no questions).

If any `docs/split-*-replan-pack.json` exists:
- Treat `items[]` as the current blockers and resolve them first.
- Follow the Output contract.
