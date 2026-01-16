# Stage 3c: Split Check1 (core gate + index pack)

Read:
- `docs/split-plan-pack.json`
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/split-check-index-pack.json` (only when no FAIL)
- `docs/split-replan-pack.json` (only when oversized stories exist)
- `docs/split-check1-replan-pack.json`
- `docs/diagnostics/split-check1.md`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split check1`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - optional `wrote: ...` lines (diagnostics/replan packs)
  - final line `next: <stage>`
