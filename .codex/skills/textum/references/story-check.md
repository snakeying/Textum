# Stage 4a: Story Check (single-story gate)

Read:
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/story-check-replan-pack.json`
- `docs/diagnostics/story-check.md`

## Command

Ask the user for the story number `n` (e.g. `1`), then run (workspace root):

`uv run --project .codex/skills/textum/scripts textum story check --n <n>`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (diagnostics/replan packs)
  - final line `next: <stage>` (fail-fast; computed from artifacts)
