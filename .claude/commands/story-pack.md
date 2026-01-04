# 阶段6b: Story 执行包生成（/story-pack）

- `$ARGUMENTS`: Story 编号（如: 1）

生成一个可复制的 `STORY_EXEC_PACK`，用于在**新窗口**执行 `/story $ARGUMENTS` 时替代“同时读 PRD/GC/Story 全文”，从而显著降噪。

> 约束：本命令**不修改任何文件**；只输出一个代码块（便于整段复制）。

## 前置条件（必须满足）

- 已在新窗口运行 `/story-check $ARGUMENTS` 且结果为 `PASS`
- `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/story-$ARGUMENTS-*.md` 均存在且 Story 文件仅匹配 1 个
- PRD 已包含锚点：接口/表详情标题行包含 `<!-- PRD#API-### -->` / `<!-- PRD#TBL-### -->`（具体数字）

## 读取（按顺序，低噪音）

1. `docs/story-$ARGUMENTS-*.md`：只抽取索引（引用集合）
2. `docs/GLOBAL-CONTEXT.md`：按索引抽取必要片段
3. `docs/PRD.md`：按锚点机械抽取必要块

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
- 对于业务规则：仅从第 4 节规则表中复制被引用的 `BR-###` 行（连同表头与分隔行）

### C) 从 PRD 抽取（锚点 + 固定边界，避免误命中）

- 必须原文复制（不做摘要/改写）
- 对每个 `PRD#API-###`：
  - 用锚点 `<!-- PRD#API-### -->` 在 PRD 中**唯一定位**到对应“接口详情”标题行
  - 复制范围：从该标题行开始，直到下一条接口详情标题行（`#### 9.3.*`）之前（包含本块内所有小节与表格）
- 对每个 `PRD#TBL-###`：
  - 用锚点 `<!-- PRD#TBL-### -->` 在 PRD 中**唯一定位**到对应“表定义”标题行
  - 复制范围：从该标题行开始，直到下一条表定义标题行（`#### 8.2.*`）之前（包含本块内所有小节与表格）
- 对每个 `PRD#BR-###`（如适用）：
  - 从 PRD 第 6 节规则表中复制该 `BR-###` 对应行（连同表头与分隔行）

> 若任何 `PRD#<ID>` 找不到对应锚点/块边界：停止并输出 `FAIL` 清单，让用户回到 `/prd` 或 `/split` 修正（不输出 pack）。

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
    | ID | 规则 | 涉及Story |
    |----|------|-----------|
    | BR-001 | ... | ... |
prd:
  api_blocks: |-
    (按 PRD#API-### 顺序逐块原文粘贴；每块包含标题行锚点)
  table_blocks: |-
    (按 PRD#TBL-### 顺序逐块原文粘贴；每块包含标题行锚点)
  rule_rows: |-
    (如有 PRD#BR-### 则粘贴对应规则表行；无则写 N/A)
```

## 开始

请提供 Story 编号（例如：`/story-pack 1`）。若已通过 `/story-check`，我会生成可复制的 `STORY_EXEC_PACK`。

