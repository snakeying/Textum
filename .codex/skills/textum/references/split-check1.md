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

Execute (agent-run; workspace root):

`uv run --project .codex/skills/textum/scripts textum split check1`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - on `PASS` with warnings: one-line `WARN` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (diagnostics/replan packs)
  - final line `next: <stage>`

Note:
- `WARN` items (threshold) are non-blocking by default; you can ignore them unless you want to reduce iteration cost.
- `--strict` is a CLI flag for `textum split check1` (not a stage suffix). Example:
  - `uv run --project .codex/skills/textum/scripts textum split check1 --strict`
