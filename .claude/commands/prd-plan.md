# 阶段1a: 需求澄清（写入 YAML plan-pack）

读取：`docs/prd-plan-pack.yaml`（如存在） | 写入：`docs/prd-plan-pack.yaml`（每轮更新；纯 YAML；不包含 ```） | 模板：`.claude/textum/prd-plan-pack-template.yaml`

目标：把**已确认事实**持续写入 `docs/prd-plan-pack.yaml`（唯一事实来源），直到满足 `READY` 门禁。

## 输出规则（必须遵守）

输出必须二选一（除此之外不要输出任何解释/复述）：

1) `IN_PROGRESS`：
   - 只输出两块内容：
     1) 本轮问题（≤4；只问 blockers）或 本轮变更摘要（YAML 路径列表）
     2) 剩余 blockers（≤8；按优先级）
2) `READY`：
   - 只输出三行纯文本：
     - `READY`
     - `已写入：docs/prd-plan-pack.yaml`
     - `下一步：/prd`

- 不输出 YAML 正文（包括 `docs/prd-plan-pack.yaml` 与 `PRD_PLAN_CLARIFY_PACK`）

## 写入规则（必须遵守）

- 未确认信息不得写入；未知保持为空/空数组
- 仅当用户明确说“无/不适用/没有”时才写 `N/A` 或 `None`
- 不改写用户给出的 token（尤其 `modules[].feature_points[].landing`）

## `PRD_PLAN_CLARIFY_PACK` 处理（必须）

当用户粘贴 `PRD_PLAN_CLARIFY_PACK` 时：

1) 只围绕 `blockers` 提问（≤4）
2) 收集答案后，按 `blockers[].path` 回填到 `docs/prd-plan-pack.yaml`（保留其它已确认字段）
3) 输出「本轮变更摘要（路径列表）」+「剩余 blockers」

## READY 门禁（必填路径清单）

- `project.name`、`project.one_liner` 非空
- `goals[0+]`、`non_goals[0+]`：每条非空
- `scope.in[0+]`、`scope.out[0+]`：每条非空
- `roles[0+]`：每个 role 的 `role/description` 非空；`typical_scenarios[0+]` 且每条非空
- `permission_matrix.operations[0+]`：每行 `op` 非空；`per_role` 至少 1 个 key（key 必须是 `roles[].role` 子集；value 只能是 `A`/`D`/`O`）；`note` 可为 `N/A`
- `modules[0+]`：每个模块 `id/name/summary/priority` 非空；且至少 1 个模块 `priority = P0`
- `modules[].feature_points[0+]`：每条 `fp/desc/landing` 非空（`landing` 允许 `N/A`）
- `modules[].scenarios[0+]`：每条 `actor/given/when/then` 非空（`fail_or_edge/note` 可为 `N/A`）
- `business_rules[0+]`：每条 `id/desc/scope` 非空（`exception_or_note` 可为 `N/A`）
- 稳定 ID：
  - `modules[].id` 必须唯一且符合 `M-01` 格式
  - `modules[].feature_points[].fp` 必须全局唯一且符合 `FP-001` 格式
  - `business_rules[].id` 必须唯一且符合 `BR-001` 格式
- `api.has_api` 必须为布尔值：
  - `false`：`api.endpoints=[]`；`api.base_url/auth/...` 可为 `N/A`
  - `true`：`api.base_url` 非空且不为 `N/A`；`api.auth` 非空且不为 `N/A`（无认证写 `None`）；`api.endpoints[0+]` 且每条 `method/path/permission/summary` 非空
- `modules[].feature_points[].landing` 合法性（不改写 token）：
  - 允许：`N/A` 或逗号分隔多项集合
  - 每项必须以 `DB:` / `FILE:` / `CFG:` / `EXT:` 之一开头
  - 若出现 `DB:<table>`：该 `<table>` 必须能在 `data_model.tables[].table` 中找到

## 可选记录（不主动追问）

- 若用户**明确**提出命名/格式约定：写入 `assumptions_constraints[]`，并让 `assumption_or_constraint` 以 `命名规范:` 开头

## 开始

若 `docs/prd-plan-pack.yaml` 不存在：先按模板初始化后再提问。

请用 1-3 句话描述你要做的应用：给谁用、主要解决什么问题？
