# Google Cloud 入门指南

本技能为单例开发者提供了一个简化的、非交互式的“顺利路径”，以开始使用 [Google Cloud](https://cloud.google.com/)。它涵盖了从环境验证和身份验证到项目选择、计费账户关联以及下游安全链的所有内容。

> [!IMPORTANT]
> 对于执行此技能的自主代理：
> 1. **变更前检查审计**：在提议或执行任何项目或计费更改之前，始终执行静默的预执行状态审计。
> 2. **单问题策略**：在交互式执行期间，一次只向用户询问一个操作参数或确认。
> 3. **非交互式输出**：将非交互式覆盖参数（`--quiet`，`--format="json"`）附加到所有变更命令中，以确保确定性、机器可解析的输出并防止终端挂起。
> 4. **首次交互规则（触发轮次）**：当开发者首次使用通用入门请求触发此技能时（例如，说“我想开始使用 Google Cloud”）：
>    - **引导性前缀**：主动提供一段简短的引导性前缀，指导开发者创建 Google Cloud 账户（指向控制台 `https://console.cloud.google.com/`）并运行 `gcloud auth login` 授权他们的工作站，即使他们看起来已经登录。
>    - **首次交互单问题**：执行静默的预飞行审计，但不要在首次交互中呈现完整的参数摘要表或请求最终同意。相反，向开发者提出一个初始操作问题（例如，*“您想重用现有的活动项目，还是创建一个全新的项目？”*）。
> *注意：如果开发者的初始提示明确说明“我批准入门配置”、“让我们开始入门”或请求干跑计划（例如，“显示确切的计划或干跑命令”），则跳过通用前缀和初始问题，直接进行请求的步骤。*

---

## 概述

对于个人开发者，入门 Google Cloud 涉及验证本地终端工具、建立认证会话、选择或实例化工作区（[项目](https://docs.cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy.md.txt)），并将其链接到活动计费账户。Google Cloud 提供了免费层级和首次用户 300 美元的免费试用。[了解更多](https://docs.cloud.google.com/free/docs/free-cloud-features)。

---

## 前置条件

- 一个个人 Google 账户（例如，`@gmail.com`）或 Google Workspace / Cloud Identity 账户。
- 一个有效的支付方式（信用卡或银行账户），用于身份验证并激活概述中提到的 300 美元的免费试用信用。

---

## 步骤

### 第 1 部分：验证主机工具设置

在请求输入或提议变更之前，静默审计主机系统的活动工具和环境状态。

1. 检查 `gcloud` CLI 二进制文件是否已安装并可访问：
   
   ```bash
   which gcloud
   ```
2. 检查是否存在活动认证身份会话：
   
   ```bash
   gcloud auth list --format="json"
   ```
3. 如果 `which gcloud` 的预执行审计返回有效路径，则直接进入第 2 部分：认证和路由会话。
4. 如果二进制文件缺失，则停止执行，并指导代理使用 [gcloud 技能](https://github.com/google/skills/tree/main/skills/cloud/gcloud) 安装 gcloud。向开发者提供官方 [Google Cloud CLI 安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk) 以设置身份验证。

---

### 第 2 部分：认证和路由会话

使用开发者的 Google 账户授权 gcloud CLI 访问 Google Cloud，并验证该账户是否适用于独立开发者入门。

1. **执行凭证认证**：
   
   ```bash
   gcloud auth login
   ```
   > [!IMPORTANT]
   > **新用户/未认证指导**：
   > 如果预执行状态审计或命令失败确认开发者未认证（例如，`gcloud auth list` 为空或缺少活动凭证）：
   > 1. 指导他们通过导航到 [Google Cloud 控制台](https://console.cloud.google.com/) 创建 Google Cloud 账户。
   > 2. 指示他们执行 `gcloud auth login` 命令以授权他们的本地工作站终端会话。
   > 3. 在身份验证成功完成之前，不要尝试项目创建或资源配置。

2. **验证活动身份**：
   
   ```bash
   gcloud config get-value account --format="json"
   ```

3. **程序化企业路由防护栏**：
   在继续之前，验证账户是否绑定到企业组织，因为企业设置必须遵循不同的架构：
   
   ```bash
   gcloud organizations list --format="json"
   ```
   - 注意，新的免费试用账户会自动获得一个 Self-Owned Organization (SOO)。为了区分个人免费试用账户和企业组织，检查 JSON 输出：
     - **企业组织（停止执行）**：如果输出列表包含一个组织节点，其中 `owner.directoryCustomerId` 存在（确认域验证的 Google Workspace 或 Cloud Identity 组织），或者用户提示中明确提到企业着陆区或多租户项目结构：
       - **立即停止执行此技能**。
       - 将开发者路由到官方 [Google Cloud 设置引导流程](https://docs.cloud.google.com/docs/enterprise/cloud-setup)。
     - **个人账户/免费试用 SOO（继续）**：如果输出列表为空 `[]`，或者它包含一个 Self-Owned Organization（其中 `owner.directoryCustomerId` 缺失且 `displayName` 不是已验证的域名），则继续进入第 3 部分：选择或实例化您的 Google Cloud 项目。

---

### 第 3 部分：选择或实例化您的 Google Cloud 项目

Google Cloud 资源按 **项目** 组织。当开发者在控制台注册免费试用时，Google Cloud 会自动创建一个默认项目（例如，“我的第一个项目”）。始终先审计活动环境，以重用现有项目并防止令牌消耗冲突错误。

1. **静默项目发现**：
   列出活动、可访问的项目（限制数量以防止上下文窗口溢出）：
   
   ```bash
   gcloud projects list --filter="lifecycleState=ACTIVE" --limit=20 --format="json"
   ```
2. **重用现有项目（推荐）**：
   如果列表返回一个活动项目，向开发者展示并提议将其设置为默认工作项目：
   
   ```bash
   gcloud config set project {PROJECT_ID} --quiet
   ```
3. **创建自定义项目**：
   如果没有项目存在，或者开发者明确请求一个全新的工作区：
   - 向开发者索要自定义的 `PROJECT_ID` 和 `PROJECT_NAME`（单问题策略）。
   - **结构化确认和同意门（强制）**：
     在运行任何项目创建或计费链接命令之前，代理 **必须** 呈现一个结构化的 markdown 表格，总结目标参数：
     | 参数 | 值 |
     | :--- | :--- |
     | 目标项目 ID | `{PROJECT_ID}` |
     | 目标项目名称 | `{PROJECT_NAME}` |
     | 活动身份账户 | `{ACCOUNT}` |
     | 目标计费账户 ID | `{BILLING_ACCOUNT_ID}` |

     向用户提出确切的同意查询：
     `"我准备好初始化您的 Google Cloud 项目并链接计费。您想让我继续吗？"`

     **关键**：代理 **必须** 不在此轮执行任何 `gcloud projects create` 或计费链接命令。您必须显示此表格，询问确切的同意查询，并 **严格停止** 等待用户的积极确认。
    - **项目 ID 冲突后缀恢复**：如果项目创建命令失败，因为 `PROJECT_ID` 在全局上已被占用（返回 `PROJECT_ID_COLLISION` 或 `ALREADY_EXISTS` 错误）：
      - 自动附加一个随机 4 位数后缀（例如，将 `my-project` 改为 `my-project-8472`）。
      - 向开发者提议此新的可用项目 ID，并在重试之前重新索要同意。
   - **执行项目创建**：一旦确认用户同意：
     
     ```bash
     gcloud projects create {PROJECT_ID} --name="{PROJECT_NAME}" --quiet --format="json"
     ```
   - 设置活动工作项目：
     
     ```bash
     gcloud config set project {PROJECT_ID} --quiet
     ```

---

### 第 4 部分：验证和链接计费

要在 Google Cloud 上部署资源，您的项目必须链接到活动 Cloud 计费账户。

1. **审计计费状态**：
   检查活动项目是否已链接到计费账户：
   
   ```bash
   gcloud billing projects describe {PROJECT_ID} --format="json"
   ```
2. 如果输出包含 `"billingEnabled": true`，则跳过链接并立即进入第 5 部分：技能链（支出控制和工作负载）。
3. **发现可用计费账户**：
   如果项目未链接，查询与认证用户身份链接的可用计费账户句柄：
   
   ```bash
   gcloud billing accounts list --format="json"
   ```
4. **链接计费账户**：
   提议将项目链接到发现的计费账户 ID，并执行：
   
   ```bash
   gcloud billing projects link {PROJECT_ID} --billing-account={BILLING_ACCOUNT_ID} --format="json"
   ```

---

### 第 5 部分：技能链（支出控制和工作负载）

入门设置现已完成。为了保护您的环境并部署工作负载，您可以链接到下游的专用技能：

1. **计费支出控制**：
   为了避免意外成本超支，请考虑设置一个程序化控制来自动禁用计费。当计费被禁用时，项目中所有 Google Cloud 服务和使用都会终止以停止进一步成本：
- 指导开发者到官方 [使用通知禁用计费指南](https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications)，该指南提供了有关如何在成本超过项目预算时自动关闭计费的分步说明。
2.  **部署工作负载**：要部署第一个资源，触发与目标应用程序匹配的下游专用技能（例如，
    [cloud-run-basics](https://github.com/google/skills/blob/main/skills/cloud/cloud-run-basics)
    或 `bigquery-basics`）。如果专用技能在本地不可用，
    指导开发者到相应的官方快速入门，例如
    [Cloud Run 容器部署快速入门](https://docs.cloud.google.com/run/docs/quickstarts/deploy-container)。
    *注意：这些下游专用技能各自负责在执行期间动态启用其所需的服务 API（例如，
    run.googleapis.com）。*

---

## 验证逻辑

完成入门步骤后，使用以下诊断命令程序化验证完成的環境状态：

1. **验证 CLI 安装**：
   
   ```bash
   which gcloud
   ```
2. **验证认证身份**：
   
   ```bash
   gcloud config get-value account
   ```
3. **验证项目工作区存在**：
   
   ```bash
   gcloud projects describe {PROJECT_ID} --format="json"
   ```
4. **验证计费链接**（确保 JSON 输出包含 `"billingEnabled": true`）：
   
   ```bash
   gcloud billing projects describe {PROJECT_ID} --format="json"
   ```

---

## 其他资源

- [Google Cloud 入门着陆页](https://docs.cloud.google.com/docs/get-started.md.txt)
- [Google Cloud 概述](https://docs.cloud.google.com/docs/overview.md.txt)
- [Google Cloud 免费计划](https://docs.cloud.google.com/free/docs/free-cloud-features)
- [Google Cloud 设置概述](https://docs.cloud.google.com/docs/enterprise/cloud-setup.md.txt)
- [Google Cloud 设置高级生产基础](https://docs.cloud.google.com/docs/enterprise/advanced-production.md.txt)
