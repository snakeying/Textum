# 阶段3a: Story 拆分规划（/split-plan）

读取：`docs/PRD.md`（只读） | 写入：`docs/split-plan.yaml`（纯 YAML；不包含 ```） | 模板：`.claude/textum/split-plan-template.yaml` | 可选输入：`SPLIT_REPLAN_PACK`

生成 split-plan 规划 pack；不生成 Story 文件。

## 最小读取范围（必须；避免通读）

- PRD：`5.1 功能清单`、`9.2 接口清单（必填）`

## 硬约束（必须遵守）

`N/A_STRICT` 判定口径（权威；逐字一致；禁止改写）：
- 定位 PRD 小节 `### 9.2 接口清单（必填）` 的正文（标题行之后到下一同级小节标题之前）
- 判定 `N/A_STRICT = true` 当且仅当：正文去掉空行并 Trim 后仅剩 1 行且该行严格等于 `N/A`

- 只做规划：不生成任何 Story 文件（不写入 `docs/story-*-*.md`）
- 输出必须严格按 `.claude/textum/split-plan-template.yaml` 的 YAML 结构（字段齐全；不得额外加 Markdown 文本；不得额外加键）
- `docs/split-plan.yaml` 中不得出现 `TBD`
- 编号必须为 `Story 1..N` 连续：
  - `stories[].n` 连续，且 `stories[].story == "Story {n}"`
  - `stories[].slug` 必须唯一且符合 `kebab-case`
- `stories[].modules` 必须为 `M-xx` 数组；不得写模块名
- `stories[].prereq_stories` 必须为 `["Story 1", ...]` 数组（无依赖则空数组）；且必须可执行（仅允许依赖更小编号）
- `stories[].goal` 必须非空（不得为 `TBD`）

### 模块有效性与 P0 覆盖（本阶段必须做；减少下游失败）

从 PRD `5.1 功能清单` 抽取：
- `P0_modules =` 所有 `priority == P0` 的 `M-xx` 集合
- `All_modules =` PRD 中出现的全部 `M-xx` 集合

校验（任一不满足即必须在本命令内修正后再写文件）：
- 对每个 Story 的 `modules[]`：每个 `M-xx` 必须属于 `All_modules`
- 对 `All_modules` 中每个 `M-xx`：必须至少出现在 1 个 Story 的 `modules[]`
- 对 `P0_modules` 中每个 `M-xx`：必须至少出现在 1 个 Story 的 `modules[]`

### API 分配（如适用）

先按 `N/A_STRICT` 判断 PRD 是否无 API：
- 若 `N/A_STRICT = true`：`PRD_HAS_API = false`
- 否则：`PRD_HAS_API = true`，并从 PRD `9.2` 抽取 `P_api = {API-###}` 集合

若 `PRD_HAS_API = false`：
- `api_assignments` 必须为空数组

若 `PRD_HAS_API = true`：
- 覆盖 + 唯一归属：
  - 对 `P_api` 中每个 `API-###`：必须在 `api_assignments[].api` 中出现且仅出现 1 次
  - `api_assignments[].story` 必须引用 `stories[].story` 中存在的 Story

### 阈值预检（仅确定信号；减少重规划）

仅对“每个 Story 分配了多少 API”做预检（按 `api_assignments` 计数；不预测 `TBL`/验收/功能点数量）：
- `api_assigned(Story N) =` `api_assignments` 中 `story == "Story N"` 的行数
- 目标：尽量让每个 `api_assigned ≤ 3`
- 若出现 `api_assigned = 4–5`：允许写入，但输出 `DECISION` 清单（见“输出规则”）
- 若出现 `api_assigned ≥ 6`：不得写入；必须先拆分/重分配（增加 Story 或调整边界）直到消除

## 重规划模式（当提供 `SPLIT_REPLAN_PACK`）

目标：把 pack 标记的过大 Story 拆成更小的 Story，并更新 `docs/split-plan.yaml` 重新满足门禁。

必须遵守 `SPLIT_REPLAN_PACK.constraints`，并完成：
1. 拆分过大 Story（插入在原 Story 之后；新 `slug` 唯一）
2. 重新分配其 `API-###`（如有；每个 API 仍必须唯一归属）
3. 重编号为连续 `Story 1..N`，同步更新 `stories[]` 与 `api_assignments[]` 的引用
4. 自检：拆分后的每条 Story 满足阈值；否则继续拆

## 输出规则

- 始终写入 `docs/split-plan.yaml`（前提：已满足全部硬约束）
- 若存在任一 Story 命中 `api_assigned = 4–5`：
  - 输出 `DECISION` 清单（`D-001` 起编号；每条包含：Story + `api_assigned` + 建议动作）
  - 末尾追加：
    - `已写入：docs/split-plan.yaml`
    - `接受 DECISION：/split`
    - `不接受 DECISION：先调整 split-plan 后重跑 /split-plan`
- 否则输出：
  - `PASS`
  - `已写入：docs/split-plan.yaml`
  - `下一步：/split`
