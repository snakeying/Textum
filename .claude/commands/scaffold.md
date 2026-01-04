# 阶段2: 上下文提取（/scaffold）

读取 `docs/PRD.md`（只读），按模板 `.claude/textum/GLOBAL-CONTEXT-template.md` 生成 `docs/GLOBAL-CONTEXT.md`。

## 读取 / 写入

- 读取：`docs/PRD.md`
- 写入：`docs/GLOBAL-CONTEXT.md`

## 硬约束

- 只做抽取/归纳：不得新增 PRD 中不存在的新规则/新枚举/新接口/新字段
- 禁止 `PRD#...`：`docs/GLOBAL-CONTEXT.md` 中不得出现任何 `PRD#...`
- 必须按模板输出全部章节：无内容写 `N/A`
- `TBD` 仅允许出现在：
  - 第 4 节规则表 “涉及Story”
  - 第 9 节依赖图

## 最小读取范围（避免通读）

只读取生成 GC 必需的 PRD 章节（通常足够）：
- `4` 权限矩阵
- `5.1` 模块清单
- `6` 规则表
- `7` 枚举/状态机
- `8.1/8.3` 表清单与关系（避免大段复制 `8.2` 逐表字段）
- `9.1/9.2` API 通用约定与接口清单
- `10` 非功能底线

## 完成后

- 提示用户在新窗口运行 `/scaffold-check`
