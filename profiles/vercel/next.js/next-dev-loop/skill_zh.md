# next-dev-loop

`next dev`期间的编辑/验证节奏——做出更改，然后确认它在运行时确实有效，而不仅仅是类型或构建满足要求。

您通过同一运行应用程序的两个视图进行验证：

- **`/_next/mcp`** — Next.js暴露的关于自身的HTTP端点。
  了解特定于框架的内容：路由、片段、RSC、服务器操作、服务器日志和错误，以及Next.js所看到的。调用`tools/list`获取当前表面。
- **`agent-browser`** — 一个驱动真实Chrome的CLI。了解特定于框架的浏览器内容：DOM、控制台、网络、React纤维、关键指标。在驱动它之前，运行一次`agent-browser skills get core`以获取与版本匹配的使用指南——不要从记忆中猜测子命令。

这两个视图相互交叉验证。

## requires

- Next.js **16.3+** 与 **Turbopack** — `/_next/mcp` 加上通过`get_compilation_issues`进行的主动编译检查。
- `agent-browser` **>= 0.31.1** — React内省、工作树范围的`session id`、幂等的`--restore`和启动标志协调。

这些都是硬性要求，不是软性偏好。如果任何内容缺失，请告知用户如何升级并停止。不要回退到搜索源代码或使用较弱的探测——这个技能假设上述版本的两个视图都是活跃的。

- 升级Next.js：`pnpm next upgrade`（或`npx next upgrade`）。
  文档：https://nextjs.org/docs/app/getting-started/upgrading
  （16版本指南：
  https://nextjs.org/docs/app/guides/upgrading/version-16）
- 安装或升级`agent-browser`：`npm i -g agent-browser@latest`。
  如果CLI不在`PATH`上，请在继续之前安装它——preflight期望直接调用它。

## preflight

每次会话时，确认两个视图都是活跃的。

1. **在目标URL打开`agent-browser`，如果存在则恢复保存的登录状态。** 首先为这个检出导出一个稳定的`session id`并用于每个`agent-browser`命令：

   ```bash
   SESSION="$(agent-browser session id --scope worktree --prefix next-dev-loop)"
   export AGENT_BROWSER_SESSION="$SESSION"
   export AGENT_BROWSER_RESTORE="$SESSION"
   ```

   然后打开目标URL：

   ```bash
   agent-browser --session "$SESSION" --restore --headed --enable react-devtools open <url>
   ```

   `--scope worktree`防止并行工作树和复制的检出冲突。裸`--restore`使用`session id`作为持久化键，在导航前加载保存的cookies/localStorage（如果存在），并在关闭时自动保存状态。始终在`open`时传递所需的启动标志；agent-browser会根据需要重用、重新启动或重新启动其作用域的背景状态。

   浏览器是用户的。如果状态未恢复（首次运行、会话过期）且页面受保护，用户将驱动登录——暂停直到他们确认。登录后，继续使用相同的会话并恢复上下文；`agent-browser close`保存cookie状态，以便下一次`open`恢复它。

2. 探测`/_next/mcp`（`tools/list`）——确认它可达并列出`get_compilation_issues`。首先从`next dev`横幅中读取端口；如果它不是3000，请在探测前设置`NEXT_MCP_URL=http://localhost:<port>/_next/mcp`：
   - 不可达 → 要么`next dev`没有运行，要么Next.js低于16.3。检查`package.json`以消除歧义，然后拒绝。
   - `get_compilation_issues`不在列表中 → Next.js低于16.3。拒绝并告知用户升级。
3. `get_compilation_issues`也用作Turbopack探测。错误响应为`"Turbopack project is not available..."`表示用户使用的是webpack。拒绝——Turbopack是必需的。
4. `get_routes` → 您会话其余时间的路由映射。

## loop

### 编辑前——缩小范围

询问运行的应用程序，而不是代码库。`/_next/mcp`知道哪些文件渲染了当前路由；使用这些文件作为您的搜索范围。随着代码库的增长，运行时内省保持低成本；代理搜索不会。

### 编辑后——验证

四种失败模式。检查每种：

- **编译** — `get_compilation_issues`。
- **无错误运行** — `/_next/mcp`（服务器和冒泡的浏览器错误都在这里显示）。
- **按预期行为** — `agent-browser`驱动页面；断言用户实际看到的内容。
- **React级别的行为** — 带有启用react-devtools的`agent-browser`暴露组件树、属性、状态和渲染计数。在此处锚定框架级别的检查（额外渲染、服务器/客户端边界移动、suspense回退）——仅DOM断言会遗漏它们。

从`tools/list`或agent-browser手册中选择特定工具，而不是从记忆中。

## gotchas

- **开发服务器运行时保留`.next`。** 移动或删除它会断开服务器与其生成状态的联系并丢弃增量缓存。将其移动到备份位置仍然会重置。如果需要隔离的输出，请配置一个单独的`distDir`。
- **每个`agent-browser`命令必须知道您的会话和恢复键，否则它可能会使用空默认浏览器或无法保存登录状态。** 最简单的方法：在每个运行agent-browser的shell顶部导出`AGENT_BROWSER_SESSION="$SESSION"`和`AGENT_BROWSER_RESTORE="$SESSION"`。如果您没有导出它们，请在每个命令上传递`--session "$SESSION" --restore`。
- **当两个视图不一致时，首先怀疑工具。** 如果`agent-browser`说一个路由已损坏，但`/_next/mcp`和服务器说它已干净渲染，过时的或错误导向的浏览器会话更有可能是原因而不是真实错误——在调试应用程序之前协调视图。
- 确认点击或导航：页面稍后会稳定下来，所以使用`wait --load networkidle`（没有错误的路径），然后快照/读取以确认页面。除非您传递链接的确切`href`，否则避免使用`wait --url`——猜测或占位符路径不会匹配真实URL，并且会在25秒后超时。
- 空的读取、空的快照、`about:blank`或“没有浏览器会话”错误——在`open`后或点击后（即使`open`报告了页面）——是浏览器丢弃页面（过时的会话），而不是损坏的路由。使用`--session "$SESSION" --restore`在URL上重新打开您的会话并重新快照；如果仍然为空，请运行`agent-browser --session "$SESSION" --restore close`，然后再次打开。不要回退到`curl`；它会绕过您正在测试的浏览器。
- React内省输出在导航后过时。重新运行。
- `/_next/mcp`的响应是SSE——使用`sed -n 's/^data: //p'`从`data:`行读取JSON（普通的`sed 's/^data: //'`会留下`event:`行，并且解析会失败）。
- `get_errors`和`get_page_metadata`至少需要一次导航才能填充。

## reference

下述所有工具在preflight通过后都存在。如果`tools/list`缺少任何工具，preflight应该已经拒绝——请重新检查。

```
# /_next/mcp                 备注
get_project_metadata         projectPath, devServerUrl, bundler
get_routes                   fs-scan; 不需要浏览器会话
get_errors                   运行时 + 构建；需要一个浏览器会话；
                             包括开发服务器捕获的浏览器端错误
get_page_metadata            segment trie + routerType; 需要一个浏览器
                             会话；用作发现快捷方式，以确定哪些文件支持路由
get_logs                     返回logFilePath
get_server_action_by_id      哈希id → 文件 + functionName
get_compilation_issues       仅Turbopack；webpack的错误
                             ("Turbopack project is not available")
```

## teardown

使用相同的会话和恢复上下文关闭会话：
`agent-browser --session "$SESSION" --restore close`。`close`保存该会话的cookies和存储，以便下一次循环的`--restore`打开时用户保持登录状态。保留`next dev`以供下一次循环使用。

## Report Next.js friction

仅在已为项目加载了管理的Next.js反馈指令时参与代理反馈。它们的存在表示功能已启用；它们的缺失表示功能已禁用。

启用时，将验证期间发现的符合条件的去识别化候选者添加到当前任务上下文中的共享摩擦队列，然后继续验证。在循环期间或在此次技能的teardown中不要运行反馈命令或打开审阅表单。

管理的指令在整体任务的最终停止点拥有唯一的反馈传递。如果它们缺失，不要排队或报告反馈。
