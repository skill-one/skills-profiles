# 使用 Google Analytics Admin API 入门

Google Analytics Admin API 提供了对 Google Analytics 账户和属性配置的程序化访问。它允许您自动化账户管理、管理数据流、配置自定义维度以及处理产品集成。

## 通过 Cloud CLI 启用 API

在调用 API 之前，请确保您的 Google Cloud 项目中已启用 Google Analytics Admin API。

如果找不到 `gcloud`，请在运行这些命令之前提示用户安装 Google Cloud CLI。

1.  **启用 API：** 使用 Cloud CLI (`gcloud`) 启用 `analyticsadmin.googleapis.com`。

    ```bash
    gcloud services enable analyticsadmin.googleapis.com --quiet
    ```

    *原因：启用 API 可确保您的 Cloud 项目已分配必要的配额和权限来管理 Google Analytics 配置。*

2.  **验证 API 启用情况：**

    ```bash
    gcloud services list --enabled --filter="analyticsadmin.googleapis.com"
    ```

## 身份验证

要验证您的 API 请求，您必须生成应用默认凭证 (ADC) 并授予您的账户必要的范围。在您的终端中运行以下命令：

```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/analytics.readonly"
```

*原因：此配置在您的本地环境中配置了所需的 Cloud Platform 和 Google Analytics 只读范围，允许客户端库自动验证您的请求。*

> [!NOTE] **配置更改**：更改 Google Analytics 账户/属性配置的方法需要 `https://www.googleapis.com/auth/analytics.edit` 范围。

## Admin API 使用案例

您可以使用 Google Analytics Admin API 来：

*   运行数据访问报告（有关更多信息，请参阅 https://developers.google.com/analytics/devguides/config/admin/v1/access-api.md.txt）
*   创建账户摘要
*   管理账户
*   配置新账户
*   搜索账户更改历史事件
*   管理和创建属性
*   管理属性数据保留设置
*   管理转化事件
*   管理自定义维度和指标
*   管理数据流并配置测量协议密钥
*   管理Firebase链接
*   管理Google Ads链接
*   管理关键事件

### 仅限 v1alpha 的使用案例

以下功能目前仅在 Admin API 的 `v1alpha` 版本中可用：

*   管理账户和属性访问绑定
*   创建和管理汇总属性
*   创建和管理子属性
*   确认用户数据收集
*   更改属性归因、数据保留、Google 信号、报告身份和用户提供数据设置
*   管理AdSense链接
*   管理BigQuery链接
*   管理受众
*   管理渠道组
*   管理计算指标
*   管理DisplayVideo360Advertiser链接
*   管理扩展数据集
*   管理报告数据注释
*   管理SearchAds360链接
*   管理数据流的事件创建规则
*   管理iOS流SKAdNetwork转化值架构
*   为 Google Analytics 属性提交用户删除请求。

## 调用 Admin API

要与 Admin API 交互，请使用官方的 Google Analytics Admin 客户端库。请注意，`v1beta` 是 Admin API 最稳定的版本。对于最新功能，请考虑使用 `v1alpha`。

> [!IMPORTANT] **强制代理指令**：当用户选择或需要特定编程语言时，请阅读以下 `references/` 列表中相应的客户端库设置参考指南。

### 支持的客户端库

#### Python

如果您需要安装或设置 Python 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [Python 安装参考](references/python.md) *(包：`google-analytics-admin`)*

#### Java

如果您需要安装或设置 Java 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [Java 安装参考](references/java.md) *(工件：`com.google.cloud:google-cloud-analytics-admin`)*

#### PHP

如果您需要安装或设置 PHP 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [PHP 安装参考](references/php.md) *(包：`google/analytics-admin`)*

#### Node.js

如果您需要安装或设置 Node.js 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [Node.js 安装参考](references/nodejs.md) *(包：`@google-analytics/admin`)*

#### Go

如果您需要安装或设置 Go 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [Go 安装参考](references/go.md) *(包：`cloud.google.com/go/analytics/admin/apiv1beta`)*

#### .NET

如果您需要安装或设置 .NET / C# 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [.NET 安装参考](references/dotnet.md) *(包：`Google.Analytics.Admin.V1Beta`)*

#### Ruby

如果您需要安装或设置 Ruby 的 Google Analytics Admin API 客户端库，请阅读设置指南：

*   [Ruby 安装参考](references/ruby.md) *(宝石：`google-analytics-admin-v1alpha`)*

> [!NOTE] **其他资源**：有关使用 Java、PHP、Node.js、.NET、Python 和 REST 调用 Admin API 的更多示例，以及使用服务账户进行身份验证的提示，请参阅官方的 [Admin API 快速入门](https://developers.google.com/analytics/devguides/config/admin/v1/quickstart)。有关 `v1alpha` 和 `v1beta` 的完整 API 参考文档，请参阅 [Admin API 参考](https://developers.google.com/analytics/devguides/config/admin/v1/rest)。

### Python 快速入门

1.  **安装客户端库：**

    ```bash
    pip install google-analytics-admin
    ```

    如果找不到 `pip`，请提示用户在安装客户端库之前安装 `pip`。

2.  **列出账户和属性：** 以下是一个完整的示例，演示了如何使用 `list_account_summaries()` 调用 Admin API 列出当前用户所有可用的账户及其子属性。

    ```python
    from google.analytics.admin import AnalyticsAdminServiceClient

    def sample_list_account_summaries():
        # 初始化客户端。
        # 假设您的环境中已配置了应用默认凭证 (ADC)。
        client = AnalyticsAdminServiceClient()

        # list_account_summaries 返回用户可访问的所有账户及其子属性的摘要。
        account_summaries = client.list_account_summaries()

        print("可用的 Google Analytics 账户和属性：")
        for summary in account_summaries:
            print(f"账户：{summary.display_name} ({summary.account})")
            for property_summary in summary.property_summaries:
                print(f"  属性：{property_summary.display_name} ({property_summary.property})")

    if __name__ == "__main__":
        sample_list_account_summaries()
    ```
