# 内存泄漏调试

这项技能提供了专家指导和工作流程，用于使用 Chrome DevTools MCP 工具在 JavaScript 和 Node.js 应用程序中查找、诊断和修复内存泄漏。

## 前置条件

高级内存调试工具（`compare_heapsnapshots`、`get_heapsnapshot_details` 等）仅在服务器使用 `--memoryDebugging` 标志启动时才可用。首先检查这些工具是否可用；如果不可用，尝试读取 MCP 配置文件以检查 `--memoryDebugging` 是否已启用。

## 核心原则

- **优先使用 MCP 内存工具**：不要尝试直接读取原始 `.heapsnapshot` 文件，因为它们体积极大，将消耗过多 token。使用 Chrome DevTools MCP 堆快照工具对快照进行汇总、比较和检查。
- **隔离泄漏**：确定泄漏是在浏览器（客户端）还是 Node.js（服务器端）。
- **常见元凶**：查找分离的 DOM 节点、未处理的闭包、全局变量、未移除的事件监听器以及无界增长的缓存。_注意：分离的 DOM 节点有时是故意使用的缓存；在将它们置为 null 之前，务必询问用户。_
- **关闭已加载的快照**：堆快照可能很大。在完成调查后，使用 `close_heapsnapshot` 对每个已加载的快照进行关闭，以释放 MCP 服务器持有的内存。

## 工作流程

### 1. 捕获快照

在调查前端 Web 应用程序内存泄漏时，利用 `chrome-devtools-mcp` 工具与应用程序交互并捕获快照。

- 使用 `click`、`navigate_page`、`fill` 等页面范围工具（指定 `pageId`）将页面操作到所需状态。
- 交互后还原页面到原始状态，以查看内存是否被释放。
- 重复相同的用户交互 10 次以放大泄漏。
- 使用 `take_heapsnapshot`（带 `pageId`）将 `.heapsnapshot` 文件保存到磁盘，包括基线、目标（操作后）和最终（还原操作后）状态。

### 2. 比较快照

使用 `take_heapsnapshot` 生成 `.heapsnapshot` 文件后，使用 Chrome DevTools MCP 内存工具进行比较。

- 使用 `get_heapsnapshot_summary` 对每个快照进行启动，以确认文件是否加载并比较高级总计。
- 使用 `compare_heapsnapshots` 比较基线和目标快照。先不带 `classIndex` 进行摘要差异，然后通过指定 `classIndex` 仅请求可疑增长的详细类差异。
- 在深入特定节点 ID 之前，使用 `compare_heapsnapshots` 的摘要输出。

### 3. 检查保留链和支配链

当类或对象类型意外增长时，在更改代码之前使用 MCP 工具检查保留链和支配链。

- 使用 `get_heapsnapshot_class_nodes` 列出可疑类的实例。
- 使用 `get_heapsnapshot_retainers`、`get_heapsnapshot_retaining_paths`、`get_heapsnapshot_dominators` 和 `get_heapsnapshot_edges` 了解代表性节点为何仍然可达。
- 使用 `get_heapsnapshot_object_details` 并指定 `nodeId` 以检索详细对象元数据（大小、类型、距离和 DOM 分离状态）。
- 使用 `get_heapsnapshot_duplicate_strings` 当字符串增长主导差异时。
- 在保留路径指向应用程序代码后，阅读 [references/common-leaks.md](references/common-leaks.md) 了解常见内存泄漏的示例和修复方法。

### 4. 高级分析和分类过滤器

使用内置的 MCP 内存工具和过滤器直接定位特定泄漏类别，而无需外部工具。

- 使用 `get_heapsnapshot_details` 或 `get_heapsnapshot_class_nodes` 并带 `filterName` 以针对常见泄漏原因：
  - `objectsRetainedByDetachedDomNodes`：识别内存中保留的分离 DOM 元素。
  - `objectsRetainedByEventHandlers`：识别由未移除的事件监听器保留的对象。
  - `objectsRetainedByContexts`：识别被困在闭包或执行上下文中的对象。
  - `objectsRetainedByConsole`：识别由控制台日志保留的对象。
