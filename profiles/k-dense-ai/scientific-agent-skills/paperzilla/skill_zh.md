# Paperzilla

当您想与您的代理讨论项目、推荐和 Paperzilla 中的规范论文时，请使用此技能。

## 您可以询问什么

- "给我项目 X 的最新推荐。"
- "打开推荐 Y 并解释它为什么重要。"
- "以 Markdown 格式获取规范论文 Z 并进行总结。"
- "告诉我这篇论文与我的研究的相关性。"
- "显示项目 X 的信息流。"
- "对推荐进行反馈。"
- "将这篇论文、推荐或信息流导出为 JSON。"

这是 Paperzilla 的核心技能。它为您的代理直接访问 Paperzilla 数据提供了途径，但它不会强制执行工作流程或外部交付集成。

## 访问方法

此存储库中的大多数当前配置文件使用 `pz` 命令行界面 (CLI)。

如果当前配置文件提供额外的特定于代理的说明，请遵循这些说明。

## 安装

### macOS
```bash
brew install paperzilla-ai/tap/pz
```

### Windows (Scoop)
```bash
scoop bucket add paperzilla-ai https://github.com/paperzilla-ai/scoop-bucket
scoop install pz
```

### Linux
使用官方的 Linux 安装指南：

- https://docs.paperzilla.ai/guides/cli-getting-started

### 从源代码构建 (Go 1.23+)
查看 CLI 存储库以获取源代码构建：

- https://github.com/paperzilla-ai/pz

## 更新

检查您的 CLI 是否是最新的，并获取特定于安装的升级步骤：

```bash
pz update
```

如果检测结果不明确，请显式覆盖它：

```bash
pz update --install-method homebrew
pz update --install-method scoop
pz update --install-method release
pz update --install-method source
```

支持 `auto`、`homebrew`、`scoop`、`release` 和 `source` 等值。

## 认证

```bash
pz login
```

## CLI 参考

如果当前配置文件使用 `pz`，这些是核心命令。

### 列出项目
```bash
pz project list
```

### 显示一个项目
```bash
pz project <project-id>
```

### 浏览项目信息流
```bash
pz feed <project-id>
```

有用的标志：

- `--must-read`
- `--since YYYY-MM-DD`
- `--limit N`
- `--json`
- `--atom`

示例：

```bash
pz feed <project-id> --must-read --since 2026-03-01 --limit 5
pz feed <project-id> --json
pz feed <project-id> --atom
```

信息流输出可以包括现有的推荐反馈标记：

- `[↑]` 点赞
- `[↓]` 点踩
- `[★]` 星标

### 阅读规范论文
```bash
pz paper <paper-id>
pz paper <paper-id> --json
pz paper <paper-id> --markdown
pz paper <paper-id> --project <project-id>
```

### 打开您项目中的一个推荐
```bash
pz rec <project-paper-id>
pz rec <project-paper-id> --json
pz rec <project-paper-id> --markdown
```

### 对推荐进行反馈
```bash
pz feedback <project-paper-id> upvote
pz feedback <project-paper-id> star
pz feedback <project-paper-id> downvote --reason not_relevant
pz feedback clear <project-paper-id>
```

## 输出和自动化

- 优先使用 `--json` 进行机器解析。
- `pz paper --markdown` 仅在 Markdown 已经准备好的情况下返回 Markdown。
- `pz rec --markdown` 可以排队生成 Markdown，并在生成过程中打印友好的重试消息。
- `--atom` 返回用于信息流阅读器的个人信息流 URL。

## 配置

```bash
export PZ_API_URL="https://paperzilla.ai"
```

## 参考文献

- 文档：https://docs.paperzilla.ai/guides/cli
- 快速入门：https://docs.paperzilla.ai/guides/cli-getting-started
- 存储库：https://github.com/paperzilla-ai/pz
