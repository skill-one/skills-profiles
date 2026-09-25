# GKE 负载扩展

本技能提供在 Google Kubernetes Engine (GKE) 上扩展应用程序的工作流程和最佳实践。它涵盖了手动扩展、水平 Pod 自动扩展 (HPA) 和垂直 Pod 自动扩展 (VPA)。

## 工作流程

### 1. 手动扩展

将部署扩展到固定数量的副本。适用于立即手动干预或测试。

**命令：**

```bash
kubectl scale deployment {deployment_name} --replicas={number} -n {namespace}

# 验证扩展事件
kubectl get deployment {deployment_name} -n {namespace}
```

### 2. 水平 Pod 自动扩展 (HPA)

根据观察到的 CPU 利用率、内存利用率或自定义指标自动扩展 Pod 的数量。

**前提条件：**

-   Metrics Server 必须正在运行（在 GKE 上默认启用）。
-   容器明确定义资源请求/限制。

**快速命令：**

```bash
kubectl autoscale deployment {deployment_name} --cpu-percent=50 --min=1 --max=10
```

**声明式方法（推荐）：** 使用 YAML 声明式文件进行版本控制的配置。参考 [assets/hpa-example.yaml](assets/hpa-example.yaml) 获取模板。

```bash
kubectl apply -f assets/hpa-example.yaml

# 验证 HPA 是否已创建并正在获取指标
kubectl get hpa
```

**自定义指标和外部指标：** 对于 GKE，基于 Cloud Monitoring 指标（例如 Pub/Sub 队列长度）扩展的现代且推荐的方法是使用 **外部** 指标类型，它由 GKE 控制平面原生支持，而无需 Custom Metrics Adapter。对于通过 Prometheus 暴露的应用程序特定指标，您可以使用 **Google Cloud Managed Service for Prometheus** 或 Prometheus Adapter。

### 3. 垂直 Pod 自动扩展 (VPA)

自动调整您的 Pod 的 CPU 和内存预留，以匹配实际使用情况。这对于正确调整工作负载至关重要。

**前提条件：**

-   集群上必须启用 VPA。
    -   **Autopilot：** 默认启用。
    -   **Standard：** 必须手动启用。

**在 Standard 集群上启用 VPA：**

```bash
gcloud container clusters update {cluster_name} --enable-vertical-pod-autoscaling --zone {zone}
```

**更新模式：**

-   `Off`：计算建议但不应用它们。适用于“干运行”分析。
-   `Initial`：仅在 Pod 创建时分配资源。
-   `Auto`：如果建议与请求差异显著，通过重启运行中的 Pod 来更新它们。
-   `InPlaceOrRecreate`：尝试在不重新创建 Pod 的情况下更新 Pod 资源。如果无法进行原地更新，则切换到 `Auto` 模式（需要 GKE 1.34+）。

**示例：** 参考 [assets/vpa-example.yaml](assets/vpa-example.yaml) 获取配置模板。

## 最佳实践

1.  **定义资源请求：** HPA 和 VPA 依赖于准确的资源请求。始终在容器规范中定义它们。
2.  **避免指标冲突：** 不要配置 HPA 和 VPA 使用相同的指标（例如，CPU）。这会导致资源争用。
    -   *典型模式：* HPA 基于 CPU，VPA 基于 Memory。
3.  **Pod 离线预算 (PDB)：** 定义 PDB 以确保在扩展事件或节点升级期间应用程序的可用性。
4.  **HPA 滞后：** HPA 具有稳定窗口（默认 5 分钟），以防止快速波动。
5.  **VPA "Auto" 模式风险：** 在 "Auto" 模式下，VPA 重启 Pod 以更改资源。确保您的应用程序能够优雅地处理重启（例如，处理 SIGTERM）。
    -   *注意：* 默认情况下，VPA 要求至少 2 个副本才能执行驱逐（以防止唯一运行的副本被驱逐导致停机）。在 GKE 1.22+ 中，您可以通过在 `PodUpdatePolicy` 中设置 `minReplicas` 来覆盖此设置。

## 正确调整工作负载工作流程

1.  以 `Off` 模式部署 VPA 24 小时以上
2.  读取建议：`kubectl describe vpa {deployment_name}-vpa -n {namespace}`
3.  比较 `target` 值与当前 `requests`
4.  带有 20% 缓冲区应用：`new_request = target * 1.2`
5.  使用补丁格式或更新部署声明式文件以应用新的资源请求

条件                     | 建议                       | 风险
----------------------------- | ------------------------------------ | ------
CPU 请求 >5x P95 实际    | 减少至 `P95 * 1.2`                | 中等
内存请求 >3x P95 实际    | 减少至 `P95 * 1.2`                | 中等
CPU 请求 >2x P95 实际    | 正确调整并带有 20% 缓冲区          | 低
未设置资源限制        | 添加限制以防止 noisy-neighbor | 低
