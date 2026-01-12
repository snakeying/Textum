# Stage 2c: Scaffold Render (no conversation)

Do one thing only: render `docs/GLOBAL-CONTEXT.md` from the canonical source `docs/scaffold-pack.json`.

Read: `docs/scaffold-pack.json` | Write: `docs/GLOBAL-CONTEXT.md`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum scaffold render`

## Output rule

Output exactly 3 lines:
- `PASS`
- `wrote: docs/GLOBAL-CONTEXT.md`
- `next: Split Plan`
