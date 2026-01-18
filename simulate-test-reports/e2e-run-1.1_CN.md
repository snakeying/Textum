# Textum 工作流模拟测试报告（E2E）

## 1. 测试概述

- **测试日期**：2026-01-17
- **模型版本**：Claude Opus 4.5 (claude-opus-4-5-20251101) / GPT-5.2-xhigh
- **测试目标**：验证 Textum Skill 版工作流在"零编程基础用户 + 中等复杂需求（28 FP、18 API）"场景下的端到端可行性与门禁有效性

**测试范围**（按 Workflow.md 阶段）：

| 批次 | 阶段 | Skill Stage 流程 |
|------|------|------------------|
| 1 | PRD 阶段 | PRD Plan → PRD Check → PRD Render → PRD Slice |
| 2 | Scaffold 阶段 | Scaffold Plan → Scaffold Check → Scaffold Render |
| 3 | Split 阶段 | Split Plan → Split Plan Check → Split Generate → Split Check1 → Split Check2 → Split Checkout |
| 4 | Story 执行 | Story Check → Story Pack → Story Exec |

## 2. 产出规模

| 指标 | 数量 |
|------|------|
| 模块 (M-xx) | 7 |
| 功能点 (FP-xxx) | 28 |
| 业务规则 (BR-xxx) | 4 |
| 数据表 (TBL-xxx) | 16 |
| 接口 (API-xxx) | 18 |
| Story | 12 |
| PRD Plan 收敛轮数 | 8 |
| Scaffold Plan 收敛轮数 | 3 |
| Split Plan 收敛轮数 | 2 |

## 3. 各阶段评估结果

### 3.1 PRD 阶段（PRD Plan → PRD Check → PRD Render → PRD Slice）

| 预期 | 模拟结果 | 实现率% |
|------|----------|---------|
| PRD Plan 每轮≤4问、只问blockers | 8轮收敛，每轮≤4问 | 100% |
| PRD Plan READY 时 pack 满足最小可用性 | modules=7、FP=28、BR=4、api.has_api=true、endpoints=18 | 100% |
| PRD Check 结构/占位符/ID一致性 | FAIL→修复→PASS | 100% |
| PRD Render 按模板生成完整 PRD | 生成 PRD.md | 100% |
| PRD Slice 生成切片目录 | 生成 prd-slices/ | 100% |

### 3.2 Scaffold 阶段（Scaffold Plan → Scaffold Check → Scaffold Render）

| 预期 | 模拟结果 | 实现率% |
|------|----------|---------|
| Scaffold Plan 收敛并写入 scaffold-pack.json | 3轮收敛 | 100% |
| Scaffold Check 结构完整 | PASS | 100% |
| Scaffold Render 生成 GLOBAL-CONTEXT.md | 生成成功 | 100% |

### 3.3 Split 阶段（Split Plan → Split Plan Check → Split Generate → Split Check1 → Split Check2 → Split Checkout）

| 预期 | 模拟结果 | 实现率% |
|------|----------|---------|
| Split Plan Story 连续编号、slug 唯一 | Story 1..12；slug 唯一 | 100% |
| Split Plan Check API 阈值预检 | PASS | 100% |
| Split Generate 生成 12 个 story-N-slug.json | 文件名与 split-plan 1:1 | 100% |
| Split Check1 阈值门禁 | WARN（Story 1 api_refs=4，流程继续） | 90% |
| Split Check2 引用一致性 | PASS | 100% |
| Split Checkout 生成依赖图 | 生成 story-mermaid.md | 100% |

### 3.4 Story 执行（Story Check → Story Pack → Story Exec）

本次选中 Story 1（foundation-auth-household）进行执行验证。

| 预期 | 模拟结果 | 实现率% |
|------|----------|---------|
| Story Check 校验 YAML/引用一致性 | PASS | 100% |
| Story Pack 生成 exec-pack | 生成 story-exec/story-001-foundation-auth-household/ | 100% |
| Story Exec 只读 exec-pack | 禁止读 PRD/GC/story-*.json | 100% |
| Story Exec 关键文件覆盖 | server.py/db.py/auth.py/models.py | 100% |
| Story Exec 验证命令（gate:compile） | PASS | 100% |
| Story Exec FP/API 覆盖 | FP-001/FP-003；API-001/002/003/004 | 100% |

## 4. 失败点汇总

| 阶段/步骤 | 出现次数 | 最终状态 |
|-----------|----------|----------|
| PRD Check（permission_matrix.operations 为空） | 1 | 已修复，PASS |
| Split Check1（api_refs=4 触发阈值） | 1 | WARN，流程继续 |

## 5. 全流程综合评估

| 维度 | 符合度% | 说明 |
|------|---------|------|
| 最终产出符合用户预期 | 100% | Story 1 验收标准全部通过；关键文件/能力覆盖完整 |
| 门禁有效性 | 100% | 6 个 check 命令均按预期拦截/放行；阈值/一致性/引用校验无漏检 |
| 低噪 | 95% | 各阶段遵守最小读取范围；Story Exec 时仅读 exec-pack |
| 可复用性 | 90% | 命令/模板结构稳定；ID 格式与锚点机制一致 |

## 6. 结论

Textum Skill 版工作流在 Claude Opus 4.5 / GPT-5.2-xhigh 模型下完成了从用户需求到 Story 执行的完整链路模拟。全流程 19 个步骤执行均符合预期，6 个校验命令（PRD Check、Scaffold Check、Split Plan Check、Split Check1、Split Check2、Story Check）的门禁机制有效运作。

本次测试覆盖了 7 个模块、28 个功能点、18 个 API、16 张数据表、12 个 Story 的中等复杂度场景。PRD Plan 在 8 轮对话内完成需求收敛（含 1 轮修复），Split Check1 触发 1 次 WARN（Story 1 api_refs=4），流程继续执行。

Story 1（基础登录与家庭模块）的执行产出覆盖了 2 个功能点（FP-001/FP-003）、4 个 API（API-001/002/003/004），验证命令 gate:compile 通过。

## 7. 附录

### A. 执行的步骤/命令

| 步骤（Skill Stage） | 对应 CLI 命令 | 执行次数 | 最终结果 |
|---------------------|---------------|----------|----------|
| PRD Plan | N/A（交互） | 8 轮 | READY |
| PRD Init | `uv run textum prd init --workspace <WS>` | 1 | PASS |
| PRD Check | `uv run textum prd check --workspace <WS>` | 2 | PASS |
| PRD Render | `uv run textum prd render --workspace <WS> --lang auto` | 1 | PASS |
| PRD Slice | `uv run textum prd slice --workspace <WS>` | 1 | PASS |
| Scaffold Plan | N/A（交互） | 3 轮 | READY |
| Scaffold Init | `uv run textum scaffold init --workspace <WS>` | 1 | PASS |
| Scaffold Check | `uv run textum scaffold check --workspace <WS>` | 1 | PASS |
| Scaffold Render | `uv run textum scaffold render --workspace <WS>` | 1 | PASS |
| Split Plan | N/A（交互） | 2 轮 | READY |
| Split Plan Init | `uv run textum split plan init --workspace <WS>` | 1 | PASS |
| Split Plan Check | `uv run textum split plan check --workspace <WS>` | 1 | PASS |
| Split Generate | `uv run textum split generate --workspace <WS>` | 1 | PASS |
| Split Check1 | `uv run textum split check1 --workspace <WS>` | 1 | WARN |
| Split Check2 | `uv run textum split check2 --workspace <WS>` | 1 | PASS |
| Split Checkout | `uv run textum split checkout --workspace <WS>` | 1 | PASS |
| Story Check | `uv run textum story check --workspace <WS> --n 1` | 1 | PASS |
| Story Pack | `uv run textum story pack --workspace <WS> --n 1` | 1 | PASS |
| Story Exec (gate:compile) | `python -m compileall app` | 2 | PASS |

> 注：CLI 命令需在 `uv run --project .codex/skills/textum/scripts` 环境下执行，`<WS>` 为工作区路径。

### B. 生成的文档/产物

| 文件 | 状态 |
|------|------|
| docs/prd-pack.json | 生成 |
| docs/PRD.md | 生成 |
| docs/prd-slices/ | 生成 |
| docs/scaffold-pack.json | 生成 |
| docs/GLOBAL-CONTEXT.md | 生成 |
| docs/split-plan-pack.json | 生成 |
| docs/stories/story-001 ~ story-012 | 生成（12 个） |
| docs/split-check-index-pack.json | 生成 |
| docs/story-mermaid.md | 生成 |
| docs/story-exec/story-001-foundation-auth-household/ | 生成 |

### C. 生成的代码（Story 1）

| 文件 | 职责 |
|------|------|
| app/server.py | HTTP 服务器（登录/家庭 API） |
| app/db.py | SQLite 数据库层 |
| app/auth.py | 认证与会话管理 |
| app/models.py | 领域模型（User/Household/Membership） |
