# Stage 1a: PRD Plan & Clarification (write JSON prd-pack)

Read: `docs/prd-pack.json` (if exists) | Write: `docs/prd-pack.json` (pure JSON; no ``` blocks)
Also read (only if exists; replan artifacts):
- `docs/prd-check-replan-pack.json`
- `docs/diagnostics/prd-check.md`

Goal: keep writing **confirmed facts only** into `docs/prd-pack.json` (single source of truth).

## Output rules (must follow)

Output MUST be exactly one of the following (no extra explanation / paraphrase):

1) `IN_PROGRESS`
   - Output exactly 2 blocks:
     1) This-round questions (~4; blockers only) OR This-round change summary (JSONPath list)
     2) Remaining blockers (~8; prioritized)

2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/prd-pack.json`
     - `next: PRD Check`

- Never output JSON bodies (including `docs/prd-pack.json`)
- **Do NOT write `docs/prd-pack.json` in a round whose output contains questions**

## Interaction language (must follow)

- The user may speak Chinese or English.
- Ask questions in the user's language (ZH/EN).
- Keep questions short and specific.

## Writing rules (must follow)

- Do not write unconfirmed info; unknown stays empty / `[]` / `null`
- Only write `N/A` when the user explicitly says "none" / "not applicable"
- Do not rewrite user-provided tokens (especially `modules[].feature_points[].landing[]`)
- When writing string values, avoid double-escaping quotes/backslashes; write the intended value as valid JSON.
- **Do NOT maintain IDs**: all `*.id` may be `null`; ID continuity/uniqueness is enforced by scripts
- **When writing, prefer using `uv run --project .codex/skills/textum/scripts textum prd patch ...` to apply minimal field-level changes (set/append/delete), instead of rewriting the whole file.**
- If multiple JSONPath edits are needed, apply multiple patch commands; keep each patch atomic.

## Start

If `docs/prd-pack.json` does not exist, initialize once (workspace root):

1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum prd init`

Then ask: describe the app in 1-3 sentences (who is it for, and what problem does it solve?).

If `docs/prd-check-replan-pack.json` exists:
- Treat `items[]` as the current blockers (ignore older issues not present).
- Choose exactly one mode for this round:
  - Ask-mode: ask up to ~4 questions to resolve blockers; do NOT write JSON.
  - Write-mode: apply a minimal write (single-action fix if possible), and output a JSONPath change summary; do NOT ask questions.
