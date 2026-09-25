您正在通过Caveman网关配置此仓库。Caveman是一个字节保留型LLM代理：在记录模式下，它会测量您的应用程序发送的内容及其成本，而不会改变其他任何东西。您的任务是进行最小化、经过验证的集成——而不是重构。

引导您至此的提示提供了四个值。参考它们：

- `GATEWAY` — 网关基础URL（例如 `https://gateway.caveman.so` 或 `http://127.0.0.1:8787`）
- `CAVE_API_KEY` — 网关认证密钥（像任何API密钥一样处理：仅环境变量，永不提交，永不完整打印）
- `PROVIDER_KEYS` — `stored`（提供者密钥加密存储在Caveman Cloud中）或 `byok`（此应用程序每条请求发送自己的提供者密钥）
- `DASHBOARD` — 仪表板基础URL（例如 `https://app.caveman.so`）

如果任何值缺失，请停止并请求它。不要猜测URL或生成密钥。

## 规则（不可协商）

1. **连贯集成。** 通过现有配置和负责的接口连接所有实时LLM调用点。确保正确性需要触及每一层。不要进行临时的重构或格式清理；只有在抽象明确所有权或降低生命周期成本时才添加抽象。
2. **密钥保留在环境变量中。** `CAVE_API_KEY` 放入仓库已使用的环境文件（`.env`、`.env.local`、…）。如果该文件没有被git忽略，请将其添加到 `.gitignore` 中并说明。不要在源代码中硬编码密钥。
3. **仅报告您观察到的内容。** 最终报告将显示真实验证响应中的HTTP状态和用量数据——永不假设成功。如果验证失败，请报告匹配的失败模板。
4. **仅记录模式。** 您正在添加测量功能。您不会启用任何优化，也不会声称任何节省——验证后的节省金额为0，直到明确启用优化器并通过其评估门。
5. **提供者密钥与您无关。** 在 `PROVIDER_KEYS: stored` 模式下，您永远不会看到密钥。在 `byok` 模式下，应用程序现有的提供者密钥保持原位不变。

## 第1步——查找所有实时LLM调用点

阅读依赖文件（`package.json`、`requirements.txt`、`pyproject.toml`、`go.mod`、锁文件）并在源代码中搜索LLM客户端：

- SDK导入：`openai`、`@anthropic-ai/sdk`、`anthropic`、`ai` + `@ai-sdk/*`（Vercel）、`langchain*`、`litellm`、`google-genai` / `@google/genai`、`crewai`、`pydantic_ai`、`openai-agents` / `agents`
- 原始HTTP请求到 `api.openai.com`、`api.anthropic.com`、`generativelanguage.googleapis.com`
- 现有基础URL环境变量：`OPENAI_BASE_URL`、`OPENAI_API_BASE`、`ANTHROPIC_BASE_URL`、`GEMINI_BASE_URL`、`GOOGLE_GEMINI_BASE_URL`

在更改任何内容之前列出您找到的内容（每个调用点文件:行）。如果您找不到**任何**LLM调用点，请停止并报告文件末尾的“无内容可连接”模板——不要编造集成。

## 第2步——选择应用程序别名

一个别名在网关路径中命名此应用程序：`GATEWAY/w/<app>`。从包/模块名称中派生它（例如 `support-bot`、`acme-api`）。语法：
小写 `[a-z0-9]` 开头，然后是 `[a-z0-9._-]`，最多64个字符。为整个应用程序组在仪表板下分配别名。

## 第3步——连接每个调用点

模式始终相同：**基础URL → 带有 `/w/<app>` 的网关，加上一个认证头。** 网关认证是 `x-cave-api-key: CAVE_API_KEY` (`Authorization: Bearer CAVE_API_KEY` 在头位置不方便时也有效）。在 `PROVIDER_KEYS: byok` 模式下，还发送 `x-cave-upstream-key: <应用程序已使用的提供者密钥>`。

两个使连接安全的事实（两者都是网关强制执行的，不是希望）：
网关从头开始重建上游认证头，因此客户端的 `Authorization`/`x-api-key` 值永远不会转发到提供者；并且 `stored` 模式下，上游认证来自服务器端的加密连接。因此，在 `stored` 模式下，当SDK坚持要求api-key参数时，将其设置为Cave密钥——它认证网关，不会再进一步。

确切形状（使用与每个调用点匹配的形状——这些是产品发布的配方，不是建议）：

**OpenAI SDK (TS)** — 聊天完成和响应都通过：
```ts
const client = new OpenAI({
  baseURL: `${process.env.CAVE_GATEWAY_URL}/w/<app>/openai/v1`,
  apiKey: process.env.OPENAI_API_KEY,           // byok: 不变 · stored: 使用 CAVE_API_KEY
  defaultHeaders: {
    "x-cave-api-key": process.env.CAVE_API_KEY!,
    // byok 仅：
    "x-cave-upstream-key": process.env.OPENAI_API_KEY!,
  },
});
```

**OpenAI SDK (Python)** — 相同形状：`base_url=f"{gw}/w/<app>/openai/v1"`，
`default_headers={"x-cave-api-key": ..., "x-cave-upstream-key": ...}`。

**Anthropic SDK (TS/Python)** — SDK 自己追加 `/v1/messages`。在两种模式下都需要 `x-cave-api-key` 头（此SDK自己的密钥参数 `x-api-key` 不是网关认证头）：
```python
client = anthropic.Anthropic(
    base_url=f"{os.environ['CAVE_GATEWAY_URL']}/w/<app>",
    api_key=os.environ["ANTHROPIC_API_KEY"],      # byok: 不变 · stored: 使用 CAVE_API_KEY
    default_headers={
        "x-cave-api-key": os.environ["CAVE_API_KEY"],
        # byok 仅：
        "x-cave-upstream-key": os.environ["ANTHROPIC_API_KEY"],
    },
)
```

**Vercel AI SDK** — `createOpenAICompatible({ baseURL: `${gw}/w/<app>/openai/v1`,
headers: { "x-cave-api-key": ... } })`；Anthropic模型通过
`createAnthropic({ baseURL: `${gw}/w/<app>/v1`, headers: { ... } })`。

**LangChain / LangGraph** — `ChatOpenAI(base_url=f"{gw}/w/<app>/openai/v1`,
default_headers={...})`；`ChatAnthropic(base_url=f"{gw}/w/<app}`,
default_headers={...})`。LangGraph 继承您传递给它的任何模型。

**LiteLLM** — 每次调用 `api_base=f"{gw}/w/<app>/openai/v1"` +
`extra_headers={...}`，或在 LiteLLM 代理 `config.yaml` 中全局设置。

**原始HTTP / 任何其他** — 交换主机，保留提供者的原生路径：
`GATEWAY/w/<app>/v1/chat/completions`（OpenAI 协议）或
`GATEWAY/w/<app>/v1/messages`（Anthropic 协议），添加头信息。

具体来说，使用别名 `support-bot` 和托管网关，OpenAI-SDK 基础URL读取 `https://gateway.caveman.so/w/support-bot/openai/v1`。并且在 `stored` 模式下，完全删除 `x-cave-upstream-key` 行——它仅适用于 `byok`。

对于未列出的框架（google-genai、crewai、pydantic-ai、openai-agents），获取 `<docs origin>/docs/integrations/` 下匹配的页面——与这个技能来源相同的起源——并遵循它。

将以下内容添加到仓库的环境文件中（并在代码中引用——不要使用字面量）：

```
CAVE_GATEWAY_URL=<GATEWAY>
CAVE_API_KEY=<CAVE_API_KEY>
```

## 第4步——使用一个真实请求进行验证

用户将设置提示粘贴到授权此操作：一个小的验证请求。现在发送它——不要暂停请求权限。一个因您犹豫而未验证的集成比一个微小的请求更糟糕；自主完成验证和报告是这个技能的目的。

通过您刚刚构建的连接发送一个最小的请求——如果应用程序有脚本，使用应用程序自己的最便宜路径，否则使用 curl **与您刚刚连接的协议匹配的路径**，使用应用程序自己的模型和小限制（`max_tokens` ≤ 32）：

```bash
# OpenAI-协议连接：
curl -sS "$CAVE_GATEWAY_URL/w/<app>/v1/chat/completions" \
  -H "x-cave-api-key: $CAVE_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"<模型仓库已使用>","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}'

# Anthropic-协议连接：
curl -sS "$CAVE_GATEWAY_URL/w/<app>/v1/messages" \
  -H "x-cave-api-key: $CAVE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"<模型仓库已使用>","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}'
```

(byok: 添加 `-H "x-cave-upstream-key: $PROVIDER_KEY"`.) 这是一个真实的、计费的提供者请求——这就是要点：真实流量，真实测量。

读取响应。成功 = HTTP 200 并带有 `usage` 块。任何其他情况 = 匹配的失败模板。

## 第5步——报告

以完全相同的格式结束，值来自您实际执行和看到的内容：

```
## Caveman 在此仓库中已启用

连接：在 <n> 个文件中的 <n> 个调用点
  - <文件> — <一行说明更改内容>
应用程序别名：<app> — 为此应用程序组分配支出
验证：HTTP 200 · 模型 <模型> · <in> 在 / <out> 外令牌（一个真实请求）
模式：记录——仅测量。未更改模型可见字节，未启用优化。验证后的节省金额为0，直到您启用优化器并通过其评估门。这种诚实是产品的核心。

查看金额：<DASHBOARD>/traces — 您的请求是第一行，从公共目录定价。 <DASHBOARD>/getting-started 切换到“已收到第一个请求。”

需要按工作流（例如 support-reply 与 nightly-digest）而不是仅按应用程序分割支出？请说“发现工作流”——我会获取 <docs origin>/docs/discover-workflows.md 并标记每个调用点所执行的任务。
```

## 失败模板（使用原样，填写——永不软化）

- **无内容可连接**： "我在此仓库中找不到LLM调用点（搜索了SDK、原始提供者HTTP、基础URL环境变量）。如果此仓库运行的是编码代理而不是发送LLM代码，请使用 `caveman wrap <agent>` 代替——见 <DASHBOARD>/getting-started。"
- **网关无法访问**： "验证请求无法访问 GATEWAY (<错误>)。连接已就位但未验证——直到网关可访问，不会测量任何内容。检查URL和网络，然后重新运行上述验证 curl。"
- **401 cave_invalid_api_key**： "网关拒绝了 CAVE_API_KEY。在 <DASHBOARD>/getting-started 中生成新密钥并更新环境文件；连接本身未更改。"
- **404 cave_route_not_found**： "网关未匹配任何路由——通常是格式错误的 /w/<app> 别名（小写 [a-z0-9] 开头，然后是 [a-z0-9._-]，最多64个）或与SDK协议不匹配的路径。修复URL并重新验证。"
- **提供者错误（通过网关的4xx/5xx）**： 原封不动地报告状态+正文；网关可访问且认证通过，上游调用失败——通常是应用程序本身的提供者密钥或模型名问题。

对于这些中的任何一项，都不要报告成功。未验证的集成报告为未验证。
