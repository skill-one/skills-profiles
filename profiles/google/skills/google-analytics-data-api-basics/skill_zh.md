# 使用 Google Analytics 数据 API 入门

Google Analytics 数据 API v1beta 提供了对 Google Analytics 报告数据的程序化访问。它允许您构建自定义仪表板、自动化报告工作流以及将 Google Analytics 数据集成到您的企业应用程序中。

## 通过 Cloud CLI 启用 API

在调用 API 之前，请确保在您的 Google Cloud 项目中启用了 Google Analytics 数据 API。

如果找不到 `gcloud`，请在运行这些命令之前提示用户安装 Google Cloud CLI。

1.  **启用 API：** 使用 Cloud CLI (`gcloud`) 启用 `analyticsdata.googleapis.com`。

    ```bash
    gcloud services enable analyticsdata.googleapis.com --quiet
    ```

    *原因：启用 API 可确保您的 Cloud 项目为运行 Google Analytics 报告分配了必要的配额和权限。*

2.  **验证 API 启用情况：**

    ```bash
    gcloud services list --enabled --filter="analyticsdata.googleapis.com"
    ```

## 身份验证

为了对 API 请求进行身份验证，您必须生成应用默认凭证 (ADC)，并授予您的帐户必要的范围。在您的终端中运行以下命令：

```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/analytics.readonly"
```

*原因：此操作配置了您本地环境中的 ADC，并包含了所需的 Cloud Platform 和 Google Analytics 只读范围，允许客户端库自动对您的请求进行身份验证。*

## 创建数据 API 报告 (v1beta)

要创建报告，请使用官方的 Google Analytics 数据客户端库。始终优先选择 API 的 `v1beta` 版本，以获得稳定性和对当前 Google Analytics 报告功能的访问。

> [!IMPORTANT] **强制代理指令：** 当用户选择或需要特定编程语言时，请阅读下面列出的 `references/` 中的相应客户端库设置参考指南。

### 支持的客户端库

#### Python

如果您需要安装或设置 Python 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [Python 安装参考](references/python.md) *(包：`google-analytics-data`)*

#### Java

如果您需要安装或设置 Java 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [Java 安装参考](references/java.md) *(工件：`com.google.cloud:google-cloud-analytics-data`)*

#### PHP

如果您需要安装或设置 PHP 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [PHP 安装参考](references/php.md) *(包：`google/analytics-data`)*

#### Node.js

如果您需要安装或设置 Node.js 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [Node.js 安装参考](references/nodejs.md) *(包：`@google-analytics/data`)*

#### Go

如果您需要安装或设置 Go 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [Go 安装参考](references/go.md) *(包：`cloud.google.com/go/analytics/data/apiv1beta`)*

#### .NET

如果您需要安装或设置 .NET / C# 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [.NET 安装参考](references/dotnet.md) *(包：`Google.Analytics.Data.V1Beta`)*

#### Ruby

如果您需要安装或设置 Ruby 的 Google Analytics 数据 API 客户端库，请阅读设置指南：

*   [Ruby 安装参考](references/ruby.md) *(宝石：`google-analytics-data-v1beta`)*

> [!NOTE] **其他资源**：有关使用 Java、PHP、Node.js、.NET、Python 和 REST 调用数据 API 的更多示例，以及有关使用服务帐户进行身份验证的提示，请参阅官方的
> [数据 API 快速入门](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart)。

### Python 快速入门

1.  **安装客户端库：**

    ```bash
    pip install google-analytics-data
    ```

    如果 `pip` 不可用，请在安装客户端库之前提示用户安装 `pip`。

2.  **运行报告请求：** 以下是一个完整的示例，演示了如何查询 Google Analytics 属性中的活跃用户和会话，按城市和日期分组。将 `YOUR-PROPERTY-ID` 替换为您的实际 Google Analytics 属性 ID（例如，`1234567`）。

    ```python
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    def sample_run_report(property_id: str):
        # 初始化客户端。
        # 假设您的环境中已配置了应用默认凭证 (ADC)。
        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="city"),
                Dimension(name="date")
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions")
            ],
            date_ranges=[
                DateRange(start_date="2026-05-01", end_date="today")
            ],
        )

        response = client.run_report(request)

        print(f"属性 {property_id} 的报告结果：")
        for row in response.rows:
            print(
                f"城市：{row.dimension_values[0].value}, "
                f"日期：{row.dimension_values[1].value}, "
                f"活跃用户：{row.metric_values[0].value}, "
                f"会话：{row.metric_values[1].value}"
            )

    if __name__ == "__main__":
        sample_run_report("YOUR-PROPERTY-ID")
    ```

    *原因：使用 `BetaAnalyticsDataClient` 和 `RunReportRequest` 可确保与 v1beta 端点兼容，并启用强类型请求验证。*

## 指标和维度架构

在构建 `RunReportRequest` 时，您必须使用有效的 API 名称作为维度和指标。有关可用字段的完整、权威列表，请参阅官方的
[数据 API 架构文档](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)。

### 常用的维度

维度表示数据的分类属性。

*   `city`：用户的城镇或城市。
*   `country`：用户的国家。
*   `date`：事件日期，格式为 YYYYMMDD。
*   `deviceCategory`：移动设备的类别（例如，桌面、移动、平板）。
*   `eventName`：触发的事件名称。
*   `pageTitle`：网页标题。

### 常用的指标

指标表示定量度量。

*   `activeUsers`：活跃用户数。
*   `eventCount`：事件总数。
*   `sessions`：会话总数。
*   `screenPageViews`：查看的应用屏幕或网页数量。
*   `totalRevenue`：来自购买、订阅和广告的总收入。

### 指标和维度兼容性检查

某些维度和指标不能在同一个报告请求中一起查询。如果您遇到关于不兼容字段的 `INVALID_ARGUMENT` 错误，请验证您的字段组合。要程序化访问数据 API 架构，请使用 `getMetadata()`。要在运行报告之前程序化检查特定维度和指标组合的兼容性，请使用 `checkCompatibility()` 方法。

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import CheckCompatibilityRequest, Compatibility, Dimension, Metric

def sample_check_compatibility(property_id: str):
    client = BetaAnalyticsDataClient()

    # 定义您想要一起查询的维度和指标。
    # 例如，检查电子商务维度 'itemName'
    # 是否与 'activeUsers' 和 'totalRevenue' 兼容。
    request = CheckCompatibilityRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="itemName"),
            Dimension(name="date")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="totalRevenue")
        ],
    )
    response = client.check_compatibility(request)

    print(f"属性 {property_id} 的兼容性检查：")
    for dim in response.dimension_compatibilities:
        is_compatible = dim.compatibility == Compatibility.COMPATIBLE
        print(f"维度 '{dim.dimension_metadata.api_name}' 兼容：{is_compatible}")

    for metric in response.metric_compatibilities:
        is_compatible = metric.compatibility == Compatibility.COMPATIBLE
        print(f"指标 '{metric.metric_metadata.api_name}' 兼容：{is_compatible}")

if __name__ == "__main__":
    sample_check_compatibility("YOUR-PROPERTY-ID")
```
