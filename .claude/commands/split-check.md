# 阶段4: Story 拆分校验

## 读取（只读）

- `docs/split-plan.md`
- `docs/story-*-*.md`（所有 Story 文件）
- `docs/GLOBAL-CONTEXT.md`
- `docs/PRD.md`（只读；不修改）

## 输出（只读）

- 若存在任何 `FAIL`：只输出 `FAIL` 清单并结束
- 否则若存在任何 `DECISION`：只输出 `DECISION` 清单并结束
- 否则：输出 `PASS`，并提示在新窗口运行 `/backfill`
- 若触发“大 Story 阈值（早期短路）”：输出 `FAIL` 或 `DECISION` 清单 + 1 个 `SPLIT_REPLAN_PACK` 代码块，然后立即结束（不继续后续校验；不提示 `/backfill`）

## 执行步骤（必须按序）

1. 解析 `docs/split-plan.md`（只抽取索引）：
   - 第 1 节 Story 表：`Story N`、`slug`、`模块`、`前置Story`
   - 第 2 节 API 分配表：`API-### -> Story N`
2. 解析所有 `docs/story-*-*.md`（只抽取索引 + 机械计数）：
   - `模块（必填）`、`前置Story`
   - 引用：`GC#BR-###`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`
   - 计数：`api_refs` / `tbl_refs` / `feature_points` / `acceptance_items`
3. **大 Story 阈值（早期短路）**：若触发阈值 → 输出 `FAIL/DECISION + SPLIT_REPLAN_PACK` 并结束
4. 解析 `docs/GLOBAL-CONTEXT.md`：只读取第 4 节业务规则表，得到合法 `BR-###` 集合
5. 解析 `docs/PRD.md`：只读取 `5.1`（模块清单）、`8.1`（表清单）、`9.2`（接口清单）得到 `P0` 模块集合、`TBL-###` 集合、`API-###` 集合；必要时按 `PRD#<ID>` 定位块核验（接口/表优先用标题行锚点 `<!-- PRD#API-### -->` / `<!-- PRD#TBL-### -->`）
6. 执行全量门禁（见下）

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

## 全量门禁（未触发早期短路时才执行）

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

### D) 引用一致性（可追溯）

- `GC#BR-###`：必须存在于 `docs/GLOBAL-CONTEXT.md` 第 4 节规则表
- `PRD#API-###`：对应 `API-###` 必须存在于 PRD `9.2 接口清单`
- `PRD#TBL-###`：对应 `TBL-###` 必须能在 PRD `8.1/8.2` 中定位到
- `PRD#BR-###`：对应 `BR-###` 必须存在于 PRD 第 6 节规则表

### E) 依赖合法性

- 引用的 `前置Story` 必须存在；禁止自依赖；依赖无环
- 若 `Story A` 依赖 `Story B`：必须满足 `B < A`

### F) 覆盖性与 API 唯一归属

- PRD `5.1` 的每个 `P0` 模块至少被 1 个 Story 覆盖（按 Story 的 `模块（必填）`）
- 若 PRD `9.2` 为 `N/A`（无 API，API 集合为空）：
  - split-plan 第 2 节必须只保留表头且无数据行
  - 所有 Story 的“接口”章节必须为 `N/A`，且不得出现任何 `PRD#API-###`
  - 跳过本节其余 API 覆盖/唯一归属检查
- 否则（有 API）：
  - split-plan 第 2 节必须与 PRD `9.2` 一致：覆盖全部 `API-###` 且仅出现一次；不得出现 PRD `9.2` 中不存在的 `API-###`
  - Story 文件“接口”章节：每个 `PRD#API-###` 必须且仅出现于 1 个 Story，且与 split-plan 分配完全一致（不得漂移/漏写/多写）

## 输出格式（必须）

- `FAIL`：`F-001` 起编号；每条包含：文件名 + 问题 + 修复方式（改 Story / 回 `/split-plan` / 重新 `/split`）
- `DECISION`：`D-001` 起编号；每条包含：风险 + 需要用户确认的问题
- `PASS`：仅提示下一步：在新窗口运行 `/backfill`

## 开始

请确认 `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/split-plan.md`、`docs/story-*-*.md` 已存在。
