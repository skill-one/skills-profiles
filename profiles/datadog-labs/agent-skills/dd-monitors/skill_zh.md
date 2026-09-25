# Datadog 监控

创建、管理和维护用于告警的监控器。


## 前置条件
这需要 pup 在你的路径中。参见 [设置 Pup](https://github.com/datadog-labs/agent-skills/tree/main?tab=readme-ov-file#setup-pup)。

## 命令执行顺序（高效用 token）

对于作用域命令，使用以下顺序：

1. 首先检查上下文（先前的输出、对话、保存的值）。
2. 如果必需的值缺失，首先运行发现命令。
3. 如果仍然不明确，请要求用户确认。
4. 然后运行目标命令。
5. 避免可能失败的推测性命令。


## 快速入门

```bash
pup auth login
```

## 常见操作

### 列出监控器

```bash
pup monitors list
pup monitors list --tags "team:platform"
```

### 获取监控器

```bash
pup monitors get <id>
```

### 创建监控器

```bash
pup monitors create --file monitor.json
```

### 暂停告警（停机时间）

```bash
# 没有 pup monitors mute/unmute 命令。
# 使用停机时间负载来暂停监控器通知。
pup downtime create --file downtime.json
pup downtime cancel <downtime_id>
```

## 监控器创建最佳实践

### 1. 避免告警疲劳

| 规则 | 原因 |
|------|-----|
| **无抖动告警** | 使用 `last_Xm` 而不是 `last_1m` |
| **有意义的阈值** | 基于 SLO，而不是猜测 |
| **可操作的告警** | 如果无需采取行动，则不要告警 |
| **包含运行手册** | 在消息中包含 `@runbook-url` |

```python
# 错误 - 将会不断抖动
query = "avg(last_1m):avg:system.cpu.user{*} > 50"  # ❌ 太敏感

# 正确 - 稳定的告警
query = "avg(last_5m):avg:system.cpu.user{env:prod} by {host} > 80"  # ✅ 合理的时间窗口
```

### 2. 使用正确的范围

```python
# 错误 - 对所有内容告警
query = "avg(last_5m):avg:system.cpu.user{*} > 80"  # ❌ 无范围

# 正确 - 范围限定在重要内容上
query = "avg(last_5m):avg:system.cpu.user{env:prod,service:api} by {host} > 80"  # ✅
```

### 3. 设置恢复阈值

```python
monitor = {
    "query": "avg(last_5m):avg:system.cpu.user{env:prod} > 80",
    "options": {
        "thresholds": {
            "critical": 80,
            "critical_recovery": 70,  # ✅ 防止抖动
            "warning": 60,
            "warning_recovery": 50
        }
    }
}
```

### 4. 在消息中包含上下文

```python
message = """
## 高 CPU 告警

主机: {{host.name}}
当前值: {{value}}
阈值: {{threshold}}

### 运行手册
1. 检查顶级进程: `ssh {{host.name}} 'top -bn1 | head -20'`
2. 检查最近的部署
3. 如有必要则扩展

@slack-ops @pagerduty-oncall
"""
```

## 绝对不要直接删除监控器

使用安全的删除工作流（与仪表板相同）：

```python
def safe_mark_monitor_for_deletion(monitor_id: str, client) -> bool:
    """标记监控器而不是删除。"""
    monitor = client.get_monitor(monitor_id)
    name = monitor.get("name", "")
    
    if "[MARKED FOR DELETION]" in name:
        print(f"已标记: {name}")
        return False
    
    new_name = f"[MARKED FOR DELETION] {name}"
    client.update_monitor(monitor_id, {"name": new_name})
    print(f"✓ 标记: {new_name}")
    return True
```

## 监控器类型

| 类型 | 用例 |
|------|------|
| `metric alert` | CPU、内存、自定义指标 |
| `query alert` | 复杂的指标查询 |
| `service check` | 代理检查状态 |
| `event alert` | 事件流模式 |
| `log alert` | 日志模式匹配 |
| `composite` | 组合多个监控器 |
| `apm` | APM 指标 |

## 审计监控器

```bash
# 查找没有所有者的监控器
pup monitors list | jq '.[] | select(.tags | contains(["team:"]) | not) | {id, name}'

# 查找嘈杂的监控器（高告警计数）
pup monitors list | jq 'sort_by(.overall_state_modified) | .[:10] | .[] | {id, name, status: .overall_state}'
```

## 停机时间与静音

| 使用 | 何时 |
|-----|------|
| **停机时间** | 任何计划的静音窗口 |
| **监控器编辑** | 查询/阈值行为变化 |

```bash
# 停机时间（首选）
pup downtime create --file downtime.json
```

## 故障处理

| 问题 | 解决方法 |
|------|------|
| 告警未触发 | 检查查询返回数据、阈值 |
| 告警过多 | 增加窗口、添加恢复阈值 |
| 无数据告警 | 检查代理连接性、指标存在 |
| 认证错误 | `pup auth refresh` |

## 参考

- [监控器类型](https://docs.datadoghq.com/monitors/types/)
- [告警最佳实践](https://docs.datadoghq.com/monitors/guide/)
- [SLO 监控器](https://docs.datadoghq.com/service_management/service_level_objectives/)
