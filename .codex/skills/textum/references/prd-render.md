# Stage 1c: PRD Render (acceptance view; no conversation)

Do one thing only: render `docs/PRD.md` from the canonical source `docs/prd-pack.json`.

Read: `docs/prd-pack.json` | Write: `docs/PRD.md` | Template: N/A (script renderer)

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum prd render`

## Output rule

Output exactly 3 lines:
- `PASS`
- `wrote: docs/PRD.md`
- `next: PRD Slice`
