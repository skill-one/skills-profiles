# Google Ads API 快速入门
本指南将引导您从零开始，成功运行第一个请求以检索广告系列。

## 支持的路径
您可以选择使用以下方式使用本指南：

1.  **官方客户端库：** Python、Java、.NET、PHP、Ruby 或 Perl。
2.  **直接 REST：** 原始 HTTP REST 请求。

---

## 关键要求：动态版本解析与运行时解析

> [!IMPORTANT]
> 为确保集成安全、稳定且最新，您必须动态解析所有 API 和运行时版本。不要依赖硬编码的默认值。

### 严格约束：

*   **禁止硬编码：** 绝对不要在生成的代码或环境设置说明中使用硬编码的 Google Ads API 版本（例如，`v24`）或语言运行时版本（例如，`Python 3.8+`、`Java 11+`），除非用户明确请求特定版本。
*   **强制动态解析：** 您必须在生成任何代码或配置之前，使用下方详细说明的步骤，在执行开始时动态解析最新稳定版本。

### A. 动态 API 版本解析
为确保集成安全、稳定且最新，您 **必须** 动态解析 Google Ads API 的最新稳定主要版本。

#### 执行步骤：

1.  **预飞行版本解析：** 使用您的网络搜索或 URL 读取工具，检查 [Google Ads API 发布说明](https://developers.google.com/google-ads/api/docs/release-notes.md.txt) 中的最新条目，或 [Googleapis Github 仓库](https://github.com/googleapis/googleapis/tree/master/google/ads/googleads) 中版本最高的目录，以解析 `RESOLVED_API_VERSION`（例如，`v24`）。如果使用 Java，您 **必须** 还要解析 Google Ads Java 客户端库的最新稳定版本（称为 `RESOLVED_LIBRARY_VERSION`，例如，`34.0.0`）。

2.  **强制响应锚点：** 您 **必须** 将以下确认块作为对用户的 **第一行** 响应输出。在输出此块之前，不要输出任何问候语、客套话或介绍性文本。
    
    ```text
    [SYSTEM: 使用 Google Ads API 版本：RESOLVED_API_VERSION (从发布说明解析)]
    ```

3.  **严格占位符映射表：** 您 **必须** 使用下表对所有代码模板和参考文件进行动态搜索和替换。不要在最终输出中留下原始占位符。

    | 目标语言 / 技术 | 模板中的占位符 | 替换模式 | 示例（假设 API `v24`） |
    | :--- | :--- | :--- | :--- |
    | **Java**（Maven/Gradle） | `LATEST_LIBRARY_VERSION` | 搜索并替换库的最新 Maven 发布版本。 | `34.0.0` |
    | **Java**（导入） | `vXX` | 替换为 **小写** API 版本。 | `com.google.ads.googleads.v24` |
    | **.NET / C#**（命名空间） | `VXX` | 替换为 **首字母大写** API 版本。 | `Google.Ads.GoogleAds.V24` |
    | **PHP**（命名空间） | `VXX` | 替换为 **首字母大写** API 版本。 | `Google\Ads\GoogleAds\V24` |
    | **REST**（端点 URL） | `vXX` | 替换为 **小写** API 版本。 | `https://googleads.googleapis.com/v24/...` |

> [!TIP]
> **离线回退：** 如果 URL 不可达或抓取失败，不要停止执行。回退到以下已知稳定版本：
> *   **Google Ads API 主要版本 (`RESOLVED_API_VERSION`)：** `v24`
> *   **Java 客户端库版本 (`RESOLVED_LIBRARY_VERSION`)：** `34.0.0`

### B. 动态语言运行时版本解析
为防止生成的设置指南因语言淘汰周期而过时，您 **必须** 动态解析语言要求。

#### 执行步骤：

1.  **获取实时要求：** 使用您的 URL 读取工具，检查官方 [Google Ads 客户端库 - 支持的版本](https://developers.google.com/google-ads/api/docs/client-libs.md.txt#supported_api_versions) 页面。

2.  **提取最低要求：** 通过扫描概述页面或兼容性表格（例如，查找明确要求，如 Python 3.8+、Java 11+、.NET 6.0+、PHP 8.1+、Ruby 3.0+）来识别用户选择的语言的最低支持运行时版本。

3.  **动态应用：** 将运行时占位符（例如，`<PYTHON_MIN_VERSION>`）中的所有占位符替换为这些解析版本。

> [!TIP]
> **离线回退：** 如果 URL 不可达或抓取失败，不要停止执行。回退到以下已知安全最低版本：
> *   **Python：** `3.9+`
> *   **Java：** `11+`
> *   **.NET：** `6.0+`
> *   **PHP：** `8.1+`
> *   **Ruby：** `3.0+`
> *   **Perl：** `5.28.1+`

---

## 第 1 步：获取 Google Ads API 凭证

在安装库或进行 API 调用之前，您必须获取五个必需的认证参数。

### 1. 开发者令牌

*   **目的：** 识别您的开发者访问权限和 API 配额。
*   **如何获取：**
    1. 直接导航到您的 Google Ads 管理员账户中的 **API 中心**：https://ads.google.com/aw/apicenter *(注意：您必须使用管理员账户登录，而不是标准投放账户)*。
    2. 复制您的开发者令牌。

> [!WARNING]
> **待定令牌限制：** 如果您的开发者令牌状态为“待定”（未批准），您 **必须仅** 针对 **Google Ads 测试账户**。使用待定令牌调用生产账户将失败，并显示错误：`DEVELOPER_TOKEN_NOT_APPROVED`。

### 2. OAuth2 客户端 ID 和客户端密钥

*   **目的：** 识别您的应用程序给 Google 的 OAuth 2.0 服务器，并允许您请求用户授权。
*   **如何获取：**
    1. 打开 [Google Cloud Console](https://console.cloud.google.com/)。
    2. 创建一个新项目（或选择一个现有项目）。
    3. 在 API 库中搜索 **Google Ads API** 并点击 **启用**。
    4. 配置 **OAuth 同意屏幕**：
       *   选择 **外部** 用户类型。
       *   将发布状态设置为 **测试**。
       *   > [!IMPORTANT]
       *   > **添加测试用户：** 您 **必须** 在此步骤中将您用于登录 Google Ads 的 Google 账户的电子邮件地址添加为 **测试用户**。否则，您将在授权过程中被阻止。
    5. 创建 OAuth 客户端：
       *   转到 **APIs & Services 🡒 凭证**。
       *   点击 **创建凭证 🡒 OAuth 客户端 ID**。
       *   选择 **桌面应用程序** 作为应用程序类型。
       *   命名客户端并点击 **创建**。
    6. **下载密钥：** 点击新创建的客户端 ID 旁边的下载图标（JSON），将其保存到本地为 `client_secrets.json`。

### 3. OAuth2 刷新令牌

*   **目的：** 允许您的应用程序自动获取新的访问令牌，而无需每小时手动用户登录。
*   **如何获取：**
    您必须运行 Google Cloud (`gcloud`) CLI 来生成您的刷新令牌。

    #### 1. 安装和验证 gcloud CLI：
    确保 [gcloud CLI](https://cloud.google.com/sdk/docs/install) 已安装并可可在您的终端中。

    #### 2. 执行登录流程：
    在终端中运行以下命令，传入在上一步骤中下载的 `client_secrets.json` 文件的路径：
    
    ```bash
    gcloud auth application-default login \
      --scopes=https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform \
      --client-id-file=client_secrets.json
    ```

    #### 3. 浏览器授权：
    1. 命令将在您的浏览器中打开一个 Google 账户登录窗口。
    2. 使用在 OAuth 同意屏幕设置中注册的 **测试用户** 电子邮件地址登录。
    3. 如果您的应用程序未经验证，点击 **高级** 并继续到项目。点击 **继续** 授权权限。

    #### 4. 获取您的刷新令牌：
    成功后，`gcloud` 将输出一条消息，指示凭据保存的位置（通常为 `~/.config/gcloud/application_default_credentials.json`）。打开该文件以复制您的 `refresh_token`。

### 4. 客户端客户 ID

*   **目的：** 您要查询或更改的特定 Google Ads 账户的 10 位 ID。
*   **格式：** 必须为 10 位数字，**不带连字符**（例如，`1234567890`，不是 `123-456-7890`）。
*   **如何找到它：** 登录 Google Ads UI；ID 显示在右上角您的用户图标旁边。

> [!IMPORTANT]
> **测试账户要求：** 如果您的开发者令牌待定（未批准），这 **必须** 是 **测试账户** 的客户 ID。测试账户在 UI 的右上角有一个红色的“测试账户”横幅。

---

### 5. 登录客户 ID

*   **是什么：** 拥有或管理目标客户账户的 Google Ads 管理员账户的 10 位客户 ID。
*   **格式：** 必须为 10 位数字，**不带连字符**（例如，`9876543210`）。
*   **何时使用：** 如果您的 OAuth 凭证（和开发者令牌）属于管理员账户，但您正在查询子账户（客户账户），则此参数是 **强制** 的。

> [!CAUTION]
> **防止 `USER_PERMISSION_DENIED`：**
> 如果您通过管理员账户层次结构访问客户账户，您 **必须** 设置此参数。
> *   `login_customer_id` = **管理员** 账户 ID。
> *   `client_customer_id` = **子/客户** 账户 ID。
> 在管理员-客户层次结构中遗漏 `login_customer_id` 是导致权限错误的 #1 原因。

---

## 第 2 步：选择您的集成策略

开发者可以使用官方高级客户端库或直接 HTTPS REST 请求连接到 Google Ads API。

### 路径 A：官方客户端库（推荐）

> [!IMPORTANT]
> **强制代理指令：** 一旦用户选择他们的语言，您 **必须**：
> 1. 使用 `view_file` 工具按需加载下方列出的相应参考文件。
> 2. 在生成代码之前，应用 **动态版本解析**（第 B 部分）来动态替换所有 `vXX`/`VXX` 占位符和库版本。

#### Python
如果您需要为 Python 设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API Python 设置参考](references/python.md)
*(包：`google-ads`)*

#### Java
如果您需要为 Java 设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API Java 设置参考](references/java.md)
*(组件：`com.google.api-ads:google-ads`)*

#### .NET / C#
如果您需要为 .NET/C# 设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API .NET 设置参考](references/dotnet.md)
*(包：`Google.Ads.GoogleAds`)*

#### PHP
如果您需要为 PHP 设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API PHP 设置参考](references/php.md)
*(包：`googleads/google-ads-php`)*

#### Ruby
如果您需要为 Ruby 设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API Ruby 设置参考](references/ruby.md)
*(宝石：`google-ads-ruby`)*

#### Perl
如果您需要为 Perl 设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API Perl 设置参考](references/perl.md)
*(包：`Google::Ads::GoogleAds::Client`)*

### 路径 B：直接 HTTP REST（无库开销）

如果用户的環境不支持官方客户端库（例如，轻量级无服务器函数、自定义语言堆栈或受限运行时），请使用此路径。

> [!IMPORTANT]
> **强制代理指令：** 如果用户选择 REST 路径，您 **必须**：
> 1. 使用 `view_file` 工具按需加载下方的 REST 参考文件。
> 2. 应用 **动态版本解析**（第 B 部分）来替换端点 URL 中的所有 `vXX` 占位符（例如，将 `vXX` 解析为 `v24` 在 `https://googleads.googleapis.com/v24/...`）。

#### REST（HTTP）
如果您需要为 REST（HTTP）设置 Google Ads API 环境，不要猜测配置。
相反，请阅读详细的设置指南：

*   [Google Ads API REST 设置参考](references/rest.md)
*(协议：原始 HTTP POST JSON)*

---

## 交叉引用：AI 助手与 MCP 连接

> [!TIP]
> **AI 助手 / MCP 集成交接：**
> 如果目标是连接 **AI 助手**（例如 Gemini、Cursor 或 Claude Code）通过自然语言查询 Google Ads：
> 1. **不要** 编写自定义脚本或客户端库代码。
> 2. **停止** 执行此技能。
> 3. **立即过渡** 到 **`google-ads-api-mcp-setup`** 技能以安装和配置官方 Google Ads 模型上下文协议 (MCP) 服务器。

---

## 第 4 步：排查常见错误

> [!IMPORTANT]
> **静态诊断约束：** 在排查时，您 **必须** 不执行 bash 命令、运行本地测试脚本或尝试在工作区中重现错误。完全依赖静态代码分析、配置审查和下方的诊断指南，以防止无限、失败的执行循环。

### 1. 错误：`USER_PERMISSION_DENIED`

*   **症状：** 在执行 API 请求时（例如，检索广告系列），您收到 `USER_PERMISSION_DENIED` 错误。
*   **可能原因：** 认证 OAuth2 用户通过 **管理员账户** 间接访问目标客户账户，但请求标头中缺少管理员账户的 ID。

#### 必需的代理响应检查清单：
在帮助用户解决此错误时，您的响应 **必须** 包括：

1.  [ ] **解释层次结构：** 解释认证用户可能属于一个位于目标客户账户之上的管理员账户。
2.  [ ] **提供修复方法：** 指示用户在他们的配置文件中将他们的 10 位管理员账户 ID 作为 `login_customer_id` 添加。
3.  [ ] **解释路由逻辑：** 解释 `login_customer_id` 告诉 API 通过管理员账户验证对子账户的访问权限。
4.  [ ] **提供配置模板：** 显示以下精确的 YAML 配置块。

> [!CAUTION]
> **安全防护栏：** 在任何情况下，都不要建议暴露原始密码、创建新的未批准的开发者令牌或放宽 OAuth 范围超出标准的 `adwords` 范围以绕过此错误。

#### 配置修复示例 (`google-ads.yaml`)：

```yaml
developer_token: INSERT_DEVELOPER_TOKEN_HERE
client_id: INSERT_OAUTH2_CLIENT_ID_HERE
client_secret: INSERT_OAUTH2_CLIENT_SECRET_HERE
refresh_token: INSERT_OAUTH2_REFRESH_TOKEN_HERE

# 在管理员-客户层次结构中，您必须在此处设置此参数以防止 `USER_PERMISSION_DENIED`：
login_customer_id: INSERT_LOGIN_CUSTOMER_ID_HERE
```

### 2. 错误：`DEVELOPER_TOKEN_NOT_APPROVED`

*   **症状：** 脚本失败并显示 `DEVELOPER_TOKEN_NOT_APPROVED` 错误消息。
*   **可能原因：** 您的开发者令牌目前处于“待定”（未批准）状态，并且您正在尝试针对实时生产 Google Ads 账户。

#### 必需的代理响应检查清单：
在帮助用户解决此错误时，您的响应 **必须** 包括：

1.  [ ] **解释“待定”限制：** 解释未批准（待定）的开发者令牌完全可用，但**仅限于 Google Ads 测试账户**。
2.  [ ] **定义生产访问级别：** 您 **必须** 明确列出所有三个访问级别名称：说明针对实时生产账户需要 Google Ads API 合规团队批准的 **探索者访问**、**基本访问** 或 **标准访问**。不要压缩或释义为“至少基本访问”。
3.  [ ] **提供沙盒设置步骤：** 指导用户如何设置沙盒环境：
    *   创建一个 **测试管理员账户**（不需要批准的令牌）。
    *   在该测试管理员下创建 **测试客户账户**。
    *   在他们的配置中使用测试客户客户 ID。
4.  [ ] **提供指南链接：** 指引用户到官方 [Google Ads API 测试账户指南](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts.md.txt)。

> [!CAUTION]
> **安全与完整性防护栏：** 您 **必须** 不建议开发者修改客户端库源代码、绕过令牌验证检查或使用第三方“破解”包装器来绕过此错误。此限制由 Google 服务器端强制执行，客户端修改将无效。
