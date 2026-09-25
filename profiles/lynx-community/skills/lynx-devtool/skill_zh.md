# Agent Lynx DevTool 技能

这项技能允许您使用 `agent-lynx` CLI 与运行在连接设备（Android、iOS、桌面）上的 Lynx 应用进行交互。

## 使用方法

使用 `agent-lynx` CLI。发布的包是 `agent-lynx`。
这个包，`@lynx-js/skill-lynx-devtool`，是这个技能的说明和资源的权威来源。`agent-lynx` 依赖于它，并直接读取它用于 `skills list/get`。一个兼容性启动器也保持历史性的单次 `npx -y @lynx-js/skill-lynx-devtool` 调用正常工作。

程序化 API 从 `agent-lynx/connector` 导出。这个入口重新导出 `@lynx-js/devtool-connector`、`@lynx-js/devtool-connector/transport` 和 `@lynx-js/devtool-connector/streams` 中的所有内容，并提供仅限守护进程的 `createDefaultTransports()` 和 `createDefaultConnector()` 辅助函数。这些辅助函数使用一个 `DaemonTransport`，以便独立脚本共享守护进程拥有的设备连接。仅当有意测试非守护进程路径时，才使用显式传输构造 `Connector`。

在线 CLI 命令遵循相同的仅限守护进程默认值。`--no-daemon` 是一个显式的逃生通道，它用直接 Android、iOS、OpenHarmony 和桌面传输替换该调用的守护进程。内置的无头运行时仍然是仅限守护进程的。`ADB_SERVER_HOST` 和 `ADB_SERVER_PORT` 仅配置这种直接模式。守护进程模式忽略它们，并带有 stderr 警告。

`agent-lynx` CLI 通常在 `PATH` 上可用。如果 `command -v agent-lynx` 失败，请使用 `npx` 代替：

```bash
npx --yes agent-lynx <command>
```

这个发布的技能没有提供本地 CLI 入口脚本。使用：

```bash
agent-lynx <command>
```

**注意**：大多数命令输出都是 JSON。您可以使用 `jq` 或 Node.js 来处理数据。

### 发现内置技能

安装的 `@lynx-js/skill-lynx-devtool` 依赖项提供了 `lynx-devtool` 技能。使用以下方式发现它或加载其完整说明：

```bash
agent-lynx skills list
agent-lynx skills get lynx-devtool
```

`skills list` 直接从该包的 `SKILL.md` YAML 前置部分读取每个名称和描述。`skills get` 返回选定的 Markdown 正文，并在存在 `references/`、`assets/` 和 `examples/` 目录时递归列出常规文件。符号链接和构建输出不包含在内。稳定名称是 `lynx-devtool`。

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

`screenshot --annotate` 刷新并缓存快照引用，然后将编号标签直接绘制到一个 JPEG 中。标签 `[N]` 映射到引用 `@eN`，因此代理可以检查图像并立即使用匹配的引用。图像标记了可见引用的稀疏可操作子集：直接操作目标、可编辑字段、显式测试目标和滚动容器。通用布局和文本引用在缓存的快照中可用，而不会使图像杂乱。视口大小的滚动容器使用角落徽章而不是全帧边框。使用 `--json`，结果还携带了此 ActionCore 调用使用的完整新鲜快照，以便消费者可以在不发出第二次刷新的情况下比较图像和引用。像素映射使用屏幕录制帧的逻辑大小元数据，而不是可能嵌入的快照视口；当此元数据不可用时，命令会失败而不是猜测。不要将 `--annotate` 与 `--fullscreen` 结合使用；相反，请使用未注释的 `screenshot --fullscreen` 或遗留的 `take-screenshot --fullscreen` 命令。有关[注释快照参考](references/screenshot-annotate.md)的详细信息。

程序化连接器导入需要一个项目依赖项：

```bash
npm install agent-lynx
```

这个项目本地安装仅用于连接器工作流，而不是通过 `PATH` 或 `npx` 上的 `agent-lynx` CLI 的 CLI 仅使用。

### 作为库使用

如果您想直接从 JavaScript 驱动 Lynx DevTool 而不是调用 CLI，请从 `agent-lynx/connector` 导入。

```js
import { Connector, createDefaultConnector } from "agent-lynx/connector";

const connector = createDefaultConnector();
const clients = await connector.listClients();

console.log(clients);
```

对于更完整的程序化工作流，请参阅 [库使用参考](references/library-usage.md) 和 [程序化调试示例](examples/programmatic-debugging.md)。

您也可以手动构造连接器，如果您有意需要自定义的非守护进程传输：

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

- `-h, --help`: 显示命令的帮助信息。
- `--no-daemon`: 跳过共享守护进程并使用直接设备传输。如果它可能拥有与相同 DebugRouter 目标连接的连接，请首先停止守护进程。

**注意**：每个子命令都支持 `--help` 标志（例如 `agent-lynx cdp --help`）。使用此标志查看可用参数及其描述的完整列表。

### 命令

#### 1. 列出客户端

列出所有可用的 Lynx 客户端（启用 DevTool 的应用）。

```bash
agent-lynx list-clients
```

#### 2. 等待客户端

直到有客户端可用。

```bash
agent-lynx wait-for-client --client-name com.lynx.uiapp
```

- `--client-name <name>`: 可选的包/应用名称，用于等待。匹配 `AppProcessName`、`bundleId`、`bundleName` 或 `App`。如果有多个客户端匹配，则返回所有匹配的客户端。如果省略，则返回第一个非无头客户端。输出始终是 JSON 数组。
- `--timeout <seconds>`: 最大等待秒数。默认为 `30`。
- `--interval <seconds>`: 发现尝试之间的秒数。默认为 `1`。

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
> LynxView 注意：当目标会话是 LynxView 时，您**必须**在发送 CDP 命令之前阅读 [支持的 CDP 方法](references/cdp/index.md)。
> WebView 注意：当目标会话是 WebView（例如 `type: "web"` 或 HTTP/HTTPS URL）时，请使用标准 Chrome DevTools Protocol 文档中的 CDP 方法名称、参数和启用先决条件。本地 `references/cdp` 页面侧重于 LynxView 支持和 Lynx 特定扩展，这些可能会在 WebView 目标上返回 `method not found`。

```bash
agent-lynx cdp -m <method> [options] [params]
```

- `-m, --method <method>`: CDP 方法名称（例如 `DOM.getDocument`、`Page.reload`）。
- `-c, --client <clientId>`: （可选）客户端 ID。如果省略，则使用第一个可用客户端。
- `-s, --session <sessionId>`: （可选）会话 ID。如果省略，则使用最新会话（具有最大的会话 ID）。
- `--thread <thread>`: （可选）目标 VM 线程，`background` 或 `main`。默认为 `background`。
- `[params]`: （可选）命令的参数 JSON 字符串。

当使用 `--thread main` 时，仅支持 `Debugger.*`、`Runtime.*`、`HeapProfiler.*` 和 `Profiler.*` 方法。

示例：

```bash
# 获取文档根
agent-lynx cdp -m DOM.getDocument
```

#### 5. 计算表达式

计算一个 JavaScript 表达式。在后台 VM 中，当前应用的 `lynx` 和 `nativeLynx` 对象作为本地变量可用。针对主 VM 的表达式将不变地发送。

```bash
agent-lynx evaluate 'JSON.stringify(lynx.__globalProps)'
agent-lynx evaluate '2 + 2' --thread main
agent-lynx evaluate 'lynx' --no-return-by-value
```

- `<expression>`: 要计算的 JavaScript 表达式。
- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--thread <thread>`: （可选）目标 VM 线程，`background` 或 `main`。默认为 `background`。仅后台表达式被包装以暴露 `lynx` 和 `nativeLynx`；主线程表达式不变地发送。
- 命令默认按值请求结果。支持 `returnByValue` 的引擎将普通 JSON-like 对象序列化为 `result.value`；当前 Android Lynx 运行时可能忽略对象值并仍然返回 `objectId`。当需要 JSON 输出时，请使用 `JSON.stringify(lynx.__globalProps)`。使用 `--no-return-by-value` 故意接收 `objectId` 以便稍后使用 `Runtime.getProperties` 或 `Runtime.callFunctionOn` 请求。`--return-by-value` 仍然接受作为默认值的显式形式。
- `--silent`, `--context-id`, `--throw-on-side-effect`, `--generate-preview`, `--object-group`, `--await-promise`, `--include-command-line-api`: 可选的计算参数。引擎支持各不相同。
- `--json`: 打印原始 `InspectData` 负载作为 JSON。默认输出是紧凑的 ASCII 摘要。

#### 6. 发送应用命令

发送应用级别的命令。

```bash
agent-lynx app -m <method> [options] [params]
```

- `-m, --method <method>`: 应用方法名称（例如 `App.openPage`）。
- `-c, --client <clientId>`: （可选）客户端 ID。
- `[params]`: （可选）参数 JSON 字符串。

> 在发送应用命令之前，您**必须**阅读 [支持的应用方法](references/app/index.md)。

#### 7. 打开 URL

在 Lynx 应用中打开特定 URL。

```bash
agent-lynx open <url> [options]
```

- `<url>`: 要打开的 URL。
- `-c, --client <clientId>`: （可选）客户端 ID。

示例：

```bash
agent-lynx open "lynx://example/page"
```

#### 8. 获取控制台

从设备捕获控制台日志。

```bash
agent-lynx get-console [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--offset <number>`: 跳过 N 条消息。
- `--limit <number>`: 限制消息数量。
- `--include-stack-traces`: 包含非错误消息的堆栈跟踪。
- `--level <levels>`: 过滤日志级别（例如 `error,warning`）。
- `--thread <thread...>`: 目标 VM 线程：`background` 或 `main`。如果省略，则默认收集两个线程。

#### 9. 获取源文件

列出所有解析的脚本。这适用于查找与其他命令（例如 `Debugger.getScriptSource`）一起使用的脚本 ID。该命令自动获取当前加载的所有脚本。

```bash
agent-lynx get-sources [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。

#### 10. 检查

打印由连接器守护进程为客户端/会话对提供的服务台 URL。在浏览器中打开打印的 URL，以将图形检查器附加到 CLI 目标会话。

```bash
agent-lynx inspect [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--port <port>`: （可选）守护进程端口。默认为 `21783`。

#### 11. Agent 截图

通过 ActionCore 捕获，可选择将新鲜快照引用直接绘制到生成的 JPEG 中。

```bash
agent-lynx screenshot [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--annotate`: （可选）刷新引用并在结果 JPEG 中绘制 `[N]` 标签，其中 `[N]` 映射到 `@eN`。
- `--fullscreen`: （可选）捕获全屏而不是 LynxView。不能与 `--annotate` 结合使用。
- `-o, --output <path>`: （可选）JPEG 输出路径。
- `--json`: （可选）返回路径、图像尺寸、完整的最新快照和注释元数据。

此命令需要持久的守护进程。有关其单图像输出合同和目标限制，请参阅 [注释快照参考](references/screenshot-annotate.md)。

#### 12. 遗留 Take 截图

使用预 Agent-Lynx 命令使用当前页面进行直接截图。

```bash
agent-lynx take-screenshot [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--fullscreen`: （可选）以全屏模式捕获截图。如果未提供，则默认为 `lynxview` 模式。
- `-o, --output <path>`: （可选）输出文件路径。

#### 13. Take 内容截图

捕获匹配 CSS 选择器的第一个节点的完整滚动内容。

```bash
agent-lynx take-content-screenshot --selector <selector> [options]
```

- `--selector <selector>`: CSS 选择器，用于 `scroll-view` 或兼容的 `list`。必需。
- `--format <jpeg|png>`: （可选）图像格式。默认为 `jpeg`。
- `--scale <number>`: （可选）正输出比例。默认为 `1`。
- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `-o, --output <path>`: （可选）输出文件路径。

`takeContentScreenshot` 官方定义用于 `scroll-view`。该命令接受任何 CSS 选择器，以便在支持在 `list` 上暴露相同方法的运行时也可以使用；不支持的节点返回 UI 方法失败。

有关行为和示例，请参阅 [Take 内容截图参考](references/take-content-screenshot.md)。

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

- `-c, --client <clientId>`: （可选）客户端 ID。

`global-switch list` 选项：

- `--fail-fast`: 在第一个键读取失败时中止。

`global-switch get` 选项：

- `--key <globalKey>`: 全局开关键。 （必需）

`global-switch set` 选项：

- `--key <globalKey>`: 全局开关键。 （必需）
- `--status <on|off>`: 目标开关状态。 （必需）

有关完整键列表和示例，请参阅 [全局开关参考](references/global-switch.md)。

#### 15. Take 堆快照

从当前 Lynx 会话捕获 QuickJS 堆快照并保存为 `.heapsnapshot` 文件。

```bash
agent-lynx take-heap-snapshot [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--thread <thread>`: （可选）目标 VM 线程，`background` 或 `main`。默认为 `background`。
- `-o, --output <path>`: （可选）输出文件路径。默认为操作系统的临时目录。

#### 16. 查询全局内存使用情况

通过全局 `Memory.*` CDP 域查询 Lynx 全局内存使用情况。使用通用 `cdp` 命令，并将请求发送到具有会话 ID `-1` 的全局 DevTool 处理程序。

```bash
# 获取全局 Lynx 内存使用情况跨所有活动实例
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage
agent-lynx cdp -s -1 -m Memory.getAllMemoryUsage '{"timeoutMs":50000}'
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: CDP 会话 ID。除非您有平台特定的原因要覆盖它，否则使用 `-1` 为全局 DevTool 处理程序。
- `params.timeoutMs` （可选）：毫秒的非负超时。最大值是 `300000`。

该命令打印原始 `Memory.getAllMemoryUsage` JSON。不要期望 CLI 输出包含派生的 `summary`、`topMemoryItems` 或 `topInstances` 包装字段。

当 DevTool MCP 服务器可用时，请优先使用 `Memory_getAllMemoryUsage` MCP 工具以相同的原始有效负载，而不是调用 CLI。

代理端报告标准：

1. 当用户请求捕获时或结果太大无法内联显示时，将完整原始 JSON 保存到文件。
2. 使用二进制单位（`KiB`、`MiB`、`GiB`）和两位小数。将 `ratioToApp` 和贡献比率作为两位小数的百分比显示。
3. 首先报告此固定摘要：
   - `collectionStatus`
   - `${completedInstanceCount}/${expectedInstanceCount}` Lynx 实例
   - `totalBytes`
   - `appBytes`
   - `ratioToApp`
   - `elementNodeCount`
   - `viewBytes`
   - `mainThreadRuntimeBytes`
   - `backgroundThreadRuntimeBytes`
4. 然后使用每个 `instances[]` 条目中的细粒度候选项报告“前 5 个内存贡献者”：
   - `instances[i].backgroundThreadRuntimeBytes`
   - `instances[i].mainThreadRuntimeBytes`
   - `instances[i].elementBytes`
   - 每个 `instances[i].viewDetail[category].sizeBytes`
   - 如果 `instances[i].viewBytes` 大于 `viewDetail[*].sizeBytes` 的总和，请包括 `other view memory` 项以显示其余部分。
5. 按字节降序对前 5 个贡献者进行排序。对于每一行，包括排名、项目类型/类别、大小、`% of totalBytes`、`% of instance.totalBytes`、`instanceId` 和 URL。
6. 然后按 `instance.totalBytes` 降序报告“实例”。对于每个实例，包括 `instanceId`、URL、`totalBytes`、`mainThreadRuntimeBytes`、`backgroundThreadRuntimeBytes`、`viewBytes`、`elementBytes` 和紧凑的 `viewDetail` 摘要，例如 `image=12 / 4.15 MiB`。
7. 不要编造缺失字段。如果 `viewDetail` 为空或某个类别的字节数为 `0`，请明确说明。

当前 CDP 有效负载不暴露嵌套的子 LynxView 对象树。

`Memory.getAllMemoryUsage` 与 `Runtime.getHeapUsage` 不同：它返回跨所有活动注册的 Lynx 实例的全局 Lynx 归属内存快照，包括元素、视图、主线程运行时、后台运行时、应用足迹和每个实例的细分。当前 CDP 有效负载不暴露单独的嵌套子 LynxView 内存树；`viewDetail` 是按 UI 视图类别或标签聚合的。有关完整响应形状，请参阅 [Memory CDP 方法](references/cdp/memory/index.md)。

#### 17. 录制

通过 TestBench（基于 CDP）录制 Lynx 页面交互。捕获所有操作（模板加载、触摸事件、JS 模块调用、数据更新）并生成 JSON 回放文件。

```bash
# 开始录制（在打开目标页面之前）
agent-lynx recorder start [options]

# 停止录制并保存回放文件
agent-lynx recorder end [options]
```

- `-c, --client <clientId>`: （可选）用于 `start` 和 `end` 的客户端 ID。
- `-o, --output <path>`: （可选）输出文件或目录路径，用于 `end`。默认为 `~/.lynx-devtool/files/lynxrecorder/recording-<clientId>-<timestamp>.json`.

工作流：

1. 运行 `recorder start`。如果它启用 `enable_debug_mode`，请重新启动应用并再次运行 `recorder start`。
2. 用户打开并交互 Lynx 页面。
3. 运行 `recorder end --output <file.json>` 以停止并保存。
4. 向用户报告绝对文件路径。

**重要**：对于可回放的文件，在 `recorder start` 之后再打开或重新加载目标页面，以便录制包括 `loadTemplate`。

有关更多详细信息，请参阅 [录制参考](references/recorder.md)。

#### 18. 性能跟踪录制

录制压缩的 Lynx 性能跟踪并将其保存为 `.pftrace` 文件。
在构建或打开目标页面之前开始跟踪，以便捕获包括其第一帧。

```bash
# 首先发现客户端；在整个工作流中保持相同的 ID。
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

- `-c, --client <clientId>`: （可选）客户端 ID。如果有多个客户端连接，请列出它们并显式选择一个。
- `trace start --no-systrace`: 禁用 systrace；默认情况下启用。
- `trace start --include-categories <categories>` /
  `trace start --exclude-categories <categories>`: 包括或排除逗号分隔的跟踪类别。
- `trace start --enable-memory-trace`: 启用内存数据收集。
- `trace start --no-force-gc`: 禁用自动垃圾回收，默认情况下启用。
- `trace start --enable-auto-heap-snapshot`: 为 `shared-group` VMs 捕获自动堆快照。添加 `--shared-group-id <id>` 以选择一个 VM。
- `trace start --js-profile-interval <interval>`: JS 采样间隔。当启用分析时，如果提供的间隔是 `0` 或 `-1`，则默认为 `-1`。
- `trace start --js-profile-type <quickjs|v8>`: 为选定的 JS 运行时启用分析。当此选项被省略时，分析将被禁用。
- `trace end --timeout <seconds>`: 等待 `Tracing.tracingComplete` 的秒数。默认为 `30`。
- `trace read-data --stream <handle>`: 由 `trace end` 返回的数字流句柄。
- `trace read-data -o, --output <path>`: 输出路径。默认为操作系统的临时目录中的时间戳 `.pftrace`。
- `trace read-data --timeout <seconds>`: 总下载超时。默认为 `30`。
- `trace event-summary <trace>`: 打印每个 Perfetto `slice.name` 及其出现次数，按出现次数降序排列。添加 `--json` 以获取结构化证据，并使用 `-o, --output <path>` 将其写入文件。
- `trace query <trace> --sql <query>`: 运行内联 Perfetto SQL 并以 JSON 形式输出。
- `trace query <trace> --sql-file <path>`: 从文件中运行 SQL。使用 `--sql` 和 `--sql-file` 中的一个；`--max-rows` 默认为 `1000`。

`trace query` 和 `trace event-summary` 是本地离线命令。它们不会连接到设备、启动守护进程或创建连接器传输。它们的 JSON 包括跟踪的绝对路径、字节长度和 SHA-256，以便代理可以证明它检查了哪个文件。SQL `bigint` 值是十进制字符串，二进制文件是 `{ "base64": "..." }` 对象。

在 Android 上，第一个 `trace start` 可能会启用 `enable_debug_mode` 并要求应用重新启动。重新启动应用并再次运行 `trace start` 之后再打开页面。没有跟踪支持的运行时需要 Android local_test 构建 或 iOS Lynx Profile 构建。有关完整工作流和故障排除，请参阅 [性能跟踪参考](references/trace.md)。

#### 19. ReactLynx 组件树

打印运行中 ReactLynx 页面的组件树，从 `@lynx-js/preact-devtools` 解码。CLI 调用连接器守护进程的 ReactLynx ActionCore；守护进程拥有 `Lynx.onVMEvent` 流、`init`+`refresh` 握手、`operation_v2` 解码和每个会话的组件缓存。CLI 仅渲染返回的树。

```bash
agent-lynx reactlynx tree [options]
```

- `-c, --client <clientId>`: （可选）客户端 ID。
- `-s, --session <sessionId>`: （可选）会话 ID。
- `--depth <n>`: （可选）要打印的最大树深度。默认：无限制。
- `--show-shells`: 包括 ReactLynx 插入的合成 `Fragment` / `Root` / `Anonymous` 包装器。默认情况下隐藏它们。
- `--json`: 以 `{ labels, roots, nodes }` 而不是 ASCII 发射；当脚本将消费树时使用此选项。

输出使用 `@cN [type] Name` 引用（来自 `agent-react-devtools` 的约定）。标签是针对可见根的先序 DFS。`reactlynx tree` 始终捕获新鲜一代并缓存它发射的确切标签视图，包括 `--depth`；稍后 `component @cN` 和 `update-* @cN` 调用将跨独立 CLI 调用重用该视图。紧凑的 `--show-shells` 标签视图也分别缓存。
