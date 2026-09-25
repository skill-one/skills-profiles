# Slack 搜索

此技能提供有效搜索 Slack 以查找消息、文件和信息的指导。

## 使用场景

无论何时您需要在 Slack 中查找信息，都可以使用此技能——包括当用户要求您定位消息、对话、文件或人员，或当您需要在回答有关 Slack 中发生情况的问题之前收集背景信息时。

## 搜索工具概述

| 工具 | 使用场景 |
|------|----------|
| `slack_search_public` | 仅搜索公共频道。无需用户授权。 |
| `slack_search_public_and_private` | 搜索所有频道，包括私密频道、私信和群组私信。需要用户授权。 |
| `slack_search_channels` | 通过名称或描述查找频道。 |
| `slack_search_users` | 通过姓名、电子邮件或角色查找人员。 |

## 搜索策略

### 先宽泛，再缩小范围

1. 从简单的关键词或自然语言问题开始。
2. 如果结果过多，添加过滤器（`in:`、`from:`、日期范围）。
3. 如果结果过少，移除过滤器并尝试同义词或相关术语。

### 选择正确的搜索模式

- **自然语言问题**（例如，"项目 X 的截止日期是什么？"）—— 适用于模糊、概念性搜索，您不知道确切的搜索关键词时。
- **关键词搜索**（例如，`project X deadline`）—— 适用于查找特定、确切的内容。

### 使用多次搜索

不要依赖单一搜索。将复杂问题分解为更小的搜索：
- 首先搜索主题
- 然后搜索特定人员的贡献
- 然后在特定频道中搜索

## 搜索修饰符参考

### 位置过滤器
- `in:channel-name` — 在特定频道内搜索
- `in:<#C123456>` — 通过 ID 在频道中搜索
- `-in:channel-name` — 排除一个频道
- `in:<@U123456>` — 在与用户的私信中搜索

### 用户过滤器
- `from:<@U123456>` — 来自特定用户（通过 ID）的消息
- `from:username` — 来自用户（通过 Slack 用户名）的消息
- `to:me` — 直接发送给您您的消息

### 内容过滤器
- `is:thread` — 仅搜索线程消息
- `has:pin` — 固定消息
- `has:link` — 包含链接的消息
- `has:file` — 带有文件附件的消息
- `has::emoji:` — 带有特定反应的消息

### 日期过滤器
- `before:YYYY-MM-DD` — 日期之前的消息
- `after:YYYY-MM-DD` — 日期之后的消息
- `on:YYYY-MM-DD` — 特定日期的消息
- `during:month` — 特定月份内的消息（例如，`during:january`）

### 文本匹配
- `"exact phrase"` — 匹配确切的短语
- `-word` — 排除包含某个词的消息
- `wild*` — 通配符匹配（`*` 之前至少有 3 个字符）

## 文件搜索

要搜索文件，请使用 `content_types="files"` 参数和类型过滤器：
- `type:images` — 图片文件
- `type:documents` — 文档文件
- `type:pdfs` — PDF 文件
- `type:spreadsheets` — 电子表格文件
- `type:canvases` — Slack 画布

示例：`content_types="files" type:pdfs budget after:2025-01-01`

## 对结果进行跟进

找到相关消息后：
- 使用 `slack_read_thread` 获取任何线程消息的完整线程上下文。
- 使用 `slack_read_channel` 并使用 `oldest`/`latest` 时间戳读取周围消息以获取上下文。
- 使用 `slack_read_user_profile` 识别结果中出现的用户 ID 是谁。

## 常见陷阱

- **布尔运算符无效。** `AND`、`OR`、`NOT` 不被支持。使用空格（隐式 AND）和 `-` 进行排除。
- **括号无效。** 不要尝试用 `()` 组合搜索词。
- **搜索不是实时。** 非常最近的消息（最后几秒）可能不会出现在搜索结果中。使用 `slack_read_channel` 获取最新的消息。
- **私密频道访问。** 当您需要包含私密频道时，请使用 `slack_search_public_and_private`，但请注意这需要用户授权。
