# 阶段4a: Story 拆分校验（结构/阈值）

读取：`docs/split-plan.yaml`、`docs/story-*-*.md` | 写入：`docs/split-check-index-pack.yaml`（仅无 `FAIL`；`PASS/DECISION` 都写） | 模板：`.claude/skills/textum/assets/split-check-index-pack-template.yaml`

做“结构/一致性/阈值”校验。

## 输出（DECISION 不阻断）

- 若存在任何 `FAIL`（含阈值 FAIL 与门禁 FAIL）：
  - 输出 `FAIL` 清单（`F-001` 起编号；每条必须包含以下字段）：
    - `定位`：目标文件（`docs/split-plan.yaml` 或 `docs/story-N-<slug>.md`）+（尽量）YAML 路径/章节名/指标名；避免行号
    - `问题`：1 句
    - `期望`：可机械执行的“替换目标/格式”（能推导就写出来）
    - `影响`：H/M/L
    - `修复`：只给 1 个动作（通常是“按定位修正对应文件”或“将 SPLIT_REPLAN_PACK 粘贴到 Split 规划重规划”）
  - 若包含阈值 FAIL：紧接着追加且仅追加 1 个 `SPLIT_REPLAN_PACK` 代码块
  - 末尾追加：
    - `修正：按 FAIL 清单逐条修复（若包含 SPLIT_REPLAN_PACK：将其粘贴到 Split 规划重规划；否则修正 docs/story-*-*.md 或 docs/split-plan.yaml）`
    - `重跑：Split 校验（结构/阈值）`
  - 然后结束（不写 pack）
- 否则（无 FAIL）：
  - 写入 `docs/split-check-index-pack.yaml`
  - 若存在任何 `DECISION`：输出 `DECISION` 清单（`D-001` 起编号；每条包含：问题 / 影响 / 建议动作），并在末尾追加：
    - `已写入：docs/split-check-index-pack.yaml`
    - `接受 DECISION：Split 校验（引用追溯/API Smoke）`
    - `不接受 DECISION：先处理 DECISION（Split 规划）后重跑 Split 校验（结构/阈值）`
  - 否则：输出：
    - `PASS`
    - `已写入：docs/split-check-index-pack.yaml`
    - `下一步：Split 校验（引用追溯/API Smoke）`

## 执行步骤（必须按序）

1. 解析 `docs/split-plan.yaml`（只抽取索引）：
   - `stories[]`：`story`、`n`、`slug`、`modules[]`、`prereq_stories[]`
   - `api_assignments[]`：`api`、`story`
2. 解析所有 `docs/story-*-*.md`（只抽取索引 + 机械计数）：
   - 解析 YAML front-matter（文件首部 `--- ... ---`），抽取：
     - `story/n/slug/title`
     - `modules/prereq_stories/fp_ids`
     - `refs.gc_br/refs.prd_br/refs.prd_tbl/refs.prd_api`
     - `artifacts.file/artifacts.cfg/artifacts.ext`
   - 计数口径：
     - `api_refs =` `refs.prd_api` 去重后数量
     - `tbl_refs =` `refs.prd_tbl` 去重后数量
     - `feature_points =` `fp_ids` 去重后数量
     - `acceptance_items =` `## 验收标准（必填）` 章节下 `- [ ]` 条目数
3. **大 Story 阈值（早期短路）**：
   - 若任一 Story 命中阈值 `FAIL`：输出 `FAIL + SPLIT_REPLAN_PACK` 并结束（不写 pack）
   - 否则：记录阈值 `DECISION`（若有），继续执行门禁
4. 执行门禁（见下）
5. 生成索引交接包（见下），写入 `docs/split-check-index-pack.yaml`

## 大 Story 阈值（早期短路）

### 机械计数口径（必须一致）

对每个 `docs/story-N-*.md`：

- `api_refs`：YAML front-matter `refs.prd_api` 去重数量
- `tbl_refs`：YAML front-matter `refs.prd_tbl` 去重数量
- `feature_points`：YAML front-matter `fp_ids` 去重数量
- `acceptance_items`：`## 验收标准（必填）` 章节下 `- [ ]` 条目数

### 默认阈值与升级规则（必须按此执行）

| 指标 | 正常 | DECISION | FAIL |
|------|------|----------|------|
| `api_refs` | `≤ 3` | `4–5` | `≥ 6` |
| `tbl_refs` | `≤ 2` | `= 3` | `≥ 4` |
| `feature_points` | `≤ 8` | `9–12` | `≥ 13` |
| `acceptance_items` | `≤ 10` | `11–15` | `≥ 16` |

升级规则：

机械判定步骤（必须；不得跳步/改写）：
1. 对每个 Story 先计算 4 个整数指标：`api_refs` / `tbl_refs` / `feature_points` / `acceptance_items`（计数口径见上文；必须按去重口径）
2. 对每个指标按上表分类到 3 档之一，并记录命中列表：
   - `fail_hits`: [{metric, value, threshold}...]（命中 FAIL 档的全部指标；可为空）
   - `decision_hits`: [{metric, value, threshold}...]（命中 DECISION 档的全部指标；可为空）
3. 产出该 Story 的阈值结论（按序判定）：
   - 若 `fail_hits` 非空 → `FAIL`
   - 否则，若 `decision_hits.length >= 2` → `FAIL`（DECISION 升级）
   - 否则，若 `decision_hits.length == 1` → `DECISION`
   - 否则 → `PASS`
4. 输出一致性要求：
   - 若阈值结论为 `FAIL`：FAIL 清单必须列出 `fail_hits` 与 `decision_hits`；并将其分别写入 `SPLIT_REPLAN_PACK.oversized_stories[].metrics.fail_hits` 与 `SPLIT_REPLAN_PACK.oversized_stories[].metrics.decision_hits`
   - 若阈值结论为 `DECISION`：DECISION 清单必须列出 `decision_hits`（此时长度固定为 `1`）

### 触发后输出（仅阈值 FAIL 时；必须）

1. 输出 `FAIL` 清单（`F-001` 起编号；每条必须包含：定位 / 问题 / 期望 / 影响 / 修复；且 `定位` 必须包含：Story 文件名 + 触发指标 + 命中阈值）
2. 紧接着追加且仅追加 1 个代码块 `SPLIT_REPLAN_PACK`（供复制到 Split 规划）
3. 立即结束（不写 pack）

### 阈值 DECISION 记录（必须；不短路）

- 对每个命中阈值 `DECISION` 的 Story：生成 1 条 `DECISION` 项（`D-001` 起编号），必须包含：
  - `docs/story-N-<slug>.md`
  - 命中指标与阈值（`api_refs/tbl_refs/feature_points/acceptance_items`）
- 建议动作：Split 规划（收敛边界/拆分），或接受后继续 Split 校验（引用追溯/API Smoke）

`SPLIT_REPLAN_PACK`（必须严格输出一个代码块）：

```yaml
SPLIT_REPLAN_PACK: v1
trigger: "oversized_story"
oversized_stories:
  - story: "Story N"
    story_file: "docs/story-N-<slug>.md"
    slug: "<slug>"
    modules: ["M-01"]
    prereq_stories: ["Story 1"]
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
  - "Story 必须重新按 1..N 连续编号；并同步改写 split-plan `stories[]`/`api_assignments[]` 与所有 Story front-matter"
  - "每个 API 必须唯一归属且全覆盖（split-plan api_assignments + Story front-matter refs.prd_api 一致）"
  - "拆分后的每个 Story 必须满足阈值；否则继续拆"
```

## 门禁（未触发早期短路时才执行）

### A) split-plan 格式与稳定可解析

- `docs/split-plan.yaml` 必须可解析为 YAML，且根键必须为 `SPLIT_PLAN_PACK: v1`
- 必须存在键：`stories`、`api_assignments`
- `stories` 至少 1 条；且编号必须为 `Story 1..N` 连续（`stories[].n` 连续且 `stories[].story == "Story {n}"`）
- `stories[].slug` 必须唯一且符合 `kebab-case`
- `docs/split-plan.yaml` 中不得出现 `TBD`

### B) Story 文件集合与编号

- 至少存在 1 个 `docs/story-*-*.md`
- 文件名必须匹配 `docs/story-[编号]-[slug].md`；同一编号不得重复
- 与 split-plan `stories[]` 必须 1:1 对应：
  - 不得缺失 Story；不得多出残留 Story
  - `slug` 必须一致
  - Story front-matter `modules` 与 `prereq_stories` 必须与 split-plan 一致（集合一致即可）

### C) Story 模板完整性与占位符

- 每个 Story 必须包含模板全部章节；无内容写 `N/A`，不得省略
- 每个 Story 必须包含 YAML front-matter（首部 `--- ... ---`），且必须存在键：`STORY`、`story`、`n`、`slug`、`modules`、`prereq_stories`、`fp_ids`、`refs`、`artifacts`
- `fp_ids` 必须至少 1 个，且每个必须为 `FP-001`（3 位数字）；禁止 `FP-01`、`FP-###` 等
- `## 功能点（必填）` 章节必须至少 1 条 `- ` 条目，且条目数必须等于 `fp_ids` 去重数量
- Story 中不得出现 fenced code blocks（```）；出现即 `FAIL`
- 占位符门禁：剔除 fenced code blocks 后逐行检查；不得残留占位符：`TBD`、`[...]`、`Story N`、`M-xx`、`FP-###`、`BR-###`、`TBL-###`、`API-###`、`ART:FILE:[path_glob]`、`ART:CFG:[key]`、`ART:EXT:[system]` 等
- 方括号门禁（避免漏检）：剔除 fenced code blocks 后逐行检查；若出现 `[` 或 `]`：仅允许
  - 行首任务清单标记：`- [ ]` / `- [x]` / `* [ ]` / `* [x]`
  - Markdown 链接：`[text](...)`
  - 路径/路由 token 中的 Next.js 风格动态段（`[` 必须紧跟在 `/` 或 `\\` 之后，且 `[]` 内不得包含空白、`/`、`\\`），如 `/posts/[slug]`、`pages/[id].tsx`、`ART:FILE:content/[slug].md`
  - 其余一律 `FAIL`
- 方括号门禁执行范围：**不扫描 YAML front-matter 区域**（仅用于避免 YAML `[]` 误伤）；但占位符门禁必须扫描 YAML front-matter

### D) 依赖合法性

- 引用的 `前置Story` 必须存在；禁止自依赖；依赖无环
- 若 `Story A` 依赖 `Story B`：必须满足 `B < A`

### E) split-plan ↔ Story 的 API 分配一致性（不读 PRD；只校验“是否按规划写”）

- 若 split-plan `api_assignments` 为空：
  - 所有 Story front-matter `refs.prd_api` 必须为空数组
  - 所有 Story 的 `## 接口` 章节正文必须严格为 1 行 `N/A`
- 若 split-plan `api_assignments` 非空：
  - split-plan 中每个 `api_assignments[].api` 必须在且仅在 1 个 Story 中出现（按 Story front-matter `refs.prd_api` 去重集合）
  - 对每个 Story：其 `refs.prd_api` 去重集合必须与 split-plan 分配到该 Story 的 API 集合一致（不得缺失/多写）

## 生成索引交接包（必须；无 FAIL 时写入）

规则：
- 严格按 `.claude/skills/textum/assets/split-check-index-pack-template.yaml` 的 YAML 结构写入（纯 YAML；不含 ```）
- `modules` 解析为 `["M-01","M-02"]` 数组；`prereq_stories` 解析为 `["Story 1"]` 数组（无则空数组）
- 引用只记录 ID（去掉 `GC#`/`PRD#` 前缀），并分类输出：
  - `fp_ids`: `FP-001`
  - `gc_br_ids`: `BR-###`
  - `prd_api_ids`: `API-###`
  - `prd_tbl_ids`: `TBL-###`
  - `prd_br_ids`: `BR-###`
- `summary.refs.*` 为全量 union（去重、升序）
- 不得残留占位符（如 `TBD`、`[...]`、`###`）

## 开始

请确认 `docs/split-plan.yaml` 与 `docs/story-*-*.md` 已存在。
