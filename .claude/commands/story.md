# 阶段6: Story 执行（v1）

- `$ARGUMENTS`: Story 编号（如: 1）

读取 `docs/GLOBAL-CONTEXT.md` 与 `docs/story-$ARGUMENTS-*.md`，完成该 Story 的开发任务。

## 必须遵守

- `docs/PRD.md` 顶部 `状态: Final`（否则停止并让用户确认是否回到 `/prd` 定稿）
- PRD 已冻结，禁止修改 `docs/PRD.md`
- `docs/GLOBAL-CONTEXT.md` 已存在
- 只做本 Story；仅读取该 Story 引用的 `PRD:Lx-Ly` 行范围（不要通读整份 PRD）

## 执行准则

- 严格按 Story 的“功能点/业务规则/数据变更/接口/验收标准/测试要求”实现
- 不在实现阶段发明新规则/新枚举/新接口；发现缺口就停止并让用户确认
- 规则编号与引用遵循 `BR-###` / `GC#BR-###`（三位数字，001 起递增且唯一）
- 全局约定以 `GLOBAL-CONTEXT.md` 为准；冲突时以 `PRD.md` 为事实依据并明确记录待澄清点

## 完成定义（Done）

- [ ] 所有验收标准可手工复现或自动化验证
- [ ] 完成 Story 指定的测试要求（能跑就跑；否则说明原因与替代验证方式）
- [ ] 若涉及 DB/接口变更：迁移、回滚策略与错误码符合 PRD/GC 约定

## 开始

请提供 Story 编号。
