# Stage 3b: Split Generate (no conversation)

Generate per-story JSON files from `docs/split-plan-pack.json` + `docs/prd-pack.json`.

Read:
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`
- `docs/split-plan-pack.json`

Write:
- `docs/stories/story-###-<slug>.json`

## Command

Execute (agent-run; workspace root):

`uv run --project .claude/skills/textum/scripts textum split generate`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (generated stories; and maybe normalized packs)
  - final line `next: <stage>`
