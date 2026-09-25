# graphify — 代码导航层

代码库的结构索引。在您使用grep之前，了解存在什么、在哪里以及它们如何连接。

**需要CLI：** `npm i -g graphify-ts`（使用Bun运行时）。

**仅限手动更新。** 图表不会自动刷新——当您需要最新索引时，您（或用户）运行`graphify update`或`graphify build`。这避免了git工作树和其他多会话设置中的写入冲突。

## 首次设置（每台机器一次性）

```bash
npm i -g graphify-ts    # 安装CLI
```

然后，每个项目一次：

```bash
graphify build .
```

之后，当索引与代码漂移时手动刷新（见下文的`graphify update`）。

## 命令

### `/graphify build` — 构建索引（首次或完全重建）

```bash
graphify build .
```

扫描所有源文件，提取AST结构，保存到`graphify-out/graph.json`。

报告："索引了{files}个文件，{nodes}个符号，{edges}个关系"

### `/graphify query <name>` — 搜索符号

```bash
graphify query graphify-out/graph.json <name>
```

不区分大小写的搜索。返回匹配的符号及其文件位置。

### `/graphify update <files...>` — 编辑后的增量更新

```bash
graphify update graphify-out/graph.json <file1> [file2...]
```

仅重新提取指定的文件。如果您计划在同一会话中再次查询图表，编辑代码后运行此命令。

### `/graphify auto-update` — 从git diff批量更新

```bash
graphify auto-update [dir]
```

通过`git diff`+未跟踪文件计算已更改的代码文件，然后调用`updateIndex`。当无操作时保持静默。方便在批量编辑后刷新，无需命名每个文件。

## 使用场景

**在搜索代码之前：** 如果存在`graphify-out/graph.json`，在Glob或Grep之前查询它。图表告诉您哪些文件包含哪些符号。这是主要价值——用结构化查找替换盲目的关键字搜索。

**编辑后：** 如果您将在同一会话中再次查询图表，运行`graphify update <编辑过的文件>`（或`graphify auto-update`进行批量刷新）。否则保留它——下一个`graphify build`或更新将补上。

**探索不熟悉的代码：** 运行`/graphify query <概念>`查找入口点，而无需猜测文件名。

## 支持的语言

Python、JavaScript、TypeScript（JSX/TSX）、Go、Rust、Java、C、C++、Ruby、C#、Kotlin、Scala、PHP

## 图表输出

保存为`graphify-out/graph.json`：

```json
{
  "nodes": [{ "id": "main::app", "label": "App", "sourceFile": "main.py", "sourceLocation": "main.py:5" }],
  "edges": [{ "source": "file::main", "target": "main::app", "relation": "contains", "confidence": "EXTRACTED" }],
  "metadata": { "files": 10, "nodes": 45, "edges": 62 }
}
```

边关系：`contains`、`method`、`imports`、`imports_from`、`calls`（INFERRED）、`inherits`
