# agent-react-devtools

一个通过 React DevTools 协议连接到正在运行的 React 或 React Native 应用的命令行工具，并以 token 效率高的格式暴露组件树、属性、状态、钩子和性能分析数据。

## 核心工作流程

1. **确保连接** — 检查 `agent-react-devtools status`。如果守护进程未运行，则使用 `agent-react-devtools start` 启动它。使用 `agent-react-devtools wait --connected` 阻塞，直到连接到 React 应用。
2. **检查** — 获取组件树，搜索组件，检查属性/状态/钩子。
3. **分析** — 开始分析，触发交互（或要求用户触发），停止分析，分析结果。
4. **操作** — 使用数据修复错误、优化性能或解释正在发生的事情。

## 基本命令

### 守护进程

```bash
agent-react-devtools start              # 启动守护进程（首次命令时自动启动）
agent-react-devtools stop               # 停止守护进程
agent-react-devtools status             # 检查连接、组件数量、最后事件
agent-react-devtools wait --connected   # 阻塞，直到连接到 React 应用
agent-react-devtools wait --component App # 阻塞，直到出现组件
```

### 组件检查

```bash
agent-react-devtools get tree           # 完整的组件层次结构（标签：@c1, @c2, ...）
agent-react-devtools get tree --depth 3 # 限制深度
agent-react-devtools get component @c5  # 特定组件的属性、状态、钩子
agent-react-devtools find Button        # 通过显示名称搜索（模糊匹配）
agent-react-devtools find Button --exact # 精确匹配
agent-react-devtools count              # 按类型计数：fn, cls, host, memo, ...
agent-react-devtools errors             # 列出存在错误或警告的组件
```

### 性能分析

```bash
agent-react-devtools profile start              # 开始录制
agent-react-devtools profile stop               # 停止并收集数据
agent-react-devtools profile slow               # 按平均渲染时间最慢的组件
agent-react-devtools profile slow --limit 10    # 前 10 个
agent-react-devtools profile rerenders          # 最频繁重新渲染的组件
agent-react-devtools profile report @c5         # 某个组件的详细报告
agent-react-devtools profile timeline --limit 10                        # 前 10 个提交（使用 --limit；无限制可能输出 300+ 行）
agent-react-devtools profile timeline --limit 10 --offset 10           # 下 10 个（分页）
agent-react-devtools profile timeline --sort duration --limit 5        # 最昂贵的 5 个提交
agent-react-devtools profile timeline --sort timeline --limit 5        # 明确按时间顺序（与默认相同）
agent-react-devtools profile commit 3           # 提交 #3 的详细信息
agent-react-devtools profile export profile.json # 导出为 React DevTools Profiler JSON
agent-react-devtools profile diff before.json after.json  # 比较两个导出
```

## 理解输出

### 组件标签

每个组件都会获得一个稳定的标签，如 `@c1`、`@c2`。在后续命令中使用这些标签来引用组件：

```
@c1 [fn] App
├─ @c2 [fn] Header
├─ @c3 [fn] TodoList
│  ├─ @c4 [fn] TodoItem key=1
│  └─ @c5 [fn] TodoItem key=2
└─ @c6 [host] div
```

类型缩写：`fn` = 函数，`cls` = 类，`host` = DOM 元素，`memo` = React.memo，`fRef` = forwardRef，`susp` = Suspense，`ctx` = 上下文。

存在错误或警告的组件会显示注释：`⚠2` = 2 个警告，`✗1` = 1 个错误。使用 `agent-react-devtools errors` 列出仅受影响的组件。

### 检查的组件

```
@c3 [fn] TodoList
props:
  items: [{"id":1,"text":"Buy milk"},{"id":2,"text":"Walk dog"}]
  onDelete: ƒ
state:
  filter: "all"
hooks:
  useState: "all"
  useMemo: [...]
  useCallback: ƒ
```

`ƒ` = 函数值。值超过 60 个字符会被截断。

### 分析输出

```
最慢的（按平均渲染时间）:
  @c3 [fn] ExpensiveList  avg:12.3ms  max:18.1ms  renders:47  causes:props-changed  changed: props: items, filter
  @c4 [fn] TodoItem  avg:2.1ms  max:5.0ms  renders:94  causes:parent-rendered, props-changed  changed: props: onToggle
```

渲染原因：`props-changed`、`state-changed`、`hooks-changed`、`parent-rendered`、`force-update`、`first-mount`。

当提供特定变化的键时，`changed:` 后缀会显示哪些属性、状态键或钩子触发了渲染（例如 `changed: props: onClick, className  state: count  hooks: #0`）。

## 常见模式

### 在重新加载后等待应用连接

```bash
agent-react-devtools wait --connected --timeout 10
agent-react-devtools get tree
```

在触发页面重新加载或 HMR 更新后使用此命令，以避免查询空状态。

### 诊断慢交互

```bash
agent-react-devtools profile start
# 用户与应用交互（或使用 agent-browser 驱动 UI）
agent-react-devtools profile stop
agent-react-devtools profile slow --limit 5
agent-react-devtools profile rerenders --limit 5
```

然后使用 `get component @cN` 和 `profile report @cN` 检查最糟糕的组件。

### 分块浏览长时间线

```bash
agent-react-devtools profile timeline --limit 20               # 提交 0–19
agent-react-devtools profile timeline --limit 20 --offset 20   # 提交 20–39
agent-react-devtools profile timeline --offset 30 --limit 10   # 跳过预热，显示 30–39
```

一旦发现峰值，使用 `profile commit <N>` 深入特定提交。

### 查找组件并检查其状态

```bash
agent-react-devtools find SearchBar
agent-react-devtools get component @c12
```

### 验证修复是否有效

```bash
agent-react-devtools profile start
# 重复交互
agent-react-devtools profile stop
agent-react-devtools profile slow --limit 5
# 与之前的运行结果比较渲染计数和持续时间
```

## 与 agent-browser 一起使用

在使用 `agent-browser` 驱动应用进行性能分析或调试时，您**必须使用带头模式** (`--headed`)。无头 Chromium 与真实浏览器执行 ES 模块脚本的方式不同，这会导致 devtools 连接脚本无法正常运行。

```bash
agent-browser --session devtools --headed open http://localhost:5173/
agent-react-devtools status  # 应该显示 1 个连接的应用
```

## 重要规则

- **标签重置** — 当应用重新加载或组件卸载/重新挂载时。重新加载后，使用 `wait --connected` 然后使用 `get tree` 或 `find` 重新检查。
- **首先使用 `status`** — 如果状态显示 0 个连接的应用，则 React 应用未连接。Web 用户可能需要运行 `npx agent-react-devtools init`；React Native 用户需要执行 [setup.md](references/setup.md) 中的手动步骤。在那种状态下，树观察命令会以 `No React app is attached` 退出 1；将其视为“未观察到”，而不是干净的结果。
- **另一个 DevTools 连接会重新分配 ID** — 当 React Native DevTools（或另一个 agent）连接到同一应用时，React 会使用新的 ID 重新刷新树，守护进程会替换其副本。在重新使用早期 `@cN` 标签之前，重新运行 `get tree` 或 `find`。
- **需要带头浏览器** — 如果使用 `agent-browser`，始终使用 `--headed` 模式。无头 Chromium 无法正确加载 devtools 连接脚本。
- **交互时分析** — 分析仅捕获在 `profile start` 和 `profile stop` 之间发生的渲染。确保相关交互在此窗口期内发生。
- **在大型树中使用 `--depth`** — 深树会产生大量输出。从 `--depth 3` 或 `--depth 4` 开始，仅在您关心的子树上进行更深入的检查。

## 参考

| 文件 | 何时阅读 |
|------|-------------|
| [commands.md](references/commands.md) | 完整的命令参考，包括所有标志和边缘情况 |
| [profiling-guide.md](references/profiling-guide.md) | 分步性能分析工作流程和解释结果 |
| [setup.md](references/setup.md) | 如何连接不同的框架（Vite、Next.js、Expo、CRA） |
