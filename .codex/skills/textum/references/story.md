# Stage 4c: Story Exec (single story)

- `$ARGUMENTS`: story number `n` (e.g. `1`)

Read:
- `docs/story-exec/story-###-<slug>/index.json` (entry)
- Then read the files listed in `index.json.read[]` (context only; in order)
- Read repo code files as needed to implement this story (keep reads minimal)

Write:
- Repo code/tests for this story only

## Hard constraints

- The exec pack is the only source of truth for requirements/context. Do not use PRD/Scaffold/story sources outside the exec pack.
- Do not invent new APIs/tables/fields not present in the exec pack.
- Treat `context.base.json:repo_structure[]` as guidance, not mandatory output; only create/modify the files you need for this story (and any files required by `validation_commands`).
- If the exec pack is missing/inconsistent/not executable: stop and output a `FAIL` list (each item must include `loc/problem/expected/impact/fix`; `fix` is one action).

## Steps

1) Ensure exec pack exists:
   - If missing: stop and output a `FAIL` list (each item must include `loc/problem/expected/impact/fix`; `fix` is one action), then one line: `next: Story Pack`
2) Load `index.json`, then load each file in `read[]`.
3) Bootstrap (minimal):
   - Ensure the parent directories exist for any files you will write in this story.
   - Do not create placeholder files you won't touch in this story.
4) Implement minimal changes to satisfy all `feature_points` and `api_endpoints` in `story.json`.
5) Verification:
   - If `context.base.json.validation_commands[]` has runnable commands (`type` startswith `gate:` or `opt:` and `command != N/A`), run all `gate:*` first (must pass), then run `opt:*` once.
   - If no runnable `gate:*` exists: state `gate:*: N/A` and rely on acceptance/self-check only.

## Output (low-noise)

- `Status (FP/API)`:
  - For each `FP-###`: `DONE` / `NOT_DONE`
  - For each `API-###`: `DONE` / `NOT_DONE`
- `Key Changes`: only "file path + 1-line change"
- `Verification`: each executed command -> `PASS/FAIL`
- `Next`: `N/A` (if preconditions fail: output `FAIL` list + `next:` and stop)
