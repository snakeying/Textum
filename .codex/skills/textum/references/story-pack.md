# Stage 4b: Story Pack (generate low-noise exec pack)

Generate a low-noise Story Exec Pack for a single story.

Read:
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/story-exec/story-###-<slug>/` (entry: `index.json`)

## Command

Ask the user for the story number `n` (e.g. `1`), then run (workspace root):

`uv run --project .codex/skills/textum/scripts textum story pack --n <n>`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: <stage>` (fail-fast; computed from the `FAIL` list)
- If command prints `PASS`: output:
  - `PASS`
  - `entry: docs/story-exec/story-###-<slug>/index.json`
  - `next: Story Exec`
