# 阶段3a: Story 拆分规划

读取 `docs/PRD.md` 与 `docs/GLOBAL-CONTEXT.md`，先产出 **低噪音** 的拆分规划 `docs/split-plan.md`

## 读取

- `docs/PRD.md`（只读；不修改）
- `docs/GLOBAL-CONTEXT.md`

## 低噪音读取（必须遵守）

- 不要通读整份 PRD；只精读 PRD 的索引章节：`5.1`（模块清单）、`6`（规则表）、`8.1`（表清单含 `TBL-###`）、`9.2`（接口清单含 `API-###`）
- 不要通读整份 GC；默认只读第 4 节业务规则表与第 8 节 API规范（用于拆分口径一致）
- 本阶段不回填 `PRD:Lx-Ly` 行号范围

## 输出（写入文件）

生成 `docs/split-plan.md`，按以下结构输出（必须包含所有小节；无内容写 `N/A`）：

1. **Story 列表（必须）**
   - 每个 Story：编号（执行顺序）、文件简称（slug）、模块 `M-xx`、一句话目标、前置 Story
2. **API 分配表（必须）**
   - `API-### -> Story N`（每个 `API-###` 必须且仅能分配给 1 个 Story）
3. **表分配表（可选）**
   - `TBL-### -> Story N`（可多对一/一对多；只要能支撑实现顺序即可）
4. **规则分配（可选）**
   - `BR-### -> Story N`（用于提示哪些 Story 需要引用 `GC#BR-###`）
5. **依赖图（必须）**
   - 文本或 Mermaid 均可，但必须清晰可读且无环
6. **自检结果（必须）**
   - `P0` 模块覆盖：每个 `P0` 模块至少 1 个 Story
   - `API-###` 覆盖：PRD `9.2` 中每个 `API-###` 已分配且仅分配一次
   - 依赖合法：无环，且满足 `前置Story < 当前编号`

## 完成后（仅提示下一步动作）

- 用户快速审阅 `docs/split-plan.md`（Story 边界/依赖/API 分配是否合理）
- 然后在新窗口手动运行 `/split` 生成 `docs/story-N-xxx.md` 并回填 `PRD:Lx-Ly`

## 开始

请确认已完成 `/scaffold` 并生成 `docs/GLOBAL-CONTEXT.md`。
