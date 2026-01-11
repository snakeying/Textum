# 阶段 1a: PRD 需求澄清（写入 JSON prd-pack）

读取：`docs/prd-pack.json`（如存在） | 写入：`docs/prd-pack.json`（每轮更新；纯 JSON；不包含 ```） | 初始化：`uv run --project .codex/skills/textum/scripts textum prd init`

目标：把**已确认事实**持续写入 `docs/prd-pack.json`（唯一事实来源），直到满足 `READY` 门禁。

## 输出规则（必须遵守）

输出必须二选一（除此之外不要输出任何解释/复述）：

1) `IN_PROGRESS`：
   - 只输出两块内容：
     1) 本轮问题（≤4；只问 blockers）或 本轮变更摘要（JSONPath 列表）
     2) 剩余 blockers（≤8；按优先级）
2) `READY`：
   - 只输出三行纯文本：
     - `READY`
     - `已写入：docs/prd-pack.json`
     - `下一步：PRD Render`

- 不输出 JSON 正文（包括 `docs/prd-pack.json`）

## 写入规则（必须遵守）

- 未确认信息不得写入；未知保持为空/空数组/`null`
- 仅当用户明确说“无/不适用/没有”时才写 `N/A`（或 `null`，以 schema 允许为准）
- 不改写用户给出的 token（尤其 `modules[].feature_points[].landing[]`）
- **不要维护编号**：所有 `*.id` 允许为 `null`；编号/唯一性/连续性由脚本自动分配与门禁校验

## READY 门禁（唯一口径）

每轮写入后运行（在项目根目录）：

`uv run --project .codex/skills/textum/scripts textum prd check`

当且仅当输出为 `PASS` 时，才可以输出 `READY`。

## 开始

若 `docs/prd-pack.json` 不存在：先执行一次初始化（在项目根目录）：

1) `uv sync --project .codex/skills/textum/scripts`
2) `uv run --project .codex/skills/textum/scripts textum prd init`

然后开始提问：请用 1-3 句话描述你要做的应用：给谁用、主要解决什么问题？
