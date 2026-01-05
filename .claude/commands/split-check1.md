# 阶段4a: Story 拆分校验（Core / split-check1）

读取 `docs/split-plan.md` 与所有 `docs/story-*-*.md`，做“结构/一致性/阈值”校验；仅在 `PASS` 时写入索引交接包 `docs/split-check-index-pack.yaml`；不读取 PRD/GC。

## 读取 / 写入

- 读取：`docs/split-plan.md`、`docs/story-*-*.md`
- 写入（仅 PASS 时）：`docs/split-check-index-pack.yaml`
- 模板：`.claude/textum/split-check-index-pack-template.md`

## 输出

- 若触发“大 Story 阈值（早期短路）”：输出 `FAIL` 或 `DECISION` 清单 + 1 个 `SPLIT_REPLAN_PACK` 代码块，然后结束（不写 pack）
- 否则若存在任何 `FAIL`：输出 `FAIL` 清单，并在末尾追加：
  - `下一步：/split（如需调整规划则先 /split-plan）`
  - `重跑：/split-check1`
  然后结束（不写 pack）
- 否则：写入 `docs/split-check-index-pack.yaml`，输出：
  - `PASS`
  - `已写入：docs/split-check-index-pack.yaml`
  - `下一步：/split-check2`

## 执行步骤（必须按序）

1. 解析 `docs/split-plan.md`（只抽取索引）：
   - 第 1 节 Story 表：`Story N`、`slug`、`模块`、`前置Story`
   - 第 2 节 API 分配表：`API-### -> Story N`
2. 解析所有 `docs/story-*-*.md`（只抽取索引 + 机械计数）：
   - `模块（必填）`、`前置Story`
   - 引用：`GC#BR-###`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`
   - 计数：`api_refs` / `tbl_refs` / `feature_points` / `acceptance_items`
3. **大 Story 阈值（早期短路）**：若触发阈值 → 输出 `FAIL/DECISION + SPLIT_REPLAN_PACK` 并结束
4. 执行门禁（见下）
5. 生成索引交接包（见下），写入 `docs/split-check-index-pack.yaml`

## 大 Story 阈值（早期短路）

### 机械计数口径（必须一致）

对每个 `docs/story-N-*.md`：

- `api_refs`：该文件中出现的唯一 `PRD#API-###` 数量（去重）
- `tbl_refs`：该文件中出现的唯一 `PRD#TBL-###` 数量（去重）
- `feature_points`：`## 功能点（必填）` 章节下 `- ` 条目数（`N/A` 视为 0）
- `acceptance_items`：`## 验收标准（必填）` 章节下 `- [ ]` 条目数

### 默认阈值与升级规则（必须按此执行）

| 指标 | 正常 | DECISION | FAIL |
|------|------|----------|------|
| `api_refs` | `≤ 3` | `4–5` | `≥ 6` |
| `tbl_refs` | `≤ 2` | `= 3` | `≥ 4` |
| `feature_points` | `≤ 8` | `9–12` | `≥ 13` |
| `acceptance_items` | `≤ 10` | `11–15` | `≥ 16` |

升级规则：
- 命中任一 `FAIL` 阈值 → 该 Story 为 `FAIL`
- 否则，若同一 Story 命中 **≥ 2 个** `DECISION` 阈值 → 升级为 `FAIL`
- 否则，若命中任一 `DECISION` 阈值 → 该 Story 为 `DECISION`

### 触发后输出（必须）

1. 输出 `FAIL` 或 `DECISION` 清单（每条包含：Story 文件名 + 触发指标 + 命中阈值）
2. 紧接着追加且仅追加 1 个代码块 `SPLIT_REPLAN_PACK`（供复制到 `/split-plan`）
3. 立即结束

`SPLIT_REPLAN_PACK`（必须严格输出一个代码块）：

```yaml
SPLIT_REPLAN_PACK: v1
trigger: "oversized_story"
oversized_stories:
  - story: "Story N"
    story_file: "docs/story-N-<slug>.md"
    slug: "<slug>"
    modules: ["M-xx"]
    prereq_stories: ["Story X"]
    metrics:
      api_refs: 0
      tbl_refs: 0
      feature_points: 0
      acceptance_items: 0
      decision_hits: []
      fail_hits: []
    api_assignments_from_split_plan: ["API-001"]
constraints:
  - "拆分后的新 Story 必须插入在原 Story 之后，顺序可执行（前置编号 < 当前编号）"
  - "Story 必须重新按 1..N 连续编号；并同步改写所有前置依赖与 API 分配表引用"
  - "每个 API 必须唯一归属且全覆盖（split-plan 第2节 + Story 接口章节一致）"
  - "拆分后的每个 Story 必须满足阈值；否则继续拆"
```

## 门禁（未触发早期短路时才执行）

### A) split-plan 格式与稳定可解析

- 必须包含章节：`## 1. Story 列表（必须）`、`## 2. API 分配表（必须）`
- Story 表表头必须为：`| Story | slug | 模块 | 目标（一句话） | 前置Story |`
- API 表表头必须为：`| API | Story | 说明 |`

### B) Story 文件集合与编号

- 至少存在 1 个 `docs/story-*-*.md`
- 文件名必须匹配 `docs/story-[编号]-[slug].md`；同一编号不得重复
- 与 split-plan 第 1 节必须 1:1 对应：
  - 不得缺失 Story；不得多出残留 Story
  - `slug` 必须一致
  - Story 内 `模块（必填）` 与 `前置Story` 必须与 split-plan 一致（集合一致即可）

### C) Story 模板完整性与占位符

- 每个 Story 必须包含模板全部章节；无内容写 `N/A`，不得省略
- 不得残留占位符：`[功能描述]`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`、`GC#BR-###` 等
- 所有 PRD 引用必须为具体数字：`PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`

### D) 依赖合法性

- 引用的 `前置Story` 必须存在；禁止自依赖；依赖无环
- 若 `Story A` 依赖 `Story B`：必须满足 `B < A`

### E) split-plan ↔ Story 的 API 分配一致性（不读 PRD；只校验“是否按规划写”）

- 若 split-plan 第 2 节无任何 API 数据行：
  - 所有 Story 不得出现任何 `PRD#API-###`
  - 所有 Story 的“接口”章节必须为 `N/A`
- 若 split-plan 第 2 节存在 API 分配：
  - split-plan 中每个 `API-###` 必须在且仅在 1 个 Story 中出现（按 Story 文件内 `PRD#API-###` 去重集合）
  - 对每个 Story：其 `PRD#API-###` 去重集合必须与 split-plan 分配到该 Story 的 `API-###` 集合一致（不得缺失/多写）

## 生成索引交接包（必须；仅 PASS 时写入）

目标：生成一个小而稳定的索引交接包，供后续对齐校验使用，避免复读所有 Story 文件。

规则：
- 严格按 `.claude/textum/split-check-index-pack-template.md` 的 YAML 结构写入（纯 YAML；不含 ```）
- `modules` 解析为 `["M-01","M-02"]` 数组；`prereq_stories` 解析为 `["Story 1"]` 数组（无则空数组）
- 引用只记录 ID（去掉 `GC#`/`PRD#` 前缀），并分类输出：
  - `gc_br_ids`: `BR-###`
  - `prd_api_ids`: `API-###`
  - `prd_tbl_ids`: `TBL-###`
  - `prd_br_ids`: `BR-###`
- `summary.refs.*` 为全量 union（去重、升序）
- 不得残留占位符（如 `[...]`、`###`）

## 开始

请确认 `docs/split-plan.md` 与 `docs/story-*-*.md` 已存在。
