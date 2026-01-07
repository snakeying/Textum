# 阶段3: Story 拆分（/split）

读取 `docs/split-plan.yaml`（规划唯一事实来源）并结合 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，按模板 `.claude/textum/story-template.md` 生成 `docs/story-N-<slug>.md`。

## 最小读取范围（必须；避免通读）

- split-plan：全量（用于 Story 边界 / 模块 / 依赖 / API 分配）
- GC：仅第 4 节业务规则表（用于挑选可用 `BR-###` 写入 `refs.gc_br`）
- PRD：
  - `5.2 功能规格`：按模块抽取 `FP-001` 与功能点描述（用于 Story 的 FP 分配与“功能点”章节）
  - `6. 业务规则`：按需抽取可引用的 `BR-###`（仅当需要 `PRD#BR-###`）
  - `8.0 功能点→落点映射`：用于把 `FP-001` 映射到本 Story 必须声明的 `refs.prd_tbl[]` / `artifacts.*[]`
  - `8.1 表清单`：用于校验/选择可用 `TBL-###`（如适用）
  - `9.2 接口清单`：仅用于确认接口 ID 集合（Story 的 `refs.prd_api` 来自 split-plan 分配）

## 读取 / 写入

- 读取：`docs/split-plan.yaml`、`docs/PRD.md`（只读）、`docs/GLOBAL-CONTEXT.md`
- 写入：`docs/story-*-*.md`
- 模板：`.claude/textum/story-template.md`

## 硬约束

- 不得更改 `docs/split-plan.yaml` 的 Story 编号/边界/API 分配：若发现不合理则停止并提示回 `/split-plan`
- 每个 Story 文件必须包含 **YAML front-matter**（文件首部 `--- ... ---`），且字段齐全、可解析（结构以模板为准）
- YAML front-matter 中所有 ID 必须为具体数字：
  - `modules[]`: `M-01`
  - `fp_ids[]`: `FP-001`
  - `refs.gc_br[]` / `refs.prd_br[]`: `BR-001`
  - `refs.prd_tbl[]`: `TBL-001`
  - `refs.prd_api[]`: `API-001`
- Story 模板章节不得缺失；无内容写 `N/A`；不得残留占位符（如 `[功能描述]`、`M-xx`、`FP-###`、`Story N`）
- 若 `docs/split-plan.yaml` 的 `api_assignments` 为空（无 API）：
  - 每个 Story front-matter `refs.prd_api` 必须为空数组
  - 每个 Story 的 `## 接口` 章节正文必须严格为 1 行 `N/A`

## 执行步骤（必须按序）

1. 解析 `docs/split-plan.yaml`：得到 `stories[]` 与 `api_assignments[]`
2. 逐个 Story 生成 1 个文件：`docs/story-N-<slug>.md`
3. 严格按模板填充：
   - 先填 YAML front-matter：
     - `story/n/slug/title` 与文件名一致
     - `modules/prereq_stories` 与 split-plan 一致
     - `fp_ids`：为本 Story 分配的 `FP-001`（必须能在 PRD `8.0` 中定位）
     - `refs`：填写 `gc_br/prd_br/prd_tbl/prd_api`（ID 列表；不带 `GC#`/`PRD#` 前缀）
     - `artifacts`：
       - `artifacts.file[]`：`ART:FILE:<path>` token（token 精确匹配）
       - `artifacts.cfg[]`：`ART:CFG:<key>` token（token 精确匹配）
       - `artifacts.ext[]`：`ART:EXT:<system>` token（token 精确匹配）
   - 再填 Markdown 正文各章节（不发明 front-matter 外的新 ID/token）
   - “接口”章节：若 `refs.prd_api` 为空则正文严格写 1 行 `N/A`；否则必须为非 `N/A`
   - “数据/产物落点”章节：若 `refs.prd_tbl` 与 `artifacts.*` 全为空则正文严格写 1 行 `N/A`；否则必须为非 `N/A`
4. 生成后占位符自检（必须；必须在本命令内修正）：
   - 对每个 `docs/story-N-<slug>.md` 逐行扫描（忽略 fenced code blocks），确保不存在任何模板占位符残留（包含 YAML front-matter 与正文），至少包括：
     - `[...]`、`[功能描述]`、`[规则摘要]`、`[接口名称]` 等方括号占位符
     - `Story N` / `功能名称`
     - `FP-###`
      - `M-xx` / `M-yy`
      - `BR-###` / `TBL-###` / `API-###`（仍为 `###` 占位）
     - `ART:FILE:[path_glob]` / `ART:CFG:[key]` / `ART:EXT:[system]`
   - 若命中任一项：必须立即在对应 Story 文件中修正并再次自检，直到全量通过
5. 结构自检：Story 编号可执行（前置编号 < 当前编号）；文件名与 split-plan 1:1 对应；无重复编号

## 完成后

- 提示用户在新窗口运行 `/split-check1`，`PASS` 后再运行 `/split-check2`
