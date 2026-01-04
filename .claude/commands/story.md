# 阶段6: Story 执行（v2）

- `$ARGUMENTS`: Story 编号（如: 1）

## 必填输入

- 1 个 `STORY_EXEC_PACK` YAML 代码块（由 `/story-pack $ARGUMENTS` 生成）
- 门禁：`/story-check $ARGUMENTS` 必须为 `PASS`

若缺任一项：停止并提示用户先在新窗口完成 `/story-check` → `/story-pack`。

## 硬约束

- 只做本 Story；严格按 pack 内容实现；不发明 pack 外的新规则/新接口/新字段
- `STORY_EXEC_PACK` 是 PRD/GC/Story 的唯一来源：禁止再读取/通读 `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、`docs/story-*.md`
- pack 缺失/矛盾/不可执行：停止并输出清单（指示回 `/story-pack` 或 `/split` 或 `/prd` 修复）

## 执行步骤（必须按序）

1. 解析 `STORY_EXEC_PACK`：提取功能点、依赖、规则、数据变更、接口、验收标准、测试要求
2. 若声明“前置Story/已有资源”：在仓库中 `rg` 定向检索，只读取必要签名（避免重复实现）
3. 实现：按验收标准最小改动完成需求，并补齐测试要求
4. 验证：优先执行 pack 中给出的 test/lint/build 命令；若无则写明替代验证方式
5. 输出：对照验收标准的完成情况 + 关键变更点 + 测试/验证结果 + 下一条 Story 的入口

## 开始

请粘贴 `STORY_EXEC_PACK`（YAML 代码块）。
