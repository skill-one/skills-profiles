# 访问受保护的 Vercel 部署

使用调用者的现有 Vercel 身份验证。不要禁用部署保护或要求长期有效的绕过密钥作为第一个解决方案。

## 选择访问路径

### HTTP 请求：使用 `vercel curl`

对于响应体、请求头、健康检查和 API 调用，将原始 `curl` 替换为 `vercel curl` (`vc curl`)。它接受原生 curl 选项，并使用 Vercel 身份验证访问受保护的预览和生产部署。

```bash
vc curl https://my-app.vercel.app/api/health
vc curl https://app.example.com/api/health
vc curl my-app.vercel.app/api/users -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada"}'
vc curl /api/health
```

仅路径形式的目标链接项目的生产部署。当精确部署很重要时，请传递完整 URL。

如果身份验证失败，请在更改保护设置之前检查本地身份和项目：

```bash
vc whoami
```

检查 `.vercel/project.json` 以确认链接的项目和团队。仅在目录未链接或链接到错误的项目时运行 `vc link`。仅在 CLI 报告没有可用认证用户时运行 `vc login`。

### 浏览器自动化：将开发 OIDC 令牌作为请求头附加

浏览器请求必须在请求头中包含短期的本地令牌：

```text
x-vercel-trusted-oidc-idp-token: <VERCEL_OIDC_TOKEN>
```

使用支持原点范围请求头的浏览器工具。使用 `agent-browser`，在不打印或持久化令牌的情况下注入开发变量：

```bash
vc env run -- sh -c \
  'test -n "$VERCEL_OIDC_TOKEN" && agent-browser open "$1" --headers "{\"x-vercel-trusted-oidc-idp-token\":\"$VERCEL_OIDC_TOKEN\"}"' \
  sh https://my-app.vercel.app
```

然后在同一会话中继续正常的浏览器工作流程。对于 Playwright 或其他浏览器驱动程序，在第一次导航之前，在浏览器上下文的附加 HTTP 头中设置相同的请求头。

如果本地 CLI 版本不通过 `vc env run` 提供令牌，请使用以下命令刷新本地开发凭证：

```bash
vc env pull .env.local --yes
```

通过项目的现有 dotenv 机制加载该文件。永远不要打印令牌，不要将令牌值粘贴到源代码中，也不要提交 `.env.local`。

使用 `x-vercel-trusted-oidc-idp-token` 用于可信来源。不要替换 `x-vercel-oidc-token`；该请求头发送到 Vercel 函数中，并用于不同的目的。

## 可信来源规则

链接的 Vercel 项目的本地开发令牌默认可以访问该项目的预览部署。它不会自动访问受保护的生产部署。对于受保护的生产部署，该项目的可信来源条目必须允许 `development` → `production`。

不要要求用户为正常的同项目预览情况配置可信来源。

需要配置的情况包括：

- 目标是受保护的生产部署，并且调用者使用本地开发令牌；
- 调用者属于另一个 Vercel 项目或团队；
- 目标项目的自访问规则已自定义；或
- 响应是 `TRUSTED_SOURCES_ENVIRONMENT_MISMATCH`。

在目标项目中，打开 **设置 → 部署保护 → 可信来源**。添加或编辑调用者，并允许所需的 `from` → `to` 环境对。本地令牌具有 `development` 环境，因此要访问受保护的生产环境需要 `development` → `production`。

将其视为访问控制更改：解释所需的精确规则，并在更改之前获得授权。不要放宽无关的环境对。

## 诊断响应

- Vercel 登录、SSO 或部署保护页面表示请求未使用接受的认证路径。
- `TRUSTED_SOURCES_ENVIRONMENT_MISMATCH` 表示令牌有效，但调用者的环境不允许访问目标环境。
- 在 Vercel 保护绕过后生成的应用程序生成的 `401` 或 `403` 属于应用程序自身的身份验证，必须单独调试。
- 标记为 `"target": "production"` 的部署仍然可以受保护。不要假设生产环境是公开的。

## 避免

- 不要禁用部署保护以使自动化通过。
- 不要在收到保护页面后反复发送原始未认证的 `curl`。
- 当 `vc curl` 或原点范围的 OIDC 头可以认证请求时，不要启动交互式 SSO 浏览器登录。
- 不要在日志、截图、提交的文件或用户界面输出中暴露 `VERCEL_OIDC_TOKEN`。

## 相关技能

- 一般 Vercel CLI 使用：`⤳ 技能: vercel-cli`
- 端到端应用程序验证：`⤳ 技能: verification`
