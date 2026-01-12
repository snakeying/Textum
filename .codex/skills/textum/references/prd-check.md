# Stage 1b: PRD Check (gate on JSON pack)

Read: `docs/prd-pack.json` | Write: none (except auto-assigning IDs when `--fix` is enabled)

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum prd check`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: PRD Plan`
- If command prints `PASS`: output:
  - `PASS`
  - `next: PRD Render`
