# 数据管道

构建用于数据集成、转换和分析自动化的数据管道和ETL工作流。基于n8n的数据工作流模板。

## 概述

本技能涵盖：
- 从多个来源进行数据提取
- 转换和清洗
- 加载到目标位置
- 调度和监控
- 错误处理和警报

---

## ETL模式

### 基本ETL流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   提取     │───▶│  转换     │───▶│    加载     │
│             │    │             │    │             │
│ • API      │    │ • 清洗     │    │ • 数据库    │
│ • 数据库   │    │ • 映射     │    │ • 仓库     │
│ • 文件     │    │ • 聚合     │    │ • 文件     │
│ • Webhook  │    │ • 丰富     │    │ • API      │
└─────────────┘    └─────────────┘    └─────────────┘
```

### n8n ETL工作流

```yaml
workflow: "每日销售ETL"
schedule: "凌晨2点每日"

nodes:
  # 提取
  - name: "从Shopify提取"
    type: shopify
    action: get_orders
    filter: created_at >= yesterday
    
  - name: "从Stripe提取"
    type: stripe
    action: get_payments
    filter: created >= yesterday
    
  # 转换
  - name: "合并数据"
    type: merge
    mode: combine_by_key
    key: order_id
    
  - name: "转换"
    type: code
    code: |
      return items.map(item => ({
        date: item.created_at.split('T')[0],
        order_id: item.id,
        customer_email: item.email,
        total: parseFloat(item.total_price),
        currency: item.currency,
        items: item.line_items.length,
        source: item.source_name,
        payment_status: item.payment.status
      }));
      
  # 加载
  - name: "加载到BigQuery"
    type: google_bigquery
    action: insert_rows
    table: sales_daily
    
  - name: "更新Google表格"
    type: google_sheets
    action: append_rows
    spreadsheet: "每日销售报告"
```

---

## 数据源

### 常用提取器

```yaml
extractors:
  databases:
    - postgresql:
        connection: connection_string
        query: "SELECT * FROM orders WHERE date >= $1"
        
    - mysql:
        connection: connection_string
        query: custom_sql
        
    - mongodb:
        connection: connection_string
        collection: orders
        filter: {date: {$gte: yesterday}}
        
  APIs:
    - rest_api:
        url: "https://api.example.com/data"
        method: GET
        headers: {Authorization: "Bearer {token}"}
        pagination: handle_automatically
        
    - graphql:
        url: "https://api.example.com/graphql"
        query: graphql_query
        
  文件:
    - csv:
        source: sftp/s3/google_drive
        delimiter: ","
        encoding: utf-8
        
    - excel:
        source: file_path
        sheet: "Sheet1"
        
    - json:
        source: api/file
        path: "data.items"
        
  SaaS:
    - salesforce: get_objects
    - hubspot: get_contacts/deals
    - stripe: get_charges
    - shopify: get_orders
```

---

## 转换

### 常用转换

```yaml
transformations:
  清洗:
    - remove_nulls: drop_or_fill
    - trim_whitespace: all_string_fields
    - deduplicate: by_key
    - validate: against_schema
    
  映射:
    - rename_fields: {old_name: new_name}
    - convert_types: {date_string: date}
    - map_values: {status_code: status_name}
    
  聚合:
    - group_by: [date, category]
    - sum: [revenue, quantity]
    - count: orders
    - average: order_value
    
  丰富:
    - lookup: from_reference_table
    - geocode: from_address
    - calculate: derived_fields
    
  过滤:
    - where: condition
    - limit: n_rows
    - sample: percentage
```

### 代码转换示例

```javascript
// 清洗和规范化数据
function transform(items) {
  return items.map(item => ({
    // 清洗字符串
    name: item.name?.trim().toLowerCase(),
    
    // 解析日期
    date: new Date(item.created_at).toISOString().split('T')[0],
    
    // 转换类型
    amount: parseFloat(item.amount) || 0,
    
    // 映射值
    status: statusMap[item.status_code] || 'unknown',
    
    // 计算字段
    total: item.quantity * item.unit_price,
    
    // 过滤嵌套
    tags: item.tags?.filter(t => t.active).map(t => t.name),
    
    // 默认值
    source: item.source || 'direct'
  }));
}

// 聚合数据
function aggregate(items) {
  const grouped = {};
  
  items.forEach(item => {
    const key = `${item.date}_${item.category}`;
    if (!grouped[key]) {
      grouped[key] = {
        date: item.date,
        category: item.category,
        total_revenue: 0,
        order_count: 0
      };
    }
    grouped[key].total_revenue += item.amount;
    grouped[key].order_count += 1;
  });
  
  return Object.values(grouped);
}
```

---

## 数据目标

### 常用加载器

```yaml
loaders:
  数据仓库:
    - bigquery:
        project: project_id
        dataset: analytics
        table: sales
        write_mode: append/truncate
        
    - snowflake:
        account: account_id
        warehouse: compute_wh
        database: analytics
        schema: public
        
    - redshift:
        cluster: cluster_id
        database: analytics
        
  数据库:
    - postgresql:
        upsert: on_conflict_update
        
    - mysql:
        batch_insert: 1000_rows
        
  文件:
    - s3:
        bucket: data-lake
        path: /processed/{date}/
        format: parquet
        
    - google_cloud_storage:
        bucket: data-bucket
        
  电子表格:
    - google_sheets:
        mode: append/overwrite
        
    - airtable:
        base: base_id
        table: table_name
        
  API:
    - webhook:
        url: destination_url
        batch_size: 100
```

---

## 调度与监控

### 管道调度

```yaml
scheduling:
  patterns:
    每小时:
      cron: "0 * * * *"
      use_for: real_time_dashboards
      
    每日:
      cron: "0 2 * * *"
      use_for: daily_reports
      
    每周:
      cron: "0 3 * * 1"
      use_for: weekly_summaries
      
    按需:
      trigger: webhook/manual
      use_for: ad_hoc_analysis
      
  依赖:
    - pipeline_a: must_complete_before pipeline_b
    - wait_for: all_extracts_complete
    
  重试:
    max_attempts: 3
    delay: exponential_backoff
    alert_on: final_failure
```

### 监控与警报

```yaml
monitoring:
  metrics:
    - rows_processed
    - execution_time
    - error_count
    - data_freshness
    
  警报:
    pipeline_failed:
      channels: [slack, pagerduty]
      template: |
        🚨 *管道失败*
        
        管道: {pipeline_name}
        阶段: {failed_stage}
        错误: {error_message}
        
        [查看日志]({logs_url})
        
    数据质量:
      trigger: anomaly_detected
      conditions:
        - row_count: differs_by > 50%
        - null_rate: exceeds_threshold
        - schema: changed_unexpectedly
        
    陈旧数据:
      trigger: last_update > threshold
      threshold: 2_hours
```

---

## 数据质量

### 质量检查

```yaml
data_quality:
  schema_validation:
    - required_fields: [id, date, amount]
    - field_types:
        id: integer
        date: date
        amount: number
    - allowed_values:
        status: [active, pending, closed]
        
  统计检查:
    - null_rate: < 5%
    - duplicate_rate: < 1%
    - value_range:
        amount: [0, 1000000]
        
  业务规则:
    - total_equals_sum_of_line_items
    - dates_are_not_in_future
    - email_format_valid
    
  趋势分析:
    - row_count: within_2_std_of_mean
    - total_value: within_expected_range
```

---

## 输出示例

**请求**: "创建每日销售数据管道"

**输出**:

```markdown
# 每日销售数据管道

## 管道概述

```
Shopify + Stripe → 转换 → BigQuery + 表格
```

## 调度
- 运行: 每日凌晨2点
- 时区: UTC
- 重试: 3次

## 提取

### Shopify订单
```yaml
source: shopify
filter: created_at >= yesterday
fields: [id, email, total_price, line_items, created_at]
```

### Stripe支付
```yaml
source: stripe
filter: created >= yesterday
fields: [id, amount, status, metadata.order_id]
```

## 转换

```javascript
// 连接和清洗数据
{
  date: order.created_at.split('T')[0],
  order_id: order.id,
  customer: order.email,
  revenue: parseFloat(order.total_price),
  items: order.line_items.length,
  payment_status: payment.status
}
```

## 加载

### BigQuery
- 表: `analytics.sales_daily`
- 模式: Append

### Google表格
- 表: "每日销售仪表板"
- 标签: "原始数据"

## 质量检查
- [ ] 行数 > 0
- [ ] 无null order_ids
- [ ] 收入总和匹配Stripe

## 警报
- Slack: #data-alerts
- 失败时: @data-team
```

---

*数据管道技能 - 隶属于Claude办公技能*
