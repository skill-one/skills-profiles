---
name: managed-deep-agents
description: 在使用 mda CLI 在 LangSmith 中构建、测试或部署托管深度代理时，请调用此技能。该技能将引导用户完成其第一个代理的端到端流程——询问用户想要构建什么，将其映射到 MDA 实际能做什么，然后搭建并部署它。涵盖基于文件的项目布局；define_deep_agent / defineDeepAgent；指令、技能、内存、身份、工具、中间件、沙盒、计划、通道和评估；mda init/build/dev/deploy/logs/delete；以及 Context Hub。
---

# 管理深度代理

## 概述

管理深度代理（MDA）是 LangSmith 中用于代码优先深度代理的托管运行时。您使用 Python 或 TypeScript 编写代理，使用 `mda dev` 本地测试，并使用 `mda deploy` 部署它。它将开源深度代理框架（参见 [[deep-agents-core]]) 与托管基础设施配对：持久的运行、沙盒、基于 Context Hub 的指令和技能、内存、跟踪和托管的 LangGraph 部署。

核心思想是 **代理是一个目录**。文件的 location 决定了其角色，CLI 将该目录编译为托管的 LangGraph 应用。

MDA 处于 **公开测试阶段**，仅在 **美国 LangSmith 云** 上运行。

## 何时使用

当用户希望以代码形式构建深度代理并在 LangSmith 上运行，而无需自行操作服务器时，或者向现有代理添加工具、中间件、内存、身份验证、计划、通道、技能、沙盒或评估时，请使用此技能。

当用户需要自定义应用程序代码、自定义 HTTP 路由、超出 LangSmith 密钥或 Supabase 的身份验证、更强的隔离性、最大可扩展性或除美国以外的区域时，请使用标准 LangSmith 部署（参见 [[langgraph-cli]], `langgraph deploy`）。

---

# 引导用户完成第一个代理

当用户对 MDA 不熟悉，或者说任何类似“帮助我构建一个代理”的话时，**不要立即生成框架**。运行此流程。它只需要两个问题，并防止构建平台无法托管的代理。

```text
询问他们想构建什么 -> 检查其是否符合限制 -> 确认形状
-> 生成框架 -> 连接能运行的最小部分 -> mda dev -> 部署
```

## 1. 询问他们想构建什么

使用普通语言，而不是 MDA 词汇。用户目前还不了解“通道”或“沙盒”是什么。

首先询问这两个问题：

- **代理应该做什么？**（“回答我们文档中的问题”、“处理传入的 bug”、“每天早上发布摘要”。）
- **谁或什么与它交谈，以及从哪里交谈？**（他们在浏览器中、他们应用程序的用户、Slack 工作区、没有人——它在计时器上运行。）

然后只询问实际答案会引发的问题：

- 它需要在单独的对话之间记住任何东西吗？
- 它需要访问私有 API、数据库或内部服务吗？
- 任何东西在发生之前都需要人类批准吗？
- 它需要写入文件或运行代码吗？

一旦你能说出功能，就停止询问。通常两个或三个问题就足够了。

## 2. 将答案与限制进行核对

在承诺任何东西之前，请将请求与 **[MDA 不能做什么](#what-mda-cannot-do)** 下方的内容进行核对。如果请求的一部分超出范围，请用一句话说明，提供最近支持的东西，并继续处理其余部分。不要悄悄构建一个较小的代理，并将其作为他们要求的东西呈现。

常见的重定向：如果他们需要自定义 HTTP 路由、自己的身份验证或非美国托管，请告诉他们 MDA 是错误层，并指向 `langgraph deploy` ([[langgraph-cli]])。

## 3. 将答案映射到功能

| 用户描述的内容 | 寻求的内容 | 存放位置 |
| --- | --- | --- |
| 它应该如何行为，它的语气，它的规则 | 指令 | `instructions.md` |
| 调用我们的 API / 数据库 / 内部服务 | 自定义工具 | `tools/` |
| 来自远程 MCP 服务器的工具 | MCP 连接器 | `connectors/mcp.py` |
| 它应该遵循的特定任务的程序 | 技能 | `skills/<name>/SKILL.md` |
| 在对话之间记住事情 | 持久内存（请阅读警告） | `memory.py` |
| 在计时器上运行，没有用户消息 | 计划 | `schedules/<name>.py` |
| 住在 Slack 中 | 通道 | `channels/slack.py` |
| 写入文件，运行代码或 shell 命令 | 沙盒 | `sandbox/__init__.py` |
| 在它做 X 之前问我 | 人机交互 | `interrupt_on=` |
| 用户不能看到彼此的聊天 | Supabase 身份验证 | `identity.py` |
| 必须返回结构化数据，而不是散文 | 结构化输出 | `response_format=` |
| 接管专业工作 | 子代理 | `subagents=` |
| PII 匿名化、调用限制、重试、日志记录 | 中间件 | `middleware/` |
| 证明它在我们更改它时仍然有效 | Harbor 评估 | `evals/tasks/` |

## 4. 在编写文件之前确认形状

用简短的块陈述计划并获取同意。命名模型，并列出您实际将要创建的功能：

```text
研究助理，Python，anthropic:claude-sonnet-4-6 上
  instructions.md   它如何研究和引用
  tools/search.py   网络搜索
  schedules/        工作日 8 点摘要
  无内存，无沙盒，无通道
```

## 5. 生成框架并连接能运行的最小部分

使用与计划匹配的标志生成框架，以便项目从正确的形状开始，而不是被编辑成形状：

```bash
mda init research-assistant --model anthropic:claude-sonnet-4-6
cd research-assistant
uv sync
```

然后一次添加 **一个** 功能，并在添加下一个之前确认每个功能都能正常工作。一个能回答良好指令并有一个真实工具的初始代理比一个所有目录都已填满的框架是一个更好的起点。

不要创建计划没有要求目录。空的或未使用的 `skills/`、`channels/` 或 `schedules/` 目录是噪音，用户不需要的 `sandbox/` 目录会无缘无故地打开沙盒（`mda init --no-sandbox` 会跳过它）。

## 6. 处理密钥而不接触他们的秘密

`mda init` 会写入一个带有空占位符的 `.env`。填写项目需要的 *名称*，并让用户粘贴 *值*：

- 不要自己将实时凭证值写入 `.env`，也不要从另一个项目目录复制密钥。
- 不要将密钥值回显到终端或回复中。
- 确认 `.gitignore` 覆盖 `.env` 和 `.env.*`——`mda init` 已经这样做了。

项目需要 `LANGSMITH_API_KEY`（用于部署）和其模型所需的提供者密钥（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、…）。取消注释正确的提供者行，并告诉用户粘贴两者。

## 7. 本地运行，然后部署

```bash
mda dev .       # 编译，打开 LangSmith Studio，热重载
mda deploy .    # 同步 Context Hub，上传，等待 DEPLOYED
```

让用户在 Studio 中实际发送一条消息，并在部署之前确认代理调用了工具。`mda deploy` 会打印部署控制面板的 URL；打开它以检查构建、修订和跟踪。

---

## MDA 不能做什么

在同意构建之前，请根据此列表检查请求。在部署时发现问题比早期发现限制更便宜。

| 限制 | 后果 |
| --- | --- |
| 仅限美国 LangSmith 云 | 没有自托管，没有混合，没有 EU 区域。需要 `langgraph deploy`。 |
| 命令行优先，公开测试阶段 | 没有公开的创建/更新/调用 REST 表面。从自己的应用程序调用已部署代理在测试期间没有文档——告诉用户联系他们的 LangChain 团队。 |
| MCP 服务器必须是远程 HTTP/SSE | 标准的 MCP 服务器不受支持。通过 HTTP 或编写自定义工具暴露它们。 |
| Slack 是唯一的通道 | 没有Discord、Teams、电子邮件或短信通道。 |
| 内存是部署共享的 | 一个 `/memories/agent/` 树用于 **所有** 调用者。没有按用户分组的内存。 |
| 身份验证是 LangSmith 密钥或 Supabase | 没有OIDC、SAML 或自定义 JWT 发行人。需要 Supabase 才能按用户进行私有线程。 |
| 仅限 LangSmith 沙盒 | 没有其他沙盒提供者。 |
| 每个项目只有一个代理条目 | 一个项目中不能有多个图。使用 `subagents=` 进行委托。 |
| 计划必须是静态字面量 | 计划声明中不能有环境变量、函数调用或计算值。 |
| 构建存档限制为 200 MB | 项目中的大型固定件或模型权重会导致部署失败。 |
| 托管字段不是您设置的 | `backend`、`store`、`checkpointer`、`memory`、`skills` 和系统提示由运行时注入。 |

## 前提条件

- 一个具有管理深度代理公开测试访问权限的工作区，以及用于它的 LangSmith API 密钥。
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
  agent.py | agent.ts              # 必须的：导出命名的 `agent`

  instructions.md                  # 系统提示 -> Context Hub
  skills/<name>/SKILL.md           # 特定任务的程序 -> Context Hub

  tools/                           # 代理导入的自定义工具
  middleware/                      # 代理导入的自定义中间件

  identity.py | identity.ts        # 谁可以调用部署
  memory.py | memory.ts            # 可选的持久内存
  channels/<name>.py               # 外部消息（Slack）
  schedules/<name>.py              # 托管的计时器
  sandbox/__init__.py | index.ts   # 托管的沙盒

  pyproject.toml | package.json    # 依赖项
  .env                             # 身份验证 + 运行时秘密，从不存档

  evals/tasks/<task>/              # Harbor 评估，不部署
```

只有代理条目是必需的。`tools/` 和 `middleware/` 是普通的约定——MDA 原封不动地复制项目文件，因此任何代理导入的本地模块都可以工作。其他路径在存在时具有托管含义。TypeScript 声明也接受 `.tsx`、`.mts` 和 `.cts`。

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

模型 ID 使用 `{provider}:{model_id}` 并通过 `init_chat_model` 解析，因此任何提供者都可以工作。注意不同语言之间提供者缩写的差异：Python 使用 `google_genai:gemini-3.6-flash`，TypeScript 使用 `google-genai:gemini-3.6-flash`。当您需要在代码中配置模型参数时，传递聊天模型实例而不是字符串。

要通过 LangSmith Gateway（速率限制、回退、工作区计费信用）路由，请使用 `mda init <name> --gateway` 生成框架。Gateway 模型缩写使用 `provider/model-name`，而不是 `provider:model-name`。

## 指令

项目根目录下的 `instructions.md` 是系统提示。它在每次运行时都会插入。

```markdown
# 研究助理

你是一个谨慎的研究助理。寻找来源，做笔记，并返回简洁的答案，附带引用。

## 行为

- 使用 `web_search` 工具来寻找来源，而不是猜测。
- 引用你使用的来源。
```

`mda dev` 在本地嵌入它。`mda deploy` 将它同步到 Context Hub，用户可以在 LangSmith UI 中编辑它，而无需重新部署。

## 技能

在 `skills/<name>/SKILL.md` 下部署拥有的程序，每个程序都有 `name` 和 `description` 前置。启动时代理只看到名称和描述，并在任务匹配时读取完整文件——因此详细的程序在需要之前不会消耗上下文。技能目录也可以包含脚本、参考和模板；从 `SKILL.md` 中引用它们。

部署会同步 `skills/` 下每个 UTF-8 文件到 Context Hub，并删除本地不再存在的已部署技能文件。代理不能修改技能。

使用 **指令** 进行始终在线的行为，**技能** 进行按需加载的程序，**内存** 进行代理本身更新的知识。

## 内存

持久内存是 **可选的，默认关闭**。在项目根目录下声明它：

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

删除文件以关闭内存。启用它会在 `/memories/agent/` 挂载一个 Context Hub 树：

- `/memories/agent/AGENTS.md` 是 **热内存**——加载到每个运行中，因此保持它紧凑。
- 树下的其他文件是 **冷内存**——仅在相关时读取。

代理使用 `read_file`、`edit_file` 和 `write_file` 读取和写入内存。在别处写入，包括在 `/memories/` 下别处，都不是持久的。

> **警告——内存被每个调用部署的调用者和每个调用者影响。** 不要在那里存储个人数据、客户数据、凭证、API 密钥或令牌。将内存内容视为不受信任的输入：它绝不能授予权限、更改工具权限或绕过批准——将这些保留在代理定义中。当调用者不应该能相互影响时，不要启用共享内存。

代理通过提示决定要记住什么，因此请在 `instructions.md` 中说明政策——要存储什么、永远不要存储什么，以及现有内存是笔记而不是指令。

## 身份验证

`identity.py` 控制谁可以调用部署。`mda init` 框架了一个安全的默认值：

```python
# identity.py
from managed_deepagents import auth, define_identity

identity = define_identity(auth=auth.langsmith_api_key())
```

调用者将 LangSmith 工作区 API 密钥作为 `x-api-key` 发送。这回答了 *调用者是否被允许*——它 **不** 给每个人提供私人线程。任何持有密钥的人都可以访问部署。

对于有私人线程的登录用户，请使用 Supabase：

```python
identity = define_identity(auth=auth.supabase(project_ref="your-project-ref"))
```

然后客户端发送 `Authorization: Bearer <access_token>`；MDA 会根据项目的 JWKS URL 验证 JWT。只从客户端发送 Supabase 发布（匿名）密钥进行登录——在这种模式下永远不要发送 LangSmith 密钥。

> 向现有部署添加 Supabase 身份验证 **不会** 为现有线程回填所有者元数据。在依赖基于身份的访问之前，计划和测试迁移。

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
        customer_id: CRM 中的客户 ID。
    """
    return f"客户 {customer_id} 在企业计划上。"
```

```ts
// tools/customer.ts
import { tool } from "langchain";
import { z } from "zod";

export const lookupCustomer = tool(
  async ({ customerId }) => `客户 ${customerId} 是企业计划。`,
  {
    name: "lookup_customer",
    description: "通过 ID 查找客户记录。",
    schema: z.object({ customerId: z.string().describe("CRM 中的客户 ID。") }),
  },
);
```

导入功能与普通本地项目完全相同。使用清晰、唯一的工具名称以避免冲突。工具从环境变量中读取部署密钥；将本地值放在 `.env` 中。对于请求元数据或功能标志等每次运行值，请使用正常的 LangChain 运行时上下文 API。

支持在服务器端传递提供商工具（例如 OpenAI 的 `tools=[{"type": "web_search"}]`），这可以避免第二个 API 密钥。

## MCP 连接器

`connectors/` 下直接导出模块级 `connector` 的模块会从远程 MCP 服务器添加工具。仅支持流式 HTTP（`"http"`）和遗留 SSE（`"sse"`）—— stdio 不受支持。

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

每台服务器：`transport`、`url`、`headers`、`include_tools` / `exclude_tools`（原始名称，应用白名单后进行拒绝列表处理）、`default_tool_timeout`、`automatic_sse_fallback`、`reconnect`。连接器级：`prefix_tool_name_with_server_name`（默认 `true`，显示 `{server}__{tool}`）和 `throw_on_load_error`（默认 `true`）。

**前缀与 `interrupt_on` 交互。** 默认情况下，基于裸工具名称的门控永远不会匹配。要么禁用前缀，要么基于前缀名称门控。

凭据放在 `headers` 中从环境变量读取，永远不会硬编码。请注意，面向每个用户 OAuth（例如 Fleet 平台工具服务器）的服务器无法通过静态头满足。

## 中间件

中间件封装模型调用、工具调用和生命周期钩子。列表中的顺序是明确的；MDA 从不推断它。使用预构建的 LangChain 中间件或编写自己的中间件（参见 [[langchain-middleware]]）。

```python
from langchain.agents.middleware import ModelCallLimitMiddleware, PIIMiddleware
from managed_deepagents import define_deep_agent

agent = define_deep_agent(
    name="support-agent",
    model="anthropic:claude-sonnet-4-6",
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        ModelCallLimitMiddleware(run_limit=50),
    ],
)
```

中间件是处理 PII、速率限制、重试、模型回退、动态模型选择和工具调用监控的正确位置。

## 沙盒

沙盒为代理提供隔离的文件系统和 shell。`mda init` 模板化一个沙盒；**删除 `sandbox/` 目录以退出**，这对于只需要其提示、工具和内存的代理是正确的。

```python
# sandbox/__init__.py
from managed_deepagents import define_sandbox

sandbox = define_sandbox(
    scope="thread",
    idle_ttl_seconds=600,
    default_timeout=600,
)
```

```ts
// sandbox/index.ts
import { defineSandbox } from "managed-deepagents";

export const sandbox = defineSandbox({
  scope: "thread",
  idleTtlSeconds: 600,
  defaultTimeout: 600,
});
```

`scope="thread"`（默认值）为每个持久线程创建一个沙盒。`scope="agent"` 在线程之间共享单个文件系统——**仅用于有意共享的状态**，因为线程可以读取和修改彼此的文件。使用 `template_name` *或* `snapshot_id` 设置创建源，切勿同时使用两者。

代理通过 `ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep` 和 `execute` 工作。使用 `instructions.md` 指定它应该工作的地方以及它必须不触碰的内容。`mda delete` 也会删除管理的沙盒。

在 `mda dev` 期间，如果提供程序不可用，运行时回退到本地临时目录并打印路径。该回退仅用于开发——在开发部署中验证沙盒行为。

## 调度

`schedules/` 下每个文件一个调度，每个文件导出一个命名的 `schedule`。文件名成为调度名称。

```python
# schedules/daily_digest.py
from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="0 8 * * 1-5",
    timezone="America/Los_Angeles",
    prompt="Summarize what you learned yesterday and list open questions.",
)
```

定义 **一个** `prompt`（转换为用户消息）或 `input`（结构化的 LangGraph 输入）。`cron` 必须是标准的五字段表达式；没有 `timezone`，调度将运行 UTC。

调度默认使用临时线程——每次运行一个新线程，运行后删除。仅在运行应累积持久线程状态时传递 `thread={"mode": "persistent", "id": "..."}`。设置 `deliver_to` 通过配置的 Slack 频道发布结果。

声明在编译时提取，**不会运行您的代码**：仅使用字面量和顶层字面量常量。没有环境变量、函数调用或 `**kwargs`。

`mda deploy` 在部署后同步调度——它删除 MDA 拥有的调度并从当前文件重新创建它们，因此删除文件并重新部署会删除调度。**`--no-wait` 跳过同步**，因此添加、更改或删除调度时切勿使用它。

## 频道

频道将代理连接到外部消息服务：传入事件启动运行，响应返回到同一对话。**Slack 是唯一受支持的提供程序。** `channels/` 下每个文件一个频道，每个文件导出一个命名的 `channel`。

```python
# channels/slack.py
from managed_deepagents import channels

channel = channels.slack()
```

文件名设置频道名称及其传入路由——`channels/slack.py` 在 `POST /channels/slack/events` 接收事件。名称必须唯一；切勿将文件命名为 `channels/channel.py`。

频道启动的运行会暴露 `runtime.channel` 给工具和中间件，携带规范化的事件和会话地址以及发布和更新消息的方法。普通 HTTP 运行和调度运行没有原始频道，因此 `runtime.channel` 不存在。

Slack 设置需要一个项目根目录的 `slack-app-manifest.json` 和 `.env` 中的 `SLACK_SIGNING_SECRET` + `SLACK_BOT_TOKEN`。将清单视为事实来源；`.mda/` 下生成的文件是构建工件，不得提交。`runtime.channel` 永远不会暴露机器人密钥。

频道 *接收* 消息以启动运行。它不等于给代理 Slack *工具* 以启动操作——项目可能需要其中任何一个或两者。

## 评估

MDA 评估是 [Harbor](https://www.harborframework.com/docs/tasks) 评估。`evals/tasks/` 是规范数据集；在 `evals/scaffold/` 下编写完整的 Harbor 任务。`mda evals` 不会引入单独的格式，也不会运行试验——它将代理打包为 Harbor 并打印 `harbor run` 命令。

```bash
mda evals init smoke      # 可选的起点在 evals/scaffold/
mda evals compile .       # 将模板复制到 evals/tasks/，写入交接
```

`evals/` 不包含在部署构建中。Harbor 需要 Docker 以其默认环境，并且**不会读取 `.env`**——生成的作业配置写入 `${VAR}` 占位符，因此请在运行 Harbor 的 shell 中导出变量。验证者将数值奖励写入 `/logs/verifier/reward.txt` 或指标写入 `/logs/verifier/reward.json`。对于更深入的评估设计，请参阅 [[eval-engineering]]。

## CLI 参考

| 命令 | 用途 |
| --- | --- |
| `mda init <name>` | 模板化项目。如果目标位置存在则失败。 |
| `mda build [path]` | 编译为管理的 LangGraph 应用程序，但不部署。 |
| `mda dev [path]` | 编译并在 LangSmith Studio 中运行本地开发服务器。 |
| `mda deploy [path]` | 编译、同步 Context Hub、上传、部署、同步调度。 |
| `mda logs [path]` | 尾部部署代理的 Agent Server 日志。 |
| `mda delete [path]` | 删除部署及其创建的 LangSmith 资源。别名：`destroy`。 |
| `mda evals init\|compile` | 模板化 Harbor 任务；将代理打包为 Harbor。别名：`eval` |

关键标志：

- `init`：`--model SPEC`、`--instructions TEXT`、`--instructions-file PATH`、`--memory agent|none`、`--gateway`、`--no-sandbox`
- `build`：`--out OUT`（默认为 `<path>/.mda/build`，每次构建前清空）
- `dev`：`--port`、`--hostname`、`--no-browser`、`--no-reload`
- `deploy`：`--name`、`--deployment-type dev|prod`、`--workspace-id`、`--no-wait`
- `logs`：`--name`、`--lines`、`--level`、`--follow` / `--no-follow`、`--workspace-id`
- `delete`：`--name`、`--workspace-id`、`--yes`

`mda init` 从当前目录检测语言（`pyproject.toml` → Python，`package.json` → TypeScript，两者或都不存在 → 交互式提示）。`mda dev` 需要 Python 的 `uv` 并自行解析 LangGraph 开发服务器。

> `mda delete` 是破坏性的，会删除部署及其 LangSmith 资源。**在运行它之前与用户确认，并且永远不要未经提示传递 `--yes`**——该标志存在是为了跳过您应该得到的确认。

## 部署和 Context Hub

身份验证按顺序解析：`LANGGRAPH_HOST_API_KEY`、`LANGSMITH_API_KEY`、`LANGCHAIN_API_KEY`——首先从项目 `.env` 读取，然后从 shell 读取。在没有任何密钥的交互式终端中，`mda deploy` 会提示并保存到 `.env`。使用 `--workspace-id` 或 `LANGSMITH_WORKSPACE_ID` 与组织范围的密钥一起使用。

`mda deploy` 将本地输入路由到不同的管理表面：

```text
instructions.md + skills/**   -> Context Hub 部署拥有的上下文
.env                          -> 部署认证 + 非保留托管密钥（永远不会存档）
项目源                        -> .mda/build 存档 -> 托管部署
schedules/**                  -> LangSmith 调度任务，部署后生效
```

非保留 `.env` 条目——提供程序密钥、工具凭据、数据库 URL——作为托管部署密钥转发。保留平台变量（`LANGSMITH_API_KEY`、`LANGGRAPH_HOST_API_KEY`、`LANGCHAIN_API_KEY`、`LANGSMITH_WORKSPACE_ID`）认证部署并路由它，但永远不会作为用户管理的密钥上传。如果模型提供程序密钥无法从 `.env`、shell 或 LangSmith 工作空间密钥中获取，则部署会在上传前失败。

Context Hub 持有 `/instructions.md` 和 `/skills/**`（部署拥有，每次部署重新同步）以及 `/memories/agent/**`（运行时拥有，跨部署保留）。

故障排除：`no agent entry file found` → 在根目录添加 `agent.py`。401/403 → 密钥的工作区缺乏 beta 访问。Context Hub 冲突 → 重新运行部署。构建超过 200 MB → 删除生成工件。`BUILD_FAILED` / `DEPLOY_FAILED` → 打开打印的 URL 并阅读修订日志。

## 人机交互

使用 `interrupt_on` 在敏感工具调用前暂停，并使用 `permissions` 门控文件系统路径：

```python
agent = define_deep_agent(
    name="support-agent",
    model="anthropic:claude-sonnet-4-6",
    tools=[refund_customer],
    interrupt_on={"refund_customer": True},
)
```

`interrupt_on` 应用与 LangChain 的人机交互中间件相同的行为；参见 [[langgraph-human-in-the-loop]] 了解批准/编辑/拒绝语义。中断需要持久线程状态，并且管理的运行时拥有检查点，因此无需额外设置。

在 `mda dev` 期间在 Studio 中响应中断。在部署的代理上，通过带有 `Command(resume=...)` 负载的 LangGraph 服务器 API 恢复——但请注意，从您自己的应用程序进行程序化调用未在公共 beta 期间记录。

## 注意事项

- **`name=` 是必需的** 在 `define_deep_agent` / `defineDeepAgent`。没有它的定义会失败。
- **模型 ID 需要提供程序前缀**：`anthropic:claude-sonnet-4-6`，而不是裸模型名称。Python 使用 `google_genai:`, TypeScript 使用 `google-genai:`, Gateway 使用 `provider/model`。
- **不要在代理定义中设置管理字段**（`backend`、`store`、`checkpointer`、`memory`、`skills`、系统提示）。
- **内存通过 `memory.py` 选择性启用**，而不是构造函数参数。`disable_memory` 是遗留的——声明或删除 `memory.py` 而不是。
- **MCP 连接器确实存在**——`connectors/` 下导出 `connector = connectors.mcp(mcp_servers={...})` 的模块。除非您设置 `prefix_tool_name_with_server_name=False`，否则工具名称为 `{server}__{tool}`；保留前缀会默默地破坏引用裸名称的 `interrupt_on` 键。
- **添加管理文件后重新启动 `mda dev`。** 新的 `memory.py`、`identity.py`、`schedules/` 或 `channels/` 声明在编译时发现，而不是通过热重载。
- **`--no-wait` 跳过调度同步** 并在 `DEPLOYED` 之前退出。
- **调度声明必须是静态字面量**——编译器提取它们，而不会运行您的代码。
- **`.env` 永远不会存档**，`.gitignore` 必须将其排除在版本控制之外。不要在代表用户的情况下向其中写入实时密钥。
- **文档的发布 CLI 略微领先于发布。** 在信任标志或导入之前，请与 `mda --help` 和安装的包进行验证。截至 `mda` 0.5.0：沙盒文档显示 `sandboxes.langsmith(...)`，但该导入会引发 `ImportError`——使用上面显示的 `define_sandbox(...)`；并且文档中记录的 `mda init --identity` 和 `mda deploy --configure-slack` 标志不存在（`identity.py` 默认模板化）。
