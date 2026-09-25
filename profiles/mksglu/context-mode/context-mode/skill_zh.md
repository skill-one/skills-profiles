# 上下文模式：所有大型输出的默认设置

## 必须遵守的规则

<context_mode_logic>
  <mandatory_rule>
    所有命令默认使用上下文模式。仅对保证输出较小的操作使用 Bash。
  </mandatory_rule>
</context_mode_logic>

Bash 白名单（安全可直接运行）：
- **文件修改**：`mkdir`，`mv`，`cp`，`rm`，`touch`，`chmod`
- **Git 写入**：`git add`，`git commit`，`git push`，`git checkout`，`git branch`，`git merge`
- **导航**：`cd`，`pwd`，`which`
- **进程控制**：`kill`，`pkill`
- **包管理**：`npm install`，`npm publish`，`pip install`
- **简单输出**：`echo`，`printf`

**其他所有情况 → `ctx_execute` 或 `ctx_execute_file`。** 任何读取、查询、获取、列出、记录、测试、构建、差异、检查或调用外部服务的命令。这包括所有 CLIs（gh，aws，kubectl，docker，terraform，wrangler，fly，heroku，gcloud 等）—— 数千个，无法全部列出。

**不确定时使用上下文模式。** 每减少 KB 的不必要上下文，都会提高整个会话的质量和速度。

## 决策树

```
即将运行命令 / 读取文件 / 调用 API？
│
├── 命令在 Bash 白名单（文件修改、Git 写入、导航、echo）？
│   └── 使用 Bash
│
├── 输出可能较大或不确定？
│   └── 使用上下文模式 ctx_execute 或 ctx_execute_file
│
├── 获取网页文档或 HTML 页面？
│   └── 使用 ctx_fetch_and_index → ctx_search
│
├── 使用 Playwright（导航、截图、控制台、网络）？
│   └── 始终使用文件名参数保存到文件，然后：
│       browser_snapshot(filename) → ctx_index(path) 或 ctx_execute_file(path)
│       browser_console_messages(filename) → ctx_execute_file(path)
│       browser_network_requests(filename) → ctx_execute_file(path)
│       ⚠ browser_navigate 自动返回截图——忽略它，
│         使用 browser_snapshot(filename) 进行任何检查。
│       ⚠ Playwright MCP 使用单个浏览器实例——不安全并行。
│         对于并行浏览器操作，通过 execute 使用 agent-browser。
│
├── 使用 agent-browser（安全并行的浏览器自动化）？
│   └── 通过 execute（shell）运行——每个调用都有自己的子进程：
│       execute("agent-browser open example.com && agent-browser snapshot -i -c")
│       ✓ 支持用于隔离浏览器实例的会话
│       ✓ 安全用于并行子代理执行
│       ✓ 轻量级可访问性树，基于引用的交互
│
├── 处理其他 MCP 工具（Context7、GitHub API 等）的输出？
│   ├── 输出已从先前工具调用中加载到上下文中？
│   │   └── 直接使用。不要用 ctx_index(content: ...) 重新索引。
│   ├── 需要多次搜索输出？
│   │   └── 通过 ctx_execute 保存到文件，然后 ctx_index(path) → ctx_search
│   └── 单次提取？
│       └── 通过 ctx_execute 保存到文件，然后 ctx_execute_file(path)
│
└── 读取文件以分析/总结（非编辑）？
    └── 使用 ctx_execute_file（文件加载到 FILE_CONTENT，而不是上下文）
```

## 使用每种工具的时机

| 情况 | 工具 | 示例 |
|------|------|------|
| 调用 API 端点 | `ctx_execute` | `fetch('http://localhost:3000/api/orders')` |
| 运行返回数据的 CLI | `ctx_execute` | `gh pr list`，`aws s3 ls`，`kubectl get pods` |
| 运行测试 | `ctx_execute` | `npm test`，`pytest`，`go test ./...` |
| Git 操作 | `ctx_execute` | `git log --oneline -50`，`git diff HEAD~5` |
| Docker/K8s 检查 | `ctx_execute` | `docker stats --no-stream`，`kubectl describe pod` |
| 读取日志文件 | `ctx_execute_file` | 解析 access.log，error.log，构建输出 |
| 读取数据文件 | `ctx_execute_file` | 分析 CSV，JSON，YAML，XML |
| 读取源代码以分析 | `ctx_execute_file` | 计数函数，查找模式，提取指标 |
| 获取网页文档 | `ctx_fetch_and_index` | 索引 React/Next.js/Zod 文档，然后搜索 |
| Playwright 截图 | `browser_snapshot(filename)` → `ctx_index(path)` → `ctx_search` | 保存到文件，服务器端索引，查询 |
| Playwright 截图（单次） | `browser_snapshot(filename)` → `ctx_execute_file(path)` | 保存到文件，沙盒中提取 |
| Playwright 控制台/网络 | `browser_*(filename)` → `ctx_execute_file(path)` | 保存到文件，沙盒中分析 |
| MCP 输出（已加载到上下文中） | 直接使用 | 不要重新索引——它已经被加载 |
| MCP 输出（需要多次查询） | `ctx_execute` 保存 → `ctx_index(path)` → `ctx_search` | 首先保存到文件，服务器端索引 |
| 清除索引的 KB 内容 | `ctx_purge(confirm: true)` | 永久删除所有索引内容 |

## 自动触发

对于以下任何情况，无需询问直接使用上下文模式：

- **API 调试**： "访问此端点"，"调用 API"，"检查响应"，"在响应中查找错误"
- **日志分析**： "检查日志"，"什么错误"，"读取 access.log"，"调试 500 错误"
- **测试运行**： "运行测试"，"检查测试是否通过"，"测试套件输出"
- **Git 历史记录**： "显示最近的提交"，"git log"，"发生了什么变化"，"分支之间的差异"
- **数据检查**： "查看 CSV"，"解析 JSON"，"分析配置"
- **基础设施**： "列出容器"，"检查 Pod"，"S3 桶"，"显示正在运行的服务"
- **依赖审计**： "检查依赖项"，"过时的包"，"安全审计"
- **构建输出**： "构建项目"，"检查警告"，"编译错误"
- **代码指标**： "计数行数"，"查找 TODO"，"函数计数"，"分析代码库"
- **网页文档查询**： "查找文档"，"检查 API 参考"，"查找示例"

## 语言选择

| 情况 | 语言 | 原因 |
|------|------|------|
| HTTP/API 调用，JSON | `javascript` | 本地 fetch，JSON.parse，async/await |
| 数据分析，CSV，统计 | `python` | csv，statistics，collections，re |
| 带管道的 Shell 命令 | `shell` | grep，awk，jq，本地工具 |
| 文件模式匹配 | `shell` | find，wc，sort，uniq |

## 搜索查询策略

- BM25 使用 **OR 语义**——匹配更多术语的结果会自动排名更高
- 每个查询使用 2-4 个具体的技术术语
- **始终使用 `source` 参数** 当多个文档被索引时，以避免跨源污染
  - 部分匹配有效：`source: "Node"` 匹配 `"Node.js v22 CHANGELOG"`
- **始终使用 `queries` 数组**——在一个调用中批量所有搜索问题：
  - `ctx_search(queries: ["transform pipe", "refine superRefine", "coerce codec"], source: "Zod")`
  - 永远不要进行多个单独的 ctx_search() 调用——将所有查询放在一个数组中

## 外部文档

- **始终使用 `ctx_fetch_and_index`** 用于外部文档——绝对不要用 `cat` 或 `ctx_execute` 使用本地路径来处理您不拥有的包
- 对于 GitHub 托管的项目的，使用原始 URL：`https://raw.githubusercontent.com/org/repo/main/CHANGELOG.md`
- 索引后，在搜索中使用 `source` 参数来限制结果到该特定文档

## 关键规则

1. **始终 console.log/print 你的发现。** stdout 是所有进入上下文的内容。没有输出 = 浪费调用。
2. **编写分析代码，而不仅仅是数据转储。** 不要 `console.log(JSON.stringify(data))`——先分析，再打印发现。
3. **输出要具体。** 打印错误详情，包括 ID，行号，确切值——而不仅仅是计数。
4. **对于需要编辑的文件**：使用正常读取工具。上下文模式用于分析，而不是编辑。
5. **对于 Bash 白名单命令**：使用 Bash 进行文件修改，Git 写入，导航，进程控制，包安装和 echo。其他所有情况都通过上下文模式。
6. **永远不要使用 `ctx_index(content: large_data)`。** 使用 `ctx_index(path: ...)` 从服务器端读取文件。`content` 参数将数据通过上下文作为工具参数发送——仅用于小段内联文本。
7. **始终在 Playwright 工具上使用 `filename` 参数** (`browser_snapshot`，`browser_console_messages`，`browser_network_requests`)。没有它，完整输出将进入上下文。
8. **不要重新索引已经进入上下文的数据。** 如果一个 MCP 工具在先前响应中返回了数据，它已经被加载——直接使用或先保存到文件。

## 沙盒数据工作流

<sandboxed_data_workflow>
  <critical_rule>
    使用支持保存到文件的工具时：始终使用 'filename' 参数。
    永远不要直接将大型原始数据返回给上下文。
  </critical_rule>
  <workflow>
    LargeDataTool(filename: "path") → mcp__context-mode__ctx_index(path: "path") → ctx_search()
  </workflow>
</sandboxed_data_workflow>

这是无论源工具（Playwright，GitHub API，AWS CLI 等）如何，保存上下文内容的通用模式。

## 示例

### 调试 API 端点
```javascript
const resp = await fetch('http://localhost:3000/api/orders');
const { orders } = await resp.json();

const bugs = [];
const negQty = orders.filter(o => o.quantity < 0);
if (negQty.length) bugs.push(`Negative qty: ${negQty.map(o => o.id).join(', ')}`);

const nullFields = orders.filter(o => !o.product || !o.customer);
if (nullFields.length) bugs.push(`Null fields: ${nullFields.map(o => o.id).join(', ')}`);

console.log(`${orders.length} orders, ${bugs.length} bugs found:`);
bugs.forEach(b => console.log(`- ${b}`));
```

### 分析测试输出
```shell
npm test 2>&1
echo "EXIT=$?"
```

### 检查 GitHub PRs
```shell
gh pr list --json number,title,state,reviewDecision --jq '.[] | "\(.number) [\(.state)] \(.title) — \(.reviewDecision // "no review")"'
```

### 读取和分析大文件
```python
# FILE_CONTENT 是由 ctx_execute_file 预加载的
import json
data = json.loads(FILE_CONTENT)
print(f"Records: {len(data)}")
# ... 分析并打印发现
```

## 浏览器与 Playwright 集成

**当任务涉及 Playwright 截图、截图或页面检查时，始终通过文件 → 沙盒路由。**

Playwright `browser_snapshot` 返回 10K–135K 个 token 的可访问性树数据。调用它而不带 `filename` 会将所有这些数据倒入上下文。将输出传递给 `ctx_index(content: ...)` 会将数据第二次作为参数发送到上下文。两者都是错误的。

**关键洞察**：`browser_snapshot` 有一个 `filename` 参数可以保存到文件而不是返回到上下文。`ctx_index` 有一个 `path` 参数可以从服务器端读取文件。`ctx_execute_file` 在沙盒中处理文件。**这些都不接触上下文。**

### 工作流 A：截图 → 文件 → 索引 → 搜索（多个查询）

```
步骤 1: browser_snapshot(filename: "/tmp/playwright-snapshot.md")
        → 保存到文件，返回 ~50B 确认（不是 135K tokens）

步骤 2: ctx_index(path: "/tmp/playwright-snapshot.md", source: "Playwright snapshot")
        → 从服务器端读取文件，索引到 FTS5，返回 ~80B 确认

步骤 3: ctx_search(queries: ["login form email password"], source: "Playwright")
        → 只返回匹配的片段 (~300B)
```

**总上下文：~430B** 而不是 270K tokens。真正的 99% 节省。

### 工作流 B：截图 → 文件 → 执行文件（单次提取）

```
步骤 1: browser_snapshot(filename: "/tmp/playwright-snapshot.md")
        → 保存到文件，返回 ~50B 确认

步骤 2: ctx_execute_file(path: "/tmp/playwright-snapshot.md", language: "javascript", code: "
          const links = [...FILE_CONTENT.matchAll(/- link \"([^\"]+)\"/g)].map(m => m[1]);
          const buttons = [...FILE_CONTENT.matchAll(/- button \"([^\"]+)\"/g)].map(m => m[1]);
          const inputs = [...FILE_CONTENT.matchAll(/- textbox|- checkbox|- radio/g)];
          console.log('Links:', links.length, '| Buttons:', buttons.length, '| Inputs:', inputs.length);
          console.log('Navigation:', links.slice(0, 10).join(', '));
        ")
        → 沙盒中处理，返回 ~200B 摘要
```

**总上下文：~250B** 而不是 135K tokens。

### 工作流 C：控制台 & 网络（如果大型则保存到文件）

```
browser_console_messages(level: "error", filename: "/tmp/console.md")
→ ctx_execute_file(path: "/tmp/console.md", ...) 或 ctx_index(path: "/tmp/console.md", ...)

browser_network_requests(includeStatic: false, filename: "/tmp/network.md")
→ ctx_execute_file(path: "/tmp/network.md", ...) 或 ctx_index(path: "/tmp/network.md", ...)
```

### 关键：为什么 `filename` + `path` 是强制性的

| 方法 | 上下文成本 | 正确？ |
|------|----------|------|
| `browser_snapshot()` → 原始数据进入上下文 | **135K tokens** | 否 |
| `browser_snapshot()` → `ctx_index(content: raw)` | **270K tokens**（加倍！） | 否 |
| `browser_snapshot(filename)` → `ctx_index(path)` → `ctx_search` | **~430B** | 是 |
| `browser_snapshot(filename)` → `ctx_execute_file(path)` | **~250B** | 是 |

### 关键规则

> **调用 `browser_snapshot`，`browser_console_messages` 或 `browser_network_requests` 时始终使用 `filename` 参数。**
> 然后通过 `ctx_index(path: ...)` 或 `ctx_execute_file(path: ...)` 处理——永远不要 `ctx_index(content: ...)`.
>
> 数据流：**Playwright → 文件 → 服务器端读取 → 上下文**。永远不要：**Playwright → 上下文 → ctx_index(content) → 上下文再次**。

## 子代理使用

子代理自动通过 PreToolUse 钩子接收上下文模式工具路由。你不需要手动将工具名称添加到子代理提示中——钩子会注入它们。只需编写自然任务描述。

## 反模式

- 通过 Bash 使用 `curl http://api/endpoint` → 50KB 淹没上下文。使用 `ctx_execute` 与 fetch 代替。
- 通过 Bash 使用 `cat large-file.json` → 整个文件在上下文中。使用 `ctx_execute_file` 代替。
- 通过 Bash 使用 `gh pr list` → 原始 JSON 在上下文中。使用 `ctx_execute` 与 `--jq` 过滤器代替。
- Bash 输出通过 `| head -20` 管道 → 你会丢失其余部分。使用 `ctx_execute` 分析所有数据并打印摘要。
- 在捕获上游合并 `ctx_execute` 输出时缩小 → `ctx_execute` 捕获，`ctx_search` 过滤；合并层会丢弃索引从未看到的数据。参见 `references/anti-patterns.md` §8。
- 通过 Bash 运行 `npm test` → 完整测试输出在上下文中。使用 `ctx_execute` 捕获并总结。
- 调用 `browser_snapshot()` 而不带 `filename` 参数 → 135K tokens 淹没上下文。**始终**使用 `browser_snapshot(filename: "/tmp/snap.md")`。
- 调用 `browser_console_messages()` 或 `browser_network_requests()` 而不带 `filename` → 整个输出淹没上下文。**始终**使用 `filename` 参数。
- 将任何大型数据传递给 `ctx_index(content: ...)` → 数据作为参数进入上下文。**始终**使用 `ctx_index(path: ...)` 从服务器端读取。`content` 参数仅用于你自己编写的短段内联文本。
- 调用 MCP 工具（Context7 `query-docs`，GitHub API 等）然后将响应传递给 `ctx_index(content: response)` → **加倍**上下文使用。响应已经在上下文中——直接使用或先保存到文件。
- 忽略 `browser_navigate` 自动截图 → 导航响应包含一个完整的页面截图。不要依赖它进行检查——单独调用 `browser_snapshot(filename)`。
- 期望 `ctx_stats` 重置或清除任何内容 → `ctx_stats` 是只读的（只显示统计信息）。使用 `ctx_purge(confirm: true)` 永久删除所有索引内容。

## 参考文件

- [JavaScript/TypeScript 模式](./references/patterns-javascript.md)
- [Python 模式](./references/patterns-python.md)
- [Shell 模式](./references/patterns-shell.md)
- [反模式 & 常见错误](./references/anti-patterns.md)
