# Kubernetes 配置文件生成器

创建生产就绪的 Kubernetes 配置文件（包括 Deployment、Service、ConfigMap、Secret 和 PersistentVolumeClaims）的逐步指导。

## 目的

此技能提供全面的指导，用于生成符合云原生最佳实践和 Kubernetes 规范的、结构良好、安全且生产就绪的 Kubernetes 配置文件。

## 使用此技能的场景

当您需要执行以下操作时，请使用此技能：

- 创建新的 Kubernetes Deployment 配置文件
- 定义用于网络连接的 Service 资源
- 生成用于配置管理的 ConfigMap 和 Secret 资源
- 创建用于有状态工作负载的 PersistentVolumeClaim 配置文件
- 遵循 Kubernetes 最佳实践和命名规范
- 实施资源限制、健康检查和安全上下文
- 设计用于多环境部署的配置文件

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践总结

1. **始终设置资源请求和限制** - 防止资源饥饿
2. **实施健康检查** - 确保 Kubernetes 能够管理您的应用程序
3. **使用特定的镜像标签** - 避免不可预测的部署
4. **应用安全上下文** - 以非 root 身份运行，丢弃能力
5. **使用 ConfigMaps 和 Secrets** - 将配置与代码分离
6. **对所有内容进行标记** - 启用过滤和组织
7. **遵循命名规范** - 使用标准的 Kubernetes 标签
8. **应用前验证** - 使用 dry-run 和验证工具
9. **对配置文件进行版本控制** - 将其存入 Git 并进行版本控制
10. **使用注释进行文档记录** - 为其他开发者添加上下文

## 故障排除

**Pod 无法启动：**

- 检查镜像拉取错误：`kubectl describe pod <pod-name>`
- 验证资源可用性：`kubectl get nodes`
- 检查事件：`kubectl get events --sort-by='.lastTimestamp'`

**Service 无法访问：**

- 验证选择器是否匹配 Pod 标签：`kubectl get endpoints <service-name>`
- 检查 Service 类型和端口配置
- 在集群内部测试：`kubectl run debug --rm -it --image=busybox -- sh`

**ConfigMap/Secret 无法加载：**

- 验证 Deployment 中的名称是否匹配
- 检查命名空间
- 确保资源存在：`kubectl get configmap,secret`

## 下一步

创建配置文件后：

1. 存入 Git 仓库
2. 设置 CI/CD 管道用于部署
3. 考虑使用 Helm 或 Kustomize 进行模板化
4. 使用 ArgoCD 或 Flux 实施 GitOps
5. 添加监控和可观察性

## 相关技能

- `helm-chart-scaffolding` - 用于模板化和打包
- `gitops-workflow` - 用于自动化部署
- `k8s-security-policies` - 用于高级安全配置
