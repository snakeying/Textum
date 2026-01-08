# 阶段6b: Story 执行包生成

- `$ARGUMENTS`: Story 编号（如: 1）

读取：`docs/story-$ARGUMENTS-*.md`、`docs/GLOBAL-CONTEXT.md`、`docs/PRD.md`（只读） | 写入：`docs/story-$ARGUMENTS-exec-pack.yaml`（纯 YAML；不包含 ```） | 模板：`N/A`

生成 1 个 `STORY_EXEC_PACK`，写入 `docs/story-$ARGUMENTS-exec-pack.yaml`，作为该 Story 的最小执行输入。

## 最小读取（必须；避免通读）

只允许引用本节列出的内容范围；其余一律视为不可用。

1. 读取 Story：仅解析 YAML front-matter 作为索引
2. 读取 GC：按索引抽取片段（固定章节 + 规则表行 + 验证命令表）
3. 读取 PRD：仅按索引/锚点抽取块（必须逐字原文复制）

## 前置条件（必须满足）

- `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/story-$ARGUMENTS-*.md` 均存在且 Story 文件仅匹配 1 个
- Story YAML front-matter 必须可解析，且 `n == $ARGUMENTS`

## 机械抽取规则（必须遵守）

### A) 从 Story 抽取索引（只看 YAML front-matter）

对 `docs/story-$ARGUMENTS-*.md` 文件首部 `--- ... ---`：

- 抽取并去重排序（按编号升序）：
  - `S_fp = fp_ids[]`（`FP-001`）
  - `S_gc_br = refs.gc_br[]`（`BR-001`）
  - `S_prd_br = refs.prd_br[]`（`BR-001`）
  - `S_tbl = refs.prd_tbl[]`（`TBL-001`）
  - `S_api = refs.prd_api[]`（`API-001`）
  - `S_art = artifacts.file + artifacts.cfg + artifacts.ext`（`ART:*` token）

### B) 从 GC 抽取（避免通读）

- 必须逐字原文复制
- 固定复制以下 **整段章节**（按标题边界截取，`## X.` 到下一个 `##` 之前）：
  - `## 2. 项目结构（必填）`
  - `## 3. 枚举值定义（必填；无则写 N/A）`
  - `## 5. 权限矩阵（必填）`
  - `## 8. API规范（必填）`
- 对于业务规则：仅从第 4 节规则表中复制被引用的 `BR-###` 行（连同表头与分隔行；无引用写 `N/A`）
- 对于项目验证命令：从 GC 第 2 节 `### 项目验证命令（如适用；否则写 N/A）` 的表格逐行抽取到 pack 的 `verification.commands`（按表格顺序；不改写）
  - 若该小节为 `N/A` 或表格不存在：`verification.commands` 只写 1 行 `type/command/note` 均为 `N/A`
  - 否则：对表格每一行数据，原文复制三列到 `type` / `command` / `note`
    - 若 `command = N/A`：该行 `type` 与 `note` 也必须为 `N/A`
    - 若 `command != N/A`：该行 `type` 必须以 `gate:` 或 `opt:` 开头；不得为 `N/A`

### C0) FP→落点映射预检查（必须；兜底防硬违约）

1. 在 PRD 中定位 `### 8.0 功能点→落点映射（必填）` 表，抽取本 Story `S_fp` 对应行（表头 + 分隔行 + 行；按 `FP-001` 升序）
2. 对每个 `FP-001` 的“落点”列：解析为集合（`N/A` 或逗号分隔多项），允许项前缀仅：`DB:` / `FILE:` / `CFG:` / `EXT:` / `N/A`
3. 计算期望覆盖集合（去重）：
   - `E_tbl =` 所有 `DB:TBL-###` 转换为 `TBL-###`（必须为具体数字）
   - `E_art =` 所有 `FILE:` / `CFG:` / `EXT:` 转换为 `ART:FILE:` / `ART:CFG:` / `ART:EXT:`（token 精确匹配）
4. 校验（任一不满足即 `FAIL` 并停止，不输出 pack）：
   - `E_tbl` 必须是 `S_tbl` 的子集（缺失则列出缺失项）
   - `E_art` 必须是 `S_art` 的子集（缺失则列出缺失项）

### C) 从 PRD 抽取（锚点 + 固定边界，避免误命中）

`N/A_STRICT` 判定口径（权威；逐字一致；禁止改写）：
- 定位 PRD 小节 `### 9.2 接口清单（必填）` 的正文（标题行之后到下一同级小节标题之前）
- 判定 `N/A_STRICT = true` 当且仅当：正文去掉空行并 Trim 后仅剩 1 行且该行严格等于 `N/A`

**接口块**

- 若 `S_api` 为空：在 pack 中写 `prd.api_blocks` 为 `N/A`
- 若 `S_api` 非空：
  - 若 PRD `### 9.2` 满足 `N/A_STRICT`：输出 `FAIL` 并停止
  - 对每个 `API-###`（按升序）：
    - 用锚点 `<!-- PRD#API-### -->` 在 PRD 中**唯一定位**到对应“接口详情”标题行
    - 复制范围：从该标题行开始，直到下一条接口详情标题行（`#### 9.3.*`）之前（包含本块内所有小节与表格）

**表定义块**

- 若 `S_tbl` 为空：在 pack 中写 `prd.table_blocks` 为 `N/A`
- 若 `S_tbl` 非空：对每个 `TBL-###`（按升序）：
  - 用锚点 `<!-- PRD#TBL-### -->` 在 PRD 中**唯一定位**到对应“表定义”标题行
  - 复制范围：从该标题行开始，直到下一条表定义标题行（`#### 8.2.*`）之前（包含本块内所有小节与表格）

**PRD 规则表行**

- 若 `S_prd_br` 为空：在 pack 中写 `prd.rule_rows` 为 `N/A`
- 若 `S_prd_br` 非空：
  - 从 PRD 第 6 节规则表中复制：表头 + 分隔行 + `S_prd_br` 对应行（按 ID 升序）

**FP→落点映射行**

- 若 `S_fp` 为空：输出 `FAIL` 并停止（不输出 pack）
- 否则：在 pack 中写入 `prd.fp_artifact_rows` 为 PRD `8.0` 表中 `S_fp` 对应行（同 C0 抽取结果；包含表头 + 分隔行 + 行）

> 若任何锚点定位失败（缺失/重复/块边界不成立）：输出 `FAIL` 清单并停止（不输出 pack）。

## 输出（必须严格）

- 若 `FAIL`：只输出 `FAIL` 清单并停止（不写 pack 文件；`F-001` 起编号；每条必须包含：问题 / 影响 / 修复方式（只给 1 个动作或命令））
- 若 `PASS`：
  1. 写入 `docs/story-$ARGUMENTS-exec-pack.yaml`（纯 YAML；不得包含 ```；不得额外加键；多行内容必须用 YAML block scalar `|-` 逐字原文粘贴）

`docs/story-$ARGUMENTS-exec-pack.yaml` 字段结构（必须严格）：

- 根键：`STORY_EXEC_PACK: v2`
- `story`：
  - `file`：实际 Story 文件路径（必须为 `docs/story-$ARGUMENTS-*.md` 且仅匹配 1 个）
  - `markdown`：`|-` 原文粘贴该 Story 全文（包含 YAML front-matter 与全部章节）
- `verification.commands`：
  - 若 GC 中无可用表格：仅 1 行，且 `type/command/note` 均为 `N/A`
  - 否则：按 GC 表格行顺序逐行原文复制三列到 `type` / `command` / `note`（不改写）
- `gc`：
  - `project_structure`：`|-` 原文粘贴 GC 第 2 节（按标题边界截取的整段章节）
  - `enums`：`|-` 原文粘贴 GC 第 3 节整段章节
  - `permission_matrix`：`|-` 原文粘贴 GC 第 5 节整段章节
  - `api_conventions`：`|-` 原文粘贴 GC 第 8 节整段章节
  - `referenced_rules`：若 `S_gc_br` 为空则写 `N/A`；否则 `|-` 原文粘贴 GC 第 4 节规则表：表头 + 分隔行 + 被引用 `BR-###` 行（按 ID 升序）
- `prd`（全部必须逐字原文粘贴）：
  - `fp_artifact_rows`：`|-` 原文粘贴 PRD `8.0` 表：表头 + 分隔行 + 本 Story 的 `S_fp` 行（按 `FP-001` 升序）
  - `api_blocks`：若 `S_api` 为空则写 `N/A`；否则 `|-` 按 `API-###` 升序逐块原文粘贴（每块从标题行开始到下一条 `#### 9.3.*` 之前；包含标题行锚点）
  - `table_blocks`：若 `S_tbl` 为空则写 `N/A`；否则 `|-` 按 `TBL-###` 升序逐块原文粘贴（每块从标题行开始到下一条 `#### 8.2.*` 之前；包含标题行锚点）
  - `rule_rows`：若 `S_prd_br` 为空则写 `N/A`；否则 `|-` 原文粘贴 PRD 第 6 节规则表：表头 + 分隔行 + 被引用 `BR-###` 行（按 ID 升序）

  2. 输出：
     - `PASS`
     - `已写入：docs/story-$ARGUMENTS-exec-pack.yaml`
     - `下一步：/story $ARGUMENTS`

## 开始

请提供 Story 编号（例如：`/story-pack 1`）。我会写入 `docs/story-$ARGUMENTS-exec-pack.yaml`。
