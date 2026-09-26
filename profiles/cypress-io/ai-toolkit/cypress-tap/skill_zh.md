# 使用 `cypress tap` 驱动 Cypress

`cypress tap` 控制一个已经运行的 `cypress open` 会话。使用它来迭代测试用例、检查报告器和命令日志，并在没有图形界面交互的情况下读取待测应用。对于一次性无头批处理，请使用 `cypress run`。

## 前置条件

- 从包元数据或锁文件中确认解析的 Cypress 版本为 15.21.0 或更高，并且包含 `tap`。不要使用 `tap --help` 来探测未知的旧版本构建；低于最低版本线的预发布版本可能会尝试会话发现，而不是打印帮助信息。
- 会话必须使用 Electron、Chrome、Chromium 或 Edge。Firefox 和 WebKit 不受支持。
- `cypress open` 和任何配置的 `baseUrl` 开发服务器必须已经运行。
- 当前工作目录 (cwd) 同时决定了 Cypress 二进制文件和自动选择的会话。当目标项目固定了较旧的 Cypress 时，从兼容的代码库中运行 `tap`，并在每次调用时传递 `--session <pid>`。

## 按任务路由

- **启动、选择或轮询会话**：阅读 [session-lifecycle.md](references/session-lifecycle.md)。
- **运行测试用例或读取其结果**：阅读 [session-lifecycle.md](references/session-lifecycle.md) 和 [reading-results.md](references/reading-results.md)。
- **编写或检查测试用例**：阅读 [recipes.md](references/recipes.md) 和 [reading-the-app.md](references/reading-the-app.md)。
- **诊断失败**：阅读 [recipes.md](references/recipes.md)、[reading-results.md](references/reading-results.md) 和 [reading-the-app.md](references/reading-the-app.md)。
- **命令失败、挂起、错误的项目或意外的输出**：阅读 [troubleshooting.md](references/troubleshooting.md)。
- **一次性非交互式批处理**：使用 `cypress run`，而不是 `tap`。

仅阅读当前任务所需的参考文档。

## 核心命令

- `sessions`：可用的会话、项目根目录、测试类型和浏览器；JSON 增加了对支持和渲染器健康状态的支持。
- `status`：生命周期阶段、选定的测试用例、运行标识、计数、构建错误和活动固定。
- `specs`：会话测试类型对应的可运行项目相对测试用例路径。
- `run <spec>`：分发一个测试用例并立即返回。
- `reporter`：测试用例概览和测试 ID；使用 `--test-id`，则显示完整的测试尝试。
- `command`：一行命令日志，包含网络数据、快照和控制台属性。
- `pin`：将应用框架回滚到命令快照。
- `dom`、`aria`、`inspect`：读取已稳定的应用或当前固定的快照。

所有命令都接受 `--session <pid>`、`--json` 和 `--timeout <ms>`。在确认支持构建的情况下，使用 `npx cypress tap <command> --help` 获取特定命令的标志。

## 不可协商的判定规则

`run` 确认分发，而不是执行，并在新运行开始前返回。在那段时间内，`status` 和应用读取仍然可以返回上一个运行的合理判定和页面。

对于每个显式运行：

1. 读取当前的 `startedAt`。
2. 分发一个测试用例。
3. 逐个轮询 `status --json` 响应。
4. 对于预期的 `spec`，仅接受 `passed` 或 `failed`，并且 `startedAt` 非空且已更改。`startedAt` 为空仅当会话中从未为该测试用例启动过运行——第一次选择时的构建失败。在重新运行或监视器重建时失败的构建仍然会推进 `startedAt`，因此它走正常路径。仅保留空回退（一个已更改的可观察基线，或先前的 `loading`/`running` 观察）用于第一次选择的情况。
5. 绑定循环并在没有匹配的新判定到达时失败。

保存活动测试用例会触发自动监视器运行。编辑后，可以使用该运行或让其稳定后再获取基线并分发另一个。切勿有意让两个运行同时进行。

成功的 `status` 调用的空白和部分有效负载是暂时的。将缺失的字段视为“继续等待”，而不是状态变化。非零的 `status` 退出是命令失败，而不是部分读取：停止轮询并报告它。

仅 `passed` 和 `failed` 是判定。构建失败是带有诊断信息的 `failed`，可能在任何测试存在之前就发生。`status` 是唯一携带该诊断的界面——`reporter` 将失败的构建渲染为空测试用例。

## 关键正确性规则

1. **针对预期的会话**。如果存在多个会话，或者自动选择行为异常，请检查 `sessions` 并传递 `--session <pid>`。自动选择可能会选择另一个项目或一个无响应的会话。
2. **保留二进制文件位置**。cwd 控制每次调用的 `npx` 解析。当项目固定了较旧的 Cypress 时，从兼容的代码库中运行命令并传递 `--session <pid>`。
3. **不要解析失败的命令**。在解析 JSON 之前检查退出代码。支持构建的失败通常使用 `stderr`，但较旧的兼容性失败可能使用 `stdout`。一个模糊的选择器是故意例外：它退出 `1` 并在 `stdout` 上列出匹配项。
4. **在检查兼容性时不要丢弃分发 stdout**。较旧的 Cypress 可能会打印 `Unknown command "tap"` 和用法文本到 `stdout`；重定向它会隐藏原因。
5. **重定向可能较大的 JSON**。`reporter --test-id --json` 和 `command --json` 可能包含数百 KB 的数据。将它们保存到文件并解析该文件。
6. **在得出不存在结论之前检查截断**。`dom` 和 `aria` 限制输出。当出现 `(output truncated)` 时，缩小选择器或提高限制。
7. **在得出不存在结论之前检查活动框架**。一个尾随的待处理/跳过的测试可以让已稳定的运行器停留在空白占位符上，而应用读取仍然退出 `0`。确认一个已知的应用锚点。如果框架为空，请从最后一个真实命令固定一个快照并读取该状态。
8. **在编辑或删除测试用例之前读取结果**。结果和快照存储在 Cypress 应用的内存中，并且在重新运行、重新启动、重命名或删除时可能会消失。
9. **清除固定**。在检查命令快照后，运行 `pin --clear`；否则，后续的应用读取将继续描述固定的过去。退出 `0` 的 `cleared:false` 结果是一个无害的无操作，即使人类输出显示 `FAILED TO CLEAR PIN`。
10. **为活动状态使用正确的读取器**。使用 `aria` 获取当前表单控件的值：`dom` 和 `inspect` 可以显示初始 HTML `value` 属性，并且 `inspect` 可能会省略可访问性值。使用 `dom` 获取精确的活动区域、toast、状态和标签文本，因为 `aria` 可能会省略后代文本。

## 输出契约

- 人类输出用于读取；`--json` 用于解析，可能包含大量数据。
- `status` 对于已知生命周期阶段退出 `0`，包括 `not connected`。发现、兼容性、不支持的浏览器和渲染器失败退出 `1`，有时没有 `stdout`；轮询器必须在非零退出时快速失败。
- `dom`、`aria` 和 `inspect` 需要恰好一个选定的元素。歧义退出 `1` 并列出候选选择器。未命中不是 CLI 失败：`dom` 和 `inspect` 报告 `found:false`；`aria` 对于未命中和没有可访问性节点的元素都返回空树。
- 失败是带有不稳定错误代码的散文。基于退出状态，而不是消息文本进行分支。

## 性能默认值

- 优先选择一次 `reporter --test-id` 读取，而不是每行一次 `command` 调用。
- 在获得新鲜判定并检查活动框架后，独立的应用读取可以并发运行。
- 如果有界状态轮询失败，请检查 `sessions` 中的 `rendererResponsive: false`；重启卡住的渲染器，而不是增加 `--timeout`。
