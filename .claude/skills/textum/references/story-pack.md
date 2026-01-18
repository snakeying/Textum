# Stage 4b: Story Pack (generate low-noise exec pack)

Generate a low-noise Story Exec Pack for a single story.

Read:
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/story-exec/story-###-<slug>/` (entry: `index.json`)
- `docs/story-pack-replan-pack.json`
- `docs/diagnostics/story-pack.md`

## Command

Ask the user for the story number `n` (e.g. `1`), then execute (agent-run; workspace root):

`uv run --project .claude/skills/textum/scripts textum story pack --n <n>`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `entry: ...` (on PASS)
  - optional `wrote: ...` lines (diagnostics/replan packs)
  - final line `next: <stage>` (fail-fast; computed from artifacts)
