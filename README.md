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

把 `.claude` 文件夹放到你的项目里就行了，就这么简单。

## 🎯 主流程命令（推荐）

| 步骤 | 命令 | 做什么 |
|------|------|--------|
| 1️⃣ | `/prd-plan` | 需求澄清，输出 `PRD_INPUT_PACK`（复制交接包） |
| 2️⃣ | `/prd` | 用 `PRD_INPUT_PACK` 生成/修正 `docs/PRD.md`（信息不足则输出 `PRD_CLARIFY_PACK`） |
| 3️⃣ | `/prd-check` | 机械性校验 PRD（结构/占位符/ID一致性）；`PASS` 后 PRD 只读 |
| 4️⃣ | `/scaffold` | 从 PRD 提取全局约定/索引（GLOBAL-CONTEXT） |
| 5️⃣ | `/scaffold-check` | 机械性校验 GLOBAL-CONTEXT（缺章/占位符/噪音） |
| 6️⃣ | `/split-plan` | 先做低噪音拆分规划（Story 列表 + API 分配 + 依赖） |
| 7️⃣ | `/split` | 按规划生成 Story 文件并补齐 `PRD#<ID>` 引用 |
| 8️⃣ | `/split-check` | 严格校验拆分结果（与 split-plan 一致、API 覆盖/唯一归属、依赖无环、引用可定位） |
| 9️⃣ | `/backfill` | 回填 GLOBAL-CONTEXT 的“规则涉及 Story / 依赖图”索引 |
| 🔟 | `/story-check 1` → `PASS` 后 `/story-pack 1` → `/story 1` | 开始做第一个任务，然后按顺序继续 `/story-check 2` → `/story-pack 2` → `/story 2`... |

> 💡 小提示：每个步骤建议开一个新窗口；`*-check` 只输出清单、不自动跑下一步；`/prd-check` `PASS` 后不要再修改 `docs/PRD.md`（要改就回到 `/prd` 并重跑后续步骤）；后续 Story 通过稳定 ID 锚点 `PRD#<ID>` 精确引用，避免通读 PRD 与行号漂移

## 🧭 执行注意事项（强烈推荐看一遍）

- 一次只跑一个 `/story N`：按顺序跑 `/story 1`、`/story 2`、`/story 3`...
- 如果同一个编号出现多个 `docs/story-N-*.md`：先回到 `/split` 修正，然后重跑 `/split-check` 与 `/backfill`
- Story 声明了“前置 Story”：先完成并合入前置，再做后续（避免并行冲突）
- 实现阶段不发明新规则/新枚举/新接口：发现缺口就停下来确认是否要回到 `/prd` 修正规格（若 PRD 需要改动，需重跑后续步骤）
- 为了省 token：`/story` 只读取 `STORY_EXEC_PACK`（由 `/story-pack` 生成，包含 Story/GC 与被引用的 PRD 块原文），不再通读 PRD/GC/Story

## 🧱 低噪音约束（v2）

- Story 引用 PRD：统一使用 `PRD#<ID>`（如 `PRD#API-001` / `PRD#TBL-001` / `PRD#BR-001`）；规则优先用 `GC#BR-###`
- PRD 块边界锚点：每个表/接口详情标题行必须包含 `<!-- PRD#TBL-### -->` / `<!-- PRD#API-### -->`（数字一致），供 `/story-pack` 机械抽取
- `N/A` vs `TBD`：`N/A`=不适用；`TBD`=等待回填（仅允许出现在 `GLOBAL-CONTEXT` 规则表“涉及Story”列与依赖图）
- 大 Story 早期短路：`/split-check` 触发阈值会输出 `SPLIT_REPLAN_PACK`，用于回到 `/split-plan` 拆分重规划

## 📁 文件会放在哪？

```
你的项目/
├── .claude/          # 🔧 工具本身（你下载的）
├── docs/             # 📄 生成的文档都在这
│   ├── PRD.md           # 需求文档（定稿后不要改）
│   ├── GLOBAL-CONTEXT.md # 全局约定/索引（/backfill 回填索引）
│   ├── split-plan.md     # 拆分规划（/split-plan 生成）
│   └── story-1-slug.md   # 任务清单
└── src/              # 💻 代码会写在这
```

## 🎬 实际使用是这样的

**第一步：聊需求**
```
你：/prd-plan
AI：你好！告诉我你想做一个什么样的应用？
你：我想做一个记账的小程序
AI：好的！这个记账应用是给谁用的呢？...
AI：...（多轮澄清后输出 PRD_INPUT_PACK）
```

**后面的步骤**
```
你：/prd              → 粘贴 PRD_INPUT_PACK，生成/修正 docs/PRD.md（或返回 PRD_CLARIFY_PACK）
你：/prd-check         → 机械校验并补齐，直到 PASS；从此 PRD 只读
你：/scaffold         → 生成全局上下文
你：/scaffold-check   → 校验全局上下文
你：/split-plan       → 生成拆分规划（Story列表 + API分配）
你：/split            → 生成 Story 文件并补齐 PRD#<ID> 引用
你：/split-check      → 严格校验拆分结果
你：/backfill         → 回填依赖图和规则索引
你：/story-check 1    → 单 Story 门禁校验
你：/story-pack 1     → 生成低噪音执行包（复制交接包）
你：/story 1          → 开始第一个任务！
```

## 📏 适合多大的项目？

| 规模 | 功能数 | 实际情况 | 举个例子 |
|------|--------|----------|----------|
| 🌱 小型 | 10-15 | ✅ 可靠完成 | 记账本、待办清单、个人笔记 |
| 🌿 中型 | 15-25 | ✅ 可靠完成 | 简单博客、问卷系统 |
| 🌳 较大 | 25-35 | ⚠️ 需人工校验，中等风险 | 多角色后台、预约平台 |

> 更大的项目？老实说，建议拆成几个独立子项目 🙏

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
