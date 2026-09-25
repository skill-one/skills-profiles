# ML流水线工作流

完成从数据准备到模型部署的端到端MLOps流水线编排。

## 概述

本技能提供全面的指导，用于构建处理完整生命周期的生产ML流水线：数据摄取→准备→训练→验证→部署→监控。

## 何时使用此技能

- 从零开始构建新的ML流水线
- 设计ML系统的流水线编排工作流
- 实现数据→模型→部署自动化
- 设置可复现的训练流水线
- 创建基于DAG的ML编排
- 将ML组件集成到生产系统中

## 此技能提供的内容

### 核心功能

1. **流水线架构**
   - 端到端工作流设计
   - DAG编排模式（Airflow、Dagster、Kubeflow）
   - 组件依赖和数据流
   - 错误处理和重试策略

2. **数据准备**
   - 数据验证和质量检查
   - 特征工程流水线
   - 数据版本化和血缘关系
   - 训练/验证/测试分割策略

3. **模型训练**
   - 训练作业编排
   - 超参数管理
   - 实验跟踪集成
   - 分布式训练模式

4. **模型验证**
   - 验证框架和指标
   - A/B测试基础设施
   - 性能回归检测
   - 模型比较工作流

5. **部署自动化**
   - 模型服务模式
   - 金丝雀部署
   - 蓝绿部署策略
   - 回滚机制

### 参考文档

参考`references/`目录中的详细指南：

- **data-preparation.md** - 数据清洗、验证和特征工程
- **model-training.md** - 训练工作流和最佳实践
- **model-validation.md** - 验证策略和指标
- **model-deployment.md** - 部署模式和 Serving 架构

### 资源和模板

`assets/`目录包含：

- **pipeline-dag.yaml.template** - 工作流编排的DAG模板
- **training-config.yaml** - 训练配置模板
- **validation-checklist.md** - 部署前验证清单

## 使用模式

### 基本流水线设置

```python
# 1. 定义流水线阶段
stages = [
    "data_ingestion",
    "data_validation",
    "feature_engineering",
    "model_training",
    "model_validation",
    "model_deployment"
]

# 2. 配置依赖关系
# 参考assets/pipeline-dag.yaml.template的完整示例
```

### 生产工作流

1. **数据准备阶段**
   - 从源摄取原始数据
   - 运行数据质量检查
   - 应用特征转换
   - 版本化处理后的数据集

2. **训练阶段**
   - 加载版本化的训练数据
   - 执行训练作业
   - 跟踪实验和指标
   - 保存训练后的模型

3. **验证阶段**
   - 运行验证测试套件
   - 与基线比较
   - 生成性能报告
   - 批准部署

4. **部署阶段**
   - 打包模型工件
   - 部署到服务基础设施
   - 配置监控
   - 验证生产流量

## 最佳实践

### 流水线设计

- **模块化**：每个阶段应可独立测试
- **幂等性**：重新运行阶段应该是安全的
- **可观察性**：每个阶段记录指标
- **版本控制**：跟踪数据、代码和模型版本
- **错误处理**：实现重试逻辑和告警

### 数据管理

- 使用数据验证库（Great Expectations、TFX）
- 使用DVC等工具版本化数据集
- 记录特征工程转换
- 维护数据血缘关系跟踪

### 模型操作

- 分离训练和服务基础设施
- 使用模型注册中心（MLflow、Weights & Biases）
- 实现新模型的渐进式发布
- 监控模型性能漂移
- 维护回滚能力

### 部署策略

- 从影子部署开始
- 使用金丝雀发布进行验证
- 实施A/B测试基础设施
- 设置自动回滚触发器
- 监控延迟和吞吐量

## 集成点

### 编排工具

- **Apache Airflow**：基于DAG的工作流编排
- **Dagster**：基于资产的流水线编排
- **Kubeflow Pipelines**：Kubernetes原生的ML工作流
- **Prefect**：现代数据流自动化

### 实验跟踪

- MLflow用于实验跟踪和模型注册中心
- Weights & Biases用于可视化和协作
- TensorBoard用于训练指标

### 部署平台

- AWS SageMaker用于托管ML基础设施
- Google Vertex AI用于GCP部署
- Azure ML用于Azure云
- OCI Data Science用于Oracle云基础设施部署
- Kubernetes + KServe用于云无关的Serving

## 逐步披露

从基础开始逐步增加复杂性：

1. **Level 1**：简单的线性流水线（数据→训练→部署）
2. **Level 2**：添加验证和监控阶段
3. **Level 3**：实现超参数调优
4. **Level 4**：添加A/B测试和渐进式发布
5. **Level 5**：多模型流水线与集成策略

## 常见模式

### 批量训练流水线

```yaml
# 参考assets/pipeline-dag.yaml.template
stages:
  - name: data_preparation
    dependencies: []
  - name: model_training
    dependencies: [data_preparation]
  - name: model_evaluation
    dependencies: [model_training]
  - name: model_deployment
    dependencies: [model_evaluation]
```

### 实时特征流水线

```python
# 流处理用于实时特征
# 与批量训练结合
# 参考references/data-preparation.md
```

### 持续训练

```python
# 按计划自动重新训练
# 由数据漂移检测触发
# 参考references/model-training.md
```

## 故障排除

### 常见问题

- **流水线失败**：检查依赖关系和数据可用性
- **训练不稳定**：检查超参数和数据质量
- **部署问题**：验证模型工件和服务配置
- **性能下降**：监控数据漂移和模型指标

### 调试步骤

1. 检查每个阶段的流水线日志
2. 在边界验证输入/输出数据
3. 独立测试组件
4. 查看实验跟踪指标
5. 检查模型工件和元数据

## 下一步

设置流水线后：

1. 探索**超参数调优**技能进行优化
2. 学习**实验跟踪设置**用于MLflow/W&B
3. 查看**模型部署模式**用于服务策略
4. 使用可观察性工具实现监控

## 相关技能

- **experiment-tracking-setup**：MLflow和Weights & Biases集成
- **hyperparameter-tuning**：自动超参数优化
- **model-deployment-patterns**：高级部署策略
