---
name: private-connectivity
description: 设置与 Grafana Cloud 的私有网络连接——AWS PrivateLink、Azure Private Link、GCP Private Service Connect 和私有数据源连接（PDC）。根据信号类型（指标/日志/追踪/配置文件）为每个信号类型配置 VPC 端点、私有端点或 PSC 转发规则；将 Alloy 连接到私有 DNS 端点而不是公共端点；验证私有 DNS 解析和端点审批状态。在将遥测数据发送到 Grafana Cloud 而不经过公共互联网时使用，消除云出口成本，满足 PCI-DSS / HIPAA / 数据驻留合规要求，配置 PDC 以进行私有数据源查询，或连接 AWS / Azure / GCP 工作负载到 Grafana——即使用户说“停止支付出口费用”、“将遥测数据保留在公共互联网之外”，或“Grafana 的 PCI 合规”而不提及 PrivateLink。
---

# Grafana Cloud 私有连接

> **文档**: https://grafana.com/docs/grafana-cloud/send-data/

将指标、日志、追踪和配置文件完全通过云服务提供商的私有骨干网络发送到 Grafana Cloud — 无需暴露公共互联网，无需出口费用。

## 常见工作流程

### 设置 AWS PrivateLink（最常见）

1. **查找服务名称。** Grafana Cloud → 堆栈详情 → "使用 AWS PrivateLink 发送"。为每种信号类型（指标 / 日志 / 追踪 / 配置文件）记下一个服务名称。

2. **为每种信号类型创建一个接口 VPC 端点:**

   ```bash
   aws ec2 create-vpc-endpoint \
     --vpc-id vpc-12345 \
     --service-name com.amazonaws.vpce.us-east-1.vpce-svc-0abc123 \
     --vpc-endpoint-type Interface \
     --subnet-ids subnet-12345 \
     --security-group-ids sg-12345 \
     --private-dns-enabled
   ```

3. **验证私有 DNS 解析**（关键 — 如果返回公共 IP，Alloy 将默默继续使用公共路径，并且您将继续支付出口费用）:

   ```bash
   dig +short prometheus-private.us-east-0.grafana.net
   # 预期: 10.x.x.x / 172.16-31.x.x / 192.168.x.x 地址
   # 返回公共 IP → 检查是否设置了 `private_dns_enabled = true`，并且 VPC 已启用 DNS 主机名
   ```

4. **更新 Alloy 以使用私有端点:**

   ```alloy
   prometheus.remote_write "cloud_private" {
     endpoint {
       url = "https://prometheus-private.us-east-0.grafana.net/api/prom/push"
       basic_auth {
         username = sys.env("PROM_USER")
         password = sys.env("GRAFANA_CLOUD_API_KEY")
       }
     }
   }

   loki.write "cloud_private" {
     endpoint {
       url = "https://logs-private.us-east-0.grafana.net/loki/api/v1/push"
       basic_auth {
         username = sys.env("LOKI_USER")
         password = sys.env("GRAFANA_CLOUD_API_KEY")
       }
     }
   }
   ```

5. **确认流量正在通过 PrivateLink 流动:** 检查 Alloy 开始推送后 VPC 端点的 CloudWatch 指标中的 `BytesProcessed`。

完整的 Terraform + 每种信号类型的端点资源在 [references/aws.md](references/aws.md)。

### 设置 Azure Private Link / GCP Private Service Connect

不同的提供商，相同的形式：创建私有端点 → 等待批准 → 验证私有 DNS → 更新 Alloy URL。完整的 CLI + 验证步骤在 [references/azure-gcp.md](references/azure-gcp.md)。

**Azure 特定的前提条件:** 在开始之前，请向 Grafana 支持预先注册您的订阅 ID — 否则端点创建将挂起在 "Pending" 状态。

## 前提条件（所有提供商）

- Grafana Cloud 堆栈必须托管在相同的云提供商上（检查：我的账户 → 堆栈 → 详情）
- 为每种信号类型（指标 / 日志 / 追踪 / 配置文件）创建单独的私有端点 — 它们具有不同的服务名称
- 仅限 AWS PrivateLink 的相同区域。跨区域需要先进行 VPC 对等连接。

## 选择正确的选项

| 场景 | 解决方案 |
|------|----------|
| 从 AWS 推送 | AWS PrivateLink |
| 从 Azure 推送 | Azure Private Link |
| 从 GCP 推送 | GCP Private Service Connect |
| 从 Grafana 查询私有数据库 / Prometheus | 私有数据源连接 (PDC) — 查看 [references/azure-gcp.md § PDC](references/azure-gcp.md#private-data-source-connect-pdc) |

## 参考

- [`references/aws.md`](references/aws.md) — 完整的 AWS PrivateLink Terraform 每种信号类型 + 端点验证（状态 + DNS）
- [`references/azure-gcp.md`](references/azure-gcp.md) — Azure Private Link + GCP Private Service Connect 设置（门户 + CLI）+ 验证 + 私有数据源连接 (PDC) 用于反向方向的私有数据源查询
