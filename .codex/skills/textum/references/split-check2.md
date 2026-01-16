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

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split check2`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - optional `wrote: ...` lines (diagnostics/replan packs; and maybe normalized pack)
  - final line `next: <stage>`
