# Stage 2c: Scaffold Render (no conversation)

Do one thing only: render `docs/GLOBAL-CONTEXT.md` from the canonical source `docs/scaffold-pack.json`.

Read: `docs/scaffold-pack.json` | Write: `docs/GLOBAL-CONTEXT.md`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum scaffold render`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: Scaffold Plan`
- If command prints `PASS`: output:
  - `PASS`
  - `wrote: docs/GLOBAL-CONTEXT.md`
  - `next: Split Plan`
