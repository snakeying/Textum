# 阶段6: Story 执行

- `$ARGUMENTS`: Story 编号（如: 1）

读取：`docs/story-$ARGUMENTS-exec-pack.yaml`（唯一事实来源；必须存在） | 写入：仓库文件（代码/测试；仅本 Story） | 模板：`N/A`

若 pack 文件不存在：停止并提示用户先运行 `/story-pack $ARGUMENTS` 写入 pack 文件。

## 硬约束

- 只做本 Story；严格按 pack 内容实现；不发明 pack 外的新规则/新接口/新字段
- `docs/story-$ARGUMENTS-exec-pack.yaml` 是唯一事实来源：禁止再读取/通读 `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/story-*.md`
- pack 缺失/矛盾/不可执行：停止并输出清单（每条必须包含：定位 / 问题 / 期望 / 影响 / 修复；只给 1 个动作；通常为“修正来源文档后重跑 `/story-pack $ARGUMENTS`”）

## 执行步骤（必须按序）

1. 解析 `docs/story-$ARGUMENTS-exec-pack.yaml`：提取功能点、依赖、规则、数据/产物落点、接口、验收标准、测试要求、验证命令（包含 `prd.fp_artifact_rows`）
2. 若声明“前置Story/已有资源”：在仓库中检索，只读取必要签名（避免重复实现）
3. 实现：按验收标准最小改动完成需求，并补齐测试要求
4. 验证（以“最终产出符合用户预期”为准；避免为 lint 等非阻断项过度返工）：
   - 将 `verification.commands` 按 `type` 分为两类（不改写命令本身）：
     - `gate:*`：门禁验证（失败需修复并重跑直到通过）
     - `opt:*`：可选验证（失败只记录 `DECISION`，不影响交付）
   - `type = N/A` 或 `command = N/A` 的行：视为不可执行，跳过
   - 执行顺序：先跑所有 `gate:*`，再跑 `opt:*`
   - 若不存在任何可执行的 `gate:*`（全部为 `N/A` 或仅有 `opt:*`）：不输出 `DECISION`；仅按验收标准做人工验证/自检并在输出中写明
5. 输出（低噪；不得粘贴大段代码/日志）：
   - `完成情况（人工验收清单）`：逐条列出 Story `## 验收标准` 的 `- [ ]` 项，并标记 `DONE` / `NOT_DONE`（若有未完成必须说明阻塞原因）
   - `关键变更`：仅列“应改动的关键文件路径 + 1 句职责/变化”，不贴 diff
   - `验证结果`：逐条列出执行过的 `gate:*` / `opt:*` 命令与结论（PASS/FAIL）；失败仅给 1 句摘要 + 下一步动作（若无可执行 `gate:*`：写 `gate:*: N/A`）
   - `DECISION`：仅在需要用户确认时输出（例如：opt 失败但可交付、或 pack 信息不足需回补）
   - `下一步`：除非用户明确指定下一条 Story 编号，否则写 `N/A`（禁止推断下一条 Story）

## 开始

请提供 Story 编号（例如：`/story 1`）。
