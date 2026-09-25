# GKE AI/ML 推理

本指南涵盖使用 Google 的推理快速入门 (GIQ) 在 GKE 上部署 AI/ML 推理工作负载，以及 LLM 服务的最佳实践。

> **MCP 工具:** `apply_k8s_manifest`, `get_k8s_resource`, `get_k8s_logs`, `get_k8s_rollout_status`, `describe_k8s_resource`, `list_k8s_events`.
> **仅 CLI:** `gcloud container ai profiles *`

## 使用场景

-   将 AI 模型（Llama、Gemma、Mistral 等）部署到 GKE
-   为推理生成优化的 Kubernetes 配置文件
-   为模型服务选择 GPU/TPU 加速器
-   配置 LLM 推理的自动扩展

## 前置条件

-   一个黄金路径 GKE Autopilot 集群（通过 ComputeClasses 和 NAP 支持 GPU 工作负载）
-   `gcloud` CLI 已认证
-   目标区域有足够的 GPU/TPU 配额

## 工作流程

### 1. 探索：查找模型和硬件

```bash
# 列出所有支持的模型
gcloud container ai profiles models list --quiet

# 查找模型的有效加速器/服务器组合
gcloud container ai profiles list --model=<MODEL_NAME> --quiet

# 示例：Gemma 2 9B 可以运行什么？
gcloud container ai profiles list --model=gemma-2-9b-it --quiet
```

### 2. 生成配置文件

```bash
gcloud container ai profiles manifests create \
  --model=<MODEL_NAME> \
  --model-server=<SERVER> \
  --accelerator-type=<ACCELERATOR> \
  --target-ntpot-milliseconds=<NTPOT> --quiet > inference.yaml
```

**参数:**

-   `--model`: 模型 ID（例如，`gemma-2-9b-it`，`llama-3-8b`）
-   `--model-server`: 推理服务器（`vllm`，`tgi`，`triton`，`tensorrt-llm`）
-   `--accelerator-type`: GPU/TPU 类型（`nvidia-l4`，`nvidia-tesla-a100`，`nvidia-h100-80gb`）
-   `--target-ntpot-milliseconds`: 目标每输出令牌标准化时间（可选，用于延迟优化）

**示例:**

```bash
gcloud container ai profiles manifests create \
  --model=gemma-2-9b-it \
  --model-server=vllm \
  --accelerator-type=nvidia-l4 \
  --target-ntpot-milliseconds=50 --quiet > inference.yaml
```

### 3. 审查和部署

```bash
# 审查占位符（HF 令牌、PVC）
cat inference.yaml

# 部署
kubectl apply -f inference.yaml

# 监控
kubectl get pods -w
kubectl logs -f <POD_NAME>
```

> 某些模型需要 Hugging Face 令牌。创建一个 Kubernetes Secret 并在配置文件中引用它。

## 推理的 GPU ComputeClass

对于 Autopilot 集群，创建一个 ComputeClass 以目标 GPU 节点：

```yaml
apiVersion: cloud.google.com/v1
kind: ComputeClass
metadata:
  name: l4-inference
spec:
  priorities:
  - machineFamily: g2
    gpu:
      type: nvidia-l4
      count: 1
    minCores: 4
    minMemoryGb: 16
```

## 加速器选择指南

| 加速器         | 适用于                 | 内存      | 相对成本 |
| -------------- | ---------------------- | --------- | -------- |
| NVIDIA T4      | 预算推理，              | 16 GB     | 最低     |
:               : 轻量级传统模型       :         :         :       :
:               :                     :         :         :       :
| NVIDIA L4 (G2) | 小型-中型模型推理       | 24 GB     | 低       |
:               : 视频，图形             :         :         :       :
| NVIDIA RTX PRO 6000 | 多模态 AI，            | 96 GB     | 中等     |
: (G4)          | 高保真 3D，            :         :         :       :
:               : 微调                  :         :         :       :
| Cloud TPU v5e  | 高性价比               | 可变      | 中等     |
:               : 变换器推理            :         :         :       :
| Cloud TPU v5p  | 高性能                 | 可变      | 高       |
:               : 训练                  :         :         :       :
| Cloud TPU v6e  | 高效率下一代            | 32 GB/芯片 | 中高     |
: (Trillium)    | 训练和推理             :         :         :       :
| Cloud TPU v7x  | 超级规模推理 &          | 192 GB/芯片 | 高       |
: (Ironwood)    | 智能代理工作流          :         :         :       :
| NVIDIA A100    | 大型模型推理，          | 40/80 GB  | 高       |
:               : 企业级 ML            :         :         :       :
| NVIDIA H100 / H200 | 边缘模型训练，          | 80/141 GB | 最高     |
:               : 高吞吐量            :         :         :       :
| NVIDIA B200 (A4) | Blackwell 级别          | 192 GB    | 最高     |
:               : 训练，FP4 精度        :         :         :       :
| NVIDIA GB200 (A4X) | 机架级 AI (Grace        | 巨大      | 最高     |
:               : Blackwell 超级芯片)    :         :         :       :

## 自动扩展 LLM 推理

### 基于 GPU 的自动扩展

使用自定义指标 GPU 利用率：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-server
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: gpu_duty_cycle
      target:
        type: AverageValue
        averageValue: "80"
```

### 推理自动扩展的最佳实践

1.  **使用 DCGM 指标**: 黄金路径启用 GPU 利用率指标的 DCGM 监控
2.  **设置适当的 minReplicas**: 至少 1 用于始终在线服务；0 用于批处理/按需
3.  **调整缩小延迟**: LLM 模型加载缓慢；使用更长的稳定窗口
4.  **考虑队列深度**: 对于延迟敏感工作负载，基于待处理请求而不是纯 GPU 利用率进行扩展

## 优化技巧

-   **量化**: 使用量化模型（GPTQ、AWQ）以减少 GPU 内存并提高吞吐量
-   **批处理**: 配置模型服务器批处理大小以进行吞吐量与延迟的权衡
-   **张量并行**: 将大型模型跨节点内的多个 GPU 分割
-   **KV 缓存优化**: 调整 vLLM 中的 `--gpu-memory-utilization` 以进行 KV 缓存分配

## 故障排除

| 问题              | 原因                    | 解决方法                         |
| ----------------- | ------------------------ | ------------------------------- |
| 无效              | 不支持的组合            | 重新运行 `gcloud container ai |
: 模型/加速器组合  :                          : profiles list               :
:                    :                          : --model=<MODEL>`            :
| GPU 配额超出      | 区域配额限制            | 申请配额增加或尝试不同区域      |
:                    :                          :                           :
| GPU 内存不足      | 模型太大无法适应        | 使用更大的 GPU，启用量化，或使用 :
:                    :                          : 张量并行                 :
:                    :                          :                           :
| 慢冷启动          | 从注册表加载大型模型     | 使用本地 SSD 进行模型缓存；预先拉取 :
:                    :                          : 镜像                     :
