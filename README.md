<h1 align="center">
🕸️ Textum
</h1>

把你的想法，编织成可运行的代码。

Textum 是一个帮助你从"我想做一个xxx"到"项目完成"的工作流工具。即使你没有编程经验，也能通过对话一步步把想法变成现实。

## ✨ 它能帮你做什么？

你只需要用自己的话描述想法，Textum 会帮你：

- 📝 把模糊的想法变成清晰的需求文档（PRD）
- 🧩 自动拆分成一个个可执行的小任务（Story）
- 🔗 理清任务之间的依赖关系，告诉你先做什么、后做什么
- 💻 一步步把每个任务变成真正能跑的代码

整个过程有多个校验点，确保不会跑偏。

[详细的流程说明](./Workflow.md) 

## 📦 安装

前置条件：
- 已安装 `uv`
- Python >= 3.11（推荐 3.11；本仓库测试基于 3.11）

在项目根目录执行一次：
- `uv sync --project .codex/skills/textum/scripts`（会创建 `.codex/skills/textum/scripts/.venv` 并安装依赖）

## 🎯 当前支持：PRD bundle + Scaffold bundle + Split bundle

文件：
- 真源：`docs/prd-pack.json`
- 阅读视图：`docs/PRD.md`（生成后不手改；要改请改 `docs/prd-pack.json` 并重跑）
- 真源：`docs/scaffold-pack.json`
- 阅读视图：`docs/GLOBAL-CONTEXT.md`（生成后不手改；要改请改 `docs/scaffold-pack.json` 并重跑）
- 真源：`docs/split-plan-pack.json`
- 真源：`docs/stories/story-###-<slug>.json`
- 交接索引：`docs/split-check-index-pack.json`

命令（在项目根目录）：
- `uv run --project .codex/skills/textum/scripts textum prd init`（首次初始化）
- `uv run --project .codex/skills/textum/scripts textum prd check`（门禁校验 + 自动分配 ID）
- `uv run --project .codex/skills/textum/scripts textum prd render`（生成 `docs/PRD.md`）
- `uv run --project .codex/skills/textum/scripts textum prd slice`（生成低噪切片到 `docs/prd-slices/`）
- `uv run --project .codex/skills/textum/scripts textum scaffold init`（初始化 `docs/scaffold-pack.json`）
- `uv run --project .codex/skills/textum/scripts textum scaffold check`（门禁校验 + 自动抽取 PRD 上下文）
- `uv run --project .codex/skills/textum/scripts textum scaffold render`（生成 `docs/GLOBAL-CONTEXT.md`）
- `uv run --project .codex/skills/textum/scripts textum split plan init`（初始化 `docs/split-plan-pack.json`）
- `uv run --project .codex/skills/textum/scripts textum split plan check`（门禁校验）
- `uv run --project .codex/skills/textum/scripts textum split generate`（生成 `docs/stories/story-*.json`）
- `uv run --project .codex/skills/textum/scripts textum split check1`（结构/阈值门禁 + 写入 `docs/split-check-index-pack.json`）
- `uv run --project .codex/skills/textum/scripts textum split check2`（引用一致性门禁）

交互（Codex）：
- 使用 `textum` skill（见 `.codex/skills/textum/SKILL.md`），在 `PRD Plan` 阶段用中文对话澄清并写入 `docs/prd-pack.json`

> 旧的命令版与旧 templates 已废弃并移动到 `outdated/`。

## 🧭 执行注意事项

- 建议每个阶段开新窗口，减少上下文污染
- `docs/PRD.md` 为生成视图：不要手改；要改请改 `docs/prd-pack.json` 并重跑 `uv run --project .codex/skills/textum/scripts textum prd render`
- 若 PRD 不符合用户预期：后续步骤都应视为作废，先把 PRD 改对再继续

## 🧪 关于 Python 环境冲突（重要）

Textum 的 Python 依赖仅用于 skill 运行，建议始终用 `--project .codex/skills/textum/scripts`：

- ✅ 推荐：`uv sync --project .codex/skills/textum/scripts`、`uv run --project .codex/skills/textum/scripts ...`（`.venv` 在 `.codex/skills/textum/scripts/.venv`，与业务项目环境隔离）
- ⚠️ 避免：在项目根目录直接 `uv sync` / `uv run`（不带 `--project`），否则可能把 Textum 依赖装进你的业务项目虚拟环境

## 💡 为什么这么设计

试过把详细 PRD 直接丢给模型吗？结果往往是：写到模块 D 的时候，模块 A 定义的字段名已经忘得差不多了。

这不是哪个工具的锅，是现阶段 LLM 的局限——上下文越长，关键信息越容易被淹没。

所以这个流程的核心就俩字：**降噪**。

- 每个阶段开新窗口，别让历史上下文污染当前任务
- 引用全用稳定 ID 锚点（`<!-- PRD#API-001 -->` 这种），别指望模型记住"上面说的那个接口"
- 执行阶段只给当前 Story 需要的上下文，不让模型通读整个 PRD

技术细节见 [Workflow.md](./Workflow.md)

## 📁 文件会放在哪？

```
你的项目/
├── .codex/           # 🧰 Codex skills 源码（可选）
├── docs/             # 📄 生成的文档都在这
│   ├── prd-pack.json                 # PRD 真源（JSON）
│   └── PRD.md                        # PRD 阅读视图（生成；不手改）
│   ├── scaffold-pack.json            # Scaffold 真源（JSON）
│   └── GLOBAL-CONTEXT.md             # 全局上下文（生成；不手改）
│   ├── split-plan-pack.json           # Split 规划真源（JSON）
│   ├── split-check-index-pack.json    # Split 交接索引（JSON）
│   └── stories/                       # Story 真源（JSON；每个 story 一个文件）
│       └── story-###-<slug>.json
└── src/              # 💻 你的代码目录
```

## 🎬 实际使用（PRD bundle）

1) `uv run --project .codex/skills/textum/scripts textum prd init`
2) 用 `textum` skill 的 `PRD Plan` 把事实写进 `docs/prd-pack.json`
3) `uv run --project .codex/skills/textum/scripts textum prd check` 直到 `PASS`
4) `uv run --project .codex/skills/textum/scripts textum prd render` 生成 `docs/PRD.md` 并人工验收
5) （可选）`uv run --project .codex/skills/textum/scripts textum prd slice` 生成低噪切片到 `docs/prd-slices/`

## 🎬 实际使用（Scaffold bundle）

1) `uv run --project .codex/skills/textum/scripts textum scaffold init`
2) 用 `textum` skill 的 `Scaffold Plan` 把技术决策写进 `docs/scaffold-pack.json`
3) `uv run --project .codex/skills/textum/scripts textum scaffold check` 直到 `PASS`
4) `uv run --project .codex/skills/textum/scripts textum scaffold render` 生成 `docs/GLOBAL-CONTEXT.md`

## 🎬 实际使用（Split bundle）

1) `uv run --project .codex/skills/textum/scripts textum split plan init`
2) 用 `textum` skill 的 `Split Plan` 把规划写进 `docs/split-plan-pack.json`
3) `uv run --project .codex/skills/textum/scripts textum split plan check` 直到 `PASS/DECISION`
4) `uv run --project .codex/skills/textum/scripts textum split generate` 生成 `docs/stories/`
5) `uv run --project .codex/skills/textum/scripts textum split check1` 直到 `PASS/DECISION`
6) `uv run --project .codex/skills/textum/scripts textum split check2` 直到 `PASS`

## 📏 适合多大的项目？

| 规模 | 功能数 | 实际情况 | 举个例子 |
|------|--------|----------|----------|
| 🌱 小型 | 10-15 | ✅ 可靠完成 | 记账本、待办清单、个人笔记 |
| 🌿 中型 | 15-25 | ✅ 可靠完成 | 简单博客、问卷系统 |
| 🌳 较大 | 25-35 | ⚠️ 需人工校验，中等风险 | 多角色后台、预约平台 |

[V2版本模拟测试报告](/simulate-test-reports/v2simulate-test-report-opus.md) 

[V3版本模拟测试报告](/simulate-test-reports/v3simulate-test-report-opus.md) 

[V4版本模拟测试报告](/simulate-test-reports/v4simulate-test-report-opus.md) 

[V5版本模拟测试报告](/simulate-test-reports/v5simulate-test-report-opus.md)  <--V5开始的模拟任务相对V2/3/4, 更为复杂模糊。

[V6版本模拟测试报告](/simulate-test-reports/v6simulate-test-report-opus.md)

[beta版本模拟测试报告](/simulate-test-reports/beta-simulate-test-report-opus.md)

以上模拟均采用 Claude opus 4.5 模型。

**⚠️ 模拟测试不代表实际项目运行时的效果，仅供参考。**

> 更大的项目？建议拆成几个独立子项目。

---

## 🕸️ 为什么叫 Textum？

> *"The Machine 真正强大的地方从来不是某个单点判断，而是它把零散的人、事件和时间编织成了一张网。"*
>
> — 致敬 *Person of Interest*

单独看，每一条信息都没有意义；被织在一起之后，因果才开始显现。

**Textum** 在拉丁语里意味着"被编织成整体的结构"。这个项目扮演的正是这样的角色：它不创造智能，只负责把需求、上下文和故事线编织在一起。

当织网完成，行动的路径就已经存在了。

---

## 📜 License

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)


[![Star History Chart](https://api.star-history.com/svg?repos=snakeying/Textum&type=Date)](https://star-history.com/#snakeying/Textum&Date)
