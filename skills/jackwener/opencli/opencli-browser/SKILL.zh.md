---
name: opencli-browser
description: 当代理需要通过 opencli 驱动真实的 Chrome 窗口时使用——检查页面、填写表单、点击登录流程或按需提取数据。涵盖 selector-first 目标合约、复合表单字段、陈旧引用处理、网络捕获，以及代理原生封装的 CLI 返回内容。不用于编写适配器——请参考 opencli-adapter-author。
---

# opencli-browser

这个 CLI 的第一个读者是一个代理，而不是人类。每个子命令都会返回一个结构化的信封，告诉你具体匹配了什么、匹配的置信度有多高，以及如果没有匹配到该怎么办。依赖这些信封——不要猜测。

这项技能是用于**驱动一个实时浏览器**来完成代理任务。如果你在 `~/.opencli/clis/<site>/` 下构建一个可重用的适配器，请使用 `opencli-adapter-author`。

---

## 前置条件

```bash
opencli doctor
```

直到 `doctor` 变为绿色，其他任何东西都不会工作。典型的失败：Chrome 没有运行、扩展没有安装、1Password / 其他扩展阻止了调试端口。医生输出会告诉你具体是哪个问题。

---

## 会话生命周期

- `opencli browser *` 命令需要在 `browser` 后面立即指定 `<session>` 位置参数。对于多步骤流程，使用相同的会话名称；使用不同的名称来隔离并行的浏览器工作。
- 对于任何多命令或人类控制节奏的浏览器工作流程，使用一个稳定的会话名称。示例：`opencli browser fb-yaya-warmup open https://example.com`，然后重用 `opencli browser fb-yaya-warmup state`、`extract`、`click` 等。
- 所拥有的浏览器会话在调用之间保持标签租约活跃。使用 `opencli browser <session> close` 释放它，或者让空闲超时过期。
- `opencli browser <session> bind` 将你已经打开的 Chrome 标签绑定到该会话。用于登录页面、SSO 流程，或者在你将控制权交给代理之前手动定位的页面。
- `--window foreground|background`（或 `OPENCLI_WINDOW=foreground|background`）选择 OpenCLI 创建/聚焦前景浏览器窗口，还是使用背景浏览器窗口来处理拥有的会话。

### 绑定标签

```bash
opencli browser gmail bind
opencli browser gmail state
opencli browser gmail click "Search"
opencli browser gmail network
opencli browser gmail unbind
```

绑定永远不会拥有用户窗口，也不会关闭用户标签。如果标签被关闭或变得无法调试，它就会失败关闭。切换到不同的真实标签时，重新运行 `opencli browser <session> bind`。

绑定会话允许导航，因为该会话现在表示代理明确拥有该标签。标签变异（`tab new`、`tab select`、`tab close`）仍然阻止绑定会话。当你希望 OpenCLI 管理标签生命周期时，使用拥有的会话。

绑定的会话没有 OpenCLI 空闲关闭计时器；绑定持续到 `unbind`、标签关闭、窗口关闭或守护进程重启。

---

## 心智模型

1. **选择器优先的目标契约。** 每个交互命令（`click`、`type`、`select`、`get text/value/attributes`）都接受一个 `<target>`，它要么是来自 `state`/`find` 的数字引用，要么是 CSS 选择器。使用 `--nth <n>` 来消除多个 CSS 匹配的歧义。
2. **每个信封报告 `matches_n` 和 `match_level`。** `match_level` 是 `exact`、`stable` 或 `reidentified`——CLI 已经帮你拯救了适度的 DOM 漂移，但级别会告诉你应该有多大的信心。
3. **先输出紧凑结果，按需输出完整负载。** `state` 是一个预算感知的快照；`get html --as json` 支持 `--depth/--children-max/--text-max`；`network` 返回形状预览，你可以使用 `--detail <key>` 重新获取单个正文。如果你发出一个巨大的负载，你正在消耗你不需要消耗的上下文。
4. **结构化错误是机器可读的。** 失败时，CLI 会发出 `{error: {code, message, hint?, candidates?}}`。基于 `code` 分支，而不是基于消息字符串。

---

## 严重规则

1. **在行动前始终检查。** 首先运行 `state` 或 `find`。不要跨会话硬编码来自记忆的引用或选择器——索引是针对每个快照的。
2. **优先使用站点适配器，而不是原始浏览器驱动。** 如果 `opencli <site> <command>` 已经涵盖了任务，请首先使用该适配器命令（`opencli facebook notifications`、`opencli reddit read`、`opencli chatgpt model <level>` 等）。仅在存在空白、调试或适配器未暴露的一次性 UI 流程时使用 `opencli browser ...`。
3. **一旦你有了数字引用，优先使用它。** 数字引用因为 CLI 为每个标记的元素生成指纹，所以可以存活轻微的 DOM 变移。手写的 CSS 选择器在网站重新渲染时第一次就会失效。
4. **每次写入后读取 `match_level`。** `exact` = 一切良好。`stable` = 元素仍然相同，但一些软属性漂移——你的操作仍然有效。`reidentified` = 原始引用已消失；CLI 找到了一个唯一的实时元素并重新标记了旧引用；在链式更多写入前，请再次确认你是否击中了正确的元素。
5. **使用 `compound` 字段来处理表单控件。** 不要用正则表达式猜测日期格式，不要两次运行 `state` 来获取完整的 `<select>` 选项列表。复合信封包含格式字符串、最多 50 个完整选项列表、`options_total` 用于溢出，以及 `<input type=file>` 的 `accept`/`multiple`。
6. **验证重要的写入。** 在 `type <target> <text>` 后，运行 `get value <target>`。在 `select` 后，运行 `get value`。自动完成小部件、React 控制输入和掩码字段都会默默地吃掉字符。CLI 无法为你检测到这一点。
7. **页面更改后的 `state` → 行动 → `state`。** 导航、表单提交和 SPA 路由更改会使引用失效。获取一个新的快照。不要重用转换前的引用。
8. **当重新使用新鲜解析的引用时使用 `&&` 链接。** 链式序列在一个 shell 中运行，所以你可以直接将刚刚从输出中读取的引用传递给下一个命令。分离的 shell 调用会保留命名的浏览器会话，但任何 shell 本地变量或从先前命令复制的引用在页面更改后可能会过时。
9. **`eval` 是只读的。** 将 JS 包裹在一个 IIFE 中并返回 JSON。如果你需要*更改*页面，请使用结构化的 `click` / `type` / `select` / `keys` 命令——它们产生结构化输出和指纹，`eval` 不行。
10. **优先使用 `network` 而不是屏幕抓取。** 如果你关心的页面从 JSON API 获取数据，API 几乎总是比抓取渲染的 DOM 更可靠。捕获一次，检查形状，然后 `--detail <key>` 你需要的正文。

---

## 目标契约（`<target>` 用于 click / type / select / get text|value|attributes）

```
<target> ::= <numeric-ref> | <css-selector>
```

- **数字引用**——来自 `state` 或 `find` 的 `[N]` 索引。廉价，对软 DOM 漂移有弹性。
- **CSS 选择器**——`querySelectorAll` 接受的任何内容。在写入操作中必须明确，或者与 `--nth <n>` 配对。

### 成功时的信封

```json
{ "clicked": true, "target": "3", "matches_n": 1, "match_level": "exact" }
```

```json
{ "value": "kalevin@example.com", "matches_n": 1, "match_level": "stable" }
```

### match_level

| level | 含义 | 你应该 |
|-------|-------|--------|
| `exact` | 指纹就绪，标签 + 强 ID 最多只有一个软漂移 | 继续。 |
| `stable` | 标签 + 强 ID 仍然一致，软信号（aria-label、role、text）漂移 | 继续，但如果 *你* 输入/点击的内容重要，请用 `get value` 或 `state` 再次检查。 |
| `reidentified` | 原始引用已消失；一个唯一的实时元素匹配了指纹并被重新标记为旧引用 | 在链式更多写入前，再次确认你是否击中了正确的元素。 |

### 结构化错误代码

基于这些，而不是基于人类消息：

| code | 含义 |
|------|------|
| `not_found` | 数字引用不再在 DOM 中。重新 `state`。 |
| `stale_ref` | 引用存在，但该引用处的元素改变了身份。重新 `state`。 |
| `invalid_selector` | CSS 被 `querySelectorAll` 拒绝。修复选择器。 |
| `selector_not_found` | CSS 匹配 0 个元素。尝试用更松散的选择器 `find`。 |
| `selector_ambiguous` | CSS 匹配 >1 个且没有 `--nth`。添加 `--nth` 或缩小选择器。 |
| `selector_nth_out_of_range` | `--nth` 超出匹配计数。 |
| `option_not_found` | `select` 无法找到匹配该标签/值的选项。错误信封包括 `available: string[]` 的真实选项标签。 |
| `not_a_select` | `select` 被调用在一个非 `<select>` 元素上。 |

错误信封始终包括 `error.code` 和 `error.message`。目标错误（`selector_not_found`、`selector_ambiguous` 等）通常添加 `error.candidates: string[]` 来提供建议选择器。`option_not_found` 添加 `error.available: string[]`。

---

## 命令参考

### 检查

| 命令 | 目的 |
|------|------|
| `browser state` | 快照：带有 `[N]` 引用的文本树、滚动提示、隐藏交互提示、`compounds (N):` 日期/选择/文件引用的侧车。 |
| `browser state --source ax` | 选择性可访问性树快照。在正常 `state` 中难以识别自定义控件、端口或 iframe 内容时使用。AX 引用可以通过角色/名称/nth 恢复陈旧的 React 重新渲染，并且可以路由同源 iframe 引用。跨源 iframe 引用是尽力而为的，因为 Chrome 可能不会向扩展暴露可附加的 OOPIF 目标。 |
| `browser state --compare-sources` | 仅用于指标的 DOM 与 AX 比较决定是否应将 AX 设置为默认值。它打印计数和大小，而不是页面文本，因此对于验证来说更安全。 |
| `browser find --css <sel> [--limit N] [--text-max N]` | 运行 CSS 查询，并为每个匹配返回一个带有 `{nth, ref, tag, role, text, attrs, visible, compound?}` 的条目。为先前快照未标记的匹配分配引用。在你知道选择器时，`state` 的廉价替代方案。 |
| `browser find --role button --name Save` | 语义定位查询。也支持 `--label`、`--text` 和 `--testid`。在具有可访问标签的控件上使用前，使用原始 CSS。 |
| `browser frames` | 列出跨源 iframe 目标。将索引传递给 `--frame` 在 `eval` 上。 |
| `browser screenshot [path]` | 视口 PNG。无路径 → base64 到 stdout。当你只需要结构时，优先使用 `state`。 |
| `browser screenshot --annotate [path]` | 视觉引用映射。刷新 DOM 引用并覆盖可见的 `[N]` 标签，以便截图可以映射回 `browser click <ref>` 目标。用于图标控件、视觉布局、图表或当文本状态不明确时。 |

### 获取（只读）

| 命令 | 返回 |
|------|------|
| `browser get title` | 纯文本 |
| `browser get url` | 纯文本 |
| `browser get text <target> [--nth N]` | `{value, matches_n, match_level}` |
| `browser get value <target> [--nth N]` | `{value, matches_n, match_level}` |
| `browser get attributes <target> [--nth N]` | `{value: {attr: val, ...}, matches_n, match_level}` |
| `browser get text --role option --name Travel` | 语义定位读取，无需先前的 `state` 调用。与 `browser find` 相同的标志。 |
| `browser get html [--selector <css>] [--as html\|json] [--depth N] [--children-max N] [--text-max N] [--max N]` | 原始 HTML，或结构化树。JSON 树节点包含 `{tag, attrs, text, children[], compound?}`。截断通过 `truncated: {depth?, children_dropped?, text_truncated?}` 报告。 |

### 交互

| 命令 | 备注 |
|------|------|
| `browser click <target> [--nth N]` | 返回 `{clicked, target, matches_n, match_level}`。 |
| `browser click --role button --name Submit` | 语义点击。写入操作需要一个唯一匹配；歧义定位器会返回候选者，而不是点击第一个匹配。 |
| `browser hover [target] [--role R --name N] [--nth N]` | 将鼠标移动到元素上。用于在获取 `state` 或点击子菜单项之前悬停菜单/工具提示。返回 `{hovered, target, matches_n, match_level}`。 |
| `browser focus [target] [--role R --name N] [--nth N]` | 聚焦元素而不输入。在 `keys` 之前或当页面对焦点/模糊做出反应时很有用。返回 `{focused, target, matches_n, match_level}`。 |
| `browser dblclick [target] [--role R --name N] [--nth N]` | 当可用时，通过原生鼠标事件双击元素。返回 `{dblclicked, target, matches_n, match_level}`。 |
| `browser check [target] [--role R --name N] [--nth N]` | 确保复选框/单选按钮/aria-checked 控件被选中。返回 `{checked, changed, target, matches_n, match_level, kind}`。在目标状态重要时，优先于此盲 `click`。 |
| `browser uncheck [target] [--role R --name N] [--nth N]` | 确保复选框/aria-checked 控件未被选中。单选按钮不能直接取消选中；选择该组中的另一个单选按钮。 |
| `browser upload [target] <file...> [--role R --name N] [--nth N]` | 通过 CDP 将本地文件路径附加到 `input[type=file]`。使用语义标志时，省略 `target` 并将文件作为位置参数传递。返回 `{uploaded, files, file_names, target, matches_n, match_level, multiple?, accept?}`。 |
| `browser drag [source] [target] [--from-role R --from-name N] [--to-role R --to-name N] [--from-nth N] [--to-nth N]` | 基于鼠标从解析元素中心拖动到另一个解析元素中心。适用于鼠标监听拖动库；原生 HTML5 `dataTransfer` 放置可能需要特定站点的回退。返回 `{dragged, source, target, source_matches_n, target_matches_n, ...}`。 |
| `browser type [target] <text> [--role R --name N] [--nth N]` | 点击后输入。使用语义标志时，省略 `target` 并将文本作为唯一位置参数传递。返回 `{typed, text, target, matches_n, match_level, autocomplete}`。`autocomplete: true` 意味着在输入后出现了一个组合框/数据列表弹出——你几乎总是需要 `keys Enter` 或对建议进行后续 `click` 来提交值。 |
| `browser fill [target] <text> [--role R --name N] [--nth N]` | 输入、textarea 和 contenteditable 目标的精确替换。使用语义标志时，省略 `target` 并将文本作为唯一位置参数传递。返回 `{filled, verified, text, actual, matches_n, match_level}`。当你需要设置原始文本并验证时，使用此命令，而不是键盘/自动完成行为。管道表单支持 `{ fill: { ref, text, submit: true } }`。 |
| `browser select [target] <option> [--role R --name N] [--nth N]` | 首先通过标签匹配原生 `<select>` 选项，然后通过值。使用语义标志时，省略 `target` 并将选项作为唯一位置参数传递。使用 `find`/`state` 中的 `compound` 来查看确切可用的标签。 |
| `browser keys <key>` | `Enter`、`Escape`、`Tab`、`Control+a` 等。针对当前聚焦的元素运行。 |
| `browser scroll <direction> [--amount px]` | `up` / `down`。默认量 `500`。 |

### 等待

```bash
browser wait selector "<css>" [--timeout ms]    # 等待选择器匹配
browser wait text "<substring>" [--timeout ms]  # 等待文本出现
browser wait download [pattern] [--timeout ms]  # 等待 Chrome 下载，其文件名/URL/mime 包含 pattern
browser wait time <seconds>                     # 硬休眠，最后手段
```

默认超时 `10000` ms。SPA 路由、登录重定向和惰性加载列表在 `state`/`get` 之前需要 `wait`。

`browser wait download` 需要 Browser Bridge 扩展 1.0.8+，因为它使用 Chrome 的下载生命周期 API。尽可能传递狭窄的文件名或 URL 子字符串，例如 `receipt.pdf`；空模式等待超时窗口中的下一个/最近下载。该命令在成功时返回 `{downloaded, filename, url, state, elapsedMs}`，在超时/失败时返回 JSON 错误信封。

### 提取

- **`web read --url <url>`** — 任意页面的单次 Markdown 阅读器。它默认展开同源的 iframe，因此旧 iframe-shell 网站的体验比仅抓取顶层文档更好。当完整性比 Markdown 噪声更重要时，使用 `--frames all-same-origin`。对于 AJAX shell 页面，使用 `opencli web read --url <url> --wait-for "<selector>" --wait-until networkidle --diagnose`；诊断信息显示 iframe URL、空容器和类似 API 的 XHR。如果需要的是表格/API 数据，切换到 `browser network` 或专用适配器，而不是依赖 Markdown。
- **`browser eval <js> [--frame N]`** — 在页面（或通过 `--frame` 在跨源 iframe 中）运行表达式。用 IIFE 包裹并返回 JSON。只读：没有 `document.forms[0].submit()`，没有点击，没有导航。如果结果是字符串，stdout 是原始字符串；否则它是 JSON。
- **`browser extract [--selector <css>] [--chunk-size N] [--start N]`** — 长格式内容的 Markdown 提取，带有续接游标。返回 `{url, title, selector, total_chars, chunk_size, start, end, next_start_char, content}`。循环 `next_start_char` 直到它是 `null`。如果没有传递 `--selector`，会自动范围到 `<main>`/`<article>`/`<body>`。

### 网络

```bash
browser network                        # 形状预览 + 缓存键列表
browser network --detail <key>         # 缓存条目的完整正文
browser network --filter "field1,field2"  # 仅保留正文形状包含所有字段作为路径段条目的条目
browser network --all                  # 包括静态资源（通常是噪声）
browser network --raw                  # 完整正文内联 — 大；请谨慎使用
browser network --ttl <ms>             # 缓存 TTL（默认 24 小时）
```

条目列表看起来像 `{key, method, status, url, ct, size, shape, body_truncated?}`。详细信息信封是 `{key, url, method, status, ct, size, shape, body, body_truncated?, body_full_size?, body_truncation_reason}`。缓存位于 `~/.opencli/cache/browser-network/`，因此可以重新检查而无需重新触发请求。

默认输出保留 JSON/XML/plain-text 和 JS-like API 响应，然后通过 URL 删除明显的静态资源和遥测。如果预期的端点丢失，运行一次 `browser network --all` 并检查是否有不寻常的内容类型或 URL 过滤器隐藏了它。

### 标签和会话

| 命令 | 目的 |
|-------|-------|
| `browser tab list` | `{index, page, url, title, active}` 的 JSON 数组。`page` 字符串是传递给 `tab select` / `tab close` 的标签标识，或传递给任何子命令上的 `--tab <targetId>`。 (`--tab` 的占位符是历史性的 — 值始终是 `page`。 |
| `browser tab new [url]` | 打开一个新标签。打印新的 `page` 字符串。 |
| `browser tab select [targetId]` | 将一个标签设为默认。所有子命令都接受 `--tab <targetId>` 来定位一个标签而不更改默认值。 |
| `browser tab close [targetId]` | 通过 `page` 关闭。 |
| `browser back` | 活动标签上的历史后退。 |
| `browser close` | 完成时释放当前拥有的浏览器会话。 |
| `browser <session> bind` | 将当前 Chrome 标签绑定到命名的浏览器会话。 |
| `browser <session> unbind` | 在不关闭用户标签/窗口的情况下分离命名的绑定会话。 |

---

## 复合表单控件

每个日期/时间、选择和文件输入都带有 `compound` 字段。使用它 — 不要使用正则表达式属性。

### 日期系列

```json
{
  "control": "date",
  "format": "YYYY-MM-DD",
  "current": "2026-04-21",
  "min": "2026-01-01",
  "max": "2026-12-31"
}
```

`control` 是 `date | time | datetime-local | month | week` 之一。`format` 是一个具体的模板字符串 — 使用该格式输入字段，或如果网站将原生输入包裹在自定义小部件中，则通过标签选择。

### 选择

```json
{
  "control": "select",
  "multiple": false,
  "current": "United States",
  "options": [
    { "label": "United States", "value": "us", "selected": true },
    { "label": "Canada", "value": "ca" }
  ],
  "options_total": 137
}
```

`options[]` 最多 50 个条目。**`current` 总是正确的** 即使选中的选项超出上限 — 它是通过扫描每个选项计算的，而不是从截断的列表中获取的。如果 `options_total > options.length` 并且你需要不在 `options[]` 中的选项，直接调用 `browser select <target> "<label>"` — CLI 匹配的是实时 DOM，而不是截断的列表。

### 文件

```json
{
  "control": "file",
  "multiple": true,
  "current": ["report.pdf", "cover.png"],
  "accept": "application/pdf,image/*"
}
```

不要编造文件路径。上传通过正常的点击流程完成 — 告诉用户要上传时，请尊重 `accept`。

### 复合控件出现的位置

- `browser find --css <sel>` 条目：每个匹配项上内联。
- `browser get html --as json` 树节点：匹配节点上内联。
- `browser state` 快照：在 `compounds (N):` 侧边栏中按数字引用键入，因此您可以一目了然地知道哪些 `[N]` 条目具有丰富的元数据。

---

## 成本指南

考虑每次调用的有效负载大小。预算的存在是有原因的。

| 命令 | 大致成本 | 使用时机 |
|-------|-----------|-------------|
| `state` | 中等（受内部预算限制） | 任何页面的第一次调用、每次导航后、需要引用时。 |
| `find --css <sel>` | 小 | 您已经知道选择器 — 一个查询，紧凑的条目。 |
| `get title` / `get url` | 微小 | 步骤之间的基本检查。 |
| `get text/value/attributes` | 每次调用微小 | 验证一个特定字段。 |
| `get html` (原始) | 可能很大 | 避免在无限制页面上使用。始终与 `--selector` 和预算配对。 |
| `get html --as json --depth 3 --children-max 20` | 中等 | 当您需要推理结构而不是特定字段时。 |
| `screenshot` | 大 | 仅当页面是视觉的（验证码、图表）。优先使用 `state`。 |
| `extract` | 每个块中等 | 长格式阅读。通过 `next_start_char` 循环。 |
| `network` (默认) | 小 | 首次查看 API。 |
| `network --detail <key>` | 变化 | 拉取一个正文。 |
| `network --raw` | 巨大 | 仅在 `--filter` 窄化候选集后。 |
| `eval "JSON.stringify(...)"` | 受控 | 当以上都不适用时的目标提取。 |

经验法则：**每页转换一个 `state`，每个后续查询一个 `find`，每个操作一个 `get`/`click`/`type`。** 如果您的计划涉及每页超过 10 个调用，您可能是在抓取而不是交互 — 考虑 `extract` 或 `network`。

---

## 链接规则

**良好 — 一个 shell，实时会话：**

```bash
opencli browser hn open "https://news.ycombinator.com" \
  && opencli browser hn state \
  && opencli browser hn click 3
```

**不良 — 每一行都是一个全新的 shell，调用 1 的引用在调用 2 运行时已经丢失。**（只有当您依赖 shell 范围状态时才是一个问题；浏览器引用本身在页面中持续存在，但交错无关的 shell 会导致竞争。）当步骤打算原子化时，请使用 `&&`。

**永远** 不要在没有 `wait` 的情况下链接写入操作然后立即 `state`，如果该操作导致网络往返 — 您将快照预响应的 DOM，并基于过时的数据做出错误决策。

---

## 配方

### 填写登录表单

```bash
opencli browser login open "https://example.com/login"
opencli browser login state                          # 找到 [N] 用于电子邮件、密码、提交
opencli browser login type 4 "me@example.com"
opencli browser login type 5 "hunter2"
opencli browser login get value 4                    # 验证（自动完成可以吃字符）
opencli browser login click 6                        # 提交
opencli browser login wait selector "[data-testid=account-menu]" --timeout 15000
opencli browser login state                          # 在登录页面上的新鲜引用
```

### 从长下拉列表中选择

```bash
opencli browser form state                          # 侧边栏显示 [12] <select name=country>
opencli browser form find --css "select[name=country]"
# compound.options_total 是 137，但 compound.current 是 "" — 未选中。
opencli browser form select 12 "Uruguay"
opencli browser form get value 12                   # { value: "uy", match_level: "exact" }
```

### 从自定义 React 下拉列表中选择

用于 Radix、shadcn、Material UI、Mercury 风格的分类字段和其他不是原生 `<select>` 的控件。

```bash
opencli browser mercury state                          # 找到分类触发器引用
# 如果触发器/选项不明确，使用 AX：
opencli browser mercury state --source ax              # 查找 combobox/button/listbox/option 名称
opencli browser mercury click 7                        # 点击分类触发器
opencli browser mercury state --source ax              # 在门户/列表框打开后刷新引用
opencli browser mercury click 12                       # 点击选项
opencli browser mercury get text 7                     # 验证可见的选中标签
```

不要在这些小部件上使用 `browser select`。`browser select` 仅用于原生 `<select>` 元素。自定义下拉列表应使用 `state -> click trigger -> state -> click option -> verify` 驱动。

### 比较 DOM 与 AX 观察

在决定页面上的 AX 引用是否更好时，收集不共享页面内容的指标：

```bash
opencli browser compare state --compare-sources
```

报告 `sources.dom.refs`、`sources.ax.refs`、`frame_sections`、`approx_tokens`、`elapsed_ms` 和任何按来源的 `error`。在争论 AX 应该成为某个网站的默认值之前使用此功能。

### 通过网络而不是 DOM 抓取列表

```bash
opencli browser hn open "https://news.ycombinator.com"
opencli browser hn network --filter "title,score"
# -> 找到 /topstories 条目，记下其键
opencli browser hn network --detail topstories-a1b2
```

### 分块读取长文章

```bash
opencli browser article open "https://blog.example.com/long-post"
opencli browser article extract --chunk-size 8000
# -> content + next_start_char: 8000
opencli browser article extract --start 8000 --chunk-size 8000
# ...直到 next_start_char 为 null
```

### 跨源 iframe

```bash
opencli browser checkout frames
# -> [{"index": 0, "url": "https://checkout.stripe.com/...", ...}]
opencli browser checkout eval "(() => document.querySelector('input[name=cardnumber]')?.value)()" --frame 0
```

`browser state --source ax` 可能会省略跨源 iframe 内容或在 Chrome 没有向扩展暴露可附加的 OOPIF 目标时失败以路由操作到它们。在这种情况下，使用 `browser frames` + `browser eval --frame`、正常的 DOM `state`，或在可能的情况下直接导航/绑定到 iframe URL。

---

## 陷阱

- **不要通过 `eval "document.forms[0].submit()"` 提交表单** — 现代网站通过 JS 处理程序拦截并静默丢弃调用。要么通过提交按钮的引用 `click`，或者（如果您知道 GET URL）直接 `open` 它。
- **不要跨页面转换重用引用。** `wait` 新状态，然后重新 `state`。旧的引用要么 404，要么（更糟）`reidentify` 到新页面上形状相似的元素。
- **`match_level: reidentified` 是一个警告，不是一个错误。** 操作已通过，但如果您在继续之前依赖 5 个更多写入操作都依赖于它是正确的元素，请使用 `get text` 或 `get value` 进行验证。
- **预算感知命令静默限制。** `get html --as json` 使用默认预算将返回 `truncated: {...}`。如果您的下游逻辑需要整个子树，请提高 `--depth` / `--children-max` 或收紧选择器。
- **`autocomplete: true` 在 `type` 响应上不是一个错误。** 它意味着一个建议弹出窗口是打开的，而您的值尚未提交。通常 `keys Enter` 接受第一个建议，或者 `click` 您想要的那个。
- **`network --filter` 是路径段的 AND 语义。** `--filter "title,score"` 保留正文形状包含 *两者* `title` 和 `score` 作为路径段条目的条目，在任何深度。它不是正则表达式。
- **屏幕截图是给人类的，不是给代理的。** 除非页面确实是视觉的（验证码、图表），否则使用 `state` + `find`。屏幕截图消耗 token，并且很少为代理可以采取的行动增加信号。

---

## 故障排除

| 症状 | 解决方法 |
|---------|-----|
| `opencli doctor` 红色： "Browser not connected" | 使用 `--remote-debugging-port=9222` 启动 Chrome，或从 [Chrome Web Store](https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk) 安装扩展。 |
| `attach failed: chrome-extension://...` | 暂时禁用 1Password / 其他 CDP 贪婪扩展。 |
| `selector_not_found` 在 `state` 后立即出现 | 页面已变异。 `wait selector "..."` 然后重试。 |
| `stale_ref` 在每个命令中跨出现 | 您正在重用来自先前页面的引用。重新 `state`。 |
| `click` 成功但什么也没发生 | 元素可能是装饰性包装器，窃取了对实际目标的点击。使用更窄的选择器 `find --css "..."` 并在内部元素上重试。 |
| `type` 看起来完成但值不正确 | 自动完成、掩码输入或 React 控制重新渲染。使用 `get value` 验证。添加 `keys Enter` 或重新输入。 |
| 巨大的 `get html` 输出 | 传递 `--selector` + `--as json --depth 3 --children-max 20 --text-max 200`。 |
| 网络缓存似乎已过时 | 提高 `--ttl` 下，或让它过期。缓存位于 `~/.opencli/cache/browser-network/`。 |

---

## 参见

- `opencli-adapter-author` — 将您刚刚发现的转换为可重用的 `~/.opencli/clis/<site>/<command>.js`。
- `opencli-autofix` — 当现有适配器损坏时，此技能将您通过 `--trace retain-on-failure` 证据并提交修复。
