# Textum Workflow (1.0)

> 设计原则：低噪是硬约束（约束注意力/上下文污染），最终产出符合用户预期是优化目标（在约束内尽量达成）。

本仓库当前形态：仅支持 **skills**（旧的 commands/templates 已移动到 `outdated/`，不再维护）。

## 0) 核心概念

- **真源只认 JSON**：`docs/*.json` 是唯一事实来源；`docs/*.md` 只是“生成视图”（生成后不手改）。
- **门禁/ID 交给脚本**：模型只写“已确认事实”；`*.id` 允许为 `null`，连续性/唯一性/append-only 由脚本自动分配与校验。
- **低噪切片用于后续阶段**：后续 bundle 默认只读取切片索引 + 被索引引用的少量文件，不通读大文件。

## 1) 完整操作流程（从 PRD Plan 开始）

说明：
- 所有命令都在“项目根目录”运行。
- 推荐每个阶段开新窗口执行（避免上下文污染）。

### Stage 1: PRD（Plan → Check(PASS) → Render（验收视图） → Slice）

说明：
- PRD 流程通过 `textum` skill 的路由触发，不需要手动运行 CLI 命令；仅在你要调试/无 skill 环境时，才参考第 2 节（uv 命令）。

1) `prd-plan`（PRD Plan；交互澄清 + 写真源）  
   - 触发意图示例：需求澄清 / 澄清需求 / PRD 计划  
   - 首次运行：若 `docs/prd-pack.json` 不存在，会自动初始化并写入真源骨架  
   - 目标：持续把“已确认事实”写进 `docs/prd-pack.json`（不输出 JSON 正文）  
2) `prd-check`（PRD Check；门禁校验 + 自动分配 ID）  
   - 触发意图示例：校验PRD / 检查PRD / 门禁  
   - 直到 `PASS`（若 `FAIL` 返回 `prd-plan` 修正真源）
3) `prd`（PRD Render；生成验收视图）  
   - 触发意图示例：生成PRD / 渲染PRD / 输出PRD  
   - 写入 `docs/PRD.md`（人工验收；若不符合预期返回 `prd-plan` 修真源）
4) `prd-slice`（PRD Slice；后续 Split Plan 必需）  
   - 触发意图示例：PRD 切片 / 切片 / 低噪切片 / slice  
   - 写入 `docs/prd-slices/`

### Stage 2: Scaffold（Plan → Check(PASS) → Render）

说明：
- Scaffold 流程通过 `textum` skill 的路由触发，不需要手动运行 CLI 命令；仅在你要调试/无 skill 环境时，才参考第 2 节（uv 命令）。

1) `scaffold-plan`（Scaffold Plan；交互澄清 + 写技术决策）  
   - 触发意图示例：上下文提取 / 全局上下文 / Scaffold 计划  
   - 首次运行：若 `docs/scaffold-pack.json` 不存在，会自动初始化并写入真源骨架  
   - 目标：把“已确认技术决策”写进 `docs/scaffold-pack.json`（不输出 JSON 正文）  
2) `scaffold-check`（Scaffold Check；门禁校验 + 自动补齐 extracted/source）  
   - 触发意图示例：校验GLOBAL-CONTEXT / 检查GLOBAL-CONTEXT / GC 门禁  
   - 直到 `PASS`（若 `FAIL` 返回 `scaffold-plan` 修正真源）
3) `scaffold`（Scaffold Render；生成阅读视图）  
   - 触发意图示例：生成GLOBAL-CONTEXT / 渲染GLOBAL-CONTEXT / 输出GLOBAL-CONTEXT  
   - 写入 `docs/GLOBAL-CONTEXT.md`（人工验收；若不符合预期返回 `scaffold-plan` 修真源）  
   - next：`Split Plan`

### Stage 3: Split（Plan → Check(PASS/DECISION) → Generate → Check1 → Check2 → Checkout）

前置：确保已完成 `PRD Slice`（存在 `docs/prd-slices/index.json`），且 `Scaffold Check` 已 `PASS`（`docs/scaffold-pack.json` 可用）。

说明：
- Split 流程通过 `textum` skill 的路由触发，不需要手动运行 CLI 命令；仅在你要调试/无 skill 环境时，才参考第 2 节（uv 命令）。

1) `split-plan`（Split Plan；交互澄清 + 写拆分规划）  
   - 首次运行：若 `docs/split-plan-pack.json` 不存在，会自动初始化并写入真源骨架  
   - 目标：写清 Story 边界/顺序、模块归属、API 归属（不输出 JSON 正文）  
   - 直到 `PASS`（或 `DECISION` 被处理；然后继续 Split Generate）
2) `split`（Split Generate；生成每个 Story 真源）  
   - 写入 `docs/stories/story-###-<slug>.json`
3) `split-check1`（Split Check1；结构/阈值门禁 + 生成交接索引）  
   - `PASS/DECISION`：写入 `docs/split-check-index-pack.json`，进入 Split Check2  
   - `FAIL`：返回 Split Plan；若触发“超标拆分建议”，会额外写入 `docs/split-replan-pack.json`（供你在 Split Plan 窗口参考）
4) `split-check2`（Split Check2；引用一致性 + 完整性门禁）  
   - 包含完整性门禁：Split Plan `story_count` 必须与实际生成的 Story 文件数一致  
   - `FAIL`：返回 Split Plan；`PASS`：进入 Split Checkout
5) `split-checkout`（Split Checkout；导出依赖图视图，便于人工检查顺序）  
   - 写入 `docs/story-mermaid.md`

### Stage 4: Story（Check → Pack → Exec / Full Exec）

前置：`docs/stories/story-###-<slug>.json` 已存在（Split Generate 已产出），且 `Scaffold Check` 已 `PASS`（包含 `extracted.modules_index`）。

说明：
- Story 流程通过 `textum` skill 的路由触发，不需要手动运行 CLI 命令；仅在你要调试/无 skill 环境时，才参考第 2 节（uv 命令）。

1) `story-check`（Story Check；单 Story 门禁）  
   - 触发意图示例：Story 校验 / Story Check / 单 Story 门禁  
   - 输入：story number `n`（例如 `4`）  
   - 读取：`docs/prd-pack.json`、`docs/scaffold-pack.json`、`docs/stories/story-###-<slug>.json`  
   - 输出：`PASS` 或 `FAIL`（按 `FAIL.fix` 指向的“单动作”处理后重跑；不要跳过门禁直接进入执行）  
   - next：`Story Pack`
2) `story-pack`（Story Pack；生成低噪执行包）  
   - 触发意图示例：Story 执行包生成 / Story Pack / 生成执行包  
   - 输入：story number `n`（例如 `4`）  
   - 写入：`docs/story-exec/story-###-<slug>/`（entry：`index.json`）  
   - 内置门禁：执行包必须自包含（`index.json.read[]` 不得越界/绝对路径）+ 预算不超标  
   - next：`Story Exec`
3) `story`（Story Exec；实现代码）  
   - 只读执行包：`docs/story-exec/story-###-<slug>/index.json` + `index.json.read[]` 列出的文件（requirements/context 真源）  
   - 可按需最小化读取 repo 代码文件来完成实现（不要通读仓库）  
   - 只实现该 Story 的 `feature_points` 与 `api_endpoints`，不发明新接口/新表/新字段
4) `story-full-exec`（Story Full Exec；实验：批量执行）  
   - 输入形如：`1/2/3`（按顺序执行；不回滚）

## 2) uv 命令（单独说明）

> 约定：始终带 `--project .codex/skills/textum/scripts`，把 Textum 依赖隔离在 `.codex/skills/textum/scripts/.venv`。

- `uv sync --project .codex/skills/textum/scripts`  
  - 作用：创建/更新 `.codex/skills/textum/scripts/.venv`，安装依赖（建议首次运行/依赖更新后执行一次）
- `uv run --project .codex/skills/textum/scripts textum <...>`  
  - 作用：运行 Textum CLI（所有 bundle 的 `init/check/render/slice/generate/...` 都通过它执行）
- PRD（手动运行/调试用；通常由各 stage 自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum prd init`（创建 `docs/prd-pack.json`；一般由 `prd-plan` 首次运行自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum prd check`  
  - `uv run --project .codex/skills/textum/scripts textum prd render`  
  - `uv run --project .codex/skills/textum/scripts textum prd slice`
- Scaffold（手动运行/调试用；通常由各 stage 自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum scaffold init`（创建 `docs/scaffold-pack.json`；一般由 `scaffold-plan` 首次运行自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum scaffold check`  
  - `uv run --project .codex/skills/textum/scripts textum scaffold render`
- Split（手动运行/调试用；通常由各 stage 自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum split plan init`（创建 `docs/split-plan-pack.json`；一般由 `split-plan` 首次运行自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum split plan check`  
  - `uv run --project .codex/skills/textum/scripts textum split generate`  
  - `uv run --project .codex/skills/textum/scripts textum split check1`  
  - `uv run --project .codex/skills/textum/scripts textum split check2`  
  - `uv run --project .codex/skills/textum/scripts textum split checkout`
- Story（手动运行/调试用；通常由各 stage 自动触发）  
  - `uv run --project .codex/skills/textum/scripts textum story check --n <n>`  
  - `uv run --project .codex/skills/textum/scripts textum story pack --n <n>`
  - `uv run --project .codex/skills/textum/scripts python -m ...`  
  - 作用：调试/检查（例如 `python -m compileall`），同样使用隔离环境

## 3) Skill → Python 脚本对应关系（便于维护）

说明：所有 CLI 入口都从 `.codex/skills/textum/scripts/textum_cli.py` 分发；下表只列“主要实现文件”（辅助模块省略或合并展示）。

### PRD

- `prd-plan` →（prompt-only）+ `textum prd init` → `prd_pack.py` / `prd_pack_validate.py`
- `prd-check` → `textum prd check` → `prd_pack_validate.py`
- `prd` → `textum prd render` → `prd_render.py`
- `prd-slice`（command-only）→ `textum prd slice` → `prd_slices.py` / `prd_slices_generate.py`

### Scaffold

- `scaffold-plan` →（prompt-only）+ `textum scaffold init` → `scaffold_pack.py`
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
- Split 交接索引：`docs/split-check-index-pack.json`；拆分建议：`docs/split-replan-pack.json`；依赖图视图：`docs/story-mermaid.md`
- Story 执行包（低噪切片）：`docs/story-exec/story-###-<slug>/index.json`（entry）
