# Dynamo 故障排除

<!--
SPDX-FileCopyrightText: 版权所有 (c) 2026 NVIDIA CORPORATION & AFFILIATES。保留所有权利。
SPDX-License-Identifier: CC-BY-4.0
-->

## 目的

将 Dynamo 故障转化为明确的问题类别、最强信号和下一步操作。从只读证据开始，避免泄露秘密，逐层修复问题。

## 前置条件

- 运行器机器上安装 Python 3.10 或更高版本。
- `kubectl` 配置为对目标命名空间具有读取权限。
- 具有读取 Pod、事件、作业、PVC 和 `DynamoGraphDeployment` 资源（非秘密）的权限。
- 到集群 API 服务器的网络可达性。

## 操作步骤

### 1. 收集只读数据包

运行：

```bash
python3 scripts/collect_dynamo_debug_bundle.py \
  --namespace "${NAMESPACE}"
```

如果用户指定了部署名称，请包含它：

```bash
python3 scripts/collect_dynamo_debug_bundle.py \
  --namespace "${NAMESPACE}" \
  --deployment-name <deployment-name>
```

不要收集 Kubernetes 秘密。不要打印 Hugging Face 令牌。

### 2. 分类故障

使用 `references/failure-decision-tree.md` 并将其分类到一个主要类别：

- 集群/平台
- 命名空间/秘密
- 模型缓存/PVC/下载
- 镜像拉取/运行时镜像
- GPU 调度/资源
- 运行器/DynamoGraphDeployment 合并
- 前端/路由器
- 工作节点/后端
- 端点/API
- 基准测试/性能作业

### 3. 自顶向下调试

按此顺序检查：

1. 命名空间、存储类、GPU 节点和 HF 秘密的存在
2. PVC 和模型下载作业
3. `DynamoGraphDeployment` 状态和事件
4. Pod 状态、`describe pod` 和容器日志
5. 前端服务和端口转发
6. `/v1/models`
7. `/v1/chat/completions`
8. 仅在端点冒烟测试通过后运行基准测试作业

### 4. 逐层修复

优先选择最小且可逆的更改：

- 创建缺失的命名空间或 HF 秘密
- 修补 `storageClassName`
- 修补镜像标签或镜像拉取秘密
- 仅当配方仍然有效时减少 GPU 请求
- 仅当工作节点不发布事件时将 KV 路由器切换到近似模式
- 修复底层配置后重新启动失败的作业

每次修复后，在深入之前重新运行相关就绪检查。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/collect_dynamo_debug_bundle.py` | 收集只读调试数据包（Pod、事件、作业、PVC、CR 状态） | `--namespace`, `--deployment-name`, `--output-dir` |

通过 agentskills.io 的 `run_script()` 协议调用：

```python
run_script("scripts/collect_dynamo_debug_bundle.py", args=["--namespace", "dynamo-demo"])
```

## 示例

收集命名空间中的所有内容以进行故障排除：

```bash
python3 scripts/collect_dynamo_debug_bundle.py --namespace dynamo-demo
```

范围到单个失败的部署：

```bash
python3 scripts/collect_dynamo_debug_bundle.py \
  --namespace dynamo-demo \
  --deployment-name qwen-vllm-disagg
```

通过代理协议等效：

```python
run_script("scripts/collect_dynamo_debug_bundle.py", args=["--namespace", "dynamo-demo", "--deployment-name", "qwen-vllm-disagg"])
```

## 输出约定

返回：

- 问题类别
- 检查的证据
- 最强信号
- 可能的原因
- 精确的下一步命令或修补
- 已排除的内容
- 是否可以继续部署或基准测试

## 限制

- 只读。永远不会修改集群；返回修复命令，而不是执行。
- 不会收集秘密或打印 Hugging Face 令牌；某些故障模式（认证）可能需要用户端检查。
- 数据包大小随部署大小增长；在非常大的命名空间上，使用 `--deployment-name` 进行范围限制。
- 不验证 disagg 传输 — 使用 `dynamo-interconnect-check` 进行该操作。

## 故障排除

| 症状 | 可能的原因 | 下一步 |
|---|---|---|
| `kubectl` 返回 Forbidden 在事件/Pod 上 | 服务账户缺乏读取 RBAC | 请求运行器在命名空间上提供只读角色绑定 |
| 数据包缺少 `DynamoGraphDeployment` 状态 | 运行器未安装或不同命名空间 | 验证 `dynamo-platform` 运行器是否安装并监视该命名空间 |
| 模型下载作业处于 `Pending` 状态 | PVC 未绑定或 HF 秘密缺失 | 修复 PVC 绑定或创建命名 HF 秘密，然后重新运行作业 |
| 工作节点 `CrashLoopBackOff` | 镜像/运行时不匹配或 GPU 不可用 | 检查容器日志；检查节点上的 `nvidia.com/gpu` 可分配 |

## 基准测试

参考 `BENCHMARK.md` 获取 NVCARPS-EVAL 性能报告（由 NVSkills CI 管道自动生成）。要刷新，请在触及此技能的上游 PR 上重新运行 `/nvskills-ci`。

## 参考

- 阅读 `references/failure-decision-tree.md` 获取特定类别的检查。
- 使用 `scripts/collect_dynamo_debug_bundle.py` 进行只读数据包收集。
