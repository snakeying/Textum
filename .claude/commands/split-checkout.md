# 阶段5: Split checkout（导出 Story 依赖图 / split-checkout）

## 最小读取（必须；避免通读）

1. 读取所有 Story：只解析 YAML front-matter（不通读正文）

## 读取 / 写入

- 读取：`docs/story-*-*.md`
- 写入：`docs/story-mermaid.md`

## 硬约束

- Mermaid 图必须仅由 Story 编号与 `prereq_stories` 推导（不得脑补额外依赖）

## 执行步骤（必须按序）

### 1) 解析所有 Story（只看 YAML front-matter）

对每个 `docs/story-*-*.md`：

- 抽取：
  - `story`（形如 `Story 1`）
  - `n`（数字）
  - `prereq_stories[]`（形如 `["Story 1"]`）

构造：

- `AllStories =` 按 `n` 升序的 `Story N` 列表
- `Edges =` 对每个 `Story N` 与其每条 `prereq_stories`，生成有向边：`prereq -> Story N`

### 2) 门禁（任一命中即停止；不写文件）

- 至少存在 1 个 `docs/story-*-*.md`
- `AllStories` 中 `n` 必须唯一
- 每个 Story：
  - `story` 必须严格等于 `"Story {n}"`
  - `prereq_stories[]` 中每个 `Story X` 必须存在于 `AllStories` 且 `X < n`
- 若依赖存在环：输出环路并停止

### 3) 写入 `docs/story-mermaid.md`（覆盖写；严格按序）

写入内容必须严格为：

1. 第一行：`# Story 依赖图`
2. 第二行：空行
3. 第三行开始写入 1 个 Mermaid code block：
   - 第一行必须为：```` ```mermaid ````
   - 第二行必须为：`flowchart TD`
   - 节点（必须全量覆盖 `AllStories`；按 `n` 升序逐行输出）：
     - 对每个 `Story n`：输出一行 `Story_{n}["Story {n}"]`
   - 边（必须全量覆盖 `Edges`；按 `prereq_n` 升序、再按 `story_n` 升序逐行输出）：
     - 对每条边 `Story a -> Story b`：输出一行 `Story_{a} --> Story_{b}`
   - 末行必须为：```` ``` ````

节点命名规则（必须）：必须生成 `Story_1["Story 1"]` 形式的节点（避免空格导致 Mermaid 解析失败）。

## 输出（必须严格）

- `PASS`
- `已写入：docs/story-mermaid.md`
- `下一步：/story-check 1`
