<h1 align="center">
🕸️ Textum
</h1>

<p align="center">
  <strong>Weave your ideas into runnable code</strong>
</p>

<p align="center">
  A workflow that helps AI make fewer mistakes <br/>
  <em>Not by making AI smarter, but by making the process more controllable</em>
</p>

<p align="center">
    <br> English | <a href="README_CN.md">中文</a>
</p>

> ⚠️ **Note**: The old commands version is deprecated and no longer supported. Only the skill version is currently supported.

## 🤔 What's this all about?

Ever run into these problems?

- 💬 You spend ages explaining requirements to AI, only for it to forget what you said halfway through
- 🔄 One tiny requirement change and suddenly you're rewriting everything
- 🎲 Every generation is a roll of the dice — quality is pure luck

**That's exactly what Textum is here to fix.**

It won't make AI any smarter, but through **structured workflow and validation**, it helps AI avoid the kind of mistakes that shouldn't happen in the first place.

---

## ✨ How does it work?

Just describe your idea in plain language. Textum breaks the whole thing down into 4 phases:

### Step 1: 📝 Requirements Clarification (PRD)
> "So, what are we building?"

AI chats with you to turn fuzzy ideas into a clear requirements doc.
Every feature gets a number (like FEATURE-001) — no more repeating yourself later.

### Step 2: 🏗️ Technical Decisions (Scaffold)
> "What's the tech stack? How do we structure this?"

Lock down the architecture, pick your technologies, define the modules.
This creates a "global context" that keeps all the coding consistent.

### Step 3: 🧩 Task Breakdown (Split)
> "What's the game plan?"

Break requirements into bite-sized tasks (Stories) — think sticky notes.
One Story, one job. Finish it, then move on.

### Step 4: 💻 Code Implementation (Story)
> "Let's write some code!"

AI tackles one Story at a time, laser-focused without distractions.
Each Story gets validated when done — no drifting off course.

> ⚠️ **Experimental**: `Story Full Exec` supports batch execution of multiple Stories (sequential, no rollback). This feature is experimental — use at your own discretion. ⚠️

---

## 🎯 Why all these steps?

Picture this: you hand AI a 10-page requirements doc and say "build it all."
What happens?

By feature #5, AI has already forgotten what fields were in feature #1. 😅

**It's not that AI is dumb — it just has limited "memory."** The more info you throw at it, the easier it loses track.

That's why Textum's philosophy is simple: **Less is more**

| The Old Way | The Textum Way |
|-------------|----------------|
| Dump all requirements on AI at once | 📦 Feed it phase by phase, only what's needed now |
| Keep saying "you know, that login API thing" | 🔗 Just say API-001 — short and unambiguous |
| One requirement change = regenerate everything | 🎯 Only regenerate what's actually affected |

---

## 📏 What kind of projects work best?

| Project Size | Feature Count | What to Expect | Examples |
|--------------|---------------|----------------|----------|
| 🌱 Small | 10-15 | ✅ Solid results | Expense tracker, todo app, personal notes |
| 🌿 Medium | 15-25 | ✅ Solid results | Simple blog, survey system |
| 🌳 Larger | 25-35 | ⚠️ Needs human review | Multi-role admin panel, booking platform |

> 💡 **Even bigger?** Split it into independent sub-projects and run each through Textum separately.

**Simulation Test Reports**

SKILL version test reports:
- [1.0](./simulate-test-reports/e2e-run-1.0_EN.md)
- [1.1](./simulate-test-reports/e2e-run-1.1_EN.md)
- [1.3](./simulate-test-reports/e2e-run-1.3_EN.md)
- [1.5](./simulate-test-reports/e2e-run-1.5_EN.md)

⚠️ (Tests below are based on the old commands version using Claude Opus 4.5. Note: commands version is deprecated, for reference only)
- [V2](./simulate-test-reports/v2simulate-test-report-opus_EN.md) | [V3](./simulate-test-reports/v3simulate-test-report-opus_EN.md) | [V4](./simulate-test-reports/v4simulate-test-report-opus_EN.md)
- [V5](./simulate-test-reports/v5simulate-test-report-opus_EN.md) (complexity ramps up from V5) | [V6](./simulate-test-reports/v6simulate-test-report-opus_EN.md) | [Beta](./simulate-test-reports/beta-simulate-test-report-opus_EN.md)

### ❌ When Textum isn't the right fit

- **Need it done yesterday**: Textum takes time to run through the workflow — not great for "hotfix and ship NOW"
- **Dead simple tasks**: Like "make this button red" — just do it, don't overthink it
- **No idea what you want**: If you can't describe it, Textum can't help 😅

---

## 🚀 Getting Started

### 1️⃣ Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via package manager
brew install uv  # macOS
pip install uv   # any platform
```

> 💡 **What's uv?** A blazing-fast Python package manager (think npm, but for Python)

### 2️⃣ Initialize the project

In your project root:

```bash
# For Codex users
uv sync --project .codex/skills/textum/scripts

# For Claude Code users (🚧 Coming soon)
uv sync --project .claude/skills/textum/scripts
```

✅ This automatically:
- Checks your Python version (needs >= 3.11)
- Creates an isolated virtual environment (keeps your project clean)
- Installs all dependencies

### 3️⃣ Start building

Fire up your AI assistant (Codex/Claude Code) and say:

> "I want to start a new project with Textum"

AI will walk you through the rest 🎯

👉 **Want the technical deep-dive?** Check out [Workflow](./Workflow.md)

---

## 🕸️ Why "Textum"?

> *"The Machine's true power was never in any single judgment, but in weaving scattered people, events, and time into a web."*
> — A tribute to *Person of Interest*

On their own, individual pieces of information mean nothing. Woven together, patterns emerge.

**Textum** is Latin for "something woven into a whole." That's exactly what this project does: it doesn't create intelligence — it weaves requirements, context, and storylines together.

Once the web is complete, the path forward reveals itself.

---

## 🙏 Found it useful?

- ⭐ **Star the repo** — Help others find it
- 🐛 **Open an Issue** — Let me know what could be better
- 💬 **Share your story** — Might turn it into a case study

Thanks! 🎉

---

## 📜 License

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[![Star History Chart](https://api.star-history.com/svg?repos=snakeying/Textum&type=Date)](https://star-history.com/#snakeying/Textum&Date)
