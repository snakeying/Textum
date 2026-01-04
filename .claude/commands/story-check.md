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

## FAIL 校验项（严格拦截）

### 0) 基础门禁

- `docs/PRD.md` 必须存在
- `docs/GLOBAL-CONTEXT.md` 必须存在
- `docs/story-$ARGUMENTS-*.md` 必须存在且仅 1 个

### 1) 模板完整性（不得缺章/占位符）

Story 必须包含以下章节；无内容写 `N/A`，但不得省略章节：

- `模块（必填）`
- `## 功能点（必填）`
- `## 依赖（必填）`
- `## 业务规则（必填；无则写 N/A）`
- `## 数据变更（如无写 N/A）`
- `## 接口（如无写 N/A）`
- `## 验收标准（必填）`
- `## 测试要求（必填；无则写 N/A）`
- `## 注意（如无写 N/A）`

占位符门禁（剔除 fenced code blocks 后逐行检查）：

- 禁止出现：`PRD#API-###` / `PRD#TBL-###` / `PRD#BR-###` / `GC#BR-###`
- 允许出现 `[` 的情况仅有：
  - 行首任务清单标记：`- [ ]` / `- [x]` / `* [ ]` / `* [x]`
    - 标记后的正文不得再出现 `[`，除非是 Markdown 链接 `[text](...)`
  - Markdown 链接：`[text](...)`
- 其他任何 `[` 一律 `FAIL`

### 2) 引用格式（必须可追溯）

- 所有 PRD 引用必须使用 `PRD#<ID>`，且 `<ID>` 必须为具体数字（如 `PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`）

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

### 5) 数据变更一致性（TBL-### 如适用）

- 令 `S_tbl =` Story 内出现的所有 `PRD#TBL-###` 去重集合
- 若 `S_tbl` 为空：Story 的 `## 数据变更` 必须为 `N/A`
- 若 `S_tbl` 非空：
  - Story 的 `## 数据变更` 不得为 `N/A`
  - 数据变更章节内出现的 `PRD#TBL-###` 去重集合必须与 `S_tbl` 完全一致（不得缺失/多写）
  - 对 `S_tbl` 中每个 `PRD#TBL-###`：校验该 `TBL-###` 必须能在 PRD `8.1/8.2` 中定位到
  - 对 `S_tbl` 中每个 `PRD#TBL-###`：PRD `8.2` 中必须存在且仅存在 1 个锚点 `<!-- PRD#TBL-### -->`

### 6) 依赖合法性（可执行顺序）

- 若声明 `前置Story: Story X`：必须满足 `X < $ARGUMENTS`
- 禁止自依赖与循环依赖（就本 Story 的前置链路做检查）

## DECISION（需要用户确认）

- “测试要求”为 `N/A` 但 Story 涉及 `API-###` 或数据变更：是否允许先实现后补测试？
- “验收标准”过少或不可验证：需要用户确认验收口径后再进入 `/story`

## PASS

- `PASS`：仅提示下一步动作（必须按序）：
  - 在新窗口运行 `/story-pack $ARGUMENTS` 生成 `STORY_EXEC_PACK`
  - 再在新窗口运行 `/story $ARGUMENTS` 并粘贴该 pack
