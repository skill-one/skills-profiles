# ego-browser

安装、连接或运行时问题，请阅读 `references/install.md`。使用 `help()` 或 `references/api.md` 查看下方列出的 API 的签名和罕见选项。

## 运行浏览器脚本

通过 heredoc 运行 JavaScript：

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpace("inspect example page");
const page = task.page("p1");
await page.goto("https://example.com");

console.log({ taskSpaceId: task.spaceId, page: page.label });
console.log(await page.snapshot());
EOF
```

在某些沙盒环境中，heredoc 输入可能无法工作；使用 `-e` 代替：

```bash
ego-browser nodejs -e '
const task = await taskSpace("inspect example page");
const page = task.page("p1");
await page.goto("https://example.com");
console.log({ taskSpaceId: task.spaceId, page: page.label });
console.log(await page.snapshot());
'
```

在 Bash/Zsh 中，用单引号包围代码，用双引号包围 JavaScript 字符串。代码中的单引号需要 shell 引用。

脚本始终在 Node.js 中运行，而不是在网页 Page 中。浏览器辅助工具和 Node.js API 属于脚本；Page 全局变量（如 `window`、`document`、`location` 和 DOM API）不属于。将浏览器端的 JavaScript 放在 `page.evaluate()` 中。不要导入 Playwright 或启动另一个浏览器。

Node.js 运行时使用 ESM。当脚本需要本地文件时，使用动态导入（如 `await import("node:fs/promises")`）加载内置模块。

Ego-browser 故意暴露了一个小的自定义 API。它不是 Playwright，即使方法名和选项看起来相似。仅使用本技能中明确列出的 TaskSpace、Page、FileChooser、鼠标和键盘 API。不要推断 Playwright 方法，如 `locator()`、`getByRole()`、`context()`、`expect()` 或 `route()`。当列出的 API 无法覆盖操作时，使用文档中的 `page.evaluate()` 或 `page.cdp()` 逃逸通道，而不是猜测其他方法。

指针操作接受可选的 `label`，用 3-6 个字的简短描述。在点击、悬停、拖动或滚动时传递它，以保持操作文本与可见代理光标同步。

当用户明确要求 ego-browser 时，从真实的浏览器命令开始，只有在失败时才诊断 CLI 或安装。

## 空间、回合和页面

- 对整个用户目标使用恰好一个 TaskSpace。创建一次，打印其 `spaceId`，并在后续回合中恢复相同的空间。只有在用户明确要求时才使用多个空间。
- 不要使用新的 TaskSpace 来恢复卡住、阻塞、超时或意外的 Page。在现有空间内恢复；如果它无法继续，请停止并询问用户。
- 每次调用都会启动一个新的 Node.js 进程。任务空间、标签和 Page 标签持久化；JavaScript 变量不会。
- 新的任务空间从 Page `p1` 开始；导航它，而不是打开另一个 Page。
- 使用 `goto()` 重新使用 Page，而不是为每个 URL 打开新的 Page。
- 所有时间值都是毫秒。

```js
// 后续回合：使用之前打印的空间 ID 和 Page 标签。
const resumed = await taskSpace(7);
const source = resumed.page("p1");
await source.goto("https://example.com/releases");
```

除非用户明确要求特定的 Ego Lite 配置文件，否则不要检查或选择配置文件。`profileId` 仅在创建空间时适用；使用 `help("profiles")` 获取精确的工作流程。

支持的 TaskSpace API：

- 状态：`spaceId`、`name`、`ownership`、`page(label)`、`userPage()`
- 页面：`await task.pages()`、`await task.tabs()`、`newPage()`、`adopt(page, { as? })`、`release(label)`
- 控制：`waitForControl(options)`、`handOff()`、`finish({ keep })`
- 高级：`cdp(method, params, options)`

页面接收永久标签，如 `p1`、`p2` 和 `p3`。优先使用这些标签，而不是自定义 `{ as }` 值。随着任务的进行，重复使用或关闭页面；运行时在达到配置的页面预算时报告。

`task.newPage()` 在必须保持多个页面打开时创建另一个空白页面。使用 `page.goto()` 单独导航它。

`await task.pages()` 返回管理的页面。`await task.tabs()` 返回空间中的每个标签，作为 `{ label?, page, targetId, title, url, active, openedBy }`。没有标签的标签是未管理的；在操作之前采用它：

```js
const active = (await task.tabs()).find((item) => item.active);
if (active && !active.label) {
  const page = await task.adopt(active.page);
  console.log({ page: page.label, url: await page.url() });
}
```

`release(label)` 将未知来源的页面返回给用户，而不关闭其标签。使用 `page.close()` 关闭 Agent 创建的页面。将 `openedBy: "unknown"` 视为用户拥有的页面，在决定是否可以关闭时考虑它。

## 页面操作

ego-browser 提供以下页面 API：

- 状态和观察：`label`、`spaceId`、`openedBy`、`targetId`、`url()`、`title()`、`info()`、`snapshot()`、`screenshot()`
- 导航和等待：`goto()`、`reload()`、`waitForURL()`、`waitForEvent()`、`waitForSelector()`、`waitForLoadState()`、`waitForFunction()`、`waitForTimeout()`
- 元素：`click()`、`dblclick()`、`hover()`、`dragAndDrop()`、`fill()`、`selectOption()`、`focus()`、`press()`、`setInputFiles()`、`waitForFileChooser()`、`close()`
- 对话框：`acceptDialog(promptText?)`、`dismissDialog()`
- 指针：`mouse.click()`、`move()`、`down()`、`up()`、`wheel()`
- 键盘：`keyboard.down()`、`up()`、`press()`、`type()`、`insertText()`、`paste()`
- 页面代码和协议：`evaluate(fnOrString, argument)`、`fetch(url, options)`、`cdp(method, params, options)`

`page.evaluate()` 回调仅在 Page 内运行；它们无法从周围脚本读取变量或 Node.js 模块。在回调内定义浏览器端辅助工具，或将一个可 JSON 序列化的值作为其第二个参数传递。

高效工作：

- 每次观察时，仅收集选择下一个操作的最便宜页面状态。使用快照进行语义或定位的真实依据，使用截图进行视觉确认；不要默认请求两者。
- 如果操作未产生预期结果，在决定是否重试之前检查当前页面。不要盲目重复它或立即退回到坐标或原始 CDP。
- 一旦页面清楚地显示请求的结果，就停止；不要通过多个界面确认相同的结果。

### 语义页面：快照和选择器

对于普通的 DOM 页面，优先使用快照和语义选择器。只有在有用的 DOM 语义不可用时，才使用截图和坐标。

在选择不熟悉的靶标之前，先拍摄快照。当当前状态足以在同一 Page 上计划多个操作时，在一个脚本调用中完成它们，然后观察结果一次。仅在中间结果改变下一个操作应该发生时，在操作之间进行观察。将操作序列、等待其最终预期状态和下一个快照保持在同一个脚本调用中。最后打印快照，以便下一回合可以直接基于它采取行动。最终快照是下一回合对已更改页面的起始视图；没有它，该回合通常必须在它选择下一个目标之前花费一个单独的浏览器调用进行观察，这会浪费计算资源。

等待预期结果：使用 `waitForURL()` 进行导航，`waitForSelector()` 进行元素状态，或 `waitForFunction()` 进行应用程序状态。当存在可观察的条件时，避免固定延迟。快照捕获当前时刻；它不会等待页面变得稳定。`page.snapshot()` 捕获当前视口。对于视口外的内容，使用 `page.snapshot({ scope: "full_page" })`。

默认视口快照包括浏览器返回的可见 iframe 内容。要关注框架的子树，重新使用其 `iframe` 行上打印的引用：

```js
console.log(await page.snapshot({ scope: "subtree", root: "@12" }));
```

使用子树返回的引用在 iframe 内执行操作。子树快照不会将后续定位操作限制在 iframe 内；它们仍然优先在顶层文档中搜索，然后再搜索框架。

`waitForLoadState()` 默认为 `load`。`waitForFunction()` 遵循 Playwright 参数顺序；当没有 Page 参数时，在选项之前传递 `undefined`：

```js
await page.waitForFunction(() => window.appReady, undefined, {
  timeout: 10_000,
});
```

```js
// 第一回合：检查并从此输出中选择目标。
const page = task.page("p1");
console.log(await page.snapshot());
```

```js
// 下一个回合：使用上一个输出执行操作，验证，然后准备下一回合。
const page = task.page("p1");
await page.fill("@21", "user@example.com");
await page.click("loc=role:button[name='Sign in']");
await page.waitForSelector("loc=css:#account-home", { state: "visible" });
console.log(await page.snapshot());
```

元素操作接受：

- 快照引用，如 `@21` 或 `ref=21`
- `text=...` 用于页面内容
- `loc=css:`、`loc=role:` 和 `loc=href:` 定位器
- `xpath=...`
- 原始 CSS 选择器

选择器操作需要恰好一个匹配。未加引号的文本规范化空白，忽略大小写，匹配子字符串；引号文本（如 `text="Save changes"`）是精确的，区分大小写。

也接受一个小型 Playwright 兼容选择器子集：`css=...`、终端 `:has-text("...")` 和 `:text-is("...")`、CSS、文本或 href 选择器之后的 `>> nth=N`（`N` 是 `-1` 或非负），以及 `loc=role:...[name*="..."]` 用于可访问名称子字符串。不支持其他 Playwright 选择器语法。

当选择器标识一个包装器时，`focus()` 和 `press()` 可以使用其交互式祖先或唯一的可编辑子代；`fill()` 和 `setInputFiles()` 仅继续到唯一的兼容控件。

`click()`、`fill()`、`hover()` 和 `dragAndDrop()` 自动使用浏览器滚轮输入将其目标置于视图中。不要仅为了使 DOM 目标可操作而预先滚动。

快照节点名称是可访问性角色。现在使用引用，或使用 `loc=...` 再次找到元素。页面更改后，拍摄新的快照。当有用的节点没有引用时，根据其角色、文本或周围上下文构建选择器。CSS 搜索嵌套打开的阴影根。操作首先在选定的文档或框架中使用可操作的匹配项，如果顶层文档没有，则搜索框架。在选定的文档或框架中选择多个可操作的匹配项是模糊的。

通过值、可见标签或零基索引选择选项。字符串匹配值或标签；传递数组用于多选：

```js
await page.selectOption("select[name=month]", { label: "October" });
```

传递 `null` 或 `[]` 清除当前选择。

### 视觉页面：截图、鼠标和键盘

对于画布、富文本、电子表格、地图和其他缺乏有用 DOM 语义的界面，使用截图与鼠标和键盘操作：

```js
const path = await page.screenshot({ path: "/absolute/path/before.png" });
await page.mouse.click(420, 260, { label: "open spreadsheet cell" });
await page.mouse.wheel(0, 600, { label: "scroll project board" });
await page.keyboard.paste("hello\tworld");
console.log({ screenshot: path });
```

使用图像查看工具检查截图。坐标使用 CSS 像素；键盘名称和 `+`-分隔的 chords 遵循 Playwright 语法。使用 `ControlOrMeta` 进行可移植快捷键，并验证结果页面状态。`mouse.wheel()` 在当前鼠标位置执行短滚轮输入动作，并在该动作完成时解析。在每个脚本调用中，在使用它之前移动或点击到预期的可滚动区域。

在 macOS 上，`keyboard.paste()` 发送本地粘贴快捷键，然后恢复用户的剪贴板。当富文本编辑器需要结构化剪贴板内容时，传递 `{ text, html }`；`text` 是纯文本回退。在其他平台上，使用 `keyboard.insertText()` 进行纯文本。

```js
await page.keyboard.paste({
  text: "Name\tStatus",
  html: "<table><tr><td>Name</td><td>Status</td></tr></table>",
});
```

对于富文本编辑器和可编辑网格，在按比例重复之前验证一个小编辑。基于画布的编辑器可能不会通过 DOM 文本或选择器暴露可见内容；使用截图或应用程序特定的可见状态验证那些结果。

### 页面 JavaScript 和 CDP

使用 `page.evaluate()` 进行批量提取或复杂的页面内工作。它接受一个可 JSON 序列化的参数并返回一个可 JSON 序列化的值：

```js
const rows = await page.evaluate(
  ({ selector, limit }) =>
    [...document.querySelectorAll(selector)].slice(0, limit).map((node) => ({
      text: node.textContent?.trim(),
      href: node.querySelector("a")?.href,
    })),
  { selector: "article", limit: 20 },
);
```

`page.evaluate()` 没有超时选项。将长时间工作保持在有界调用中；在安全超时情况下，使用 `executionStopped` 和 `mayHaveLateEffects` 决定是否需要先重新加载或关闭页面进行不安全的后续操作。

首先使用文档中的页面方法。如果包装器缺失或当前页面上的包装器不可靠，使用 `page.cdp()` 作为诊断或控制的较低级别路径。它接受页面、运行时、DOM、网络、输入和类似命令；使用 `task.cdp()` 进行 Target 和浏览器命令。原始 CDP 使引用无效。不要跨回合持久化 `page.targetId`。

## 操作收据、弹窗和对话框

当预期操作将打开新页面时，在操作之前开始等待：

```js
const popupPromise = page.waitForEvent("popup");
await page.click('a[target="_blank"]');
const popupPage = await popupPromise;
await popupPage.waitForLoadState();
```

高级操作也会立即报告观察到的弹窗，作为 `receipt.popups` 中的 `{ label, targetId }`。使用 `task.page(receipt.popups[0].label)` 解析页面并继续；当目的地重要时要等待其 URL。

对于不常见的协议事件工作流，`await page.events()` 返回并清除缓冲的事件数组；它不是一个 EventEmitter。

同步 JavaScript 对话框可能作为 `receipt.dialog` 或在 `page.info()` 中出现。在继续之前处理它：

```js
await page.acceptDialog("prompt response");
// 或：await page.dismissDialog();
```

收据仅描述已分发的操作和立即的弹窗或对话框观察；它不验证结果应用程序状态。

## 文件和请求

使用绝对路径设置现有文件输入：

```js
await page.setInputFiles("input[type=file]", ["/absolute/path/report.pdf"]);
```

如果点击创建了文件输入，在点击之前开始等待：

```js
const chooserPromise = page.waitForFileChooser({ timeout: 10_000 });
await page.click("button.upload");
const chooser = await chooserPromise;
const result = await chooser.setFiles("/absolute/path/report.pdf");
```

由上传触发的 JavaScript 对话框可能作为 `result.dialog` 返回；当存在时，使用上述对话框方法处理它。

对于浏览器下载，在触发操作的之前准备事件，并将返回的工件保存到同一脚本中的绝对路径：

```js
const downloadPromise = page.waitForEvent("download", { timeout: 30_000 });
await page.click("button.download");
const download = await downloadPromise;
console.log({
  url: download.url(),
  suggestedFilename: download.suggestedFilename(),
});
await download.saveAs("/absolute/path/report.pdf");
```

`download.saveAs()` 等待完成并创建缺失的父目录。`download.path()` 返回回合本地的临时文件；`failure()`、`cancel()` 和 `delete()` 管理其生命周期。临时下载文件在 SDK 回合处置时被删除，因此请在脚本结束前调用 `saveAs()`。不要使用原始 CDP 设置全局下载目录；每个下载等待配置并恢复仅针对所处理的页面会话。

`page.fetch()` 在 Page 中运行 `window.fetch()`：相对 URL、cookie 和 service workers 使用该 Page，浏览器 CORS 仍然适用。它返回 `{ ok, status, statusText, url, headers, body }`：

```js
const response = await page.fetch("/api/items", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ limit: 20 }),
  timeout: 10_000,
});
```

保存二进制响应而不将其转换为文本：

```js
await page.fetch("/image.png", { saveAs: "/absolute/path/image.png" });
```

使用标准的 Node.js `fetch()` 进行不需要 Page 浏览器语义的背景请求。

## 用户控制和完成

当用户接管控制或空间不活跃或未分配时停止。不要重试或绕过停止。权限提示、设备选择器和其他浏览器拥有的提示需要用户处理。

当用户必须在浏览器中操作时，调用 `await task.handOff()`，结束回合，并解释他们应该做什么。用户确认后，恢复相同的空间：

```js
const task = await takeOverTaskSpace(7);
const userPage = task.userPage();
```

如果 `userPage` 未被管理，请采用它。仅在当前脚本必须原地等待时使用 `waitForControl()`。仅在用户明确要求时才声明用户拥有的或非活动的空间。首先找到其数字 ID；名称可能重复：

```js
const spaces = await listTaskSpaces();
console.log(spaces.filter((space) => space.ownership === "user"));

const task = await claimTaskSpace(7);
const userPage = task.userPage();
```

当任务成功时，默认使用 `await task.finish({ keep: [] })` 关闭 TaskSpace。调用 `finish()` 恰好一次，并在它解析之前等待，然后报告完成。

保留页面是一个罕见的例外：仅在用户明确要求时，或当结果必须保留在浏览器中供用户查看或继续工作时保留必要的页面。仅访问的页面、搜索结果和中间步骤不需要保持打开。

```js
await task.finish({ keep: [] }); // 默认：不保留 Agent 管理的页面。
await task.finish({ keep: ["p2"] }); // 异常：仅保留结果页面供用户查看。
```

用户创建的未管理标签受保护；如果任何剩余，`keep: []` 不会关闭整个空间。不要在完成时逐个关闭不需要的页面；列出要保留的页面。

仅在任务仍在进行时使用 `page.close()`。当任务因用户控制或错误而停止时，不要调用 `finish()`。

如果最终输出包含 `[ego-browser:notice]`，完成当前浏览器任务，告诉用户有可用的 Ego Lite 更新，并在他们批准后运行 `ego-browser upgrade`。升级后重新阅读此技能。

## 参考

- [安装和连接](references/install.md)
- [API 签名和选项](references/api.md)
- [清除 cookie、缓存和存储](references/clearing-state.md) — 在清除任何 cookie、缓存或存储之前阅读；一些清除会影响到整个浏览器配置文件。
