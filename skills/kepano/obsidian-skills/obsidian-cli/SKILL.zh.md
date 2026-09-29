---
name: obsidian-cli
description: 使用 Obsidian CLI 与 Obsidian 数据库交互，以读取、创建、搜索和管理笔记、任务、属性等。同时支持插件和主题开发，可通过命令重新加载插件、运行 JavaScript、捕获错误、截屏以及检查 DOM。当用户需要与 Obsidian 数据库交互、管理笔记、搜索数据库内容、从命令行执行数据库操作，或开发与调试 Obsidian 插件和主题时使用。
---

# Obsidian 命令行界面

使用 `obsidian` 命令行界面与正在运行的 Obsidian 实例进行交互。需要先打开 Obsidian。

## 命令参考

运行 `obsidian help` 查看所有可用命令。这是始终最新的。完整文档：https://help.obsidian.md/cli

## 语法

**参数** 使用 `=` 指定值。对包含空格的值进行引号括起来：

```bash
obsidian create name="My Note" content="Hello world"
```

**标志** 是无值的布尔开关：

```bash
obsidian create name="My Note" silent overwrite
```

对于多行内容，使用 `\n` 表示换行，使用 `\t` 表示制表符。

## 文件定位

许多命令接受 `file` 或 `path` 来定位文件。如果没有指定，则使用当前活动文件。

- `file=<name>` — 类似于维基链接解析（仅名称，无需路径或扩展名）
- `path=<path>` — 从仓库根目录开始的精确路径，例如 `folder/note.md`

## 仓库定位

命令默认定位最近聚焦的仓库。将 `vault=<name>` 作为第一个参数来定位特定仓库：

```bash
obsidian vault="My Vault" search query="test"
```

## 常用模式

```bash
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello" template="Template" silent
obsidian append file="My Note" content="New line"
obsidian search query="search term" limit=10
obsidian daily:read
obsidian daily:append content="- [ ] New task"
obsidian property:set name="status" value="done" file="My Note"
obsidian tasks daily todo
obsidian tags sort=count counts
obsidian backlinks file="My Note"
```

在任何命令中使用 `--copy` 将输出复制到剪贴板。使用 `silent` 防止文件打开。在列表命令中使用 `total` 获取计数。

## 插件开发

### 开发/测试循环

对插件或主题进行代码更改后，请遵循以下工作流程：

1. **重新加载** 插件以应用更改：
   ```bash
   obsidian plugin:reload id=my-plugin
   ```
2. **检查错误** — 如果出现错误，请修复并重复步骤 1：
   ```bash
   obsidian dev:errors
   ```
3. **通过截图或 DOM 检查进行可视化验证**：
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **检查控制台输出** 以查找警告或意外日志：
   ```bash
   obsidian dev:console level=error
   ```

### 额外开发者命令

在应用上下文中运行 JavaScript：

```bash
obsidian eval code="app.vault.getFiles().length"
```

检查 CSS 值：

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

切换移动模拟：

```bash
obsidian dev:mobile on
```

运行 `obsidian help` 查看额外的开发者命令，包括 CDP 和调试器控制。
