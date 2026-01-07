# 阶段5: GLOBAL-CONTEXT 回填（规则涉及 Story + 依赖图）

## 最小读取（必须；避免通读）

1. 读取所有 Story：只解析 YAML front-matter（不通读正文）
2. 读取 GC：仅第 4 节规则表 + 第 9 节依赖图（定位替换范围）

## 读取 / 写入

- 读取：`docs/GLOBAL-CONTEXT.md`、`docs/story-*-*.md`
- 写入：
  - 更新 `docs/GLOBAL-CONTEXT.md`
  - 生成 `docs/story-mermaid.md`

## 更新范围（只做小更新）

1. GC 第 4 节规则表：回填 “涉及Story” 列
2. GC 第 9 节：回填 Story 依赖图（Mermaid）
3. 新增 `docs/story-mermaid.md`：仅包含依赖图（Mermaid）

## 硬约束

- 不改变规则 `BR-###` 与规则文本（只更新 “涉及Story” 列）
- 不做大段重排（避免无意义 diff）
- Mermaid 图必须仅由 Story 编号与 `prereq_stories` 推导（不得脑补额外依赖）

## 执行步骤（必须按序）

### 1) 解析所有 Story（只看 YAML front-matter）

对每个 `docs/story-*-*.md`：

- 抽取：
  - `story`（形如 `Story 1`）
  - `n`（数字）
  - `prereq_stories[]`（形如 `["Story 1"]`）
  - `refs.gc_br[]`（形如 `["BR-001"]`）

构造：

- `AllStories =` 按 `n` 升序的 `Story N` 列表
- `Edges =` 对每个 `Story N` 与其每条 `prereq_stories`，生成有向边：`prereq -> Story N`
- `BR_to_Stories =` `BR-### -> [Story N,...]`（按 `n` 升序；去重）

### 2) 门禁（任一命中即停止；不写回）

- 若任一 `prereq_stories` 引用的 `Story X` 不在 `AllStories`：输出缺失清单并停止
- 若依赖存在环：输出环路并停止
- 读取 GC 第 4 节规则表的 ID 列为集合 `GC_BR`；若 `refs.gc_br[]` 中任一 `BR-###` 不在 `GC_BR`：输出缺失清单并停止

### 3) 更新 `docs/GLOBAL-CONTEXT.md`

**3.1 回填规则表 “涉及Story”**

- 在 `## 4. 业务规则（必填）` 下定位规则表（表头必须包含：`| ID | 规则 | 涉及Story |`）
- 对表中每条规则 `BR-###`：
  - 若 `BR_to_Stories[BR-###]` 为空：将 “涉及Story” 单元格置空（移除 `TBD`）
  - 否则：写为 `Story 1, Story 3`（逗号+空格分隔；按编号升序；去重）

**3.2 回填第 9 节依赖图（Mermaid）**

- 在 `## 9. Story依赖图（必填；拆分后回填）` 标题下，用 **1 个 Mermaid code block** 整体替换原正文（覆盖写）：
  - 第一行必须为：```` ```mermaid ````
  - 第二行必须为：`flowchart TD`
  - 节点（必须全量覆盖 `AllStories`；按 `n` 升序逐行输出）：
    - 对每个 `Story n`：输出一行 `Story_{n}["Story {n}"]`
  - 边（必须全量覆盖 `Edges`；按 `prereq_n` 升序、再按 `story_n` 升序逐行输出）：
    - 对每条边 `Story a -> Story b`：输出一行 `Story_{a} --> Story_{b}`
  - 末行必须为：```` ``` ````

节点命名规则（必须）：必须生成 `Story_1["Story 1"]` 形式的节点（避免空格导致 Mermaid 解析失败）。

### 4) 生成 `docs/story-mermaid.md`

写入内容（覆盖写；严格按序）：

1. 第一行：`# Story 依赖图`
2. 第二行：空行
3. 从第三行开始：粘贴与 GC 第 9 节 **完全相同** 的 Mermaid code block（含起止 ``` 行）

## 完成后

- 提示用户按序运行：
  - `/story-check 1` → `/story-pack 1` → `/story 1`
