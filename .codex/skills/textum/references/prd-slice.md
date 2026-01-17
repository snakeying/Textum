# Stage 1d: PRD Slice (generate low-noise slices)

Generate low-noise PRD slices.

Read: `docs/prd-pack.json` | Write: `docs/prd-pack.json` (normalize/ID), `docs/prd-slices/`

## Command

Execute (agent-run; workspace root):

`uv run --project .codex/skills/textum/scripts textum prd slice`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (slice dir; and maybe normalized pack)
  - final line `next: <stage>`
