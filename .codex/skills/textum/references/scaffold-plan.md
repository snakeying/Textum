# Stage 2a: Scaffold Plan (write `docs/scaffold-pack.json`)

Read:
- `docs/prd-pack.json`
- `docs/scaffold-check-replan-pack.json` (if exists)
- `docs/diagnostics/scaffold-check.md` (if exists)

Write:
- `docs/scaffold-pack.json` (pure JSON; no ``` blocks)

Goal: write **confirmed technical decisions only** into `docs/scaffold-pack.json` (single source of truth).

## Output contract (hard)

Output MUST be exactly one of:

1) `IN_PROGRESS`
   - Output exactly 2 blocks:
     1) Either:
        - This-round questions (<=4; blockers only), OR
        - This-round change summary (JSONPath list; no questions)
     2) Remaining blockers (<=8; prioritized)
   - If you output questions: **do NOT write** `docs/scaffold-pack.json` this round.

2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/scaffold-pack.json`
     - `next: Scaffold Check`

- Never output JSON bodies (including `docs/scaffold-pack.json`).

## Interaction

- Ask in the user's language (ZH/EN).

## Writing rules

- Do not guess; if not confirmed, ask.
- Do not manually edit `extracted` (it is auto-populated by scripts).
- Required decisions (minimum):
  - `$.decisions.tech_stack.backend`
  - `$.decisions.tech_stack.frontend`
  - `$.decisions.tech_stack.database`
  - `$.decisions.repo_structure[]`
  - `$.decisions.validation_commands[]` (use a single full `N/A` row if truly not applicable)
- `$.decisions.validation_commands[].type` must start with `gate:` or `opt:` (unless the row is fully `N/A`).
- `validation_commands` `N/A` must be either fully `N/A`, or fully concrete (no partial `N/A`).

## Start / Replan handling

If `docs/scaffold-pack.json` does not exist (workspace root):
1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum scaffold init`
Then ask: confirm backend/frontend/database choices (be specific: language + framework + DB).

If `docs/scaffold-check-replan-pack.json` exists:
- Treat `items[]` as the current blockers and resolve them first.
- Follow the Output contract: pick either ask-mode (questions only) or write-mode (change summary only).
