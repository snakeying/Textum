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
- Treat `context.base.json:repo_structure[]` as guidance, not mandatory output; only create/modify files you need for this story (and any files required by `validation_commands`).
- Write raw code into repo files; do not copy JSON-escaped strings into source (e.g., never leave `\\\"` in Python code). Prefer single quotes when practical to avoid escaping.

## Steps

1) Preconditions:
   - If `docs/story-exec/.../index.json` is missing, or any file in `index.json.read[]` is missing/unreadable: output a `FAIL` list (`loc/problem/expected/impact/fix`; `fix` is one action), then `next: Story Pack`, and stop.
2) Load context:
   - Load `index.json`, then load each file in `read[]` (in order).
3) Implement (minimal):
   - Only implement what the exec pack lists as this story’s `feature_points` and `api_endpoints`.
   - Keep repo reads minimal; do not create placeholder files you won't touch.
4) Verify:
   - If `context.base.json.validation_commands[]` has runnable commands (`type` startswith `gate:` or `opt:` and `command != N/A`), run all `gate:*` first, then `opt:*` once.
   - If no runnable `gate:*` exists: state `gate:*: N/A` and rely on acceptance/self-check only.
   - If any `gate:*` fails: apply the smallest possible fix, then rerun the failing `gate:*` until PASS.
   - If `gate:compile` reports `SyntaxError: unexpected character after line continuation character`, check for stray backslashes before quotes (e.g., `f\\\"{...}\\\"`) and remove them.

## Output (low-noise)

- `Status (FP/API)`: for each `FP-###` and `API-###` -> `DONE` / `NOT_DONE`
- `Key Changes`: only "file path + 1-line change"
- `Verification`: each executed command -> `PASS/FAIL` (or `gate:*: N/A`)
- Final line: `next: N/A` (except precondition failure: output `FAIL` list + `next: Story Pack` and stop)
