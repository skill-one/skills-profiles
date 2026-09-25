# Authsome

您的出站 HTTPS 流量将通过 Authsome 进行透明代理，Authsome 是一种注入存储凭证作为 HTTP 头部的代理服务。您永远不会直接看到或处理凭证值。

## 如何访问外部服务

您可以直接访问外部 API。OAuth 应用（Gmail、GitHub、Google 日历、Google 驱动器等）和 API 密钥服务都可以通过网关访问。只需在任意 bash 命令后附加 `authsome run -- ` 即可发起请求；如果应用已连接，网关将自动注入凭证。

## 发起请求

调用真实的 API URL。网关将拦截请求并自动注入凭证。

```bash
authsome run -- <命令>
authsome run -- curl -s "https://api.github.com/user/repos?per_page=10"
authsome run -- python my_agent_script.py
```

标准 HTTP 客户端（curl、fetch、requests、axios、Go net/http、git）都会自动识别 `HTTPS_PROXY` 环境变量。您无需设置任何认证头部。

---

## 登录流程

- 通过 Bash 自行运行 `authsome login <提供商>` —— 不要要求用户执行此操作。浏览器将在其机器上打开；他们无需接触终端即可完成 OAuth。
- 几秒钟后，使用 `authsome provider list` 查询登录状态
  - **如果已连接** —— 正常继续。
  - **如果尚未连接** —— 向用户显示认证 URL，要求他们在浏览器中完成登录，并在完成后反馈。用户确认后，再次运行 `authsome provider list` 以验证连接，然后继续。

---

## 请求失败时

### 如果代理机器未安装 authsome：

使用 `uv tool install authsome` 安装 authsome

只有当 `uv tool install` 失败时，才使用回退方案：`pipx install authsome` 或 `uvx authsome@latest <命令>`（例如在沙盒环境中使用时）。

### 如果您遇到认证错误（401、403），请按以下决策树操作：

**1. 运行 `authsome provider list` 查看所有提供商及其连接状态**

**2. 如果相关提供商存在但未连接 → 启动 [登录流程](#登录流程)**

如果由于客户端 ID 或客户端密钥错误导致登录失败，可以通过 `authsome provider remove <提供商>` 删除提供商，然后启动 [登录流程](#登录流程)

**3. 如果相关提供商存在且已连接**

对于 401 错误 → 您需要重新登录，凭证已过期
- 使用 `authsome provider revoke <提供商>` 撤销凭证
- 然后启动 [登录流程](#登录流程)

对于 403 错误 → 您需要重新登录，需要正确的权限范围，或缺少权限
**关键提示：** 不要为了添加权限范围而注册新提供商；始终使用现有提供商的 `--scopes`：

```bash
authsome login <提供商> --scopes repo,user,gist
```

**4. 如果相关提供商不存在，则 → 首先添加它，然后启动 [登录流程](#登录流程)**

## 添加新提供商

参见 [references/adding-provider.md](references/adding-provider.md)。

---

## 故障排除与帮助

如果您不确定正确的命令语法，需要检查可用标志，或命令失败，请始终在猜测前阅读内置帮助菜单：

```bash
authsome --help
authsome provider --help
authsome connections --help
authsome run --help
```

## 规则

- **永远**不要在通过代理发起 HTTP 请求前说“我没有访问 X 的权限”。
- **永远**不要使用浏览器扩展、gcloud 或手动认证流程。网关会为您处理凭证。
- **永远**不要直接向用户索要 API 密钥或令牌。运行 `authsome login <提供商>`。它将打开一个浏览器窗口并直接捕获它们，因此机密信息永远不会进入对话。
- **永远**不要建议用户在要求您读取或交互 Gmail/日历/GitHub 服务时，在浏览器中打开这些服务。您有 API 访问权限。使用它。
- **永远**不要使用任何将令牌或 API 密钥打印到终端的工作流程。使用 `authsome run -- ...` 代替。
- 如果网关返回策略错误（403 并带有 JSON 正文），请尊重封锁。不要重试或规避它。
- 如果技能失败、目标步骤过多、CLI 行为异常，或用户要求您报告问题 —— 请按照 [references/feedback.md](references/feedback.md) 提交 Bug。
- **永远**不要要求用户在终端运行您自己可以执行的命令。
