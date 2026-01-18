# Stage 3d: Split Check2 (ref consistency)

Also enforces a completeness gate: split plan `story_count` must match generated story files count.

Read:
- `docs/split-check-index-pack.json`
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`

Write:
- `docs/scaffold-pack.json` (refresh extracted/source if needed)
- `docs/split-check2-replan-pack.json`
- `docs/diagnostics/split-check2.md`

## Command

Execute (agent-run; workspace root):

`uv run --project .claude/skills/textum/scripts textum split check2`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (diagnostics/replan packs; and maybe normalized pack)
  - final line `next: <stage>`
