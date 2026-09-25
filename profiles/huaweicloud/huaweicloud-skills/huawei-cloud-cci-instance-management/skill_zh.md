# 华为云CCI容器实例生命周期管理

## 概述

使用hcloud CLI（KooCLI）管理华为云CCI（云容器实例）的完整生命周期。CCI是一种无服务器容器服务——无需集群管理，只需创建命名空间，定义网络，然后直接部署工作负载。

**架构**：hcloud CLI → CCI OpenAPI → 命名空间 / 网络 / 部署 / 有状态集 / 容器 / EIPPool / 服务 / Ingress

## 约束和规则

### 安全规则

- **两步确认**：所有破坏性操作（删除命名空间/网络/部署/有状态集/容器/EIPPool）都需要明确用户确认——先预览命令、资源详情和风险警告；用户确认后才能执行。
- **凭证安全**：不要在任何对话、命令或输出中暴露AK/SK值。仅使用`hcloud configure list`检查凭证状态（仅存在性）。优先使用配置文件模式或环境变量，而不是显式AK/SK参数。

### 资源约束

- **命名空间风味注解是强制的**：每个命名空间都必须带有`namespace-kubernetes-io/flavor`注解（值：`general-computing`或`gpu-accelerated`）。否则，创建会失败。
- **limits必须等于requests**：CCI强制`resources.limits == resources.requests`。不匹配会导致"limit and request doesn't equal"错误。将两者设置为相同的值（例如，`500m/1Gi`）。
- **网络必须先于工作负载**：如果命名空间中不存在网络，Pod/部署/有状态集创建会失败或保持Pending状态。始终先创建网络，然后再部署工作负载。
- **VPC CIDR限制**：VPC子网CIDR不能是`10.247.0.0/16`——CCI保留此范围用于服务网络。使用它会导致IP冲突和工作负载创建失败。
- **删除顺序**：容器 → 部署/有状态集 → EIPPool → 网络 → 命名空间。删除命名空间会级联删除其下所有资源。

### hcloud CLI约束

- **网络创建必须使用Python辅助脚本**：hcloud CLI无法传递包含点的注解键（`network.alpha.kubernetes.io/default-security-group`）。点表示法或`--cli-jsonInput`都不起作用。使用`scripts/cci_network_helper.py`。
- **命名空间注解使用连字符替换**：像`namespace.kubernetes.io/flavor`这样的键可以使用连字符（`namespace-kubernetes-io/flavor`），CCI会自动规范化。此解决方案仅适用于命名空间，不适用于网络。
- **始终使用`--help`验证参数**：CCI有数百个参数。在构建任何命令之前，运行`hcloud CCI <操作> --help`。帮助输出是权威来源。

> 这些规则的详细说明位于[安全约束](#安全约束)、[hcloud CLI限制](#hcloud-cli-limitations)和[注意事项](#注意事项)中。

## 标准工作流

```
1. 创建命名空间（带风味注解）
2. 创建网络（需要Python辅助脚本用于注解——见hcloud CLI限制）
3. 创建部署 / 有状态集 / 容器（运行工作负载）
4. 查询状态，查看日志
5. （可选）创建EIPPool用于容器公网IP访问
6. 清理：删除工作负载 → 删除网络 → 删除命名空间
```

## 前置条件

### 1. hcloud CLI要求（强制）

- 安装hcloud CLI（版本 >= 7.2.2）
- 运行`hcloud version`验证安装
- 首次使用：`printf "y\n" | hcloud version`接受隐私声明

### 2. 凭证配置

hcloud CLI支持两种凭证模式。有关完整详细信息，请参阅[references/credential-configuration.md](references/credential-configuration.md)。

**快速设置**（选择一种）：

```bash
# 模式A——长期AK/SK
export HUAWEI_CLOUD_AK=<your-ak>
export HUAWEI_CLOUD_SK=<your-sk>
export HUAWEI_CLOUD_REGION=cn-north-4

# 模式B——临时AK/SK+安全令牌
export HUAWEI_CLOUD_AK=<your-temp-ak>
export HUAWEI_CLOUD_SK=<your-temp-sk>
export HUAWEI_CLOUD_SECURITY_TOKEN=<your-security-token>
export HUAWEI_CLOUD_REGION=cn-north-4
```

- **安全规则**：不要暴露AK/SK/SecurityToken值。使用`hcloud configure list`仅检查存在性。

> ⚠️ **已知限制——Python辅助脚本凭证独立于hcloud CLI**：Python辅助脚本（`scripts/cci_network_helper.py`）使用`HW_ACCESS_KEY` / `HW_SECRET_KEY`（可选`HW_SECURITY_TOKEN`）环境变量进行身份验证，这些凭证**独立于**hcloud CLI的凭证源（配置文件或`HUAWEI_CLOUD_AK`/`HUAWEI_CLOUD_SK`）。如果`HW_ACCESS_KEY`/`HW_SECRET_KEY`中的凭证缺乏创建CCI网络的必要IAM权限，脚本将因403错误而失败。确保这些变量包含具有足够CCI权限的凭证（例如，`CCI FullAccess`）。hcloud CLI继续独立使用其自己的凭证源——运行辅助脚本不会影响后续hcloud CLI命令。

### 3. 验证检查

```bash
hcloud version
hcloud configure list
```

## 安全约束

### 危险操作确认机制

> **此技能严格执行所有破坏性操作的二步确认机制。**

所有破坏性操作在执行前都需要明确用户确认。流程：

**步骤1：预览**——显示命令、资源详情和风险警告

**步骤2：确认并执行**——只有用户明确确认后

#### 需要确认的操作

| 操作 | 风险等级 | 描述 |
|-------|------------|-------------|
| 删除命名空间 | 🔴 严重 | 级联——删除此命名空间下的所有资源（网络、Pod、部署等） |
| 删除网络 | 🟠 高 | 断开与VPC的连接；运行中的Pod失去网络 |
| 删除部署 | 🟠 高 | 终止工作负载的所有副本 |
| 删除有状态集 | 🟠 高 | 终止所有副本；PVC数据可能丢失 |
| 删除容器 | 🟠 高 | 终止容器实例 |
| 删除EIPPool | 🟡 中等 | 释放分配给Pod的公网IP |

### 凭证安全

- **不要在任何对话、命令或输出中暴露AK/SK/SecurityToken值**
- **不要直接要求用户输入AK/SK/SecurityToken**在对话中
- **仅使用** `hcloud configure list`检查凭证状态（仅存在性，非值）
- **优先使用**配置文件模式或环境变量，而不是显式AK/SK参数

## 命令格式标准

CCI遵循标准的hcloud格式，具有Kubernetes风格的嵌套参数：

```bash
hcloud CCI <操作> --param=value --cli-region=<region> --cli-output=json
```

### CCI特定参数规则

CCI参数遵循Kubernetes API约定——深度嵌套的对象，使用点表示法：

1. **注解使用`{*}`格式**：`--metadata.annotations.namespace-kubernetes-io/flavor=general-computing`
2. **标签使用`{*}`格式**：`--metadata.labels.app=my-app`
3. **容器数组（1基）**：`--spec.template.spec.containers.1.name=main --spec.template.spec.containers.1.image=nginx`
4. **资源使用`{*}`格式**：`--spec.template.spec.containers.1.resources.limits.cpu=500m`
5. **选择器matchLabels使用`{*}`格式**：`--spec.selector.matchLabels.app=my-app`
6. **命名空间操作需要`--namespace`**：所有工作负载操作都必须指定命名空间

> **⚠️ 关键**：在构建任何CCI命令之前，始终运行`hcloud CCI <操作> --help`验证确切的参数名称。CCI有数百个参数；帮助输出是权威来源。

### 参数格式详情

有关完整的CCI参数格式规则和示例，请参阅[references/parameter-format.md](references/parameter-format.md)。

## 场景路由

| 用户意图 | 参考文档 |
|---|---|
| 创建/查询/删除命名空间 | [references/task-namespace-management.md](references/task-namespace-management.md) |
| 创建/查询/删除网络 | [references/task-network-management.md](references/task-network-management.md) |
| 创建/查询/更新/删除/扩展部署 | [references/task-deployment-management.md](references/task-deployment-management.md) |
| 创建/查询/更新/删除有状态集 | [references/task-statefulset-management.md](references/task-statefulset-management.md) |
| 创建/查询/删除容器 | [references/task-pod-management.md](references/task-pod-management.md) |
| 创建/查询/删除EIPPool | [references/task-eippool-management.md](references/task-eippool-management.md) |
| 查询状态，查看日志，事件 | [references/task-logs-and-status.md](references/task-logs-and-status.md) |
| 完整工作流（创建→运行→清理） | [references/common-workflows.md](references/common-workflows.md) |
| 所有CCI操作快速参考 | [references/cci-operation-catalog.md](references/cci-operation-catalog.md) |
| 故障排除 | [references/troubleshooting.md](references/troubleshooting.md) |
| IAM权限 | [references/iam-policies.md](references/iam-policies.md) |
| 验证步骤 | [references/verification-method.md](references/verification-method.md) |
| 正确/错误模式比较 | [references/acceptance-criteria.md](references/acceptance-criteria.md) |

## 核心命令

### 命名空间

```bash
# 创建命名空间（general-computing风味）
hcloud CCI createCoreV1Namespace \
  --metadata.name=<ns-name> \
  --metadata.annotations.namespace-kubernetes-io/flavor=general-computing \
  --cli-region=<region \
  --cli-output=json

# 列出命名空间
hcloud CCI listCoreV1Namespace --cli-region=<region> --cli-output=json

# 查看命名空间详情
hcloud CCI readCoreV1Namespace --name=<ns-name> --cli-region=<region> --cli-output=json

# 删除命名空间（需要两步确认）
hcloud CCI deleteCoreV1Namespace --name=<ns-name> --cli-region=<region>
```

### 网络

> **⚠️ hcloud CLI限制**：网络创建需要Python辅助脚本，因为hcloud CLI无法传递包含点的注解键`network.alpha.kubernetes.io/default-security-group`（hcloud将其视为嵌套级别）。`--cli-jsonInput`方法也不起作用，因为hcloud存在一个bug，注解在`--dryrun`输出中显示，但在实际请求中未传输。见下文[hcloud CLI限制](#hcloud-cli-limitations)。
>
> **⚠️ 凭证要求**：Python辅助脚本使用`HW_ACCESS_KEY`/`HW_SECRET_KEY`（可选`HW_SECURITY_TOKEN`）环境变量进行身份验证。这与hcloud CLI的凭证源（读取`HUAWEI_CLOUD_AK`/`HUAWEI_CLOUD_SK`或其配置）**独立**。如果`HW_ACCESS_KEY`/`HW_SECRET_KEY`中的凭证缺乏创建CCI网络的权限，脚本将因403错误而失败。确保它们具有足够的IAM权限（例如，`CCI FullAccess`）。脚本运行后，hcloud CLI命令继续独立使用其自己的凭证源，不受影响。

```bash
# 步骤1：获取VPC子网详情（包括neutron_network_id）
hcloud VPC ShowSubnet --vpc_id=<vpc-id> --subnet_id=<subnet-id> --cli-region=<region> --cli-output=json

# 步骤2：通过Python辅助脚本创建网络
python scripts/cci_network_helper.py create \
  --namespace=<ns-name> \
  --name=<network-name> \
  --vpc-id=<vpc-id> \
  --subnet-id=<subnet-id> \
  --network-id=<neutron-network-id> \
  --security-group-id=<sg-id> \
  --region=<region>

# 步骤3：等待网络状态变为Active
hcloud CCI readNetworkingCciIoV1beta1NamespacedNetworkStatus \
  --name=<network-name> \
  --namespace=<ns-name> \
  --cli-region=<region> \
  --cli-output=json

# 列出网络
hcloud CCI listNetworkingCciIoV1beta1NamespacedNetwork \
  --namespace=<ns-name> \
  --cli-region=<region> \
  --cli-output=json
```

**必需的网络spec字段**：网络创建需要`attachedVPC`、`subnetID`、`networkType`，**并且**需要`networkID`（neutron网络ID）。`networkID`字段是**必需的**——它是从`hcloud VPC ShowSubnet`获取的neutron网络ID。

**必需的网络注解**：`network.alpha.kubernetes.io/default-security-group`（CCI网络安全组的正确注解键，不是`security-group-id`）。此注解必须设置为安全组ID。

### 部署

```bash
# 创建部署
hcloud CCI createAppsV1NamespacedDeployment \
  --namespace=<ns-name> \
  --metadata.name=<deploy-name> \
  --spec.replicas=1 \
  --spec.selector.matchLabels.app=<deploy-name> \
  --spec.template.metadata.labels.app=<deploy-name> \
  --spec.template.spec.containers.1.name=<container-name> \
  --spec.template.spec.containers.1.image=<image> \
  --spec.template.spec.containers.1.resources.limits.cpu=500m \
  --spec.template.spec.containers.1.resources.limits.memory=1Gi \
  --spec.template.spec.containers.1.resources.requests.cpu=500m \
  --spec.template.spec.containers.1.resources.requests.memory=1Gi \
  --cli-region=<region> \
  --cli-output=json

# 扩展部署
hcloud CCI patchAppsV1NamespacedDeploymentScale \
  --name=<deploy-name> \
  --namespace=<ns-name> \
  --spec.replicas=<new-replicas> \
  --cli-region=<region>

# 查看部署状态
hcloud CCI readAppsV1NamespacedDeploymentStatus \
  --name=<deploy-name> \
  --namespace=<ns-name> \
  --cli-region=<region> \
  --cli-output=json
```

### 有状态集

```bash
# 创建有状态集
hcloud CCI createAppsV1NamespacedStatefulSet \
  --namespace=<ns-name> \
  --metadata.name=<sts-name> \
  --spec.replicas=1 \
  --spec.selector.matchLabels.app=<sts-name> \
  --spec.template.metadata.labels.app=<sts-name> \
  --spec.template.spec.containers.1.name=<container-name> \
  --spec.template.spec.containers.1.image=<image> \
  --spec.template.spec.containers.1.resources.limits.cpu=500m \
  --spec.template.spec.containers.1.resources.limits.memory=1Gi \
  --cli-region=<region> \
  --cli-output=json

# 查看有状态集状态
hcloud CCI readAppsV1NamespacedStatefulSetStatus \
  --name=<sts-name> \
  --namespace=<ns-name> \
  --cli-region=<region> \
  --cli-output=json
```

### 容器

```bash
# 创建容器（单个容器实例）
hcloud CCI createCoreV1NamespacedPod \
  --namespace=<ns-name> \
  --metadata.name=<pod-name> \
  --spec.containers.1.name=<container-name> \
  --spec.containers.1.image=<image> \
  --spec.containers.1.resources.limits.cpu=500m \
  --spec.containers.1.resources.limits.memory=1Gi \
  --cli-region=<region> \
  --cli-output=json

# 查看容器状态
hcloud CCI readCoreV1NamespacedPodStatus \
  --name=<pod-name> \
  --namespace=<ns-name> \
  --cli-region=<region> \
  --cli-output=json

# 查看容器日志
hcloud CCI readCoreV1NamespacedPodLog \
  --name=<pod-name> \
  --namespace=<ns-name> \
  --container=<container-name> \
  --cli-region=<region>
```

### EIPPool

```bash
# 创建EIPPool（用于容器公网IP访问——自动创建EIP）
hcloud CCI createCrdYangtseCniV1NamespacedEIPPool \
  --namespace=<ns-name> \
  --apiVersion=crd.yangtse.cni/v1 \
  --kind=EIPPool \
  --metadata.name=<eippool-name> \
  --spec.amount=1 \
  --spec.eipAttributes.networkType=5_bgp \
  --spec.eipAttributes.ipVersion=4 \
  --spec.eipAttributes.bandwidth.shareType=PER \
  --spec.eipAttributes.bandwidth.size=5 \
  --spec.eipAttributes.bandwidth.chargeMode=bandwidth \
  --spec.eipAttributes.bandwidth.name=<bw-name> \
  --cli-region=<region> \
  --cli-output=json

# 查看EIPPool状态
hcloud CCI readCrdYangtseCniV1NamespacedEIPPoolStatus \
  --name=<eippool-name> \
  --namespace=<ns-name> \
  --cli-region=<region> \
  --cli-output=json
```

**EIPPool必需字段**：`--apiVersion=crd.yangtse.cni/v1`和`--kind=EIPPool`是强制的。`spec.eipAttributes.networkType`是必需的（值：`5_bgp`用于动态BGP，`5_gray`用于专用负载均衡）。`spec.eipAttributes.bandwidth.chargeMode`和`name`在自动创建EIP时是必需的。

**容器EIP绑定**：要将EIPPool分配给容器，请添加注解`yangtse.io/eippool=<eippool-name>`（使用连字符解决方案：`--metadata.annotations.yangtse-io/eippool=<eippool-name>`）。

## VPC/Subnet前提条件

CCI工作负载在映射到现有VPC子网的网络上运行。在创建网络之前，查询可用的VPC和子网，并获取neutron网络ID（创建网络所需）：

```bash
# 列出VPC
hcloud VPC ListVpcs --cli-region=<region> --cli-output=json

# 列出子网
hcloud VPC ListSubnets --cli-region=<region> --cli-output=json

# 获取子网详情（包括neutron_network_id——创建网络所需）
hcloud VPC ShowSubnet --vpc_id=<vpc-id> --subnet_id=<subnet-id> --cli-region=<region> --cli-output=json
```

> **⚠️ VPC子网CIDR限制**：VPC和子网CIDR不能是`10.247.0.0/16`——CCI保留此范围用于服务网络。使用它会导致IP冲突和工作负载创建失败。

> **⚠️ neutron_network_id是必需的**：`VPC ShowSubnet`输出中的`neutron_network_id`是Network spec中`networkID`字段的值。此字段是创建网络**必需的**。

## 命名空间风味类型

| 风味值 | 描述 | 用例 |
|---|---|---|
| `general-computing` | 普通计算类型 | 标准工作负载、Web服务、微服务 |
| `gpu-accelerated` | GPU加速类型 | AI、ML、高性能计算 |

## 资源配额和限制

CCI按命名空间执行资源配额。常见默认值：

| 资源 | 默认限制 |
|---|---|
| 容器 | 因地区而异 |
| 每容器CPU | 0.25 - 8核 |
| 每容器内存 | 0.5Gi - 32Gi |
| PVC | 因地区而异 |

查询当前配额：

```bash
hcloud CCI listCoreV1NamespacedResourceQuota --namespace=<ns-name> --cli-region=<region> --cli-output=json
```

## 输出格式

### JSON（推荐）
```bash
hcloud CCI <操作> --cli-region=<region> --cli-output=json
```

### 表格（用于手动查看）
```bash
hcloud CCI <操作> --cli-region=<region> --cli-output=table
```

### JMESPath过滤
```bash
# 过滤部署状态
hcloud CCI readAppsV1NamespacedDeploymentStatus --name=<deploy> --namespace=<ns> --cli-region=<region> --cli-output=json --cli-query="{replicas:status.replicas,ready:status.readyReplicas,available:status.availableReplicas}"

# 过滤容器阶段
hcloud CCI readCoreV1NamespacedPodStatus --name=<pod> --namespace=<ns> --cli-region=<region> --cli-output=json --cli-query="status.phase"
```

## 调试

在任何命令中添加`--cli-debug=true`以获取详细的请求/响应信息：

```bash
hcloud CCI <操作> --cli-debug=true --cli-region=<region>
```

## 参数确认

在执行任何CCI操作之前，确认这些参数：

| 参数 | 必填 | 描述 | 来源 |
|---|---|---|---|
| `--namespace` | 是 | CCI命名空间名称 | 现有或新建 |
| `--cli-region` | 是 | 华为云区域ID | `HUAWEI_CLOUD_REGION`或配置 |
| `--metadata.name` | 是 | 资源名称 | 用户指定 |
| 风味注解 | 是（命名空间） | `general-computing`或`gpu-accelerated` | 用户选择 |
| VPC/Subnet ID | 是（网络） | 从`VPC ListVpcs` / `VPC ShowSubnet` | 查询现有资源 |
| neutron_network_id | 是（网络） | 从`VPC ShowSubnet`响应 | 查询结果 |

> 在执行任何CCI命令之前运行`hcloud CCI <操作> --help`验证参数名称，然后参考上表。

## 注意事项

有关详细故障排除信息，请参阅[references/troubleshooting.md](references/troubleshooting.md)。

**快速参考**：

| 问题 | 原因 | 快速修复 |
|---|---|---|
| 命名空间创建失败 | 缺少风味注解 | 添加`--metadata.annotations.namespace-kubernetes-io/flavor=general-computing` |
| 网络创建失败（400/403） | 缺少VPC/子网/注解/networkID，或凭证范围不足 | 验证子网/neutron ID，安全组；使用Python辅助；使用**长期AK/SK**（模式A） |
| 容器保持Pending | 命名空间中不存在网络 | 先创建网络 |
| 403权限错误 | IAM不足 | 检查[references/iam-policies.md](references/iam-policies.md) |
| 深度嵌套参数错误 | 点表示法错误 | 使用`--help`验证确切的参数路径 |
| 带点的注解未传递 | hcloud CLI限制 | 使用Python辅助脚本进行网络创建 |
| EIPPool创建失败（400/422） | 缺少apiVersion/kind/networkType | 添加所有必需字段（见EIPPool部分） |
| limit/request不匹配 | CCI要求limits == requests | 将requests设置为与limits相同的值（例如，`500m/1Gi`） |

## 验证方法

有关完整验证步骤，请参阅[references/verification-method.md](references/verification-method.md)。

**快速清单**：

| 步骤 | 命令 | 预期结果 |
|---|---|---|
| 命名空间 | `hcloud CCI readCoreV1Namespace --name=<ns> --cli-region=<region>` | status.phase=Active |
| 网络 | `hcloud CCI readNetworkingCciIoV1beta1NamespacedNetworkStatus --name=<net> --namespace=<ns>` | status.phase=Active |
| 部署 | `hcloud CCI readAppsV1NamespacedDeploymentStatus --name=<deploy> --namespace=<ns>` | readyReplicas >= 1 |
| 容器 | `hcloud CCI readCoreV1NamespacedPodStatus --name=<pod> --namespace=<ns>` | status.phase=Running |

## 最佳实践

1. **命名空间隔离**：为不同团队/项目使用不同的命名空间以避免资源冲突
2. **按需创建EIPPool**：仅在需要容器公网IP访问时创建EIPPool

## hcloud CLI限制

> **⚠️ 关键**：hcloud CLI存在已知限制，会影响CCI操作。理解这些对于成功创建网络至关重要。

| 限制 | 影响 | 解决方案 |
|---|---|---|
| **无法通过CLI参数传递包含点的注解键** | hcloud将点视为嵌套级别，所以`network.alpha.kubernetes.io/default-security-group`创建深度嵌套结构 | 使用Python辅助脚本(`scripts/cci_network_helper.py`)进行网络创建 |
| **`--cli-jsonInput`无法正确传输注解** | hcloud bug：注解在`--dryrun`输出中显示，但在实际请求中未传输 | 使用Python辅助脚本 |
| **`--cli-jsonInput`需要ASCII编码** | UTF-8 BOM导致JSON解析失败 | 确保JSON输入文件为纯ASCII（无BOM） |
| **命名空间注解使用连字符替换** | 像`namespace.kubernetes.io/flavor`这样的键可以使用连字符(`namespace-kubernetes-io/flavor`)，CCI会自动规范化 | 此解决方案仅适用于命名空间，不适用于网络 |

**为什么网络需要Python辅助脚本**：注解键`network.alpha.kubernetes.io/default-security-group`无法通过hcloud CLI传递（点表示法或`--cli-jsonInput`）。与命名空间注解不同，CCI不会规范化连字符替换的键用于网络资源。Python辅助脚本(`scripts/cci_network_helper.py`)直接构造正确的API请求体。
