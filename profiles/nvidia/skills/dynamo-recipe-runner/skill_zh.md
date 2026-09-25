# Dynamo配方运行器

<!--
SPDX-文件版权声明: 版权所有 (c) 2026 NVIDIA 公司及其附属公司。保留所有权利。
SPDX-许可证标识符: CC-BY-4.0
-->

## 目的

将用户意图最小化地转化为可工作的Dynamo配方端点。不要创建新的指南内容。在现有的`recipes/`树中操作，修补最小的必要清单文件，在用户具有集群访问权限时部署，并使用兼容OpenAI的冒烟请求来验证成功。

## 前置条件

- 运行器机器上安装Python 3.10+
- 配置了可工作的集群上下文的`kubectl`
- 集群为模型缓存PVCs提供了默认的存储类
- Hugging Face令牌存储在目标命名空间中名为`hf-token-secret`（或等效）的Kubernetes密钥中
- 对ai-dynamo/dynamo存储库中`recipes/`树的读取访问权限

## 必须的输入

在更改清单文件之前收集或推断这些内容：

- 配方目标：模型、框架（`vllm`、`sglang`、`trtllm`、`tokenspeed`）、部署模式以及GPU类型/数量
- Kubernetes上下文和命名空间
- Hugging Face密钥名称，通常是`hf-token-secret`
- 模型缓存PVCs的存储类
- 如果配方使用占位符或过时的测试镜像，则运行时镜像标签
- 是否运行命令或仅生成确切命令

如果必需的值缺失且无法从选定的配方中推断，则仅请求该值。

## 说明

### 1. 预检查

首先运行只读检查：

```bash
git status --short
python3 scripts/recipe_tool.py list --format table
kubectl config current-context
kubectl get storageclass
kubectl get nodes -o wide
kubectl get namespace "${NAMESPACE}"
kubectl get secret hf-token-secret -n "${NAMESPACE}"
```

如果`kubectl`不可用或集群无法访问，则通过选择和验证配方，然后返回确切命令而不是假装部署运行来继续。

### 2. 选择配方

使用`recipes/README.md`中的配方矩阵和扫描器：

```bash
python3 scripts/recipe_tool.py list \
  --query qwen --framework vllm --mode disagg --format table
```

优先选择确切的现有配方。除非用户明确要求编写新配方，否则不要发明新的清单文件。

### 3. 检查和验证

阅读选定的配方README、模型缓存清单文件、`deploy.yaml`和如果存在的话`perf.yaml`。然后运行：

```bash
python3 scripts/recipe_tool.py validate \
  recipes/<model>/<framework>/<mode>
```

在应用清单文件之前解决报告的障碍：存储类、模型缓存PVC、镜像标签、HF令牌密钥、GPU数量、前端服务名称和路由器模式。

### 4. 补丁最小值

仅修补此运行所需的配方特定值。不要重新格式化整个YAML文件。常见的补丁：

- `storageClassName`
- 镜像仓库/标签
- 模型路径或模型缓存挂载路径
- GPU资源请求/限制
- 前端`DYN_ROUTER_MODE`
- 仅当清单文件硬编码命名空间时才指定命名空间

永远不要将Hugging Face令牌写入文件或日志。使用Kubernetes密钥。

### 5. 部署

当它与默认顺序不同时，请遵循选定的配方README。默认顺序是：

```bash
kubectl apply -f recipes/<model>/model-cache/ -n "${NAMESPACE}"
kubectl wait --for=condition=Complete job/model-download -n "${NAMESPACE}" --timeout=6000s
kubectl apply -f recipes/<model>/<framework>/<mode>/deploy.yaml -n "${NAMESPACE}"
kubectl get dynamographdeployment -n "${NAMESPACE}"
kubectl get pods -n "${NAMESPACE}" -o wide
```

在测试之前等待前端和工作节点准备就绪。

### 6. 冒烟测试

将前端服务端口转发，然后验证`/v1/models`和一个聊天完成：

```bash
kubectl port-forward svc/<deployment-name>-frontend 8000:8000 -n "${NAMESPACE}"
curl http://127.0.0.1:8000/v1/models
```

如果也安装了`dynamo-router-starter`，请优先使用其`scripts/check_router_health.py`进行完整的兼容OpenAI的冒烟测试。如果此测试失败，请切换到`dynamo-troubleshoot`。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/recipe_tool.py list` | 列出可用配方，可选过滤 | `--query`、`--framework`、`--mode`、`--format` |
| `scripts/recipe_tool.py validate` | 在应用之前验证配方目录 | 位置参数配方路径 |

通过agentskills.io的`run_script()`协议调用：

```python
run_script("scripts/recipe_tool.py", args=["list", "--framework", "sglang", "--format", "table"])
run_script("scripts/recipe_tool.py", args=["validate", "recipes/nemotron-3-super-fp8/sglang/agg"])
```

## 示例

列出适合单个8xB200节点的sglang配方：

```bash
python3 scripts/recipe_tool.py list --framework sglang --format table
```

在应用之前验证特定配方并解决障碍：

```bash
python3 scripts/recipe_tool.py validate recipes/nemotron-3-super-fp8/sglang/agg
```

通过代理协议等效：

```python
run_script("scripts/recipe_tool.py", args=["validate", "recipes/nemotron-3-super-fp8/sglang/agg"])
```

## 输出契约

返回：

- 选定的配方路径及其选择原因
- 确切修补的值
- 运行或要运行的命令
- 端点和冒烟测试结果
- 未解决的障碍（如果有）
- 部署未健康时的下一步故障排除步骤

## 限制

- 仅在现有的`recipes/`树中操作。不会编写新的清单文件。
- 修改集群的apply步骤需要`kubectl`对目标命名空间的权限。
- 冒烟测试深度有意最小化；对于完整的路由器/端点覆盖使用`dynamo-router-starter`。
- 多节点disagg传输的正确性不在范围内；部署后使用`dynamo-interconnect-check`。

## 故障排除

| 症状 | 可能的原因 | 下一步 |
|---|---|---|
| `kubectl`集群无法访问 | 上下文未设置或VPN关闭 | 返回运行它们的确切命令；当集群可访问时继续 |
| `validate`报告缺少存储类 | 集群没有默认的`StorageClass` | 在应用之前修补模型缓存清单文件上的`storageClassName` |
| 模型缓存作业卡在`Pending` | PVC未绑定或HF密钥缺失 | 检查PVC事件；创建或重命名HF密钥以匹配配方 |
| 工作节点`ImagePullBackOff` | 过时的镜像标签或缺少拉取密钥 | 补丁镜像标签；验证命名空间中的镜像拉取密钥 |
| 部署后`/v1/models` 4xx/5xx | 前端未准备就绪或服务端口错误 | 等待节点就绪；重新运行端口转发；如果仍然存在，切换到`dynamo-troubleshoot` |

## 基准测试

有关NVCARPS-EVAL性能报告，请参阅`BENCHMARK.md`（由NVSkills CI管道自动生成）。要刷新，请在触及此技能的上游PR上重新运行`/nvskills-ci`。

## 参考

- 阅读`references/k8s-recipe-workflow.md`以获取命令模板和就绪检查。
- 使用`scripts/recipe_tool.py`进行配方发现和轻量级验证。
