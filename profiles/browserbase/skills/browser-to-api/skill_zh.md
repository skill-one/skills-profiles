# 浏览器到API

基于重放驱动的API发现。消费一个`browser-trace`捕获，将其CDP请求/响应事件配对，模板化观察到的URL，从样本中推断JSON模式，并发出**OpenAPI 3.1**文档以及人类可读的覆盖报告。

这项技能**不会捕获流量**。它是在`browser-trace`的`cdp/network/*.jsonl`桶上执行的纯离线后处理。这两个技能的组合如下：

```
browser-trace    →  .o11y/<run>/cdp/network/{requests,responses}.jsonl
browser-to-api   →  .o11y/<run>/api-spec/index.html + openapi.yaml + client.mjs
```

## 何时使用

- 用户需要一个第三方或未文档化的网站API的OpenAPI文档。
- 用户有一个`browser-trace`运行，并希望从中提取端点+模式。
- 用户正在构建针对未发布规范的网站的客户端/SDK。
- 用户需要一个覆盖报告，显示哪些流程将扩展规范。

如果用户想要**捕获**流量，请先引导他们使用`browser-trace`。

## 两步工作流程

### 1. 使用`browser-trace`捕获（可选地通过`browse network on`捕获正文）

```bash
# 本地示例，针对现有的可调试Chrome目标
TARGET=9222

node ../browser-trace/scripts/start-capture.mjs "$TARGET" my-site
browse open about:blank --cdp "$TARGET"
browse network on                                    # 捕获请求/响应正文
browse open https://example.com
# ...驱动你想要覆盖的任何流程...

# 在关闭捕获之前，先快照正文目录（临时目录是每个会话共享的，
# 所以如果你跳过这一步，后续的`browse network on`运行会将你的正文
# 与未来捕获写入的内容混合）。
cp -r "$(browse network path | jq -r .path)" .o11y/my-site/cdp/network/bodies/
browse network off

node ../browser-trace/scripts/stop-capture.mjs my-site
node ../browser-trace/scripts/bisect-cdp.mjs my-site
```

`browse network on`是**可选但强烈推荐**的——没有它，规范中没有响应体模式（`browse cdp`使用的CDP水龙头不嵌入正文）。有了它，CDP将请求正文（已经由CDP捕获）和响应正文都通过CDP `requestId`连接到跟踪中。

### 2. 生成规范

```bash
node scripts/discover.mjs --run .o11y/my-site
# → .o11y/my-site/api-spec/index.html          ← 打开这个
#   .o11y/my-site/api-spec/client.mjs
#   .o11y/my-site/api-spec/openapi.yaml
#   .o11y/my-site/api-spec/openapi.json
#   .o11y/my-site/api-spec/report.md
#   .o11y/my-site/api-spec/confidence.json
#   .o11y/my-site/api-spec/samples/*.json
#   .o11y/my-site/api-spec/intermediate/*.jsonl
```

`discover.mjs`会自动检测`<run>/cdp/network/bodies/`。要使用来自其他地方的正文捕获（例如，没有快照，想要实时`browse network`目录），请显式传递`--bodies <path>`。

### 3. 打开HTML报告

`discover.mjs`完成后，**始终打开生成的HTML报告**：

```bash
open .o11y/my-site/api-spec/index.html
```

报告是一个自包含的HTML文件（不需要服务器），它将每个发现的操作显示为可展开的卡片，包含变量、客户端使用情况、请求/响应示例，以及生成的`client.mjs`代码片段在底部。这是主要交付物——始终为用户打开它。

## CLI标志

| 标志 | 必须的 | 含义 |
|---|---|---|
| `--run <path>` | 是 | `browser-trace`运行目录的路径 |
| `--out <path>` | 否 | 输出目录；默认`<run>/api-spec/` |
| `--bodies <path>` | 否 | 要连接到跟踪中的`browse network`捕获目录（当存在时自动检测`<run>/cdp/network/bodies/`） |
| `--include <regex>` | 否 | 仅包含匹配正则表达式的URL（可重复） |
| `--exclude <regex>` | 否 | 排除匹配正则表达式的URL（附加到默认值；可重复） |
| `--origins <list>` | 否 | 用逗号分隔的起源允许列表（例如`api.example.com,example.com`） |
| `--format <yaml\|json\|both>` | 否 | 输出格式。默认`both` |
| `--title <string>` | 否 | OpenAPI `info.title`。默认从主要起源派生 |
| `--redact <list>` | 否 | 要额外隐藏的额外标头名称/JSON键（用逗号分隔） |
| `--min-samples <n>` | 否 | 包含的每个端点的最小样本数。默认`1` |
| `--stage <name>` | 否 | 仅运行一个阶段：`load`，`filter`，`normalize`，`infer`，`emit` |

## 输出布局

```
<run>/api-spec/
├── index.html                可视报告 — 打开这个（自包含，不需要服务器）
├── client.mjs                无依赖的fetch客户端，每个操作都有类型化的函数
├── openapi.yaml              机器可读的规范
├── openapi.json              镜像
├── report.md                 markdown摘要+curl示例
├── confidence.json           每个端点的置信度+规范化标志
├── samples/                  隐藏的请求/响应示例
│   └── <method>__<path-hash>.json
└── intermediate/             管道副产品（配对/过滤/端点jsonl）
```

## 从`browse cdp`和`browse network`中获取的内容

两个互补的捕获源：

| 来源 | 提供的内容 | 限制 |
|---|---|---|
| `browse cdp`（由`browser-trace`使用） | 请求方法/URL/标头/`postData`，响应状态/标头/mimeType，完整事件时间 | **不嵌入响应正文。** 正文必须使用`Network.getResponseBody`拉取，而水龙头不会这样做。 |
| `browse network on`（单独命令） | 磁盘上的请求正文**和**响应正文，按CDP `requestId`键 | 捕获目录是每个`browse`会话共享的；在另一个`browse network on`覆盖它之前，先快照它。 |

`discover.mjs`会在传递`--bodies <path>`（或将其存放在`<run>/cdp/network/bodies/`下，这是自动检测的）时从`browse network`目录中拉取正文。匹配是通过`requestId`进行的——`browse network`将`id`写入每个`request.json`中，我们直接连接。

正文存在时会发生什么变化：

- ✅ 路径模板化、查询参数模式、状态代码、内容类型——无论如何都一样。
- ✅ 请求体模式——来自CDP的`postData`就足够了；正文目录对于非`postData`情况是一个不错的附加功能。
- ✅ **响应体模式**——完全从真实样本中推断。如果没有正文，你会得到`{ description, content: <mimeType> }`骨架。

报告会标记每个没有响应体样本的端点。

## 自动噪声过滤

规范化阶段会自动分类并丢弃基础设施噪声：

- **跟踪/分析**——包含`/track`、`/pixel`、`/beacon`、`/impression`、`/pageview`、`/dag/v*`的路径
- **机器人防御**——Akamai（`/akam/`）、指纹有效载荷（`sensor_data`）、混淆的多段路径
- **会话管道**——`/session`、`/authenticate/start`、cookie同意、A/B实验端点
- **HTML页面渲染**——返回`text/html`的GET请求（渲染的页面，而不是API）

这通常会丢弃60-80%的捕获流量。`--include`标志可以挽救误报。

## GraphQL/多路复用端点分解

当单个端点（如`/dapi/fe/gql`）使用不同的`operationName`值调用时，该技能会自动将其分解为单独的逻辑操作。每个操作都有自己的：
- OpenAPI路径条目（例如`/dapi/fe/gql [Autocomplete]`）
- 仅从该操作的样本中推断的请求/响应模式
- 报告中的curl示例和变量表

检测基于正文字段（`operationName`、`method`、`action`）和查询参数（`opname`、`op`）。这涵盖了GraphQL（APQ和内联）、JSON-RPC以及类似的调度模式。

## 限制

- **覆盖范围受捕获流程限制。** 未在跟踪中执行的端点不会出现。该技能无法证明完整性。
- **模式是归纳的，而不是合同的。** 即使每个样本都包含该字段，服务器上的字段也可能是可选的。
- **认证是观察到的，而不是指定的。** 该技能会记录形状为认证的标头在`x-observed-auth`扩展中，但不会声明安全方案。
- **路径模板化是启发式的。** 数字/UUID/十六进制/slug模式按段检测。歧义的URL会在`confidence.json`中标记。
- **隐藏是尽力而为的。** 默认隐藏涵盖了常见的凭证，但特定于应用程序的秘密可能会漏过；使用`--redact`来处理已知的自定义标头/键。

## 最佳实践

1. **驱动你想要文档化的流程。** 浏览器跟踪越丰富，规范就越丰富。
2. **对嘈杂的网站使用`--origins`。** 营销页面会命中数十个分析主机；限制为你关心的API起源。
3. **首先检查`report.md`。** 它包含每个发现的操作的可用的curl示例和响应样本。
4. **将`--min-samples`提高到2+** 当你只想在最终文档中包含置信度高的端点时——丢弃长尾。
5. **与`browse network on`配对** 当响应体模式很重要时。CDP水龙头本身包含请求正文，但不包含响应正文。

有关管道内部和文件格式参考，请参阅[REFERENCE.md](REFERENCE.md)。
