# 阶段3: Story 拆分（/split）

读取 `docs/split-plan.md`（规划唯一事实来源）并结合 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，按模板 `.claude/textum/story-template.md` 生成 `docs/story-N-<slug>.md`。

## 读取 / 写入

- 读取：`docs/split-plan.md`、`docs/PRD.md`（只读）、`docs/GLOBAL-CONTEXT.md`
- 写入：`docs/story-*-*.md`
- 模板：`.claude/textum/story-template.md`

## 最小读取范围（避免通读）

- split-plan：全量（用于 Story 边界 / 模块 / 前置Story / API 分配）
- GC：仅第 4 节业务规则表（用于挑选可用 `GC#BR-###`）
- PRD：
  - `5.2 功能规格`：按模块抽取 `FP-xx` 与功能点描述（用于 Story 的 FP 分配与“功能点”章节）
  - `6. 业务规则`：按需抽取可引用的 `BR-###`（仅当需要 `PRD#BR-###`）
  - `8.0 功能点→落点映射`：用于把 `FP-xx` 映射到本 Story 必须声明的 `PRD#TBL-###` / `ART:*`
  - `8.1 表清单`：用于校验/选择可用 `TBL-###`（如适用）
  - `9.2 接口清单`：仅用于确认接口 ID 集合（Story 的 `PRD#API-###` 来自 split-plan 分配）

## 硬约束

- 不得更改 `docs/split-plan.md` 的 Story 编号/边界/API 分配：若发现不合理则停止并提示回 `/split-plan`
- Story 内引用 PRD 必须使用 `PRD#<ID>` 且为具体数字：`PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`
- 模板章节不得缺失；无内容写 `N/A`；不得残留占位符（如 `[功能描述]`、`M-xx`、`GC#BR-###`、`PRD#API-###`）
- 若 split-plan 第 2 节无任何 API 行（无 API）：所有 Story 的“接口”章节必须写 `N/A` 且不得出现 `PRD#API-###`

## 执行步骤（必须按序）

1. 解析 `docs/split-plan.md`：得到 `Story N` 列表与 `API-### -> Story N` 分配
2. 逐个 Story 生成 1 个文件：`docs/story-N-<slug>.md`
3. 严格按模板填充：
   - `模块（必填）`、`前置Story` 与 split-plan 一致
   - `关联功能点（必填）`：填写本 Story 覆盖的 `FP-xx`（必须是 PRD 中存在的具体数字；逗号分隔）
   - `## 功能点`：每条必须为 `- FP-xx: ...`，且该章节出现的 `FP-xx` 去重集合必须与“关联功能点”一致
   - “接口”章节：若分配了 `API-###`，列出对应 `PRD#API-###`；若未分配任何 API，则写 `N/A`
   - “数据/产物落点/业务规则”按需列出 `PRD#TBL-###`、`ART:FILE/CFG/EXT:*`、`GC#BR-###`、`PRD#BR-###`
     - `ART:*` token 规范：`ART:FILE:<path>` / `ART:CFG:<key>` / `ART:EXT:<system>`（token 后用空格或 ` - ` 接说明；不要把额外的冒号/括号塞进 token）
4. 生成后占位符自检（必须；必须在本命令内修正）：
   - 对每个 `docs/story-N-<slug>.md` 逐行扫描（忽略 fenced code blocks），确保不存在任何模板占位符残留，至少包括：
     - `[...]`、`[功能描述]`、`[规则摘要]`、`[接口名称]` 等方括号占位符
     - `Story [编号]` / `[功能名称]`
     - `FP-xx` / `FP-yy`
      - `M-xx` / `M-yy`
      - `GC#BR-###`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`
     - `ART:FILE:[path_glob]` / `ART:CFG:[key]` / `ART:EXT:[system]`
   - 若命中任一项：必须立即在对应 Story 文件中修正并再次自检，直到全量通过
5. 结构自检：Story 编号可执行（前置编号 < 当前编号）；文件名与 split-plan 1:1 对应；无重复编号

## 完成后

- 提示用户在新窗口运行 `/split-check1`，`PASS` 后再运行 `/split-check2`
