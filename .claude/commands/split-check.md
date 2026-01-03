# 阶段4: Story 拆分校验

## 读取

- `docs/PRD.md`（只读）
- `docs/GLOBAL-CONTEXT.md`
- `docs/split-plan.md`
- `docs/story-*-*.md`（所有 Story 文件）

## 输出（只读）

只输出“问题清单 + 如何修复（改 Story / 重新 `/split`）”。**不修改任何文件**；不自动执行其它命令。

> ⚠️ `docs/PRD.md` 只读（禁止修改）。发现规格缺口/矛盾 → `FAIL`，由用户决定是否回到 `/prd` 修正规格。

输出规则：
- 如存在任何 `FAIL`：只输出 `FAIL` 条目并结束（不输出 `DECISION/PASS`；不提示运行 `/backfill`）
- 仅当无 `FAIL` 且存在 `DECISION`：只输出 `DECISION` 条目并结束（不输出 `PASS`；不提示运行 `/backfill`）
- 仅当无 `FAIL/DECISION`：输出 `PASS`，并提示在新窗口手动运行 `/backfill`

## 注意力控制（必须遵守）

为避免“PRD + GC + 多个 Story”带来的注意力稀释，本命令必须按“先索引、后核对、只读片段”的方式执行：

0. **只读 PRD**：`docs/PRD.md` 只读（禁止修改）
1. **先读 split-plan 只抽取索引信息**（不要在此阶段理解业务细节，也不要输出索引表）：
   - 第 1 节 Story 表：`Story N`、`slug`、`模块`、`前置Story`
   - 第 2 节 API 分配表：`API-### -> Story N`
2. **再读所有 Story，但只抽取索引信息**（不要在此阶段理解业务细节，也不要输出索引表）：
   - `模块（必填）`
   - `前置Story`
   - `GC#BR-###`
   - `PRD#API-###`（若该 Story “接口”章节非 `N/A`，则必须有）
   - `PRD#TBL-###`（若该 Story “数据变更”章节非 `N/A`，则必须有）
   - `PRD#BR-###`（如适用；仅当 Story 直接引用 PRD 规则）
3. **再读 GC 只看第 4 节业务规则表**：拿到合法的 `BR-###` 集合
4. **再读 PRD 只看 5.1（模块清单）、8.1（表清单）、9.2（接口清单）**：拿到 `P0` 模块集合、`TBL-###` 表集合与 `API-###` 接口集合（不要通读 PRD）
5. **最后只按需读取 PRD 片段**：仅在需要验证时，按 `PRD#<ID>` 在 PRD 中定位对应块/表格行进行核验（不要通读 PRD；不要把片段粘贴到输出）

## FAIL 校验项（严格拦截）

### 0) split-plan 文件与格式（必须稳定可读）

- `docs/split-plan.md` 必须存在
- `docs/split-plan.md` 必须符合 `.claude/textum/split-plan-template.md` 的固定格式：
  - 必须包含章节标题：`## 1. Story 列表（必须）` 与 `## 2. API 分配表（必须）`
  - Story 表表头必须为：`| Story | slug | 模块 | 目标（一句话） | 前置Story |`
  - API 表表头必须为：`| API | Story | 说明 |`

若 split-plan 缺失/格式不稳定，直接 `FAIL`：提示用户回到 `/split-plan` 重新生成（不要尝试“猜测解析”）。

### 1) Story 文件与编号

- 至少存在 1 个 `docs/story-*-*.md`
- 文件名必须匹配 `docs/story-[编号]-[slug].md`
- 同一个 `[编号]` 只能对应 1 个 Story 文件（禁止重复编号）

并校验与 split-plan 一致（必须全部满足）：
- split-plan 第 1 节列出的每个 `Story N` 都必须有对应的 `docs/story-N-<slug>.md`
- 每个 `docs/story-N-<slug>.md` 都必须能在 split-plan 第 1 节找到对应的 `Story N` 行（禁止额外/残留 Story 文件）
- 每个 `docs/story-N-<slug>.md` 的 `slug` 必须与 split-plan 第 1 节该行一致（禁止漂移）
- 每个 Story 文件的 `模块（必填）` 必须与 split-plan 第 1 节该行 `模块` 一致（同一集合；顺序可不同）
- 每个 Story 文件“依赖”章节的 `前置Story` 必须与 split-plan 第 1 节该行 `前置Story` 一致（同一集合；顺序可不同）

### 2) Story 模板完整性（不得缺章）

每个 Story 必须包含以下章节；无内容按模板写 `N/A`，但不得省略章节：

- `模块（必填）`
- `## 功能点（必填）`
- `## 依赖（必填）`
- `## 业务规则（必填；无则写 N/A）`
- `## 数据变更（如无写 N/A）`
- `## 接口（如无写 N/A）`
- `## 验收标准（必填）`
- `## 测试要求（必填；无则写 N/A）`
- `## 注意（如无写 N/A）`

若出现模板占位符未替换（如 `[功能描述]`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`、`GC#BR-###` 等），视为 `FAIL`。
若出现任何 PRD 引用不是 `PRD#...` 格式，也视为 `FAIL`。

### 3) 引用与格式（必须可定位且可追溯）

- 所有 PRD 引用必须使用 `PRD#<ID>`，且 `<ID>` 必须为具体数字（如 `PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`）
  - 每个 Story 的“接口/数据变更/业务规则”必须能定位到 PRD 对应内容：
  - 接口（如适用）：若该 Story “接口”章节非 `N/A`：
    - 必须至少包含 1 个 `PRD#API-###`（具体数字：`PRD#API-001` 形式）
    - 对每个 `PRD#API-###`：校验该 `API-###` 存在于 PRD `9.2 接口清单`
  - 数据表（如适用）：若该 Story “数据变更”章节非 `N/A`：
    - 必须至少包含 1 个 `PRD#TBL-###`（具体数字：`PRD#TBL-001` 形式）
    - 对每个 `PRD#TBL-###`：校验该 `TBL-###` 能在 PRD `8.1/8.2` 中定位到
  - 规则（如需直接引用 PRD）：使用 `PRD#BR-###`，并校验该 `BR-###` 存在于 PRD `6. 业务规则` 的规则表
  - `PRD#<ID>` 作为最小阅读范围；除非需要核验内容，否则不要通读 PRD

### 4) 规则一致性（GC#BR 必须存在）

- 收集所有 Story 中的 `GC#BR-###`
- 校验每个引用的 `BR-###` 都存在于 `docs/GLOBAL-CONTEXT.md` 第 4 节业务规则表

### 5) 依赖合法性（无环）

- 每个 Story 的“前置Story”引用的编号必须存在
- 禁止自依赖
- 依赖图必须无环；若有环，输出形成环的 Story 链路
- **编号顺序必须可执行**：若 Story A 声明前置 Story B，则必须满足 `B < A`（确保用户可按 `/story 1..N` 顺序执行）

### 6) 覆盖性（P0 模块 + 接口）

- 从 PRD `5.1 模块清单` 读取所有 `P0` 模块：每个 `P0` 模块至少对应 1 个 Story（按 Story 的“模块（必填）”字段匹配）
- PRD `9.2 接口清单` 必须为每条接口提供且仅提供一个 `API-###`（缺失/重复均视为 `FAIL`）
- 从 PRD `9.2 接口清单` 读取所有 `API-###`，建立“应覆盖接口集合”
- 从所有 Story 的“接口”章节收集其 `PRD#API-###`，建立“已覆盖接口集合”
- 对比集合差集：任何 PRD `9.2` 中的 `API-###` 未被覆盖 → `FAIL`

并新增“唯一归属”门禁（必须过）：
- 每个 PRD `API-###` 必须且仅能归属到 1 个 Story：
  - split-plan 第 2 节中：每个 `API-###` 必须且仅出现一次
  - split-plan 第 2 节中：必须覆盖 PRD `9.2 接口清单` 的所有 `API-###`（缺失/多余均 `FAIL`）
  - Story 文件中：每个 `PRD#API-###` 必须且仅出现在 1 个 Story 的“接口”章节
  - 且 Story 文件中的归属必须与 split-plan 第 2 节一致（`API-### -> Story N` 不得漂移；也不得“多写/漏写”）
  - 对每个 `Story N`：其“接口”章节内出现的 `PRD#API-###` 集合必须与 split-plan 分配给该 `Story N` 的 `API-###` 集合完全一致

> 若发现“Story 想实现的能力在 PRD 中不存在/自相矛盾”，直接 `FAIL` 并停止；由用户决定是否回到 `/prd` 修正规格。

## DECISION 校验项（需要用户明确确认）

- 验收标准过少或不可验证（例如只有空泛描述、缺少可复现步骤）
- 关键 Story（覆盖 `P0` 模块或核心接口）测试要求为 `N/A`

## 输出格式（必须）

按以下结构输出（只输出清单，不输出文件内容）：

- `FAIL`：编号 + 文件名 + 问题描述 + 修复方式（改 Story / 重新 `/split`）
- `DECISION`：编号 + 文件名 + 风险说明 + 需要用户确认的问题（继续/回退修复）
- `PASS`：仅提示下一步动作：在新窗口手动运行 `/backfill`

## 开始

请确认 `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/split-plan.md`、`docs/story-*-*.md` 已存在。
