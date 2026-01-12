# Stage 3d: Split Check2 (ref consistency)

Also enforces a completeness gate: split plan `story_count` must match generated story files count.

Read:
- `docs/split-check-index-pack.json`
- `docs/prd-pack.json`
- `docs/scaffold-pack.json`

Write: none

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split check2`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: Split Plan`
- If command prints `PASS`: output:
  - `PASS`
  - `next: Split Checkout`
