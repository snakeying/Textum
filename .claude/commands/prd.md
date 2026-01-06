# 阶段1b: PRD 生成/修正

只做一件事：把用户提供的 `PRD_INPUT_PACK` 落盘为 `docs/PRD.md`（按 `.claude/textum/PRD-framework.md`）。

> 约束：本命令**不做需求对话**。若信息不足以生成“可检查的 PRD”，只输出 `PRD_CLARIFY_PACK` 并停止（**不修改任何文件**）。

## 输入

- 用户粘贴的 `PRD_INPUT_PACK`
- （可选）`FAIL/DECISION` 清单（用于精准修正）

## 输出

二选一（必须遵守）：

1. **成功**：创建/更新 `docs/PRD.md`（不含任何模板占位符），并提示用户在新窗口运行 `/prd-check`
2. **信息不足**：只输出 `PRD_CLARIFY_PACK`（不修改任何文件）

## PACK 完备性校验（必须）

- `PRD_INPUT_PACK` 是唯一事实来源：PRD 只能从 pack 的已确认字段映射出来（不得脑补）
- 必须满足最小可用性：
  - `modules` 至少 1 个，且至少 1 个模块 `priority = P0`
  - `business_rules` 至少 1 条且每条非空（否则后续 GLOBAL-CONTEXT 无法生成可用规则索引）
- 对照 `.claude/textum/PRD-framework.md` 的必填章/表逐项校验：必须能**完整填满**且不残留任何占位符（如 `[...]`、`[field]`、`[METHOD]`、`[table]`、`PRD#API-###`、`PRD#TBL-###`）
- 必须可闭合“功能点→落点映射”（PRD `8.0`）：
  - pack 来源：`modules[].feature_points[].landing`（不可为空；不明确就回 `PRD_CLARIFY_PACK`）
  - pack 中每条 `landing` 允许值：`N/A` 或逗号分隔多项集合（不改写 token 本体）：
    - `DB:<table>`：数据库表（`<table>` 必须能在 `data_model.tables[].table` 中找到）
    - `FILE:<path/glob>`：文件/目录/生成产物（允许包含如 `/posts/[slug]` 等路由/通配片段）
    - `CFG:<key>`：配置项/开关/参数
    - `EXT:<system>`：外部依赖
  - PRD 输出规范：`DB:<table>` 必须映射为 `DB:TBL-###`（`TBL-001` 起连续）并能在 PRD `8.2` 用锚点 `<!-- PRD#TBL-### -->` 唯一定位
  - 若 `data_model.tables` 为空：PRD `8.1/8.2/8.3` 均写 `N/A`，且 PRD `8.0` 不得出现任何 `DB:` 落点
- 只要存在任何缺失/歧义/需要确认的信息，一律输出 `PRD_CLARIFY_PACK` 并停止（不写文件）

## 写作规则（必须遵守）

- 严格按 `.claude/textum/PRD-framework.md` 的结构输出所有章节
- 低噪音：短句/表格优先；禁止长段散文复述；一行一条
- 稳定ID：
  - 模块：`M-01` 起递增且唯一
  - 规则：`BR-001` 起递增且唯一
  - 功能点：`FP-01` 起递增且唯一（用于 8.0 映射与后续 Story 关联）
  - 表：`TBL-001` 起递增且唯一（如有表）
  - 接口：`API-001` 起递增且唯一（如有 API）
- 无 API（如适用）：若 `PRD_INPUT_PACK.api.has_api=false`，则 PRD 第 9 节 `9.1/9.2/9.3` 必须写 `N/A`，且全文不得出现任何 `API-###/API-001` 与 `<!-- PRD#API-... -->`
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
