# Google Ads API 账户性能诊断技能

本技能提供使用 Google Ads MCP 服务器工具诊断常见账户性能问题的说明。

## 工作流程

### 识别活跃的客户账户
大多数诊断任务需要向特定客户账户发送 GAQL 查询。如果用户没有显式提供客户 ID，您必须首先调用 `list_accessible_customers`（或 `customers_list_accessible_customers`）工具来检索您有权访问的客户资源名称/ID。

一旦您获得了可访问的客户 ID 列表，请在这些客户账户下使用 `search` 工具查询 `customer_client` 资源，以找到活跃的客户客户账户。确保仅选择启用的客户账户并过滤掉管理账户：
```sql
SELECT
  customer_client.id,
  customer_client.descriptive_name,
  customer_client.status,
  customer_client.manager
FROM customer_client
WHERE customer_client.status = 'ENABLED' AND customer_client.manager = FALSE
```
仅针对从此列表检索到的启用客户客户 ID 运行后续的诊断查询。不要查询已停用或管理账户，因为这样做会导致 API 错误。

### 直接使用 MCP 工具
要检索信息并运行查询，您必须直接在 MCP 服务器上调用 `search` 工具（使用 `customer_id`、`fields`、`resource` 和 `conditions` 等参数）。不要编写或执行自定义 Python 脚本或使用 Google Ads 客户库查询 API，因为它们在评估沙盒中会失败身份验证。

### 1. 转化和转化价值损失

当转化或转化价值突然下降时，使用以下步骤来诊断问题。

**步骤：**
1.  **发现字段**：使用 `get_resource_metadata` 并指定资源 `campaign` 或 `ad_group`，以确保您拥有正确的字段名称。
2.  **查询性能**：使用 `search` 检索性能数据。
    *   **资源**：`campaign` 或 `ad_group`
    *   **字段**：包括 `campaign.name`、`metrics.conversions`、`metrics.conversions_value`、`metrics.cost_micros`。
    *   **细分**：为了隔离损失，包括细分如 `segments.date`、`segments.device`、`segments.conversion_action`。
    *   **条件**：将下降的时期与先前时期进行比较（例如，`segments.date >= '{start_date}'`）。
    *   *注意*：`metrics.cost_micros` 必须除以 1,000,000 才能获得标准货币金额。

    **示例 GAQL 查询：**
    要查询客户账户 `{customer_id}` 在 `{start_date}` 和 `{end_date}` 之间的性能数据：
    ```sql
    SELECT
      campaign.name,
      metrics.conversions,
      metrics.conversions_value,
      metrics.cost_micros,
      segments.date,
      segments.device,
      segments.conversion_action
    FROM campaign
    WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
    ```

3.  **分析**：检查损失是否仅限于某些设备（例如，移动设备与桌面设备）或特定的转化操作。
4.  **检查上传**：如果使用离线导入，请查询 `offline_conversion_upload_conversion_action_summary` 以验证上传管道健康状况。如果查询没有返回结果，请报告该账户不存在离线上传，然后继续。

    **示例 GAQL 查询：**
    要检查客户账户 `{customer_id}` 的上传管道健康状况：
    ```sql
    SELECT
      offline_conversion_upload_conversion_action_summary.conversion_action_name,
      offline_conversion_upload_conversion_action_summary.successful_event_count,
      offline_conversion_upload_conversion_action_summary.total_event_count,
      offline_conversion_upload_conversion_action_summary.status
    FROM offline_conversion_upload_conversion_action_summary
    ```

### 2. 机会损失（展示份额）

要识别由于广告排名、出价或预算导致的机会损失，请分析展示份额指标。

**步骤：**
1.  **查询展示份额**：使用 `search` 检索展示份额指标。
    *   **资源**：`campaign`
    *   **字段**：包括 `campaign.name`、`metrics.search_impression_share`、`metrics.search_rank_lost_impression_share`、`metrics.search_budget_lost_impression_share`。
    *   *注意*：API 中返回的展示份额值为小数（例如，0.35 = 35%）或格式化字符串（例如，`"< 0.10"`）。

    **示例 GAQL 查询：**
    要查询客户账户 `{customer_id}` 在 `{start_date}` 和 `{end_date}` 之间的展示份额指标：
    ```sql
    SELECT
      campaign.name,
      metrics.search_impression_share,
      metrics.search_rank_lost_impression_share,
      metrics.search_budget_lost_impression_share
    FROM campaign
    WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
    ```

2.  **分析**：
    *   高 `search_budget_lost_impression_share` 表示由于预算有限而失去的机会。
    *   高 `search_rank_lost_impression_share` 表示由于广告排名低（出价或质量问题）而失去的机会。

### 3. 低线索流量诊断

当用户询问“为什么我最近几天的线索流量低？”时，请遵循系统化方法。

**步骤：**
1.  **确认下降**：查询过去几天的转化数据，并与先前时期进行细分比较。
2.  **隔离原因**：
    *   检查流量（点击量、展示量）是否下降。
    *   检查转化率（转化量/点击量）是否下降。
3.  **如果流量下降**：检查展示份额指标（见工作流程 2）以查看这是预算或排名问题，还是搜索量普遍下降。
4.  **如果转化率下降**：检查按 `segments.device` 或 `segments.conversion_action` 的细分数据，以查看是否有特定领域出现故障。
5.  **检查变更**：查询 `change_event` 资源，以查看在下降开始时是否对出价、预算或定位进行了任何更改。
    *   *注意（change_event 限制）*：对 `change_event` 资源的查询：
        *   必须指定 `LIMIT` 子句，其值小于或等于 10000。
        *   必须按日期过滤（`change_event.change_date_time`），范围在过去 30 天内。
        *   不能选择性能指标（例如，`metrics.*` 不受支持；只能选择 `change_event` 属性和允许的资源字段）。

    **示例 GAQL 查询：**
    要查询客户账户 `{customer_id}` 在 `{start_date}` 和 `{end_date}` 之间的变更事件：
    ```sql
    SELECT
      change_event.change_date_time,
      change_event.change_resource_name,
      change_event.resource_change_operation,
      change_event.changed_fields
    FROM change_event
    WHERE change_event.change_date_time >= '{start_date}' AND change_event.change_date_time <= '{end_date}'
    LIMIT 10000
    ```

### 4. 离线上传管道诊断

当特定操作的离线转化上传（例如，store-purchase）不再显示或失败时，使用以下步骤来诊断问题。

**步骤：**
1.  **检索客户账户**：如果未提供 `{customer_id}`，请首先调用 `list_accessible_customers`（或 `customers_list_accessible_customers`）工具来检索您有权访问的客户资源名称/ID。然后，查询 `customer_client` 资源以找到活跃的客户客户账户，确保过滤掉管理账户和已停用/已取消的账户以避免查询错误。

    **示例 GAQL 查询：**
    ```sql
    SELECT
      customer_client.id,
      customer_client.descriptive_name,
      customer_client.status,
      customer_client.manager
    FROM customer_client
    WHERE customer_client.status = 'ENABLED' AND customer_client.manager = FALSE
    ```

2.  **验证管道健康状况**：为活跃的客户账户查询 `offline_conversion_upload_conversion_action_summary`。
    *   **字段**：包括 `offline_conversion_upload_conversion_action_summary.conversion_action_name`、`offline_conversion_upload_conversion_action_summary.successful_event_count`、`offline_conversion_upload_conversion_action_summary.total_event_count` 和 `offline_conversion_upload_conversion_action_summary.status`。

    **示例 GAQL 查询：**
    ```sql
    SELECT
      offline_conversion_upload_conversion_action_summary.conversion_action_name,
      offline_conversion_upload_conversion_action_summary.successful_event_count,
      offline_conversion_upload_conversion_action_summary.total_event_count,
      offline_conversion_upload_conversion_action_summary.status
    FROM offline_conversion_upload_conversion_action_summary
    ```

3.  **分析**：
    *   *注意*：如果对 `offline_conversion_upload_conversion_action_summary` 的查询返回结果为空或为空（表示客户账户没有配置或激活的离线转化上传），请立即停止/中断诊断工作流程。直接向用户报告可访问的账户中不存在离线转化上传数据或摘要，而不是重试或尝试生成自定义脚本。
    *   如果返回了结果，请通过比较 `successful_event_count` 与 `total_event_count` 来验证上传成功率。检查 `status` 字段以诊断失败。
