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
     1) This-round change summary (JSONPath list; may be empty; no questions)
     2) Remaining blockers (<=8; prioritized)

2) `READY`
   - Output exactly 3 plain-text lines:
     - `READY`
     - `wrote: docs/scaffold-pack.json`
     - `next: Scaffold Check`

- Never output JSON bodies (including `docs/scaffold-pack.json`).

## No conversation

- Do not ask questions in this stage.
- If prerequisites are missing, output blockers with a single-action fix (update `docs/prd-pack.json.workflow_preferences`), then stop.

## Blocking prerequisites

Do not write `docs/scaffold-pack.json` unless all are true:
- `docs/prd-pack.json.workflow_preferences` exists and `workflow_preferences.confirmed=true`
- `workflow_preferences.scaffold_plan` is complete and valid:
  - `tech_stack.backend`, `tech_stack.frontend`, `tech_stack.database` are non-null strings (not `N/A`)
  - `repo_structure[]` is non-empty, each row has concrete `path` and `purpose`
  - `validation_commands[]` is non-empty; each row is either:
    - fully `N/A` (`type/command/note` all `N/A`), OR
    - fully concrete with `type` starting `gate:` or `opt:` (no partial `N/A`)

## Writing rules

- Source of truth for preferences: `docs/prd-pack.json.workflow_preferences.scaffold_plan.*`
- Copy preferences into `docs/scaffold-pack.json` decisions:
  - `$.decisions.tech_stack.*` from `workflow_preferences.scaffold_plan.tech_stack.*`
  - `$.decisions.repo_structure[]` from `workflow_preferences.scaffold_plan.repo_structure[]`
  - `$.decisions.validation_commands[]` from `workflow_preferences.scaffold_plan.validation_commands[]`
- Do not infer/guess decisions beyond the confirmed preferences.
- Do not manually edit `extracted` (it is auto-populated by scripts).
- Hard gate: you MUST NOT output `READY` unless `docs/scaffold-pack.json.decisions` is complete and concrete (no placeholders; no partial `N/A` rows).

## Start / Replan handling

If `docs/scaffold-pack.json` does not exist (agent-run; workspace root):
1) `uv sync --project .claude/skills/textum/scripts`
2) `uv run --project .claude/skills/textum/scripts textum scaffold init`
Then proceed to fill `docs/scaffold-pack.json` from `docs/prd-pack.json.workflow_preferences` (no questions).
 
If `docs/scaffold-check-replan-pack.json` exists:
- Treat `items[]` as the current blockers and resolve them first.
- Follow the Output contract.
