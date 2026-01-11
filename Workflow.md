# Textum Workflow 1.0

> 设计原则：低噪是硬约束（约束注意力/上下文污染），最终产出符合用户预期是优化目标（在约束内尽量达成）。

当前版本：仅支持 **PRD bundle**（其余 bundle 将在后续逐步迁移）。

## PRD bundle（JSON 真源 → PRD.md 视图）

**真源与模板**
- 真源：`docs/prd-pack.json`
- 视图：`docs/PRD.md`（生成后不手改；要改请改真源并重跑渲染）
- 模板：`.codex/skills/textum/assets/prd-pack.template.json`
- Schema：`.codex/skills/textum/assets/prd-pack.schema.json`

**运行时**
- Python >= 3.11（推荐 3.11；测试基于 3.11）
- `uv` 管理虚拟环境：在项目根目录先执行 `uv sync --project .codex/skills/textum`

**命令（在项目根目录）**
- `uv run --project .codex/skills/textum textum prd init`：初始化 `docs/prd-pack.json`
- `uv run --project .codex/skills/textum textum prd check`：门禁校验 + 自动分配 ID（模型不维护编号）
- `uv run --project .codex/skills/textum textum prd render`：从 `docs/prd-pack.json` 生成 `docs/PRD.md`

**门禁口径（摘要）**
- `api.has_api` 必须为布尔值（避免 `N/A_STRICT` 这类文本判定）
- landing token：`N/A` 或以 `DB:` / `FILE:` / `CFG:` / `EXT:` 开头；`DB:<table_name>` 需能在 `data_model.tables[].name` 中找到
- 稳定 ID：`M-01` / `FP-001` / `BR-001` / `TBL-001` / `API-001` 均由脚本自动分配与校验（编号连续性/唯一性/append-only 不交给模型）
- 禁止 fenced code blocks：任何字段不得包含 ```

## Roadmap

Scaffold/Split/Story bundles：暂未迁移（本版本 `textum` skill 会返回 `NOT_SUPPORTED`）。
