# Stage 3e: Split Checkout (export dependency graph)

Read:
- `docs/stories/story-###-<slug>.json`

Write:
- `docs/story-mermaid.md`
- `docs/split-checkout-replan-pack.json`
- `docs/diagnostics/split-checkout.md`

## Command

Run (workspace root):

`uv run --project .codex/skills/textum/scripts textum split checkout`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (dependency graph, diagnostics/replan packs)
  - final line `next: <stage>`
