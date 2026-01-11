---
name: textum
description: Textum PRD→Story workflow for Claude with low-noise outputs and gate checks. Use when users want to start requirement planning, generate/validate a PRD, extract GLOBAL-CONTEXT, split into Stories, validate splits, build Story exec packs, or execute a Story.
---

# PRD→Story 工作流（低噪+门禁）

目标：使用一套“低噪 + 门禁校验 + 交接包”的 PRD→Story 工作流，避免发明规则与上下文污染。

## 交互约定（低噪）

- 用户用自然语言表达意图即可（例如：开始计划/生成PRD/校验/拆分/执行Story）。
- 若意图不明确：只给 3–6 个阶段选项让用户选择，再继续；不要长解释。
- 建议每个阶段在新会话执行；仅当 `check` 输出 `FAIL` 时，把清单带回对应“生成阶段”修复后重跑。
- 输出中的“下一步/重跑/修正”只写阶段名（例如：`PRD 生成/修正`、`PRD 校验`、`Split 规划`）。

## 阶段路由（只选一）

根据用户意图选择阶段，并打开对应引用文件，严格按其中的“读取/写入/输出规则/门禁”执行：

### 默认入口（无明确意图）

若用户未表达明确阶段意图：先问“当前处于哪个状态？”并只给 3–6 个选项（不解释）：

- 还没开始 → 需求澄清（plan）
- 已有想法 → PRD 生成/修正
- 已有 PRD → PRD 校验
- 已拆分 Story → Story 校验

- 需求澄清（plan）→ `references/prd-plan.md`
- PRD 生成/修正 → `references/prd.md`
- PRD 校验 → `references/prd-check.md`
- GLOBAL-CONTEXT 生成 → `references/scaffold.md`
- GLOBAL-CONTEXT 校验 → `references/scaffold-check.md`
- Split 规划 → `references/split-plan.md`
- Split 生成 Story → `references/split.md`
- Split 校验（结构/阈值）→ `references/split-check1.md`
- Split 校验（引用追溯/API Smoke）→ `references/split-check2.md`
- 导出依赖图 → `references/split-checkout.md`
- Story 校验 → `references/story-check.md`
- Story 执行包生成 → `references/story-pack.md`
- Story 执行 → `references/story.md`
- Story 批量执行（实验）→ `references/story-full-exec.md`

## 始终硬约束

- 低噪是硬约束：除必须的清单/交接包外，不输出复述与长文。
- 所有 `FAIL` 清单条目必须包含：`定位/问题/期望/影响/修复`，且 `修复` 只给 1 个动作。
- 所有 `DECISION` 清单条目必须包含：`定位/问题/影响/建议动作`，且 `建议动作` 只给 1 个动作。
