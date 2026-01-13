# Stage 1d: PRD Slice (generate low-noise slices)

Generate low-noise PRD slices.

Read: `docs/prd-pack.json` | Write: `docs/prd-slices/`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum prd slice`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: PRD Plan`
- If command prints `PASS`: output:
  - `PASS`
  - `wrote: docs/prd-slices/`
  - `next: Scaffold Plan`
