# Stage 2c: Scaffold Render (no conversation)

Do one thing only: render `docs/GLOBAL-CONTEXT.md` from the canonical source `docs/scaffold-pack.json`.

Read: `docs/scaffold-pack.json` | Write: `docs/GLOBAL-CONTEXT.md`

## Command

Execute (agent-run; workspace root):

`uv run --project .codex/skills/textum/scripts textum scaffold render`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (rendered GLOBAL-CONTEXT.md; and maybe normalized pack)
  - final line `next: <stage>`
