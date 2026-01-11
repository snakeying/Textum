# 阶段1b: PRD 生成/修正

只做一件事：把 plan-pack 落盘为 PRD（按模板）。

> 约束：本命令**不做需求对话**。若信息不足以生成“可检查的 PRD”，输出 `PRD_PLAN_CLARIFY_PACK` 并停止（**不修改任何文件**）。

读取：`docs/prd-plan-pack.yaml` +（如存在）`docs/PRD.md` | 写入：`docs/PRD.md`（信息不足则不写） | 模板：`.codex/skills/textum/assets/PRD-framework.md` | 可选输入：`FAIL/DECISION` 清单

## 输入

- plan-pack（唯一事实来源；不得向用户索要整包粘贴）
- （可选）`FAIL/DECISION` 清单（用于精准修正）

## 修正模式（当提供 `FAIL/DECISION` 清单时必须遵守）

- 以现有 `docs/PRD.md` 为基线：**只修改清单命中的位置**，其余内容不做无关改动（最小 diff）
- 稳定 ID/锚点禁止漂移：不得重排/重编号；若必须新增，只能在末尾新增并按序递增
- 若清单需要补充事实且 plan-pack 不足以支撑：输出 `PRD_PLAN_CLARIFY_PACK` 并停止（不写文件）

## 输出

二选一（必须遵守）：

1. **成功**：创建/更新 `docs/PRD.md`（不含任何模板占位符），并输出：
   - `PASS`
   - `已写入：docs/PRD.md`
   - `下一步：PRD 校验`
2. **信息不足**：输出 `PRD_PLAN_CLARIFY_PACK` 代码块后，追加两行纯文本指引（不修改任何文件）：
   - `下一步：将 PRD_PLAN_CLARIFY_PACK 粘贴到“需求澄清（plan）”继续补齐`
   - `重跑：PRD 生成/修正`

## PACK 完备性校验（必须）

- `docs/prd-plan-pack.yaml` 是唯一事实来源：PRD 只能从已确认字段映射出来（不得脑补）
- 必须满足最小可用性：
  - `modules` 至少 1 个，且至少 1 个模块 `priority = P0`
  - `business_rules` 至少 1 条且每条非空
- 对照 `.codex/skills/textum/assets/PRD-framework.md` 的必填章/表逐项校验：必须能**完整填满**且不残留任何占位符（如 `TBD`、`[...]`、`[field]`、`[METHOD]`、`[PATH]`、`[table]`、`PRD#API-###`、`PRD#TBL-###`）
- PRD `7.3 命名规范`：
  - 仅当 plan-pack `assumptions_constraints[].assumption_or_constraint` 中存在以 `命名规范:` 开头的已确认约定时才写表格
  - 否则该小节正文仅一行 `N/A`（不追问、不阻断）
- 必须可闭合“功能点→落点映射”（PRD `8.0`）：
  - pack 来源：`modules[].feature_points[].landing`（不可为空；不明确就回 `PRD_PLAN_CLARIFY_PACK`）
  - pack 中每条 `landing` 允许值：`N/A` 或逗号分隔多项集合（不改写 token 本体）：
    - `DB:<table>`：数据库表（`<table>` 必须能在 `data_model.tables[].table` 中找到）
    - `FILE:<path/glob>`：文件/目录/生成产物（允许包含如 `/posts/[slug]` 等路由/通配片段）
    - `CFG:<key>`：配置项/开关/参数
    - `EXT:<system>`：外部依赖
  - PRD 输出规范：`DB:<table>` 必须映射为 `DB:TBL-###`（`TBL-001` 起连续）并能在 PRD `8.2` 用锚点 `<!-- PRD#TBL-### -->` 唯一定位
  - 若 `data_model.tables` 为空：PRD `8.1/8.2/8.3` 均写 `N/A`，且 PRD `8.0` 不得出现任何 `DB:` 落点
- 仅当无法生成“可检查的 PRD”时才输出 `PRD_PLAN_CLARIFY_PACK` 并停止（不写文件）；阻断条件包括：
  - plan-pack 不满足“需求澄清（plan）”的 `READY` 门禁（例如：`api.has_api=null`、缺模块/缺功能点/缺落点、缺规则、缺权限矩阵等）
  - 任何必填表格/章节只能靠猜测才能补齐
  - 无法闭合 `8.0 功能点→落点映射`（含落点 token 不合法、或 `DB:<table>` 找不到 `data_model.tables[].table`）
  - `api.has_api=true` 但 `api.endpoints` 无法提供最小清单（method/path/permission/summary）
  - 需要新增 API/TBL 但缺少最小可定位信息，无法保证 ID/锚点稳定
- 其余“非阻断缺失”（例如：第 2.3/7.1/7.2/10 细节不足、表字段不全、错误码不全）：用 `N/A`/`None` 明确落盘，不追问、不阻断

## 写作规则（必须遵守）

- 严格按 `.codex/skills/textum/assets/PRD-framework.md` 的结构输出所有章节
- 低噪音：短句/表格优先；禁止长段散文复述；一行一条
- 禁止 fenced code blocks：PRD 中不得出现任何 ```（用表格/短句替代）
- 全文不得出现 `TBD`
- 稳定ID：
  - 模块：优先使用 plan-pack `modules[].id`；缺失才生成 `M-01` 起递增且唯一
  - 规则：优先使用 plan-pack `business_rules[].id`；缺失才生成 `BR-001` 起递增且唯一
  - 功能点：优先使用 plan-pack `modules[].feature_points[].fp`；缺失才生成 `FP-001` 起递增且唯一（3 位数字）
  - 表：`TBL-001` 起递增且唯一（如有表）
  - 接口：`API-001` 起递增且唯一（如有 API）
- 无 API（如适用）：若 `api.has_api=false`，则 PRD 第 9 节 `9.1/9.2/9.3` 三个小节正文必须严格为 1 行 `N/A`（不得残留表格/子标题/其它文本），且全文不得出现任何 `API-###/API-001` 与 `<!-- PRD#API-... -->`
- 块边界：每个表/接口必须在其详情小节标题包含对应 `TBL-###` / `API-###`；不要把多个 ID 的细节混在同一块里
- 锚点（机械抽取用）：每个表/接口详情标题行必须追加对应锚点 `<!-- PRD#TBL-### -->` / `<!-- PRD#API-### -->`，且锚点内数字与标题 `TBL-###` / `API-###` 一致

## `PRD_PLAN_CLARIFY_PACK` 格式（必须严格按此输出）

先输出 1 个代码块（YAML），便于复制回“需求澄清（plan）”进行补齐；然后追加两行纯文本指引（见上文“输出/信息不足”）：

```yaml
PRD_PLAN_CLARIFY_PACK: 
target_file: "docs/prd-plan-pack.yaml"
blockers:
  - id: "Q-001"
    path: "yaml.path.like.modules[0].feature_points[0].landing"
    ask: "用用户听得懂的话提问（必须可回答）"
    expected: "期望答案格式（例如：三选一 / 逗号分隔 / 一句话 / 表格）"
    options: ["可选项A", "可选项B", "可选项C"] # 没有就写 []
```

规则：
- `blockers` 最多 8 条；按优先级排序（先问会阻塞大范围章节的）
- 每条问题必须能被非程序员直接回答；必要时给 A/B/C 选项
- 不要输出任何 PRD 正文/草稿（避免在错误信息下误写文件）

## 开始

我会读取 `docs/prd-plan-pack.yaml`（以及可选的 `FAIL/DECISION` 清单）。信息足够时一次性生成/修正 `docs/PRD.md`；信息不足时输出 `PRD_PLAN_CLARIFY_PACK` 并给出下一步指引。
