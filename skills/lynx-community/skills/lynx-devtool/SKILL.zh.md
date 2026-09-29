---
name: lynx-devtool
description: 在处理Lynx DevTool或调试Lynx应用、页面或设备时使用，尤其是在任务中提到客户端或会话、CDP或App命令、DOM/CSS检查、运行时或控制台日志、在设备上评估JavaScript、截图、堆快照、性能跟踪、Page.reload或App.openPage、全局开关、交互式快照引用和点击/填充/滚动、检查或搜索ReactLynx组件树、将DOM快照引用链接到ReactLynx组件（`reactlynx link`），或在Android、iOS或桌面端修改ReactLynx的props/state/context时使用。
---

# Agent Lynx 开发工具技能

此技能允许您使用 `agent-lynx` CLI 与运行在连接设备（Android、iOS、桌面）上的 Lynx 应用进行交互。

## 使用方法

使用 `agent-lynx` CLI。发布的包是 `agent-lynx`。
此包 `@lynx-js/skill-lynx-devtool` 是此技能说明和资源的规范来源。`agent-lynx` 依赖于它，并直接读取它以用于 `skills list/get`。一个兼容性启动器还保持了历史性的单次 `npx -y @lynx-js/skill-lynx-devtool` 调用的可用性。

程序化 API 从 `agent-lynx/connector` 导出。此入口重新导出 `@lynx-js/devtool-connector`、`@lynx-js/devtool-connector/transport` 和 `@lynx-js/devtool-connector/streams` 中的所有内容，并提供仅适用于守护进程的 `createDefaultTransports()` 和 `createDefaultConnector()` 辅助函数。辅助函数使用一个 `DaemonTransport`，以便独立脚本共享守护进程拥有的设备连接。仅在故意测试非守护进程路径时，才使用显式传输构造 `Connector`。

在线 CLI 命令遵循相同的仅适用于守护进程的默认设置。`--no-daemon` 是一个显式的逃生通道，它用直接 Android、iOS、OpenHarmony 和桌面传输替换该调用的守护进程。内置的无头运行时仍然是仅适用于守护进程的。`ADB_SERVER_HOST` 和 `ADB_SERVER_PORT` 仅配置此直接模式。守护进程模式忽略它们，并附带一个 stderr 警告。

`agent-lynx` CLI 通常在 `PATH` 上可用。如果 `command -v agent-lynx` 失败，请使用 `npx`：

```bash
npx --yes agent-lynx <command>
```

此发布的技能不附带本地 CLI 入口脚本。使用：

```bash
agent-lynx <command>
```

**注意**：大多数命令输出都是 JSON。您可以使用 `jq` 或 Node.js 处理数据。

### 发现内置技能

安装的 `@lynx-js/skill-lynx-devtool` 依赖项提供了 `lynx-devtool` 技能。使用以下方式发现它或加载其完整说明：

```bash
agent-lynx skills list
agent-lynx skills get lynx-devtool
```

`skills list` 直接从该包的 `SKILL.md` YAML 前置部分读取每个名称和描述。`skills get` 返回选定的 Markdown 正文，并在存在时递归列出 `references/`、`assets/` 和 `examples/` 下的常规文件。符号链接和构建输出不包含在内。稳定名称是 `lynx-devtool`。

### 快照工作流

```bash
agent-lynx snapshot
agent-lynx tap @e3 --snapshot
agent-lynx fill @e1 "Alice"
agent-lynx clear @e1
agent-lynx scroll @e2 --direction down
agent-lynx get text @e3
agent-lynx get style @e3 --property color,width
agent-lynx wait --text Ready
agent-lynx screenshot --annotate -o page.jpeg
```

快照引用存在于守护进程内存中，跨 CLI 调用。不要将 `--no-daemon` 传递给 `snapshot`、`tap`、`long-press`、`fill`、`clear`、`scroll`、`get text`、`get style`、`wait` 或 `screenshot`。`wait` 使用守护进程的 SSE 命令路由；其他快照命令使用 `POST /command/<action>`。

`screenshot --annotate` 刷新并缓存快照引用，然后将编号标签直接绘制到一个 JPEG 中。标签 `[N]` 映射到引用 `@eN`，因此代理可以检查图像并立即使用匹配的引用。图像标记了可见引用的稀疏可操作子集：直接操作目标、可编辑字段、显式测试目标和滚动容器。通用布局和文本引用在缓存的快照中可用，而不会使图像杂乱。视口大小的滚动容器使用角落徽章而不是全帧边框。使用 `--json`，结果还携带了此相同 ActionCore 调用使用的完整新鲜快照，因此消费者可以在不发出第二次刷新的情况下比较图像和引用。像素映射使用屏幕录制帧的逻辑大小元数据，而不是可能内嵌的快照视口；当此元数据不可用时，命令会失败而不是猜测。不要将 `--annotate` 与 `--fullscreen` 结合使用；相反，请使用未注释的 `screenshot --fullscreen` 或遗留的 `take-screenshot --fullscreen` 命令。有关详细信息，请参阅 [带注释的屏幕截图参考](references/screenshot-annotate.md)。

程序化连接器导入需要项目依赖项：

```bash
npm install agent-lynx
```

此项目本地安装仅适用于连接器工作流，而不是通过 `PATH` 或 `npx` 上的 `agent-lynx` CLI 的 CLI 仅使用。

### 作为库使用

如果您想直接从 JavaScript 驱动 Lynx DevTool 而不是调用 CLI，请从 `agent-lynx/connector` 导入。

```js
import { Connector, createDefaultConnector } from "agent-lynx/connector";

const connector = createDefaultConnector();
const clients = await connector.listClients();

console.log(clients);
```

对于更完整的程序化工作流，请参阅 [库使用参考](references/library-usage.md) 和 [程序化调试示例](examples/programmatic-debugging.md)。

如果您故意需要自定义、非守护进程传输，也可以手动构造连接器：

```js
import {
  AndroidTransport,
  Connector,
  DesktopTransport,
  iOSTransport,
} from "agent-lynx/connector";

const connector = new Connector([
  new AndroidTransport({ host: "127.0.0.1", port: 5037 }),
  new DesktopTransport(),
  new iOSTransport(),
]);
```

### 全局选项

- `-h, --help`：显示命令的帮助信息。
- `--no-daemon`：绕过共享守护进程并在此调用中使用直接设备传输。如果守护进程可能拥有与相同 DebugRouter 目标连接，请首先停止守护进程。

**注意**：每个子命令都支持 `--help` 标志（例如 `agent-lynx cdp --help`）。使用此标志查看可用参数及其描述的完整列表。

### 命令

#### 1. 列出客户端

列出所有可用的 Lynx 客户端（启用 DevTool 的应用）。

```bash
agent-lynx list-clients
```

#### 2. 等待客户端

等待客户端可用。

```bash
agent-lynx wait-for-client --client-name com.lynx.uiapp
```

- `--client-name <name>`：可选的包/应用名称以等待。匹配 `AppProcessName`、`bundleId`、`bundleName` 或 `App`。如果多个客户端匹配，则返回所有匹配的客户端。如果省略，则返回第一个非无头客户端。输出始终是 JSON 数组。
- `--timeout <seconds>`：最大秒数。默认为 `30`。
- `--interval <seconds>`：发现尝试之间的秒数。默认为 `1`。

#### 3. 列出会话

列出所有活动的调试会话。会话对应于特定的 Lynx 视图或上下文。

```bash
agent-lynx list-sessions
# 可选：按客户端 ID 过滤
agent-lynx list-sessions --client <clientId>
```

#### 4. 发送 CDP 命令

向特定会话发送 Chrome DevTools Protocol (CDP) 命令。

> 注意：Lynx 仅支持标准 CDP 命令的一部分。
> LynxView 注意：当目标会话是 LynxView 时，发送 CDP 命令之前，您**必须**阅读 [支持的 CDP 方法](references/cdp/index.md)。
> WebView 注意：当目标会话是 WebView（例如 `type: "web"` 或 HTTP/HTTPS URL）时，请使用标准 Chrome DevTools Protocol 文档中的 CDP 方法名称、参数和启用先决条件。本地 `references/cdp` 页面侧重于 LynxView 支持和 Lynx 特定扩展，这些扩展在 WebView 目标上可能返回 `method not found`。

```bash
agent-lynx cdp -m <method> [options] [params]
```

- `-m, --method <method>`：CDP 方法名称（例如 `DOM.getDocument`、`Page.reload`）。
- `-c, --client <clientId>`：可选的客户端 ID。如果省略，则使用第一个可用客户端。
- `-s, --session <sessionId>`：可选的会话 ID。如果省略，则使用最新会话（具有最大的会话 ID）。
- `--thread <thread>`：可选的虚拟机线程，`background` 或 `main`。默认为 `background`。
- `[params]`：可选的命令参数的 JSON 字符串。

当使用 `--thread main` 时，仅支持 `Debugger.*`、`Runtime.*`、`HeapProfiler.*` 和 `Profiler.*` 方法。

示例：

```bash
# 获取文档根
agent-lynx cdp -m DOM.getDocument
```

#### 5. 计算表达式

计算一个 JavaScript 表达式。在后台虚拟机中，当前应用的 `lynx` 和 `nativeLynx` 对象作为本地变量可用。针对主虚拟机的表达式保持不变。

```bash
agent-lynx evaluate 'JSON.stringify(lynx.__globalProps)'
agent-lynx evaluate '2 + 2' --thread main
agent-lynx evaluate 'lynx' --no-return-by-value
```

- `<expression>`：要计算的 JavaScript 表达式。
- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--thread <thread>`：可选的虚拟机线程，`background` 或 `main`。默认为 `background`。只有后台表达式被包装以暴露 `lynx` 和 `nativeLynx`；主线程表达式保持不变。
- 默认情况下，命令按值请求结果。支持 `returnByValue` 的引擎将普通 JSON 类似对象序列化为 `result.value`；当前的 Android Lynx 运行时可能忽略对象值并仍然返回 `objectId`。当需要 JSON 输出时，请使用 `JSON.stringify(lynx.__globalProps)`。使用 `--no-return-by-value` 故意接收 `objectId`，以便稍后使用 `Runtime.getProperties` 或 `Runtime.callFunctionOn` 请求。`--return-by-value` 仍然接受作为默认值的显式形式。
- `--silent`、`--context-id`、`--throw-on-side-effect`、`--generate-preview`、`--object-group`、`--await-promise`、`--include-command-line-api`：可选的计算参数。引擎支持各不相同。

#### 6. 发送应用命令

发送应用级别的命令。

```bash
agent-lynx app -m <method> [options] [params]
```

- `-m, --method <method>`：应用方法名称（例如 `App.openPage`）。
- `-c, --client <clientId>`：可选的客户端 ID。
- `[params]`：可选的参数的 JSON 字符串。

> 您**必须**在发送应用命令之前阅读 [支持的应用方法](references/app/index.md)。

#### 7. 打开 URL

在 Lynx 应用中打开特定 URL。

```bash
agent-lynx open <url> [options]
```

- `<url>`：要打开的 URL。
- `-c, --client <clientId>`：可选的客户端 ID。

示例：

```bash
agent-lynx open "lynx://example/page"
```

#### 8. 获取控制台

从设备捕获控制台日志。

```bash
agent-lynx get-console [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--offset <number>`：跳过 N 条消息。
- `--limit <number>`：限制消息数量。
- `--include-stack-traces`：为非错误消息包含堆栈跟踪。
- `--level <levels>`：过滤日志级别（例如 `error,warning`）。
- `--thread <thread...>`：目标虚拟机线程：`background` 或 `main`。如果省略，则默认收集两个线程。

#### 9. 获取源

列出所有解析的脚本。这对于查找与其他命令（例如 `Debugger.getScriptSource`）一起使用的脚本 ID 很有用。该命令自动获取当前加载的所有脚本。

```bash
agent-lynx get-sources [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。

#### 10. 检查

打印由连接器守护进程为客户端/会话对服务的 DevTool 检查器 URL。在浏览器中打开打印的 URL，以将图形检查器附加到 CLI 目标相同的会话。

```bash
agent-lynx inspect [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--port <port>`：可选的守护进程端口。默认为 `21783`。

#### 11. 代理屏幕截图

通过 ActionCore 捕获，可选择将新鲜快照引用直接绘制到生成的 JPEG 中。

```bash
agent-lynx screenshot [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--annotate`：可选的刷新引用并绘制 `[N]` 标签，其中 `[N]` 映射到 `@eN`。
- `--fullscreen`：可选的捕获全屏而不是 LynxView。不能与 `--annotate` 结合使用。
- `-o, --output <path>`：可选的 JPEG 输出路径。
- `--json`：可选的返回路径、图像尺寸、完整新鲜快照和注释元数据。

此命令需要持久的守护进程。有关其单图像输出契约和目标限制，请参阅 [带注释的屏幕截图参考](references/screenshot-annotate.md)。

#### 12. 遗留的屏幕截图

使用预 Agent-Lynx 命令对当前页面进行直接屏幕截图。

```bash
agent-lynx take-screenshot [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--fullscreen`：可选的以全屏模式捕获屏幕截图。如果未提供，则默认为 `lynxview` 模式。
- `-o, --output <path>`：可选的输出文件路径。

#### 13. 捕获内容屏幕截图

捕获与 CSS 选择器匹配的第一个节点的完整可滚动内容。

```bash
agent-lynx take-content-screenshot --selector <selector> [options]
```

- `--selector <selector>`：CSS 选择器，用于 `scroll-view` 或兼容的 `list`。必需。
- `--format <jpeg|png>`：可选的图像格式。默认为 `jpeg`。
- `--scale <number>`：可选的正输出比例。默认为 `1`。
- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `-o, --output <path>`：可选的输出文件路径。

`takeContentScreenshot` 官方定义为 `scroll-view`。该命令接受任何 CSS 选择器，因此可以在 `list` 上暴露相同方法的运行时也可以使用；不支持的节点返回 UI 方法失败。

有关行为和示例，请参阅 [捕获内容屏幕截图参考](references/take-content-screenshot.md)。

#### 14. 全局开关

管理 DevTool 全局开关。

```bash
# 列出所有支持的键及其当前值
agent-lynx global-switch list [options]

# 获取一个键
agent-lynx global-switch get --key <globalKey> [options]

# 设置一个键
agent-lynx global-switch set --key <globalKey> --status <on|off> [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。

`global-switch list` 选项：

- `--fail-fast`：在第一个键读取失败时中止。

`global-switch get` 选项：

- `--key <globalKey>`：全局开关键。 （必需）

`global-switch set` 选项：

- `--key <globalKey>`：全局开关键。 （必需）
- `--status <on|off>`：目标开关状态。 （必需）

有关完整键列表和示例，请参阅 [全局开关参考](references/global-switch.md)。

#### 15. 捕获堆快照

从当前 Lynx 会话捕获 QuickJS 堆快照，并将其保存为 `.heapsnapshot` 文件。

```bash
agent-lynx take-heap-snapshot [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--thread <thread>`：可选的虚拟机线程，`background` 或 `main`。默认为 `background`。
- `-o, --output <path>`：可选的输出文件路径。默认为操作系统临时目录。

#### 16. 查询全局内存使用

通过全局 `Memory.*` CDP 域查询 Lynx 全局内存使用情况。使用通用 `cdp` 命令，并将请求发送到具有会话 ID `-1` 的全局 DevTool 处理程序。

```bash
# 获取跨所有活动实例的全局 Lynx 内存使用情况
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage '{"timeoutMs":50000}'
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：CDP 会话 ID。除非您有平台特定的原因要覆盖它，否则请使用 `-1` 以用于全局 DevTool 处理程序。
- `params.timeoutMs`（可选）：毫秒的非负超时。最大值是 `300000`。

该命令打印原始 `Memory.getAllMemoryUsage` JSON。不要期望 CLI 输出包含派生的 `summary`、`topMemoryItems` 或 `topInstances` 包装字段。

当 DevTool MCP 服务器可用时，请优先使用 `Memory_getAllMemoryUsage` MCP 工具以相同的原始有效负载，而不是调用 CLI。

代理端报告标准：

1. 当用户请求捕获或结果过大无法内联显示时，将完整的原始 JSON 保存到文件中。
2. 使用二进制单位（`KiB`、`MiB`、`GiB`），保留两位小数。将 `ratioToApp` 和贡献率以百分比形式显示，保留两位小数。
3. 首先报告此固定摘要：
   - `collectionStatus`
   - `${completedInstanceCount}/${expectedInstanceCount}` 个 Lynx 实例
   - `totalBytes`
   - `appBytes`
   - `ratioToApp`
   - `elementNodeCount`
   - `viewBytes`
   - `mainThreadRuntimeBytes`
   - `backgroundThreadRuntimeBytes`
4. 然后报告 "Top 5 内存贡献者"，使用每个 `instances[]` 条目中的细粒度候选项：
   - `instances[i].backgroundThreadRuntimeBytes`
   - `instances[i].mainThreadRuntimeBytes`
   - `instances[i].elementBytes`
   - 每个 `instances[i].viewDetail[category].sizeBytes`
   - 如果 `instances[i].viewBytes` 大于 `viewDetail[*].sizeBytes` 的总和，则包含一个 `other view memory` 项用于剩余部分。
5. 按字节降序对 Top 5 贡献者进行排序。对于每一行，包括排名、项目类型/类别、大小、`% of totalBytes`、`% of instance.totalBytes`、`instanceId` 和 URL。
6. 然后报告按 `instance.totalBytes` 降序排列的 "实例"。对于每个实例，包括 `instanceId`、URL、`totalBytes`、`mainThreadRuntimeBytes`、`backgroundThreadRuntimeBytes`、`viewBytes`、`elementBytes` 和紧凑的 `viewDetail` 摘要，例如 `image=12 / 4.15 MiB`。
7. 不要编造缺失的字段。如果 `viewDetail` 为空或某个类别有 `0` 字节，请明确说明。当前的 CDP 负载没有暴露嵌套的子 LynxView 对象树。

`Memory.getAllMemoryUsage` 与 `Runtime.getHeapUsage` 不同：它返回跨所有活动注册的 Lynx 实例的全局 Lynx 归属内存快照，包括元素、视图、主线程运行时、后台运行时、应用程序足迹和每个实例的细分。当前的 CDP 负载没有暴露单独的嵌套子 LynxView 内存树；`viewDetail` 是按 UI 视图类别或标签聚合的。有关完整响应形状，请参阅 [Memory CDP 方法](references/cdp/memory/index.md)。

#### 17. 录制

通过 TestBench（基于 CDP）录制 Lynx 页面交互。捕获所有操作（模板加载、触摸事件、JS 模块调用、数据更新），并生成 JSON 回放文件。

```bash
# 开始录制（在打开目标页面之前）
agent-lynx recorder start [options]

# 停止录制并保存回放文件
agent-lynx recorder end [options]
```

- `-c, --client <clientId>`：可选的 `start` 和 `end` 的客户端 ID。
- `-o, --output <path>`：可选的 `end` 的输出文件或目录路径。默认为 `~/.lynx-devtool/files/lynxrecorder/recording-<clientId>-<timestamp>.json`。

工作流程：

1. 运行 `recorder start`。如果它启用 `enable_debug_mode`，请重新启动应用程序并再次运行 `recorder start`。
2. 用户打开并交互 Lynx 页面。
3. 运行 `recorder end --output <file.json>` 停止并保存。
4. 向用户报告绝对文件路径。

**重要提示**：要生成可回放的文件，在 `recorder start` 后打开或重新加载目标页面，以便录制包括 `loadTemplate`。

有关更多详细信息，请参阅 [录制参考](references/recorder.md)。

#### 18. 性能跟踪录制

录制压缩的 Lynx 性能跟踪，并保存为 `.pftrace` 文件。在构建或打开目标页面之前开始跟踪，以便捕获其第一帧。

```bash
# 首先发现客户端；在整个工作流程中保持相同的 ID。
agent-lynx list-clients

# 在打开目标页面之前开始。
agent-lynx trace start --client <clientId>

# 打开并交互页面，然后停止并捕获流句柄。
agent-lynx trace end --client <clientId>

# 下载 `trace end` 返回的句柄。
agent-lynx trace read-data --client <clientId> --stream <handle> -o ./my-trace.pftrace

# 在没有设备或守护进程的情况下本地检查下载的文件。
agent-lynx trace event-summary ./my-trace.pftrace
agent-lynx trace query ./my-trace.pftrace \
  --sql "SELECT name, COUNT(*) AS count FROM slice GROUP BY name"
```

- `-c, --client <clientId>`：可选的客户端 ID。如果多个客户端已连接，请列出它们并显式选择一个。
- `trace start --no-systrace`：禁用 systrace；默认情况下启用。
- `trace start --include-categories <categories>` / `--exclude-categories <categories>`：包含或排除逗号分隔的跟踪类别。
- `trace start --enable-memory-trace`：启用内存数据收集。
- `trace start --no-force-gc`：禁用自动垃圾回收，默认情况下启用。
- `trace start --enable-auto-heap-snapshot`：为 `shared-group` VMs 捕获自动堆快照。添加 `--shared-group-id <id>` 以选择一个 VM。
- `trace start --js-profile-interval <interval>`：JS 采样间隔。在启用分析时，如果提供的间隔为 `0` 或 `-1`，则默认为 `100`；否则默认为 `-1`。
- `trace start --js-profile-type <quickjs|v8>`：为选定的 JS 运行时启用分析。如果省略此选项，则禁用分析。
- `trace end --timeout <seconds>`：等待 `Tracing.tracingComplete` 的时间（秒）。默认为 `30`。
- `trace read-data --stream <handle>`：由 `trace end` 返回的数字流句柄。
- `trace read-data -o, --output <path>`：输出路径。默认为操作系统临时目录中的时间戳 `.pftrace`。
- `trace read-data --timeout <seconds>`：总下载超时。默认为 `30`。
- `trace event-summary <trace>`：按计数降序打印每个 Perfetto `slice.name` 及其出现次数。添加 `--json` 以获取结构化证据，并使用 `-o, --output <path>` 将其写入文件。
- `trace query <trace> --sql <query>`：运行内联 Perfetto SQL 并输出 JSON。
- `trace query <trace> --sql-file <path>`：从文件运行 SQL。使用 `--sql` 和 `--sql-file` 中的确切一个；`--max-rows` 默认为 `1000`。

`trace query` 和 `trace event-summary` 是本地离线命令。它们不会连接到设备、启动守护进程或创建连接器传输。它们的 JSON 包括跟踪的绝对路径、字节长度和 SHA-256，以便代理可以证明它检查了哪个文件。SQL `bigint` 值是十进制字符串，blob 是 `{ "base64": "..." }` 对象。

在 Android 上，第一个 `trace start` 可能启用 `enable_debug_mode` 并要求重新启动应用程序。重新启动应用程序并在打开页面之前再次运行 `trace start`。没有跟踪支持的运行时需要 Android local_test 构建 或 iOS Lynx Profile 构建。有关完整工作流程和故障排除，请参阅 [性能跟踪参考](references/trace.md)。

#### 19. ReactLynx 组件树

打印正在运行的 ReactLynx 页面的组件树，从 `@lynx-js/preact-devtools` 解码。CLI 调用连接器守护进程的 ReactLynx ActionCore；守护进程拥有 `Lynx.onVMEvent` 流、`init`+`refresh` 握手、`operation_v2` 解码和每个会话的组件缓存。CLI 仅渲染返回的树。

```bash
agent-lynx reactlynx tree [options]
```

- `-c, --client <clientId>`：可选的客户端 ID。
- `-s, --session <sessionId>`：可选的会话 ID。
- `--depth <n>`：可选的最大树深度。默认：无限制。
- `--show-shells`：包含 ReactLynx 插入的合成 `Fragment` / `Root` / `Anonymous` 包装器。默认情况下隐藏它们。
- `--json`：输出 `{ labels, roots, nodes }` 而不是 ASCII；当脚本将消费树时使用此选项。

输出使用 `@cN [type] Name` 引用（来自 `agent-react-devtools` 的约定）。标签是按可见根的先序深度优先搜索。`reactlynx tree` 总是捕获一个新鲜生成并缓存它发出的确切标签视图，包括 `--depth`；后续的 `component @cN` 和 `update-* @cN` 调用会在独立的 CLI 调用之间重用该视图。紧凑的 `--show-shells` 标签视图分别缓存。

```
@c1 [fn] App
├─ @c2 [fn] Header
│  └─ @c3 [fn] Logo
└─ @c4 [fn] Body
```

要求：

- ReactLynx 命令需要连接器守护进程；不要将它们与 `--no-daemon` 结合使用。
- 页面必须是 **开发构建** 并运行 `@lynx-js/preact-devtools`（生产捆绑包会移除 `setupReactLynx()`）。成功初始化会在设备控制台日志中记录 `[PREACT DEVTOOLS] Devtools initialized successfully`。
- `@lynx-js/preact-devtools` 必须包含 `document.body` 和 `preactDevtoolsCtx.Node` 修复（针对 `lynx-family/preact-devtools` 的 PR #2 + PR #5）。没有它们，`refresh` 通道将返回零个 `operation_v2` 帧，CLI 将打印 "stale preact-devtools" 诊断。

当树为空时，CLI 退出并带有代码 `1`，并在标准错误输出中写入三个目标诊断之一：

- **`saw 0 frames`**：`PreactDevtools` 通道上没有响应。应用程序很可能缺少 `@lynx-js/preact-devtools`，是生产构建，尚未完成 `setupReactLynx()`，或者您选择了错误的 `--session`。
- **`saw N frames but no operation_v2`**：钩子已加载，但其 `refresh` 处理程序有错误。将 `@lynx-js/preact-devtools` 升级到包含 PRs #2 和 #5 的构建。
- **`tree is empty`**：在提交之间卸载了每个节点——罕见，使用 `DEBUG`（下方）重新运行以查看原始信封。

对于深度调试，设置 `DEBUG=devtool-mcp-server:reactlynx` 以在标准错误输出上记录每个 PreactDevtools 帧的类型和有效载荷大小，同时保持标准输出（树 / JSON）干净：

```bash
DEBUG='devtool-mcp-server:reactlynx' agent-lynx reactlynx tree
# 2026-05-25T... devtool-mcp-server:reactlynx frame 1: type=operation_v2 dataSize=54
# 2026-05-25T... devtool-mcp-server:reactlynx frame 2: type=operation_v2 dataSize=756
# 2026-05-25T... devtool-mcp-server:reactlynx frame 3: type=root-order dataSize=1
# 2026-05-25T... devtool-mcp-server:reactlynx frame 4: type=root-order-page dataSize=object
```

#### 20. ReactLynx 组件检查

通过发送 Preact DevTools `inspect` 信封并读取 `inspect-result` 来检查单个 ReactLynx 组件（props / state / hooks / context / signals）。

```bash
agent-lynx reactlynx component <ref> [options]
```

- `<ref>`：由 `reactlynx tree` / `reactlynx find` 产生的标签 `@cN`，或数字 vnode ID。
  - 使用 `@cN` 时，守护进程将其与最新的匹配标签视图解析。在缓存未命中时，它会捕获一次树。如果标签生成时显示外壳，请传递 `--show-shells`。
  - 使用数字 ID（例如 `3856353762`），则绕过组件缓存。
- `-c, --client <clientId>`，`-s, --session <sessionId>`：标准的目标标志。
- `--show-shells`：在解析 `@cN` 时，像 `reactlynx tree --show-shells` 那样计算合成 Fragment / Root / Anonymous 包装器。
- `--refresh`：在解析 `@cN` 之前捕获一个新的完整树。对数字 ID 无效。
- `--json`：打印原始 `InspectData` 负载作为 JSON。默认输出是紧凑的 ASCII 摘要。

示例输出：

```text
@c5 (id=3856353783) [fn] TUXIntroViewListCell key=1. HMR
  source: src/TUXIntroViewListCell.tsx:42:3
  props:
    {
      "title": "1. HMR",
      "icon": { "type": "vnode", "name": "TUXIcon" }
    }
```

复杂值由上游的 `serialize.ts` 标记——`{ "type": "function", "name": "..." }`、`{ "type": "vnode", "name": "..." }`、`{ "type": "signal", "value": ... }`、`{ "type": "map", "entries": [...] }` 等。有关完整模式，请参阅 [serialize.ts](https://github.com/lynx-family/preact-devtools/blob/main/src/adapter/shared/serialize.ts)。

如果应用程序未能以 `inspect-result` 回复，守护进程将驱逐该会话的 ReactLynx 缓存，CLI 将退出并带有代码 `1`。在重试之前运行 `reactlynx tree`。相同的 `DEBUG=devtool-mcp-server:reactlynx` 命名空间会跟踪每个帧。

#### 21. ReactLynx 组件查找

查找每个名称匹配子字符串或正则表达式的组件。输出与 `reactlynx tree` 相同地排序（先序深度优先搜索），因此 `@cN` 标签与其他子命令可以循环使用。

```bash
agent-lynx reactlynx find <pattern> [options]
```

- `<pattern>`：子字符串（默认，不区分大小写）或带有 `--regex` 的 JavaScript 正则表达式。
- `-c, --client <clientId>`，`-s, --session <sessionId>`：标准的目标标志。
- `--regex`：将 `<pattern>` 视为 JavaScript 正则表达式（例如 `--regex '^Toast(List)?$'`）。
- `--show-shells`：包含合成 Fragment / Root / Anonymous 包装器。
- `--refresh`：在搜索之前捕获一个新的组件生成。如果没有它，`find` 会重用守护进程缓存（并在缓存未命中时捕获一次）。
- `--limit <n>`：最多打印的匹配项数。默认 `50`。
- `--json`：输出 `[{ label, id, name, type, key, ancestors: [{label, name}] }, ...]` 以供脚本后处理。

示例输出：

```text
@c8 [fn] TUXCenterToastActivator
  in @c1 TUXApp > @c2 Provider > @c3 App
@c10 [fn] TUXTopToastActivator
  in @c1 TUXApp > @c2 Provider > @c3 App
```

`reactlynx find` 是在树太大无法可视化扫描时发现标签以进行后续 `reactlynx component @cN` 调用的推荐方法。当找到匹配项时，它会发布其完整深度标签视图作为选定外壳模式的最新视图。

#### 22. ReactLynx 元素/组件链接

解析最新守护进程缓存 DOM 快照与守护进程缓存 ReactLynx 组件树之间的一个确切关系：

```bash
# Snapshot element -> 最近显示的 ReactLynx 组件
agent-lynx snapshot
agent-lynx reactlynx link @e7

# ReactLynx 组件 -> 最新 Snapshot 中的第一个主机元素
agent-lynx reactlynx tree
agent-lynx reactlynx link @c8
```

该命令也接受 `@cN` 的数字 Preact VNode ID，并支持 `--json`、`--show-shells` 和 `--refresh`。默认情况下，它会重用最新的组件生成和选定的外壳模式的确切标签视图；在组件缓存未命中时，它会捕获一次生成。`--refresh` 会显式替换解析关系之前的组件生成。

这是一个通过 Lynx `nodeId` / ReactLynx `uniqueId` 的确切身份查找；它永远不会回退到坐标、文本或树位置匹配。它使用现有的应用程序侧 `element-picked` 和 `highlight` 协议，因此应用程序必须包含兼容的 `@lynx-js/preact-devtools` 开发构建。JSON 返回完整的 Snapshot 引用、组件标签/id/类型/名称/键和组件缓存生成。

该命令故意不刷新 DOM Snapshot：刷新会静默使用户尝试关联的 `@eN` 引用失效。首先运行 `agent-lynx snapshot`，并在守护进程报告缺失或陈旧的引用时显式重新运行它。组件到元素查找返回 Preact DevTools 暴露的第一个主机元素；元素到组件查找返回其最近显示的组件。因此，这些方向对于渲染多个主机元素的组件不保证形成双射。

#### 23. ReactLynx 组件更新

修改一个字段并等待应用程序侧适配器的更新后 `inspect-result` 确认：

```bash
agent-lynx reactlynx update-prop <ref> <path> <value> [options]
agent-lynx reactlynx update-state <ref> <path> <value> [options]
agent-lynx reactlynx update-context <ref> <path> <value> [options]
```

- `<ref>` 遵循与 `reactlynx component` 相同的缓存 `@cN` 或数字 vnode-id 规则。
- `<path>` 从选定的 props/state/context 对象开始，例如 `count`、`user.name` 或 `items.0.title`。不要将其前缀为 `root.`, `props.`, `state.`, 或 `context.`。
- `<value>` 作为 JSON 解析。为外壳引号字符串 JSON，或传递 `--raw` 以将参数作为字符串原封不动地发送。
- `--show-shells` 选择包含外壳的标签视图；`--refresh` 在解析 `@cN` 之前捕获一个新的树。
- `--json` 发出原始更新后 `InspectData` 确认。

守护进程将同一客户端/会话的 ReactLynx 操作序列化，因此广播的 Preact VM 事件不能在并发命令之间相互干扰。不同的会话可以并行进行。缓存是基于版本的，而不是实时订阅：`tree` 和显式的 `--refresh` 会替换它，`find` 默认重用它，而缓存失败的检查/更新会将其移除。
