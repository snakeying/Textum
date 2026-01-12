# Stage 3e: Split Checkout (export dependency graph)

Read:
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/story-mermaid.md`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split checkout`

## Output rule

- If command prints `FAIL`: output the `FAIL` list as-is, then one line: `next: Split Generate`
- If command prints `PASS`: output:
  - `PASS`
  - `next: Story Check`

