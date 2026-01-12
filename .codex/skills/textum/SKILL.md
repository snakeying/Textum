---
name: textum
description: Textum PRD→Scaffold→Story workflow for Codex with low-noise outputs and gate checks (支持中文意图：需求澄清/生成PRD/校验PRD/上下文提取).
---

# Textum (skills-first)

Hard constraints:
- Low-noise is non-negotiable (avoid attention/context pollution).
- Multi-window: each stage is self-contained; do not narrate upstream/downstream flow.
- Output “next step” as a stage name only.

Prereq (runtime):
- `uv` installed.
- Run `uv sync --project .codex/skills/textum/scripts` once (creates `.codex/skills/textum/scripts/.venv`).

Supported stages:
- PRD Plan → `references/prd-plan.md`
- PRD Render → `references/prd.md`
- PRD Check → `references/prd-check.md`
- Scaffold Plan → `references/scaffold-plan.md`
- Scaffold Render → `references/scaffold.md`
- Scaffold Check → `references/scaffold-check.md`
- Split Plan → `references/split-plan.md`
- Split Generate → `references/split.md`
- Split Check1 → `references/split-check1.md`
- Split Check2 → `references/split-check2.md`

Routing:
- CN intent examples:
  - `PRD Plan`: 需求澄清 / 澄清需求 / PRD 计划
  - `PRD Render`: 生成PRD / 渲染PRD / 输出PRD
  - `PRD Check`: 校验PRD / 检查PRD / 门禁
  - `Scaffold Plan`: 上下文提取 / 全局上下文 / Scaffold 计划
  - `Scaffold Render`: 生成GLOBAL-CONTEXT / 渲染GLOBAL-CONTEXT / 输出GLOBAL-CONTEXT
  - `Scaffold Check`: 校验GLOBAL-CONTEXT / 检查GLOBAL-CONTEXT / GC 门禁
  - `Split Plan`: Story 拆分规划 / Split Plan / 拆分计划
  - `Split Generate`: 生成Story / Split Generate / 拆分生成
  - `Split Check1`: Split 校验1 / 拆分校验1 / 结构阈值校验
  - `Split Check2`: Split 校验2 / 拆分校验2 / 引用一致性校验
- If intent is unclear, ask the user to pick one: `PRD Plan` / `PRD Render` / `PRD Check` / `Scaffold Plan` / `Scaffold Render` / `Scaffold Check` / `Split Plan` / `Split Generate` / `Split Check1` / `Split Check2`.
- If the user asks for non-supported stages (story), reply `NOT_SUPPORTED` (one line) and ask them to wait for the next bundle.

Always:
- For every `FAIL` item: include `loc/problem/expected/impact/fix`, and `fix` must be a single action.
