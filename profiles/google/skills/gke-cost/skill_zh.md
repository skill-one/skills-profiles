# GKE 成本优化

本指南涵盖在保持黄金路径安全性和可靠性前提下降低 GKE 成本的战略。

> **MCP 工具:** `get_k8s_resource`, `describe_k8s_resource`, `apply_k8s_manifest`, `patch_k8s_resource`, `get_cluster`

## 黄金路径成本特性

黄金路径已包含成本优化设置：

| 设置                  | 值                  | 影响                  |
| ------------------------ | ---------------------- | ----------------------- |
| `autoscalingProfile`     | `OPTIMIZE_UTILIZATION` | 侵略性节点缩放减少空闲计算 |
| `verticalPodAutoscaling` | `enabled`              | VPA 建议             |
| Autopilot 定价        | 按 Pod 请求付费    | 未使用节点容量不收费    |
| 节点自动配置          | 启用                | 自动创建合适规模的节点池 |

## 成本优化策略

### 1. 通过 ComputeClasses 使用 Spot VM

为容错工作负载使用 Spot VM（成本降低 60-90%）。

```yaml
apiVersion: cloud.google.com/v1
kind: ComputeClass
metadata:
  name: spot-with-fallback
spec:
  activeMigration:
    optimizeRulePriority: true
  priorities:
  - machineFamily: n4
    spot: true
  - machineFamily: n4
    spot: false
```

**适合 Spot 的工作负载:**

工作负载                          | 适合 Spot?
--------------------------------- | ---------------
批处理 / 数据处理           | 是
开发 / 测试环境           | 是
无状态 Web/API (副本 >= 2) | 是 (带 PDB)
带检查点的工作          | 是
有状态工作负载 (数据库)    | 否
单副本关键服务          | 否

**处理驱逐:**

```yaml
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 25  # 必须小于 30 秒用于 Spot
      containers:
      - name: app
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 5"]
```

### 1.1 直接工作负载 Spot 选择 (NodeSelector)

对于 GKE Autopilot 中的无状态或批处理工作负载，您无需创建自定义 ComputeClass 即可使用 Spot VM。您可以通过在 Pod 或 Deployment 规范中添加 `nodeSelector` 直接目标内置 Spot 容量。

> [!WARNING] **驱逐警告**: Spot VM 可中断，可随时在 30 秒通知下被驱逐。工作负载必须容错，并至少以 2 个副本运行以实现高可用性。在推荐 Spot VM 时，始终明确告知用户此驱逐风险。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stateless-spot-app
spec:
  replicas: 2
  template:
    spec:
      nodeSelector:
        cloud.google.com/gke-provisioning: Spot
      terminationGracePeriodSeconds: 25  # 必须小于 30 秒以允许在驱逐前优雅关闭
      containers:
      - name: app
        image: <IMAGE>
```

### 2. Pod 尺寸调整

使用 VPA 建议减少过度配置的请求。

```bash
# 1. 以建议模式部署 VPA
kubectl apply -f - <<EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: <DEPLOYMENT>-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: <DEPLOYMENT>
  updatePolicy:
    updateMode: "Off"
EOF

# 2. 等待 24+ 小时收集数据

# 3. 读取建议
kubectl get vpa <DEPLOYMENT>-vpa -o jsonpath='{.status.recommendation}'
```

**优化规则:**

条件                     | 操作                             | 节省
----------------------------- | ---------------------------------- | -------
CPU 请求 >5x P95 实际    | 减少到 `P95 * 1.2`              | 高
内存请求 >3x P95 实际    | 减少到 `P95 * 1.2`              | 高
CPU 请求 >2x P95 实际    | 减少到 `P95 * 1.2`              | 中
未设置资源请求          | 添加请求 (启用二进制打包)        | 中

### 3. 机器类型选择

| 系列        | 用例                                     | 相对成本 |
| ------------- | -------------------------------------------- | ------------- |
| e2            | 通用型，可突发                   | 最低        |
| t2a / t2d     | 扩展 (Arm/AMD)，性价比       | 低           |
| n4a           | Axion Arm 架构，通用型             | 低           |
| n4 / n4d      | 通用型 (Intel/AMD)，灵活形状 | 低-中    |
| c4a           | 计算-优化型 (Arm)，高效率     | 中-高   |
| c3 / c4       | 计算-优化型 (Intel)                    | 中-高   |
| c3d / c4d     | 计算-优化型 (AMD)，高性能    | 中-高   |
| ek-standard   | Autopilot 增强 (黄金路径)             | 中        |
| m3 / x4       | 内存-优化型，SAP HANA，大型数据库  | 高        |
| g2 (L4 GPU)   | AI 推理                                 | 高        |
| a3 (H100 GPU) | AI 训练                                  | 最高       |
| a4 / a4x      | 超级规模 AI (Blackwell GPU)              | 最高       |

> 在 Autopilot 中，机器类型由系统管理。使用 ComputeClasses 影响选择。

### 4. 承诺使用折扣 (CUDs)

对于稳态工作负载，购买 1 年或 3 年 CUDs：

-   1 年：~20-30% 折扣
-   3 年：~50-55% 折扣
-   自动应用于区域中的匹配使用量
-   通过 Google Cloud Console > Billing > Committed use discounts 购买

### 5. 集群管理

-   **停止/启动开发集群**：即使没有工作负载，空闲的开发集群也会产生费用（控制平面费用）。
-   **适当规模的节点池** (标准)：使用 Cluster Autoscaler 并设置合适的 min/max。
-   **多租户集群**：跨团队共享单个集群，而不是每个团队一个集群（参见 `gke-multitenancy` 技能）。

## 成本监控

```bash
# 查看集群成本明细 (需要成本管理 API)
gcloud billing budgets list --billing-account=<BILLING_ACCOUNT> --quiet

# 查看节点利用率
kubectl top nodes

# 查看 Pod 资源使用与请求对比
kubectl top pods --all-namespaces --containers
```

## 开发/测试成本节省

对于非生产环境，以下黄金路径偏差是可以接受的：

| 设置                 | 生产 (黄金路径) | 开发/测试                      |
:                         :              :                               :
| ----------------------- | ------------------ | ----------------------------- |
| 集群模式            | Autopilot          | Autopilot (更少 Pod 更便宜) |
| 发布通道            | Regular            | Rapid (更快获取修复)      |
| 私有节点            | 必须使用           | 可选 (简化访问)             |
| 监控组件            | 完整套件         | SYSTEM_COMPONENTS 只        |
| 密钥管理器轮换       | 120 秒             | 禁用                          |
| 维护窗口            | 配置               | 不需要                        |
