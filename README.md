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

- Claude Code：把 `.claude/` 放到项目根目录（提供 `/prd-plan` 等命令）
- Codex：本仓库提供 skill 源码 `.codex/skills/textum/`；需要时复制到你的 Codex skills 目录（如 `$CODEX_HOME/skills/textum`）后使用
- （可选）Claude skill 版本：`.claude/skills/textum/`（自包含；不影响 `.claude/commands` 与 `.claude/textum`）

## 🎯 主流程命令

> 说明：下表为 Claude Code 的 `/...` 命令版；Codex 使用 `textum` skill（见 `.codex/skills/textum/SKILL.md`）按阶段路由执行。

| 步骤 | 命令 | 做什么 |
|------|------|--------|
| 1️⃣ | `/prd-plan` | 需求澄清，持续写入 `docs/prd-plan-pack.yaml`（唯一事实来源） |
| 2️⃣ | `/prd` | 读取 `docs/prd-plan-pack.yaml` 生成/修正 `docs/PRD.md`（信息不足则输出 `PRD_PLAN_CLARIFY_PACK`） |
| 3️⃣ | `/prd-check` | 机械性校验 PRD（结构/占位符/ID一致性），输出 `FAIL/DECISION/PASS` 清单；无 `FAIL`（`PASS` 或接受 `DECISION`）后 PRD 只读 |
| 4️⃣ | `/scaffold` | 从 PRD 提取全局约定/索引（GLOBAL-CONTEXT） |
| 5️⃣ | `/scaffold-check` | 机械性校验 GLOBAL-CONTEXT（缺章/占位符/噪音） |
| 6️⃣ | `/split-plan` | 先做低噪音拆分规划（Story 列表 + API 分配 + 依赖） |
| 7️⃣ | `/split` | 按规划生成 Story 文件（含 YAML front-matter：`fp_ids/refs/artifacts`） |
| 8️⃣ | `/split-check1`（无 `FAIL`）→ `/split-check2` | 拆分校验（结构/阈值 → 引用可追溯；有 API 时 Smoke Test） |
| 9️⃣ | `/split-checkout` | 导出 Story 依赖图（写入 `docs/story-mermaid.md`） |
| 🔟 | `/story-check 1`（无 `FAIL`）→ `/story-pack 1` → `/story 1` | 开始做第一个任务，然后按顺序继续 `/story-check 2` → `/story-pack 2` → `/story 2`... |

> 💡 小提示：每个步骤建议开一个新窗口；`*-check` 只输出清单、不自动跑下一步（若输出 `DECISION`，确认接受后再继续）；`/prd-check` 输出 `PASS/DECISION` 且确认接受后不要再修改 `docs/PRD.md`（要改就回到 `/prd` 并重跑后续步骤）；后续通过 PRD 详情锚点 `<!-- PRD#... -->` 精确定位（如 `<!-- PRD#API-001 -->` / `<!-- PRD#TBL-001 -->`），避免通读 PRD 与行号漂移

## 🧭 执行注意事项

- 按顺序执行 `/story 1`、`/story 2`、`/story 3`...（一次只跑一个）
- Story 有"前置 Story"时，先完成前置再做后续
- 实现阶段发现缺口？停下来确认是否要回到 `/prd` 修正（改了 PRD 需重跑后续步骤）

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
├── .claude/          # 🔧 Claude Code 命令与模板（/commands）
├── .codex/           # 🧰 Codex skills 源码（可选）
├── docs/             # 📄 生成的文档都在这
│   ├── prd-plan-pack.yaml               # 需求澄清计划包（唯一事实来源）
│   ├── PRD.md                        # 需求文档（定稿后不要改）
│   ├── GLOBAL-CONTEXT.md             # 全局约定/索引（/scaffold 生成；定稿后不改）
│   ├── split-plan.yaml               # 拆分规划（/split-plan 生成）
│   ├── split-check-index-pack.yaml   # 索引交接包（/split-check1 生成）
│   ├── story-mermaid.md              # Story 依赖图（/split-checkout 生成）
│   ├── story-1-slug.md               # 任务清单
│   └── story-1-exec-pack.yaml        # 执行包（/story-pack 生成）
└── src/              # 💻 代码会写在这
```

## 🎬 实际使用是这样的

**第一步：聊需求**
```
你：/prd-plan
AI：你好！告诉我你想做一个什么样的应用？
你：我想做一个记账的小程序
AI：好的！这个记账应用是给谁用的呢？...
AI：...（多轮澄清后更新 docs/prd-plan-pack.yaml，并输出 READY）
```

**后面的步骤**
```
你：/prd              → 读取 docs/prd-plan-pack.yaml，生成/修正 docs/PRD.md（或返回 PRD_PLAN_CLARIFY_PACK）
你：/prd-check         → 输出 FAIL/DECISION/PASS 清单；无 FAIL（PASS 或接受 DECISION）后 PRD 只读
你：/scaffold         → 生成全局上下文
你：/scaffold-check   → 校验全局上下文
你：/split-plan       → 生成拆分规划（Story列表 + API分配）
你：/split            → 生成 Story 文件（含 YAML front-matter：`fp_ids/refs/artifacts`）
你：/split-check1     → 拆分校验（Core：结构/一致性/阈值）
你：/split-check2     → 拆分校验（引用可追溯 + 有 API 时 Smoke Test）
你：/split-checkout   → 导出 Story 依赖图（docs/story-mermaid.md）
你：/story-check 1    → 单 Story 门禁校验
你：/story-pack 1     → 写入 `docs/story-1-exec-pack.yaml`（`STORY_EXEC_PACK`）
你：/story 1          → 开始第一个任务！
```

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

MIT
