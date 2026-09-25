# 第二大脑 — 欢迎向导

使用 LLM Wiki 模式设置新的 Obsidian 知识库。LLM 扮演图书管理员的角色——阅读原始资料，将其编译成结构化的互链 wiki，并随着时间的推移维护它。

## 向导流程

引导用户完成以下 5 个步骤。每次只问一个问题。每个步骤都有一个合理的默认值——用户可以接受它或提供自己的值。

### 第 1 步：知识库名称

询问：
> "您想如何命名您的知识库？这将作为文件夹名称。"
> 默认值：`second-brain`

接受用户提供的任何名称。这将作为文件夹名称和在代理配置中的标题。

### 第 2 步：知识库位置

询问：
> "我应该在哪里创建它？给我一个路径，或者我将使用默认路径。"
> 默认值：`~/Documents/`

接受任何绝对或相对路径。将 `~` 解析为用户的家目录。最终的 vault 路径是 `{location}/{vault-name}/`。

### 第 3 步：领域 / 主题

询问：
> "这个知识库是关于什么的？这有助于我设置相关的标签并描述 vault 的用途。"
>
> 示例："AI 研究"、"金融科技初创公司的竞争情报"、"个人健康与健身"

接受自由文本。使用它来：
- 为代理配置编写一行领域描述
- 生成 5-8 个与领域相关的建议标签

### 第 4 步：代理配置

自动检测正在运行此技能的代理。明确说明：
> "我正在 **[Agent Name]** 中运行，因此我将为这个 vault 生成 **[config file]**。"

然后询问：
> "您是否使用其他 AI 代理需要配置文件？选项：Claude Code、Codex、Cursor、Gemini CLI —— 或跳过。"

跳过自动检测到的代理。为所有选定的代理生成配置文件。

**代理检测逻辑：**
- 如果使用 `CLAUDE.md` 约定或技能工具是 Claude Code 的 → Claude Code
- 如果环境指示 Codex → Codex
- 如果工作目录中存在 `.cursor/` → Cursor
- 如果使用 `GEMINI.md` 约定 → Gemini CLI
- 如果不确定，询问用户他们正在使用哪个代理

### 第 5 步：可选的 CLI 工具

询问：
> "这些工具扩展了 LLM 在您的 vault 中的功能。全部可选但推荐："
>
> 1. **summarize** — 从 CLI 摘要链接、文件和媒体
> 2. **qmd** — 您 wiki 的本地搜索引擎（随着其增长变得很有帮助）
> 3. **agent-browser** — 用于网络研究的浏览器自动化
>
> "全部安装、选择特定的工具（例如 '1 和 3'），或跳过？"

## 向导后：搭建 vault

收集所有答案后，按顺序执行以下步骤：

### 1. 创建目录结构

运行欢迎脚本，传递完整的 vault 路径：

```
bash <skill-directory>/scripts/onboarding.sh <vault-path>
```

这将创建所有目录以及初始的 `wiki/index.md` 和 `wiki/log.md` 文件。

### 2. 生成代理配置文件

为每个选定的代理，从 `<skill-directory>/references/agent-configs/` 读取相应的模板：

| 代理 | 模板 | 输出文件 | 输出位置 |
|---|---|---|---|
| Claude Code | `claude-code.md` | `CLAUDE.md` | vault 根目录 |
| Codex | `codex.md` | `AGENTS.md` | vault 根目录 |
| Cursor | `cursor.md` | `second-brain.mdc` | `<vault>/.cursor/rules/` |
| Gemini CLI | `gemini.md` | `GEMINI.md` | vault 根目录 |

对于每个模板，替换占位符：

- `{{VAULT_NAME}}` → 第 1 步中的 vault 名称
- `{{DOMAIN_DESCRIPTION}}` → 从第 3 步派生的一行描述
- `{{DOMAIN_TAGS}}` → 基于第 3 步的领域生成 5-8 个领域相关标签，以项目符号列表的形式
- `{{WIKI_SCHEMA}}` → 读取 `<skill-directory>/references/wiki-schema.md` 并插入从 `## 架构` 开始的所有内容

将生成的配置写入 vault。

### 3. 更新 wiki/log.md

追加设置条目：

```
## [YYYY-MM-DD] setup | Vault 初始化
为 {{DOMAIN_DESCRIPTION}} 创建了 vault "{{VAULT_NAME}}"。
代理配置：{{生成的配置文件列表}}。
```

### 4. 安装 CLI 工具（如果选定）

对于用户在第 5 步中选定的每个工具，运行安装命令：

- summarize: `npm i -g @steipete/summarize`
- qmd: `npm i -g @tobilu/qmd`
- agent-browser: `npm i -g agent-browser && agent-browser install`

每次安装后，使用 `<tool> --version` 进行验证。报告每个工具的成功或失败。

### 5. 显示摘要

向用户显示：

1. **已创建的内容** — 目录树和配置文件
2. **下一步操作** — 安装 Obsidian Web Clipper 浏览器扩展：
   > 安装 Obsidian Web Clipper 以轻松将网络文章保存到您的 vault：
   > https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf
3. **如何开始** — 在 Obsidian 中打开 vault 文件夹，将文章剪辑到 `raw/`，然后运行 `/second-brain-ingest`

## 参考文件

这些文件随此技能捆绑并提供在 `<skill-directory>/references/`：

- `wiki-schema.md` — 标准的 wiki 规则（所有代理配置的单一事实来源）
- `tooling.md` — CLI 工具详情、安装命令和验证步骤
- `agent-configs/claude-code.md` — CLAUDE.md 模板
- `agent-configs/codex.md` — AGENTS.md 模板
- `agent-configs/cursor.md` — Cursor 规则模板
- `agent-configs/gemini.md` — GEMINI.md 模板

## 下一步

设置完成后，用户的流程是：

1. **将文章剪辑到 `raw/`** 使用 Obsidian Web Clipper
2. **使用 `/second-brain-ingest` 吸收来源** — 将原始文件处理成 wiki 页面
3. **使用 `/second-brain-query` 提问** — 从 wiki 搜索和综合信息
4. **使用 `/second-brain-lint` 进行健康检查** — 每次吸收 10 次或每月运行一次
