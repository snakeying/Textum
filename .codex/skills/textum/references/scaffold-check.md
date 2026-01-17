# Stage 2b: Scaffold Check (gate on JSON scaffold-pack)

Read: `docs/prd-pack.json`, `docs/scaffold-pack.json`

Write:
- `docs/scaffold-pack.json` (auto-populates `source` and `extracted`)
- `docs/scaffold-check-replan-pack.json`
- `docs/diagnostics/scaffold-check.md`

## Command

Execute (agent-run; workspace root):

`uv run --project .codex/skills/textum/scripts textum scaffold check`

## Output rule

- Output the command output as-is (low-noise).
- The command always prints:
  - `PASS` or `FAIL`
  - on `FAIL`: one-line `FAIL` items (`loc/problem/expected/impact/fix`)
  - optional `wrote: ...` lines (diagnostics/replan packs; and maybe normalized pack)
  - final line `next: <stage>`
