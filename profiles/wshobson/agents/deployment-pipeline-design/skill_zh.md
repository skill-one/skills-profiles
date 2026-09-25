# 部署流水线设计

多阶段CI/CD流水线的架构模式，包含审批门禁、部署策略和环境晋升工作流。

## 目的

通过合理的阶段组织、自动化的质量门禁和渐进式交付策略，设计健壮、安全的部署流水线，在速度与安全之间取得平衡。这项技能涵盖了流水线架构的结构设计以及可靠生产部署的操作模式。

## 输入 / 输出

### 你提供的内容

- **应用类型**：语言/运行时、容器化或裸金属、单体或微服务
- **部署目标**：Kubernetes、ECS、虚拟机、无服务器或平台即服务
- **环境拓扑**：环境数量（开发/测试/生产）、区域布局、空气隔离需求
- **发布要求**：可接受的停机时间、回滚SLA、流量拆分需求、金丝雀与蓝绿部署偏好
- **门禁约束**：审批团队、所需的测试覆盖率阈值、合规扫描（SAST、DAST、SCA）
- **监控堆栈**：Prometheus、Datadog、CloudWatch或其他用于自动化晋升决策的指标源

### 该技能生成的输出

- **流水线配置**：阶段定义、作业依赖、并行度和缓存策略
- **部署策略**：选定的发布模式及其注释配置（金丝雀权重、蓝绿切换、滚动参数）
- **健康检查设置**：浅层与深层就绪探针、部署后冒烟测试脚本
- **门禁定义**：自动化的指标阈值和手动审批工作流
- **回滚计划**：自动回滚触发器和手动运行手册步骤

## 适用场景

- 为新服务或平台迁移设计CI/CD架构
- 在环境之间实施部署门禁
- 配置带有强制安全扫描的多环境流水线
- 建立使用金丝雀或蓝绿策略的渐进式交付
- 调试阶段成功但生产行为错误的流水线
- 通过在指标退化时自动回滚来减少平均恢复时间

## 详细模式和实例

详细模式文档位于`references/details.md`。当上层导航层级不足时，请阅读该文件。

## 故障排除

### 流水线健康检查通过但生产服务不健康

流水线健康检查正在访问一个浅层的`/ping`端点，即使数据库无法访问时它也会返回200。使用验证实际依赖的深层就绪检查（见上文健康检查部分）。

### 金丝雀部署从未完全晋升

Argo Rollouts需要一个有效的`AnalysisTemplate`才能自动晋升。如果Prometheus查询返回无数据（例如，指标名称已更改），分析将保持不确定状态，晋升将停滞。添加`inconclusiveLimit`以便快速失败而不是无限期挂起：

```yaml
spec:
  metrics:
  - name: error-rate
    failureCondition: "result[0] > 0.05"
    inconclusiveLimit: 2   # 2次不确定结果后失败，而不是无限期挂起
    provider:
      prometheus:
        query: |
          sum(rate(http_requests_total{status=~"5.."}[2m]))
          / sum(rate(http_requests_total[2m]))
```

### 测试环境部署成功但生产作业从未启动

检查生产环境保护规则是否配置正确——缺少审阅者分配意味着审批门禁将无限期等待且无通知。在GitHub Actions中，确保**设置→环境→生产**中的`Required reviewers`设置为现有用户或团队。

### 每次运行都会破坏Docker层缓存导致构建缓慢

如果`COPY . .`出现在依赖安装之前，任何源文件更改都会使依赖层失效。先复制依赖清单：

```dockerfile
# 好：依赖与源代码分开缓存
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

### 回滚将数据库迁移应用于旧代码

没有回滚迁移的服务回滚会导致模式/代码不匹配错误。始终确保迁移至少在一个发布周期内是向后兼容的（仅增量），并将撤销脚本与迁移版本化：

```bash
# migrations/V20240315__add_nullable_column.sql       (正向)
# migrations/V20240315__add_nullable_column.undo.sql  (逆向)
```

直到旧代码版本从所有环境完全退役前，切勿运行破坏性迁移（DROP COLUMN、ALTER NOT NULL）。

## 高级主题

关于平台特定的流水线配置、多区域晋升工作流和高级Argo Rollouts模式，请参阅：

- [`references/advanced-strategies.md`](references/advanced-strategies.md) — 扩展YAML示例、平台特定配置（GitHub Actions、GitLab CI、Azure Pipelines）、多区域金丝雀模式以及数据库迁移回滚策略

## 相关技能

- `github-actions-templates` - 用于GitHub Actions实现模式和可重用工作流
- `gitlab-ci-patterns` - 用于GitLab CI/CD流水线实现
- `secrets-management` - 用于CI/CD流水线中的密钥管理
