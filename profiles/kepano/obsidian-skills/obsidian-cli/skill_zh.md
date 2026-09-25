# Obsidian CLI

使用 `obsidian` CLI 与正在运行的 Obsidian 实例进行交互。需要 Obsidian 处于打开状态。

## 命令参考

运行 `obsidian help` 可查看所有可用命令。该命令始终保持最新。完整文档：https://help.obsidian.md/cli

## 语法

**参数** 需以 `=` 后跟值的形式提供。包含空格的值请用引号括起来：

```bash
obsidian create name="My Note" content="Hello world"
```

**标志** 是无值的布尔开关：

```bash
obsidian create name="My Note" silent overwrite
```

对于多行内容，使用 `\n` 表示换行，使用 `\t` 表示制表符。

## 文件定位

许多命令接受 `file` 或 `path` 来定位文件。若未提供 `file` 或 `path`，则使用当前活动文件。

- `file=<name>` — 按 wikilink 的方式解析（仅名称，无需路径或扩展名）
- `path=<path>` — 从库根目录出发的精确路径，例如 `folder/note.md`

## 库定位

命令默认定位最近聚焦的库。使用 `vault=<name>` 作为第一个参数以定位特定库：

```bash
obsidian vault="My Vault" search query="test"
```

## 常见模式

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

在任何命令中使用 `--copy` 可将输出复制到剪贴板。使用 `silent` 可防止文件打开。在列表命令中使用 `total` 可获取计数。

## 插件开发

### 开发/测试周期

在修改插件或主题的代码后，请遵循以下工作流程：

1. **重载** 插件以应用更改：
   ```bash
   obsidian plugin:reload id=my-plugin
   ```
2. **检查错误** — 若出现错误，请修复后从第 1 步重新开始：
   ```bash
   obsidian dev:errors
   ```
3. **通过截图或 DOM 检查进行视觉验证**：
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **检查控制台输出**，查看是否有警告或意外日志：
   ```bash
   obsidian dev:console level=error
   ```

### 其他开发者命令

在应用上下文中运行 JavaScript：

```bash
obsidian eval code="app.vault.getFiles().length"
```

检查 CSS 值：

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

切换移动端模拟：

```bash
obsidian dev:mobile on
```

运行 `obsidian help` 可查看包括 CDP 和调试器控制的额外开发者命令。
