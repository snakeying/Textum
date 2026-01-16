# Stage 4d: Story Full Exec (experimental, batch)

- `$ARGUMENTS`: story number list in `n1/n2/...` form (example: `1/2/3`)

Read:
- For each `n`: `docs/story-exec/story-###-<slug>/index.json` + its `read[]` files (only)

Write:
- Repo code/tests for multiple stories (in input order)

## Input parsing (must follow)

- `$ARGUMENTS` must match: `<n1>/<n2>/...` (positive integers, `/` only, no spaces)
- Split by `/`, keep order, de-duplicate (keep first occurrence)
- If parsing fails or list is empty: output a `FAIL` list (exactly 1 item; `loc/problem/expected/impact/fix`; `fix` is one action), then `next: N/A`, and stop (do not execute any story)

## Pre-check (fail-fast)

For each `n` in order:
- Ensure the exec pack exists; if missing, output `FAIL` list + `next: Story Pack` and stop

## Execution rules (continue; no rollback)

For each `n` in order:
1) Execute the story using only its exec pack:
   - Do not read PRD/Scaffold/story sources outside the exec pack.
   - Do not invent new APIs/tables/fields not present in the exec pack.
   - If the exec pack is missing/inconsistent/not executable: mark `Story <n>` as `FAIL` and continue.
2) Run validation commands once each (no retries):
   - Run all runnable `gate:*` first, then `opt:*`.
   - If any `gate:*` fails or acceptance is not met: mark `Story <n>` as `FAIL` but continue to next `n`.

## Output (one-time summary; low-noise)

- Summary:
  - If any story failed: output `FAIL`
  - Else: output `PASS`
- Per-story status (1 line each):
  - `Story <n>: PASS` or `Story <n>: FAIL`
- If any failures: output a `FAIL` list (each item must include `loc/problem/expected/impact/fix`; `fix` is one action)
- Final line: `next: N/A`
