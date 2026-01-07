# 阶段4b: Story 拆分校验（PRD/GC 对齐 + API Smoke / split-check2）

读取 `docs/split-check-index-pack.yaml`，并对齐 `docs/GLOBAL-CONTEXT.md` 与 `docs/PRD.md` 做引用可追溯与（有 API 时）Smoke Test；不读取所有 Story 文件。

## 读取（只读）

- `docs/split-check-index-pack.yaml`（必须存在）
- `docs/GLOBAL-CONTEXT.md`
- `docs/PRD.md`（只读；不修改）

## 输出（只读）

- 若存在任何 `FAIL`：只输出 `FAIL` 清单并结束
- 否则：输出 `PASS`，并提示在新窗口运行 `/backfill`

## 最小读取（避免通读）

1. 解析 index pack：得到 Story 列表、模块覆盖、引用集合、API 分配
2. 读取 GC：仅第 4 节业务规则表（得到合法 `BR-###` 集合）
3. 读取 PRD（只读以下索引章即可）：
   - `5.1 功能清单`（模块 + 优先级，得到 `P0` 模块集合与全部 `M-xx` 集合）
   - `6. 业务规则`（规则表，得到 `BR-###` 集合）
   - `8.0 功能点→落点映射`（得到 `FP-001` 集合）
   - `8.1 表清单`（得到 `TBL-###` 集合）
   - `9.2 接口清单`（按 `N/A_STRICT` 判断是否无 API；得到 `API-###` 集合）
4. 仅当触发 API Smoke Test 时：再读取 PRD `9.3 接口详情`（按锚点 `<!-- PRD#API-### -->` 定向检索，不通读）

## FAIL 校验项（机械性门禁）

### 0) 基础门禁

- `docs/split-check-index-pack.yaml` 必须存在且可解析
- `docs/GLOBAL-CONTEXT.md` 必须存在
- `docs/PRD.md` 必须存在

### 1) GC 规则引用一致性（GC#BR）

- 对 index pack `summary.refs.gc_br_ids` 中每个 `BR-###`：
  - 必须存在于 GC 第 4 节规则表的 ID 列；否则 `FAIL`

### 2) PRD 规则引用一致性（PRD#BR）

- 对 index pack `summary.refs.prd_br_ids` 中每个 `BR-###`：
  - 必须存在于 PRD 第 6 节规则表；否则 `FAIL`

### 3) PRD 表引用一致性（PRD#TBL）

- 对 index pack `summary.refs.prd_tbl_ids` 中每个 `TBL-###`：
  - 必须存在于 PRD `8.1 表清单`；否则 `FAIL`

### 3.5) 功能点引用与覆盖（FP）

令：
- `P_fp =` PRD `8.0 功能点→落点映射` 表中出现的 `FP-001` 集合
- `S_fp =` index pack `summary.refs.fp_ids` 集合

校验（任一不满足即 `FAIL`）：
- 合法性：对 `S_fp` 中每个 `FP-001`，必须存在于 `P_fp`
- 覆盖：对 `P_fp` 中每个 `FP-001`，必须存在于 `S_fp`（否则该功能点没有被任何 Story 覆盖）

### 4) 模块有效性与 P0 覆盖

- 对 index pack 中每个 Story 的 `modules[]`：
  - 每个 `M-xx` 必须存在于 PRD `5.1 功能清单`；否则 `FAIL`
- PRD `5.1` 中每个 `P0` 模块必须至少被 1 个 Story 覆盖（按 index pack 的 `modules[]`）；否则 `FAIL`

### 5) API 分配一致性（PRD ↔ split-plan ↔ Story）

先判断 PRD 是否有接口（N/A 严格口径；必须按此判定）：
- 定位小节 `### 9.2 接口清单（必填）` 的正文（标题行之后到下一同级小节标题之前）
- 判定 `N/A_STRICT = true` 当且仅当：正文去掉空行并 Trim 后仅剩 1 行且该行严格等于 `N/A`
- 若 `N/A_STRICT = true`：`PRD_HAS_API = false`
- 否则：`PRD_HAS_API = true`，并收集 PRD `9.2` 的 `API-###` 集合 `P_api`

令：
- `Plan_api =` index pack `split_plan.api_assignments[].api` 集合
- `Story_api =` index pack `summary.refs.prd_api_ids` 集合

若 `PRD_HAS_API = false`：
- `P_api` 视为空集合
- `Plan_api` 必须为空；否则 `FAIL`
- `Story_api` 必须为空；否则 `FAIL`

若 `PRD_HAS_API = true`：
- 覆盖：
  - `Plan_api` 必须与 `P_api` 完全一致（不得漏分配/多分配）；否则 `FAIL`
- split-plan 唯一归属（必须）：
  - 对 `P_api` 中每个 `API-###`：其在 index pack `split_plan.api_assignments[].api` 中出现次数必须为 `1`；否则 `FAIL`
- Story 唯一归属（必须）：
  - 对 `P_api` 中每个 `API-###`：其在 index pack `stories[].refs.prd_api_ids` 中出现的 Story 数量必须为 `1`；否则 `FAIL`
- 双向一致（必须）：
  - 对 `P_api` 中每个 `API-###`：split-plan 分配到的 `Story N` 必须与 Story 实际引用该 `API-###` 的 `Story N` 相同；否则 `FAIL`

## API Smoke Test（仅当 PRD_HAS_API=true 时执行）

对 `P_api` 中每个 `API-###`：
- PRD 中必须存在且仅存在 1 次锚点：`<!-- PRD#API-### -->`；否则 `FAIL`
- 该锚点必须出现在以 `#### 9.3.` 开头的接口详情标题行中，且标题行必须包含同一个 `API-###`；否则 `FAIL`

## 输出格式（必须）

- `FAIL`：`F-001` 起编号；每条包含：问题 + 影响 + 修复方式（回 `/prd` / 重新 `/split-plan` / 重新 `/split` / 重跑 `/split-check1`）
- `PASS`：仅提示下一步：在新窗口运行 `/backfill`

## 开始

请先生成 `docs/split-check-index-pack.yaml`，再运行本命令。
