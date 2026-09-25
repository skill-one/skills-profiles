# 认证 Google Cloud

[认证](https://docs.cloud.google.com/docs/authentication.md.txt) 是证明 **你是谁** 的过程。在 Google Cloud 中，你代表一个 **主体**（如用户或服务）。这是在 [授权](https://docs.cloud.google.com/iam/docs/overview.md.txt)（确定 **你能做什么**）之前的第一个步骤。

## 认证

### 代理的澄清问题

在提供具体解决方案之前，请与用户澄清以下几点：

1.  **谁或什么正在进行认证？**（人类开发者、本地脚本还是生产环境中的应用程序？）
2.  **代码运行在哪里？**（本地笔记本电脑、[计算引擎](https://docs.cloud.google.com/compute/docs.md.txt)、[GKE](https://docs.cloud.google.com/kubernetes-engine/docs.md.txt)、[Cloud Run](https://docs.cloud.google.com/run/docs.md.txt) 或其他云如 AWS/Azure？）
3.  **目标是什么？**（Google Cloud API（如存储/BigQuery）还是你构建的自定义应用程序？）
4.  **你使用高级客户端库吗？**（例如，Python、Go、Node.js 库通常会自动处理 ADC。）

---

## 人类认证

为了让用户访问 Google Cloud，他们需要一个 Google Cloud 可以识别的身份。

### 用户身份类型

Google Cloud 支持多种配置内部员工（开发人员、管理员、员工）身份的方式：

*   **[Google 管理的帐户](https://docs.cloud.google.com/iam/docs/user-identities.md.txt)**：你可以使用 Cloud Identity 或 Google Workspace 创建受管理的用户帐户。这些帐户被称为受管理的帐户，因为你的组织控制它们的生命周期和配置。
*   **[使用 Cloud Identity 或 Google Workspace 进行联合](https://docs.cloud.google.com/iam/docs/user-identities.md.txt)**：你可以联合身份，以允许用户使用他们现有的身份和凭据登录 Google 服务。用户针对外部身份提供程序（IdP）进行认证，但你必须使用 Google Cloud 目录同步 (GCDS) 或其他外部权威来源（如 Active Directory 或 Microsoft Entra ID）等工具将帐户同步到 Google Cloud。
*   **[员工身份联合](https://docs.cloud.google.com/iam/docs/user-identities.md.txt)**：这允许你使用外部 IdP 直接使用 IAM 对员工进行认证和授权。与标准联合不同，你不需要将用户身份从现有 IdP 同步到 Google Cloud 身份。它支持无同步、基于属性的单一登录。

### 开发人员和管理员访问方法

用于在开发和管理工作期间与 Google Cloud 资源和 API 交互。

*   **[Google Cloud 控制台](https://console.cloud.google.com/)**：主要 Web 界面。你使用你的 Google 帐户（Gmail 或 [Google Workspace](https://workspace.google.com/)) 进行认证。
*   **[gcloud CLI](https://docs.cloud.google.com/sdk/docs/install-sdk.md.txt) (`gcloud auth login`)**：用于认证 CLI 本身，以便你可以运行管理命令（例如，`gcloud compute instances list`）。它使用存储在本地的一个 **凭据**（如 OAuth 2.0 刷新令牌）。
*   **本地开发与 [应用默认凭据 (ADC)](https://docs.cloud.google.com/docs/authentication/application-default-credentials.md.txt) (`gcloud auth application-default login`)**：这与 CLI 认证不同。它创建一个本地 JSON 文件，Google Cloud **客户端库**（Python、Java 等）使用该文件，在你本地笔记本电脑上运行代码时充当“你”。
*   **[服务帐户模拟](https://docs.cloud.google.com/docs/authentication/use-service-account-impersonation.md.txt)**：出于安全原因，开发人员应避免下载服务帐户密钥。相反，他们应作为人类 (`gcloud auth login`) 进行认证，并使用服务帐户模拟来运行 CLI 命令或生成短期凭据。这是本地开发和故障排除的一个关键最佳实践。

### 对于最终用户和客户

当人类（不是开发人员）需要访问你在 Google Cloud 上部署的 Web 应用程序时使用。注意：这些与员工身份是不同的。

*   **[感知身份代理 (IAP)](https://docs.cloud.google.com/iap/docs.md.txt)**：充当 Web 应用程序的中心授权层。它拦截 Web 请求并在允许用户访问应用程序之前验证用户的身份（通过 Google Workspace、Cloud Identity 或外部提供程序）。它通常用于保护不需要 VPN 的内部应用程序，或保护客户门户。
*   **[身份平台](https://docs.cloud.google.com/identity-platform/docs.md.txt)**：一种客户身份和访问管理 (CIAM) 解决方案，可以直接将消费者登录（电子邮件/密码、电话、社交）添加到你的自定义构建应用程序的代码中。

---

## 服务到服务认证

当代码在生产环境中运行时，它应该使用 **服务帐户** 而不是人类用户帐户。

### 服务帐户和服务代理

*   **[服务帐户](https://docs.cloud.google.com/iam/docs/service-account-overview.md.txt)**：一个特殊身份，专为非人类用户设计。它就像一个“机器人身份”，有自己的电子邮件地址。
*   **[服务代理](https://docs.cloud.google.com/iam/docs/service-agents.md.txt)**：由 Google 管理的服务帐户，允许服务（如 Pub/Sub）代表你访问你的资源。

### 最佳实践：附加服务帐户

不要使用 **服务帐户密钥**（危险的 JSON 文件），而应将自定义服务帐户附加到 Google Cloud 资源。然后，该资源的运行环境通过本地元数据服务器提供一个 **令牌**（一个短期数字对象）。

*   **[计算引擎](https://docs.cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances.md.txt)**：在创建 VM 时分配服务帐户。
*   **[Cloud Run](https://docs.cloud.google.com/run/docs/securing/service-identity.md.txt)**：在服务配置中分配服务帐户。

### 特殊情况和高级主题

#### Kubernetes Engine (GKE)

使用 **[GKE 的工作负载身份联合](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity.md.txt)** 将 Kubernetes 身份映射到 IAM 主体标识符。这授予特定的 Kubernetes 工作负载访问特定的 Google Cloud API 的权限。[在此处了解更多信息。](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity.md.txt)

#### 外部工作负载（[工作负载身份联合](https://docs.cloud.google.com/iam/docs/workload-identity-federation.md.txt)）

对于运行在 **Google Cloud 外部** 的代码（例如 AWS、Azure 或本地），不要使用密钥。相反，使用工作负载身份联合来交换外部令牌（如 AWS IAM 角色）以获取短期 Google Cloud 访问令牌。

#### [API 密钥](https://docs.cloud.google.com/docs/authentication/api-keys.md.txt)

API 密钥是用于公共数据（例如 Google Maps）或简化访问（如 **[Vertex AI 快速入门模式](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview.md.txt)**）的加密字符串，后者允许在不复杂设置的情况下快速测试 Gemini 模型。人类和服务（例如基于 Cloud Run 的 AI 代理）都可以使用 API 密钥，只要服务支持它。

注意：API 密钥应被
[限制](https://docs.cloud.google.com/api-keys/docs/add-restrictions-api-keys.md.txt)
到特定的 API 和项目，以最大程度地降低安全风险。将 API 密钥存储在像 [密钥管理器](https://docs.cloud.google.com/secret-manager/docs.md.txt) 这样的密钥管理器中，以防止意外暴露。

#### OAuth 2.0 访问范围

虽然 IAM 是处理授权的现代方法，但传统的 Compute Engine VM 和 GKE 节点池仍然依赖于与 IAM 一起使用的 **访问范围**。如果 VM 的范围被限制，即使附加的服务帐户具有正确的 IAM 权限，它也无法进行 API 调用。如果附加的服务帐户意外失败，请首先检查此设置。

#### 短期凭据

模拟和安全的客户端到服务通信的底层机制是 **IAM 服务帐户凭据 API**。此 API 动态生成短期访问令牌、OpenID Connect (OIDC) ID 令牌或自签名 JSON Web 令牌 (JWT)，从而消除了对静态凭据的需求。

---

## 授权

认证后，Google Cloud 使用 **[身份和访问管理 (IAM)](https://docs.cloud.google.com/iam/docs/overview.md.txt)** 来确定经过认证的主体能做什么。

*   **允许策略**：一个绑定 **主体** 到 **资源** 上的 **角色** 的记录。
*   **[预定义角色](https://docs.cloud.google.com/iam/docs/roles-permissions)**：预构建的角色，如 `roles/storage.objectViewer` 或 `roles/bigquery.dataEditor`。**始终首先尝试使用这些角色。**
*   **[自定义角色](https://docs.cloud.google.com/iam/docs/creating-custom-roles.md.txt)**：如果预定义角色过于宽泛，则用户定义的特定权限集合。

---

## 示例

### 人类到服务（本地 Python 开发）

1.  **Authn**：运行 `gcloud auth application-default login` 以创建本地凭据 (ADC)。
2.  **Authz**：授予你的电子邮件 `roles/storage.objectViewer` 角色在存储桶上。
3.  **代码**：使用 Python `storage.Client()`。它自动通过 ADC 查找你的本地凭据。*注意：ADC 按特定顺序搜索——首先检查 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量，然后是本地 gcloud JSON 文件，最后是附加的服务帐户元数据服务器。*

### 服务到服务（Cloud Run 到 Cloud SQL）

1.  **Authn**：将自定义服务帐户附加到你的 Cloud Run 服务。
2.  **Authz**：授予该服务帐户在项目上的 `roles/cloudsql.client` 角色。
3.  **代码**：Cloud Run 环境自动向连接驱动程序提供令牌。

### 调用自定义应用程序（[OIDC](https://docs.cloud.google.com/docs/authentication/get-id-token.md.txt)）

当从另一个服务调用私有 Cloud Run 服务时，调用者生成一个 Google 签名的 **OpenID Connect (OIDC) ID 令牌** 并在 `Authorization: Bearer <TOKEN>` 标头中传递它。

---

## 验证检查清单

-   [ ] 用户是否在本地运行代码？建议 `gcloud auth application-default login` 或 **服务帐户模拟**。
-   [ ] 用户是否尝试在本地使用服务帐户密钥？强烈不建议这样做，并建议使用模拟。
-   [ ] 用户是否在生产环境中运行？建议附加一个自定义的、最小权限的服务帐户，而不是使用密钥。
-   [ ] 用户是否依赖于计算引擎默认服务帐户？建议创建一个自定义服务帐户。
-   [ ] 用户是否在另一个云上运行？建议使用工作负载身份联合。
-   [ ] 用户是否调用自定义应用程序？建议使用 OIDC ID 令牌。
-   [ ] 用户是否限制他们的 API 密钥？检查适当的 [API 密钥限制](https://docs.cloud.google.com/docs/authentication/api-keys.md.txt)。

## 参考

-   [认证概述](https://docs.cloud.google.com/docs/authentication.md.txt)
-   [用户身份](https://docs.cloud.google.com/iam/docs/user-identities.md.txt)
-   [应用默认凭据](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc.md.txt)
-   [服务帐户最佳实践](https://docs.cloud.google.com/iam/docs/best-practices-service-accounts.md.txt)
