# 阶段6a: Story 校验

- `$ARGUMENTS`: Story 编号（如: 1）

读取：`docs/story-$ARGUMENTS-*.md`、`docs/GLOBAL-CONTEXT.md`（只读）、`docs/PRD.md`（只读） | 写入：无（只输出 `FAIL/DECISION/PASS`；不修改文件） | 模板：`N/A`

校验单个 Story 并输出 `FAIL/DECISION/PASS` 清单；不修改任何文件。

## 最小读取（必须；避免通读）

只允许引用本节列出的内容范围；其余一律视为不可用。

1. 读取 Story：仅解析 YAML front-matter + 定位章节边界（不摘抄正文）
2. 读取 GC：仅第 4 节业务规则表（抽取合法 `BR-###` 集合）
3. 读取 PRD（只读；按索引定向读取）：
   - `### 9.2 接口清单（必填）`：按 `N/A_STRICT` 判定 `PRD_HAS_API`；抽取 `API-###` 集合（如适用）
   - `### 8.0 功能点→落点映射（必填）`：抽取本 Story `fp_ids` 对应行（用于 FP 存在性 + 落点闭合）
   - `### 8.1 表清单`：抽取 `TBL-###` 集合
   - 第 6 节规则表：抽取 `BR-###` 集合
   - 若 `refs.prd_api` 非空：按锚点 `<!-- PRD#API-### -->` 定向校验 PRD `9.3` 接口详情存在性
   - 若 `refs.prd_tbl` 非空：按锚点 `<!-- PRD#TBL-### -->` 定向校验 PRD `8.2` 表定义存在性

## 输出规则（只读）

- 不输出任何原文（只输出清单）
- 若存在任何 `FAIL`：
  - 输出 `FAIL` 清单（`F-001` 起编号；每条必须包含以下字段）：
    - `定位`：目标 Story 文件（`docs/story-N-<slug>.md`）+ YAML front-matter key / Markdown 章节名 / 门禁项；避免行号
    - `问题`：1 句
    - `期望`：可机械执行的“替换目标/格式”（能推导就写出来）
    - `影响`：H/M/L
    - `修复`：只给 1 个动作（通常是“按定位修正 docs/story-$ARGUMENTS-*.md”）
  - 末尾追加：
    - `修正：按 FAIL 清单逐条修复 docs/story-$ARGUMENTS-*.md 后重跑 Story 校验`
    - `重跑：Story 校验（参数不变）`
  - 然后结束
- 仅当无 `FAIL`：输出 `DECISION`（若有）或 `PASS`

## FAIL 校验项（严格拦截）

### 0) 基础门禁

- `docs/PRD.md` 必须存在
- `docs/GLOBAL-CONTEXT.md` 必须存在
- `docs/story-$ARGUMENTS-*.md` 必须存在且仅匹配 1 个

### 1) YAML front-matter（必须可解析且字段齐全）

对 Story 文件首部 `--- ... ---`：

- 必须存在且可解析为 YAML
- 根键必须为 `STORY: v1`
- 必须存在键：`story`、`n`、`slug`、`title`、`modules`、`prereq_stories`、`fp_ids`、`refs`、`artifacts`
- 一致性（任一不满足即 `FAIL`）：
  - `n` 必须等于 `$ARGUMENTS`，且 `story` 必须严格等于 `"Story {n}"`
  - 文件名必须匹配：`docs/story-{n}-{slug}.md`（`slug` 与 front-matter 一致）
  - `slug` 必须为 `kebab-case`
- `modules`：
  - 必须为非空数组；每项必须为 `M-01`（2 位数字）形式；不得出现 `M-xx`/模块名
  - 去重后不得为空；不得重复
- `prereq_stories`：
  - 必须为数组；每项必须严格匹配 `Story <number>`；不得重复
  - 不得包含自身；每个 `<number>` 必须 `< n`
- `fp_ids`：
  - 必须为非空数组；每项必须为 `FP-001`（3 位数字）形式；不得重复；不得出现 `FP-###`
- `title`：
  - 必须为非空字符串；不得为 `TBD` / `功能名称`
- `refs` 必须存在且包含 4 个键，且每个都必须为数组：
  - `refs.gc_br[]`：每项必须为 `BR-001`（3 位数字）形式；不得包含 `GC#` 前缀
  - `refs.prd_br[]`：每项必须为 `BR-001`（3 位数字）形式；不得包含 `PRD#` 前缀
  - `refs.prd_tbl[]`：每项必须为 `TBL-001`（3 位数字）形式；不得包含 `PRD#` 前缀
  - `refs.prd_api[]`：每项必须为 `API-001`（3 位数字）形式；不得包含 `PRD#` 前缀
- `artifacts` 必须存在且包含 3 个键，且每个都必须为数组：
  - `artifacts.file[]`：每项必须匹配 `ART:FILE:<path>`
  - `artifacts.cfg[]`：每项必须匹配 `ART:CFG:<key>`
  - `artifacts.ext[]`：每项必须匹配 `ART:EXT:<system>`

### 2) 模板完整性与占位符（不得缺章/不得残留）

必须包含以下 Markdown 章节（缺失即 `FAIL`；无内容写 `N/A` 但不得省略章节）：

- `## 功能点（必填）`
- `## 依赖（必填）`
- `## 业务规则（必填；无则写 N/A）`
- `## 数据/产物落点（必填；无则写 N/A）`
- `## 接口（如无写 N/A）`
- `## 验收标准（必填）`
- `## 测试要求（必填；涉及 API 时不得为 N/A；否则无则写 N/A）`
- `## 注意（如无写 N/A）`

Story 中不得出现 fenced code blocks（```）；出现即 `FAIL`。

占位符门禁（逐行检查；包含 YAML front-matter 与正文；任一命中即 `FAIL`）：

- `TBD`
- `[...]`
- `Story N` / `功能名称`
- `M-xx`
- `FP-###`
- `BR-###` / `TBL-###` / `API-###`（仍为 `###` 占位）
- `ART:FILE:[path_glob]` / `ART:CFG:[key]` / `ART:EXT:[system]`

方括号使用规则（避免误伤路由/路径）：逐行检查；若出现 `[` 或 `]`：

- 允许：行首任务清单标记 `- [ ]` / `- [x]` / `* [ ]` / `* [x]`
- 允许：Markdown 链接 `[text](...)`
- 允许：路径/路由 token 中的 Next.js 风格动态段（`[` 必须紧跟在 `/` 或 `\\` 之后，且 `[]` 内不得包含空白、`/`、`\\`），如 `/posts/[slug]`、`pages/[id].tsx`、`ART:FILE:content/[slug].md`
- 其余一律 `FAIL`

方括号门禁执行范围：**不扫描 YAML front-matter 区域**（避免 YAML `[]` 误伤）；但占位符门禁必须扫描 YAML front-matter。

### 3) 业务规则引用一致性（GC/PRD）

- 对 `refs.gc_br[]` 中每个 `BR-###`：必须存在于 `docs/GLOBAL-CONTEXT.md` 第 4 节业务规则表的 ID 列；否则 `FAIL`
- 对 `refs.prd_br[]` 中每个 `BR-###`：必须存在于 `docs/PRD.md` 第 6 节规则表；否则 `FAIL`

### 4) 接口一致性（PRD_HAS_API + 锚点）

先判断 PRD 是否有接口（必须按 `N/A_STRICT` 判定）：

`N/A_STRICT` 判定口径（权威；逐字一致；禁止改写）：
- 定位 PRD 小节 `### 9.2 接口清单（必填）` 的正文（标题行之后到下一同级小节标题之前）
- 判定 `N/A_STRICT = true` 当且仅当：正文去掉空行并 Trim 后仅剩 1 行且该行严格等于 `N/A`

据此：若 `N/A_STRICT = true` 则 `PRD_HAS_API = false`；否则 `PRD_HAS_API = true` 并抽取 `P_api` 集合。

令：`S_api = refs.prd_api[]` 去重集合。

- 若 `PRD_HAS_API = false`：
  - `S_api` 必须为空
  - Story 的 `## 接口` 章节正文必须严格为 1 行 `N/A`
- 若 `PRD_HAS_API = true`：
  - 对 `S_api` 中每个 `API-###`：必须存在于 `P_api`；否则 `FAIL`
  - 若 `S_api` 为空：Story 的 `## 接口` 章节正文必须严格为 1 行 `N/A`
  - 若 `S_api` 非空：
    - Story 的 `## 接口` 章节正文不得为 `N/A`
    - 对 `S_api` 中每个 `API-###`：PRD `9.3` 中必须存在且仅存在 1 次锚点 `<!-- PRD#API-### -->`；否则 `FAIL`

### 5) 数据/产物落点一致性（FP→落点闭合；TBL/ART）

令：

- `S_tbl = refs.prd_tbl[]` 去重集合
- `S_art = (artifacts.file + artifacts.cfg + artifacts.ext)` 去重集合

章节一致性（任一不满足即 `FAIL`）：

- 若 `S_tbl` 与 `S_art` 均为空：Story 的 `## 数据/产物落点` 章节正文必须严格为 1 行 `N/A`
- 若 `S_tbl` 或 `S_art` 任一非空：Story 的 `## 数据/产物落点` 章节正文不得为 `N/A`

表存在性（任一不满足即 `FAIL`）：

- 对 `S_tbl` 中每个 `TBL-###`：必须存在于 PRD `### 8.1 表清单`；否则 `FAIL`
- 对 `S_tbl` 中每个 `TBL-###`：PRD `8.2` 中必须存在且仅存在 1 次锚点 `<!-- PRD#TBL-### -->`；否则 `FAIL`

FP→落点闭合（任一不满足即 `FAIL`）：

1. 在 PRD `### 8.0 功能点→落点映射（必填）` 表中抽取 `fp_ids` 对应行，解析“落点”列为集合（`N/A` 或逗号分隔多项）
2. 期望集合（去重）：
   - `E_tbl =` 所有 `DB:TBL-###` 转为 `TBL-###`
   - `E_art =` 所有 `FILE:`/`CFG:`/`EXT:` 转为 `ART:FILE:`/`ART:CFG:`/`ART:EXT:`（token 必须精确匹配）
3. 校验：
   - `E_tbl` 必须是 `S_tbl` 的子集（缺失则列出缺失项）
   - `E_art` 必须是 `S_art` 的子集（缺失则列出缺失项）

若存在额外落点（`S_tbl - E_tbl` 或 `S_art - E_art` 非空）：输出 `DECISION`（提示 PRD `8.0` 映射可能缺失/漂移，建议修正 PRD 后重跑）。

### 6) 依赖合法性（可执行顺序）

- 对 `prereq_stories[]` 中每个 `Story X`：必须满足 `X < n`

### 7) 测试要求最小可用性（涉及 API 时强制）

- 若 `S_api` 非空：Story 的 `## 测试要求` 章节正文不得为 `N/A`

## DECISION（不阻断；需要用户确认）

- 若输出 `DECISION`：
  - 接受：继续 Story 执行包生成
  - 不接受：先修正后重跑 Story 校验

## PASS

- `PASS`：仅提示下一步动作（必须按序）：
  - Story 执行包生成（编号 $ARGUMENTS）
  - Story 执行（编号 $ARGUMENTS）
