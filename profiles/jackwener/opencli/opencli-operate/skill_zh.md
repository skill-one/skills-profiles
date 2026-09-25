# OpenCLI 操作 — AI 代理的浏览器自动化

通过 CLI 逐步控制 Chrome。重用现有的登录会话 — 无需密码。

## 前置条件

```bash
opencli doctor    # 验证扩展程序 + 守护进程连接性
```

要求：运行 Chrome + 安装 OpenCLI 浏览器桥接扩展程序。

## 严重规则

1. **始终使用 `state` 检查页面，绝不要使用 `screenshot`** — `state` 返回结构化 DOM，带有 `[N]` 元素索引，是即时的且不消耗代币。`screenshot` 需要视觉处理且速度慢。仅在用户明确要求保存视觉内容时才使用 `screenshot`。
2. **始终使用 `click`/`type`/`select` 进行交互，绝不要使用 `eval` 来点击或输入** — `eval "el.click()"` 绕过 `scrollIntoView` 和 CDP 点击管道，导致屏幕外元素点击失败。使用 `state` 找到 `[N]` 索引，然后 `click <N>`。
3. **使用 `get value` 而不是截图来验证输入** — 在 `type` 后，运行 `get value <index>` 来确认。
4. **每次页面更改后都运行 `state`** — 在 `open`、`click`（链接）、`scroll` 后，始终运行 `state` 以查看新元素及其索引。绝不要猜测索引。
5. **使用 `&&` 严格链式命令** — 将 `open + state`、多个 `type` 调用、`type + get value` 组合成单个 `&&` 链。每个工具调用都有开销；链式调用可减少开销。
6. **`eval` 是只读的** — 仅用于数据提取 (`JSON.stringify(...)`)，绝不要用于点击、输入或导航。始终用 IIFE 包裹以避免变量冲突：`eval "(function(){ const x = ...; return JSON.stringify(x); })()"`。
7. **最小化总工具调用次数** — 在行动前规划你的序列。一个良好的任务完成使用 3-5 次工具调用，而不是 15-20 次。将 `open + state` 合并为一个调用。将 `type + type + click` 合并为一个调用。仅在需要发现新索引时才单独运行 `state`。
8. **优先使用 `network` 来发现 API** — 大多数网站都有 JSON API。基于 API 的适配器比 DOM 抓取更可靠。

## 命令成本指南

| 成本 | 命令 | 使用场景 |
|------|------|-------------|
| **免费且即时** | `state`, `get *`, `eval`, `network`, `scroll`, `keys` | 默认 — 使用这些 |
| **免费但更改页面** | `open`, `click`, `type`, `select`, `back` | 交互 — 运行 `state` 后 |
| **昂贵（视觉代币）** | `screenshot` | 仅当用户需要保存图像时 |

## 动作链式规则

命令可以用 `&&` 链式。浏览器通过守护进程持久化，因此链式是安全的。

**尽可能链式** — 较少的工具调用 = 更快的完成：
```bash
# 好：一次调用中打开 + 检查（节省 1 次往返）
opencli operate open https://example.com && opencli operate state

# 好：一次调用中填写表单（节省 2 次往返）
opencli operate type 3 "hello" && opencli operate type 4 "world" && opencli operate click 7

# 好：一次调用中输入 + 验证
opencli operate type 5 "test@example.com" && opencli operate get value 5

# 好：点击 + 等待 + 检查（用于触发页面更改的点击）
opencli operate click 12 && opencli operate wait time 1 && opencli operate state

# 不好：为每个动作分开调用（浪费）
opencli operate type 3 "hello"    # 不要这样
opencli operate type 4 "world"    # 当你可以链式
opencli operate click 7            # 三个动作时
```

**页面更改 — 总是放在链式中的最后**（后续命令看到过时的索引）：
- `open <url>`，`back`，`click <导航的链接/按钮>`

**规则**：已知索引时链式，需要发现索引时单独运行 `state`。

## 核心工作流程

1. **导航**：`opencli operate open <url>`
2. **检查**：`opencli operate state` → 带有 `[N]` 索引的元素
3. **交互**：使用索引 — `click`，`type`，`select`，`keys`
4. **等待**（如果需要）：`opencli operate wait selector ".loaded"` 或 `wait text "Success"`
5. **验证**：`opencli operate state` 或 `opencli operate get value <N>`
6. **重复**：浏览器在命令之间保持打开状态
7. **保存**：编写 TS 适配器到 `~/.opencli/clis/<site>/<command>.ts`

## 命令

### 导航

```bash
opencli operate open <url>              # 打开 URL（触发页面更改）
opencli operate back                    # 后退（触发页面更改）
opencli operate scroll down             # 滚动（上/下，--amount N）
opencli operate scroll up --amount 1000
```

### 检查（免费且即时）

```bash
opencli operate state                   # 结构化 DOM 带有 [N] 索引 — 主要工具
opencli operate screenshot [path.png]   # 保存视觉内容到文件 — 仅用于用户交付物
```

### 获取（免费且即时）

```bash
opencli operate get title               # 页面标题
opencli operate get url                 # 当前 URL
opencli operate get text <index>        # 元素文本内容
opencli operate get value <index>       # 输入/文本区域值（用于输入后验证）
opencli operate get html                # 完整页面 HTML
opencli operate get html --selector "h1" # 范围 HTML
opencli operate get attributes <index>  # 元素属性
```

### 交互

```bash
opencli operate click <index>           # 点击元素 [N]
opencli operate type <index> "text"     # 向元素 [N] 输入
opencli operate select <index> "option" # 选择下拉菜单
opencli operate keys "Enter"            # 按键（Enter，Escape，Tab，Control+a）
```

### 等待

三种变体 — 根据情况使用正确的变体：

```bash
opencli operate wait time 3                       # 等待 N 秒（固定延迟）
opencli operate wait selector ".loaded"            # 等待元素出现在 DOM 中
opencli operate wait selector ".spinner" --timeout 5000  # 带有超时（默认 30 秒）
opencli operate wait text "Success"                # 等待页面出现文本
```

**何时等待**：在 SPAs 的 `open` 后，触发异步加载的 `click` 后，动态渲染内容前的 `eval` 前。

### 提取（免费且即时，只读）

仅用于读取数据。绝不要使用 `eval` 来点击、输入或导航。

```bash
opencli operate eval "document.title"
opencli operate eval "JSON.stringify([...document.querySelectorAll('h2')].map(e => e.textContent))"

# 重要提示：将复杂逻辑包裹在 IIFE 中以避免 "已声明" 错误
opencli operate eval "(function(){ const items = [...document.querySelectorAll('.item')]; return JSON.stringify(items.map(e => e.textContent)); })()"
```

**选择器安全性**：始终使用后备选择器 — `querySelector` 在未命中时返回 `null`：
```bash
# 不好：如果选择器未命中则崩溃
opencli operate eval "document.querySelector('.title').textContent"

# 好：使用 || 或 ?. 后备
opencli operate eval "(document.querySelector('.title') || document.querySelector('h1') || {textContent:''}).textContent"
opencli operate eval "document.querySelector('.title')?.textContent ?? 'not found'"
```

### 网络（API 发现）

```bash
opencli operate network                  # 显示捕获的 API 请求（自 `open` 后自动捕获）
opencli operate network --detail 3       # 显示请求 #3 的完整响应体
opencli operate network --all            # 包括静态资源
```

### 沉淀（保存为 CLI）

```bash
opencli operate init hn/top              # 在 ~/.opencli/clis/hn/top.ts 生成适配器骨架
opencli operate verify hn/top            # 测试适配器（如果 `limit` 参数定义，则仅添加 `--limit 3`）
```

- `init` 自动检测活动浏览器会话的域名（无需指定）
- `init` 创建文件 + 从当前页面填充 `site`、`name`、`domain` 和 `columns`
- `verify` 端到端运行适配器并打印输出；如果适配器中不存在 `limit` 参数，则不会传递 `--limit 3`

### 会话

```bash
opencli operate close                   # 关闭自动化窗口
```

## 示例：提取 HN 故事

```bash
opencli operate open https://news.ycombinator.com
opencli operate state                   # 看到 [1] 一个 "Story 1"，[2] 一个 "Story 2"...
opencli operate eval "JSON.stringify([...document.querySelectorAll('.titleline a')].slice(0,5).map(a => ({title: a.textContent, url: a.href})))"
opencli operate close
```

## 示例：填写表单

```bash
opencli operate open https://httpbin.org/forms/post
opencli operate state                   # 看到 [3] 输入 "Customer Name"，[4] 输入 "Telephone"
opencli operate type 3 "OpenCLI" && opencli operate type 4 "555-0100"
opencli operate get value 3             # 验证："OpenCLI"
opencli operate close
```

## 保存为可重用 CLI — 完整工作流程

### 分步沉淀流程：

```bash
# 1. 探索网站
opencli operate open https://news.ycombinator.com
opencli operate state                          # 了解 DOM 结构

# 2. 发现 API（高质量适配器的关键）
opencli operate eval "fetch('/api/...').then(r=>r.json())"   # 触发 API 调用
opencli operate network                        # 查看捕获的 API 请求
opencli operate network --detail 0             # 检查响应体

# 3. 生成骨架
opencli operate init hn/top                    # 创建 ~/.opencli/clis/hn/top.ts

# 4. 编辑适配器（填写 func 逻辑）
# - 如果找到 API：直接使用 fetch()（策略 Strategy.PUBLIC 或 COOKIE）
# - 如果没有 API：使用 page.evaluate() 进行 DOM 提取（策略 Strategy.UI）

# 5. 验证
opencli operate verify hn/top                  # 运行适配器并显示输出

# 6. 如果验证失败，编辑并重试
# 7. 完成时关闭
opencli operate close
```

### 示例适配器：

```typescript
// ~/.opencli/clis/hn/top.ts
import { cli, Strategy } from '@jackwener/opencli/registry';

cli({
  site: 'hn',
  name: 'top',
  description: 'Hacker News Top stories',
  domain: 'news.ycombinator.com',
  strategy: Strategy.PUBLIC,
  browser: false,
  args: [{ name: 'limit', type: 'int', default: 5 }],
  columns: ['rank', 'title', 'score', 'url'],
  func: async (_page, kwargs) => {
    const limit = Math.min(Math.max(1, kwargs.limit ?? 5), 50);
    const resp = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
    const ids = await resp.json();
    return Promise.all(
      ids.slice(0, limit).map(async (id: number, i: number) => {
        const item = await (await fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`)).json();
        return { rank: i + 1, title: item.title, score: item.score, url: item.url ?? '' };
      })
    );
  },
});
```

保存到 `~/.opencli/clis/<site>/<command>.ts` → 立即可用作为 `opencli <site> <command>`。

### 策略指南

| 策略 | 何时使用 | browser: |
|------|------|----------|
| `Strategy.PUBLIC` | 公共 API，无需认证 | `false` |
| `Strategy.COOKIE` | 需要登录 Cookie | `true` |
| `Strategy.UI` | 直接 DOM 交互 | `true` |

**始终优先 API 而非 UI** — 在浏览过程中发现 API 时，直接使用 `fetch()`。

## 小贴士

1. **始终先 `state`** — 绝不要猜测元素索引，始终先检查
2. **会话持久化** — 浏览器在命令之间保持打开状态，无需重新打开
3. **使用 `eval` 进行数据提取** — `eval "JSON.stringify(...)"` 比多次 `get` 调用更快
4. **使用 `network` 发现 API** — JSON API 比 DOM 抓取更可靠
5. **别名**：`opencli op` 是 `opencli operate` 的简写

## 常见陷阱

1. **`form.submit()` 在自动化中失败** — 不要使用 `form.submit()` 或 `eval` 提交表单。直接导航到搜索 URL：
   ```bash
   # 不好：form.submit() 常常静默失败
   opencli operate eval "document.querySelector('form').submit()"
   # 好：构造 URL 并导航
   opencli operate open "https://github.com/search?q=opencli&type=repositories"
   ```

2. **GitHub DOM 频繁更改** — 优先使用 `data-testid` 属性（如果可用）；它们比类名或标签结构更稳定。

3. **SPA 页面需要 `wait` 才能提取** — 在 SPAs 的 `open` 或 `click` 后，DOM 不会立即准备好。始终 `wait selector` 或 `wait text` 之后再 `eval`。

4. **点击前使用 `state`** — 运行 `opencli operate state` 检查可交互元素及其索引。绝不要从内存中猜测索引。

5. **`evaluate` 在浏览器上下文中运行** — 适配器中的 `page.evaluate()` 在浏览器中执行。Node.js API (`fs`，`path`，`process`) 不可用。使用 `fetch()` 进行网络调用，DOM API 获取页面数据。

6. **`page.evaluate` 中的反引号会破坏 JSON 存储** — 当适配器将作为 JSON 存储或传输时，避免在 `page.evaluate` 中使用模板字面量。使用字符串连接或函数式 `evaluate`：
   ```typescript
   // 不好：反引号在适配器为 JSON 时会破坏
   page.evaluate(`document.querySelector("${selector}")`)
   // 好：函数式 evaluate
   page.evaluate((sel) => document.querySelector(sel), selector)
   ```

## 故障排除

| 错误 | 解决方法 |
|-------|-----|
| "Browser not connected" | 运行 `opencli doctor` |
| "attach failed: chrome-extension://" | 暂时禁用 1Password |
| 元素未找到 | `opencli operate scroll down && opencli operate state` |
| 页面更改后索引过时 | 再次运行 `opencli operate state` 获取最新索引 |
