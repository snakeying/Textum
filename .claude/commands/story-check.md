# 阶段6a: Story 校验

- `$ARGUMENTS`: Story 编号（如: 1）

读取 `docs/story-$ARGUMENTS-*.md`、`docs/GLOBAL-CONTEXT.md`、`docs/PRD.md`，输出 `FAIL/DECISION/PASS` 清单；不修改任何文件。

## 读取

- `docs/story-$ARGUMENTS-*.md`（必须且仅匹配 1 个）
- `docs/GLOBAL-CONTEXT.md`
- `docs/PRD.md`（只读）

## 最小读取（避免通读）

1. 先读 Story 抽取索引：`模块`、`前置Story`、`GC#BR-###`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`
2. 读取 PRD `### 9.2 接口清单`：判断是否为 `N/A`（PRD_HAS_API）
3. 再按索引在 GC/PRD 做定位校验（不通读全文）
4. 输出只包含清单（不粘贴原文）

## 输出规则（只读）

- 不输出原文
- 若存在任何 `FAIL`：
  - 输出 `FAIL` 清单（`F-001` 起编号；**每条必须包含：问题 / 影响 / 修复方式（只给 1 个动作或命令）**）
  - 末尾追加：
    - `下一步：按 FAIL 清单中每条“修复方式”执行修正（从 F-001 开始），修完后重跑本命令`
    - `重跑：/story-check $ARGUMENTS`
  - 然后结束
- 仅当无 `FAIL`：输出 `DECISION`（若有）或 `PASS`

## FAIL 校验项（严格拦截）

### 0) 基础门禁

- `docs/PRD.md` 必须存在
- `docs/GLOBAL-CONTEXT.md` 必须存在
- `docs/story-$ARGUMENTS-*.md` 必须存在且仅 1 个

### 1) 模板完整性（不得缺章/占位符）

Story 必须包含以下章节；无内容写 `N/A`，但不得省略章节：

- `模块（必填）`
- `关联功能点（必填）`
- `## 功能点（必填）`
- `## 依赖（必填）`
- `## 业务规则（必填；无则写 N/A）`
- `## 数据/产物落点（必填；无则写 N/A）`
- `## 接口（如无写 N/A）`
- `## 验收标准（必填）`
- `## 测试要求（必填；涉及 API 时不得为 N/A；否则无则写 N/A）`
- `## 注意（如无写 N/A）`

占位符门禁（剔除 fenced code blocks 后逐行检查）：

- 禁止出现：`PRD#API-###` / `PRD#TBL-###` / `PRD#BR-###` / `GC#BR-###`
- 允许出现 `[`/`]` 的情况仅有：
  - 行首任务清单标记：`- [ ]` / `- [x]` / `* [ ]` / `* [x]`
    - 标记后的正文不得再出现 `[`，除非是 Markdown 链接 `[text](...)`
  - Markdown 链接：`[text](...)`
  - 路径/路由等“包含 `/` 或 `\\` 的字符串”中的方括号（如 `pages/[slug].tsx`、`ART:FILE:content/[slug].md`、`/posts/[slug]`）
- 其他任何 `[`/`]` 一律 `FAIL`

### 2) 引用格式（必须可追溯）

- 所有 PRD 引用必须使用 `PRD#<ID>`，且 `<ID>` 必须为具体数字（如 `PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`）

### 2.5) 关联功能点（FP）可追溯性（必须）

- Story 必须包含 `关联功能点（必填）:` 行，且至少包含 1 个 `FP-xx`
- 每个 `FP-xx` 必须为具体数字（允许 `FP-01` / `FP-001`；禁止 `FP-xx`、`FP-##`）
- 对 Story 中出现的每个 `FP-xx`：必须能在 PRD `### 8.0 功能点→落点映射（必填）` 表中找到对应行；找不到即 `FAIL`
- `## 功能点（必填）` 章节内每条条目必须为 `- FP-xx: ...`，且该章节出现的 `FP-xx` 去重集合必须与“关联功能点”一致（不得缺失/多写）

### 3) 规则一致性（GC#BR 必须存在）

- 收集 Story 中所有 `GC#BR-###`：校验每个引用的 `BR-###` 都存在于 `docs/GLOBAL-CONTEXT.md` 第 4 节业务规则表
- 收集 Story 中所有 `PRD#BR-###`：校验每个引用的 `BR-###` 都存在于 PRD 第 6 节规则表

### 4) 接口一致性（API-### 必须存在且可定位）

- 先判断 PRD 是否有接口：若 PRD `### 9.2` 内容为 `N/A`，则 `PRD_HAS_API = false`
- 令 `S_api =` Story 内出现的所有 `PRD#API-###` 去重集合
- 若 `PRD_HAS_API = false`：
  - Story 的 `## 接口` 必须为 `N/A`
  - `S_api` 必须为空（不得出现任何 `PRD#API-###`）
- 若 `PRD_HAS_API = true`：
  - 若 `S_api` 为空：Story 的 `## 接口` 必须为 `N/A`
  - 若 `S_api` 非空：
    - Story 的 `## 接口` 不得为 `N/A`
    - 接口章节内出现的 `PRD#API-###` 去重集合必须与 `S_api` 完全一致（不得缺失/多写）
    - 对 `S_api` 中每个 `PRD#API-###`：校验该 `API-###` 必须存在于 PRD `9.2 接口清单`
    - 对 `S_api` 中每个 `PRD#API-###`：PRD `9.3` 中必须存在且仅存在 1 个锚点 `<!-- PRD#API-### -->`

### 5) 数据/产物落点一致性（TBL/ART 如适用）

- 令 `S_tbl =` Story 内出现的所有 `PRD#TBL-###` 去重集合
- 令 `S_art =` Story 内出现的所有 `ART` token 去重集合（建议从 `## 数据/产物落点` 章节中以 `- ART:` 开头的条目抽取）：
  - 仅允许：`ART:FILE:<path>` / `ART:CFG:<key>` / `ART:EXT:<system>`
  - token 截止位置：到第一个空格或 ` - ` 之前（后续描述不属于 token）
- 若 `S_tbl` 与 `S_art` 均为空：Story 的 `## 数据/产物落点` 必须为 `N/A`
- 若 `S_tbl` 或 `S_art` 任一非空：Story 的 `## 数据/产物落点` 不得为 `N/A`
- 若 `S_tbl` 非空：
  - “数据/产物落点”章节内出现的 `PRD#TBL-###` 去重集合必须与 `S_tbl` 完全一致（不得缺失/多写）
  - 对 `S_tbl` 中每个 `PRD#TBL-###`：校验该 `TBL-###` 必须能在 PRD `8.1/8.2` 中定位到
  - 对 `S_tbl` 中每个 `PRD#TBL-###`：PRD `8.2` 中必须存在且仅存在 1 个锚点 `<!-- PRD#TBL-### -->`

### 5.5) FP→落点声明闭合（必做兜底）

目标：避免进入执行包/实现阶段后被迫发明 pack 外新落点，导致最终产出偏离用户预期。

- 在 PRD `### 8.0 功能点→落点映射（必填）` 表中抽取本 Story 关联 `FP-xx` 对应行，解析“落点”列为集合（`N/A` 或逗号分隔多项）
- 期望集合（去重）：
  - `E_tbl =` 所有 `DB:TBL-###` 转为 `PRD#TBL-###`
  - `E_art =` 所有 `FILE:`/`CFG:`/`EXT:` 转为 `ART:FILE:`/`ART:CFG:`/`ART:EXT:` token
- 校验（任一不满足即 `FAIL`）：
  - `E_tbl` 必须是 `S_tbl` 的子集（缺失则列出缺失项）
  - `E_art` 必须是 `S_art` 的子集（缺失则列出缺失项）
- 若存在额外落点（`S_tbl - E_tbl` 或 `S_art - E_art` 非空）：输出 `DECISION`，提示 PRD `8.0` 映射可能缺失/漂移，建议回 `/prd` 修正

### 6) 依赖合法性（可执行顺序）

- 若声明 `前置Story: Story X`：必须满足 `X < $ARGUMENTS`
- 禁止自依赖与循环依赖（就本 Story 的前置链路做检查）

### 7) 测试要求最小可用性（涉及 API 时强制）

- 若 `S_api` 非空：Story 的 `## 测试要求` 不得为 `N/A`

## DECISION（需要用户确认）

- “测试要求”为 `N/A` 但 Story 涉及数据/产物落点：是否允许先实现后补测试？
- “验收标准”过少或不可验证：需要用户确认验收口径后再进入 `/story`

## PASS

- `PASS`：仅提示下一步动作（必须按序）：
  - 在新窗口运行 `/story-pack $ARGUMENTS` 写入 `docs/story-$ARGUMENTS-exec-pack.yaml`
  - 再在新窗口运行 `/story $ARGUMENTS`
