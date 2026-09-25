# 浏览器追踪

将一个**第二个、只读的 CDP 客户端**附加到由主自动化驱动的浏览器会话上。该追踪记录完整的 DevTools 水管到 NDJSON，并行轮询屏幕截图和 DOM 转储，并将所有内容切片成 bash 工具可以搜索的目录树。

这项技能**不会**驱动页面——它只用于监听。将它与 `browser` 技能 `browse`、Stagehand、Playwright 或任何其他使用 CDP 的工具配合使用。

## 使用场景

- 用户想要调试浏览器自动化运行（失败的表单、缺失的元素、挂起的导航、JS 异常）。
- 用户有一个正在运行的自动化，并希望在重启之前中途附加追踪。
- 用户想要将 CDP 水管分割成网络 / 控制台 / DOM / 页面桶。
- 用户想要随时间获取屏幕截图 + DOM 快照，并通过时间戳与 CDP 事件关联。

如果用户只是想要**驱动**浏览器，请使用 `browser` 技能。

## 设置检查

```bash
node --version                                  # 需要 Node 18+
which browse || npm install -g browse
which jq     || true                                # 可选——仅用于临时查询
```

验证 `browse cdp` 是否存在：

```bash
browse --help | grep -q "^\s*cdp " || echo "browse cdp 不可用——更新 browse"
```

## 工作原理

每个 Chrome DevTools 目标都接受**多个并发 CDP 客户端**。主自动化是一个客户端；这项技能添加了第二个客户端，该客户端仅启用观察域（网络、控制台、运行时、日志、页面），并且永远不会发送操作命令。

追踪器有三个部分：

1. **水管**：`browse cdp <target>` 将每个 CDP 事件作为每行一个 JSON 对象流式传输到 `cdp/raw.ndjson`。
2. **采样器**：轮询循环每隔一段时间（默认 2 秒）调用 `browse screenshot --cdp <target> --path <file>` 和 `browse get html body --cdp <target>`。辅助工具在采样时传递 `--cdp`，以便它可以从自己的进程中附加到追踪的目标；一旦浏览守护进程会话附加到 CDP 目标，则该会话中的后续命令不需要重复 `--cdp`。
3. **二分器**：运行结束后，`bisect-cdp.mjs` 一次遍历 `raw.ndjson`，将其切片为按 CDP 方法键控的每个桶的 JSONL 文件，并使用顶级 `Page.frameNavigated` 事件作为边界来按页面进行二分。

## 快速入门

### 本地 Chrome

```bash
# 1. 使用调试端口启动 Chrome（任何 user-data-dir 都可以使其隔离）。
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-o11y \
  about:blank &

# 2. 启动追踪器。
node scripts/start-capture.mjs 9222 my-run

# 3. 运行主自动化，目标端口为 9222。
browse open https://example.com --cdp 9222
# ...无论运行做什么...

# 4. 停止并二分。
node scripts/stop-capture.mjs my-run
node scripts/bisect-cdp.mjs my-run
```

### Browserbase 远程

两个辅助工具封装了平台端的账本管理：`bb-capture.mjs` 创建或附加到会话并启动追踪器；`bb-finalize.mjs` 在结束时将平台工件（最终会话元数据、服务器日志、下载）拉入运行目录。

> Browserbase 在最后一个 CDP 客户端断开连接后立即结束会话。**使用 `--keep-alive` 创建，然后在或与追踪器一起将自动化附加到会话的 `connectUrl`。** `bb-capture.mjs --new` 处理 keep-alive 会话和追踪器设置；您的自动化仍然需要附加。

```bash
export BROWSERBASE_API_KEY=...

# 1. 一步创建 keep-alive 会话并启动追踪器。
#    打印会话 ID、connectUrl 前缀，以及您可以在浏览器中打开的实时调试器 URL，以便交互式地观看运行。
node scripts/bb-capture.mjs --new my-run

# 2. 驱动自动化。bb-capture 将会话 ID 签名到清单中。
SID=$(jq -r .browserbase.session_id .o11y/my-run/manifest.json)
CONNECT_URL="$(browse cloud sessions get "$SID" | jq -r .connectUrl)"
BROWSE_NAME=my-run-browser
browse open https://example.com --cdp "$CONNECT_URL" --session "$BROWSE_NAME"
browse open https://news.ycombinator.com --session "$BROWSE_NAME"

# 3. 停止追踪器、二分，然后拉取平台工件并释放。
node scripts/stop-capture.mjs my-run
node scripts/bisect-cdp.mjs my-run
node scripts/bb-finalize.mjs my-run --release
```

附加到一个*已经运行*的会话（例如，您的生产工作器创建的会话）— `bb-capture.mjs` 接受会话 ID 而不是 `--new`：

```bash
# 选择一个正在运行的会话（过滤客户端端；browse cloud sessions list 没有--status 标志）
browse cloud sessions list | jq -r '.[] | select(.status == "RUNNING") | .id'

node scripts/bb-capture.mjs <session-id> mid-flight-debug
# ...追踪器与现有的自动化客户端一起运行；没有中断...
node scripts/stop-capture.mjs mid-flight-debug
node scripts/bisect-cdp.mjs mid-flight-debug
node scripts/bb-finalize.mjs mid-flight-debug   # 没有 --release：保留会话运行
```

#### 从 Browserbase 平台获得的内容

`bb-capture.mjs` 向 `manifest.json` 添加一个 `browserbase` 块（会话 ID、项目、区域、启动时间、过期时间、调试器 URL）。`bb-finalize.mjs` 写入：

- `<run>/browserbase/session.json` — 最终 `browse cloud sessions get` 快照（proxyBytes、状态、结束时间、视口、…）
- `<run>/browserbase/logs.json` — `browse cloud sessions logs` 输出。**通常为空。** CDP 水管在 `cdp/raw.ndjson` 中是真相来源；这是一个旁路。
- `<run>/browserbase/downloads.zip` — 会话下载的文件，如果有的话（脚本丢弃当没有文件时得到的 22 字节空 zip）

会话回放工件获取已**弃用**，并且不会获取。使用 `screenshots/` 和 `dom/` 中的屏幕截图 + DOM 转储进行视觉真相。

清单中的实时 `debugger_url` 打开一个由 Browserbase 提供的交互式 Chrome DevTools 视图——这对于在追踪器将水管捕获到磁盘时*观看*长时间运行的自动化很有用。

## 文件系统布局

```
.o11y/<run-id>/
  manifest.json                 运行元数据：目标、域、启动时间、停止时间
  index.jsonl                   每行一个采样：{ts, screenshot, dom, url}
  cdp/
    raw.ndjson                  完整 CDP 水管（每行一个 JSON 对象）
    summary.json                {sessionId, duration, totalEvents, pages[]} — 见下文形状
    network/{requests,responses,finished,failed,websocket}.jsonl   会话范围的桶（始终写入）
    console/{logs,exceptions}.jsonl
    runtime/all.jsonl
    log/entries.jsonl
    page/{navigations,lifecycle,frames,dialogs,all}.jsonl
    dom/all.jsonl                                                  （仅当 O11Y_DOMAINS 包括 DOM 时）
    target/{attached,detached}.jsonl
    pages/                      按顶级 frameNavigated 边界索引的每页切片
      000/                      第一个具体页面
        url.txt                 此页面的 URL
        summary.json            此页面的域/网络/时间块（与 pages[] 条目形状相同）
        raw.jsonl               限定于此页面的水管
        network/, console/, page/, runtime/, log/, target/, dom/    相同的桶，仅非空文件
  screenshots/<iso-ts>.png      每个采样间隔一个 PNG
  dom/<iso-ts>.html             每个采样间隔一个 HTML 转储
  browserbase/                  由 bb-finalize.mjs 添加（Browserbase 运行仅限）
    session.json                最终 `browse cloud sessions get` 快照（proxyBytes、状态、结束时间、…）
    logs.json                   `browse cloud sessions logs` 输出（通常为空）
    downloads.zip               `browse cloud sessions downloads get` 输出（仅当会话下载文件时）
```

当通过 `bb-capture.mjs` 启动运行时，`manifest.json` 还包含一个顶级 `browserbase` 块：`session_id`、`project_id`、`region`、`started_at`、`expires_at`、`keep_alive`、`debugger_url`。

### 摘要形状

`cdp/summary.json` 是任何分析的入口点：它具有会话级别的总计和一个按顶级 `Page.frameNavigated` 索引的 `pages[]` 数组。每页条目按导航顺序发出（页面 0 = 第一个具体 URL）。

```json
{
  "sessionId": "45f28023-…",
  "duration": { "startMs": 1777312533000, "endMs": 1777312609000, "totalMs": 76000 },
  "totalEvents": 420,
  "pages": [
    {
      "pageId": 0,
      "url": "https://example.com/",
      "startMs": 1777312533000, "endMs": 1777312538886, "durationMs": 5886,
      "eventCount": 60,
      "domains": {
        "Network": { "count": 18, "errors": 1 },
        "Console": { "count": 2 },
        "Page":    { "count": 24 },
        "Runtime": { "count": 13 }
      },
      "network": { "requests": 4, "failed": 1, "byType": { "Document": 2, "Script": 1, "Other": 1 } }
    }
  ]
}
```

`startMs` / `endMs` / `durationMs` 是墙上毫秒，从 `manifest.started_at` 加上每个事件 CDP 单调时间戳的偏移量导出。`domains[*]` 仅在非零时包含 `errors`/`warnings` 键。

### 使用 `query.mjs` 深入挖掘

对于交互式探索，使用 `scripts/query.mjs <run-id> <command>` 而不是记住路径：

```bash
node scripts/query.mjs my-run list                    # 页面的单行表格
node scripts/query.mjs my-run page 1                  # 页面 1 的完整摘要
node scripts/query.mjs my-run page 1 network/failed   # 查看 page 1 的 failed.jsonl
node scripts/query.mjs my-run errors                  # 所有跨页面的错误，按 pid 归因
node scripts/query.mjs my-run errors 2                # 仅来自页面 2 的错误
node scripts/query.mjs my-run hosts                   # 按请求计数的前端主机
node scripts/query.mjs my-run host api.example.com    # 某个主机所有请求/响应
node scripts/query.mjs my-run summary                 # 完整的 summary.json
```

后台它只是读取 `cdp/summary.json` 和 `cdp/pages/<pid>/` 树——一旦您知道形状，可以自由使用原始 `jq`/`rg` 跳过它。

## 顶级遍历配方

```bash
# 所有失败的网络请求（使用 jq -c 保持它行分隔）
jq -c '.params' .o11y/<run>/cdp/network/failed.jsonl

# 查找特定主机的请求
jq -c 'select(.params.request.url | test("api\\.example\\.com"))' \
  .o11y/<run>/cdp/network/requests.jsonl

# 4xx/5xx 响应
jq -c 'select(.params.response.status >= 400)
       | {status: .params.response.status, url: .params.response.url}' \
  .o11y/<run>/cdp/network/responses.jsonl

# 仅控制台错误
jq -c 'select(.params.type == "error")' .o11y/<run>/cdp/console/logs.jsonl

# 访问的 URL 序列
jq -r '.params.frame.url' .o11y/<run>/cdp/page/navigations.jsonl

# 找到最接近某个时间戳的屏幕截图（例如，当异常触发时）
ls .o11y/<run>/screenshots/ | sort | awk -v t=20260427T1714123NZ '
  $0 >= t { print; exit }'
```

有关完整的 jq 配方库和按方法二分的映射，请参阅 **REFERENCE.md**。有关端到端调试场景，请参阅 **EXAMPLES.md**。

## 最佳实践

1. **在 Browserbase 上使用 `bb-capture.mjs`**：它强制执行 `--keep-alive`，获取 connectUrl，捕获调试器 URL，并在清单中签名。手动操作容易出错。
2. **不要 `--release` 您不拥有的会话**：`bb-finalize.mjs --release` 是用于您使用 `--new` 创建的会话。当通过 `bb-capture.mjs <session-id>` 附加到生产会话时，运行 `bb-finalize.mjs` 而不带 `--release`，以便原始自动化保持运行。
3. **远程上顺序很重要**：在 Browserbase 上，在（或与追踪器一起）附加主自动化客户端之前，创建会话并使用 `--keep-alive`。否则，一旦追踪器的 WS 关闭，会话就会结束。
4. **不要比 ~1s 更快地轮询**：每个采样运行浏览器 CLI 读取命令和 Chrome 屏幕截图。2s 是一个很好的默认值。
5. **故意选择域**：默认值（`Network Console Runtime Log Page`）涵盖大多数调试。通过 `O11Y_DOMAINS="$O11Y_DOMAINS DOM"` 添加 `DOM` 以获取 DOM 树突变（非常嘈杂）。
6. **通过附加到该会话的 `connectUrl` 重用一个 Browserbase 会话以在远程上为自动化客户端**：使用 `browse open ... --cdp "$CONNECT_URL" --session <name>`。`--session` 标志命名本地浏览守护进程；它不是 Browserbase 会话附加标志。
7. **始终运行 `stop-capture.mjs`**，即使发生崩溃，以便背景进程不会持续存在，并且清单会获得 `stopped_at`。
8. **每次运行二分一次**：`bisect-cdp.mjs` 是幂等的——它每次都会覆盖从 `raw.ndjson` 到每个桶文件的文件。

## 故障排除

- **`browse cdp 立即退出`**：通常意味着目标无法访问（端口错误）或 Browserbase 会话已经结束。对于远程，通过 `browse cloud sessions get <id>` 验证——如果 `status` 是 `COMPLETED`，请使用 `--keep-alive` 重新创建并首先附加自动化。
- **即使进程正在运行，`raw.ndjson` 为空**：确认 CDP 客户端实际上正在驱动页面。追踪器只发出浏览器生成的事件，因此空闲浏览器产生 ~5 行 attach/discover 消息和除此之外的任何内容。
- **所有屏幕截图看起来都一样**：检查 `index.jsonl`——如果 `url` 没有改变，页面还没有导航。轮询循环独立于主自动化的速度运行。
- **Browserbase 会话在运行中途结束**：它可能触发了 `--timeout`。使用更高的超时（`BB_SESSION_TIMEOUT=1800 node scripts/bb-capture.mjs --new ...`）重新创建或移除超时标志。
- **`bb-capture.mjs <id>` 说“不运行”**：您尝试附加的会话已经结束。使用 `browse cloud sessions list | jq '.[] | select(.status == "RUNNING")'` 列出候选者并重试。
- **`browserbase/logs.json` 为空 `[]`**：预期——在实践中 `browse cloud sessions logs` 是稀疏的。CDP 水管在 `cdp/raw.ndjson` 中是真相来源。
- **会话录制在哪里（rrweb）？**：会话回放工件获取已弃用；这项技能不会获取它。使用 `screenshots/` 中的屏幕截图流和 `dom/` 中的 DOM 转储。

有关完整参考，请参阅 [REFERENCE.md](REFERENCE.md)。
有关示例调试运行，请参阅 [EXAMPLES.md](EXAMPLES.md)。
