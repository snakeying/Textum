# 阶段5: Split checkout（导出 Story 依赖图 / split-checkout）

读取：`docs/story-*-*.md` | 写入：`docs/story-mermaid.md` | 模板：`N/A`

仅导出依赖图；不修改任何 Story 文件。

## 最小读取（必须；避免通读）

1. 读取所有 Story：只解析 YAML front-matter（首部 `--- ... ---`）

## 输出规则（只读）

- 不输出任何 Story 原文
- 若存在任何 `FAIL`：
  - 输出 `FAIL` 清单（`F-001` 起编号；每条必须包含以下字段）：
    - `定位`：目标 Story 文件（`docs/story-N-<slug>.md`）+ YAML front-matter key（如 `prereq_stories`）或门禁项；避免行号
    - `问题`：1 句
    - `期望`：可机械执行的“替换目标/格式”（能推导就写出来）
    - `影响`：H/M/L
    - `修复`：只给 1 个动作（通常是“按定位修正对应 Story 文件”）
  - 末尾追加：
    - `修正：按 FAIL 清单逐条修复 docs/story-*-*.md 后重跑 /split-checkout`
    - `重跑：/split-checkout`
  - 然后结束（不写文件）
- 否则：
  - 覆盖写入 `docs/story-mermaid.md`
  - 输出：
    - `PASS`
    - `已写入：docs/story-mermaid.md`
    - `下一步：选择一个可执行的 Story 运行 /story-check N（例如：/story-check 1）`

## 硬约束（必须遵守）

- Mermaid 图必须仅由 Story 编号与 `prereq_stories` 推导（不得脑补额外依赖）

## 执行步骤（必须按序）

### 1) 解析所有 Story（只看 YAML front-matter）

对每个 `docs/story-*-*.md`：

- 必须存在 YAML front-matter（文件首部 `--- ... ---`），且必须可解析为 YAML；否则 `FAIL`
- 根键必须包含 `STORY: v1`；否则 `FAIL`
- 抽取（仅用于构图）：
  - `story`（严格形如 `Story 1`）
  - `n`（整数）
  - `prereq_stories[]`（形如 `["Story 1"]`；无依赖则空数组）

构造：

- `AllStories =` 按 `n` 升序的 `Story N` 列表
- `Edges =` 对每个 `Story N` 与其每条 `prereq_stories`，生成有向边：`prereq -> Story N`

### 2) 门禁（任一命中即停止；不写文件）

- 至少存在 1 个 `docs/story-*-*.md`
- `AllStories` 中 `n` 必须唯一
- 每个 Story：
  - `story` 必须严格等于 `"Story {n}"`
  - `prereq_stories[]` 中每个 `Story X` 必须存在于 `AllStories` 且 `X < n`

### 3) 写入 `docs/story-mermaid.md`（覆盖写；严格按序）

写入内容必须严格为：

1. 第一行：`# Story 依赖图`
2. 第二行：空行
3. 第三行开始写入 1 个 Mermaid fenced code block（围栏为 3 个反引号字符 `` ` ``）：
   - 开始行必须为：三个反引号 + `mermaid`
   - 第二行必须为：`flowchart TD`
   - 节点（必须全量覆盖 `AllStories`；按 `n` 升序逐行输出）：
     - 对每个 `Story n`：输出一行 `Story_{n}["Story {n}"]`
   - 边（必须全量覆盖 `Edges`；按 `prereq_n` 升序、再按 `story_n` 升序逐行输出）：
     - 对每条边 `Story a -> Story b`：输出一行 `Story_{a} --> Story_{b}`
   - 结束行必须为：三个反引号

节点命名规则（必须）：必须生成 `Story_1["Story 1"]` 形式的节点（避免空格导致 Mermaid 解析失败）。

## 开始

请确认 `docs/story-*-*.md` 已存在。
