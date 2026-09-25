# Cargo — 托管的MCP服务器

Cargo有两个界面。本文档的其余部分记录了CLI。这个部分记录了`https://mcp.getcargo.io/mcp`，以及更有用的**何时使用哪个**。

> **这里有三样东西被称为MCP。** 这项技能是Cargo运行的**托管服务器**，您可以将客户端指向它。从自己的工作区发布一个经过策划的服务器（`ai mcp-server create`，然后`cargo-ai mcp`通过stdio）并连接到其他人的服务器（`release update-draft --mcp-clients`）都是[`cargo-ai`](../cargo-ai/SKILL.md)。在回答之前，请先确认用户指的是哪一个：这些词语是相同的，而答案之间没有任何关联。

## 哪个界面

| 任务 | 界面 |
| --- | --- |
| 执行一个操作，或对许多记录执行一个操作 | 任意；如果已经连接，则为MCP |
| 查找Cargo能做什么，以及它的成本 | 任意（`search_actions`是MCP的一半） |
| 从模型中读取记录 | 任意 |
| 仓库SQL、聚合、连接 | **CLI** ([`cargo-storage`](../cargo-storage/SKILL.md)) |
| 构建或编辑多步骤工作流、工具或剧本 | **CLI** ([`cargo-orchestration`](../cargo-orchestration/SKILL.md)) |
| 工作区作为代码，计划和部署 | **CLI** ([`cargo-project`](../cargo-project/SKILL.md)) |
| 提供邮箱、预热、发送 | **CLI** ([`cargo-mailbox-management`](../cargo-mailbox-management/SKILL.md)) |
| 段落、连接器、内容库、警报、托管、计费管理 | **CLI** |
| 完全没有shell（ChatGPT、Claude桌面、claude.ai、n8n） | **MCP**，并明确说明无法实现的功能 |

表格下方的规则：**MCP是运行时，CLI是平台。** 十三种工具涵盖了发现操作、执行操作、监视操作完成以及读取数据。所有构建可重用内容的功能都仅限于CLI。持有两者的代理应该优先为用户将重新运行或版本控制的内容使用CLI，而为一次性执行在对话中使用MCP。

当任务路由到CLI时，这是整个启动过程：

```bash
npm install -g @cargo-ai/cli
cargo-ai login --email you@company.com   # 通过邮件代码登录，无需浏览器；首次使用时创建帐户
cargo-ai whoami                          # 在执行任何消耗操作之前确认工作区
```

## 连接

端点是`https://mcp.getcargo.io/mcp`，流式传输HTTP。未经身份验证的请求将返回`401`，并带有包含`resource_metadata`的`WWW-Authenticate`挑战，因此OAuth客户端可以发现授权服务器、注册并提示用户，无需除URL之外的其他配置。首次连接时返回`401`是握手，而不是错误。

```bash
claude mcp add --transport http cargo https://mcp.getcargo.io/mcp
```

任何接收JSON块（Claude桌面、Cursor、项目`.mcp.json`）的客户端：

```json
{
  "mcpServers": {
    "cargo": {
      "type": "http",
      "url": "https://mcp.getcargo.io/mcp"
    }
  }
}
```

对于CI、无头代理或没有OAuth的客户端，从**设置 > API**中传递工作区范围的API令牌。从环境中读取它；永远不要内联值：

```json
{
  "mcpServers": {
    "cargo": {
      "type": "http",
      "url": "https://mcp.getcargo.io/mcp",
      "headers": { "Authorization": "Bearer ${CARGO_API_TOKEN}" }
    }
  }
}
```

**工具列表不是固定的。** 端点提供以下平台工具以及工作区使用`defineMcpServer`发布的内容，因此两个令牌可以看到两个不同的列表。读取您实际获得的列表，而不是这里记录的列表。

## 脊干

```
whoami                 → 我在哪个工作区，有多少积分
search_actions         → 查找操作，并读取其成本
get_action_schema      → 它需要什么输入
autocomplete_action    → 解析需要选择ID的字段（HubSpot对象类型、Slack频道）
execute_action         │ 单个记录
execute_action_batch   │ 多个记录
get_run / get_batch    → 在结果为"executing"时轮询
```

对于数据：`list_models` → `describe_model` → `query_models`。此外，`list_runs`列出了最近的临时运行，而`get_usage`将过去7天的积分支出按集成分解。

**每个会话都以`whoami`开始。** 令牌将会话绑定到恰好一个工作区，并且没有标志可以覆盖它。指向错误工作区的会话将返回看似合理但自信错误的读取：模型是真实的，记录也是真实的，它们只是属于其他人。在采取任何行动之前，将工作区名称重命名为用户。

**`search_actions`在您执行操作之前定价工作。** 每个结果旁边都带有`credits[].cost`，您将`action`对象原封不动地传递给下游所有内容：

```json
{
  "name": "丰富人员并查找电子邮件",
  "credits": [{ "cost": 0.1, "type": "fixed" }],
  "action": {
    "kind": "connector",
    "integrationSlug": "aiArk",
    "actionSlug": "enrichPerson",
    "connectorUuid": "7bb944ec-0254-44bc-b0e4-8a56378e80cf"
  }
}
```

**将`action`对象原封不动地传递，不要添加`config`键。** 输入属于`data`（单个）或`records`（批量）——永远不会在`config`中，`config`是*节点的*配置，在顶层操作上没有意义。放置在错误位置的输入将被静默丢弃，并且操作将没有任何输入运行，因此未解释的空结果值得首先检查。

`get_action_schema`采用相同的对：操作，加上可选的`data`，用于那些输出取决于其输入的操作——HubSpot对象类型或目标表格决定返回哪些字段。CLI的`orchestration action get-output-schema`行为相同。

返回四种`kind`值：`connector`（第三方集成）、`native`（内置平台操作）、`tool`（此工作区中的保存工作流）和`agent`（此工作区中的AI代理）。使用`kind`和`integrationSlug`过滤器缩小嘈杂的目录。

## 三种可能出错的方式

**分散`execute_action`。** 每个记录一个调用更慢、费用更高，并且在之后没有任何东西可以检查。`execute_action_batch`采用相同的`action`加上`records`数组，生成一个批处理对象，完成的批处理包含其输出CSV的下载。工具描述说永远不要循环它：请字面理解。

**在引用之前花费。** 首先运行**10-20条记录**，报告观察到的成本和命中率，然后引用完整的**记录数**和**积分估计**并让用户批准。对于人员数据的命中率在40%到70%之间，因此每条*可用*行的成本不是标价，并且在没有样本的情况下无法知道。完整纪律：
[`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md)。

**将`query_models`误认为SQL。** 它列出一个模型上的记录，带有限制和偏移量。它不会聚合、连接或通过表达式过滤。任何形如“多少”、“按...分组”或“连接到”的问题都是CLI问题（[`cargo-storage`](../cargo-storage/SKILL.md)）。这样说，而不是自己拉取行并自己计数，这将在限制处静默截断。

## 任何涉及人员的内容

同意规则不会因为界面改变而放宽。法律依据、抑制检查以及与该人员工作相关的步骤将阻止任何来源、丰富或接触某人的步骤。批量未经请求的消息、购买的或收集的列表以及消费者定位被拒绝。完整文本是
[`../cargo-gtm/references/acceptable-use.md`](../cargo-gtm/references/acceptable-use.md)；在没有安装兄弟技能的情况下，上述段落单独起作用。

## 返回报告

叙述和总结；永远不要在用户处粘贴原始JSON。在批处理后，按顺序给出记录数、命中率、实际花费的积分和下载。
