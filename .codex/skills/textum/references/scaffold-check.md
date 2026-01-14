# Stage 2b: Scaffold Check (gate on JSON scaffold-pack)

Read: `docs/prd-pack.json`, `docs/scaffold-pack.json` | Write: `docs/scaffold-pack.json` (auto-populates `source` and `extracted`)

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum scaffold check`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: Scaffold Plan`
- If command prints `PASS`: output:
  - `PASS`
  - `next: Scaffold Render`
