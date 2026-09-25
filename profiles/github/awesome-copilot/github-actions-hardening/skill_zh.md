# GitHub Actions 强化

一个专注于 GitHub Actions 工作流安全的审查工具。它针对 Actions 特有的威胁模型进行推理——信任边界存在于触发类型、令牌作用域和字符串插值中——而不是通用安全扫描器寻找的应用代码漏洞。大多数工作流风险对语言格式化工具来说是不可见的，因为危险代码本身就是 YAML 文件，以及 GitHub 在脚本运行前将 `${{ }}` 表达式扩展为 shell 的方式。

## 使用此技能的场景

在以下情况下使用此技能：

* 审查、审计或强化 `.github/workflows/` 下的任何文件
* 编写新工作流并希望其默认安全
* 使用 `pull_request_target`、`workflow_run` 或 `issue_comment` 触发器的工作流
* 关于 `GITHUB_TOKEN` 权限或 `permissions:` 键的问题
* 固定 Actions 到提交 SHA、标签还是分支
* 在 `run:` 步骤中处理不可信输入（问题标题、PR 正文、分支名、提交信息）
* Actions 的 OIDC/云认证，或 CI 中的密钥处理
* 公开仓库上的自托管运行器
* 任何类似“这个工作流安全吗？”、“保护我的 CI”或“审查这个 GitHub Action”的请求

## 核心洞察

在工作流中，**`${{ <expr> }}` 会在运行器中扩展到脚本 *在 shell 执行它之前*。** 因此，像这样的步骤：

```yaml
- run: echo "标题: ${{ github.event.issue.title }}"
```

并不是传递一个变量——它将攻击者控制的文本直接粘贴到你的 shell 命令中。一个标题为 `"; <攻击者命令> #` 的问题会被连接到脚本并执行。这是最常见的实际 Actions 漏洞，模型通常会生成它。将任何包含外部贡献者可以影响的数据的 `${{ }}` 视为代码注入点。

## 执行工作流

对每个审查的工作流，按顺序遵循以下步骤。

### 第 1 步 — 映射触发器和信任级别

阅读每个 `on:` 触发器，并分类工作流的权限：

* `push`、`pull_request`（来自同一仓库）→ 以贡献者自己的信任运行
* 来自 **分支** 的 `pull_request` → 使用 **只读** 令牌，**无密钥**（设计上安全）
* `pull_request_target`、`workflow_run`、`issue_comment`、`issues` → 在基本仓库的上下文中运行，使用 **读写令牌并完全访问密钥**，但可以被 **外部贡献者触发**。这些是危险的触发器。

阅读 `references/triggers-and-privilege.md` 获取完整的信任矩阵。

### 第 2 步 — 搜索脚本注入

对每个 `run:` 块、`actions/github-script` 中的每个 `script:` 以及自定义操作的每个输入，列出 `${{ }}` 表达式并检查是否解析为攻击者可控制的数据。高风险上下文包括：

* `github.event.issue.title`、`github.event.issue.body`
* `github.event.pull_request.title`、`github.event.pull_request.body`、`.head.ref`、`.head.label`
* `github.event.comment.body`、`github.event.review.body`
* `github.event.pages.*.page_name`、`github.event.commits.*.message`、`github.event.head_commit.*`
* `github.head_ref` 和任何 `github.event.*` 字段分支作者可以设置

阅读 `references/injection.md` 获取完整的注入点列表和安全的模式修复。

### 第 3 步 — 检查特权触发器是否执行不可信代码

如果 `pull_request_target` 或 `workflow_run` 工作流检出 PR/分支代码 (`ref: ${{ github.event.pull_request.head.sha }}`) **然后运行它**（构建、测试、安装脚本、`npm install` 带生命周期脚本等），这就是对特权令牌的远程代码执行。将其标记为 **严重**。安全的模式是将它们分成两个工作流：一个无特权的 `pull_request` 工作流运行不可信代码，一个特权 `workflow_run` 工作流只消费其结果。

### 第 4 步 — 审计 `permissions:`

* 如果没有 `permissions:` 块，工作流会继承仓库默认设置，这可能允许读写所有内容。标记它。
* 建议使用顶层 `permissions: {}`（拒绝所有）或 `contents: read`，然后按每个作业授予最小权限（例如仅在评论作业上授予 `pull-requests: write`）。
* 标记任何 `permissions: write-all` 或宽泛的 `write` 权限范围，这些步骤实际上并不需要。

阅读 `references/permissions-and-tokens.md` 获取每个作用域的指导方针和 OIDC 设置。

### 第 5 步 — 审计 Action 引用（供应链）

对每个 `uses:`：

* **第三方 Action**（不是 `actions/*` 或 `github/*`）**必须** 固定到完整的 40 个字符的提交 SHA，而不是标签或分支。标签和分支是可变的；一个被攻陷的上游 Action 可以将 `v1` 重写为恶意代码，并使用你的令牌和密钥运行。
* 本地 `actions/*` 风险较低，但 SHA 固定仍然是强化的建议。
* 标记 `@main`、`@master` 或任何分支引用为 **高**——那就是“最新”并且可以随时在你不知情的情况下更改。
* 在尾随注释中注明人类可读版本：`uses: foo/bar@<sha> # v2.1.0`。

阅读 `references/supply-chain.md` 获取固定、Actions 的 Dependabot 以及工件/缓存风险。

### 第 6 步 — 检查密钥和输出处理

* 不回显、打印或写入日志中的密钥；步骤中不使用 `set -x` / `bash -x` 处理密钥。
* 密钥不能传递给运行不可信代码的步骤或不可信的第三方 Action。
* 写入 `$GITHUB_ENV` 或 `$GITHUB_OUTPUT` 的不可信的多行数据可以注入环境变量或步骤输出——使用随机分隔符 heredoc 形式，并永远不要写入原始用户输入。
* `actions/checkout` 默认在磁盘上留下一个令牌；当作业稍后运行不可信代码时，设置 `persist-credentials: false`。

### 第 7 步 — 生成报告

使用 `references/report-format.md` 中的格式输出发现：首先是一个严重性摘要表，然后是按问题类型分组的结果，包括文件、确切的违规 YAML、平实的风险描述和具体的修复前/后示例。永远不要自动应用更改——将它们提交审查。

## 严重性指南

| 严重性 | 含义 | 示例 |
| --- | --- | --- |
| 🔴 严重 | 令牌/密钥盗窃或外部贡献者可触发的 RCE | `pull_request_target` 检出并运行分支代码；`${{ github.event.* }}` 在特权触发器的 `run:` 中 |
| 🟠 高 | 可利用的供应链或作用域问题 | 第三方 Action 在可变标签/分支上；`write-all` 权限；注入点在 `issue_comment` |
| 🟡 中 | 条件或链式风险 | 缺少 `permissions:` 块；非分支 PR 作者可访问密钥 |
| 🔵 低 | 强化差距，低直接风险 | 本地 Action 未 SHA 固定；非特权作业上 `persist-credentials` 默认 |
| ⚪ 信息 | 观察，不是漏洞 | 固定 SHA 旁边缺少版本注释 |

## 输出规则

* **始终** 首先显示一个发现摘要表（按严重性计数）。
* **按问题类型分组**，而不是按文件。
* **必须精确**——引用违规行并给出行位置。
* **始终** 将每个 **严重/高** 与具体的修复 YAML 示例配对。
* **永远** 不要因为分支 `pull_request` 运行不可信代码就将其标记为危险——它没有密钥且使用只读令牌。将 **严重** 保留给特权触发器。
* 如果工作流已经强化，请说明并列出检查了哪些内容。

## 参考文件

按需加载：

* `references/triggers-and-privilege.md` — 每个触发器的信任矩阵，为什么 `pull_request_target` 和 `workflow_run` 是特权，以及两个工作流的安全模式。
  + 搜索模式：`pull_request_target`、`workflow_run`、`issue_comment`、`fork`、`密钥`、`只读令牌`、`信任边界`
* `references/injection.md` — 攻击者可控制的 `${{ }}` 上下文完整列表和每个注入点的 `env:` 变量安全模式 (`run`、`github-script`、Action 输入)。
  + 搜索模式：`脚本注入`、`github.event`、`head_ref`、`问题标题`、`env`、`中间变量`、`actions/github-script`
* `references/permissions-and-tokens.md` — `GITHUB_TOKEN` 作用域、按作业类型的最小权限 `permissions:` 配方，以及云认证的 OIDC 而不是长生命周期的密钥。
  + 搜索模式：`permissions`、`GITHUB_TOKEN`、`write-all`、`contents: read`、`id-token`、`OIDC`、`最小权限`
* `references/supply-chain.md` — 固定第三方 Action、`github-actions` 的 Dependabot、跨 `workflow_run` 的工件和缓存中毒，以及自托管运行器暴露。
  + 搜索模式：`SHA 固定`、`uses`、`可变标签`、`Dependabot`、`下载工件`、`缓存`、`自托管运行器`
* `references/report-format.md` — 输出模板：摘要表、发现卡片和修复前/后块。
  + 搜索模式：`报告`、`格式`、`发现`、`摘要`、`修复`、`前`、`后`
