# 概述

该技能支持为华为云 FunctionGraph 函数创建和配置计划触发器（TIMER 类型）。它支持 Quartz Cron 表达式格式，可灵活配置调度策略。

该触发器允许在指定的时间间隔内自动执行无服务器函数，非常适合以下场景：

- 定期数据处理任务
- 计划备份操作
- 常规监控和健康检查
- 基于时间的通知系统

# 前置条件

在使用此技能前，请确保满足以下要求：

1. **Python 环境**：安装 Python 3.9+
2. **SDK 安装**：安装 FunctionGraph SDK：`pip install huaweicloudsdkfunctiongraph`
3. **环境变量**：配置以下环境变量：
   - `HUAWEI_AK`：华为云访问密钥
   - `HUAWEI_SK`：华为云密钥
   - `HUAWEI_REGION`：目标区域（例如 `cn-north-4`）
   - `HUAWEI_PROJECT_ID`：项目 ID
4. **FunctionGraph 函数**：目标函数必须已存在于指定区域
5. **网络访问**：稳定连接到华为云 API 端点

# 使用方法

## 基本命令结构

```bash
cd scripts
python create_trigger.py \
    --function-urn "urn:fss:cn-north-4:project_id:function:default:my-function:latest" \
    --name "daily-trigger" \
    --schedule "0 0 2 * * ?" \
    --schedule-type "Cron" \
    --status "ACTIVE"
```

## 示例

### Cron 表达式触发器

```bash
cd scripts
python create_trigger.py \
    --function-urn "urn:fss:cn-north-4:project_id:function:default:my-function:latest" \
    --name "daily-trigger" \
    --schedule "0 0 8 * * ?" \
    --schedule-type "Cron"
```

### 固定频率触发器

```bash
cd scripts
python create_trigger.py \
    --function-urn "urn:fss:cn-north-4:project_id:function:default:my-function:latest" \
    --name "every-5min" \
    --schedule "5m" \
    --schedule-type "Rate"
```

## Cron 表达式格式

FunctionGraph 使用 **Quartz Cron** 格式，包含 6 或 7 个字段：

```
┌───────────── 秒 (0-59)
│ ┌───────────── 分 (0-59)
│ │ ┌───────────── 小时 (0-23)
│ │ │ ┌───────────── 月份中的日 (1-31)
│ │ │ │ ┌───────────── 月 (1-12)
│ │ │ │ │ ┌───────────── 周中的日 (1-7, 1=星期日)
│ │ │ │ │ │
* * * * * ?
```

有关 Cron 表达式的详细参考，包括特殊字符和常见示例，请参阅 [Cron 表达式参考](./references/cron-reference.md)。

# 参数确认

创建触发器前，请确认以下参数：

| 参数         | 必填 | 描述               | 示例                     |
|--------------|------|--------------------|--------------------------|
| `function_urn` | 是   | 目标函数 URN       | `urn:fss:cn-north-4:xxx:function:default:my-func:latest` |
| `trigger_name` | 是   | 触发器名称（1-64字符） | `daily-trigger`         |
| `schedule`   | 是   | Cron 表达式或 Rate 值 | `0 0 2 * * ?` 或 `5m`   |
| `schedule_type` | 否   | `Cron`（默认）或 `Rate` | `Cron`                  |
| `enable_status` | 否   | `ACTIVE`（默认）或 `DISABLED` | `ACTIVE`                |
| `user_event`  | 否   | 额外的用户事件数据     | `optional info`         |

## 确认清单

- [ ] 函数 URN 正确且函数存在
- [ ] Cron 表达式已验证
- [ ] 触发器名称符合命名规范
- [ ] IAM 权限充足
- [ ] 区域与函数位置匹配

# 输出格式

## 成功响应

```json
{
    "status": "success",
    "trigger_id": "timer-xxx-xxx-xxx",
    "trigger_name": "daily-trigger",
    "trigger_type": "TIMER",
    "schedule": "0 0 2 * * ?",
    "enable_status": "ACTIVE",
    "message": "Trigger created successfully"
}
```

## 错误响应

```json
{
    "status": "failed",
    "error_code": "TriggerAlreadyExists",
    "message": "Trigger with the same name already exists"
}
```

有关完整错误代码和故障排除信息，请参阅 [Cron 表达式参考](./references/cron-reference.md)。

# 验证方法

创建触发器后，验证配置：

## 1. 列出函数触发器

进入 FunctionGraph 控制台 → 函数详情 → 触发器选项卡查看所有触发器

## 2. 检查触发器详情

进入 FunctionGraph 控制台 → 函数详情 → 触发器 → 查看触发器详情

## 3. 监控触发器执行

进入 FunctionGraph 控制台 → 函数详情 → 触发器 → 查看执行历史

预期指标：

- 触发器状态：**Active**
- 下次执行时间：正确计算
- 执行历史：无失败调用

# 最佳实践

## Cron 表达式最佳实践

1. **避免频繁执行**：除非必要，使用间隔 ≥ 5 分钟
2. **考虑时区**：FunctionGraph 默认使用 UTC
3. **使用 `?` 代替未使用的日字段**：月份中的日或周中的日应使用 `?`
4. **创建前验证**：使用在线 Cron 验证器测试表达式

## 命名规范

- 使用描述性名称：`daily-data-sync`，`hourly-health-check`
- 遵循模式：`[频率]-[用途]`
- 最大 64 个字符
- 使用小写和连字符

## 安全注意事项

1. **最小权限**：授予最小的 IAM 权限
2. **启用加密**：使用 KMS 对敏感函数输入进行加密
3. **监控执行**：为失败设置 Cloud Eye 报警
4. **速率限制**：配置适当的重试参数

## 运维建议

1. **测试时使用禁用状态**
2. **在描述字段中记录触发器用途**
3. **设置适当的重试**，处理瞬态失败
4. **启用后监控首次执行**

# 参考文档

有关详细信息，请参阅：

- [SDK 安装指南](./references/sdk-installation-guide.md)
- [IAM 策略](./references/iam-policies.md)
- [验证方法](./references/verification-method.md)
- [验收标准](./references/acceptance-criteria.md)
- [Cron 表达式参考](./references/cron-reference.md)

# 重要说明

## 兼容性说明

该技能设计用于与华为云 FunctionGraph API 兼容。`tags` 字段用于技能发现和分类，`version` 字段遵循语义化版本控制。

## 限制

1. **最大触发器数量**：每个函数默认支持最多 10 个触发器
2. **Cron 精度**：秒级调度可能存在轻微延迟
3. **超时处理**：函数超时应小于触发器间隔
4. **冷启动**：首次执行可能存在额外延迟

## 成本影响

- 触发器配置无额外成本
- 函数调用按调用计费
- 考虑执行频率进行成本优化

## 常见陷阱

1. **时区错误**：记住 FunctionGraph 使用 UTC
2. **重叠调度**：多个触发器可能导致并发执行
3. **长时间运行函数**：确保函数在下次触发前完成
4. **Cron 语法错误**：部署前验证表达式格式

有关故障排除和错误代码，请参阅 [Cron 表达式参考](./references/cron-reference.md)。

---

**相关技能**：

- `huawei-cloud-functiongraph-function-create`
- `huawei-cloud-functiongraph-deploy`
