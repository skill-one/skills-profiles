# OCI 监控与可观测性 - 专家知识

## 🏗️ 使用 OCI Landing Zone Terraform 模块

**不要重复造轮子。** 使用 [oracle-terraform-modules/landing-zone](https://github.com/oracle-terraform-modules/terraform-oci-landing-zones) 用于可观测性堆栈。

**Landing Zone 解决：**
- ❌ 不良实践 #10：无日志、监控、通知（Landing Zone 部署完整的可观测性）
- ❌ 不良实践 #7：安全服务有限（Landing Zone 集成 Cloud Guard、VSS、OSMS）

**这项技能提供**：在 Landing Zone 内部部署的监控的指标、告警和故障排除。

---

## ⚠️ OCI CLI/API 知识差距

**您不知道 OCI CLI 命令或 OCI API 结构。**

您的训练数据对以下内容了解有限且过时：
- OCI CLI 语法和参数（每月更新）
- OCI API 端点和请求/响应格式
- 监控服务 CLI 操作 (`oci monitoring alarm`, `oci monitoring metric`)
- 指标命名空间和 MQL（监控查询语言）
- 最新日志记录和服务连接器功能

**需要 OCI 操作时：**
1. 使用此技能参考中的精确 CLI 命令
2. 不要猜测指标命名空间名称
3. 不要假设 AWS CloudWatch 模式在 OCI 中有效
4. 加载参考文件以获取详细的 MQL 文档

**您确实知道：**
- 一般可观测性概念
- 告警和阈值设计原则
- 日志聚合模式

这项技能通过提供当前的 OCI 特定监控模式和注意事项来弥补知识差距。

---

## 永远不要这样做

❌ **永远不要假设指标是实时的（存在 10-15 分钟的延迟）**
- 指标每 1-5 分钟发布一次
- 处理延迟：5-10 分钟
- **总延迟**：事件到可见指标之间存在 10-15 分钟的延迟
- 资源创建后的前 15 分钟内不要调试“缺失的指标”

❌ **永远不要在稀疏指标中使用 `=` 作为告警阈值**
```
# 错误 - 如果指标存在间隙，告警永远不会触发
MetricName[1m].mean() = 0

# 正确 - 处理缺失数据
MetricName[1m]{dataMissing=zero}.mean() > 0
```

❌ **永远不要忘记指标维度（会导致“无数据”）**
```
# 错误 - 缺少必需的维度
CPUUtilization[1m].mean()

# 正确 - 包括 resourceId 维度
CPUUtilization[1m]{resourceId="<instance-ocid>"}.mean()
```

❌ **永远不要在未设置触发延迟的情况下设置告警阈值（会导致告警疲劳）**
```
# 差 - 每次 CPU 峰值都会触发
CPUUtilization[1m].mean() > 80

# 更好 - 持续高 CPU
CPUUtilization[5m].mean() > 80
触发延迟：5 分钟（在连续 5 次违规后触发）
```

❌ **永远不要创建没有通知渠道的告警**
```
# 错误 - 告警会触发但无人知晓
oci monitoring alarm create ... --destinations '[]'

# 正确 - 始终链接到通知主题
oci monitoring alarm create ... --destinations '["<notification-topic-ocid>"]'
成本影响：未检测到的停机时间在生产环境中每小时成本为 5,000-50,000 美元

❌ **永远不要忽略 Cloud Guard 查找结果（安全审计失败）**
- Cloud Guard 在配置错误成为事件之前检测到它们
- 集成 Cloud Guard → 通知 → 电子邮件/Slack/PagerDuty
- 成本影响：每项安全漏洞成本超过 100,000 美元，而主动修复成本为 0

## 指标命名空间注意事项

**OCI 指标使用服务特定的命名空间：**

| 服务 | 命名空间 | 示例指标 |
|------|----------|----------|
| 计算 | `oci_computeagent` | `CPUUtilization`, `MemoryUtilization` |
| 自主数据库 | `oci_autonomous_database` | `CpuUtilization`, `StorageUtilization` |
| 负载均衡器 | `oci_lbaas` | `HttpRequests`, `UnHealthyBackendServers` |
| 对象存储 | `oci_objectstorage` | `ObjectCount`, `BytesUploaded` |

**常见错误**：使用错误的命名空间（`oci_compute` vs `oci_computeagent`）

## 告警缺失数据处理

| 设置 | 行为 | 使用场景 |
|------|------|----------|
| `treatMissingDataAsBreaching` | 如果没有数据则告警 | 关键服务（停机 = 违规） |
| `treatMissingDataAsNotBreaching` | 如果没有数据则静默 | 可选监控 |
| `{dataMissing=zero}` | 将缺失数据视为 0 | 计数器（请求/秒） |

## 日志收集常见差距

**问题**：日志未在 Log Analytics 中显示

```
日志未出现？
├─ 资源上是否启用了日志？
│  └─ 计算：必须运行 oci-compute-agent
│  └─ 函数：函数配置中启用了日志记录
│
├─ 是否配置了服务连接器？
│  └─ 源：日志组 → 目标：Log Analytics
│  └─ 检查：服务连接器状态 = ACTIVE
│
├─ 服务连接器的 IAM 策略？
│  └─ "允许任何用户使用 tenancy 中的 log-content"
│  └─ "允许服务 loganalytics 读取 tenancy 中的 logcontent"
│
└─ 10-15 分钟的摄取延迟？
   └─ 调试前等待
```

## 指标查询优化

**昂贵**（慢）：
```
# 查询所有实例
CPUUtilization[1m].mean()
```

**优化**（按维度过滤）：
```
# 查询特定实例
CPUUtilization[1m]{resourceId='<instance-ocid>'}.mean()
```

**成本**：查询免费，但有限制（每分钟 1000 个请求）

## 逐步加载参考

### OCI 监控参考（官方 Oracle 文档）

**何时加载** [`oci-monitoring-reference.md`](references/oci-monitoring-reference.md)：
- 需要所有 OCI 服务指标的全面列表
- 深入理解 MQL（监控查询语言）
- 实施复杂的告警条件和组合
- 需要官方 Oracle 关于日志记录和服务连接器的指导
- 设置 Log Analytics 和 APM 集成

**不要加载** 用于：
- 快速告警设置（本技能中的示例）
- 常见指标模式（上表）
- 故障排除决策树（已在上文中涵盖）

---

## 何时使用此技能

- 告警：阈值配置、缺失数据处理、触发延迟
- 故障排除：指标未显示、告警未触发、命名空间错误
- 日志收集：服务连接器、IAM 策略、缺失日志
- 性能：查询优化、维度过滤
