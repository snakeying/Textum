# 阶段6b: Story 执行包生成

- `$ARGUMENTS`: Story 编号（如: 1）

生成 1 个 `STORY_EXEC_PACK`，写入 `docs/story-$ARGUMENTS-exec-pack.yaml`，作为该 Story 的最小执行输入。

## 读取 / 写入

- 读取：`docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/story-$ARGUMENTS-*.md`
- 写入：`docs/story-$ARGUMENTS-exec-pack.yaml`（内容为纯 YAML；不包含 ```）

## 前置条件（必须满足）

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
- 收集 `FP-001` 形式的功能点 ID：从 `关联功能点（必填）:` 行抽取（去重后按编号升序）
- 收集 `PRD#API-###` / `PRD#TBL-###` / `PRD#BR-###`
- 收集 `ART` token（从 `## 数据/产物落点` 章节中以 `- ART:` 开头的条目抽取；去重后按编号升序）：
  - 仅允许：`ART:FILE:<path>` / `ART:CFG:<key>` / `ART:EXT:<system>`
  - token 截止位置：到第一个空格或 ` - ` 之前（后续描述不属于 token）
- 去重后按 ID 升序排列

### B) 从 GC 抽取（避免通读）

- 必须原文复制（不做摘要/改写）
- 固定复制以下 **整段章节**（按标题边界截取，`## X.` 到下一个 `##` 之前）：
  - `## 2. 项目结构（必填）`
  - `## 3. 枚举值定义（必填；无则写 N/A）`
  - `## 5. 权限矩阵（必填）`
  - `## 8. API规范（必填）`
- 对于业务规则：仅从第 4 节规则表中复制被引用的 `BR-###` 行（连同表头与分隔行；无引用写 `N/A`）
- 对于项目验证命令：从 GC 第 2 节 `### 项目验证命令（如适用；否则写 N/A）` 的表格逐行抽取到 pack 的 `verification.commands`（按表格顺序；不改写）
  - 若该小节为 `N/A` 或表格不存在：`verification.commands` 只写 1 行 `type/command/note` 均为 `N/A`
  - 否则：对表格每一行数据，原文复制三列到 `type` / `command` / `note`；`command` 允许为 `N/A`

### C0) FP→落点映射预检查（必须；兜底防硬违约）

1. 在 PRD 中定位 `### 8.0 功能点→落点映射（必填）` 表，抽取本 Story 关联的 `FP-001` 对应行（表头 + 分隔行 + 行；按 `FP-001` 升序）
2. 对每个 `FP-001` 的“落点”列：解析为集合（`N/A` 或逗号分隔多项），允许项前缀仅：`DB:` / `FILE:` / `CFG:` / `EXT:` / `N/A`
3. 计算期望覆盖集合（去重）：
   - `E_tbl =` 所有 `DB:TBL-###` 转换为 `PRD#TBL-###`（必须为具体数字）
   - `E_art =` 所有 `FILE:` / `CFG:` / `EXT:` 转换为 `ART:FILE:` / `ART:CFG:` / `ART:EXT:`（token 精确匹配）
4. 校验（任一不满足即 `FAIL` 并停止，不输出 pack）：
   - `E_tbl` 必须是 Story 内 `PRD#TBL-###` 的子集（缺失则列出缺失项）
   - `E_art` 必须是 Story 内 `ART:*` token 集合的子集（缺失则列出缺失项）

### C) 从 PRD 抽取（锚点 + 固定边界，避免误命中）

- 必须原文复制（不做摘要/改写）
- `N/A_STRICT` 判定口径（必须按此判定）：定位 PRD 小节 `### 9.2 接口清单（必填）` 的正文，去掉空行并 Trim 后仅剩 1 行且该行严格等于 `N/A`
- 令 `S_api =` Story 内出现的所有 `PRD#API-###` 去重集合
- 若 `S_api` 为空：在 pack 中写 `prd.api_blocks` 为 `N/A`
- 若 `S_api` 非空：
  - 若 PRD `### 9.2` 满足 `N/A_STRICT`：输出 `FAIL` 并停止
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

- `prd.fp_artifact_rows`：
  - 若 Story 未声明任何 `FP-001`：输出 `FAIL` 并停止（不输出 pack）
  - 否则：粘贴 PRD `8.0 功能点→落点映射` 表中与本 Story 关联 `FP-001` 对应的行（包含表头 + 分隔行 + 行；按 `FP-001` 升序）

> 若任何 `PRD#<ID>` 找不到对应锚点/块边界：输出 `FAIL` 清单并停止（不输出 pack）。

## 输出（必须严格）

- 若 `FAIL`：只输出 `FAIL` 清单并停止（不写 pack 文件；`F-001` 起编号；每条必须包含：问题 / 影响 / 修复方式（只给 1 个动作或命令））
- 若 `PASS`：
  1. 写入 `docs/story-$ARGUMENTS-exec-pack.yaml`（字段齐全；内容为原文复制；格式如下）

`docs/story-$ARGUMENTS-exec-pack.yaml` 内容格式（必须严格）：

```yaml
STORY_EXEC_PACK: v2
story:
  file: "docs/story-$ARGUMENTS-*.md"
  markdown: |-
    (原文粘贴 Story 全文)
verification:
  commands:
    - type: "N/A"
      command: "N/A"
      note: "N/A"
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
  fp_artifact_rows: |-
    (原文粘贴 PRD 8.0 表：表头 + 分隔行 + 本 Story 关联 FP 行；若不适用写 N/A)
  api_blocks: |-
    (若无 PRD#API 引用写 N/A；否则按 PRD#API-### 顺序逐块原文粘贴；每块包含标题行锚点)
  table_blocks: |-
    (若无 PRD#TBL 引用写 N/A；否则按 PRD#TBL-### 顺序逐块原文粘贴；每块包含标题行锚点)
  rule_rows: |-
    (若无 PRD#BR 引用写 N/A；否则粘贴 PRD 第6节规则表：表头 + 分隔行 + 被引用 BR-### 行)
```

  2. 输出：
     - `PASS`
     - `已写入：docs/story-$ARGUMENTS-exec-pack.yaml`
     - `下一步：/story $ARGUMENTS`

## 开始

请提供 Story 编号（例如：`/story-pack 1`）。我会写入 `docs/story-$ARGUMENTS-exec-pack.yaml`。
