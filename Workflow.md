# Textum Workflow (skills-first)

> 设计原则：低噪是硬约束（约束注意力/上下文污染），最终产出符合用户预期是优化目标（在约束内尽量达成）。

本仓库当前形态：仅支持 **skills-first**（旧的 commands/templates 已移动到 `outdated/`，不再维护）。

## 0) 核心概念

- **真源只认 JSON**：`docs/*.json` 是唯一事实来源；`docs/*.md` 只是“生成视图”（生成后不手改）。
- **门禁/ID 交给脚本**：模型只写“已确认事实”；`*.id` 允许为 `null`，连续性/唯一性/append-only 由脚本自动分配与校验。
- **低噪切片用于后续阶段**：后续 bundle 默认只读取切片索引 + 被索引引用的少量文件，不通读大文件。

## 1) 完整操作流程（从 PRD Plan 开始）

说明：
- 所有命令都在“项目根目录”运行。
- 推荐每个阶段开新窗口执行（避免上下文污染）。

### Stage 1: PRD（Plan → Check/Render 循环 → Slice）

1) 初始化（首次运行才需要）  
   - `uv sync --project .codex/skills/textum/scripts`  
   - `uv run --project .codex/skills/textum/scripts textum prd init` → 写入 `docs/prd-pack.json`
2) `prd-plan`（PRD Plan；交互澄清 + 写真源）  
   - 目标：持续把“已确认事实”写进 `docs/prd-pack.json`（不输出 JSON 正文）  
   - 每轮写入后运行：`uv run --project .codex/skills/textum/scripts textum prd check`，直到 `PASS`
3) `prd`（PRD Render；生成阅读视图）  
   - `uv run --project .codex/skills/textum/scripts textum prd render` → 写入 `docs/PRD.md`
4) `prd-slice`（PRD Slice；后续 Split Plan 必需）  
   - `uv run --project .codex/skills/textum/scripts textum prd slice` → 写入 `docs/prd-slices/`

### Stage 2: Scaffold（Plan → Check/Render 循环）

1) 初始化（首次运行才需要）  
   - `uv run --project .codex/skills/textum/scripts textum scaffold init` → 写入 `docs/scaffold-pack.json`
2) `scaffold-plan`（Scaffold Plan；交互澄清 + 写技术决策）  
   - 目标：把“已确认技术决策”写进 `docs/scaffold-pack.json`（不输出 JSON 正文）  
   - 每轮写入后运行：`uv run --project .codex/skills/textum/scripts textum scaffold check`，直到 `PASS`
3) `scaffold`（Scaffold Render；生成阅读视图）  
   - `uv run --project .codex/skills/textum/scripts textum scaffold render` → 写入 `docs/GLOBAL-CONTEXT.md`

### Stage 3: Split（Plan → Generate → Check1 → Check2 → Checkout）

前置：确保已完成 `PRD Slice`（存在 `docs/prd-slices/index.json`）。

1) 初始化（首次运行才需要）  
   - `uv run --project .codex/skills/textum/scripts textum split plan init` → 写入 `docs/split-plan-pack.json`
2) `split-plan`（Split Plan；交互澄清 + 写拆分规划）  
   - 目标：写清 Story 边界/顺序、模块归属、API 归属（不输出 JSON 正文）  
   - 每轮写入后运行：`uv run --project .codex/skills/textum/scripts textum split plan check`，直到 `PASS`（或 `DECISION` 被处理）
3) `split`（Split Generate；生成每个 Story 真源）  
   - `uv run --project .codex/skills/textum/scripts textum split generate` → 写入 `docs/stories/story-###-<slug>.json`
4) `split-check1`（Split Check1；结构/阈值门禁 + 写交接索引）  
   - `uv run --project .codex/skills/textum/scripts textum split check1` → 通过时写入 `docs/split-check-index-pack.json`
5) `split-check2`（Split Check2；引用一致性门禁）  
   - `uv run --project .codex/skills/textum/scripts textum split check2`
6) `split-checkout`（Split Checkout；导出依赖图视图，便于人工检查顺序）  
   - `uv run --project .codex/skills/textum/scripts textum split checkout` → 写入 `docs/story-mermaid.md`

### Stage 4: Story（Check → Pack → Exec / Full Exec）

1) `story-check`（Story Check；单 Story 门禁）  
   - `uv run --project .codex/skills/textum/scripts textum story check --n <n>`
2) `story-pack`（Story Pack；生成低噪执行包）  
   - `uv run --project .codex/skills/textum/scripts textum story pack --n <n>` → 入口 `docs/story-exec/story-###-<slug>/index.json`
3) `story`（Story Exec；实现代码）  
   - 只读执行包：`index.json` + `index.json.read[]` 列出的文件  
   - 只实现该 Story 的 `feature_points` 与 `api_endpoints`，不发明新接口/新表/新字段
4) `story-full-exec`（Story Full Exec；实验：批量执行）  
   - 输入形如：`1/2/3`（按顺序执行；不回滚）

## 2) uv 命令（单独说明）

> 约定：始终带 `--project .codex/skills/textum/scripts`，把 Textum 依赖隔离在 `.codex/skills/textum/scripts/.venv`。

- `uv sync --project .codex/skills/textum/scripts`  
  - 作用：创建/更新 `.codex/skills/textum/scripts/.venv`，安装依赖（建议首次运行/依赖更新后执行一次）
- `uv run --project .codex/skills/textum/scripts textum <...>`  
  - 作用：运行 Textum CLI（所有 bundle 的 `init/check/render/slice/generate/...` 都通过它执行）
- `uv run --project .codex/skills/textum/scripts python -m ...`  
  - 作用：调试/检查（例如 `python -m compileall`），同样使用隔离环境

## 3) Skill → Python 脚本对应关系（便于维护）

说明：所有 CLI 入口都从 `.codex/skills/textum/scripts/textum_cli.py` 分发；下表只列“主要实现文件”（辅助模块省略或合并展示）。

### PRD

- `prd-plan` →（prompt-only）+ `textum prd init/check` → `prd_pack.py` / `prd_pack_validate.py`
- `prd` → `textum prd render` → `prd_render.py`
- `prd-check` → `textum prd check` → `prd_pack_validate.py`
- `prd-slice`（command-only）→ `textum prd slice` → `prd_slices.py` / `prd_slices_generate.py`

### Scaffold

- `scaffold-plan` →（prompt-only）+ `textum scaffold init/check` → `scaffold_pack.py` / `scaffold_pack_validate.py`
- `scaffold` → `textum scaffold render` → `scaffold_render.py`
- `scaffold-check` → `textum scaffold check` → `scaffold_pack_validate.py`

### Split

- `split-plan` →（prompt-only）+ `textum split plan init/check` → `split_plan_pack.py` / `split_plan_pack_validate.py`
- `split` → `textum split generate` → `split_story_generate.py`
- `split-check1` → `textum split check1` → `split_check_index_generate.py` / `split_check_index_pack.py`
- `split-check2` → `textum split check2` → `split_check_refs.py`
- `split-checkout` → `textum split checkout` → `split_checkout.py`

### Story

- `story-check` → `textum story check --n <n>` → `story_check.py`（拆分：`story_check_utils.py` / `story_check_validate_internal.py` / `story_check_validate_external.py`）
- `story-pack` → `textum story pack --n <n>` → `story_exec_pack.py`（辅助：`story_exec_pack_validate.py` / `story_exec_pack_utils.py`）
- `story` / `story-full-exec` →（prompt-only，无 Python 脚本；执行的是代码改动）

## 4) 产物清单（快速定位）

- PRD 真源：`docs/prd-pack.json`；阅读视图：`docs/PRD.md`；切片：`docs/prd-slices/`
- Scaffold 真源：`docs/scaffold-pack.json`；阅读视图：`docs/GLOBAL-CONTEXT.md`
- Split 规划真源：`docs/split-plan-pack.json`；Story 真源：`docs/stories/story-###-<slug>.json`
- Split 交接索引：`docs/split-check-index-pack.json`；依赖图视图：`docs/story-mermaid.md`
- Story 执行包（低噪切片）：`docs/story-exec/story-###-<slug>/index.json`（entry）
