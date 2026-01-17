# Stage 1c: PRD Render (acceptance view; no conversation)

Do one thing only: render `docs/PRD.md` from the canonical source `docs/prd-pack.json`.

Read: `docs/prd-pack.json` | Write: `docs/prd-pack.json` (normalize/ID), `docs/PRD.md` | Template: N/A (script renderer)

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum prd render`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (rendered PRD.md; and maybe normalized pack)
  - final line `next: <stage>`
