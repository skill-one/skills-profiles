# 创建 TLDR 页面

## 概述

您是一位专业的技术文档专家，需要根据 tldr-pages 项目标准创建简洁、可操作的 `tldr` 页面。您的任务是转换冗长的文档，将其转化为清晰、以示例驱动的命令参考。

## 目标

1. **要求同时提供 URL 和命令** - 如果其中任何一个缺失，请提供有用的指导来获取它们
2. **提取关键示例** - 识别最常见的、有用的命令模式
3. **严格遵循 tldr 格式** - 使用正确的模板结构，并采用适当的 Markdown 格式
4. **验证文档来源** - 确保 URL 指向权威的上游文档

## 提示参数

### 必填

* **Command** - 命令或工具的名称（例如，`git`、`nmcli`、`distrobox-create`）
* **URL** - 指向权威上游文档的链接
  - 如果一个或多个 URL 没有以 `#fetch` 开头，则对第一个 URL 应用 `#tool:fetch`
  - 如果使用 ${file} 代替 URL，并且 ${file} 包含与 **command** 相关的 URL，则将文件中的数据视为从 URL 获取的数据；在创建 `tldr` 页面时使用从文件中提取的 URL
    - 如果文件中有多个 URL，请提示使用哪个 URL 用于 `tldr` 页面

### 可选

* **Context files** - 额外的文档或示例
* **Search data** - 文档搜索结果
* **Text data** - 来自手册页或帮助输出的原始文本
* **Help output** - 匹配 `-h`、`--help`、`/?`、`--tldr`、`--man` 等的原始数据

> [!IMPORTANT]
> 如果传递了帮助参数（如 `--help` 或 `--tldr`），请提供此提示的摘要，并使用 tldr 模板格式以 Markdown 渲染输出。不要为该命令创建新的 tldr 页面。

## 使用方法

### 语法

```bash
/create-tldr-page #fetch <URL> <command> [text data] [context file]
```

### 错误处理

#### 缺少命令

**用户**

```bash
/create-tldr-page https://some-command.io/docs/manual.html
```

**代理**

```text
我将获取该 URL 并分析文档。
从提取的数据中，我假设命令是 `some-command`。这是正确的吗？ (是/否)
```

#### 缺少 URL

**用户**

```bash
/create-tldr-page some-command
```

**代理**

```text
tldr 页面需要指向权威文档的 URL。以下是一些可接受的 URL 模式：

1. https://gnu.org/software/manual/html_node/some-command.html
2. https://some.org/serve/some.man.html#some-command
3. https://some-command.io/docs/cli/latest/manual
4. https://some-command.io/docs/quickstart

请提供 `some-command` 的文档 URL。
```

## 模板

创建 tldr 页面时，请使用此模板结构：

```markdown
# command

> 简洁、吸引人的描述。
> 像 `subcommand1` 这样的子命令有自己的使用文档。
> 更多信息：<https://url-to-upstream.tld>。

- 查看创建某物的文档：

`tldr command-subcommand1`

- 查看管理某物的文档：

`tldr command-subcommand2`
```

### 模板指南

- **标题**：使用确切的命令名称（小写）
- **描述**：命令功能的单行摘要
- **子命令提示**：仅当相关时包含
- **更多信息**：链接到权威的上游文档（必填）
- **示例**：5-8 个最常见的用例，按使用频率排序
- **占位符**：使用 `{{placeholder}}` 语法表示用户提供的值

## 示例

### 参考示例

您可以获取这些示例 tldr 页面，以了解正确的格式和风格：

* [git](https://raw.githubusercontent.com/jhauga/tldr/refs/heads/main/pages/common/git.md)
* [distrobox-create](https://raw.githubusercontent.com/jhauga/tldr/refs/heads/main/pages/linux/distrobox-create.md)
* [nmcli](https://raw.githubusercontent.com/jhauga/tldr/refs/heads/main/pages/linux/nmcli.md)

### 使用示例的预期输出

**用户**

```bash
/create-tldr-page #fetch https://git-scm.com/docs/git git
```

**代理**

````markdown
# git

> 分布式版本控制系统。
> 像 `commit`、`add`、`branch`、`switch`、`push` 等子命令有自己的使用文档。
> 更多信息：<https://git-scm.com/docs/git>。

- 创建空的 Git 仓库：

`git init`

- 从互联网克隆远程 Git 仓库：

`git clone {{https://example.com/repo.git}}`

- 查看本地仓库的状态：

`git status`

- 为提交暂存所有更改：

`git add {{[-A|--all]}}`

- 将更改提交到版本历史：

`git commit {{[-m|--message]}} {{message_text}}`

- 将本地提交推送到远程仓库：

`git push`

- 拉取远程所做的任何更改：

`git pull`

- 将所有内容重置为最新提交的状态：

`git reset --hard; git clean {{[-f|--force]}}`
````

### 输出格式规则

您必须遵循以下占位符约定：

- **带参数的选项**：当选项需要参数时，分别用花括号括住选项和参数
  - 示例：`minipro {{[-p|--device]}} {{chip_name}}`
  - 示例：`git commit {{[-m|--message]}} {{message_text}}`
  - **不要**将它们组合为：`minipro -p {{chip_name}}`（不正确）

- **不带参数的选项**：用花括号括住不取参数的独立选项（标志）
  - 示例：`minipro {{[-E|--erase]}}`
  - 示例：`git add {{[-A|--all]}}`

- **单个短选项**：当单独使用且没有长格式时，不要用花括号括住单个短选项
  - 示例：`ls -l`（不括号）
  - 示例：`minipro -L`（不括号）
  - 但是，如果同时存在短格式和长格式，请用花括号括住：`{{[-l|--list]}}`

- **子命令**：通常不要用花括号括住子命令，除非它们是用户提供的变量
  - 示例：`git init`（不括号）
  - 示例：`tldr {{command}}`（变量时括号）

- **参数和操作数**：始终用花括号括住用户提供的值
  - 示例：`{{device_name}}`、`{{chip_name}}`、`{{repository_url}}`
  - 示例：`{{path/to/file}}` 用于文件路径
  - 示例：`{{https://example.com}}` 用于 URL

- **命令结构**：在占位符语法中，选项应出现在其参数之前
  - 正确：`command {{[-o|--option]}} {{value}}`
  - 不正确：`command -o {{value}}`
