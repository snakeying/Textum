# 阶段6b: Story 执行包生成

- `$ARGUMENTS`: Story 编号（如: 1）

生成 1 个可复制的 `STORY_EXEC_PACK`（只输出 1 个代码块），作为该 Story 的最小执行输入。

## 前置条件（必须满足）

- 已在新窗口运行 `/story-check $ARGUMENTS` 且结果为 `PASS`
- `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/story-$ARGUMENTS-*.md` 均存在且 Story 文件仅匹配 1 个
- PRD 已包含锚点：
  - 若本 Story 引用 `PRD#TBL-###`：对应表详情标题行包含 `<!-- PRD#TBL-### -->`
  - 若本 Story 引用 `PRD#API-###`：对应接口详情标题行包含 `<!-- PRD#API-### -->`

## 读取（按顺序，低噪音）

1. `docs/story-$ARGUMENTS-*.md`：抽取索引（引用集合）
2. `docs/GLOBAL-CONTEXT.md`：按索引抽取片段
3. `docs/PRD.md`：按锚点抽取块

## 机械抽取规则（必须遵守）

### A) 从 Story 抽取索引

- 收集 `GC#BR-###`
- 收集 `PRD#API-###` / `PRD#TBL-###` / `PRD#BR-###`
- 去重后按 ID 升序排列

### B) 从 GC 抽取（避免通读）

- 必须原文复制（不做摘要/改写）
- 固定复制以下 **整段章节**（按标题边界截取，`## X.` 到下一个 `##` 之前）：
  - `## 2. 项目结构（必填）`
  - `## 3. 枚举值定义（必填；无则写 N/A）`
  - `## 5. 权限矩阵（必填）`
  - `## 8. API规范（必填）`
- 对于业务规则：仅从第 4 节规则表中复制被引用的 `BR-###` 行（连同表头与分隔行；无引用写 `N/A`）

### C) 从 PRD 抽取（锚点 + 固定边界，避免误命中）

- 必须原文复制（不做摘要/改写）
- 令 `S_api =` Story 内出现的所有 `PRD#API-###` 去重集合
- 若 `S_api` 为空：在 pack 中写 `prd.api_blocks` 为 `N/A`
- 若 `S_api` 非空：
  - 若 PRD `### 9.2` 内容为 `N/A`：输出 `FAIL` 并停止
  - 对每个 `PRD#API-###`：
    - 用锚点 `<!-- PRD#API-### -->` 在 PRD 中**唯一定位**到对应“接口详情”标题行
    - 复制范围：从该标题行开始，直到下一条接口详情标题行（`#### 9.3.*`）之前（包含本块内所有小节与表格）
- 令 `S_tbl =` Story 内出现的所有 `PRD#TBL-###` 去重集合
- 若 `S_tbl` 为空：在 pack 中写 `prd.table_blocks` 为 `N/A`
- 若 `S_tbl` 非空：对每个 `PRD#TBL-###`：
  - 用锚点 `<!-- PRD#TBL-### -->` 在 PRD 中**唯一定位**到对应“表定义”标题行
  - 复制范围：从该标题行开始，直到下一条表定义标题行（`#### 8.2.*`）之前（包含本块内所有小节与表格）
- 令 `S_prd_br =` Story 内出现的所有 `PRD#BR-###` 去重集合
- 若 `S_prd_br` 为空：在 pack 中写 `prd.rule_rows` 为 `N/A`
- 若 `S_prd_br` 非空：
  - 从 PRD 第 6 节规则表中复制：表头 + 分隔行 + `S_prd_br` 对应行（按 ID 升序）

> 若任何 `PRD#<ID>` 找不到对应锚点/块边界：输出 `FAIL` 清单并停止（不输出 pack）。

## 输出（必须严格）

只输出一个代码块，格式如下（字段齐全；内容为原文复制）：

```yaml
STORY_EXEC_PACK: v1
story:
  file: "docs/story-$ARGUMENTS-*.md"
  markdown: |-
    (原文粘贴 Story 全文)
gc:
  project_structure: |-
    (原文粘贴 GC 第2节)
  enums: |-
    (原文粘贴 GC 第3节)
  permission_matrix: |-
    (原文粘贴 GC 第5节)
  api_conventions: |-
    (原文粘贴 GC 第8节)
  referenced_rules: |-
    (若无 GC#BR 引用写 N/A；否则粘贴 GC 第4节规则表：表头 + 分隔行 + 被引用 BR-### 行)
prd:
  api_blocks: |-
    (若无 PRD#API 引用写 N/A；否则按 PRD#API-### 顺序逐块原文粘贴；每块包含标题行锚点)
  table_blocks: |-
    (若无 PRD#TBL 引用写 N/A；否则按 PRD#TBL-### 顺序逐块原文粘贴；每块包含标题行锚点)
  rule_rows: |-
    (若无 PRD#BR 引用写 N/A；否则粘贴 PRD 第6节规则表：表头 + 分隔行 + 被引用 BR-### 行)
```

## 开始

请提供 Story 编号（例如：`/story-pack 1`）。若已通过 `/story-check`，我会生成可复制的 `STORY_EXEC_PACK`。
