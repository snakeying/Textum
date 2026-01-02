# 阶段3: Story 拆分（v1）

读取 `docs/split-plan.md`（拆分规划）并结合 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，按 `.claude/textum/story-template-v6.md` 格式生成 `docs/story-N-xxx.md`。

## 输入文件

- 拆分规划: `docs/split-plan.md`
- PRD: `docs/PRD.md`
- 全局上下文: `docs/GLOBAL-CONTEXT.md`
- 模板: `.claude/textum/story-template-v6.md`

## 任务

将 `docs/split-plan.md` 的规划落盘为 Story 文件；并确保数据/接口/规则都能被精确引用与实现。

## 核心约束（必须遵守）

- 以 `docs/split-plan.md` 为唯一事实来源：不要在本阶段重新拆分、改 Story 编号、或改 `API-###` 分配
- 若发现边界/依赖/API 分配不合理：停止，提示用户回到 `/split-plan` 更新 `docs/split-plan.md` 后再运行 `/split`

## 行号引用规则（必须遵守）

**必须使用精确行号格式**: `PRD:L[起]-L[止]`

1. 读取 PRD 时，记录每个引用段落的实际行号
2. 数据表定义 → 记录该表从字段行到最后一个字段行的行范围
3. 接口定义 → 记录从路径到响应（含失败场景）的完整行范围
4. 业务规则 → 记录规则所在行（或规则表对应行范围）

示例:
```
- 定义: PRD:L259-L267      (某数据表)
- 定义: PRD:L406-L409      (某接口)
- PRD:L121-L122: 某业务规则描述
```

> 建议：当引用表/接口时，确保行范围覆盖其 `TBL-###` / `API-###` 标识所在行，便于后续做一致性校验。

## 稳定ID引用（推荐）

为降低行号变化带来的风险，PRD 中的表/接口应有稳定ID：

- 表: `TBL-###`
- 接口: `API-###`

在 Story 的“数据变更/接口”中引用稳定ID：接口必须包含 `API-###`；同时给出 `PRD:Lx-Ly` 作为最小阅读范围（示例见 Story 模板）。

## 低噪音拆分（必须遵守）

为避免被 PRD 细节淹没，严格按以下顺序执行：

1. **先读 `docs/split-plan.md`**：把 Story 编号/依赖/模块、以及 `API-###` 分配作为唯一事实来源（不要在本阶段重新“脑拆分”）
2. **再按 Story 逐个回到 PRD 按需定位**：
   - 用 `API-###` / `TBL-###` 快速定位对应块
   - 仅补齐本 Story 涉及项的 `PRD:Lx-Ly` 行号范围（不要通读 PRD）
3. **生成 Story 文件**：严格按模板补齐每个章节；无内容写 `N/A`

## 生成规则（必须遵守）

- 每个 Story 必须生成 1 个文件：`docs/story-[编号]-[slug].md`
- 文件内容严格按模板；模板里的每个章节都必须出现；无内容写 `N/A`，不要省略章节
- Story 顶部必须填写：编号、模块 `M-xx`、前置 Story、目标/范围/验收标准
- “接口”章节必须列出本 Story 负责的每个 `API-###`，并为每条接口给出 `PRD:Lx-Ly`
- “数据变更”章节如涉及表：写 `TBL-###` + `PRD:Lx-Ly`（不涉及则 `N/A`）
- “业务规则”章节优先引用 `GC#BR-###`；若引用 PRD，必须给出对应 `PRD:Lx-Ly`

## 输出要求

1. 按 `.claude/textum/story-template-v6.md` 格式生成
2. 文件命名: `docs/story-[编号]-[slug].md`
3. 编号即执行顺序：若某 Story 声明 `前置Story: Story X`，则必须满足 `X < 当前编号`（确保用户可按 `/story 1..N` 顺序执行）
4. 每个 Story 的 PRD 引用必须包含精确行号（数据/接口/规则）；接口必须附带 `API-###`，数据表变更建议附带 `TBL-###`
5. 每个 Story 必须写清：功能点、依赖（前置 Story + 已有资源；尽量写可检索的代码标识符）、验收标准、测试要求
6. 模板中的每个章节都必须出现；无内容写 `N/A`，不要省略章节
7. 生成 Story 依赖关系图（可先在拆分结果摘要里给出）
8. 不要修改 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`；只生成/更新 `docs/story-*.md`

## 一致性检查（必须做）

- 覆盖检查：所有 `P0` 模块、核心表、关键接口至少被一个 Story 覆盖
- 依赖检查：无循环依赖；如有环，调整 Story 边界或拆分/前置顺序
- 顺序检查：所有 `前置Story` 的编号必须小于当前 Story 编号（保证可按 `/story 1..N` 顺序执行）
- 命名检查：Story 简称稳定、可读，避免与未来功能冲突

## 完成后（仅提示下一步动作）

- 在新窗口手动运行 `/split-check`
- 如 `FAIL/DECISION`：把清单复制回本窗口，修正 Story 文件后再次手动运行 `/split-check`
- 直到 `PASS`：在新窗口手动运行 `/backfill`

## 开始

请确认已运行 `/split-plan` 并生成 `docs/split-plan.md`；同时 `docs/PRD.md`（顶部 `状态: Final`）与 `docs/GLOBAL-CONTEXT.md` 已存在。
