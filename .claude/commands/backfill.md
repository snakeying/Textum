# 阶段5: GLOBAL-CONTEXT 回填

## 读取

- `docs/GLOBAL-CONTEXT.md`
- `docs/story-*-*.md`（所有 Story 文件）

## 更新目标（只做“小更新”）

1. 回填 `GLOBAL-CONTEXT` 第 4 节业务规则表的 “涉及Story” 列
2. 回填 `GLOBAL-CONTEXT` 第 9 节 Story 依赖图

## 约束（必须遵守）

- 不修改 `docs/PRD.md`
- 不改变业务规则编号（`BR-###`，三位数字）与文本含义（只更新 “涉及Story” 列）
- 不重排大段内容，避免无意义 diff
- 如发现不一致（Story 引用不存在的 BR / 依赖循环），输出待处理清单，请用户决策后再修

## 执行步骤

1. 检查 `docs/PRD.md`、`docs/GLOBAL-CONTEXT.md`、以及至少 1 个 `docs/story-*-*.md` 是否存在
2. 逐个读取 `docs/story-*-*.md`：
   - 识别 Story 编号（如 `story-3-xxx.md` → `Story 3`）
   - 解析 “依赖/前置Story”（如 `Story X, Y`）
   - 收集引用到的规则（匹配 `GC#BR-###` 格式）
3. 回填 `docs/GLOBAL-CONTEXT.md`：
   - 第 4 节：对每条 `BR-###` 规则，把 “涉及Story” 更新为实际引用它的 Story 列表（无引用则留空；不要保留 `TBD`）
   - 第 9 节：根据 “前置Story” 生成依赖图（文本或 Mermaid 均可，但需清晰可读）
4. 依赖检查：
   - 若存在循环依赖，列出形成环的 Story 链路，并给出建议的拆分/改依赖方案
5. 输出更新后的 `docs/GLOBAL-CONTEXT.md`

## 开始

请确认已完成 `/split` 与 `/split-check`，并已生成 `docs/story-*-*.md`。
