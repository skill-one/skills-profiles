# opencli-browser

这个CLI的第一个读者是一个代理，而不是人类。每个子命令都会返回一个结构化的信封，告诉你确切匹配了什么，匹配的置信度如何，以及如果没有匹配应该做什么。依赖这些信封——不要猜测。

这项技能用于**驱动一个实时浏览器**来完成代理任务。如果你在`~/.opencli/clis/<site>/`下构建一个可重用的适配器，请使用`opencli-adapter-author`。

---

## 前置条件

```bash
opencli doctor
```

直到`doctor`变为绿色，否则其他任何东西都不会工作。典型的失败：Chrome未运行，扩展未安装，1Password/其他扩展阻止了调试端口。医生输出会告诉你哪个。

---

## 会话生命周期

- `opencli browser *`命令需要在`browser`之后立即指定`<session>`占位符。对于多步骤流程，使用相同的会话名称；使用不同的名称来隔离并行的浏览器工作。
- 使用一个稳定的会话名称来执行任何多命令或人类节奏的浏览器工作流程。示例：`opencli browser fb-yaya-warmup open https://example.com`，然后重用`opencli browser fb-yaya-warmup state`、`extract`、`click`等。
- 拥有的浏览器会话在调用之间保持一个标签租约活跃。使用`opencli browser <session> close`释放它，或者让空闲超时过期。
- `opencli browser <session> bind`将你已经打开的Chrome标签绑定到该会话。用于登录页面、SSO流程或在你手动定位后将控制权交给代理的页面。
- `--window foreground|background`（或`OPENCLI_WINDOW=foreground|background`）选择OpenCLI是创建/聚焦前台浏览器窗口还是使用后台浏览器窗口来执行拥有的会话。

### 绑定标签

```bash
opencli browser gmail bind
opencli browser gmail state
opencli browser gmail click "Search"
opencli browser gmail network
opencli browser gmail unbind
```

绑定永远不会拥有用户的窗口，也不会关闭用户的标签。如果标签被关闭或变为不可调试，它将失败关闭。当你切换到不同的真实标签时，重新运行`opencli browser <session> bind`。

允许在绑定的会话上进行导航，因为该会话现在表示代理明确拥有该标签。标签变异（`tab new`、`tab select`、`tab close`）仍然阻止绑定的会话。当你希望OpenCLI管理标签生命周期时，使用拥有的会话。

绑定的会话没有OpenCLI空闲关闭计时器；绑定持续到`unbind`、标签关闭、窗口关闭或守护进程重启。

---

## 心智模型

1. **选择器优先的目标合同。** 每个交互命令（`click`、`type`、`select`、`get text/value/attributes`）都接受一个`<target>`，它要么是来自`state`/`find`的数字引用，要么是CSS选择器。使用`--nth <n>`来消除多个CSS匹配的歧义。
2. **每个信封报告`matches_n`和`match_level`。** `match_level`是`exact`、`stable`或`reidentified`——CLI已经拯救了适度的DOM漂移，但级别告诉你要多自信。
3. **首先输出紧凑，按需输出完整负载。** `state`是一个预算感知的快照；`get html --as json`支持`--depth/--children-max/--text-max`；`network`返回形状预览，你可以使用`--detail <key>`重新获取单个正文。如果你发出巨大的负载，你正在燃烧你不需要燃烧的上下文。
4. **结构化错误是机器可读的。** 在失败时，CLI会发出`{error: {code, message, hint?, candidates?}}`。基于`code`分支，而不是基于消息字符串。

---

## 关键规则

1. **在行动之前始终检查。** 首先运行`state`或`find`。永远不要跨会话从记忆中硬编码引用或选择器——索引是针对每个快照的。
2. **优先使用站点适配器，而不是原始浏览器驱动。** 如果`opencli <site> <command>`已经涵盖了任务，请首先使用该适配器命令（`opencli facebook notifications`、`opencli reddit read`、`opencli chatgpt model <level>`等）。仅当适配器不暴露一次性UI流程时，才使用`opencli browser ...`。
3. **一旦你有了数字引用，就优先使用它。** 数字引用因为CLI为每个标记的元素生成指纹，所以可以存活轻微的DOM漂移。手写的CSS选择器在站点重新渲染时第一次就会失效。
4. **每次写入后都要读取`match_level`。** `exact` = 一切顺利。`stable` = 元素相同，但一些软属性漂移——你的操作仍然适用。`reidentified` = 原始引用已消失，CLI找到了一个唯一的替代元素；再次检查你是否击中了正确的元素。
5. **使用`compound`字段来处理表单控件。** 不要正则猜测日期格式，不要两次运行`state`来获取完整的`<select>`选项列表。复合信封包含格式字符串、最多50个完整选项列表、`options_total`用于溢出，以及`<input type=file>`的`accept`/`multiple`。
6. **验证重要的写入。** 在`type <target> <text>`之后，运行`get value <target>`。在`select`之后，运行`get value`。自动完成小部件、React受控输入和掩码字段都会默默地吃掉字符。CLI无法为你检测到这一点。
7. **页面更改后的`state` → 行动 → `state`。** 导航、表单提交和SPA路由更改会使引用失效。获取一个新的快照。不要重用转换前的引用。
8. **当重新使用新鲜解析的引用时，使用`&&`进行链接。链接序列在一个shell中运行，所以你可以将上一条命令从输出中直接传递到下一条命令。分离的shell调用会保留命名的浏览器会话，但任何shell本地变量或从上一条命令复制的引用在页面更改后都可能过时。
9. **`eval`是只读的。** 将JS包装在IIFE中并返回JSON。如果你需要更改页面，请使用结构化的`click` / `type` / `select` / `keys`命令——它们生成结构化输出和指纹，`eval`不会。
10. **优先使用`network`而不是屏幕抓取。** 如果你关心的页面从JSON API获取数据，API几乎总是比抓取渲染的DOM更可靠。捕获一次，检查形状，然后使用`--detail <key>`重新获取你需要的正文。如果你发出巨大的负载，你正在燃烧你不需要燃烧的上下文。

---

## 站点地图

如果`browser open`或`browser analyze`返回`sitemap.available: true`，在继续多步骤站点流程之前切换到`opencli-browser-sitemap`。站点地图是页面、操作、工作流程、API和陷阱的先验上下文；它不是事实。如果浏览器状态与站点地图不一致，请通过`opencli-sitemap-author`信任浏览器并将站点地图标记为过时。

---

## 目标合同（`<target>`用于click / type / select / get text|value|attributes）

```
<target> ::= <numeric-ref> | <css-selector>
```

- **数字引用**——来自`state`或`find`的`[N]`索引。便宜，对软DOM漂移有弹性。
- **CSS选择器**——`querySelectorAll`接受任何内容。在写入操作上必须是不明确的，或者与`--nth <n>`配对。

### 成功时的信封

```json
{ "clicked": true, "target": "3", "matches_n": 1, "match_level": "exact" }
```

```json
{ "value": "kalevin@example.com", "matches_n": 1, "match_level": "stable" }
```

### match_level

| level | meaning | you should |
|-------|---------|------------|
| `exact` | Fingerprint agreed on tag + strong IDs with at most one soft drift | Proceed. |
| `stable` | Tag + strong IDs still agree, soft signals (aria-label, role, text) drifted | Proceed, but if *what* you typed/clicked matters, re-check with `get value` or `state`. |
| `reidentified` | Original ref was gone; a unique live element matched the fingerprint and was re-tagged with the old ref | Double-check you hit the right element before chaining more writes. |

### 结构化错误代码

基于这些，而不是基于人类消息：

| code | meaning |
|------|---------|
| `not_found` | Numeric ref no longer exists in the DOM. Re-`state`. |
| `stale_ref` | Ref exists but the element at that ref changed identity. Re-`state`. |
| `invalid_selector` | CSS was rejected by `querySelectorAll`. Fix the selector. |
| `selector_not_found` | CSS matches 0 elements. Try `find` with a looser selector. |
| `selector_ambiguous` | CSS matches >1 and no `--nth`. Add `--nth` or narrow the selector. |
| `selector_nth_out_of_range` | `--nth` beyond match count. |
| `option_not_found` | `select` couldn't find an option matching that label/value. Error envelope includes `available: string[]` of the real option labels. |
| `not_a_select` | `select` was called on a non-`<select>` element. |

错误信封始终包括`error.code`和`error.message`。目标错误（`selector_not_found`、`selector_ambiguous`等）通常添加`error.candidates: string[]`以提供建议的选择器。`option_not_found`添加`error.available: string[]`。

---

## 命令参考

### 检查

| command | purpose |
|---------|---------|
| `browser state` | 快照：带有`[N]`引用的文本树，滚动提示，隐藏交互提示，`compounds (N):`用于日期/选择/文件引用的侧车。 |
| `browser state --source ax` | 选择性访问性树快照。当自定义控件、端口或iframe内容难以在正常`state`中识别时使用。AX引用可以通过角色/名称/nth恢复陈旧的React重新渲染，并且可以路由同源的iframe引用。跨源iframe引用的最佳尝试是因为Chrome可能不会向扩展程序暴露可附加的OOPIF目标。 |
| `browser state --compare-sources` | 仅用于指标DOM与AX比较，以决定是否AX应成为默认值。它打印计数和大小，而不是页面文本，因此它更安全地用于验证。 |
| `browser find --css <sel> [--limit N] [--text-max N]` | 运行CSS查询，并为每个匹配项返回一个包含`{nth, ref, tag, role, text, attrs, visible, compound?}`的条目。为快照未标记的匹配项分配引用。当您已经知道选择器时，这是`state`的廉价替代方案。 |
| `browser find --role button --name Save` | 语义定位查询。还支持`--label`、`--text`和`--testid`。在您使用原始CSS之前使用它，当控件具有可访问标签时。 |
| `browser frames` | 列出跨源iframe目标。将索引传递给`--frame`在`eval`上。 |
| `browser screenshot [path]` | 视口PNG。没有路径→ base64到stdout。当您只需要结构时，优先使用`state`。 |
| `browser screenshot --annotate [path]` | 视觉引用映射。刷新DOM引用，并在截图上叠加可见的`[N]`标签，以便截图可以映射回`browser click <ref>`目标。用于图标控件、视觉布局、图表或当文本状态不明确时。 |

### 获取（只读）

| command | returns |
|---------|---------|
| `browser get title` | plain text |
| `browser get url` | plain text |
| `browser get text <target> [--nth N]` | `{value, matches_n, match_level}` |
| `browser get value <target> [--nth N]` | `{value, matches_n, match_level}` |
| `browser get attributes <target> [--nth N]` | `{value: {attr: val, ...}, matches_n, match_level}` |
| `browser get text --role option --name Travel` | 无需先`state`调用的语义定位读取。与`browser find`具有相同的标志。 |
| `browser get html [--selector <css>] [--as html\|json] [--depth N] [--children-max N] [--text-max N] [--max N]` | 原始HTML，或结构化树。JSON树节点包含`{tag, attrs, text, children[], compound?}`。截断通过`truncated: {depth?, children_dropped?, text_truncated?}`报告。 |

### 交互

| command | notes |
|---------|-------|
| `browser click <target> [--nth N]` | 返回`{clicked, target, matches_n, match_level}`。 |
| `browser click --role button --name Submit` | 写入操作需要一个唯一的匹配；歧义定位器会返回候选者而不是点击第一个匹配项。 |
| `browser hover [target] [--role R --name N] [--nth N]` | 将鼠标移动到元素上。用于在获取`state`或点击子菜单项之前悬停菜单/工具提示。返回`{hovered, target, matches_n, match_level}`。 |
| `browser focus [target] [--role R --name N] [--nth N]` | 在不键入的情况下聚焦元素。在`keys`之前或当页面对焦点/模糊做出反应时很有用。返回`{focused, target, matches_n, match_level}`。 |
| `browser dblclick [target] [--role R --name N] [--nth N]` | 当可用时，通过原生鼠标事件双击元素。返回`{dblclicked, target, matches_n, match_level}`。 |
| `browser check [target] [--role R --name N] [--nth N]` | 确保复选框/单选按钮/aria-checked控件被选中。返回`{checked, changed, target, matches_n, match_level, kind}`。在目标状态很重要时，优先使用此命令而不是盲目的`click`。 |
| `browser uncheck [target] [--role R --name N] [--nth N]` | 确保复选框/aria-checked控件未被选中。单选按钮不能直接取消选中；选择该组中的另一个单选按钮。 |
| `browser upload [target] <file...> [--role R --name N] [--nth N]` | 通过CDP将本地文件路径附加到`input[type=file]`。使用语义标志时，省略`target`并将文件作为位置参数传递。返回`{uploaded, files, file_names, target, matches_n, match_level, multiple?, accept?}`。 |
| `browser drag [source] [target] [--from-role R --from-name N] [--to-role R --to-name N] [--from-nth N] [--to-nth N]` | 基于鼠标从一个解析的元素中心拖动到另一个元素。适用于鼠标监听拖动库；原生HTML5 `dataTransfer`放下可能需要特定站点的回退。返回`{dragged, source, target, source_matches_n, target_matches_n, ...}`。 |
| `browser type [target] <text> [--role R --name N] [--nth N]` | 点击后键入。使用语义标志时，省略`target`并将文本作为唯一的位置参数传递。返回`{typed, text, target, matches_n, match_level, autocomplete}`。 `autocomplete: true`意味着一个组合框/数据列表弹出窗口在键入后出现——你几乎总是需要`keys Enter`或后续`click`在建议上提交值。 |
| `browser fill [target] <text> [--role R --name N] [--nth N]` | 输入、textarea和contenteditable目标的精确替换。使用语义标志时，省略`target`并将文本作为唯一的位置参数传递。返回`{filled, verified, text, actual, matches_n, match_level}`。使用此命令时，你需要原始文本设置和验证，而不是键盘/自动完成行为。表单管道支持`{ fill: { ref, text, submit: true } }`。 |
| `browser select [target] <option> [--role R --name N] [--nth N]` | 通过标签首先匹配原生`<select>`选项，然后通过值。使用语义标志时，省略`target`并将选项作为唯一的位置参数传递。使用`find`/`state`中的`compound`来查看可用的确切标签。 |
| `browser keys <key>` | `Enter`、`Escape`、`Tab`、`Control+a`等。针对当前聚焦的元素运行。 |
| `browser scroll <direction> [--amount px]` | `up` / `down`。默认金额`500`。 |

### 等待

```bash
browser wait selector "<css>" [--timeout ms]    # 等待选择器匹配
browser wait text "<substring>" [--timeout ms]  # 等待文本出现
browser wait download [pattern] [--timeout ms]  # 等待Chrome下载，其文件名/URL/mime包含模式
browser wait time <seconds>                     # 硬睡眠，最后手段
```

默认超时`10000` ms。SPA路由、登录重定向和惰性加载列表需要在导航、表单提交和SPA路由更改后运行`wait`，因为它们使引用失效。`browser wait download`需要浏览器桥接扩展1.0.8+，因为它使用Chrome的下载生命周期API。尽可能传递狭窄的文件名或URL子字符串，例如`receipt.pdf`；当无法提供时，空模式等待超时窗口中的下一个/最近的下载。该命令在成功时返回`{downloaded, filename, url, state, elapsedMs}`，在超时/失败时返回JSON错误信封。

### 提取

- **`web read --url <url>`** — 一次性Markdown阅读器，用于任意页面。它默认扩展相关的同源iframe，因此旧iframe-shell站点比仅抓取顶层文档的站点工作得更好。对于AJAX shell页面，使用`opencli web read --url <url> --wait-for "<selector>" --wait-until networkidle --diagnose`；诊断显示iframe URL、空容器和API样式的XHR。如果需要的是表格/API数据，切换到`browser network`或专用适配器，而不是依赖Markdown。
- **`browser eval <js> [--frame N]`** — 在页面（或通过`--frame`在跨源iframe中）运行表达式。将其包装在IIFE中并返回JSON。只读：没有`document.forms[0].submit()`、没有点击、没有导航。如果结果是字符串，stdout是原始字符串；否则它是JSON。
- **`browser extract [--selector <css>] [--chunk-size N] [--start N]`** — 长格式内容的Markdown提取，带有连续光标。返回`{url, title, selector, total_chars, chunk_size, start, end, next_start_char, content}`。循环`next_start_char`直到它为`null`。如果你不传递`--selector`，它会自动范围到`<main>`/`<article>`/`<body>`，如果你传递`--selector`。

### 网络

```bash
browser network                        # 形状预览 + 缓存键列表
browser network --detail <key>         # 缓存的一个完整正文
browser network --filter "field1,field2"  # 仅保留正文形状包含所有字段作为路径段的所有条目
browser network --all                  # 包括静态资源（通常是噪音）
browser network --raw                  # 完整正文内联——很大；谨慎使用
browser network --ttl <ms>             # 缓存TTL（默认24小时）
```

列表条目看起来像`{key, method, status, url, ct, size, shape, body_truncated?}`。详细信封是`{key, url, method, status, ct, size, shape, body, body_truncated?, body_full_size?, body_truncation_reason}`。缓存存储在`~/.opencli/cache/browser-network/`中，因此你可以重新检查而不需要重新触发请求。

默认输出保留JSON/XML/plain-text和JS样式的API响应，然后通过URL删除明显的静态资产和遥测。如果预期的端点缺失，运行`browser network --all`一次，并检查是否异常的内容类型或URL过滤器隐藏了它。

### 标签和会话

| command | purpose |
|---------|---------|
| `browser tab list` | JSON数组，包含`{index, page, url, title, active}`。`page`字符串是你可以将其作为`<targetId>`传递给`tab select` / `tab close`的标签身份，或者传递给任何子命令上的`--tab <targetId>`。 (`--tab`的占位符是历史的——值始终是`page`。) |
| `browser tab new [url]` | 打开一个新标签。打印新的`page`字符串。 |
| `browser tab select [targetId]` | 使一个标签成为默认的。所有子命令都可以接受`--tab <targetId>`来定位一个标签，而无需更改默认值。 |
| `browser tab close [targetId]` | 通过`page`关闭。 |
| `browser back` | 活动标签上的历史后退。 |
| `browser close` | 完成时释放当前拥有的浏览器会话。 |
| `browser <session> bind` | 将当前Chrome标签绑定到命名的浏览器会话。 |
| `browser <session> unbind` | 无需关闭用户标签/窗口即可分离命名的绑定会话。 |

---

## 复合表单控件

每个日期/时间、选择和文件输入都带有`compound`字段。使用它——不要正则匹配属性。

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

`control`是`date | time | datetime-local | month | week`之一。`format`是一个具体的模板字符串——使用该格式键入字段，或者`select`通过标签如果站点将原生输入包装在自定义小部件中。

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

`options[]`最多限制为50个条目。**`current`始终正确**即使选择的选项超出限制，它是通过扫描每个选项计算出来的，而不是从截断的列表中获取。如果`options_total > options.length`，并且你需要一个不在`options[]`中的选项，请直接运行`browser select <target> "<label>"`——CLI匹配的是实时DOM，而不是截断的列表。

### 文件

```json
{
  "control": "file",
  "multiple": true,
  "current": ["report.pdf", "cover.png"],
  "accept": "application/pdf,image/*"
}
```

不要编造文件路径。上传是通过正常的点击流程完成的——在告诉用户要上传时，请尊重`accept`。

### 复合字段出现的位置

- `browser find --css <sel>`条目：每个匹配项的行内。
- `browser get html --as json`树节点：匹配节点的行内。
- `browser state`快照：在`compounds (N):`侧车中键由数字引用，所以你可以一目了然地告诉哪些`[N]`条目具有丰富的元数据。

---

## 成本指南

考虑每次调用的有效负载大小。预算是存在的，有原因。

| command | rough cost | when to use |
|---------|-----------|-------------|
| `state` | medium (bounded by internal budget) | 任何页面的第一次调用，每次导航后，当你需要引用时。 |
| `find --css <sel>` | small | 你已经知道选择器——一次查询，紧凑条目。 |
| `get title` / `get url` | tiny | 在步骤之间进行基本检查。 |
| `get text/value/attributes` | tiny per call | 验证一个特定字段。 |
| `get html` (raw) | can be huge | 避免在无限制的页面上。始终与`--selector`和预算一起使用。 |
| `get html --as json --depth 3 --children-max N --text-max N --max N` | medium | 当你需要推理结构，而不是特定字段时。 |
| `screenshot` | large | 只有当页面是视觉时（CAPTCHA、图表）。优先使用`state`。 |
| `extract` | medium per chunk | 长格式阅读。循环`next_start_char`直到它为`null`。 |
| `network` (default) | small | 首次查看API。 |
| `network --detail <key>` | varies | 获取一个正文。 |
| `network --raw` | huge | 仅当`--filter`缩小了候选集后。 |
| `eval "JSON.stringify(...)"` | controlled | 当没有上述选项适合时，针对特定引用的提取。 |

经验法则：**每个页面转换一个`state`，每个后续查询一个`find`，每个动作一个`get`/`click`/`type`。如果你的计划涉及每个页面超过10个调用，你可能是在抓取而不是交互——考虑`extract`或`network`。
