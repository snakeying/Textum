# 阶段6c: Story 批量执行（实验 / story-full-exec）

- `$ARGUMENTS`: Story 编号列表（例如：`1/2/3`）

读取：`docs/story-<n>-exec-pack.yaml`（每个 n；唯一事实来源；必须存在） | 写入：仓库文件（代码/测试；多个 Story） | 模板：`N/A`

在同一窗口中按指定顺序依次执行多个 Story，并在末尾汇总 `FAIL`。

## 输入解析（必须）

- 将 `$ARGUMENTS` 解析为编号序列 `N_list`：
  - 支持分隔符：`/`、空格、`,`、`;`
  - 去除空项；保留输入顺序；去重（保留首次出现）
  - 每个编号必须为正整数；否则输出 `FAIL` 并停止（不执行任何 Story）
  - `N_list` 解析后不得为空；否则输出 `FAIL` 并停止（不执行任何 Story）

## 全量前置检查（必须；fail-fast）

- 对 `N_list` 中每个 `n`：`docs/story-<n>-exec-pack.yaml` 必须存在
- 若任一缺失：输出 `FAIL` 清单（每个缺失 pack 1 条；需明确缺失的 `docs/story-<n>-exec-pack.yaml`）并停止（不执行任何 Story）

## 执行规则（继续执行；不回滚）

## 权威执行规则（必须）

- 对每个 `Story <n>` 的执行细则以 `.codex/skills/textum/references/story.md` 为准（尤其是：硬约束 / 执行步骤 / 验证 / 低噪输出规则）
- 本命令仅改变：对多个 Story 依次执行并一次性汇总输出；不逐个等待人工验收

对 `N_list` 按顺序逐个执行：

1. 执行：
   - 对每个 `n`：按 `/story <n>` 的硬约束与步骤执行（`docs/story-<n>-exec-pack.yaml` 为唯一事实来源；禁止再读取/通读 `docs/PRD.md` / `docs/GLOBAL-CONTEXT.md` / `docs/story-*.md`）
   - 验证命令：按 pack 的 `verification.commands` 执行；`gate:*` / `opt:*` 各只跑 1 次；失败不重试
   - 若出现阻断（pack 不足/矛盾、验收未达成、任一 `gate:*` FAIL）：记录 `FAIL`，但继续执行下一个 Story

## 输出（低噪；一次性汇总）

- 若在“输入解析”或“全量前置检查”阶段出现 `FAIL`：只输出 `FAIL` 清单并停止（不执行任何 Story）
- 总结论：
  - 若任一 Story 出现 `FAIL` → 输出 `FAIL`
  - 否则 → 输出 `PASS`
- 执行摘要（每个 Story 仅 1 行）：
  - `Story <n>: PASS`
  - 或 `Story <n>: FAIL`
- 若存在任何 `FAIL`：输出 `FAIL` 清单（`F-001` 起编号；每条必须包含：`定位/问题/期望/影响/修复`；且 `修复` 只给 1 个动作）
- 若存在需要用户确认的非阻断项：输出 `DECISION` 清单（`D-001` 起编号；每条包含：问题 / 影响 / 建议动作）
- 末尾追加：
  - `修正：按 FAIL 清单逐条修复后重跑 /story-full-exec <原参数>`
  - `重跑：/story-full-exec <原参数>`
