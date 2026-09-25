# Grafana Cloud 私有连接

> **文档**: https://grafana.com/docs/grafana-cloud/send-data/

将指标、日志、跟踪和配置文件完全通过云提供商的私有骨干网络发送到 Grafana Cloud — 无需暴露公共互联网，无需出口费用。

## 常见工作流程

### 设置 AWS PrivateLink（最常见）

1. **查找服务名称。** Grafana Cloud → 堆栈详情 → "使用 AWS PrivateLink 发送"。为每种信号类型（指标 / 日志 / 跟踪 / 配置文件）记下一个服务名称。

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

**Azure 特定的前提条件:** 在开始之前，请先向 Grafana 支持注册您的订阅 ID — 否则端点创建将挂起在 "Pending" 状态。

## 前提条件（所有提供商）

- Grafana Cloud 堆栈必须托管在相同的云提供商上（检查：我的账户 → 堆栈 → 详情）
- 为每种信号类型（指标 / 日志 / 跟踪 / 配置文件）创建单独的私有端点 — 它们具有不同的服务名称
- 仅限相同区域 AWS PrivateLink。跨区域需要先进行 VPC 对等连接。

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
