使用此技能帮助用户通过 `skills` CLI 与开放的 Agent Skills 生态系统进行交互。

## 概述

`skills` CLI 是可安装 Agent Skills 的包管理器。使用它来发现技能、使用正确的标志进行安装，并在安装后进行管理。

下方的示例使用 `bunx skills`，但如果用户的环境中不可用 Bun，则 `npx skills` 是相同的流程。

始终优先使用当前的 CLI 语法：

```bash
bunx skills add <source> --skill <name>
```

不要使用旧的 `owner/repo@skill-name` 示例。

## 何时使用

当用户：

- 询问“为 X 找一个技能”、“有没有 X 的技能”或“我该如何做 X”，并且 X 听起来像是一个可重用的工作流时
- 询问“你能做 X”并且 X 听起来像是一个可能已经作为技能存在的专业功能时
- 需要帮助 `bunx skills`、`npx skills`、`skills.sh`、技能包安装或 `skills-lock.json`
- 想要为特定代理（如 Codex 或 OpenCode）安装技能
- 想要列出、检查、更新、删除、恢复、同步、备份或初始化已安装的技能
- 想要帮助搜索工作流、工具、模板或特定领域的功能（如设计、测试、部署、文档或代码审查）

不要在用户已经有一个本地技能并希望帮助编写或改进其内容时使用此技能。在这种情况下，请使用技能编写工作流。

## 发现工作流

当用户需要一个技能时，请按照以下顺序操作：

1. 确定领域和任务。
   示例：React 性能、PR 审查、变更日志生成、PDF 提取。
   同时判断任务是否足够常见，以至于可能存在可重用的技能。
2. 首先检查 [skills.sh](https://skills.sh/)。
   当领域已经覆盖在那里时，优先选择知名且已安装的技能。
3. 如果排行榜没有明确回答需求，使用以下方式搜索：

```bash
bunx skills find <query>
```

1. 在推荐任何东西之前验证质量：
   - 安装数量：优先选择安装量超过 1K 的技能，并对安装量少于 100 的技能保持谨慎
   - 来源声誉：优先选择官方或已建立的维护者，如 `openai`、`anthropics`、`microsoft` 或类似受信任的发布者
   - 仓库质量：检查源仓库，并对少于 100 个星标的仓库持怀疑态度
2. 清晰地呈现选项。
   包括技能名称、它有助于什么、安装数量和来源、为什么看起来值得信赖、安装命令，以及 `skills.sh` 上的更多信息链接。
3. 如果用户想继续，提供安装帮助。
4. 如果没有合适的，直接说明，使用您的通用功能帮助完成任务，并提及用户可以使用 `bunx skills init` 创建自己的包。

## 安装快速参考

### 常见来源

```bash
# GitHub 简写
bunx skills add xixu-me/skills

# 完整 GitHub URL
bunx skills add https://github.com/xixu-me/skills

# 仓库内一个技能的直接路径
bunx skills add https://github.com/xixu-me/skills/tree/main/skills/skills-cli

# GitLab URL
bunx skills add https://gitlab.com/org/repo

# 任何 git URL
bunx skills add git@github.com:owner/repo.git

# 本地包路径
bunx skills add ./my-local-skills
```

### 常见安装模式

```bash
# 列出包中的技能而不安装
bunx skills add <source> --list

# 安装一个技能
bunx skills add <source> --skill skills-cli

# 安装多个技能
bunx skills add <source> --skill pr-review --skill commit

# 全局安装
bunx skills add <source> --skill skills-cli -g -y

# 安装到特定代理
bunx skills add <source> --skill skills-cli -a codex -y

# 安装所有技能到所有代理
bunx skills add <source> --all

# 安装所有技能到一个代理
bunx skills add <source> --skill '*' -a codex -y

# 复制文件而不是创建符号链接
bunx skills add <source> --skill skills-cli -a codex --copy -y
```

### 安装方法

当用户选择如何安装时：

- 符号链接是默认的，通常是最佳选择，因为更新保持集中
- `--copy` 创建独立的副本，并在符号链接不受支持或不方便时作为备用方案

如果用户只要求安装一个技能，除非他们提到 CI 打包、可移植性、文件系统限制或明确要求副本，否则优先选择默认的符号链接工作流。

### 重要标志

| 标志                  | 使用                                            |
| --------------------- | ---------------------------------------------- |
| `--skill <name>`      | 安装一个或多个命名的技能                       |
| `-a, --agent <agent>` | 针对特定代理，如 `codex`                      |
| `-g, --global`        | 在用户范围内而不是项目范围内安装               |
| `-y, --yes`           | 跳过提示                                       |
| `--list`              | 列出包中可用的技能                           |
| `--copy`              | 复制而不是符号链接                             |
| `--all`               | 所有技能到所有代理的缩写                     |

## 管理已安装的技能

使用这些命令进行持续维护：

```bash
# 列出已安装的技能
bunx skills ls
bunx skills ls -g
bunx skills ls -a codex
bunx skills ls --json

# 检查更新
bunx skills check

# 更新已安装的技能
bunx skills update

# 删除已安装的技能
bunx skills remove my-skill
bunx skills remove my-skill -a codex
bunx skills remove -g my-skill
bunx skills remove --all

# 初始化一个新的技能包
bunx skills init
bunx skills init my-skill

# 从 skills-lock.json 恢复
bunx skills experimental_install

# 将 node_modules 中的技能同步到代理目录
bunx skills experimental_sync
bunx skills experimental_sync -a codex -y
```

当用户要求初始化一个技能时，解释他们是否想要：

- `bunx skills init` 在当前目录创建 `SKILL.md`
- `bunx skills init <name>` 创建一个包含 `SKILL.md` 的新子目录

## 相关工具：Skills Vault

如果用户希望跨机器或团队对已安装的技能进行声明式备份和恢复，请使用 [Skills Vault](https://github.com/xixu-me/skills-vault)。

Skills Vault 是 `skills` 生态系统的独立 CLI 伴侣。它不是 `skills add` 可安装的技能来源。当用户希望将已安装的技能快照到清单中、预览恢复命令或在其他地方重现相同设置时使用它。

常见的伴侣命令：

```bash
# 将已安装的技能备份到 skvlt.yaml
bunx skvlt backup

# 预览恢复
bunx skvlt restore --dry-run

# 从清单中恢复所有内容
bunx skvlt restore --all

# 诊断本地环境
bunx skvlt doctor
```

当用户明确需要可移植清单工作流、跨机器备份和恢复或团队共享已安装的技能设置时，优先使用此工具而不是 `skills experimental_*`。

## 推荐格式

当推荐一个技能时，保持答案具体且可安装。

使用类似这样的结构：

```text
我找到一个应该适合的技能。

技能： <skill-name>
匹配原因： <一句话>
来源： <owner/repo 或 URL>
质量检查： <安装数量 / 来源声誉 / 仓库信心备注>
安装：
bunx skills add <source> --skill <skill-name> [可选标志]
了解更多： https://skills.sh/<publisher>/<package>/<skill-name>

如果您需要，我可以为您安装它 <agent-or-scope>。
```

如果用户提到目标代理或范围，请在命令中包含它。示例：

```bash
bunx skills add <source> --skill <skill-name> -a codex -y
bunx skills add <source> --skill <skill-name> -g -y
```

示例：

```text
我找到一个可能有助于的技能。

技能： screenshot
匹配原因：它专注于操作系统级的桌面和窗口截图捕获。
来源： openai/skills
质量检查：高安装量、值得信赖的发布者，以及广泛使用的源仓库。
安装：
bunx skills add openai/skills --skill screenshot
了解更多： https://skills.sh/openai/skills/screenshot
```

## 常见技能类别

当用户的措辞模糊时，将其映射到可能的类别：

| 类别        | 示例查询                                    |
| --------------- | -------------------------------------------------- |
| Web 开发      | `react`, `nextjs`, `typescript`, `css`, `tailwind` |
| 测试         | `testing`, `jest`, `playwright`, `e2e`             |
| DevOps          | `deploy`, `docker`, `kubernetes`, `ci-cd`          |
| 文档         | `docs`, `readme`, `changelog`, `api-docs`          |
| 代码质量    | `review`, `lint`, `refactor`, `best-practices`     |
| 设计          | `ui`, `ux`, `design-system`, `accessibility`       |
| 生产力    | `workflow`, `automation`, `git`                    |

## 搜索技巧

- 使用具体的关键词。`react testing` 比 `testing` 更好。
- 尝试替代术语。如果 `deploy` 失败，尝试 `deployment` 或 `ci-cd`。
- 首先检查流行来源。许多强大的技能来自已建立的发布者。
- 如果第一次搜索过于宽泛，通过领域加任务进行缩小。

## 常见错误

- 从搜索结果中推荐一个技能，而未检查它是否看起来已建立。
- 忘记在用户要求特定代理时指定 `-a <agent>`。
- 将 `bunx skills find --help` 当作真正的帮助命令。使用 `bunx skills --help` 获取命令帮助。
- 在一个弱搜索术语后假设没有技能存在。首先尝试更具体或相邻的查询。

## 故障排除

如果用户遇到错误或令人困惑的结果：

- "未找到技能" - 建议更好的查询，检查 [skills.sh](https://skills.sh/)，或直接帮助并提及 `bunx skills init`
- 自动化或 CI 中的交互式提示 - 添加 `-y`
- 错误的安装范围 - 在项目安装和 `-g` 之间切换
- 符号链接问题 - 重试使用 `--copy`
- 对可用包内容的疑问 - 运行 `bunx skills add <source> --list`
- 对安装状态的疑问 - 运行 `bunx skills ls` 或 `bunx skills ls --json`
- 跨机器的可移植备份或恢复 - 提及 [Skills Vault](https://github.com/xixu-me/skills-vault) 及其 `backup` / `restore --dry-run` 工作流

当您不确定确切标志时，使用：

```bash
bunx skills --help
```
