---
name: browser-to-api
description: 将网站的可见 HTTP 流量通过分析 `browser-trace` 捕获转换为最佳努力 OpenAPI 3.1 规范。适用于用户希望从浏览器会话中发现/提取 API 端点、从网络流量构建 OpenAPI 文档，或为客户端集成文档化第三方网站的 XHR/fetch 接口。
---

# 浏览器到 API

基于重放驱动的 API 发现。消费一个 `browser-trace` 捕获，将其 CDP 请求/响应事件配对，模板化观察到的 URL，从样本中推断 JSON 架构，并生成一个 **OpenAPI 3.1** 文档以及人类可读的覆盖报告。

这项技能 **不会捕获流量**。它是在 `browser-trace` 的 `cdp/network/*.jsonl` 桶上执行的离线后处理。这两个技能的组合如下：

```
browser-trace    →  .o11y/<run>/cdp/network/{requests,responses}.jsonl
browser-to-api   →  .o11y/<run>/api-spec/index.html + openapi.yaml + client.mjs
```

## 何时使用

- 用户需要一个第三方或未文档化的网站 API 的 OpenAPI 文档。
- 用户有一个 `browser-trace` 运行，并希望从中提取端点 + 架构。
- 用户正在为不发布规范的网站构建客户端/SDK。
- 用户需要一个覆盖报告，显示哪些流程可以扩展规范。

如果用户想要 **捕获** 流量，请先引导他们使用 `browser-trace`。

## 两步工作流程

### 1. 使用 `browser-trace` 捕获（可选地通过 `browse network on` 捕获正文）

```bash
# 本地示例，针对现有的可调试 Chrome 目标
TARGET=9222

node ../browser-trace/scripts/start-capture.mjs "$TARGET" my-site
browse open about:blank --cdp "$TARGET"
browse network on                                    # 捕获请求/响应对正文
browse open https://example.com
# ...驱动你想要覆盖的任何流程...

# 在关闭捕获之前快照正文目录（临时目录是按会话共享的，
# 因此后续的 `browse network on` 运行会将你的正文与未来捕获写入的内容混合，
# 如果你跳过这一步）。
cp -r "$(browse network path | jq -r .path)" .o11y/my-site/cdp/network/bodies/
browse network off

node ../browser-trace/scripts/stop-capture.mjs my-site
node ../browser-trace/scripts/bisect-cdp.mjs my-site
```

`browse network on` 是 **可选但强烈推荐** 的——没有它，规范中没有响应正文架构（`browse cdp` 使用的 CDP 水管不嵌入正文）。有了它，CDP 会将请求正文（已经由 CDP 捕获）和响应正文通过 CDP `requestId` 加入到跟踪中。

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

`discover.mjs` 会自动检测 `<run>/cdp/network/bodies/`。要使用来自其他地方的正文捕获（例如，没有快照，想要实时 `browse network` 目录），请显式传递 `--bodies <path>`。

### 3. 打开 HTML 报告

`discover.mjs` 完成后，**始终打开生成的 HTML 报告**：

```bash
open .o11y/my-site/api-spec/index.html
```

报告是一个自包含的 HTML 文件（不需要服务器），它将每个发现的操作显示为可展开的卡片，包含变量、客户端使用情况、请求/响应示例，以及底部的生成 `client.mjs` 片段。这是主要交付物——始终为用户打开它。

## CLI 标志

| 标志 | 必须的 | 含义 |
|---|---|---|
| `--run <path>` | 是 | `browser-trace` 运行目录的路径 |
| `--out <path>` | 否 | 输出目录；默认 `<run>/api-spec/` |
| `--bodies <path>` | 否 | 要加入跟踪的 `browse network` 捕获目录（当存在时自动检测 `<run>/cdp/network/bodies/`） |
| `--include <regex>` | 否 | 仅包含匹配正则表达式的 URL（可重复） |
| `--exclude <regex>` | 否 | 排除匹配正则表达式的 URL（可重复；除了默认值） |
| `--origins <list>` | 否 | 以逗号分隔的来源允许列表（例如 `api.example.com,example.com`） |
| `--format <yaml\|json\|both>` | 否 | 输出格式。默认 `both` |
| `--title <string>` | 否 | OpenAPI `info.title`。默认从主要来源派生 |
| `--redact <list>` | 否 | 要删除的额外头名称 / JSON 键（以逗号分隔） |
| `--min-samples <n>` | 否 | 包含的最小样本数。默认 `1` |
| `--stage <name>` | 否 | 仅运行一个阶段：`load`，`filter`，`normalize`，`infer`，`emit` |

## 输出布局

```
<run>/api-spec/
├── index.html                可视报告 — 打开这个（自包含，不需要服务器）
├── client.mjs                无依赖的 fetch 客户端，每个操作都有类型化的函数
├── openapi.yaml              机器可读的规范
├── openapi.json              镜像
├── report.md                 Markdown 摘要 + curl 示例
├── confidence.json           每个端点的置信度 + 规范化标志
├── samples/                  删除后的请求/响应示例
│   └── <method>__<path-hash>.json
└── intermediate/             管道副产品（配对/过滤/端点 jsonl）
```

## 从 `browse cdp` 和 `browse network` 中获得的内容

两个互补的捕获源：

| 来源 | 提供 | 限制 |
|---|---|---|
| `browse cdp`（由 `browser-trace` 使用） | 请求方法/URL/头/`postData`，响应状态/头/媒体类型，完整事件时间 | **不嵌入响应正文。** 正文必须使用 `Network.getResponseBody` 拉取，而水管不会做这件事。 |
| `browse network on`（单独命令） | 请求正文 **和** 响应正文保存在磁盘上，按 CDP `requestId` 键 | 捕获目录按 `browse` 会话共享；在另一个 `browse network on` 覆盖之前快照它。 |

`discover.mjs` 如果传递 `--bodies <path>`（或将其存放在 `<run>/cdp/network/bodies/` 下，这是自动检测的）将从 `browse network` 目录中拉取正文。匹配是通过 `requestId` 进行的——`browse network` 将其写入每个 `request.json` 作为 `id`，我们直接连接。

正文存在时会发生什么变化：

- ✅ 路径模板化、查询参数架构、状态代码、内容类型——无论如何都一样。
- ✅ 请求正文架构——`postData` 从 CDP 足够；正文目录对于非 `postData` 情况是一个不错的功能。
- ✅ **响应正文架构**——完全从真实样本中推断。没有正文时你会得到 `{ description, content: <mimeType> }` 骨架。

报告会标记每个没有响应正文样本的端点。

## 自动噪声过滤

规范化阶段会自动分类并丢弃基础设施噪声：

- **跟踪 / 分析** — 包含 `/track`，`/pixel`，`/beacon`，`/impression`，`/pageview`，`/dag/v*` 的路径
- **机器人防御** — Akamai (`/akam/`), 指纹有效载荷 (`sensor_data`), 混淆的多段路径
- **会话管道** — `/session`，`/authenticate/start`，Cookie 同意，A/B 实验端点
- **HTML 页面渲染** — 返回 `text/html` 的 GET 请求（渲染的页面，不是 API）

这通常会丢弃 60-80% 的捕获流量。`--include` 标志可以挽救一个误报。

## GraphQL / 多路复用端点分解

当单个端点（如 `/dapi/fe/gql`）使用不同的 `operationName` 值调用时，该技能会自动将其分解为多个逻辑操作。每个操作都有自己的：
- OpenAPI 路径条目（例如 `/dapi/fe/gql [Autocomplete]`）
- 仅从该操作的样本中推断的请求/响应架构
- 报告中的 Curl 示例和变量表

检测基于正文字段（`operationName`，`method`，`action`）和查询参数（`opname`，`op`）。这涵盖了 GraphQL（APQ 和内联），JSON-RPC，以及类似的调度模式。

## 限制

- **覆盖范围受捕获流程限制。** 未在跟踪中执行的端点不会出现。该技能无法证明完整性。
- **架构是归纳的，不是合同的。** 即使每个样本都包含它，服务器上的字段也可能是可选的。
- **认证是观察到的，不是指定的。** 该技能会记录形状为认证的头在 `x-observed-auth` 扩展中，但不会声明安全方案。
- **路径模板化是启发式的。** 数字 / UUID / 十六进制 / 段落模式按段检测。歧义的 URL 会标记在 `confidence.json` 中。
- **删除是尽力而为的。** 默认删除覆盖常见的凭证，但特定于应用程序的密钥可能会泄露；使用 `--redact` 用于已知的自定义头/键。

## 最佳实践

1. **驱动你想要文档化的流程。** 浏览器跟踪越丰富，规范就越丰富。
2. **对嘈杂的网站使用 `--origins`。** 营销页面会命中几十个分析主机；限制为你关心的 API 来源。
3. **首先检查 `report.md`。** 它包含可用的 curl 示例和每个发现的操作的响应样本。
4. **将 `--min-samples` 提高到 2+** 当你只想在最终文档中包含置信度高的端点时——丢弃长尾。
5. **与 `browse network on` 配合使用** 当响应正文架构很重要时。CDP 水管本身包含请求正文，但不包含响应正文。

有关管道内部和文件格式参考，请参阅 [REFERENCE.md](REFERENCE.md)。
