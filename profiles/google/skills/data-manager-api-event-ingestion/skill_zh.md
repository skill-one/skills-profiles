# 数据管理器 API 事件摄取

## 实现工作流

### 前置条件

-   **认证 & 库安装**：如果您需要设置对数据管理器 API 的访问权限或安装客户端和实用程序库，请参考 `data-manager-api-setup` 技能。

### 第 1 步：确定用例 & 阅读文档

-   **确定目标账户类型**：[关键] 如果无法从用户上下文中确定，请在生成任何代码之前考虑澄清正在摄取哪些目标事件。这映射到 `Destination` 中的 `operating_account` 的 `account_type` 字段，并确定有效的事件标识符和要求。
-   **确定用户意图**：
    -   **实现摄取代码**：请遵循下方“实现指南”列中与目标和用例相关的相关实现指南。这对于确保字段要求得到满足并正确配置目标至关重要。
    -   **检查请求状态或检查错误**：请参考下方的 [错误处理与故障排除](#error-handling-troubleshooting) 部分。
    -   **从其他 Google API 迁移**：请参考下方的 [第 3 步：检索迁移指南](#step-3-retrieve-migration-guides) 以提取相关字段映射指南的完整内容。

| 目标 (`operating_account.account_type`) | 用例 | 实现指南 |
| :--- | :--- | :--- |
| **Google Ads** (`GOOGLE_ADS`) | 离线转化、用于潜在客户的增强转化 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/google-ads/offline/send-events.md.txt) |
| **Google Ads** (`GOOGLE_ADS`) | 补充 Google 标签的多源转化 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/google-ads/online/send-events.md.txt) |
| **Google Ads** (`GOOGLE_ADS`) | 店铺销售转化 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/google-ads/store-sales/send-events.md.txt) |
| **Google Analytics** (`GOOGLE_ANALYTICS_PROPERTY`) | 推荐和自定义 GA4 事件 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/analytics/recommended-custom-events/send-events.md.txt) |
| **Google Analytics** (`GOOGLE_ANALYTICS_PROPERTY`) | 具有交易 ID 的多源事件 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/analytics/online/send-events.md.txt) |
| **Floodlight** (`FLOODLIGHT_CONFIG`) | Floodlight 离线转化 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/cm360/offline/send-events.md.txt) |
| **Floodlight** (`FLOODLIGHT_CONFIG`) | 补充 Google 或 Floodlight 标签的多源转化 | [发送事件](https://developers.google.com/data-manager/api/devguides/events/cm360/online/send-events.md.txt) |

如果请求不匹配任何行，请获取 [事件概述](https://developers.google.com/data-manager/api/devguides/events.md.txt) 以找到正确的指南，而不是猜测。

### 第 2 步：检索代码示例

> [!IMPORTANT]
> 如果编写或更新摄取脚本，请始终检索相关代码示例作为参考：

| 语言 | 示例 |
| :--- | :--- |
| **Python** | [`ingest_events.py`](https://github.com/googleads/data-manager-python/blob/main/samples/events/ingest_events.py) |
| **Java** | [`IngestEvents.java`](https://github.com/googleads/data-manager-java/blob/main/data-manager-samples/src/main/java/com/google/ads/datamanager/samples/IngestEvents.java) |
| **PHP** | [`ingest_events.php`](https://github.com/googleads/data-manager-php/blob/main/samples/events/ingest_events.php) |
| **Node** | [`ingest_events.ts`](https://github.com/googleads/data-manager-node/blob/main/samples/events/ingest_events.ts) |
| **.NET**| [`IngestEvents.cs`](https://github.com/googleads/data-manager-dotnet/blob/main/samples/IngestEvents.cs) |

### 第 3 步：检索迁移指南

> [!IMPORTANT]
> 如果重构代码以从另一个 Google API 升级，请始终提取相关字段映射指南的完整内容。

#### Google Ads

*   **离线转化、用于潜在客户的增强转化**（从 Google Ads API 迁移）：
    [Google Ads 离线转化迁移字段映射](https://developers.google.com/data-manager/api/devguides/events/google-ads/offline/upgrade/field-mappings.md.txt)
*   **店铺销售转化**（从 Google Ads API 迁移）：
    [Google Ads 店铺销售迁移字段映射](https://developers.google.com/data-manager/api/devguides/events/google-ads/store-sales/upgrade/field-mappings.md.txt)

#### Google Analytics

*   **推荐和自定义 GA4 事件**（从 Google Analytics 测量协议迁移）：
    [Google Analytics 测量协议迁移字段映射](https://developers.google.com/data-manager/api/devguides/events/analytics/measurement-protocol/upgrade/field-mappings.md.txt)

#### Floodlight

*   **Floodlight 离线转化**（从 Campaign Manager 360 API 迁移）：
    [Campaign Manager 360 离线转化迁移字段映射](https://developers.google.com/data-manager/api/devguides/events/cm360/offline/upgrade/field-mappings.md.txt)

### 第 4 步：实现

使用以下检查点实现摄取逻辑：

-   [ ] **初始化客户端**：实例化数据管理器客户端 (`IngestionServiceClient`)。
-   [ ] **定义目标**：使用 `product_destination_id` 和适当的账户配置构建 `Destination` 对象：`operating_account`（接收数据的目标账户）、`login_account`（如果使用管理员账户或数据合作伙伴账户进行身份验证）、`linked_account`（如果您是通过合作伙伴链接到管理员账户的数据合作伙伴访问账户）。**强烈推荐**：请参考 [配置目标和标头](https://developers.google.com/data-manager/api/devguides/concepts/destinations.md.txt) 指南，了解更多关于配置目标的详细信息。
-   [ ] **准备事件数据**：使用实用程序库帮助程序正确格式化和规范化用户标识符。
-   [ ] **构建有效负载**：构建包含目标、事件记录和同意权限的请求有效负载 (`IngestEventsRequest`)。
-   [ ] **支持验证**：支持在 `IngestEventsRequest` 上发送 `validate_only` 布尔选项，以允许开发人员在不实际上传数据的情况下验证模式。
-   [ ] **发送请求**：执行 `ingest_events` 并记录返回的 `request_id` 以供后续诊断。
-   [ ] **检查摄取警告**：如果任何非必需字段出现验证失败，`ingest_events` 的响应还将包含 `field_warnings`，这是一个包含 `FieldWarning` 对象的列表，详细说明了问题。
-   [ ] **检索请求状态**：使用诊断检查摄取请求的状态。由于请求处理是异步的，成功的摄取响应（返回 `request_id` 的 HTTP 200 OK）仅表示有效负载已接收。要检查记录是否实际上成功、部分成功或处理失败，请使用 `request_id` 查询 `client.retrieve_request_status` 端点。跳过此步骤是常见用户错误。

## 格式化

*   获取 [格式化用户数据](https://developers.google.com/data-manager/api/devguides/concepts/formatting.md.txt) 指南，并将其用作格式化和规范化规则的真实来源。

*   使用实用程序库对用户数据进行格式化、哈希和加密（电子邮件、电话号码、地址）。

    **Python 示例：**

    ```python
    from google.ads.datamanager_util import Formatter
    from google.ads.datamanager_util.format import Encoding

    formatter: Formatter = Formatter()

    processed_email: str = formatter.process_email_address(
        email, Encoding.HEX
    )
    ```

## 关键注意事项

*   将 `product_destination_id` 格式化为数字字符串。它**不是**资源名称路径。
*   严格按 RFC 3339 格式化 `event_timestamp`。在可用的情况下，使用 SDK 的 typed 时间戳对象，而不是原始字符串。
*   将点击标识符 (`gclid`、`gbraid`、`wbraid`) 嵌套在 `ad_identifiers` 块内，而不是直接在基础事件有效负载上。
*   `ConsentStatus` 的枚举值是 `CONSENT_GRANTED` 和 `CONSENT_DENIED`。不要使用 `GRANTED` 和 `DENIED` 的值。
*   请注意，`consent` 可以在 `IngestEventsRequest` 上全局设置，也可以在单个 `Event` 上设置。
*   验证 `UserIdentifier` 使用 `email_address` 和 `phone_number`。不要使用 Google Ads API 字段 `hashed_email` 和 `hashed_phone_number`。
*   确保事件上的货币字段命名为 `currency`，而不是 `currency_code`。
*   如果 `validate_only` 设置为 `true`，请不要调用诊断端点 (`retrieve_request_status`)。

## 错误处理与故障排除

### 检查错误有效负载 & 摄取警告

> [!IMPORTANT]
> 参考 [理解 API 错误](https://developers.google.com/data-manager/api/devguides/concepts/understand-errors.md.txt)
> 获取有关如何理解 API 返回的错误和警告结构的详细指南。

### 检索请求状态（诊断）

使用指数退避定期轮询，至少在发送 `IngestEventsRequest` 30 分钟后开始。

1.  调用 `client.retrieve_request_status`，使用 `RetrieveRequestStatusRequest(request_id=...)`。
2.  循环遍历响应中的 `request_status_per_destination` 以检查每个目标的 `request_status`。
3.  如果处理完成且 `request_status` 是 `SUCCESS`、`PARTIAL_SUCCESS` 或 `FAILED`，请检查诊断值：
    *   **事件记录计数**：检查 `events_ingestion_status.record_count`（包括成功和失败）。
    *   **错误详细信息**：如果状态是 `FAILED` 或 `PARTIAL_SUCCESS`，请检查每个错误在 `error_info.error_counts` 下的 `reason` 和 `record_count`。
    *   **警告详细信息**：检查每个警告在 `warning_info.warning_counts` 下的 `reason` 和 `record_count`（即使目标状态是 `SUCCESS`）。

## API 参考

*   [REST API 参考](https://developers.google.com/data-manager/api/reference/rest/v1/events/ingest.md.txt)
*   [诊断指南](https://developers.google.com/data-manager/api/devguides/diagnostics.md.txt)
