# 阶段3a: Story 拆分规划

读取 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，先产出 **低噪音** 的拆分规划 `docs/split-plan.md`

## 读取

- `docs/PRD.md`（只读；不修改）
- `docs/GLOBAL-CONTEXT.md`
- （可选）来自 `/split-check` 的 `SPLIT_REPLAN_PACK`（用于重规划：拆分过大的 Story）
- 模板: `.claude/textum/split-plan-template.md`

## 低噪音读取（必须遵守）

- 不要通读整份 PRD；只精读 PRD 的索引章节：`5.1`（模块清单）、`6`（规则表）、`8.1`（表清单含 `TBL-###`）、`9.2`（接口清单含 `API-###`）
- 不要通读整份 GC；默认只读第 4 节业务规则表与第 8 节 API规范（用于拆分口径一致）
- 本阶段不生成 Story 文件，也不补齐 Story 内的 `PRD#<ID>` 引用（只做拆分规划）

## 重规划模式（当提供 `SPLIT_REPLAN_PACK`）

若用户粘贴了 `SPLIT_REPLAN_PACK`，则本次 `/split-plan` 的目标变为：**在尽量小改动的前提下**，把 pack 中标记为过大的 Story 拆分为多个更小的 Story，并更新 `docs/split-plan.md` 使其重新满足门禁。

必须遵守 `SPLIT_REPLAN_PACK.constraints`，并按以下顺序执行：

1. 读取现有 `docs/split-plan.md`（作为唯一事实来源的基线）
2. 从 `SPLIT_REPLAN_PACK.oversized_stories` 逐条取出需要拆分的 Story
3. 对每条过大 Story：
   - 将其拆成 2..N 条新 Story（插入在原 Story 之后；`slug` 必须唯一）
   - 按功能边界/数据边界/API 归属把 `api_assignments_from_split_plan` 分配给拆分后的新 Story（每个 `API-###` 仍必须且仅能归属到 1 个 Story）
   - 更新依赖：原本依赖该 Story 的后续 Story，默认改为依赖“拆分后最后一个 Story”（若用户另有明确依赖口径，则按其口径调整）
4. 重新按 `Story 1..N` 连续编号，并同步更新：
   - 第 1 节 Story 表的 `Story` 与 `前置Story`
   - 第 2 节 API 分配表的 `Story` 引用
5. 自检：确保拆分后的每条 Story 满足阈值（`api_refs`/`tbl_refs`/`feature_points`/`acceptance_items`），否则继续细拆

## 输出（写入文件）

生成 `docs/split-plan.md`，并**严格按** `.claude/textum/split-plan-template.md` 输出（必须包含所有章节与表格；无内容写 `N/A`）。

固定格式要求（必须遵守）：
- 第 1 节 Story 表必须使用模板中的表头：`| Story | slug | 模块 | 目标（一句话） | 前置Story |`
- 第 2 节 API 表必须使用模板中的表头：`| API | Story | 说明 |`
- Story 编号必须写成 `Story N`（N 为数字且从 1 递增，不跳号）
- `slug` 必须唯一（用于后续生成 `docs/story-N-slug.md`）

## 完成后（仅提示下一步动作）

- 用户快速审阅 `docs/split-plan.md`（Story 边界/依赖/API 分配是否合理）
- 然后在新窗口手动运行 `/split` 生成 `docs/story-N-xxx.md` 并补齐 `PRD#<ID>` 引用
- 如本次是重规划：请在新窗口重新运行 `/split-check` 直到 `PASS`

## 开始

请确认已完成 `/scaffold` 并生成 `docs/GLOBAL-CONTEXT.md`。
