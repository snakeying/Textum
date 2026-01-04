# 阶段3a: Story 拆分规划（/split-plan）

读取 `docs/PRD.md`（只读）与 `docs/GLOBAL-CONTEXT.md`，生成 `docs/split-plan.md`（规划文件；不生成 Story 文件）。

## 读取 / 写入

- 读取：`docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`
- 可选输入：`SPLIT_REPLAN_PACK`（来自 `/split-check`）
- 写入：`docs/split-plan.md`
- 模板：`.claude/textum/split-plan-template.md`

## 硬约束

- 只做规划：不生成 `docs/story-*.md`，不补齐 `PRD#<ID>` 引用
- 格式必须可解析：
  - 第 1 节表头：`| Story | slug | 模块 | 目标（一句话） | 前置Story |`
  - 第 2 节表头：`| API | Story | 说明 |`
- 编号必须为 `Story 1..N` 连续；`slug` 必须唯一
- 若 PRD `9.2` 为 `N/A`（无 API）：第 2 节必须只保留表头且无数据行；第 6 节对应自检写 `N/A`
- 否则：PRD `9.2` 的每个 `API-###` 必须在第 2 节出现且仅出现一次（全覆盖 + 唯一归属）

## 最小读取范围（避免通读）

- PRD：`5.1`（模块清单）、`6`（规则表）、`8.1`（表清单）、`9.2`（接口清单；如为 `N/A` 则跳过）
- GC：默认只读第 4 节规则表与第 8 节 API规范

## 重规划模式（当提供 `SPLIT_REPLAN_PACK`）

目标：把 pack 标记的过大 Story 拆成更小的 Story，并更新 `docs/split-plan.md` 重新满足门禁。

必须遵守 `SPLIT_REPLAN_PACK.constraints`，并完成：
1. 拆分过大 Story（插入在原 Story 之后；新 `slug` 唯一）
2. 重新分配其 `API-###`（如有；每个 API 仍必须唯一归属）
3. 重编号为连续 `Story 1..N`，同步更新依赖与 API 分配表引用
4. 自检：拆分后的每条 Story 满足阈值；否则继续拆

## 完成后

- 提示用户在新窗口运行 `/split`；若本次为重规划，再提示重新运行 `/split-check`
