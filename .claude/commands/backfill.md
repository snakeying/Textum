# 阶段5: GLOBAL-CONTEXT 回填

## 读取 / 写入

- 读取：`docs/GLOBAL-CONTEXT.md`、`docs/story-*-*.md`
- 写入：更新 `docs/GLOBAL-CONTEXT.md`

## 更新范围（只做小更新）

1. 第 4 节规则表：回填 “涉及Story”
2. 第 9 节：回填 Story 依赖图

## 硬约束

- 不改变规则 `BR-###` 与规则文本（只更新 “涉及Story” 列）
- 不做大段重排（避免无意义 diff）

## 执行步骤

1. 解析所有 Story：
   - 文件名 → `Story N`
   - 前置Story
   - 规则引用：`GC#BR-###`
2. 门禁：
   - 若存在引用不存在的 `BR-###`：输出清单并停止（不写回）
   - 若依赖存在环：输出环路并停止（不写回）
3. 更新 `docs/GLOBAL-CONTEXT.md`：
   - 第 4 节：把 “涉及Story” 写成 `Story 1, Story 3`（无引用留空；移除 `TBD`）
   - 第 9 节：生成依赖图（文本或 Mermaid）

## 完成后

- 提示用户从 `Story 1` 开始按序运行：`/story-check 1` → `/story-pack 1` → `/story 1`
