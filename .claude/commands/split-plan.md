# 阶段3a: Story 拆分规划（/split-plan）

读取 `docs/PRD.md`（只读）与 `docs/GLOBAL-CONTEXT.md`，生成 `docs/split-plan.md`（规划文件；不生成 Story 文件）。

## 读取 / 写入

- 读取：`docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`
- 可选输入：`SPLIT_REPLAN_PACK`
- 写入：`docs/split-plan.md`
- 模板：`.claude/textum/split-plan-template.md`

## 硬约束

- `N/A_STRICT` 判定口径（必须按此判定）：定位 PRD 小节 `### 9.2 接口清单（必填）` 的正文，去掉空行并 Trim 后仅剩 1 行且该行严格等于 `N/A`
- 只做规划：不生成 `docs/story-*.md`，不补齐 `PRD#<ID>` 引用
- 格式必须可解析：
  - 第 1 节表头：`| Story | slug | 模块 | 目标（一句话） | 前置Story |`
  - 第 2 节表头：`| API | Story | 说明 |`
- 编号必须为 `Story 1..N` 连续；`slug` 必须唯一
- 若 PRD `9.2` 满足 `N/A_STRICT`（无 API）：第 2 节必须只保留表头且无数据行；第 4 节对应自检写 `N/A`
- 否则：PRD `9.2` 的每个 `API-###` 必须在第 2 节出现且仅出现一次（全覆盖 + 唯一归属）
- **阈值预检（仅确定信号；减少重规划）**：只对“每个 Story 分配了多少 API”做预检（按第 2 节计数；不预测 `TBL`/验收/功能点数量）：
  - 计数：`api_assigned(Story N) =` 第 2 节中 `Story N` 对应的 `API-###` 行数
  - 目标：尽量让每个 `api_assigned ≤ 3`
  - 若出现 `api_assigned = 4–5`：允许，但必须在第 4 节自检中给 `DECISION` 并列出这些 Story（避免后续与其它阈值叠加导致重规划）
  - 若出现 `api_assigned ≥ 6`：**不得输出该规划**；必须先拆分/重分配（增加 Story 或调整边界）直到消除（因为后续阈值门禁的 `api_refs ≥ 6` 会必然 `FAIL`）

## 最小读取范围（避免通读）

- PRD：`5.1`（模块清单）、`6`（规则表）、`8.1`（表清单）、`9.2`（接口清单；若 `N/A_STRICT` 则跳过）
- GC：默认只读第 4 节规则表与第 8 节 API规范

## 重规划模式（当提供 `SPLIT_REPLAN_PACK`）

目标：把 pack 标记的过大 Story 拆成更小的 Story，并更新 `docs/split-plan.md` 重新满足门禁。

必须遵守 `SPLIT_REPLAN_PACK.constraints`，并完成：
1. 拆分过大 Story（插入在原 Story 之后；新 `slug` 唯一）
2. 重新分配其 `API-###`（如有；每个 API 仍必须唯一归属）
3. 重编号为连续 `Story 1..N`，同步更新依赖与 API 分配表引用
4. 自检：拆分后的每条 Story 满足阈值；否则继续拆

## 完成后

- 提示用户在新窗口运行 `/split`；若本次为重规划，再提示重新运行 `/split-check1` 与 `/split-check2`
