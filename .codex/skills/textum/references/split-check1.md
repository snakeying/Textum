# Stage 3c: Split Check1 (core gate + index pack)

Read:
- `docs/split-plan-pack.json`
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/split-check-index-pack.json` (only when no FAIL)
- `docs/split-replan-pack.json` (only when FAIL due to oversized story)

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split check1`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then (if present) one line `wrote: docs/split-replan-pack.json`, then one line: `next: Split Plan`
- If command prints `DECISION`: output `DECISION` list as-is, then one line: `next: Split Check2`
- If command prints `PASS`: output:
  - `PASS`
  - `next: Split Check2`
