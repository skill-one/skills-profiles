# PR Review Canvas

生成一个交互式的 HTML 代码评审页面，就像同行在引导你了解关键内容。

## 工作流程

### 1. 获取 PR 数据

并行运行以下 `gh api` 命令：

```bash
gh api repos/{owner}/{repo}/pulls/{number} --jq '{title, body, user: .user.login, state, additions, deletions, changed_files, base: .base.ref, head: .head.ref}'
gh api repos/{owner}/{repo}/pulls/{number}/files --paginate --jq '.[] | {filename, status, additions, deletions, patch}'
gh api repos/{owner}/{repo}/pulls/{number}/comments --jq '.[] | {user: .user.login, body, path, line}'
```

### 2. 分析 PR 并生成 HTML 正文

读取差异内容，理解 PR 的内容，直接将 `<body>` 的内容作为 HTML 写出。你有完全的创作自由——目标是向评审者清晰地解释 PR。使用最适合 PR 的结构。

**典型结构**（按需调整）：
- 标题栏，包含标题、PR 编号、作者、统计信息
- 摘要框，用普通英语解释 PR 的作用
- 核心文件区域，包含注释和差异内容
- 机械性/模板文件默认折叠
- 底部有评审清单

**但也可以添加：**
- **伪代码摘要**，用于冗长代码——用普通英语或简短伪代码展示算法，下方折叠真实差异（使用标记为 "Show full implementation" 的 `.bp-section` 卡片）。当 150 行的 retry/backoff/error-handling 代码实际上只是 "fetch with exponential backoff and circuit breaker" 时，效果很好。
- 图表（内联 SVG、通过 CDN 的 mermaid、ASCII 艺术在 `<pre>` 中）
- 流程图显示前后控制流
- 表格比较旧版本和新的行为
- 警告、问题或注意事项的标注框
- 如果有助于理解，可以添加交互式小部件
- 任何其他使评审更清晰的内容

**伪代码模式示例：**
```html
<div class="file-card">
  <div class="file-hdr" onclick="toggle(this)">
    <span class="fname">retryClient.ts</span>
    <div class="fstats"><span class="pill add">+173</span><span class="pill del">&minus;11</span><span class="chev open">&#9654;</span></div>
  </div>
  <div class="file-body open">
    <div class="file-note">
      <strong>用普通英语解释这段代码的作用：</strong>
      <pre style="margin-top:8px;color:var(--text);font-size:12px;line-height:1.6;">
fetch(url):
  if circuit breaker is open → fail fast
  retry up to N times:
    try fetch with timeout
    on success → close circuit breaker, return
    on retryable error → wait (exponential backoff + jitter)
    on non-retryable error → throw
  circuit breaker records failure</pre>
    </div>
    <div class="bp-section" style="margin:0;border:0;border-radius:0;">
      <div class="bp-hdr" onclick="toggleBP(this)">
        <span>显示完整实现 (+173 行)</span><span class="chev">&#9654;</span>
      </div>
      <div class="bp-body"><div data-diff="retryClient"></div></div>
    </div>
  </div>
</div>
```

### 3. 可用的 CSS 类和 JS 工具

从本技能目录中读取 [styles.css](styles.css) 和 [renderer.js](renderer.js)。这些为你提供了预构建的深色主题工具包。将它们原样注入 [template.html](template.html)。

**可使用的 CSS 类：**

| 类名 | 用途 |
|-------|---------|
| `.header`, `.header h1`, `.header-meta` | 页面标题栏 |
| `.pill.add`, `.pill.del`, `.pill.files` | 统计徽章 (+N, -N, N 个文件) |
| `.content` | 居中的内容包装器（最大 900px） |
| `.summary` | 摘要/TL;DR 框 |
| `.section-title` | 带底部边框的章节标题 |
| `.ic` | 内联代码引用（等宽字体、蓝色、深色背景） |
| `.file-card`, `.file-hdr`, `.file-body` | 可折叠的文件卡片（在 `.file-hdr` 上使用 `onclick="toggle(this)"`） |
| `.file-note` | 文件卡片内的粘性评审注释 |
| `.bp-section`, `.bp-hdr`, `.bp-body` | 可折叠的模板卡片（使用 `onclick="toggleBP(this)"`） |
| `.bp-note` | 模板卡片内的注释 |
| `.verdict` | 评审清单框 |

**可用的 JS 函数：**

| 函数 | 用途 |
|----------|-------|
| `toggle(hdrElement)` | 切换 `.file-body` 的展开/折叠状态 |
| `toggleBP(hdrElement)` | 切换 `.bp-body` 的展开/折叠状态 |
| `renderDiff(target, diffInput)` | 渲染统一差异。`target` 可以是 DOM 元素、字符串 ID 或 CSS 选择器。`diffInput` 可以是原始补丁字符串，也可以是行数组——两者都有效。自动过滤导入语句，折叠仅空白更改，检测移动的代码（蓝色/紫色色调）。 |
| `esc(string)` | 对字符串进行 HTML 转义 |

**渲染差异——使用 `data-diff` 属性进行自动发现。**
在你的 body HTML 中需要渲染差异的地方放置 `<div data-diff="KEY"></div>` 占位符。渲染器在 DOM 加载后自动找到它们，并从 `template.html` 中的 `<script id="pr-diffs-json" type="application/json">` 元素填充它们。

**关键：** 补丁字符串可以包含 `</script>`，除了换行符、反斜杠和引号外。即使 `json.dumps(...)` 也不够，如果你将原始输出粘贴到可执行的 `<script>` 中，因为 HTML 解析可能会提前终止标签。切勿手动将补丁字符串嵌入 JS/JSON。相反，使用以下安全方法：

1. 在获取步骤中，使用 `jq` 将补丁保存到 JSON 文件（`jq` 正确处理转义）：
```bash
gh api repos/{owner}/{repo}/pulls/{number}/files --paginate \
  --jq '[.[] | {key: (.filename | gsub("[^a-zA-Z0-9]"; "_")), value: (.patch // "")}] | from_entries' \
  > /tmp/pr-patches-{number}.json
```

2. 在组装步骤中，使用 Python 将 JSON 安全地注入 `template.html`：
```bash
python3 <<'PY'
import json
from pathlib import Path

patches = json.loads(Path('/tmp/pr-patches-{number}.json').read_text())
html = Path('/tmp/pr-review-{number}-body.html').read_text()
css = Path('styles.css').read_text()
js = Path('renderer.js').read_text()
tmpl = Path('template.html').read_text()

# 防止字面值 </script> 提前终止 HTML script 标签。
safe_json = json.dumps(patches).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

out = (
  tmpl.replace('/* INJECT_CSS */', css)
      .replace('/* INJECT_JS */', js)
      .replace('<!-- INJECT_BODY -->', html)
      .replace('{"__PR_DIFFS_PLACEHOLDER__":true}', safe_json)
)

Path('/tmp/pr-review-{number}.html').write_text(out)
PY
```

这保证了有效的 JSON 和安全的 HTML 嵌入。代理将 body HTML 写入临时文件，然后 Python 安全地组装所有内容。

差异数据键应与 HTML 中的 `data-diff` 属性值匹配：
```html
<div data-diff="path_to_file_ts"></div>
```

由于 renderer.js 在 `<head>` 中加载，你也可以直接从内联 `<script>` 标签中调用 `renderDiff(target, lines)`，如果需要用于自定义用例。该函数接受 `target` 为 DOM 元素、ID 字符串或 CSS 选择器，`lines` 为字符串或数组。

**你不受限于这些。** 添加你自己的内联 `<style>` 块、`<script>` 块、SVG、图表或任何其他内容。预构建的组件可以节省时间，但不会限制你。

### 4. 组装和提供

1. 将你的 body HTML（所有放入 `<body>` 中的内容）写入 `/tmp/pr-review-{number}-body.html`
2. 使用步骤 3 中的 `jq` 命令将补丁保存到 `/tmp/pr-patches-{number}.json`
3. 运行步骤 3 中的 Python 组装脚本（从本技能目录读取 styles.css、renderer.js、template.html，安全地注入 body + 补丁，写入最终的 HTML）
4. 在固定端口上启动本地服务器：
   ```bash
   cd /tmp && python3 -m http.server 8432 --bind 127.0.0.1
   ```
   将其后台运行，然后导航应用内的浏览器到 `http://127.0.0.1:8432/pr-review-{number}.html`。

   **为什么固定端口和 `cd /tmp`：** 后台 shell 没有伪终端，所以 Python 会无限期地缓冲其启动消息（"Serving HTTP on..."）——使用端口 0 意味着你永远无法知道选择了哪个端口。而 `--directory /tmp` 虽然有效，但 `cd /tmp` 在不同版本的 Python 中更稳健。如果端口 8432 被占用，尝试 8433、8434 等。

### 差异功能（由 renderer.js 自动处理）

- 过滤掉仅导入的行
- 将仅空白更改折叠为上下文行
- 检测移动的代码块（在一个地方删除 3+ 连续行，并在其他地方相同地添加）——以蓝色/紫色渲染，而不是红色/绿色
- 近似匹配（移动 + 小编辑）会得到不同的紫色色调

### 样式说明

- 深色主题：`#1a1a1a` 背景，Inter 字体，IBM Plex Mono 代码字体
- 使用 `var(--warning)` 表示橙色，`var(--success)` 表示绿色，`var(--danger)` 表示红色，`var(--accent)` 表示蓝色
- 粘性文件标题（`position: sticky; top: 0`）和注释（`top: 35px`）在滚动时固定
- 核心文件默认展开（`.file-body.open`），机械文件折叠
