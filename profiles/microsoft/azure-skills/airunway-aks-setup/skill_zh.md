# AI Runway AKS 设置

该技能引导用户从裸 Kubernetes 集群部署到正在运行的 AI 模型部署。请按顺序执行每个步骤，除非用户提供了 `skip-to-step N` 以从特定阶段继续。

> **成本意识：** GPU 节点池会产生显著的算力费用（A100-80GB 每小时可能成本为 3–5 美元以上）。在配置 GPU 资源之前，请确认用户了解相关成本影响。

## 前提条件

该技能假定已存在 AKS 集群。如果用户没有集群，请首先引导至 `azure-kubernetes` 技能进行集群配置（需配置 GPU 节点池，除非仅支持 CPU 推理即可接受），然后返回此处。

## 快速参考

| 属性 | 值 |
|----------|------|
| 适用场景 | AKS 端到端 AI Runway 上手配置 |
| CLI 工具 | `kubectl`、`make`、`curl` |
| MCP 工具 | 无 |
| 相关技能 | `azure-kubernetes`（集群配置）、`azure-diagnostics`（故障排查） |

## 何时使用此技能

当用户需要以下操作时，使用此技能：
- 从零开始在现有 AKS 集群上配置 AI Runway
- 安装 AI Runway 控制器和 CRDs
- 评估模型部署的 GPU 硬件兼容性
- 选择并安装推理提供商（KAITO、Dynamo、KubeRay）
- 通过 AI Runway 将首个 AI 模型部署到 AKS
- 从特定步骤恢复部分完成的 AI Runway 设置

## MCP 工具

该技能不使用 MCP 工具。所有集群操作均通过 `kubectl` 和 `make` 直接执行。

## 规则

1. 按顺序执行步骤——到达每一步时加载对应参考文档
2. 在每一步报告集群状态：✓ 正常，✗ 缺失/失败
3. 在进行任何安装或部署操作前，先询问用户确认
4. 如果某步骤已完成，报告状态并跳至下一步
5. 如果用户提供 `skip-to-step N`，从第 N 步开始；假设之前步骤已完成

## 步骤

| # | 步骤 | 参考文档 |
|---|------|-----------|
| 1 | **集群验证** — 上下文检查、节点清单、GPU 检测 | [step-1-verify.md](references/steps/step-1-verify.md) |
| 2 | **控制器安装** — CRD + 控制器部署 | [step-2-controller.md](references/steps/step-2-controller.md) |
| 3 | **GPU 评估** — 检测 GPU 型号、标记 dtype/attention 限制 | [step-3-gpu.md](references/steps/step-3-gpu.md) |
| 4 | **提供商配置** — 推荐并安装推理提供商 | [step-4-provider.md](references/steps/step-4-provider.md) |
| 5 | **首次部署** — 选择模型、部署、验证 Ready 状态 | [step-5-deploy.md](references/steps/step-5-deploy.md) |
| 6 | **总结** — 回顾、冒烟测试、后续步骤 | [step-6-summary.md](references/steps/step-6-summary.md) |

## 错误处理

| 错误/症状 | 可能原因 | 修复方案 |
|-----------------|--------------|-------------|
| 无 kubeconfig 上下文 | 未连接到集群 | 运行 `az aks get-credentials` 或等效命令 |
| 控制器处于 CrashLoopBackOff | 配置或 RBAC 问题 | 执行 `kubectl logs -n airunway-system -l control-plane=controller-manager --previous` |
| 提供商未就绪 | 镜像拉取或 RBAC 问题 | 执行 `<提供商 Pod 名称>` 所在命名空间的 `kubectl logs <pod-name> -n <namespace>` |
| ModelDeployment 卡在 Pending 状态 | GPU 调度失败或提供商未就绪 | 执行 `kubectl describe modeldeployment <name> -n <namespace>` 事件 |
| 推理时出现 `bfloat16` 错误 | T4 或 V100 不支持 bfloat16 | 向 serving 参数添加 `--dtype float16` |

如需完整的错误处理和回滚流程，请参阅 [troubleshooting.md](references/troubleshooting.md)。
