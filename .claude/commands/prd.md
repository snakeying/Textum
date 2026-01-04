# 阶段1b: PRD 生成/修正

本命令只做一件事：把用户提供的 `PRD_INPUT_PACK` 落盘为 `docs/PRD.md`（按 `.claude/textum/PRD-framework.md`）。

> 约束：本命令**不做需求对话**。若信息不足以生成“可检查的 PRD”，只输出 `PRD_CLARIFY_PACK` 并停止（**不修改任何文件**）。

## 输入

- 用户粘贴的 `PRD_INPUT_PACK`（来自需求澄清步骤）
- （可选）上一轮 `/prd-check` 的 `FAIL/DECISION` 清单（用于精准修正）

## 输出

二选一（必须遵守）：

1. **成功**：创建/更新 `docs/PRD.md`（不含任何模板占位符），并提示用户在新窗口运行 `/prd-check`
2. **信息不足**：只输出 `PRD_CLARIFY_PACK`（不修改任何文件）

## PACK 完备性校验（必须）

- `PRD_INPUT_PACK` 是唯一事实来源：PRD 只能从 pack 的已确认字段映射出来（不得脑补）
- 对照 `.claude/textum/PRD-framework.md` 的必填章/表逐项校验：必须能**完整填满**且不残留任何占位符（如 `[...]`、`[field]`、`[METHOD]`、`[table]`、`PRD#API-###`、`PRD#TBL-###`）
- 只要存在任何缺失/歧义/需要确认的信息，一律输出 `PRD_CLARIFY_PACK` 并停止（不写文件）

## 写作规则（必须遵守）

- 严格按 `.claude/textum/PRD-framework.md` 的结构输出所有章节
- 低噪音：短句/表格优先；禁止长段散文复述；一行一条
- 稳定ID：
  - 模块：`M-01` 起递增且唯一
  - 规则：`BR-001` 起递增且唯一
  - 表：`TBL-001` 起递增且唯一（如有表）
  - 接口：`API-001` 起递增且唯一（如有 API）
- 块边界：每个表/接口必须在其详情小节标题包含对应 `TBL-###` / `API-###`；不要把多个 ID 的细节混在同一块里
- 锚点（机械抽取用）：每个表/接口详情标题行必须追加对应锚点 `<!-- PRD#TBL-### -->` / `<!-- PRD#API-### -->`，且锚点内数字与标题 `TBL-###` / `API-###` 一致

## `PRD_CLARIFY_PACK` 格式（必须严格按此输出）

只输出一个代码块，便于用户整段复制回需求澄清窗口：

```yaml
PRD_CLARIFY_PACK: v1
blockers:
  - id: "Q-001"
    target: "PRD 章节/表名（例如：4 权限矩阵 / 9.3 接口详情）"
    ask: "用用户听得懂的话提问（必须可回答）"
    expected: "期望答案格式（例如：三选一 / 逗号分隔 / 一句话 / 表格）"
    options: ["可选项A", "可选项B", "可选项C"] # 没有就写 []
```

规则：
- `blockers` 最多 8 条；按优先级排序（先问会阻塞大范围章节的）
- 每条问题必须能被非程序员直接回答；必要时给 A/B/C 选项
- 不要输出任何 PRD 正文/草稿（避免在错误信息下误写文件）

## 开始

请粘贴 `PRD_INPUT_PACK`（以及可选的 `/prd-check` 清单）。我会在信息足够时一次性生成/修正 `docs/PRD.md`；否则只返回 `PRD_CLARIFY_PACK`。
