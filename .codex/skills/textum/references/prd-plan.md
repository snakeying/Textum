# Stage 1a: PRD Plan & Clarification (write `docs/prd-pack.json`)

Read (if exists):
- `docs/prd-pack.json`
- `docs/prd-check-replan-pack.json`
- `docs/diagnostics/prd-check.md`

Write:
- `docs/prd-pack.json` (pure JSON; no ``` blocks)

Goal: write **confirmed facts only** into `docs/prd-pack.json` (single source of truth).

## Output contract (hard)

Output MUST be exactly one of:

1) `IN_PROGRESS`
   - Output exactly 2 blocks:
     1) Either:
        - This-round questions (<=4; blockers only), OR
        - This-round change summary (JSONPath list; no questions)
     2) Remaining blockers (<=8; prioritized)
   - If you output questions: **do NOT write** `docs/prd-pack.json` this round.

2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/prd-pack.json`
     - `next: PRD Check`

- Never output JSON bodies (including `docs/prd-pack.json`).

## Interaction

- Ask in the user's language (ZH/EN).
- Keep questions short and specific (<=4 per round; bundle when possible).

## Workflow preferences

Confirm the preferences below (user-specified wins; otherwise recommend ONE set, then confirm-or-edit):
- tech stack: backend / frontend / database (strings; use concrete strings like `CLI (no UI)` / `none` when applicable)
- repo structure: major folders (non-empty list of `{path,purpose}`)
- validation commands: lint/test/build gates (non-empty list of `{type,command,note}`)
  - `type` starts with `gate:` or `opt:`; OR a single full `N/A` row only if truly not applicable

Interaction rule (prefer a single bundled question):
- If user did not specify: propose ONE recommended set (stack + structure + validation) and ask "confirm or edits?"
- Set `workflow_preferences.confirmed=true` only after the user explicitly confirms the set.

## Writing rules

- Do not guess; unknown stays empty / `[]` / `null`.
- Only write `N/A` when the user explicitly says "none" / "not applicable".
- Do not rewrite user-provided tokens (especially `modules[].feature_points[].landing[]`).
- **Do NOT maintain IDs**: all `*.id` may be `null` (scripts enforce ID continuity/uniqueness).
- If `workflow_preferences` is missing, add it using the template shape (`schema_version="workflow-preferences@v1"`, `confirmed=false`, `scaffold_plan.*` empty/null).
- Write preferences to `workflow_preferences.scaffold_plan.*` (see "Workflow preferences" section).
- Prefer atomic edits via `textum prd patch {set|append|delete}`; avoid full-file rewrites.

## Pre-READY minimum

Hard gate: you MUST NOT output `READY` unless these are **confirmed** and written.
- `roles[]` is non-empty (each role has `role/description/typical_scenarios[]`).
- `permission_matrix.operations[]` is non-empty (each item has `op` and `per_role` with `A/D/O`).
- `workflow_preferences.confirmed=true` and `workflow_preferences.scaffold_plan` is complete (tech_stack backend/frontend/database, repo_structure[], validation_commands[]).

Non-technical prompting (do not mention JSONPath/fields):
- Confirm roles and "who can do what".
- Even for personal / single-user apps, `roles[]` still needs at least one role (e.g., `user` / `owner`).
- If the user does not care about permissions: explicitly confirm a simple default "everyone can do everything",
  then encode it as one operation row (e.g., `op="all"`, every role=`A`).

## Start / Replan handling

If `docs/prd-pack.json` does not exist (agent-run; workspace root):
1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum prd init`
Then ask: describe the app in 1-3 sentences, plus preferred stack/structure/validation; if none, propose ONE recommended set and ask the user to confirm-or-edit.

If `docs/prd-check-replan-pack.json` exists:
- Treat `items[]` as the current blockers and resolve them first.
- Follow the Output contract: pick either ask-mode (questions only) or write-mode (change summary only).
