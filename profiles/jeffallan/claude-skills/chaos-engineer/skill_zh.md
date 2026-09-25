# 混沌工程师

## 使用此技能的场景

- 设计和执行混沌实验
- 实现故障注入框架（混沌猴、Litmus 等）
- 规划和开展游戏日演练
- 构建影响范围控制和安全机制
- 在 CI/CD 中设置持续混沌测试
- 基于实验结果提升系统弹性

## 核心工作流程

1. **系统分析** - 绘制架构、依赖关系、关键路径和故障模式
2. **实验设计** - 定义假设、稳态、影响范围和安全控制
3. **执行混沌** - 运行受控实验并监控快速回滚
4. **学习与改进** - 记录发现、实施修复、增强监控
5. **自动化** - 将混沌测试集成到 CI/CD 以实现持续弹性

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 实验 | `references/experiment-design.md` | 设计假设、影响范围、回滚 |
| 基础设施 | `references/infrastructure-chaos.md` | 服务器、网络、区域、区域故障 |
| Kubernetes | `references/kubernetes-chaos.md` | Pod、节点、Litmus、混沌网格实验 |
| 工具与自动化 | `references/chaos-tools.md` | 混沌猴、Gremlin、Pumba、CI/CD 集成 |
| 游戏日 | `references/game-days.md` | 规划、执行、从游戏日中学习 |

## 安全检查清单

每个实验都必须强制执行的显而易见的约束：

- **稳态优先** — 在注入任何故障之前定义和验证基准指标
- **影响范围上限** — 从最小可能影响范围开始；仅在验证后扩展
- **自动回滚 ≤ 30 秒** — 中断路径必须在实验开始前进行脚本编写和测试
- **单一变量** — 一次只改变一个故障条件，直到行为被充分理解
- **无安全网不生产** — 面向客户的环境需要断路器、功能标志或金丝雀隔离
- **形成闭环** — 每个实验都必须产生书面学习摘要和至少一项跟踪改进

## 输出模板

实施混沌工程时，请提供：
1. 实验设计文档（假设、指标、影响范围）
2. 实现代码（故障注入脚本/清单）
3. 监控设置和告警配置
4. 回滚程序和安全控制
5. 学习摘要和改进建议

## 具体示例：Pod 故障实验（Litmus Chaos）

以下展示了使用 Litmus Chaos 在 Kubernetes 上的完整实验——从假设到回滚。

### 第 1 步 — 定义稳态并应用实验

```bash
# 验证基准：p99 延迟 < 200ms，错误率 < 0.1%
kubectl get deploy my-service -n production
kubectl top pods -n production -l app=my-service
```

### 第 2 步 — 创建并应用 Litmus ChaosEngine 清单

```yaml
# chaos-pod-delete.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: my-service-pod-delete
  namespace: production
spec:
  appinfo:
    appns: production
    applabel: "app=my-service"
    appkind: deployment
  # 限制影响范围：一次只删除一个副本
  engineState: active
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "60"          # 秒
            - name: CHAOS_INTERVAL
              value: "20"          # 每 20 秒删除一个 Pod
            - name: FORCE
              value: "false"
            - name: PODS_AFFECTED_PERC
              value: "33"          # 最大 33% 的副本受影响
```

```bash
# 应用实验
kubectl apply -f chaos-pod-delete.yaml

# 监控实验状态
kubectl describe chaosengine my-service-pod-delete -n production
kubectl get chaosresult my-service-pod-delete-pod-delete -n production -w
```

### 第 3 步 — 实验期间监控

```bash
# 尾部应用日志以查找错误
kubectl logs -l app=my-service -n production --since=2m -f

# 完成时检查 ChaosResult 判定
kubectl get chaosresult my-service-pod-delete-pod-delete \
  -n production -o jsonpath='{.status.experimentStatus.verdict}'
```

### 第 4 步 — 如果稳态被违反则回滚/中止

```bash
# 立即停止实验
kubectl patch chaosengine my-service-pod-delete \
  -n production --type merge -p '{"spec":{"engineState":"stop"}}'

# 确认所有 Pod 都健康
kubectl rollout status deployment/my-service -n production
```

## 具体示例：使用 toxiproxy 的网络延迟

```bash
# 安装 toxiproxy CLI
brew install toxiproxy   # macOS；在 Linux 上使用二进制发布版

# 启动 toxiproxy 服务器（与您的服务一起运行）
toxiproxy-server &

# 为下游依赖创建代理
toxiproxy-cli create -l 0.0.0.0:22222 -u downstream-db:5432 db-proxy

# 注入 300ms 延迟和 10% 振动——影响范围：此代理仅限
toxiproxy-cli toxic add db-proxy -t latency -a latency=300 -a jitter=30

# 运行您的负载测试/在此处观察指标 ...

# 移除 toxic 以恢复正常行为
toxiproxy-cli toxic remove db-proxy -n latency_downstream
```

## 具体示例：混沌猴（Spinnaker / 独立版）

```bash
# chaos-monkey-config.yml — 限制为单个 ASG
deployment:
  enabled: true
  regionIndependence: false
chaos:
  enabled: true
  meanTimeBetweenKillsInWorkDays: 2
  minTimeBetweenKillsInWorkDays: 1
  grouping: APP           # 每个应用杀一个实例，而不是每个集群
  exceptions:
    - account: production
      region: us-east-1
      detail: "*-canary"  # 永不杀死金丝雀实例

# 应用并手动触发杀死以进行测试
chaos-monkey --app my-service --account staging --dry-run false
```

[文档](https://jeffallan.github.io/claude-skills/skills/devops/chaos-engineer/)
