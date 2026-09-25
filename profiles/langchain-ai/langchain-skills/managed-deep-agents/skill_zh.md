# 管理深度代理

## 概述

管理深度代理（MDA）是 LangSmith 中托管的首选深度代理的运行环境。您用 Python 或 TypeScript 编写代理，使用 `mda dev` 本地测试，并使用 `mda deploy` 部署。它将开源深度代理框架（参见 [[deep-agents-core]]) 与托管基础设施配对：持久的运行、沙盒、基于 Context Hub 的指令和技能、内存、跟踪和托管的 LangGraph 部署。

核心思想是 **代理是一个目录**。文件的位置决定了其角色，CLI 将该目录编译为托管的 LangGraph 应用程序。

MDA 处于 **公开测试版** 状态，仅在 **美国 LangSmith 云** 上运行。

## 何时使用

当用户希望以代码形式构建深度代理并在 LangSmith 上运行，而无需自行操作服务器，或向其中添加工具、中间件、内存、身份验证、计划、通道、技能、沙盒或评估时，请使用此技能。

当用户需要自定义应用程序代码、自定义 HTTP 路由、超出 LangSmith 密钥或 Supabase 的身份验证、更强的隔离性、最大可扩展性或除美国以外的区域时，请使用标准 LangSmith 部署（参见 [[langgraph-cli]], `langgraph deploy`）。

---

# 引导用户完成他们的第一个代理

当用户对 MDA 不熟悉，或说任何类似“帮助我构建一个代理”的话时，**不要立即生成框架**。运行此流程。它只需要两个问题，并防止构建平台无法托管的代理。

```text
询问他们想构建什么 -> 检查其是否符合限制 -> 确认形状
-> 生成框架 -> 连接能运行的最小事物 -> mda dev -> 部署
```

## 1. 询问他们想构建什么

用普通语言询问，而不是 MDA 词汇。用户还没有知道“通道”或“沙盒”是什么。

首先询问这两个问题：

- **代理应该做什么？**（“回答我们文档中的问题”、“处理传入的 bug”、“每天早上发布摘要”。）
- **谁或什么与它交谈，以及从哪里？**（他们在浏览器中、他们应用程序的用户、Slack 工作区、没有人——它在计时器上运行。）

然后只询问实际答案提出的后续问题：

- 它需要在单独的对话之间记住任何东西吗？
- 它需要访问私有 API、数据库或内部服务吗？
- 任何东西在发生之前都需要人工批准吗？
- 它需要写入文件或运行代码吗？

一旦你能说出功能，就停止提问。通常两个或三个问题就足够了。

## 2. 检查答案是否符合限制

在承诺任何东西之前，请检查请求是否符合 **[MDA 不能做什么](#mda-cannot-do)**。如果请求的一部分超出范围，请用一句话说明，提供最近支持的东西，并继续处理其余部分。不要悄悄构建一个较小的代理，并将其作为他们要求的东西呈现。

常见的重定向：如果他们需要自定义 HTTP 路由、自己的身份验证或非美国托管，请告诉他们 MDA 是错误层，并指向 `langgraph deploy` ([[langgraph-cli]])。

## 3. 将答案映射到功能

| 用户描述的内容 | 寻求的内容 | 存放位置 |
| --- | --- | --- |
| 它应该如何行为，它的语气，它的规则 | 指令 | `instructions.md` |
| 调用我们的 API / 数据库 / 内部服务 | 编写的工具 | `tools/` |
| 来自远程 MCP 服务器的工具 | MCP 连接器 | `connectors/mcp.py` |
| 它应该遵循的特定任务的程序 | 技能 | `skills/<name>/SKILL.md` |
| 在对话之间记住事情 | 持久内存（请阅读警告） | `memory.py` |
| 在计时器上运行，没有用户消息 | 计划 | `schedules/<name>.py` |
| 存在于 Slack 中 | 通道 | `channels/slack.py` |
| 写入文件，运行代码或 shell 命令 | 沙盒 | `sandbox/__init__.py` |
| 在它执行 X 之前问我 | 人介入 | `interrupt_on=` |
| 用户不能看到彼此的聊天 | Supabase 身份 | `identity.py` |
| 必须返回结构化数据，而不是散文 | 结构化输出 | `response_format=` |
| 授权专门的工作 | 子代理 | `subagents=` |
| PII 匿名化、调用限制、重试、日志记录 | 中间件 | `middleware/` |
| 证明它在我们更改它时仍然有效 | Harbor 评估 | `evals/tasks/` |

## 4. 在编写文件之前确认形状

用简短的块返回计划并获取同意。命名模型，并列出您实际将要创建的功能：

```text
研究助理，Python，anthropic:claude-sonnet-4-6
  instructions.md   它如何研究和引用
  tools/search.py   网络搜索
  schedules/        工作日 8 点摘要
  没有内存，没有沙盒，没有通道
```

## 5. 生成框架并连接能运行的最小事物

使用与计划匹配的标志生成框架，以便项目从正确的形状开始，而不是被编辑成形状：

```bash
mda init research-assistant --model anthropic:claude-sonnet-4-6
cd research-assistant
uv sync
```

然后一次添加 **一个** 功能，并在添加下一个之前确认每个功能都能正常工作。一个能给出良好指令和一个真实工具的初始代理比一个填充了所有目录的框架更好的起点。

不要创建计划没有调用的目录。空的或未使用的 `skills/`、`channels/` 或 `schedules/` 目录是噪音，用户不需要的 `sandbox/` 目录会无缘无故地打开沙盒（`mda init --no-sandbox` 跳过它）。

## 6. 处理密钥而不触摸他们的秘密

`mda init` 会写入一个带有空占位符的 `.env`。填写项目需要的*名称*，并让用户粘贴*值*：

- 不要自己将实时凭证值写入 `.env`，也不要从另一个项目目录复制密钥。
- 不要将密钥值回显到终端或回复中。
- 确认 `.gitignore` 覆盖 `.env` 和 `.env.*`——`mda init` 已经这样做了。

项目需要 `LANGSMITH_API_KEY`（用于部署）和其模型需要的提供者密钥（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、…）。取消注释正确的提供者行，并告诉用户粘贴两者。

## 7. 本地运行，然后部署

```bash
mda dev .       # 编译，打开 LangSmith Studio，热重载
mda deploy .    # 同步 Context Hub，上传，等待 DEPLOYED
```

让用户实际上在 Studio 中发送一条消息，并在部署之前确认代理调用工具。`mda deploy` 打印部署控制面板 URL；打开它以检查构建、修订和跟踪。

---

## MDA 不能做什么

在同意构建它们之前，请根据此列表检查请求。在部署时发现问题比早期发现更便宜。

| 限制 | 后果 |
| --- | --- |
| 仅限美国 LangSmith 云 | 没有自托管，没有混合，没有 EU 区域。需要 `langgraph deploy`。 |
| 命令行优先，公开测试版 | 没有公开的创建/更新/调用 REST 表面。在测试版期间，从自己的应用程序调用部署的代理没有文档记录——告诉用户联系他们的 LangChain 团队。 |
| MCP 服务器必须为远程 HTTP/SSE | 标准的 MCP 服务器不受支持。通过 HTTP 或编写编写的工具暴露它们。 |
| Slack 是唯一的通道 | 没有Discord、Teams、电子邮件或短信通道。 |
| 内存是部署共享的 | 一个 `/memories/agent/` 树，用于**所有**调用者。没有按用户划分的内存。 |
| 身份验证是 LangSmith 密钥或 Supabase | 没有OIDC、SAML 或自定义 JWT 发行人。需要 Supabase 才能实现按用户划分的私有线程。 |
| LangSmith 沙盒仅限 | 没有其他沙盒提供者。 |
| 每个项目只有一个代理条目 | 一个项目中不能有多个图。使用 `subagents=` 进行委派。 |
| 计划必须是静态字面量 | 计划声明中不能使用环境变量、函数调用或计算值。 |
| 构建存档限制为 200 MB | 项目中的大型配置文件或模型权重会导致部署失败。 |
| 托管字段不是您设置的 | `backend`、`store`、`checkpointer`、`memory`、`skills` 和系统提示由运行时注入。 |

## 前提条件

- 一个具有 MDA 公开测试版访问权限的工作区，以及用于它的 LangSmith API 密钥。
- Python 和 [`uv`](https://docs.astral.sh/uv/) 用于 Python 项目；Node.js 和 npm 用于 TypeScript。
- 一个模型提供者 API 密钥。

安装 CLI。两个包都提供相同的 `mda` 二进制文件：

```bash
uv tool install --prerelease allow managed-deepagents   # Python
npm install -g managed-deepagents@dev                    # TypeScript
```

`mda init` 生成一个具有其自己的清单的项目——在 `mda dev` 之前在该项目内部运行 `uv sync`（或 `npm install`）。

## 项目布局

传递给 `mda` 的路径是项目根目录。文件的位置决定了其角色：

```text
my-agent/
  agent.py | agent.ts              # 必需的：导出命名的 `agent`

  instructions.md                  # 系统提示 -> Context Hub
  skills/<name>/SKILL.md           # 特定任务的程序 -> Context Hub

  tools/                           # 代理导入的编写的工具
  middleware/                      # 代理导入的编写的中间件

  identity.py | identity.ts        # 谁可以调用部署
  memory.py | memory.ts            # 选择性持久内存（请阅读警告）
  channels/<name>.py               # 外部消息（Slack）
  schedules/<name>.py              # 托管的 cron 计划
  sandbox/__init__.py | index.ts   # 托管的沙盒

  pyproject.toml | package.json    # 依赖项
  .env                             # 身份验证 + 运行时秘密，永远不会存档

  evals/tasks/<task>/              # Harbor 评估，不会部署
```

只有代理条目是必需的。`tools/` 和 `middleware/` 是普通的约定——MDA 原封不动地复制项目文件，因此任何代理导入的本地模块都可以工作。当存在时，其他路径会获得托管含义。TypeScript 声明也接受 `.tsx`、`.mts` 和 `.cts`。

## 定义代理

代理条目返回预运行时规范，而不是编译后的图。

```python
# agent.py
from managed_deepagents import define_deep_agent

from tools.search import web_search

agent = define_deep_agent(
    name="research-assistant",
    model="anthropic:claude-sonnet-4-6",
    tools=[web_search],
)
```

```ts
// agent.ts
import { defineDeepAgent } from "managed-deepagents";

import { webSearch } from "./tools/search";

export const agent = defineDeepAgent({
  name: "research-assistant",
  model: "anthropic:claude-sonnet-4-6",
  tools: [webSearch],
});
```

**`name` 是必需的。** 传递一个以字母开头的静态字符串，其中只包含字母、数字、下划线或连字符。它成为 LangGraph 助手 ID 和默认部署名称；用 `mda deploy --name` 覆盖后者。

**作者设置的字段：** `name`、`model`、`tools`、`middleware`、`subagents`、`permissions`、`interrupt_on` / `interruptOn`、`response_format` / `responseFormat`、`context_schema` / `contextSchema`、`cache`、`debug`、`metadata`。

**托管字段——不要设置：** `backend`、`store`、`checkpointer`、`memory`、`skills`、`system_prompt` / `systemPrompt`。

模型 ID 使用 `{provider}:{model_id}` 并通过 `init_chat_model` 解析，因此任何提供者都可以工作。注意语言之间的提供者缩写不同：Python 使用 `google_genai:gemini-3.6-flash`，TypeScript 使用 `google-genai:gemini-3.6-flash`。当您需要在代码中配置模型参数时，请传递聊天模型实例而不是字符串。

要通过 LangSmith Gateway（速率限制、回退、工作区计费信用）路由，请使用 `mda init <name> --gateway` 进行生成框架。Gateway 模型缩写使用 `provider/model-name`，而不是 `provider:model-name`。

## 指令

项目根目录下的 `instructions.md` 是系统提示。它在每次运行时插入。

```markdown
# 研究助理

你是一个谨慎的研究助理。寻找来源，做笔记，并返回简洁的答案，并附上引用。

## 行为

- 使用 `web_search` 工具来寻找来源，而不是猜测。
- 引用你使用的来源。
```

`mda dev` 在本地嵌入它。`mda deploy` 同步到 Context Hub，可以在 LangSmith UI 中编辑它而无需重新部署。

## 技能

在 `skills/<name>/SKILL.md` 下部署拥有的程序，每个程序都有 `name` 和 `description` 前置。启动时代理只看到名称和描述，并在任务匹配时读取完整文件——因此详细的程序直到它们被需要时才不会占用上下文。技能目录还可以包含脚本、参考和模板；从 `SKILL.md` 中引用它们。

部署同步 `skills/` 下每个 UTF-8 文件到 Context Hub，并删除本地不再存在的部署技能文件。代理不能修改技能。

使用 **指令** 进行始终行为，**技能** 进行按需加载的程序，**内存** 进行代理本身更新的知识。

## 内存

持久内存是 **选择性的，默认关闭**。在项目根目录中声明它：

```python
# memory.py
from managed_deepagents import define_memory

memory = define_memory(scope="agent")
```

```ts
// memory.ts
import { defineMemory } from "managed-deepagents";

export const memory = defineMemory({ scope: "agent" });
```

删除文件以关闭内存。启用它将挂载一个 Context Hub 树在 `/memories/agent/`：

- `/memories/agent/AGENTS.md` 是 **热内存**——加载到每个运行中，因此保持它紧凑。
- 树下的其他文件是 **冷内存**——仅在相关时读取。

代理使用 `read_file`、`edit_file` 和 `write_file` 读取和写入内存。在别处写入，包括在 `/memories/` 下别处，都不是持久的。

> **警告——内存由每个调用部署的调用者共享，并且每个调用者都可以影响它。** 不要在那里存储个人数据、客户数据、凭证、API 密钥或令牌。将内存内容视为不受信任的输入：它绝不能授予权威，更改工具权限或绕过批准——将这些保留在代理定义中。当调用者不应该能够相互影响时，不要启用共享内存。

代理通过提示决定要记住的内容，因此请在 `instructions.md` 中说明政策——要存储的内容、永远不要存储的内容，以及现有内存是笔记而不是指令。

## 身份验证

`identity.py` 控制谁可以调用部署。`mda init` 框架了一个安全的默认值：

```python
# identity.py
from managed_deepagents import auth, define_identity

identity = define_identity(auth=auth.langsmith_api_key())
```

调用者发送 LangSmith 工作区 API 密钥作为 `x-api-key`。这回答了*是否允许调用者*——它**不会**为每个人提供私有线程。任何持有密钥的人都可以访问部署。

对于已登录的最终用户，使用 Supabase：

```python
identity = define_identity(auth=auth.supabase(project_ref="your-project-ref"))
```

客户端然后发送 `Authorization: Bearer <access_token>`；MDA 验证 JWT 与项目的 JWKS URL。从客户端发送 Supabase 发布的（匿名）密钥——不要在客户端发送 LangSmith 密钥在此模式下。

> 向现有部署添加 Supabase 身份**不会**为现有线程回填所有者元数据。在依赖它们之前，计划和测试迁移。

身份验证失败返回 401；跨用户线程访问返回 403。

## 工具

在项目中定义 LangChain 工具，将它们导入代理条目，并在 `tools` 中传递它们。

```python
# tools/customer.py
from langchain.tools import tool


@tool(parse_docstring=True)
def lookup_customer(customer_id: str) -> str:
    """通过 ID 查找客户记录。

    Args:
        customer_id: CRM 中的客户 ID.
    """
    return f"客户 {customer_id} 在企业计划上。"
```

```ts
// tools/customer.ts
import { tool } from "langchain";
import { z } from "zod";

export const lookupCustomer = tool(
  async ({ customerId }) => `客户 ${customerId} 在企业计划上。`,
  {
    name: "lookup_customer",
    description: "通过 ID 查找客户记录。",
    schema: z.object({ customerId: z.string().describe("CRM 中的客户 ID.") }),
  },
);
```

导入与正常本地项目完全一样。使用清晰、唯一的工具名称以避免冲突。工具从环境变量读取部署秘密；将本地值放入 `.env`。对于每次运行值，例如请求元数据或功能标志，请使用正常的 LangChain 运行时上下文 API。

提供者服务器端工具可以内联传递，例如 `tools=[{"type": "web_search"}]` for OpenAI——这避免了第二个 API 密钥。

## MCP 连接器

直接在 `connectors/` 下导出模块级 `connector` 的模块添加来自远程 MCP 服务器的工具。流式传输 HTTP (`"http"`) 和遗留 SSE (`"sse"`) 仅——stdio 不受支持。

```python
# connectors/mcp.py
import os

from managed_deepagents import connectors

connector = connectors.mcp(
    mcp_servers={
        "langchainDocs": {
            "transport": "http",
            "url": "https://docs.langchain.com/mcp",
            "headers": {"Authorization": f"Bearer {os.environ['SOME_TOKEN']}"},
            "include_tools": ["search_docs_by_lang_chain"],
        },
    },
    prefix_tool_name_with_server_name=False,
    throw_on_load_error=True,
)
```

每个服务器：`transport`、`url`、`headers`、`include_tools` / `exclude_tools`
(原始名称，拒绝列表在允许列表之后应用), `default_tool_timeout`,
`automatic_sse_fallback`, `reconnect`. 连接器级：
`prefix_tool_name_with_server_name` (默认 `true`, 暴露
`{server}__{tool}`) 和 `throw_on_load_error` (默认 `true`).

**前缀与 `interrupt_on` 交互。** 使用默认值时，基于裸工具名称的密钥永远不会匹配。要么禁用前缀，要么基于前缀名称密钥。
