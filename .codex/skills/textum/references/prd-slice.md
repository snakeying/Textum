# Stage 1d: PRD Slice (generate low-noise slices)

Generate low-noise PRD slices.

Read: `docs/prd-pack.json` | Write: `docs/prd-slices/`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum prd slice`

## Output rule

Output exactly 3 lines:
- `PASS`
- `wrote: docs/prd-slices/`
- `next: Scaffold Plan`
