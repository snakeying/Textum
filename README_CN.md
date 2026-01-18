<h1 align="center">
🕸️ Textum
</h1>

<p align="center">
  <strong>把你的想法，编织成可运行的代码</strong>
</p>

<p align="center">
  一个让 AI 少犯错的工作流 <br/>
  <em>不是让 AI 更聪明，而是让过程更可控</em>
</p>

> ⚠️ **注意**：旧的 commands 版本已废弃，不再支持。当前仅支持 SKILL 版本。

## 🤔 这是干什么的?

你是否遇到过这种情况：

- 💬 跟 AI 聊了半天需求，结果它写到一半就忘了前面说的
- 🔄 需求改了一点，整个代码都得重写
- 🎲 每次生成的结果都不一样，质量全靠运气

**Textum 就是用来解决这些问题的。**

它不会让 AI 变得更聪明，但会通过**流程和校验**，让 AI 少犯一些本可以避免的错误。

---

## ✨ 它怎么工作？

你只需要用自己的话描述想法，Textum 会帮你把整个过程拆成 4 个阶段：

### 第 1 步：📝 需求澄清（PRD）
> "你想做什么？"

AI 会跟你聊天，把模糊的想法变成清晰的需求文档。  
每个功能点都会被编号（比如 FP-001），API 也会编号（比如 API-001），后面就用编号代替长篇大论。

### 第 2 步：🏗️ 技术决策（Scaffold）
> "用什么技术？怎么组织代码？"

确定整体架构、技术选型、模块划分。  
这一步会生成一份"全局上下文"，后面写代码都按这个来。

### 第 3 步：🧩 任务拆分（Split）
> "按什么顺序实现？"

把需求拆成一个个小任务（Story），就像便利贴一样。  
每个 Story 只做一件事，完成一个再开始下一个。

### 第 4 步：💻 代码实现（Story）
> "开始写代码！"

AI 一次只实现一个 Story，不会被其他无关信息干扰。
每个 Story 写完都有校验，确保没跑偏。

> ⚠️ **试验性功能**：`Story 批量执行` 支持批量执行多个 Story（按顺序，不回滚）。此功能尚在试验阶段，请自行评估风险后使用。 ⚠️

---

## 🎯 为什么要分这么多步？

想象一下：你写了一份 10 页的需求文档，丢给 AI 说"帮我全写出来"。  
结果呢？

写到第 5 个功能的时候，AI 已经忘了第 1 个功能里的字段叫什么了。😅

**这不是 AI 笨，是它的"记忆"有限** — 信息越多，越容易丢失重点。

所以 Textum 的核心思路就是：**少即是多**

| 传统做法 | Textum 的做法 |
|----------|---------------|
| 一次性给 AI 所有需求 | 📦 分阶段喂，每次只给当前需要的 |
| 每次都说"那个用户登录的接口" | 🔗 用 API-001 代替，简洁不歧义 |
| 改需求要重新生成全部代码 | 🎯 只重新生成受影响的部分 |

---

## 📏 适合什么样的项目？

| 项目规模 | 功能数量 | 实际情况 | 举个例子 |
|----------|----------|----------|----------|
| 🌱 小型 | 10-15 个 | ✅ 可靠完成 | 记账本、待办清单、个人笔记 |
| 🌿 中型 | 15-25 个 | ✅ 可靠完成 | 简单博客、问卷系统 |
| 🌳 较大 | 25-35 个 | ⚠️ 需要人工校验 | 多角色后台、预约平台 |

> 💡 **更大的项目？** 建议拆成几个独立子项目，分别用 Textum 处理。

**模拟测试报告**

 SKILL 版本的测试报告
- [1.0](./simulate-test-reports/e2e-run-1.0_CN.md)
- [1.1](./simulate-test-reports/e2e-run-1.1_CN.md) 
- [1.3](./simulate-test-reports/e2e-run-1.3_CN.md) 
- [1.5](./simulate-test-reports/e2e-run-1.5_CN.md)

⚠️（以下测试基于旧 commands 版本，采用 Claude Opus 4.5。请注意：commands版本已经废弃，仅供参考）
- [V2](./simulate-test-reports/v2simulate-test-report-opus_CN.md) | [V3](./simulate-test-reports/v3simulate-test-report-opus_CN.md) | [V4](./simulate-test-reports/v4simulate-test-report-opus_CN.md)
- [V5](./simulate-test-reports/v5simulate-test-report-opus_CN.md)（从 V5 开始任务更复杂） | [V6](./simulate-test-reports/v6simulate-test-report-opus_CN.md) | [Beta](./simulate-test-reports/beta-simulate-test-report-opus_CN.md)

### ❌ 不太适合的场景

- **实时性要求极高**：Textum 需要时间走完流程，不适合"改个 bug 马上上线"
- **非常简单的任务**：比如"把这个按钮颜色改成红色"，直接改比走流程快
- **完全不确定需求**：如果你自己都不知道要做什么，Textum 帮不了你 😅

---

## 🚀 怎么开始使用？

### 1️⃣ 安装 uv

```bash
# macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者用包管理器（可选）
brew install uv  # macOS
```

> 💡 **uv 是什么？** 一个超快的 Python 包管理工具（类似 npm 之于 Node.js）

### 2️⃣ 初始化项目

在你的项目根目录执行：

```bash
# 如果你用 Codex
uv sync --project .codex/skills/textum/scripts

# 如果你用 Claude Code
uv sync --project .claude/skills/textum/scripts
```

✅ 这会自动：
- 检查 Python 版本（需要 >= 3.11）
- 创建隔离的虚拟环境（不会污染你的业务项目）
- 安装所有依赖

### 3️⃣ 开始使用

打开你的 AI 助手（Codex/Claude Code），说：

> "我想用 Textum 开始一个新项目"

AI 会引导你完成整个流程 🎯

👉 **想看详细的技术文档？** 查看 [Workflow](./Workflow_CN.md)

---

## 🕸️ 为什么叫 Textum？

> *"The Machine 真正强大的地方从来不是某个单点判断，而是它把零散的人、事件和时间编织成了一张网。"*  
> — 致敬 *Person of Interest*

单独看，每一条信息都没有意义；被织在一起之后，因果才开始显现。

**Textum** 在拉丁语里意味着"被编织成整体的结构"。这个项目扮演的正是这样的角色：它不创造智能，只负责把需求、上下文和故事线编织在一起。

当织网完成，行动的路径就已经存在了。

---

## 🙏 如果你觉得有用

- ⭐ **给个 Star** — 让更多人发现它
- 🐛 **提 Issue** — 告诉我哪里可以改进
- 💬 **分享使用场景** — 我可能会写成 case study

谢谢 🎉

---

## 📜 License

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[![Star History Chart](https://api.star-history.com/svg?repos=snakeying/Textum&type=Date)](https://star-history.com/#snakeying/Textum&Date)
