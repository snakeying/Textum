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

## Output rules (must follow)

Output MUST be exactly one of:

1) `IN_PROGRESS`
   - Output exactly 2 blocks:
     1) This-round questions (~4; blockers only) OR This-round change summary (JSONPath list)
     2) Remaining blockers (~8; prioritized)
2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/split-plan-pack.json`
     - `next: Split Generate`

- Never output JSON bodies (including `docs/split-plan-pack.json`)
- Do NOT write `docs/split-plan-pack.json` in a round whose output contains questions

## Writing rules (must follow)

- No narration; write facts/decisions only.
- Story numbering must be consecutive: `Story 1..N`.
- `stories[].slug` must be unique kebab-case.
- `stories[].modules` must be PRD module ids only (`M-01`), not names.
- If a PRD module is assigned to multiple stories, feature points under that module are distributed round-robin across those stories.
- `api_assignments[]`:
  - If PRD `api.has_api=false`: must be `[]`
  - Else: every PRD `API-###` must appear exactly once.

## READY gate (single source of truth)

After each write, run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split plan check`

Only if the output is `PASS`, you may output `READY`.

## Start

If `docs/split-plan-pack.json` does not exist, initialize once (workspace root):

1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum split plan init`

Then ask (preference check; defaults are OK):
- Default (if user gives no preference): 12 stories; order = prerequisites first, then cover P0 modules early.
- Ask only if needed (at most 1 preference question):
  - "Any preferred story count or must-have sequencing constraints? (default: 12; deps-first then P0)"
- If the user says "no preference": accept defaults and proceed without follow-up questions.

If the user is returning from a Split gate failure and a `docs/split-*-replan-pack.json` exists:
- Treat `items[]` as the current blockers (ignore older issues not present).
- Choose exactly one mode for this round:
  - Ask-mode: ask up to ~4 questions to resolve blockers; do NOT write JSON.
  - Write-mode: apply a minimal write (single-action fix if possible), and output a JSONPath change summary; do NOT ask questions.
