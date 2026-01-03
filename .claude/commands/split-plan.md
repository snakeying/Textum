# 阶段3a: Story 拆分规划

读取 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，先产出 **低噪音** 的拆分规划 `docs/split-plan.md`

## 读取

- `docs/PRD.md`（只读；不修改）
- `docs/GLOBAL-CONTEXT.md`
- 模板: `.claude/textum/split-plan-template-v1.md`

## 低噪音读取（必须遵守）

- 不要通读整份 PRD；只精读 PRD 的索引章节：`5.1`（模块清单）、`6`（规则表）、`8.1`（表清单含 `TBL-###`）、`9.2`（接口清单含 `API-###`）
- 不要通读整份 GC；默认只读第 4 节业务规则表与第 8 节 API规范（用于拆分口径一致）
- 本阶段不生成 Story 文件，也不补齐 Story 内的 `PRD#<ID>` 引用（只做拆分规划）

## 输出（写入文件）

生成 `docs/split-plan.md`，并**严格按** `.claude/textum/split-plan-template-v1.md` 输出（必须包含所有章节与表格；无内容写 `N/A`）。

固定格式要求（必须遵守）：
- 第 1 节 Story 表必须使用模板中的表头：`| Story | slug | 模块 | 目标（一句话） | 前置Story |`
- 第 2 节 API 表必须使用模板中的表头：`| API | Story | 说明 |`
- Story 编号必须写成 `Story N`（N 为数字且从 1 递增，不跳号）
- `slug` 必须唯一（用于后续生成 `docs/story-N-slug.md`）

## 完成后（仅提示下一步动作）

- 用户快速审阅 `docs/split-plan.md`（Story 边界/依赖/API 分配是否合理）
- 然后在新窗口手动运行 `/split` 生成 `docs/story-N-xxx.md` 并补齐 `PRD#<ID>` 引用

## 开始

请确认已完成 `/scaffold` 并生成 `docs/GLOBAL-CONTEXT.md`。
