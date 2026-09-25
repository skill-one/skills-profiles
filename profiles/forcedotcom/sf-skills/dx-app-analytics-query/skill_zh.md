# 应用分析

## 此技能适用场景

当工作涉及以下内容时，使用 `dx-app-analytics-query`：
- 通过 REST/sObject API 创建 `AppAnalyticsQueryRequest` 记录
- 通过元数据 API 配置 `AppAnalyticsSettings`（模拟模式、退出）
- 理解查询生命周期：新建 → 待处理 → 完成 → 过期 → 失败
- 选择 dataType 值：PackageUsageSummary、PackageUsageLog、SubscriberSnapshot
- 分析下载的文件格式和压缩选项
- 使用 startTime、endTime、availableSince 进行时间范围过滤
- 排查失败或过期的分析查询

当用户需要以下操作时，应委派给其他技能：
- 运行标准 CRM SOQL 查询 → platform-soql-query
- 在标准对象上构建报告/仪表板 → 报告技能
- 部署或检索通用元数据 XML → platform-metadata-deploy / retrieving-metadata

---

## 可用类型

### AppAnalyticsQueryRequest (REST/sObject API)

异步查询请求，ISV 合作伙伴使用它从 ISV 智能数据湖检索其管理的包的使用分析数据。通过 `POST /services/data/vXX.0/sobjects/AppAnalyticsQueryRequest` 创建记录，并通过 `GET /services/data/vXX.0/sobjects/AppAnalyticsQueryRequest/<id>` 进行轮询。系统处理查询并在完成后提供预签名的下载 URL。

**字段（14 个属性）：**

| 字段 | 类型 | 描述 |
|------|------|------|
| DataType | string (可过滤) | 分析数据类型。值：`PackageUsageSummary`、`PackageUsageLog`、`SubscriberSnapshot` |
| RequestState | string (可过滤) | 处理状态。值：`New`、`Pending`、`Complete`、`Expired`、`Failed`、`NoData`、`Delivered` |
| StartTime | string | 请求数据的时间范围开始 |
| EndTime | string | 时间范围结束。应设置在小时边界上 |
| AvailableSince | string | 将查询限制为在此时间之后索引的数据（包含）。用于增量检索 |
| PackageIds | string | 以逗号分隔的管理包 ID 列表（033 前缀） |
| OrganizationIds | string | 以逗号分隔的订阅者组织 ID 列表，用于过滤结果 |
| DownloadUrl | string | 用于下载结果的预签名 URL。当 RequestState 为 Complete 时填充 |
| DownloadSize | long | 结果数据文件的大小（字节） |
| DownloadExpirationTime | string | 下载 URL 过期的时间 |
| FileType | string (可过滤) | 输出格式。值：`csv`、`parquet` |
| FileCompression | string (可过滤) | 压缩。值：`none`、`gzip`、`snappy` |
| QuerySubmittedTime | string | 查询提交到数据湖的时间 |
| ErrorMessage | string | 失败查询的诊断消息 |

### AppAnalyticsSettings (元数据 API)

ISV 应用分析的配置设置，控制模拟模式和退出行为。通过元数据 API (`sf project deploy`) 或工具 API 部署。

**字段（2 个属性）：**

| 字段 | 类型 | 描述 |
|------|------|------|
| enableSimulationMode | boolean (可过滤) | 当为 true 时，允许查询示例使用日志进行集成测试，而无需真实订阅者数据 |
| enableAppAnalyticsOptOut | boolean (可过滤) | 当为 true 时，将此订阅者组织退出 AppExchange 应用分析数据收集 |

---

## 请求生命周期

```text
新建 → 待处理 → 完成 → (在过期窗口内下载)
                     → 过期（下载 URL 无效）
                     → 已交付（下载确认接收）
         → 失败（检查 errorMessage）
         → 无数据（没有符合标准的记录）
```

---

## 常见模式

### 查询包使用摘要（过去 7 天）

通过 REST API 创建记录：

```bash
POST /services/data/v60.0/sobjects/AppAnalyticsQueryRequest
Content-Type: application/json

{
  "DataType": "PackageUsageSummary",
  "StartTime": "<7-days-ago>T00:00:00Z",
  "EndTime": "<today-on-hour-boundary>T00:00:00Z",
  "PackageIds": "033XXXXXXXXXXXX",
  "FileType": "csv",
  "FileCompression": "gzip"
}
```

通过 GET 轮询记录，直到 `RequestState` 达到 `Complete`，然后从 `DownloadUrl` 下载。

### 增量数据检索

将 `AvailableSince` 设置为上次成功查询完成的时间戳，以避免重新下载您已经拥有的数据。

### 为测试启用模拟模式

通过元数据 API 部署 `AppAnalyticsSettings` 并设置 `enableSimulationMode: true`，以查询示例数据而无需真实订阅者。

---

## 高信号注意事项

- AppAnalyticsQueryRequest 是一个 **sObject** — 通过 REST 数据 API (`/sobjects/AppAnalyticsQueryRequest`) 创建和轮询记录，**不**通过元数据 API XML 部署。
- AppAnalyticsQueryRequest **没有** Apex 触发器，**不**通过自定义对象或流程流转。
- 下载 URL 会过期 — 在尝试下载前，始终检查 `DownloadExpirationTime`。
- `EndTime` 应设置在小时边界上以获得一致结果。
- `AvailableSince` 是包含的 — 在该时间戳精确索引的数据将被包含。
- `PackageIds` 使用 033 前缀 ID，而不是 04t（包版本）ID。
- 数据由 ISV 智能数据湖基础设施异步处理。没有同步查询选项。
- `FileType: parquet` 与 `FileCompression: snappy` 为大型数据集提供最佳性能。

---

## 输出格式

```text
分析任务：<查询 / 配置 / 排查>
数据类型：<PackageUsageSummary / PackageUsageLog / SubscriberSnapshot>
包 ID：<033 前缀 ID>
时间范围：<startTime> 至 <endTime>
文件格式：<csv|parquet> / <none|gzip|snappy>
请求状态：<当前状态>
下一步：<轮询完成 / 下载 / 调查失败>
```
