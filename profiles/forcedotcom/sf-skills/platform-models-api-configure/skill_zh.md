# 为 AI 编码代理设置 Salesforce 模型 API

Salesforce 模型 API (`https://api.salesforce.com/ai/gpt/v1`) 使用已签名的 **OrgJWT** (通过 `client_credentials` 获取，具有 `sfap_api` 范围 — 参见 `scripts/get-orgjwt.sh`；无需代理)。该认证和基础 URL 对 **任何** 代理都是相同的。然后每个代理如何与端点通信是代理特定的：Anthropic 客户端 (**Claude Code** 和 **Claude Agent SDK**) 通过 **Bedrock 模式** (第 3 步中的环境变量) 进行路由，而其他代理 (例如 Codex) 则使用它们自己的客户端配置针对同一端点和令牌 — Bedrock 模式 **不** 适用于它们。

以下步骤是 **Claude Code / Claude Agent SDK 的参考实现** (Bedrock 模式 + JSON 设置文件 + API 密钥辅助工具)。对于非 Bedrock 代理，请重用 OrgJWT 认证 (第 1 步) 和基础 URL，并在该代理自己的配置位置应用等效的客户端设置，而不是 Bedrock 环境变量。

捆绑脚本位于 `scripts/` 中。以下路径占位符：`<SKILL>` = **此技能自己的目录** 的绝对路径 (包含此 `SKILL.md` 的文件夹；从上下文中的技能路径解析)。`<ABS>` = 用户项目根目录的绝对路径。始终输出完全解析的绝对路径 — API 密钥辅助工具从未定义的工作目录运行，因此相对路径会使其失效。

## 前置条件

在组织中创建一个连接应用程序，具有 **`sfap_api`** OAuth 范围并启用 **client_credentials** 流 (消费者密钥/密钥 + 运行用户)。设置步骤：https://developer.salesforce.com/docs/ai/agentforce/guide/access-models-api-with-rest.html
`curl` + `jq` 已安装。

## 收集输入

- `SF_INSTANCE_URL` — 组织 My Domain，例如 `https://acme.my.salesforce.com`
- `SF_CLIENT_ID`, `SF_CLIENT_SECRET` — 连接应用程序的消费者密钥/密钥
- 模型 API 基础 URL：`https://api.salesforce.com/ai/gpt/v1`
- 模型：一个完全限定名的 `sfdc_ai__…`，例如
  `sfdc_ai__DefaultBedrockAnthropicClaude46Sonnet`
  (完整列表：https://developer.salesforce.com/docs/ai/agentforce/guide/supported-models.html)
- 范围：项目 (`<cwd>/.claude/settings.json`，默认) 或用户 (`~/.claude/settings.json`) — 参考代理设置路径
- 标头 — `<FEAT>` = `x-client-feature-id` (默认 `ai-platform-models-connected-app`),
  `<APP>` = `x-sfdc-app-context` (默认 `EinsteinGPT`)。用于第 2 步验证 curl 和 `ANTHROPIC_CUSTOM_HEADERS`。

## 步骤 (参考实现)

JSON 设置 + API 密钥辅助工具代理的具体值。重用 OrgJWT 认证、验证 curl 和基础 URL，对于任何代理都是原样；调整设置文件位置和环境变量连接到目标代理。

1. 编写 `<project>/.claude/.orgjwt.env` (chmod 600)，gitignore 它：
   ```ini
   SF_INSTANCE_URL="..."
   SF_CLIENT_ID="..."
   SF_CLIENT_SECRET="..."
   ```
2. 验证 — 必须在写入设置之前返回 `200`：
   ```bash
   TOKEN=$(bash <SKILL>/scripts/get-orgjwt.sh <ABS>/.claude/.orgjwt.env)
   curl -s -o /dev/null -w '%{http_code}\n' \
     <MODELS_API_URL>/model/<MODEL>/invoke-with-response-stream \
     -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
     -H 'x-client-feature-id: <FEAT>' -H 'x-sfdc-app-context: <APP>' \
     --data '{"anthropic_version":"bedrock-2023-05-31","max_tokens":16,"messages":[{"role":"user","content":"hi"}]}'
   ```
3. 编写 `.claude/settings.json` (合并到现有；保留其他键)：
   ```json
   {
     "apiKeyHelper": "bash <SKILL>/scripts/get-orgjwt.sh <ABS>/.claude/.orgjwt.env",
     "model": "<MODEL>",
     "env": {
       "ANTHROPIC_AUTH_TOKEN": "",
       "CLAUDE_CODE_USE_BEDROCK": "1",
       "CLAUDE_CODE_SKIP_BEDROCK_AUTH": "1",
       "ANTHROPIC_BEDROCK_BASE_URL": "<MODELS_API_URL>",
       "ANTHROPIC_SMALL_FAST_MODEL": "<MODEL>",
       "ANTHROPIC_DEFAULT_MODEL": "<MODEL>",
       "ANTHROPIC_CUSTOM_HEADERS": "x-client-feature-id: <FEAT>\nx-sfdc-app-context: <APP>"
     }
   }
   ```
   在 `apiKeyHelper` 中使用绝对路径。(`<FEAT>` / `<APP>` 默认值在上述 "收集输入" 中。)
4. 告知管理员完全重启代理 (`claude` 为参考代理) — 设置和 API 密钥辅助工具仅在启动时加载。

### 捕获为运行手册 (当被要求记录时，而不是应用到机器上)

如果用户希望将设置记录下来以供审查，而不是应用到他们的机器上 (例如 "保存为 Markdown 运行手册")，请将上述所有内容按顺序和自包含地写入请求的文件 (例如 `models-api-setup-runbook.md`)：
精确的 `.orgjwt.env` 内容、`chmod 600` + gitignore 注释、验证 curl (带有 "必须在写入设置之前返回 `200`" 的注释)、完整的 `settings.json` 块 (包含第 3 步的每个键) 和最终的 "完全重启 `claude`" 步骤。不要遗漏任何九个 `settings.json` 键。

## 完成前验证

- [ ] 创建了 `.claude/.orgjwt.env`，`chmod 600`，并 gitignore
- [ ] 验证 curl 在写入 `settings.json` 之前返回 HTTP `200`
- [ ] `ANTHROPIC_AUTH_TOKEN` 在 `settings.json` 中设置为 `""`
- [ ] `CLAUDE_CODE_USE_BEDROCK` 设置为 `"1"`
- [ ] `CLAUDE_CODE_SKIP_BEDROCK_AUTH` 设置为 `"1"`
- [ ] `ANTHROPIC_BEDROCK_BASE_URL` 精确为 `https://api.salesforce.com/ai/gpt/v1` (无尾随斜杠/路径)
- [ ] `model`、`ANTHROPIC_DEFAULT_MODEL` 和 `ANTHROPIC_SMALL_FAST_MODEL` 都使用完全限定的 `sfdc_ai__…` 别名
- [ ] `ANTHROPIC_CUSTOM_HEADERS` 包含 `x-client-feature-id` 和 `x-sfdc-app-context`
- [ ] `apiKeyHelper` 使用绝对路径 (`bash <SKILL>/scripts/get-orgjwt.sh <ABS>/.claude/.orgjwt.env`)
- [ ] 用户被告知完全重启 `claude`

## 必须完全精确 (每个都会导致特定失败)

- `"ANTHROPIC_AUTH_TOKEN": ""` — 清除任何可能优先于 `apiKeyHelper` 的全局令牌 (优先级：`ANTHROPIC_AUTH_TOKEN` > `ANTHROPIC_API_KEY` > `apiKeyHelper`)。没有它 → 错误/旧的 bearer → 401/404。
- `CLAUDE_CODE_USE_BEDROCK=1` — 激活 Bedrock API 客户端；没有它，Claude Code 使用标准的 Anthropic API 协议并完全忽略 `ANTHROPIC_BEDROCK_BASE_URL`，因此每次调用都绕过模型 API。
- `CLAUDE_CODE_SKIP_BEDROCK_AUTH=1` — 否则，Claude Code 会用 AWS SigV4 覆盖 `Authorization`，OrgJWT 从未到达。
- `apiKeyHelper` 必须作为 `bash <路径> <credsfile>` 调用 (避免退出码 126)。
- 模型必须是一个完全限定的 `sfdc_ai__…` 别名 (参见支持的模型)。
- 认证是来自 `client_credentials` 的 OrgJWT (一个已签名的 JWT，2 个点，范围 `sfap_api`) — **不是** `sf org display` (未签名的会话令牌 → 404)。`sf` CLI 没有客户端密钥命令；辅助工具调用 `/services/oauth2/token`。
- 仅 `ANTHROPIC_BEDROCK_BASE_URL` 路由；不需要租户 ID 标头。

## 诊断

| 错误 | 含义 | 首先检查 |
|-------|---------|-------------|
| `401` | 令牌不是有效的 OrgJWT | 连接应用程序 `sfap_api` 范围，`client_credentials` 流启用，`.orgjwt.env` 中的消费者密钥/密钥；`ANTHROPIC_AUTH_TOKEN` 未清除为 `""` |
| `404` | 令牌有效但模型/环境/组织无法路由 | 完全限定的 `sfdc_ai__…` 模型别名，`ANTHROPIC_BEDROCK_BASE_URL` 精确为 `https://api.salesforce.com/ai/gpt/v1`，组织有权使用模型 API，`ANTHROPIC_AUTH_TOKEN` 清除 |
| `model not available` | 非别名模型 ID | 替换为完全限定的 `sfdc_ai__…` 别名 (参见支持的模型) |
