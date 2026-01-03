# 阶段6a: Story 校验（v1）

- `$ARGUMENTS`: Story 编号（如: 1）

读取 `docs/story-$ARGUMENTS-*.md`、`docs/GLOBAL-CONTEXT.md`、`docs/PRD.md`，输出 `FAIL/DECISION/PASS` 清单用于回到 `/split` 修正 Story 或回到 `/prd` 修正规格；**不修改任何文件**。

## 读取

- `docs/story-$ARGUMENTS-*.md`（且必须只匹配 1 个文件）
- `docs/GLOBAL-CONTEXT.md`
- `docs/PRD.md`（只读）

## 低噪音读取（必须遵守）

1. **先读 Story 只抽取索引**：`模块`、`前置Story`、`GC#BR-###`、`PRD#API-###`、`PRD#TBL-###`、`PRD#BR-###`
2. **再按索引定位 GC/PRD**：只查被引用的规则/ID/锚点（`PRD#<ID>`）；不要通读全文
3. 输出只包含清单，不粘贴原文片段

## FAIL 校验项（严格拦截）

### 0) 基础门禁

- `docs/PRD.md` 必须存在
- `docs/GLOBAL-CONTEXT.md` 必须存在
- `docs/story-$ARGUMENTS-*.md` 必须存在且仅 1 个

### 1) 模板完整性（不得缺章/占位符）

Story 必须包含以下章节；无内容写 `N/A`，但不得省略章节：

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

### 2) 引用格式（必须可追溯）

- 所有 PRD 引用必须使用 `PRD#<ID>`，且 `<ID>` 必须为具体数字（如 `PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`）

### 3) 规则一致性（GC#BR 必须存在）

- 收集 Story 中所有 `GC#BR-###`
- 校验每个引用的 `BR-###` 都存在于 `docs/GLOBAL-CONTEXT.md` 第 4 节业务规则表

### 4) 接口一致性（API-### 必须存在且可定位）

- 若 Story 的“接口”章节非 `N/A`：
  - 必须至少包含 1 个 `PRD#API-###`（具体数字：`PRD#API-001` 形式）
  - 对每个 `PRD#API-###`：校验该 `API-###` 必须存在于 PRD `9.2 接口清单`

### 5) 数据变更一致性（TBL-### 如适用）

- 若 Story 的“数据变更”章节非 `N/A`：
  - 必须至少包含 1 个 `PRD#TBL-###`（具体数字：`PRD#TBL-001` 形式）
  - 对每个 `PRD#TBL-###`：校验该 `TBL-###` 必须能在 PRD `8.1/8.2` 中定位到

### 6) 依赖合法性（可执行顺序）

- 若声明 `前置Story: Story X`：必须满足 `X < $ARGUMENTS`
- 禁止自依赖与循环依赖（就本 Story 的前置链路做检查）

## DECISION（需要用户确认）

- “测试要求”为 `N/A` 但 Story 涉及 `API-###` 或数据变更：是否允许先实现后补测试？
- “验收标准”过少或不可验证：需要用户确认验收口径后再进入 `/story`

## PASS

- `PASS`：仅提示下一步动作：在新窗口手动运行 `/story $ARGUMENTS`
