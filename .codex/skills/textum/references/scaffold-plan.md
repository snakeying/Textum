# Stage 2a: Scaffold Plan (write JSON scaffold-pack)

Read: `docs/prd-pack.json` | Write: `docs/scaffold-pack.json` (pure JSON; no ``` blocks)
Also read (only if exists; replan artifacts):
- `docs/scaffold-check-replan-pack.json`
- `docs/diagnostics/scaffold-check.md`

Goal: write **confirmed technical decisions only** into `docs/scaffold-pack.json` (single source of truth).

## Output rules (must follow)

Output MUST be exactly one of:

1) `IN_PROGRESS`
   - Output exactly 2 blocks:
     1) This-round questions (~4; blockers only) OR This-round change summary (JSONPath list)
     2) Remaining blockers (~8; prioritized)
2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/scaffold-pack.json`
     - `next: Scaffold Check`

- Never output JSON bodies (including `docs/scaffold-pack.json`)
- Do NOT write `docs/scaffold-pack.json` in a round whose output contains questions

## Interaction language (must follow)

- The user may speak Chinese or English.
- Ask questions in the user's language (ZH/EN). If mixed, follow the user's last message.

## Writing rules (must follow)

- Do not guess; if not confirmed, ask.
- Do not manually edit `extracted` (it is auto-populated by scripts).
- `$.decisions.validation_commands[].type` must start with `gate:` or `opt:` (unless the row is fully `N/A`).
- `validation_commands` `N/A` must be either fully `N/A`, or fully concrete (no partial `N/A`).
- Required decisions (minimum):
  - `$.decisions.tech_stack.backend`
  - `$.decisions.tech_stack.frontend`
  - `$.decisions.tech_stack.database`
  - `$.decisions.repo_structure[]`
  - `$.decisions.validation_commands[]` (use a single full `N/A` row if truly not applicable)

## Start

If `docs/scaffold-pack.json` does not exist, initialize once (workspace root):

1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum scaffold init`

Then ask: confirm your preferred backend/frontend/database choices (be specific: language + framework + DB).

If `docs/scaffold-check-replan-pack.json` exists:
- Treat `items[]` as the current blockers.
- Choose exactly one mode for this round:
  - Ask-mode: ask up to ~4 questions to resolve blockers; do NOT write JSON.
  - Write-mode: apply a minimal write (single-action fix if possible), and output a JSONPath change summary; do NOT ask questions.
