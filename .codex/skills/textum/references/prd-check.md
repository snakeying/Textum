# Stage 1b: PRD Check (gate on JSON pack)

Read: `docs/prd-pack.json`

Write:
- `docs/prd-pack.json` (normalize/ID)
- `docs/prd-check-replan-pack.json`
- `docs/diagnostics/prd-check.md`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum prd check`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (diagnostics/replan packs; and maybe normalized pack)
  - final line `next: <stage>`
