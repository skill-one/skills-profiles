# 数据库同步

全面的数据库同步、复制和数据集成技能。

## 核心架构

### 同步模式

```
数据库同步模式：
┌─────────────────────────────────────────────────────────┐
│                 单向复制                          │
│  ┌──────────┐         ┌──────────┐                      │
│  │  主库  │ ──────▶ │  从库  │                      │
│  └──────────┘         └──────────┘                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 双向同步                          │
│  ┌──────────┐         ┌──────────┐                      │
│  │ 数据库A │ ◀─────▶ │ 数据库B │                      │
│  │    A     │         │    B     │                      │
│  └──────────┘         └──────────┘                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  中心辐射模式                           │
│           ┌──────────┐                                   │
│           │  辐条1  │                                   │
│           └────┬─────┘                                   │
│                │                                         │
│  ┌──────────┐──┴──┌──────────┐                          │
│  │  辐条2  │◀───▶│   中心   │◀────┬──────────┐        │
│  └──────────┘     └──────────┘     │  辐条3  │        │
│                                     └──────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 同步方法

```yaml
sync_methods:
  full_sync:
    description: "完整数据刷新"
    use_when:
      - 初始同步
      - 模式变更
      - 灾难恢复
    considerations:
      - 需要停机时间
      - 资源密集型
      
  incremental_sync:
    description: "仅变更数据"
    tracking_methods:
      - 时间戳 (updated_at)
      - 变更数据捕获 (CDC)
      - 触发器
      - 基于日志
    advantages:
      - 最小化数据传输
      - 近实时
      
  snapshot_sync:
    description: "时间点快照"
    use_when:
      - 分析
      - 报表
      - 备份
```

## 配置

### 源/目标设置

```yaml
sync_config:
  source:
    type: postgresql
    host: "source-db.example.com"
    port: 5432
    database: "production"
    credentials:
      type: secret_manager
      path: "db/source/credentials"
    ssl: required
    
  target:
    type: mysql
    host: "target-db.example.com"
    port: 3306
    database: "analytics"
    credentials:
      type: secret_manager
      path: "db/target/credentials"
    ssl: required
    
  sync_settings:
    mode: incremental
    batch_size: 10000
    parallel_tables: 4
    retry_attempts: 3
    checkpoint_interval: 5_minutes
```

### 表映射

```yaml
table_mappings:
  - source_table: users
    target_table: dim_users
    columns:
      id: user_id
      email: email_address
      created_at: registration_date
      status: user_status
    transformations:
      - column: status
        transform: "UPPER(status)"
      - column: email_address
        transform: "LOWER(email)"
    filters:
      - "status != 'deleted'"
      - "created_at > '2023-01-01'"
    
  - source_table: orders
    target_table: fact_orders
    columns:
      "*": "*"  # 所有列
    exclude_columns:
      - internal_notes
      - deleted_at
    incremental_key: updated_at
```

## 变更数据捕获

### CDC配置

```yaml
cdc_config:
  method: logical_replication  # 或: trigger, polling
  
  postgresql:
    publication: "sync_publication"
    slot: "sync_slot"
    tables:
      - users
      - orders
      - products
      
  change_tracking:
    capture_deletes: true
    capture_before_values: true
    
  output_format:
    type: json
    include:
      - operation
      - timestamp
      - table
      - key
      - before
      - after
```

### CDC事件处理

```yaml
cdc_events:
  example_insert:
    operation: INSERT
    timestamp: "2024-01-15T10:30:00Z"
    table: users
    key: { id: 12345 }
    after:
      id: 12345
      email: "user@example.com"
      status: "active"
      
  example_update:
    operation: UPDATE
    timestamp: "2024-01-15T10:31:00Z"
    table: users
    key: { id: 12345 }
    before:
      status: "active"
    after:
      status: "premium"
      
  example_delete:
    operation: DELETE
    timestamp: "2024-01-15T10:32:00Z"
    table: users
    key: { id: 12345 }
    before:
      id: 12345
      email: "user@example.com"
```

## 冲突解决

### 冲突策略

```yaml
conflict_resolution:
  strategies:
    - name: last_write_wins
      description: "最后写入者胜出"
      resolution: |
        IF source.updated_at > target.updated_at
        THEN use source
        ELSE keep target
        
    - name: source_priority
      description: "源始终优先"
      resolution: "always use source"
      
    - name: merge
      description: "合并非冲突字段"
      resolution: |
        FOR each field:
          IF only_one_changed: use_changed
          IF both_changed: use source.field
          
    - name: custom_rules
      description: "字段特定规则"
      rules:
        - field: quantity
          strategy: sum
        - field: status
          strategy: priority_order
          order: ["active", "pending", "inactive"]
        - field: last_login
          strategy: max
```

### 冲突日志

```yaml
conflict_log:
  format:
    timestamp: "{{time}}"
    table: "{{table}}"
    key: "{{primary_key}}"
    field: "{{conflicting_field}}"
    source_value: "{{source.value}}"
    target_value: "{{target.value}}"
    resolution: "{{applied_strategy}}"
    result: "{{final_value}}"
    
  storage:
    type: table
    name: sync_conflicts
    retention_days: 90
    
  alerting:
    threshold: 100  # 每小时冲突数
    notify: ["slack:#data-alerts"]
```

## 模式管理

### 模式同步

```yaml
schema_sync:
  mode: evolve  # 或: strict, ignore
  
  operations:
    add_column:
      action: apply
      default_value: null
      
    remove_column:
      action: warn
      keep_data: true
      
    modify_type:
      action: review
      safe_changes:
        - varchar_expand
        - int_to_bigint
        
    rename_column:
      action: manual
      create_mapping: true
```

### 迁移脚本

```sql
-- 示例迁移：添加新列
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS 
  loyalty_tier VARCHAR(20) DEFAULT 'bronze';

-- 示例迁移：创建同步跟踪表
CREATE TABLE IF NOT EXISTS _sync_metadata (
  table_name VARCHAR(100) PRIMARY KEY,
  last_sync_at TIMESTAMP,
  last_sync_key VARCHAR(255),
  records_synced BIGINT,
  status VARCHAR(20)
);

-- 示例迁移：添加同步触发器
CREATE OR REPLACE FUNCTION track_changes()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO _change_log (
    table_name, operation, key, changed_at
  ) VALUES (
    TG_TABLE_NAME, TG_OP, NEW.id, NOW()
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## 监控面板

### 同步状态

```
数据库同步状态
═══════════════════════════════════════

总体状态：✓ 健康

源：PostgreSQL (production)
目标：MySQL (analytics)
模式：   增量CDC

表：
┌──────────────┬──────────┬───────────┬──────────┐
│ 表名        │ 状态     │ 滞后       │ 记录数  │
├──────────────┼──────────┼───────────┼──────────┤
│ users        │ ✓ 同步   │ 2s        │ 1.2M     │
│ orders       │ ✓ 同步   │ 5s        │ 8.5M     │
│ products     │ ✓ 同步   │ 1s        │ 50K      │
│ events       │ ⚠ 落后   │ 2m 30s    │ 45M      │
└──────────────┴──────────┴───────────┴──────────┘

吞吐量：
当前：  5,230 条记录/秒
平均：  4,850 条记录/秒
峰值：     12,400 条记录/秒

过去24小时：
同步记录数：45.2M
错误数：         23
冲突数：      156
```

### 指标

```yaml
metrics:
  - name: sync_lag_seconds
    type: gauge
    labels: [table_name, sync_job]
    alert:
      warning: "> 60"
      critical: "> 300"
      
  - name: records_synced_total
    type: counter
    labels: [table_name, operation]
    
  - name: sync_errors_total
    type: counter
    labels: [table_name, error_type]
    
  - name: conflict_count
    type: counter
    labels: [table_name, resolution_strategy]
```

## 集成示例

### PostgreSQL到BigQuery

```yaml
pg_to_bigquery:
  source:
    type: postgresql
    connection: "${PG_CONNECTION_STRING}"
    tables:
      - name: orders
        incremental_key: updated_at
        
  target:
    type: bigquery
    project: "my-project"
    dataset: "analytics"
    
  schedule: "*/5 * * * *"  # 每5分钟
  
  transform:
    - type: add_metadata
      columns:
        _synced_at: "CURRENT_TIMESTAMP()"
        _source: "'production'"
```

### MySQL到Elasticsearch

```yaml
mysql_to_elasticsearch:
  source:
    type: mysql
    tables:
      - products
      
  target:
    type: elasticsearch
    index: products_search
    
  mapping:
    id: _id
    name:
      type: text
      analyzer: standard
    description:
      type: text
      analyzer: english
    category:
      type: keyword
    price:
      type: float
```

## 最佳实践

1. **彻底测试**：验证同步准确性
2. **监控滞后**：告警复制延迟
3. **处理冲突**：定义明确的解决规则
4. **迁移前备份**：保护数据
5. **使用增量同步**：最小化负载
6. **记录所有操作**：保持审计追踪
7. **计划故障**：实现重试逻辑
8. **模式演进**：优雅处理变更
