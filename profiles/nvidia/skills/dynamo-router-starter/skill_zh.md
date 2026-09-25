# Dynamo 路由器入门指南

<!--
SPDX-文件版权声明: 版权所有 (c) 2026 NVIDIA CORPORATION & AFFILIATES. 保留所有权利。
SPDX-许可证标识符: CC-BY-4.0
-->

## 目的

通过运行基准路由模式，在适当的情况下启用 KV 感知路由，并验证端点是否正常工作，使 Dynamo 路由变得简单。让用户专注于精确命令和成功信号，而不是路由器内部细节。

## 前置条件

- Python 3.10+，且可导入 `dynamo` 包（`python3 -m dynamo.frontend --help` 命令可用）。
- 对于 Kubernetes 运行：已配置 `kubectl`，可访问目标命名空间，且已部署 Dynamo 配方。
- 网络可达前端服务（通过端口转发或直接访问）。
- 至少有一个工作节点已加载模型（`/v1/models` 返回至少一个条目）。

## 必需输入

收集或推断：

- 本地 Python/CLI 或 Kubernetes 配方路径
- 所需模式：`round-robin`（轮询）、`kv`（KV 感知）、`least-loaded`（最少负载）、`device-aware-weighted`（设备感知加权）、`direct`（直接）或 `random`（随机）
- 前端端口或 Kubernetes 前端服务
- 工作节点是否发布 KV 事件；如果没有，则使用近似 KV 模式
- 用于冒烟测试的模型名称，如果 `/v1/models` 无法发现

## 操作说明

### 1. 建立基准

对于已注册工作节点的本地启动：

```bash
python3 -m dynamo.frontend --router-mode round-robin --http-port 8000
```

对于 Kubernetes，检查所选配方 `deploy.yaml` 并定位前端服务。如果配方尚未部署，请先使用 `dynamo-recipe-runner`。

### 2. 启用 KV 路由

对于本地前端：

```bash
python3 -m dynamo.frontend --router-mode kv --http-port 8000
```

对于 Kubernetes，仅修改前端服务环境变量：

```yaml
envs:
  - name: DYN_ROUTER_MODE
    value: kv
```

如果后端工作节点未发布 KV 缓存事件，则设置为近似模式，而不是让路由器等待事件：

```yaml
envs:
  - name: DYN_ROUTER_USE_KV_EVENTS
    value: "false"
```

### 3. 冒烟测试

在端口转发前端服务或启动本地前端后，运行：

```bash
python3 scripts/check_router_health.py \
  --base-url http://127.0.0.1:8000
```

这必须验证 `/v1/models`，并在模型可发现时，执行一个 `/v1/chat/completions` 请求。

### 4. 仔细比较模式

在比较轮询与 KV 路由时：

- 使用相同的模型、工作节点、提示集、并发性和采样设置
- 如果演示 KV 重用，请发送重复前缀提示
- 除非收集了足够的基准样本，否则将结果标记为冒烟比较
- 不要声称单个聊天请求带来的吞吐量提升

如果端点不健康或工作节点缺失，请切换到 `dynamo-troubleshoot`。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/check_router_health.py` | 对 Dynamo 前端进行 `/v1/models` 和一个聊天完成的冒烟测试 | `--base-url`, `--retries`, `--timeout` |

通过 agentskills.io 的 `run_script()` 协议调用：

```python
run_script("scripts/check_router_health.py", args=["--base-url", "http://127.0.0.1:8000"])
```

## 示例

在端口 8000 上本地 KV 路由前端，然后进行冒烟测试：

```bash
python3 -m dynamo.frontend --router-mode kv --http-port 8000 &
python3 scripts/check_router_health.py --base-url http://127.0.0.1:8000
```

通过端口转发可访问的 Kubernetes 部署前端：

```bash
kubectl port-forward svc/qwen-vllm-disagg-frontend 8000:8000 -n dynamo-demo &
python3 scripts/check_router_health.py --base-url http://127.0.0.1:8000 --retries 3
```

通过代理协议等效调用：

```python
run_script("scripts/check_router_health.py", args=["--base-url", "http://127.0.0.1:8000", "--retries", "3"])
```

## 输出约定

返回：

- 所选模式和原因
- 本地命令或 Kubernetes 环境补丁
- 前端服务或 URL
- 冒烟测试结果
- 任何限制，如近似 KV 模式或缺失工作节点 KV 事件
- 下一步命令以进行更全面的比较

## 限制

- 冒烟测试是一个聊天完成；它不是基准测试。使用 `dynamo-benchmark` 获取吞吐量/延迟数据。
- 没有 worker 发布 KV 事件时，KV 感知模式会降级为近似模式；此技能会标记但不会修复底层的 worker 配置。
- 模式比较需要匹配的工作负载；跨模式延迟声明需要单独的基准测试运行。

## 故障排除

| 症状 | 可能原因 | 下一步 |
|---|---|---|
| `/v1/models` 返回空列表 | 没有工作节点注册到前端 | 验证工作节点 Pod 是否 Ready；确认它们连接到相同的 etcd/NATS |
| 冒烟聊天请求超时 | 前端运行，但工作节点未服务 | 切换到 `dynamo-troubleshoot`；检查工作节点日志 |
| KV 模式卡住 | 工作节点未发布 KV 缓存事件 | 设置 `DYN_ROUTER_USE_KV_EVENTS=false`（近似模式） |
| 端口转发时连接被拒绝 | 端口转发丢失或服务名称错误 | 重新运行端口转发；确认前端服务名称与配方匹配 |

## 基准测试

参考 `BENCHMARK.md` 获取 NVCARPS-EVAL 性能报告（由 NVSkills CI 管道自动生成）。要刷新，请在触及此技能的上游 PR 上重新运行 `/nvskills-ci`。

## 参考

- 阅读 `references/router-modes.md` 了解紧凑的模式/环境映射。
- 使用 `scripts/check_router_health.py` 进行端点冒烟测试。
