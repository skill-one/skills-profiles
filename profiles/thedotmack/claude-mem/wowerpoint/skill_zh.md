# Wowerpoint

一个文档输入，一个PDF输出。仅支持幻灯片演示文稿——来自同一引擎的视频和播客效果明显更差，不在范围内；如果用户需要这些，请直接将用户引导至 `notebooklm` CLI。

## 触发条件

- "Wowerpoint <文件>"
- "制作关于 <文件> 的幻灯片"
- "将此报告转换为幻灯片"
- "Kawaii-deck 这个"

## 设置（每台机器一次性）

如果 `notebooklm auth check` 返回 0 且 `command -v jq` 解析成功，则跳过。

```bash
uv tool install --with playwright --force notebooklm-py
$(uv tool dir)/notebooklm-py/bin/playwright install chromium
```

`jq` 是工作流程中 JSON 解析所必需的；如果缺失，请安装（在 macOS 上使用 `brew install jq`，或使用您的发行版包管理器）。

然后用户需要交互式地进行身份验证——不要脚本化。告诉他们输入 `! notebooklm login`，以便 OAuth ENTER 落在他们的终端中。

## 工作流程

### 1. 源文档

您需要恰好一个源文档。如果它不存在或太薄弱以至于无法承载演示文稿，**请先编写它**——使用 mem-search 和顺序思考使其全面（长格式、叙述性、几千字是正常的）。不要通过添加更多源来掩盖薄弱的源。

### 2. 身份验证预检查

```bash
notebooklm auth check 2>&1 | tail -5
```

退出码 1 为 `Run 'notebooklm login' to authenticate.` = 停止并告诉用户。

### 3. 创建笔记本，添加源

```bash
NOTEBOOK_ID=$(notebooklm create "<标题>" --json | jq -r .notebook.id)
SOURCE_ID=$(notebooklm source add "<doc-path>" --notebook "$NOTEBOOK_ID" --json | jq -r .source.id)
```

标题：源文档的 H1，或其文件名干；对有日期的工作追加日期。

JSON 封装键不同——`create` → `.notebook.id`，`source add` → `.source.id`，`generate` → `.task_id`。错误的键 = 空字符串 = 安静的下游失败。

### 4. 启动子代理

生成大约需要 10 分钟；永远不要阻塞它。使用以下模板，并使用 `run_in_background: true`。

### 5. 结束你的回合

打印笔记本 URL，以便用户可以实时查看：

```text
https://notebooklm.google.com/notebook/<NOTEBOOK_ID>
```

子代理的完成通知在文件出现在磁盘上时触发。

## 输出路径

源文件旁边，平行文件名：

```text
<source-dir>/<source-stem>-slides.pdf
```

如果源不在合适的位置作为输出位置，默认为 `reports/<stem>-slides.pdf`。

## 分享链接（WOWerpoint 服务器）

PDF 落在磁盘上后，子代理还会将其 POST 到 WOWerpoint 服务器，该服务器将 16:9 的演示文稿转换为 9:16 的移动双胞胎并返回分享 URL。分享 URL 是用户的主要交付成果；磁盘上的 PDF 是备份。

必需的环境（在用户的 shell 中导出——子代理继承父代理的环境，因此简单的 `export` 足够；不会运行 dotenv 加载器）：

```bash
WOWERPOINT_API_BASE=https://wowerpoint-api.<subdomain>.workers.dev
WOWERPOINT_VIEWER_BASE=https://wowerpoint-viewer.<subdomain>.workers.dev
WOWERPOINT_UPLOAD_TOKEN=<token>
```

如果任何变量缺失，请跳过分享链接步骤，只需将 PDF 交给用户。

上传模式（在子代理确认 PDF 存在于磁盘后运行）。捕获完整响应，以便处理空的 `id` 和 `error` 负载——`jq -r '.id'` 在缺失键时返回字面字符串 `null`，因此始终通过 `.id // empty` 管道：

```bash
if [ -n "$WOWERPOINT_API_BASE" ] && [ -n "$WOWERPOINT_UPLOAD_TOKEN" ] && [ -n "$WOWERPOINT_VIEWER_BASE" ]; then
  UPLOAD_JSON=$(curl -sS --connect-timeout 10 --max-time 30 -X POST "$WOWERPOINT_API_BASE/api/decks" \
    -H "Authorization: Bearer $WOWERPOINT_UPLOAD_TOKEN" \
    -F "file=@<OUTPUT_PATH>" \
    -F "title=<TITLE>")
  DECK_ID=$(printf '%s' "$UPLOAD_JSON" | jq -r '.id // empty')
  API_ERROR=$(printf '%s' "$UPLOAD_JSON" | jq -r '.error // empty')
  if [ -n "$API_ERROR" ] || [ -z "$DECK_ID" ]; then
    echo "WOWerpoint 上传警告：${API_ERROR:-缺失 id}"
  else
    echo "分享 URL：$WOWERPOINT_VIEWER_BASE/$DECK_ID"
  fi
fi
```

返回的 `id` 是从标题派生的短横线分隔的缩写，带有随机生物后缀（例如 `tokenrouter-quest-hawk`，或者如果标题为空或非 ASCII，则为 `velvet-comet-tiger`）。分享 URL 是：

```text
$WOWERPOINT_VIEWER_BASE/<id>
```

它立即生效（显示一个“正在转换中…”页面，在准备好时自动刷新）。转换每个幻灯片大约需要 1-2 分钟。在最终响应中打印分享 URL。

## 提示

一句话。默认：

```text
使用可爱的角色讲述 <主题> 的故事。保持温暖和清晰。
```

将 `<主题>` 替换为源文档 H1 或用户框架中的一个短语描述。如果用户提供了自己的提示，请逐字传递——不要扩展它。

## 子代理模板（复制粘贴，参数化）

```text
您正在处理 NotebookLM 幻灯片演示文稿生成。在 `<repo-absolute-path>` 中工作。

上下文：
- `notebooklm` CLI 已安装并经过身份验证（父代理使用 `notebooklm auth check` 验证）。
- 笔记本和源已经存在。

输入：
- 笔记本 ID：`<NOTEBOOK_ID>`
- 源 ID：`<SOURCE_ID>`
- 生成提示：`<PROMPT>`
- 输出路径：`<OUTPUT_PATH>`
- 演示文稿标题：`<TITLE>`（笔记本标题，用于分享链接步骤）

步骤：

1. 等待源：`notebooklm source wait <SOURCE_ID> -n <NOTEBOOK_ID> --timeout 600`
   退出 0 = 就绪，1 = 错误，2 = 超时。超时情况下，运行 `notebooklm source list -n <NOTEBOOK_ID> --json` 并报告状态。

2. 生成：`notebooklm generate slide-deck "<PROMPT>" --format detailed --length default --notebook <NOTEBOOK_ID> --json --retry 2`
   从 JSON 中解析 `task_id`（顶层键是 `task_id`）。
   在 `GENERATION_FAILED` 或 "No result found for RPC ID"：睡眠 300，重试一次，然后放弃。

3. 等待工件：`notebooklm artifact wait <task_id> -n <NOTEBOOK_ID> --timeout 1800`

4. 下载：`notebooklm download slide-deck <OUTPUT_PATH> -a <task_id> -n <NOTEBOOK_ID>`

5. 验证：`ls -la <OUTPUT_PATH>` 确认文件存在。

6. 上传到 WOWerpoint 服务器以获取移动分享链接。如果任何 `WOWERPOINT_API_BASE`、`WOWERPOINT_UPLOAD_TOKEN` 或 `WOWERPOINT_VIEWER_BASE` 未设置，则静默跳过。否则：

   ```bash
   if [ -n "$WOWERPOINT_API_BASE" ] && [ -n "$WOWERPOINT_UPLOAD_TOKEN" ] && [ -n "$WOWERPOINT_VIEWER_BASE" ]; then
     UPLOAD_JSON=$(curl -sS --connect-timeout 10 --max-time 30 -X POST "$WOWERPOINT_API_BASE/api/decks" \
       -H "Authorization: Bearer $WOWERPOINT_UPLOAD_TOKEN" \
       -F "file=@<OUTPUT_PATH>" \
       -F "title=<TITLE>")
     DECK_ID=$(printf '%s' "$UPLOAD_JSON" | jq -r '.id // empty')
     API_ERROR=$(printf '%s' "$UPLOAD_JSON" | jq -r '.error // empty')
     if [ -n "$API_ERROR" ] || [ -z "$DECK_ID" ]; then
       echo "WOWerpoint 上传警告：${API_ERROR:-缺失 id}"
     else
       echo "分享 URL：$WOWERPOINT_VIEWER_BASE/$DECK_ID"
     fi
   fi
   ```

   警告情况下，磁盘上的 PDF 仍然是有效的交付成果——不要重试上传。

简要报告（少于 200 字）：
- 最终工件 ID
- 每个阶段的耗时（源等待、生成、渲染等待、下载）
- 输出文件路径 + 大小
- 分享 URL（如果生成）
- 任何重试或警告
- 如果任何步骤失败，则精确的错误消息

不要手动轮询状态。`wait` 命令处理退避。
```

## 失败模式

- **`pip: command not found`** — 现代 macOS 不在 PATH 上提供 pip。使用 `uv tool install`。
- **`Playwright not installed`** — 使用 `--with playwright` 安装 `notebooklm-py`，然后 `playwright install chromium`。
- **`Run 'notebooklm login' to authenticate`** — 只有用户才能完成 OAuth。
- **`task_id` 解析为空字符串** — 错误的 JSON 封装键。`generate` 在顶层返回 `{"task_id": "..."}`。
- **速率限制 (`GENERATION_FAILED` 或 "No result found for RPC ID")** — `--retry 2` 处理瞬态；持久性故障意味着等待 5-10 分钟或回退到 Web UI。
- **源上传拒绝用于敏感文档** — 在添加包含凭证、客户数据或未发布产品信息的源之前进行确认。NotebookLM 是一个 Google 服务。
- **`--length long` 不存在** — 仅 `default|short`。如果用户要求“长幻灯片”，请使用 `default` 并解释。
- **没有 `--style` 标志** — 可爱的东西存在于提示文本中。

## 运营技巧

- **廉价重跑** — 一旦笔记本 + 源存在，使用不同的提示重新生成只需重复生成 + 下载。重用 `NOTEBOOK_ID` 和 `SOURCE_ID`。
- **Web UI 回退** — 如果生成被速率限制超过 30 分钟，打开笔记本 URL，在 UI 中触发生成，然后 `notebooklm artifact list -n <NOTEBOOK_ID>` 和 `download`。
