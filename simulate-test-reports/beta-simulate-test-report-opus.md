# Textum 工作流模拟测试报告 beta版本（Opus）

## 1. 测试概述

- **测试日期**: 2026-01-11
- **模型版本**: Claude Opus 4.5 (claude-opus-4-5-20251101)
- **测试目标**: 验证 Textum beta 版本工作流在"静默模式 + 虚拟文件系统"下的端到端执行能力，覆盖 PRD→Story 全流程门禁与阈值机制

**测试范围**（按 Workflow.md 阶段）:
- 阶段 1: `/prd-plan` → `/prd` → `/prd-check`
- 阶段 2: `/scaffold` → `/scaffold-check`
- 阶段 3: `/split-plan` → `/split` → `/split-check1` → `/split-check2`
- 阶段 4: `/split-checkout` → `/story-check 1` → `/story-pack 1` → `/story 1`

## 2. 产出规模

| 指标 | 数量 |
|------|------|
| 模块 | 7 (M-01~M-07) |
| 功能点 | 30 FP |
| 业务规则 | 8 BR |
| 数据表 | 5 TBL |
| API 端点 | 16 API |
| Story | 6 |
| 角色 | 2 |

## 3. 各阶段评估结果

### 3.1 阶段 1: PRD 阶段

#### /prd-plan

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 多轮收敛至 READY | 7 轮后 READY | 100 | 每轮≤4 问题；blockers 逐轮递减 |

#### /prd

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 生成 PRD 或输出 PRD_PLAN_CLARIFY_PACK | PASS；写入 docs/PRD.md | 100 | 无 PRD_PLAN_CLARIFY_PACK |

#### /prd-check

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 校验 PRD 结构与一致性 | R1: FAIL×2；R2: PASS | 90 | 首次未通过，修正后通过 |

**偏差记录（事实）**:
1. R1 触发 FAIL：落点格式 `DB:users` 未转换为 `DB:TBL-001`
2. R1 触发 FAIL：接口详情锚点缺失

### 3.2 阶段 2: Scaffold 阶段

#### /scaffold

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 从 PRD 抽取生成 GC | 已写入 docs/GLOBAL-CONTEXT.md | 100 | 8 章节完整；技术栈=N/A（PRD 未指定） |

#### /scaffold-check

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 校验 GC 结构与一致性 | DECISION | 95 | 无 FAIL；验证命令表全为 N/A 触发 DECISION |

**偏差记录（事实）**:
1. 验证命令表所有行 `命令=N/A`，触发 DECISION（用户接受后继续）

### 3.3 阶段 3: Split 阶段

#### /split-plan

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 生成 split-plan | R1: 阈值预检 FAIL；R2: DECISION；R3: PASS | 85 | 3 次执行；阈值预检有效拦截 |

**偏差记录（事实）**:
1. R1 阈值预检 FAIL：单 Story api_assigned=7≥6
2. R2 DECISION：单 Story api_assigned=4（4-5 区间）

#### /split

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 生成 Story 文件 | R1: 5 Stories；R2: 6 Stories | 100 | 占位符自检通过 |

#### /split-check1

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 结构/阈值校验 | R1: FAIL×1；R2: DECISION×1 | 90 | 阈值 FAIL 触发重规划 |

**偏差记录（事实）**:
1. R1 阈值 FAIL：feature_points=13≥13，生成 SPLIT_REPLAN_PACK
2. R2 阈值 DECISION：api_refs=4（4-5 区间）

#### /split-check2

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 引用可追溯 + API Smoke | PASS | 100 | GC/PRD 引用一致；API 唯一归属；锚点全匹配 |

### 3.4 阶段 4: Story 执行阶段

#### /split-checkout

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 导出依赖图 | PASS；写入 docs/story-mermaid.md | 100 | 6 节点；5 边 |

#### /story-check 1

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 校验 Story 1 | PASS | 100 | 无 FAIL/DECISION |

#### /story-pack 1

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 生成执行包 | PASS；写入 docs/story-1-exec-pack.yaml | 100 | GC/PRD 片段原文复制 |

#### /story 1

| 预期 | 模拟结果 | 实现率% | 说明 |
|------|----------|---------|------|
| 执行 Story 1 | 完成；DECISION | 95 | 5/5 验收项 DONE；无 gate 命令触发 DECISION |

**偏差记录（事实）**:
1. verification.commands 全为 N/A，无可执行 gate 命令，触发 DECISION

## 4. 失败点汇总

| ID | 阶段/命令 | 触发条件 | 表现 | 对最终产出影响 | 噪音风险 | 归因类型 |
|----|-----------|----------|------|----------------|----------|----------|
| F-01 | /prd-check R1 | 落点格式门禁 | `DB:users` 未转换为 `DB:TBL-001` | M | L | format_drift |
| F-02 | /prd-check R1 | 锚点存在性门禁 | 接口详情锚点缺失 | M | L | format_drift |
| F-03 | /split-plan R1 | 阈值预检 api_assigned≥6 | 单 Story 分配 7 个 API | H | M | weak_stop_condition |
| F-04 | /split-check1 R1 | 阈值 feature_points≥13 | 单 Story 功能点=13 | H | M | weak_stop_condition |

## 5. 全流程综合评估

| 维度 | 符合度% | 说明 |
|------|---------|------|
| 最终产出符合用户预期 | 95 | Story 1 全部验收项完成；DECISION 均为非阻断性 |
| 门禁有效性 | 90 | 阈值门禁有效拦截过大 Story；格式门禁捕获漂移 |
| 低噪 | 85 | 多窗口隔离有效；阈值触发导致 2 次重规划 |
| 可复用性 | 90 | 命令/模板结构稳定；ID 体系一致 |

## 6. 结论

本次模拟测试覆盖了 Textum beta 版本工作流的 4 个阶段、13 个命令执行点。全流程在"静默模式 + 虚拟文件系统"约束下完成，最终产出 6 个 Story，其中 Story 1 的 5 项验收标准全部达成。

门禁机制在 /prd-check 阶段捕获了 2 处格式漂移（落点格式与锚点缺失），在 /split-plan 与 /split-check1 阶段通过阈值预检与阈值校验有效拦截了过大 Story（api_assigned≥6、feature_points≥13），触发了 2 次重规划流程。

DECISION 机制在 /scaffold-check、/split-plan R2、/split-check1 R2、/story 1 共触发 4 次，均为非阻断性（验证命令缺失、阈值边界区间），用户接受后流程正常继续。

整体而言，Textum beta 版本工作流在本次模拟中展现了稳定的门禁拦截能力与多窗口隔离效果，ID 体系（BR/TBL/API/FP）在全流程中保持一致。

## 7. 附录

### 7.1 使用到的命令清单

| 命令 | 执行次数 | 最终结果 |
|------|----------|----------|
| /prd-plan | 7 | READY |
| /prd | 2 | PASS |
| /prd-check | 2 | PASS |
| /scaffold | 1 | 已写入 |
| /scaffold-check | 1 | DECISION |
| /split-plan | 3 | PASS |
| /split | 2 | 已写入 |
| /split-check1 | 2 | DECISION |
| /split-check2 | 1 | PASS |
| /split-checkout | 1 | PASS |
| /story-check 1 | 1 | PASS |
| /story-pack 1 | 1 | PASS |
| /story 1 | 1 | 完成 |

### 7.2 生成的文档

| 文件 | 状态 |
|------|------|
| docs/prd-plan-pack.yaml | 已生成 |
| docs/PRD.md | 已生成 |
| docs/GLOBAL-CONTEXT.md | 已生成 |
| docs/split-plan.yaml | 已生成 |
| docs/story-1-auth.md | 已生成 |
| docs/story-2-user.md | 已生成 |
| docs/story-3-conversation.md | 已生成 |
| docs/story-4-message.md | 已生成 |
| docs/story-5-ai-feedback.md | 已生成 |
| docs/story-6-admin.md | 已生成 |
| docs/split-check-index-pack.yaml | 已生成 |
| docs/story-mermaid.md | 已生成 |
| docs/story-1-exec-pack.yaml | 已生成 |

### 7.3 生成的代码

| 文件 | 职责 |
|------|------|
| src/lib/auth.ts | 认证逻辑 |
| src/app/api/auth/* | 认证 API 路由 |
| prisma/schema.prisma | 数据模型（users, password_resets） |

---

## 8. 试验性测试：/story-full-exec（批量执行）

> **⚠️ 声明**：`/story-full-exec` 是试验性命令，**不建议在生产环境使用**。该命令在单窗口中批量执行多个 Story，存在上下文爆炸、错误累积、无法回滚等风险。此测试仅用于评估技术可行性。

### 8.1 测试前置条件

基于主流程模拟的 VFS 状态，补齐 Story 2-6 的 exec-pack：

| 步骤 | 模拟结果 | 说明 |
|------|----------|------|
| /story-pack 2 | PASS | 写入 docs/story-2-exec-pack.yaml |
| /story-pack 3 | PASS | 写入 docs/story-3-exec-pack.yaml |
| /story-pack 4 | PASS | 写入 docs/story-4-exec-pack.yaml |
| /story-pack 5 | PASS | 写入 docs/story-5-exec-pack.yaml |
| /story-pack 6 | PASS | 写入 docs/story-6-exec-pack.yaml |

### 8.2 /story-full-exec 1/2/3/4/5/6 执行结果

| 阶段 | 预期 | 模拟结果 | 说明 |
|------|------|----------|------|
| 输入解析 | N_list=[1,2,3,4,5,6] | PASS | 分隔符 `/` 正确解析 |
| 全量前置检查 | 6 个 exec-pack 存在 | PASS | 无缺失 |
| Story 1 执行 | 按 pack 实现 | PASS | 5/5 验收项 |
| Story 2 执行 | 按 pack 实现 | PASS | 4/4 验收项 |
| Story 3 执行 | 按 pack 实现 | PASS | 6/6 验收项 |
| Story 4 执行 | 按 pack 实现 | PASS | 5/5 验收项 |
| Story 5 执行 | 按 pack 实现 | PASS | 4/4 验收项 |
| Story 6 执行 | 按 pack 实现 | PASS | 5/5 验收项 |
| 总结论 | — | PASS | 6/6 Story 完成 |

**DECISION 记录**: 所有 Story 的 verification.commands 均为 N/A，无可执行 gate 命令，仅基于验收标准自检。

### 8.3 风险评估

| 风险 | 严重程度 | 说明 |
|------|----------|------|
| 上下文爆炸 | H | 多个 exec-pack 原文 + 多个 Story 的代码实现，单窗口上下文可能超限 |
| 错误累积 | H | Story 间存在依赖；若前序 Story 实现有误但未被 gate 拦截，错误传递到后续 Story |
| 无法回滚 | M | 命令明确"继续执行；不回滚"，中途 FAIL 后已执行的代码变更无法撤销 |
| 验证缺失放大 | H | 若 gate 命令缺失，多个 Story 全靠自检，风险叠加 |

### 8.4 适用性判断

| 场景 | 适用性 | 说明 |
|------|--------|------|
| Story 数量 ≤3，复杂度低，gate 命令完备 | ✓ 可用 | 风险可控 |
| Story 数量多，Story 间强依赖 | ✗ 高风险 | 错误累积风险高 |
| gate 命令缺失 | ✗ 高风险 | 无自动验证，风险叠加 |
| 生产环境 | ✗ 高风险 | 逐个执行 /story N 更可控 |

### 8.5 命令设计评价

| 维度 | 评估 | 说明 |
|------|------|------|
| 技术可行性 | ✓ 可行 | 命令设计合理，fail-fast 前置检查有效 |
| 低噪（硬约束） | 部分符合 | 单窗口执行降低窗口切换噪音，但上下文爆炸风险与硬约束存在冲突 |
| 产出符合预期（优化目标） | 依赖前提 | 依赖 gate 命令质量；若 gate 缺失，错误累积风险高 |

### 8.6 试验性测试结论

`/story-full-exec` 在本次模拟中技术上可行，6 个 Story 全部完成。但该命令的风险特性决定了其仅适用于特定场景（Story 数量少、复杂度低、gate 命令完备）。在 gate 命令缺失或 Story 间强依赖的场景下，错误累积风险显著，不适合使用。
