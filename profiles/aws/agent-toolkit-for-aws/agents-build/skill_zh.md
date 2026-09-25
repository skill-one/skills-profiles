# 构建

为您的 AgentCore 代理项目添加功能。

## 使用场景

- 为您的代理添加跨会话内存
- 从 Web 应用、移动应用或后端服务调用已部署的代理
- 配置 VPC 网络以供私有资源（RDS、内部 API）使用
- 使用协调器/专家模式构建多代理系统
- 将现有的 Bedrock 代理迁移到 AgentCore
- 添加浏览器工具以便代理可以导航网站
- 添加代码解释器以便代理可以在沙盒中执行代码
- 添加 AgentCore 支付以便代理可以支付 x402-或 MPP-保护的 API、工具或内容
- 从项目中删除资源或拆除部署

**不适用于**：

- 通过网关连接到外部工具/API（OpenAPI 规范、Lambda、MCP 服务器、凭证、策略）→ 使用 `agents-connect`
- 搭建新项目 → 使用 `agents-get-started`
- 部署 → 使用 `agents-deploy`

## 输入

`$ARGUMENTS` 可以是：

- 一个功能："memory"、"integrate"、"vpc"、"multi-agent"、"migrate"、"browser"、"code-interpreter"、"payments"、"teardown"
- 对他们需求的描述："记住用户偏好"、"从 React 应用调用"、"抓取网站"、"在代理中运行 pandas"、"删除我的代理"、"清理资源"
- 空的 — 技能将根据上下文确定工作流程

## 处理

### 第 0 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。

如果较旧： "运行 `agentcore update` 以获取最新版本。"

### 第 1 步：读取项目上下文

读取 `agentcore/agentcore.json` 以了解当前项目 — 框架、现有资源、代理配置。

如果找不到 `agentcore/agentcore.json`：

1. **检查开发者是否在错误的目录中。** 在父目录（最多 3 级）中查找 `agentcore/agentcore.json`。如果找到，告诉他们： "在 `<路径>` 找到 AgentCore 项目。您是在该项目中工作吗？"
2. **如果附近没有项目存在**，询问他们想要添加什么功能。然后提供两条路径：
   - "我可以引导您先创建项目，然后再添加 CAPABILITY — 您想这样做吗？"（内联运行 get-started 流程，然后继续构建工作流程）
   - "如果您已经在其他地方有项目，请 `cd` 进入该项目并重试。"

不要只是说 "去使用 agents-get-started" 并停止 — 这样会丢失开发者实际想要做什么的上下文。

### 第 2 步：确定工作流程

**重要区分** — 在路由到构建参考之前，检查提示是否实际上是连接或调试问题：

- 如果短语提到外部 API、Lambda 函数、OpenAPI 规范、网关、凭证、MCP 服务器或策略 → 这是 `agents-connect`，不是构建
- 如果开发者说某件事出错了（错误答案、错误、工具失败）→ 这是 `agents-debug`，不是构建
- 构建是为**向工作项目添加新功能**，而不是修复已损坏的项目

根据开发者的提示和 `$ARGUMENTS`，加载适当的参考：

| 开发者意图 | 加载的参考 |
|---|---|
| 添加内存、记住事情、用户偏好、跨会话 | [`references/memory.md`](references/memory.md) |
| 从应用调用代理、从代码调用、流式传输、SDK 客户端、代理 URL、在会话中执行 shell | [`references/integrate.md`](references/integrate.md) |
| VPC、私有网络、RDS、内部 API、子网、安全组 | [`references/vpc.md`](references/vpc.md) |
| 多代理、协调器、专家、A2A、委托、代理交接 | [`references/multi-agent.md`](references/multi-agent.md) |
| 调用者到代理的自定义头部、头部允许列表、租户 ID/关联 ID/跟踪传播 | [`references/request-headers.md`](references/request-headers.md) |
| 迁移 Bedrock 代理、导入代理、迁移到 AgentCore | [`references/migrate.md`](references/migrate.md) |
| 浏览器工具、Web 导航、表单填写、抓取、Nova Act、Playwright、实时视图 | [`references/browser.md`](references/browser.md) |
| 代码解释器、执行代码、沙盒、运行 Python/JS/TS、代理中的数据分析、pandas | [`references/code-interpreter.md`](references/code-interpreter.md) |
| 支付、支付 x402 或 MPP 内容、402 支付要求、机器支付协议、WWW-Authenticate: Payment、微支付、付费 API/工具、支付管理器/连接器 | [`references/payments.md`](references/payments.md) |
| 删除代理、删除资源、拆除、清理、销毁、重新开始 | [`references/teardown.md`](references/teardown.md) |
| 更改模型、切换模型、使用 Haiku/Sonnet/Nova、不同模型 | 内联 — 见下文 "更改模型" |

如果开发者询问本地开发和部署之间的区别（例如，"为什么我的内存在部署后工作但在本地不工作？"），加载 [`references/local-vs-deployed.md`](references/local-vs-deployed.md) 以及特定的构建参考。

将匹配的文件读入上下文并按其 Process 部分逐步执行 — 不要总结。

如果意图不明确，询问开发者他们想要添加什么功能。

### 更改模型

模型在 `app/<AgentName>/model/load.py` 中配置（由 `agentcore create` 搭建）。要更改它：

1. 打开 `app/<AgentName>/model/load.py`
2. 在 `BedrockModel()` 构造函数中更改 `model_id` 参数

```python
# 默认（由 CLI 搭建）
return BedrockModel(model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0")

# 切换到 Haiku 以节省成本
return BedrockModel(model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0")

# 切换到 Nova Lite
return BedrockModel(model_id="amazon.nova-lite-v1:0")
```

跨区域推理前缀（`us.`、`eu.`、`apac.`、`global.`）控制推理运行的位置。使用 `global.` 以获得最大吞吐量，或使用地理前缀以实现数据驻留。并非所有模型都支持所有前缀 — 查看 Bedrock 推理配置文件文档。

更改模型后：

- 验证模型是否在您的区域启用：AWS 控制台 → Amazon Bedrock → 模型访问
- 对于跨区域配置文件，在所有目标区域中启用
- 如果使用 `agents-harden`，更新 IAM 策略以范围到新的模型 ARN
- 运行 `agentcore dev` 以本地测试，然后 `agentcore deploy` 以更新已部署的代理

不需要更改 `agentcore.json` — 模型是在代码中配置的，而不是在项目配置中。

### 预飞行：在生成 CLI 命令之前验证任何 `--name`

无论您加载哪个参考，大多数最终都会生成 `agentcore add <resource> --name <something>` 命令。CLI 在**后期**对无效名称失败 — 您会在完成提示后看到错误，而不是在运行命令前。提前验证：

| 资源 | 最大字符数 | 允许 | 以...开头 |
|---|---|---|---|
| 代理（`add agent`） | 48 | 字母数字 + `_` | 字母 |
| 内存、网关、网关目标、凭证、评估器、在线评估、策略、策略引擎、支付管理器、支付连接器 | 48 | 字母数字 + `_` | 字母 |

在构建命令之前计算字符数。如果名称超过限制或包含连字符、点或空格，请提供反馈： "`<name>` 是 N 个字符 / 使用 `-`，CLI 会拒绝。如何 `<建议>`？" 不要使用无效名称运行命令，希望 CLI 消息会很清楚。

注意：`agentcore create --name`（项目名称）有**更严格的 23 字符限制**，并且不允许下划线。这在上面的 `agents-get-started` 中涵盖；如果您看到开发者重新运行创建，请特别指出 23 字符限制。

## 输出

取决于工作流程 — 请查看加载的参考以获取具体输出。

## 质量标准

- 基于开发者的意图加载了正确的参考
- 所有输出都符合加载参考的质量标准
- 在相关位置包含对其他技能（agents-connect、agents-deploy）的交叉引用
