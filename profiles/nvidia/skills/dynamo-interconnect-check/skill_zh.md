# Dynamo 互连检查

<!--
SPDX-文件版权声明: 版权所有 (c) 2026 NVIDIA 公司及关联公司。保留所有权利。
SPDX-许可证标识符: CC-BY-4.0
-->

## 目的

确认传输解耦服务确实有效。部署可以通过端点冒烟测试，但 disagg 可能处于静默错误状态：如果 NIXL/UCX 无法通过 RDMA 或 NVLink 到达对等工作节点，KV 传输会回退到慢速或损坏的路径。在信任 disagg 部署或其基准数据之前，通过只读检查来捕获这些问题。

这项技能是只读的。它永远不会修改集群，也永远不会打印机密信息。

## 前置条件

- 运行在操作员机器上的 Python 3.10+
- 对目标 Dynamo 部署中工作节点 Pod 的 `kubectl exec` 访问权限
- 对配方目录的读取权限 (`recipes/<model>/<framework>/<mode>`)
- 对于节点能力检查：工作节点 Pod 镜像中提供 `ibstat`、`nvidia-smi`、`lsmod` 等工具（缺少工具报告为 `skipped`，而不是失败）

## 使用场景

- `dynamo-recipe-runner` 部署 **disagg** 或多节点配方后
- 在报告 disagg 吞吐量/延迟之前，以确保数据反映真实的传输
- 当聚合工作正常但 disagg 运行缓慢、挂起或返回错误输出，并且你怀疑是网络而不是模型时

对于诊断已经崩溃或无法调度的 Pod，请首先使用 `dynamo-troubleshoot`。

## 说明

### 1. 检查配方上的传输环境变量

```bash
python3 scripts/check_interconnect.py env recipes/<model>/<framework>/<mode>
```

报告哪些 NIXL/UCX/NCCL 传输变量已设置，并标记 disagg-critical 的变量（例如 `UCX_TLS`、`UCX_NET_DEVICES`、`NCCL_IB_HCA`）缺失。这里缺失只是一个警告——它们可能已嵌入镜像中——因此需要与节点和 NIXL 检查确认。有关每个变量的作用，请参阅 `references/interconnect-env-vars.md`。

### 2. 检查节点能力

在 GPU 节点上本地执行，或在运行的工作节点 Pod 内：

```bash
python3 scripts/check_interconnect.py node \
  --namespace "${NAMESPACE}" --pod <worker-pod>
```

进行只读探测：InfiniBand 设备和活动链路、GPUDirect RDMA (`nvidia_peermem`)、GDRCopy 和 GPU 架构中的 NVLink。缺少工具报告为 `skipped`，而不是失败。

### 3. 验证 NIXL 可达性

```bash
python3 scripts/check_interconnect.py nixl \
  --namespace "${NAMESPACE}" --pod <worker-pod>
```

在 Pod 中查找 NIXL 测试工具，并显示运行成对预填充↔解码传输测试的确切下一步。完整的跨 Pod 传输测试需要两个在网络上调度的 GPU Pod。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/check_interconnect.py env` | 检查配方上的 NIXL/UCX/NCCL 环境变量 | 位置参数配方路径 |
| `scripts/check_interconnect.py node` | 在节点或 Pod 上探测 InfiniBand、GPUDirect RDMA、GDRCopy、NVLink | `--namespace`、`--pod` |
| `scripts/check_interconnect.py nixl` | 显示 Pod 的 NIXL 传输测试准备情况 | `--namespace`、`--pod` |

通过 agentskills.io 的 `run_script()` 协议调用：

```python
run_script("scripts/check_interconnect.py", args=["env", "recipes/qwen3-coder-480b/sglang/disagg"])
run_script("scripts/check_interconnect.py", args=["node", "--namespace", "dynamo-demo", "--pod", "qwen-worker-0"])
```

## 示例

在部署前验证 disagg 配方的传输环境形状：

```bash
python3 scripts/check_interconnect.py env recipes/qwen3-coder-480b/sglang/disagg
```

部署后，验证工作节点 Pod 的网络：

```bash
python3 scripts/check_interconnect.py node \
  --namespace dynamo-demo --pod qwen-worker-0
python3 scripts/check_interconnect.py nixl \
  --namespace dynamo-demo --pod qwen-worker-0
```

通过代理协议等效：

```python
run_script("scripts/check_interconnect.py", args=["nixl", "--namespace", "dynamo-demo", "--pod", "qwen-worker-0"])
```

## 输出契约

每个检查返回 `ok` / `warn` / `fail` / `skipped` 及一行详细信息，并包含 disagg 传输准备情况的汇总判断。报告：

- 传输环境变量存在与 disagg-critical 缺失的变量
- RDMA / GPUDirect / NVLink 能力状态
- NIXL 可达性是否已验证，以及未验证时的下一步命令
- 清晰声明 disagg 是否可信，或首先需要修复什么

## 限制

- 只读网络探测；不会运行完整的成对 NIXL 传输（需要两个调度的 GPU Pod 和 Pod 内的 NIXL 测试工具）
- 缺少工具 (`ibstat`、`nvidia-smi`、`lsmod`) 的 `skipped` 结果是不确定的，不是通过
- 环境变量检查检查配方文本；未检测到通过 initContainers 或操作员应用的环境注入的值
- 单节点聚合部署不会执行传输——这项技能用于 disagg / 多节点验证

## 故障排除

| 症状 | 可能原因 | 下一步 |
|---|---|---|
| `env` 报告所有 critical 变量缺失 | 变量嵌入镜像或由操作员注入 | 在工作节点 Pod 内运行 `node` 检查以验证实际环境 |
| `node` 报告没有 Active IB 链路 | 网络中断或 HCA 未分配给节点 | 联系集群管理员；验证 `kubectl describe node` 显示 `nvidia.com/gpu` 和 IB 标签 |
| `nvidia_peermem` 缺失 | GPUDirect RDMA 模块未加载 | 要求集群管理员加载 `nvidia-peermem`；没有它，NIXL 回退到分阶段副本 |
| `nixl` 找不到测试工具 | 工作节点镜像缺少 NIXL 测试框架 | 使用 NIXL 支持的镜像或从调试 Pod 运行独立的传输测试 |

## 基准测试

有关 NVCARPS-EVAL 性能报告（由 NVSkills CI 管道自动生成），请参阅 `BENCHMARK.md`。要刷新，请在触及此技能的上游 PR 上重新运行 `/nvskills-ci`。

## 参考

- `references/interconnect-env-vars.md` — NIXL/UCX/NCCL 环境变量目录和 IB 能力检查清单。
- 使用 `scripts/check_interconnect.py` 进行所有只读检查。
