marimo 是一个用于构建可重复的 Python 程序（marimo 笔记本）的响应式 Python 运行时。单元格通过它们定义和引用的变量相互连接。运行一个单元格会以数据流顺序重新执行依赖项。活动运行时持有内核命名空间、单元格状态和数据流图。在会话运行期间，内核从该状态写入笔记本（`.py` 文件）。

用户通过带有单元格、输出和控件的笔记本 UI 与相同的运行时交互。

**警告。活动运行时是事实依据。** 在会话期间，您**不应**直接修改关联的 `.py` 文件。文件编辑**不会**到达活动内核或用户，内核在保存时可能会覆盖它们。使用 `marimo._code_mode` (`cm`) 进行笔记本更改。读取磁盘是允许的，但最好使用 `ctx.cells[...].code` 获取当前单元格代码。

Harness 报告此 `SKILL.md` 的绝对路径。从其父目录解析捆绑的 `scripts/...` 和 `reference/...` 路径，即使当前工作目录是笔记本工作区也是如此。在命令示例中，将 `/absolute/path/to/marimo-pair` 替换为该目录。

## 必须首先执行的内核命令

开始每个代码模式会话时，使用此专用命令：

```bash
bash /absolute/path/to/marimo-pair/scripts/execute-code.sh \
  --url http://localhost:2718 \
  -c "import marimo._code_mode as cm; help(cm)"
```

对于每个内核（包括只读任务），请按以下顺序执行：

1. 运行一次检查命令。
2. 等待成功的 `help(cm)` 输出。
3. 然后在后续调用中使用 `cm.get_context()` 或另一个 `cm` API。

在检查命令成功之前，**不要**运行特定于任务的 `cm` 代码。

## 连接到笔记本

使用从报告的技能目录或 MCP（`execute_code(...)`）提供的捆绑 `execute-code.sh` 在活动的 marimo 内核中运行 Python。

`execute-code.sh` 总是接受 `--url`。如果用户提供一个笔记本 URL，则直接对其运行所需的检查：

```bash
bash /absolute/path/to/marimo-pair/scripts/execute-code.sh \
  --url http://localhost:2718 \
  -c "import marimo._code_mode as cm; help(cm)"
```

该命令成功后，使用 `-c CODE`、`-` 表示 stdin 或文件路径传递任务代码：

```bash
bash /absolute/path/to/marimo-pair/scripts/execute-code.sh \
  --url http://localhost:2718 - <<'PY'
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    cid = ctx.create_cell("x = df.head()")
    ctx.run_cell(cid)
PY
```

如果用户未提供 URL，则查找或启动笔记本。使用 `bash /absolute/path/to/marimo-pair/scripts/discover-servers.sh`、MCP `list_sessions()` 或本地进程上下文查找正在运行的服务器，并将它报告的 `url` 传递给 `--url`。打开一个笔记本时，脚本会自动针对它；有多个时，使用 `--file` 并传递笔记本的文件键。

如果没有运行服务器并且用户想要笔记本，则使用 `--no-token`（并且不使用 `--headless`）启动 marimo 以自动注册以供发现。笔记本 UI 必须打开才能让 `execute-code` 针对它。正确的调用取决于上下文（项目工具、全局安装、沙盒模式）。如果笔记本文件包含 PEP 723 `#
/// script` 头部，则必须使用 `--sandbox` 打开它——否则 marimo 会忽略内联依赖项。有关完整决策树，请参阅 [finding-marimo.md](reference/finding-marimo.md)，有关选择器解析、脚本、MCP 和 shell 引用的信息，请参阅 [execution-context.md](reference/execution-context.md)。

## 临时区域范围

`execute-code` 在 marimo 的临时区域中评估 Python：一个具有内核全局变量浅拷贝的临时命名空间。笔记本变量可以通过名称访问，但新的顶层绑定和重新绑定在每次调用后都会被丢弃。对笔记本拥有的对象的就地修改可以持久化，因为这些名称仍然引用活动对象。

每次调用都会报告来自临时区域的 stdout 和 stderr，以及它触发的笔记本单元格的 console 输出，包括反应性后代。

### 普通Python

在临时区域中使用普通 Python 来检查变量、采样数据、测试转换、探测 API、检查导入和读取控件状态。

```python
print(df.head())

x = 10
print(x)
```

在这里，`df` 来自笔记本全局变量，而 `x` 是临时区域局部绑定。`x` 仅在此调用中存在，**不会**被添加到笔记本全局变量。

### 使用 `cm` 持久化

顶层临时区域分配和重新绑定是临时的。要持久化工作，包括新变量，您**必须**通过 `marimo._code_mode` (`cm`) 提交更改。

`marimo._code_mode` 是一个私有的、不稳定的代理 API（注意前面的下划线）。它用于像此技能这样的工具从临时区域驱动活动内核。**不要**从笔记本单元格、库代码或用户会运行的任何内容中导入它——方法可能会在 marimo 版本和内核之间更改或消失。将每个 `import marimo._code_mode as cm` 视为仅限临时区域。

打开代码模式上下文以排队笔记本更改。

```python
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    cid = ctx.create_cell("x = df.head()")
    ctx.run_cell(cid)
```

临时区域支持顶层异步代码。直接使用 `async with`；将其包装在 `asyncio.run(...)` 中是不必要的，并且可能与内核的事件循环冲突。

在此代码块退出并且新单元格运行后，`x` 是笔记本状态。后续临时区域调用可以通过名称读取 `x`。在同一临时区域调用中后续的代码应读取 `ctx.globals["x"]`，因为单元格运行之前临时区域命名空间已被复制。

在上下文中，排队突变方法是无阻塞的。直接调用它们；不要 `await` 它们。每次调用都会排队一个操作，以便 marimo 在上下文正常退出时应用。如果代码块引发异常，队列将被丢弃。

在干净退出时，marimo 会应用包、验证并应用结构性单元格更改、运行排队单元格，然后可能运行依赖项。验证仅限于结构，因为排队单元格运行仍可能出错。`create_cell` 和 `edit_cell` 仅更改笔记本结构。使用 `run_cell` 执行。

`create_cell` 目前默认为 `hide_code=True`，这将折叠 UI 中的代码编辑器。如果用户希望创建的单元格在无需手动展开的情况下可见，请传递 `hide_code=False`。

## Marimo 规则

marimo 对笔记本代码施加一个小合同，以便它可以将笔记本保持为有向无环图（DAG）：

- **无循环** - 单元格不能相互循环依赖。
- **跨单元格无公共重新定义** - 每个名称有一个所有者单元格。
- **无通配符导入** - `import *` 阻止对定义进行静态分析。

这些规则使内核、UI 和保存的工件保持一致。

当 `cm` 提交单元格主体时，marimo 会解析其顶层定义和引用。公共名称进入图。以 `_` 开头的名称是其单元格的局部名称，其他单元格无法访问。如果 `cm` 编辑违反了合同，marimo 会拒绝结构性更改并返回验证错误。

## 笔记本的形状

笔记本是有序单元格的集合。`ctx.cells` 是文档视图，`ctx.graph` 是数据流视图。

```python
for cell in ctx.cells:
    cell  # .id, .code, .name, .config, .status, .errors

ctx.cells["setup"]         # 通过名称
ctx.cells[0]               # 通过位置
list(ctx.cells.keys())     # 所有 ID，按笔记本顺序
```

单元格 ID 是不透明的字符串，可以从笔记本查询或从 `cm` 返回值捕获：

```python
cid = ctx.create_cell("df = pd.read_csv('data.csv')")
print(cid)   # 例如 'Hbol'
```

或者，单元格可以通过名称分配和引用。可以使用图来了解其在数据流中的作用。

```python
for cid, impl in ctx.graph.cells.items():
    impl  # .defs, .refs   (公共名称的集合)

ctx.graph.descendants(cid)   # 当此单元格更改时重新运行的单元格
ctx.graph.ancestors(cid)     # 此单元格依赖的单元格
```

在 marimo 中，删除是**破坏性**的，因此在使用之前查询后代以了解其影响可能很有用。

## 编写笔记本更改

图合同使 marimo 能够运行和保存笔记本。仅通过传递这些检查并不能保证有用的工件。提交的单元格仍然应该是可读的、可重新运行的、可编辑的。

进行持久化更改，重用笔记本现有的名称、导入、依赖项和 UI 模型。不要懒惰。避免一次性解决方案，这些解决方案通过 `cm` 验证但留下脆弱的笔记本。

### 单元格主体

提交属于单元格的代码。

- **提交单元格内容** - `create_cell` 和 `edit_cell` 接收单元格内容，而不是保存文件的 `@app.cell` 包装器。
- **替换之前读取** - 目前，另一个编辑器可能在使用临时区域调用之间更改单元格。在 `edit_cell` 之前，从 `ctx.cells[...]` 读取当前主体，并提交完整的替换。
- **重用笔记本导入** - 如果 `np` 已经存在，使用它或编辑拥有导入的单元格。**不要**仅为了绕过图而添加 `import numpy as _np`。
- **每个公共名称只定义一次** - 公共名称有一个所有者单元格。在另一个单元格中重新分配它将失败，并显示 `Multiply-defined names`；编辑拥有单元格或给结果一个新名称。有关详细信息，请参阅 [gotchas.md](reference/gotchas.md)。
- **有意运行单元格** - `create_cell` 和 `edit_cell` 仅更改结构。当单元格应执行时，排队 `ctx.run_cell(...)`。

### 单元格边界

单元格也是一个重新运行边界。将昂贵或可重用的计算放在呈现的上游，以便 UI 编辑保持廉价。将廉价的、特定于呈现的工作与视图一起保留，当这样做更容易阅读时。

仅在组合是 UI 的一部分时使用 `mo.vstack` 和 `mo.hstack`。叙事通常在相邻的 markdown 单元格中阅读得更好。

### 优先使用 `cm` 管理的更改

当它们存在时，使用 `cm` API。避免直接文件编辑、shell 包命令和仅限临时区域的状
