使用此工作流程从 Meticulous 获取结构化的会话数据——Meticulous 记录的用户流程和网络模拟，它们涵盖了您的代码更改。

> 开始之前，运行 `meticulous-cli-update` 技能以确保 Meticulous CLI 和技能是最新版本——除非它已经在此对话中更早运行过，在这种情况下可以跳过。

## 第 1 步 — 查找相关会话并下载其数据

从 git 仓库的根目录运行以下命令：

```bash
meticulous local relevant-sessions --format=multi-file --minimum-times-to-cover-each-line=1
```

这将：

1. 识别出哪些记录的会话在当前分支上执行了更改的代码路径。
2. 将每个会话的数据下载为结构化的目录树到 `.meticulous/sessions/`。

**选项：**

| 选项                               | 类型         | 默认                | 描述                                                                                                                               |
| ------------------------------------ | ------------ | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `--format`                           | `multi-file` | —                      | 设置为 `multi-file` 以将每个相关会话的数据下载为结构化的目录树                                       |
| `--minimum-times-to-cover-each-line` | number       | —                      | 选择至少覆盖每行编辑的这么多会话，当有更多候选时选择最多样化的子集                                     |
| `--include-superfluous-sessions`     | boolean      | `false`                | 还包括那些测试了一些更改但在 `--minimum-times-to-cover-each-line` 下是多余的会话                   |
| `--outputDir`                        | string       | `.meticulous/sessions` | 多文件格式的输出目录                                                                                                              |
| `--showMaybeRelevant`                | boolean      | `false`                | 还显示可能受影响的会话                                                                                                             |
| `--startingPointSha`                 | string       | —                      | 仅考虑自该提交 SHA 之后的更改                                                                                                     |

## 第 2 步 — 理解输出结构

下载的数据按以下方式组织：

```
.meticulous/sessions/
  manifest.json                       # 所有会话的列表及其摘要元数据
  sessions/
    <sanitized-session-id>/           # 会话 ID 中的特殊字符被替换以保持文件系统安全
      summary.json                    # 会话概览：URL、视口、持续时间、事件计数
      user-events.json                # 用户交互序列（点击、输入、导航）
      network-requests/
        summary.json                  # 所有网络请求：方法、URL、状态（无正文）
        <order>.json                  # 单个请求/响应对（带正文）
      storage/
        cookies.json                  # 初始 Cookie 状态
        local-storage.json            # 初始 localStorage 状态
        session-storage.json          # 初始 sessionStorage（如果存在）
        indexed-db.json               # 初始 IndexedDB（如果存在）
      url-history.json                # 带时间戳的页面导航历史
      context.json                    # 功能标志、用户 ID、自定义上下文（如果存在）
      websockets/                     # WebSocket 数据（如果存在）
        summary.json                  # WebSocket 连接概览
        <connection-id>.json          # 每个连接的事件
```

## 第 3 步 — 浏览数据

1. **从 `manifest.json` 开始** 查看所有可用的会话。每个条目包括会话 ID、起始 URL、事件计数、持续时间和网络请求计数。选择与您的任务相关的会话。

2. **在会话目录中读取 `summary.json`** 以快速了解该会话的概览——起始 URL、视口大小、总持续时间以及事件数量。

3. **读取 `user-events.json`** 以了解用户流程。每个事件具有：
   - `type`：交互类型（例如，`click`、`input`、`scroll`）
   - `selector`：目标元素的 CSS 选择器
   - `timestampMs`：事件发生的时间
   - `coordinates`：点击位置（如果适用）

4. **浏览 `network-requests/summary.json`** 查看会话期间所有发出的 API 调用。每个条目显示 HTTP 方法、URL、状态码、内容类型和响应时间——没有响应正文，因此可以快速浏览。

5. **读取单个 `network-requests/<order>.json`** 文件以获取特定 API 调用的完整请求/响应数据。在编写测试时使用这些数据作为模拟数据。摘要中的 `order` 字段对应于文件名。

6. **检查 `storage/`** 文件如果您需要了解初始应用程序状态（Cookies、localStorage 等）。

## 第 4 步 — 使用数据用于测试

常见用例：

### 理解用户流程

读取 `user-events.json` 查看用户交互的确切序列。这告诉您用户点击了什么、输入了什么以及导航了什么，这有助于您理解您的代码更改需要支持什么。

### 创建网络模拟

使用网络请求文件为您的测试创建模拟响应：

1. 读取 `network-requests/summary.json` 找到相关的 API 端点。
2. 读取单个 `network-requests/<order>.json` 文件以获取完整的请求/响应对。
3. 使用 `response.content.text` 字段作为测试中的模拟响应数据。

### 验证覆盖率

将用户事件和网络请求与您的代码更改进行交叉引用，以验证会话是否涵盖了您修改的代码路径。

## 替代方案：下载特定会话

如果您已经知道需要哪些会话 ID，可以直接下载它们：

```bash
# CLI
meticulous download session --sessionId=<id> --format=multi-file

# MCP (返回相同的结构化数据而不是写入磁盘)
get_session_data(sessionId="<id>")
```

CLI 默认写入 `.meticulous/sessions/`；使用 `--outputDir` 更改输出位置。

## 最后一步 — 向 Meticulous 提交反馈

使用会话数据完成后，向 Meticulous 团队提交一条简短的反馈笔记：会话数据是否涵盖了您需要的流程，以及缺少了哪些信息或哪些信息会使任务更简单？

```bash
# CLI
meticulous agent submit-feedback --message="<一句话或两句话>" --outcome=<helped|neutral|hindered> --skill=meticulous-use-session-data

# MCP
submit_feedback(message="<一句话或两句话>", outcome="<helped|neutral|hindered>", skill="meticulous-use-session-data")
```
