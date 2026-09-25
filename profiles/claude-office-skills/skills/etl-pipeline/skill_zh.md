# ETL 管道

全面的技能，用于设计和自动化提取、转换、加载数据管道。

## 管道架构

### 核心ETL流程

```
数据管道架构：
┌─────────────────────────────────────────────────────────┐
│                     提取                              │
├─────────┬─────────┬─────────┬─────────┬─────────────────┤
│ Postgres│  MySQL  │ MongoDB │  APIs   │  文件 (CSV/JSON)│
└────┬────┴────┬────┴────┬────┴────┬────┴────────┬────────┘
     │         │         │         │              │
     └─────────┴─────────┴────┬────┴──────────────┘
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    转换                             │
│  • 清理与验证    • 聚合与连接               │
│  • 标准化           • 计算指标              │
│  • 去重           • 应用业务规则           │
└────────────────────────┬────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      加载                                │
├─────────────┬─────────────┬─────────────┬───────────────┤
│  BigQuery   │  Snowflake  │  Redshift   │  数据湖    │
└─────────────┴─────────────┴─────────────┴───────────────┘
```

## 源连接器

### 数据库连接

```yaml
sources:
  postgres:
    type: postgresql
    host: db.example.com
    port: 5432
    database: production
    ssl: true
    提取:
      方法: 增量
      键: updated_at
      批量大小: 10000

  mysql:
    type: mysql
    host: mysql.example.com
    port: 3306
    database: analytics
    提取:
      方法: CDC
      binlog: true

  mongodb:
    type: mongodb
    连接字符串: mongodb+srv://...
    database: app_data
    提取:
      方法: 变更流
```

### API源

```yaml
api_sources:
  stripe:
    type: rest_api
    base_url: https://api.stripe.com/v1
    认证: bearer_token
    端点:
      - /charges
      - /customers
      - /subscriptions
    分页: 游标
    速率限制: 每秒100次

  salesforce:
    type: salesforce
    实例URL: https://company.salesforce.com
    认证: oauth2
    对象:
      - Account
      - Opportunity
      - Contact
    批量API: true
```

## 转换层

### 常见转换

```python
# 数据清理
transformations = {
    "clean_nulls": {
        "操作": "fill_null",
        "列": ["email", "phone"],
        "值": "unknown"
    },
    
    "standardize_dates": {
        "操作": "date_parse",
        "列": ["created_at", "updated_at"],
        "格式": "ISO8601"
    },
    
    "normalize_currency": {
        "操作": "convert_currency",
        "源列": "amount",
        "货币列": "currency",
        "目标": "USD"
    },
    
    "deduplicate": {
        "操作": "distinct",
        "键列": ["customer_id", "transaction_id"],
        "保留": "latest"
    }
}
```

### 聚合规则

```sql
-- 每日收入聚合
SELECT 
    DATE(created_at) as date,
    product_category,
    COUNT(*) as transactions,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders
WHERE created_at >= '${start_date}'
GROUP BY 1, 2
```

### 连接操作

```yaml
joins:
  - name: enrich_orders
    左: orders
    右: customers
    类型: 左
    on:
      - 左: customer_id
        右: id
    选择:
      - orders.*
      - customers.email
      - customers.segment
      - customers.lifetime_value

  - name: add_product_details
    左: enriched_orders
    右: products
    类型: 左
    on:
      - 左: product_id
        右: id
```

## 加载策略

### BigQuery加载

```yaml
bigquery_load:
  项目: my-project
  数据集: analytics
  表: fact_orders
  
  模式:
    - name: order_id
      type: STRING
      mode: REQUIRED
    - name: customer_id
      type: STRING
    - name: amount
      type: NUMERIC
    - name: created_at
      type: TIMESTAMP
  
  加载配置:
    写入配置: WRITE_APPEND
    创建配置: CREATE_IF_NEEDED
    聚类字段: [customer_id]
    时间分区:
      字段: created_at
      类型: DAY
```

### Snowflake加载

```yaml
snowflake_load:
  仓库: ETL_WH
  数据库: ANALYTICS
  模式: PUBLIC
  表: FACT_ORDERS
  
  阶段:
    阶段: '@MY_STAGE'
    文件格式: JSON
  
  复制选项:
    错误处理: CONTINUE
    清理: true
    按列名匹配: CASE_INSENSITIVE
```

## 管道编排

### DAG定义

```yaml
pipeline:
  name: daily_analytics_etl
  调度: "0 2 * * *"  # 每日凌晨2点
  
  任务:
    - id: extract_orders
      类型: 提取
      源: postgres
      查询: "SELECT * FROM orders WHERE date = '${execution_date}'"
      
    - id: extract_customers
      类型: 提取
      源: postgres
      查询: "SELECT * FROM customers"
      
    - id: transform_data
      类型: 转换
      依赖: [extract_orders, extract_customers]
      操作:
        - join_customers
        - calculate_metrics
        - apply_business_rules
      
    - id: load_warehouse
      类型: 加载
      依赖: [transform_data]
      目标: bigquery
      表: fact_orders
      
    - id: notify_complete
      类型: 通知
      依赖: [load_warehouse]
      渠道: slack
      消息: "每日ETL成功完成"
```

### 错误处理

```yaml
error_handling:
  重试:
    最大尝试次数: 3
    延迟秒数: 300
    指数退避: true
  
  错误时:
    - 记录错误
    - 发送警报
    - 保存失败记录
  
  死信队列:
    启用: true
    目的地: s3://etl-errors/
    保留天数: 30
```

## 数据质量

### 验证规则

```yaml
quality_checks:
  - name: null_check
    列: customer_id
    规则: not_null
    严重性: error
    
  - name: range_check
    列: amount
    规则: between
    最小值: 0
    最大值: 100000
    严重性: warning
    
  - name: 唯一性
    列: [order_id]
    规则: unique
    严重性: error
    
  - name: 参照完整性
    列: product_id
    参考表: products
    参考列: id
    严重性: error
    
  - name: 新鲜度
    列: updated_at
    规则: max_age_hours
    值: 24
    严重性: warning
```

### 质量指标仪表盘

```
数据质量报告 - ${date}
═══════════════════════════════════════
处理记录总数: 1,250,000
通过验证:       1,247,500 (99.8%)
验证失败:           2,500 (0.2%)

按类型的问题:
┌─────────────────┬────────┬──────────┐
│ 问题类型      │ 计数  │ 严重性 │
├─────────────────┼────────┼──────────┤
│ 空值         │ 1,200  │ Warning  │
│ 无效格式  │   850  │ Error    │
│ 超出范围    │   300  │ Warning  │
│ 重复值      │   150  │ Error    │
└─────────────────┴────────┴──────────┘
```

## 监控与告警

### 管道指标

```yaml
metrics:
  - name: pipeline_duration
    类型: gauge
    标签: [pipeline_name, status]
    
  - name: records_processed
    类型: counter
    标签: [pipeline_name, source, destination]
    
  - name: error_count
    类型: counter
    标签: [pipeline_name, error_type]
    
  - name: data_freshness
    类型: gauge
    标签: [table_name]
```

### 告警配置

```yaml
alerts:
  - name: pipeline_failed
    条件: status == 'failed'
    渠道: [pagerduty, slack]
    
  - name: high_error_rate
    条件: error_rate > 0.05
    渠道: [slack]
    
  - name: slow_pipeline
    条件: duration > 2 * avg_duration
    渠道: [slack]
    
  - name: data_freshness
    条件: freshness_hours > 24
    渠道: [email]
```

## 最佳实践

1. **增量加载**: 尽可能使用增量提取
2. **幂等性**: 确保管道可以安全地重新运行
3. **分区**: 按日期分区大表
4. **监控**: 跟踪管道健康指标
5. **文档**: 记录所有转换
6. **测试**: 在生产前使用样本数据进行测试
7. **版本控制**: 在git中跟踪管道变更
