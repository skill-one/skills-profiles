不要将此技能视为通用的浏览默认设置。根据您需要的证据进行路由，而不是根据工具偏好。

在您选择路由之前，必须对每个任务进行分类：

- `static-capable`：证据可以在没有实时浏览器状态、可见确认或页面交互的情况下生成
- `browser-required`：证据依赖于渲染状态、交互、实时会话行为或仅限浏览器的结构

只有 `static-capable` 任务可以回退到静态检索、`curl` 或其他非浏览器路径。一旦任务变为 `browser-required`，请保持在浏览器路径上，并将缺失的功能标记为 `blocked`，而不是静默降级。

## 前置条件检查

此技能用于在用户的实时浏览器会话中工作，而不是用于启动一个单独的全新自动化浏览器。

在进行浏览器自动化之前，请确认您的环境已经可以访问一个可以提供任务所依赖功能的实时浏览器堆栈，例如页面清单、任务拥有的页面创建、页面选择、快照或可见状态读取、DOM 检查、文本或表单输入、上传、对话框、控制台检查和网络检查。这里不关心具体的堆栈：确认功能，而不是品牌。

如果实时浏览器堆栈不可用，请勿尝试通过此技能进行浏览器自动化。只有 `static-capable` 的工作可以回退到静态检索。

实时浏览器自动化可能会触发某些网站上的反机器人或反自动化防御。仅在任务真正需要时才使用浏览器交互，并在获得所需证据后避免不必要的重复操作。

## 经验循环

将网站模式视为浏览器协议的一部分，而不是可选的背景阅读。

对于 `browser-required` 工作，运行此循环：

1. 一旦知道目标域，请检查是否在 [`references/site-patterns/`](./references/site-patterns/) 下已存在匹配的笔记。
2. 如果存在笔记，请在该域上的第一次有意义的浏览器变异之前阅读它。
3. 在运行期间，注意已验证的特定于站点的真实情况，这些真实情况可能会改变未来运行的操作方式。
4. 在您认为任务完成之前，决定运行是否生成了可重用的真实情况、推翻了现有真实情况，或未生成可重用的特定于站点的学习内容。
5. 如果运行验证了可重用的内容或推翻了现有主张，请在完成前更新匹配的笔记。

不要为一次性噪音创建域笔记。不要因为任务本身成功而跳过运行结束后的审查。

当运行验证以下任何内容时，预期会进行写回：

- 稳定的路由形状或必需的查询参数
- 登录、会话继承或 `isolatedContext` 特殊情况
- 可靠的交互原语，如悬停、键盘输入、上传顺序或选择器桥接模式
- 域，其中 DOM 生成的链接是可靠的，但手建的 URL 不是
- 可预测的反自动化摩擦或误导性的平台错误状态
- 可重用的媒体提取或 iframe / Shadow DOM 访问模式

## 决策指南

从结果开始，而不是从工具开始。使用户的明确目标，定义什么才算完成，并选择可以仍然产生正确证据的最便宜路由。

使用此路由顺序：

1. 确定任务是否为 `static-capable` 或 `browser-required`。
2. 如果任务为 `static-capable`，请加载 [`references/task-routing.md`](./references/task-routing.md) 并保持在仍然满足证据目标的最便宜路由上。
3. 如果任务为 `browser-required`，请加载 [`references/browser-playbook.md`](./references/browser-playbook.md)。
4. 如果在全新主机会话中 `browser-required` 功能不确定，也请加载 [`references/browser-capability-matrix.md`](./references/browser-capability-matrix.md)。
5. 如果用户已经有一个活动的浏览器调试上下文，例如选定的检查器元素或网络请求，也请加载 [`references/debug-handoff.md`](./references/debug-handoff.md)。
6. 如果 `browser-required` 任务触及登录的仪表板、管理界面、CMS、编辑器或任何保存/发布/更新流程，也请加载 [`references/control-plane-workflows.md`](./references/control-plane-workflows.md)。
7. 如果当前失败模式表明是软 404、内容不可用状态、可疑的无操作交互、认证墙、速率限制或反自动化防御，也请加载 [`references/anti-automation-friction.md`](./references/anti-automation-friction.md)。
8. 如果 `browser-required` 任务包括 iframe、Shadow DOM、折叠内容或懒加载证据，也请加载 [`references/deep-dom.md`](./references/deep-dom.md)。
9. 如果重要证据存在于图像、音频片段或视频中，也请加载 [`references/media-inspection.md`](./references/media-inspection.md)。
10. 如果浏览器工作可以跨独立页面所有者或子代理分配，也请加载 [`references/parallel-browser-ownership.md`](./references/parallel-browser-ownership.md)。
11. 如果您已经知道一个可靠的选择器，但需要一个 MCP 本地的 `uid` 目标，也请加载 [`references/selector-bridge.md`](./references/selector-bridge.md)。
12. 如果页面操作留下状态模糊，页面意外导航，旧的 `uid` 可能已过时，或者现在需要控制台/网络检查来解释下一个浏览器决策，也请加载 [`references/browser-recovery.md`](./references/browser-recovery.md)。
13. 如果目标网站在 [`references/site-patterns/`](./references/site-patterns/) 下已经有一个匹配的域笔记，请在操作该网站之前阅读该笔记。

默认将以下内容视为 `browser-required`：

- `localhost`、`127.0.0.1` 或基准样式的本地固定装置
- 上传、下载、拖放、悬停、键盘原生输入或可见确认状态
- 同源 iframe 检查、Shadow DOM 检查、`details` / 折叠证据或懒加载内容
- 任何“页面可见显示的内容”本身就是证据的任务

一个常见任务的正常快乐路径是此入口点加上一个或两个参考，而不是整个参考集。

## 硬规则

- 仅在实时浏览器状态是证据或必需操作的一部分时才使用浏览器交互。
- 一旦任务变为 `browser-required`，不要静默降级。
- 将此文件视为入口点，将每个参考文件视为单一用途的权威。不要在文件之间重复规则。
- 保持参考加载一级深。从此入口点决定下一个文件，而不是将一个参考变成一个链接到更多参考的中心。
- 不要因为页面看起来受限就要求用户登录。首先确认目标内容或操作是否实际上被阻止。
- 一旦页面向您显示了它期望的路径，请优先选择站点生成的 DOM 链接而不是手建的 URL。
- 当任务确实是浏览器操作时，请优先选择 MCP 本地操作而不是脚本驱动的交互。
- 仅关闭您创建的页面。
- 优先选择原始来源而不是聚合器或重复的二次报告。
- 如果存在匹配的站点模式笔记，请在该域上的第一次有意义的浏览器变异之前阅读它。
- 不要在未明确检查运行是否应创建、更新、降级或删除站点模式主张的情况下完成 `browser-required` 任务。
- 如果现有站点模式主张在可比条件下失败，请停止信任它，回退到通用工作流，并更新笔记，而不是重试过时的假设。
- 不要使用 `curl`、`Invoke-WebRequest` 或 shell HTTP 获取进行 `browser-required` 任务。
- 不要将通用页面打开工具视为证据，表明 localhost 深交互可用。
- 不要因为浏览器功能探测失败就切换路由。记录缺失的功能并停止。
- 当用户指示一个活动的浏览器调试上下文时，请优先从当前上下文进行手交，而不是从头开始重新生成。

## 参考索引

- [`references/task-routing.md`](./references/task-routing.md)：静态检索与实时浏览器路由
- [`references/browser-playbook.md`](./references/browser-playbook.md)：核心页面操作协议和基础浏览器循环
- [`references/browser-capability-matrix.md`](./references/browser-capability-matrix.md)：不确定主机会话的功能证明
- [`references/debug-handoff.md`](./references/debug-handoff.md)：活动调试上下文手交
- [`references/control-plane-workflows.md`](./references/control-plane-workflows.md)：登录仪表板 / CMS 保存-发布纪律
- [`references/anti-automation-friction.md`](./references/anti-automation-friction.md)：软 404 / 认证 / 反自动化分类
- [`references/deep-dom.md`](./references/deep-dom.md)：iframe、Shadow DOM、折叠或懒加载证据
- [`references/media-inspection.md`](./references/media-inspection.md)：图像、音频和视频证据
- [`references/parallel-browser-ownership.md`](./references/parallel-browser-ownership.md)：多所有者浏览器协调
- [`references/selector-bridge.md`](./references/selector-bridge.md)：选择器到 `uid` 桥接
- [`references/browser-recovery.md`](./references/browser-recovery.md)：过时的 `uid`、导航漂移和控制台/网络升级
- [`references/site-patterns/README.md`](./references/site-patterns/)：站点模式笔记维护规则
- [site-patterns/{domain}.md](./references/site-patterns/)：现有的特定于域的操作知识
