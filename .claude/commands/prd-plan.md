# 阶段1a: 需求澄清（边聊边写 YAML plan-pack）

目标：通过多轮对话把“已确认事实”持续写入 `docs/prd-plan-pack.yaml`（唯一事实来源），避免最后才生成 YAML 导致信息丢失/注意力漂移。

## 读取 / 写入

- 读取（如存在）：`docs/prd-plan-pack.yaml`
- 写入（每轮都更新）：`docs/prd-plan-pack.yaml`（纯 YAML；不包含 ```）
- 模板（用于初始化）：`.claude/textum/prd-plan-pack-template.yaml`

## 输入

- 用户需求描述（自由文本），或
- `PRD_PLAN_CLARIFY_PACK`（可选）

## 对话规则（必须遵守）

- 全程中文（必要技术词可用英文）
- 每轮最多提 4 个问题；只问 blockers
- 未确认的信息不得写入 `docs/prd-plan-pack.yaml`；未知必须继续追问
- 每轮输出只包含：本轮问题（或本轮变更摘要）+ 剩余 blockers（最多 8 条）

## 收敛门禁（宣布 READY 前必须满足）

- `project.name`、`project.one_liner` 非空
- `goals` 至少 1 条且非空；`non_goals` 至少 1 条且非空
- `scope.in` / `scope.out` 至少各 1 条且非空
- `roles` 至少 1 个；每个 role 的 `role/description` 非空；`typical_scenarios` 至少 1 条
- `permission_matrix.operations` 至少 1 行；且 `per_role` 的 key 必须是 `roles[].role` 的子集
- `modules` 至少 1 个，且至少 1 个模块 `priority = P0`
- 每个模块：
  - `summary` 非空
  - `feature_points` 至少 1 条；每条 `desc` 非空；`landing` 非空（允许 `N/A`）
  - `scenarios` 至少 1 条；每条 `actor/given/when/then` 非空（`fail_or_edge/note` 可为 `N/A`）
- `business_rules` 至少 1 条且非空；每条 `scope` 非空
- `api.has_api` 必须为布尔值：
  - 若 `api.has_api=false`：`api.endpoints` 必须为空数组；`api.base_url/auth/...` 可为 `N/A`
  - 若 `api.has_api=true`：`api.endpoints` 至少 1 条；每条 `method/path/permission/summary` 非空
- `modules[].feature_points[].landing` 规则（不改写 token）：
  - 允许：`N/A` 或逗号分隔多项集合
  - 每项必须以以下前缀之一开头：`DB:` / `FILE:` / `CFG:` / `EXT:`
  - 若存在 `DB:<table>`：该 `<table>` 必须能在 `data_model.tables[].table` 中找到

## `PRD_PLAN_CLARIFY_PACK` 处理（必须）

当用户粘贴 `PRD_PLAN_CLARIFY_PACK` 时：

1. 只围绕 `blockers` 提问（每轮最多 4 个）
2. 收集答案后，按 `blockers[].path` 回填到 `docs/prd-plan-pack.yaml`（保留其它已确认字段）
3. 输出「本轮变更摘要（路径列表）」+「剩余 blockers」

## 输出状态

- `IN_PROGRESS`：继续提问（不输出 YAML；只更新 `docs/prd-plan-pack.yaml`）
- `READY`：满足收敛门禁；输出：
  - `READY`
  - `已写入：docs/prd-plan-pack.yaml`
  - `下一步：/prd`

## 开始

若 `docs/prd-plan-pack.yaml` 不存在：先按模板初始化后再提问。

请用 1-3 句话描述你要做的应用：给谁用、主要解决什么问题？
