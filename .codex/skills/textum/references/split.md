# Stage 3b: Split Generate (no conversation)

Generate per-story JSON files from `docs/split-plan-pack.json` + `docs/prd-pack.json`.

Read:
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`
- `docs/split-plan-pack.json`

Write:
- `docs/stories/story-###-<slug>.json`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split generate`

## Output rule

Output exactly 3 lines:
- `PASS`
- `wrote: docs/stories/`
- `next: Split Check1`

