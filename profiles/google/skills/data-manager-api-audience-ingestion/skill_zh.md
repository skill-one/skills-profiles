# 数据管理器 API 受众摄入

## 实现工作流

### 前置条件

-   **认证 & 库安装**：如果您需要设置对数据管理器 API 的访问权限或安装客户端和实用程序库，请参考 `data-manager-api-setup` 技能。
-   **受众创建（如果需要）**：如果用户没有现有的受众或需要创建一个新的，请使用 `[创建受众](references/create-audience.md)` 参考。此步骤提供了摄入或删除请求所需的 `product_destination_id`。

### 第 1 步：确定用例 & 阅读文档

-   **确定目标账户类型**：[关键] 如果不清楚数据发送到何处（例如，Google Ads、展示与视频 360 等），请在生成任何代码之前停止并明确与用户沟通。不要默认假设是 Google Ads。这对应于 `Destination` 中 `operating_account` 的 `account_type` 字段。
-   **阅读实现指南**：在回答问题或编写代码之前，请阅读与您的目标和用例相关的指南。因为每个目标都有独特的有效载荷结构、同意规则和必填字段。

| 目标 | 受众类型 | 接受的数据类型 | 上传指南 | 删除所有/替换所有指南 |
| :--- | :--- | :--- | :--- | :--- |
| **Google Ads** | Customer Match | `composite_data.user_data`（联系信息）、`mobile_data`（设备 ID）、`user_id_data`（用户 ID） | [上传数据](https://developers.google.com/data-manager/api/devguides/audiences/google-ads/customer-match/upload-data.md.txt) | [删除所有/替换所有](https://developers.google.com/data-manager/api/devguides/audiences/google-ads/customer-match/remove-all-members.md.txt) |
| **展示与视频 360**（DV360） | Customer Match | `composite_data.user_data`（联系信息）、`mobile_data`（设备 ID） | [上传数据](https://developers.google.com/data-manager/api/devguides/audiences/display-video/customer-match/upload-data.md.txt) | [删除所有/替换所有](https://developers.google.com/data-manager/api/devguides/audiences/display-video/customer-match/remove-all-members.md.txt) |

### 第 2 步：获取代码示例

> [!IMPORTANT] 如果编写或更新摄入脚本，请始终获取相关代码示例作为参考：

| 语言 | 示例 |
| :--- | :--- |
| **Python** | [`ingest_audience_members.py`](https://github.com/googleads/data-manager-python/blob/main/samples/audiences/ingest_audience_members.py) |
| **Java** | [`IngestAudienceMembers.java`](https://github.com/googleads/data-manager-java/blob/main/data-manager-samples/src/main/java/com/google/ads/datamanager/samples/IngestAudienceMembers.java) |
| **PHP** | [`ingest_audience_members.php`](https://github.com/googleads/data-manager-php/blob/main/samples/audiences/ingest_audience_members.php) |
| **Node** | [`ingest_audience_members.ts`](https://github.com/googleads/data-manager-node/blob/main/samples/audiences/ingest_audience_members.ts) |
| **.NET**| [`IngestAudienceMembers.cs`](https://github.com/googleads/data-manager-dotnet/blob/main/samples/IngestAudienceMembers.cs) |

### 第 3 步：获取迁移指南

> [!IMPORTANT] 如果重构代码以从另一个 Google API 升级，请始终提取相关字段映射指南的全部内容。

#### Google Ads

*   **Google Ads API Customer Match**：[Google Ads API 到 Customer Match 迁移字段映射](https://developers.google.com/data-manager/api/devguides/audiences/google-ads/customer-match/upgrade/field-mappings.md.txt)

#### 展示与视频 360

*   **展示与视频 360 API Customer Match**：[展示与视频 360 API 到 Customer Match 迁移字段映射](https://developers.google.com/data-manager/api/devguides/audiences/display-video/customer-match/upgrade/field-mappings.md.txt)

### 第 4 步：实现

使用以下检查点实现摄入逻辑：

-   [ ] **初始化客户端**：实例化数据管理器客户端 (`IngestionServiceClient`)。
-   [ ] **定义目标**：使用 `product_destination_id` 和适当的账户配置构建 `Destination` 对象：`operating_account`（接收数据的靶账户）、`login_account`（如果使用管理员账户或数据合作伙伴账户进行身份验证）、`linked_account`（如果您是通过合作伙伴链接到管理员账户的数据合作伙伴访问账户）。**强烈推荐**：参考 [配置目标和标头](https://developers.google.com/data-manager/api/devguides/concepts/destinations.md.txt) 指南，了解更多关于配置目标的信息。
-   [ ] **格式化用户数据**：如果发送 `IngestAudienceMembersRequest` 或 `RemoveAudienceMembersRequest`，请参考 **[格式化用户数据](references/formatting.md)** 以使用实用程序库正确规范化和散列用户标识符。
-   [ ] **构建有效载荷**：根据操作构建适当的有效载荷：
    *   **添加**：`IngestAudienceMembersRequest`
    *   **删除**：`RemoveAudienceMembersRequest`
    *   **删除所有**：`RemoveAllAudienceMembersRequest`
-   [ ] **支持验证**：支持在有效载荷上发送 `validate_only` 布尔选项，以允许开发人员在不实际应用更改的情况下验证架构。
-   [ ] **发送请求**：执行适当的方法并记录返回的 `request_id` 以供后续诊断：
    *   **添加**：`ingest_audience_members`
    *   **删除**：`remove_audience_members`
    *   **删除所有**：`remove_all_audience_members`
-   [ ] **检查摄入警告**：如果任何非必填字段出现验证失败，`ingest_audience_members` 的响应还将包含 `field_warnings`，这是一个包含 `FieldWarning` 对象的列表，详细说明了问题。
-   [ ] **获取请求状态**：使用诊断检查摄入请求的状态。由于请求处理是异步的，成功的响应（HTTP 200 OK 返回 `request_id`）仅表示有效载荷已接收。要检查记录是否实际成功、部分成功或处理失败，请使用 `request_id` 查询 `client.retrieve_request_status`。跳过此步骤是常见的用户错误。

## 关键注意事项

*   如果在 `user_data` 中发送散列的用户标识符用于 `ingest_audience_members` 或 `remove_audience_members`，您必须将 `IngestAudienceMembersRequest` 上的 `encoding` 字段设置为 `HEX` 或 `BASE64`。
*   如果*上传*到 Customer Match 受众，`IngestAudienceMembersRequest` 上的 `terms_of_service` 字段是必需的，以指示用户已接受政策。
*   仅在所有必填字段（`postal_code`、`family_name`、`given_name`、`region_code`）都存在的情况下，才在 `UserIdentifier` 上设置 `address` 字段；不完整的 `address` 字段会导致 API 请求失败。
*   `product_destination_id` 必须是数字字符串。它不是资源名称。
*   `ConsentStatus` 的枚举值是 `CONSENT_GRANTED` 和 `CONSENT_DENIED`。不要使用 `GRANTED` 和 `DENIED` 的值。
*   `UserIdentifier` 上的字段名是 `email_address` 和 `phone_number`。不要使用 Google Ads API 字段名 `hashed_email` 和 `hashed_phone_number`。
*   如果 `validate_only` 设置为 `true`，请不要调用诊断端点 (`retrieve_request_status`)。

## 错误处理 & 排错

### 检查错误有效载荷 & 摄入警告

> [!IMPORTANT]
> 参考 [理解 API 错误](https://developers.google.com/data-manager/api/devguides/concepts/understand-errors.md.txt)
> 获取有关如何理解 API 返回的错误和警告结构的详细指南。

### 获取请求状态（诊断）

使用指数退避，从发送请求后至少 30 分钟开始，定期轮询状态。

1.  调用 `client.retrieve_request_status` 使用
    `RetrieveRequestStatusRequest(request_id=...)`。
2.  遍历响应中的 `request_status_per_destination` 以检查每个目标的 `request_status`。
3.  如果处理完成且 `request_status` 是 `SUCCESS`、`PARTIAL_SUCCESS` 或 `FAILED`，请检查诊断值：
    *   **受众状态**：检查与您的请求相关的状态：
        *   **摄入**：检查嵌套在 `audience_members_ingestion_status` 下的数据类型特定状态（例如，
            `composite_data_ingestion_status`）。
        *   **删除单个成员**：检查嵌套在 `audience_members_removal_status` 下的数据类型特定状态（例如，
            `composite_data_removal_status`）。
        *   **删除所有成员**：对于此请求类型，没有嵌套状态字段或记录计数可用。
        *   **记录计数**：如果适用（摄入或删除单个成员），请检查 `record_count`（嵌套在数据类型特定状态对象内），它包括成功和失败。
        *   **标识符计数**：如果适用（摄入或删除单个成员），请检查嵌套在状态对象内的数据类型特定计数字段（例如，如果上传或删除复合数据，则为 `data_type_counts`；如果上传或删除移动 ID，则为 `mobile_id_count`）。参考 [诊断指南](https://developers.google.com/data-manager/api/devguides/diagnostics.md.txt)
            获取其他计数字段。
        *   **匹配率范围**：对于 `user_data` 和 `composite_data` 的上传，请检查嵌套在状态对象内的 `upload_match_rate_range`。
    *   **错误详情**：如果状态是 `FAILED` 或 `PARTIAL_SUCCESS`，请检查每个错误的 `reason` 和 `record_count` 在
        `error_info.error_counts` 下。
    *   **警告详情**：请检查每个警告的 `reason` 和 `record_count` 在 `warning_info.warning_counts` 下（即使目标状态是 `SUCCESS`）。

## API 参考

*   [发送受众成员指南](https://developers.google.com/data-manager/api/devguides/audiences/send-audience-members.md.txt)
*   [REST API 参考：摄入](https://developers.google.com/data-manager/api/reference/rest/v1/audienceMembers/ingest.md.txt)
*   [REST API 参考：删除](https://developers.google.com/data-manager/api/reference/rest/v1/audienceMembers/remove.md.txt)
*   [REST API 参考：删除所有](https://developers.google.com/data-manager/api/reference/rest/v1/audienceMembers/removeAll.md.txt)
