# 阶段3: Story 拆分（/split）

读取 `docs/split-plan.md`（规划唯一事实来源）并结合 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，按模板 `.claude/textum/story-template.md` 生成 `docs/story-N-<slug>.md`。

## 读取 / 写入

- 读取：`docs/split-plan.md`、`docs/PRD.md`（只读）、`docs/GLOBAL-CONTEXT.md`
- 写入：`docs/story-*-*.md`
- 模板：`.claude/textum/story-template.md`

## 硬约束

- 不得更改 `docs/split-plan.md` 的 Story 编号/边界/API 分配：若发现不合理则停止并提示回 `/split-plan`
- Story 内引用 PRD 必须使用 `PRD#<ID>` 且为具体数字：`PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`
- 模板章节不得缺失；无内容写 `N/A`；不得残留占位符（如 `[功能描述]`、`PRD#API-###`）
- 若 split-plan 第 2 节无任何 API 行（无 API）：所有 Story 的“接口”章节必须写 `N/A` 且不得出现 `PRD#API-###`

## 执行步骤（必须按序）

1. 解析 `docs/split-plan.md`：得到 `Story N` 列表与 `API-### -> Story N` 分配
2. 逐个 Story 生成 1 个文件：`docs/story-N-<slug>.md`
3. 严格按模板填充：
   - `模块（必填）`、`前置Story` 与 split-plan 一致
   - “接口”章节：若分配了 `API-###`，列出对应 `PRD#API-###`；若未分配任何 API，则写 `N/A`
   - “数据变更/业务规则”按需列出 `PRD#TBL-###` / `GC#BR-###` / `PRD#BR-###`
4. 自检：Story 编号可执行（前置编号 < 当前编号）；文件名与 split-plan 1:1 对应；无重复编号

## 完成后

- 提示用户在新窗口运行 `/split-check`，直到 `PASS` 后再运行 `/backfill`
