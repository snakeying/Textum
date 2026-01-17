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
     1) Either:
        - This-round questions (<=4; blockers only), OR
        - This-round change summary (JSONPath list; no questions)
     2) Remaining blockers (~8; prioritized)
   - If you output questions: **do NOT write** `docs/split-plan-pack.json` this round.
2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/split-plan-pack.json`
     - `next: Split Generate`

- Never output JSON bodies (including `docs/split-plan-pack.json`)

## Interaction

- Ask in the user's language (ZH/EN).
- Prefer the single preference question in "Start"; accept defaults if the user has no preference.

## Writing rules

- No narration; write facts/decisions only.
- Story numbering must be consecutive: `Story 1..N`.
- `stories[].slug` must be unique kebab-case.
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

Then ask (preference check; defaults are OK):
- Default (if user gives no preference): 12 stories; order = prerequisites first, then cover P0 modules early.
- Ask only if needed (at most 1 preference question):
  - "Any preferred story count or must-have sequencing constraints? (default: 12; deps-first then P0)"
- If the user says "no preference": accept defaults and proceed without follow-up questions.

If any `docs/split-*-replan-pack.json` exists:
- Treat `items[]` as the current blockers and resolve them first.
- Follow the Output contract: pick either ask-mode (questions only) or write-mode (change summary only).
