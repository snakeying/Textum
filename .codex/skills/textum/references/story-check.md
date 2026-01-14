# Stage 4a: Story Check (single-story gate)

Read:
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`
- `docs/stories/story-###-<slug>.json`

Write:
- N/A

## Command

Ask the user for the story number `n` (e.g. `1`), then run (workspace root):

`uv run --project .codex/skills/textum/scripts textum story check --n <n>`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: <stage>` (fail-fast; computed from the `FAIL` list)
- If command prints `PASS`: output:
  - `PASS`
  - `next: Story Pack`
