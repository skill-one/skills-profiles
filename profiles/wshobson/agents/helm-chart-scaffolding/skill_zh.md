# Helm Chart 模板生成

为打包和部署 Kubernetes 应用程序而创建、组织和管理的 Helm chart 的全面指南。

## 目的

本技能提供构建生产就绪 Helm chart 的分步说明，包括 chart 结构、模板模式、值管理以及验证策略。

## 何时使用此技能

当您需要执行以下操作时，请使用此技能：

- 从零开始创建新的 Helm chart
- 打包 Kubernetes 应用程序以进行分发
- 使用 Helm 管理多环境部署
- 为可重用的 Kubernetes 实现实现模板
- 设置 Helm chart 仓库
- 遵循 Helm 最佳实践和规范

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **为 chart 和应用版本使用语义化版本控制**
2. **在 values.yaml 中用注释记录所有值**
3. **使用模板辅助函数处理重复逻辑**
4. **在打包前验证 chart**
5. **明确固定依赖版本**
6. **使用条件处理可选资源**
7. **遵循命名规范（小写、连字符）**
8. **包含带有使用说明的 NOTES.txt**
9. **使用辅助函数一致地添加标签**
10. **在所有环境中测试安装**

## 故障排除

**模板渲染错误：**

```bash
helm template my-app ./my-app --debug
```

**依赖问题：**

```bash
helm dependency update
helm dependency list
```

**安装失败：**

```bash
helm install my-app ./my-app --dry-run --debug
kubectl get events --sort-by='.lastTimestamp'
```

## 相关技能

- `k8s-manifest-generator` - 用于创建基础 Kubernetes 实现文件
- `gitops-workflow` - 用于自动 Helm chart 部署
