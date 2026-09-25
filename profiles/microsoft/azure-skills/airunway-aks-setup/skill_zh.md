# AI Runway AKS 设置

此技能将用户从裸 Kubernetes 集群引导至运行中的 AI 模型部署。除非用户提供 `skip-to-step N` 以从特定阶段继续，否则请按顺序遵循每个步骤。

> **成本意识提示：** GPU 节点池会产生显著的计算费用（A100-80GB 每小时可能高达 3-5 美元或更高）。在提供 GPU 资源之前，请确认用户了解成本影响。

## 前置条件

此技能假定已存在 AKS 集群。如果用户没有集群，请先将其转交给 `azure-kubernetes` 技能进行创建（除非仅接受 CPU 推理），然后返回此处。

## 快速参考

| 属性 | 值 |
|------|----|
| 最佳适用场景 | AKS 上的端到端 AI Runway 引导 |
| CLI 工具 | `kubectl`, `make`, `curl` |
| MCP 工具 | 无 |
| 相关技能 | `azure-kubernetes`（集群设置）, `azure-diagnostics`（故障排除） |

## 使用此技能的场景

当用户需要执行以下操作时，请使用此技能：
- 从零开始在现有 AKS 集群上设置 AI Runway
- 安装 AI Runway 控制器和 CRDs
- 评估模型部署的 GPU 硬件兼容性
- 选择并安装推理提供者（KAITO、Dynamo、KubeRay）
- 通过 AI Runway 将第一个 AI 模型部署到 AKS
- 从特定步骤继续部分完成的 AI Runway 设置

## MCP 工具

此技能不使用 MCP 工具。所有集群操作均直接通过 `kubectl` 和 `make` 执行。

## 规则

1. 按顺序执行步骤 — 在达到每个步骤时加载参考
2. 在每个步骤报告集群状态：✓ 健康, ✗ 缺失/失败
3. 在任何安装或部署操作之前请求用户确认
4. 如果步骤已完成，报告状态并跳至下一步
5. 如果用户提供 `skip-to-step N`，则从步骤 N 开始；假定先前的步骤已完成

## 步骤

| # | 步骤 | 参考 |
|---|------|------|
| 1 | **集群验证** — 上下文检查、节点清单、GPU 检测 | [step-1-verify.md](references/steps/step-1-verify.md) |
| 2 | **控制器安装** — CRD + 控制器部署 | [step-2-controller.md](references/steps/step-2-controller.md) |
| 3 | **GPU 评估** — 检测 GPU 型号、标记 dtype/注意力约束 | [step-3-gpu.md](references/steps/step-3-gpu.md) |
| 4 | **提供者设置** — 推荐并安装推理提供者 | [step-4-provider.md](references/steps/step-4-provider.md) |
| 5 | **首次部署** — 选择模型、部署、验证 Ready 状态 | [step-5-deploy.md](references/steps/step-5-deploy.md) |
| 6 | **总结** — 回顾、冒烟测试、后续步骤 | [step-6-summary.md](references/steps/step-6-summary.md) |

## 错误处理

| 错误/症状 | 可能原因 | 解决方法 |
|----------|----------|----------|
| 无 kubeconfig 上下文 | 未连接到集群 | 运行 `az aks get-credentials` 或等效命令 |
| 控制器处于 CrashLoopBackOff 状态 | 配置或 RBAC 问题 | `kubectl logs -n airunway-system -l control-plane=controller-manager --previous` |
| 提供者未就绪 | 镜像拉取或 RBAC 问题 | `kubectl logs <pod-name> -n <namespace>`（针对提供者 Pod） |
| ModelDeployment 卡在 Pending 状态 | GPU 调度失败或提供者未就绪 | `kubectl describe modeldeployment <name> -n <namespace>` 查看事件 |
| 推理时出现 `bfloat16` 错误 | T4 或 V100 缺乏 bfloat16 支持 | 在服务参数中添加 `--dtype float16` |

有关完整的错误处理和回滚流程，请参阅 [troubleshooting.md](references/troubleshooting.md)。
