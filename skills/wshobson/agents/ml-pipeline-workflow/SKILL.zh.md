---
name: ml-pipeline-workflow
description: 构建从数据准备到模型训练、验证和生产的端到端 MLOps 管道。在创建机器学习管道、实施 MLOps 实践或自动化模型训练和部署工作流时使用。
---

# 机器学习管道工作流

完成从数据准备到模型部署的端到端 MLOps 管道编排。

## 概述

本技能提供全面的指导，用于构建处理完整生命周期的生产机器学习管道：数据摄取 → 准备 → 训练 → 验证 → 部署 → 监控。

## 何时使用此技能

- 从零开始构建机器学习管道
- 设计机器学习系统的流程编排
- 实施数据 → 模型 → 部署自动化
- 设置可复现的训练工作流
- 创建基于 DAG 的机器学习编排
- 将机器学习组件集成到生产系统中

## 此技能提供的内容

### 核心功能

1. **管道架构**
   - 端到端工作流设计
   - DAG 编排模式（Airflow、Dagster、Kubeflow）
   - 组件依赖和数据流
   - 错误处理和重试策略

2. **数据准备**
   - 数据验证和质量检查
   - 特征工程管道
   - 数据版本化和血缘关系
   - 训练/验证/测试分割策略

3. **模型训练**
   - 训练作业编排
   - 超参数管理
   - 实验跟踪集成
   - 分布式训练模式

4. **模型验证**
   - 验证框架和指标
   - A/B 测试基础设施
   - 性能回归检测
   - 模型比较工作流

5. **部署自动化**
   - 模型服务模式
   - 金丝雀部署
   - 蓝绿部署策略
   - 回滚机制

### 参考文档

查看 `references/` 目录中的详细指南：

- **data-preparation.md** - 数据清理、验证和特征工程
- **model-training.md** - 训练工作流和最佳实践
- **model-validation.md** - 验证策略和指标
- **model-deployment.md** - 部署模式和 serving 架构

### 资产和模板

`assets/` 目录包含：

- **pipeline-dag.yaml.template** - 工作流编排的 DAG 模板
- **training-config.yaml** - 训练配置模板
- **validation-checklist.md** - 部署前验证清单

## 使用模式

### 基本管道设置

```python
# 1. 定义管道阶段
stages = [
    "data_ingestion",
    "data_validation",
    "feature_engineering",
    "model_training",
    "model_validation",
    "model_deployment"
]

# 2. 配置依赖关系
# 查看 assets/pipeline-dag.yaml.template 获取完整示例
```

### 生产工作流

1. **数据准备阶段**
   - 从来源摄取原始数据
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
   - 与基线进行比较
   - 生成性能报告
   - 批准部署

4. **部署阶段**
   - 打包模型工件
   - 部署到服务基础设施
   - 配置监控
   - 验证生产流量

## 最佳实践

### 管道设计

- **模块化**：每个阶段应该是独立可测试的
- **幂等性**：重新运行阶段应该是安全的
- **可观察性**：在每个阶段记录指标
- **版本控制**：跟踪数据、代码和模型版本
- **故障处理**：实现重试逻辑和告警

### 数据管理

- 使用数据验证库（Great Expectations、TFX）
- 使用 DVC 或类似工具版本化数据集
- 记录特征工程转换
- 维护数据血缘关系跟踪

### 模型操作

- 分离训练和服务基础设施
- 使用模型注册中心（MLflow、Weights & Biases）
- 实施新模型的渐进式发布
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

- **Apache Airflow**：基于 DAG 的工作流编排
- **Dagster**：基于资产的管道编排
- **Kubeflow Pipelines**：Kubernetes 本地机器学习工作流
- **Prefect**：现代数据流自动化

### 实验跟踪

- MLflow 用于实验跟踪和模型注册
- Weights & Biases 用于可视化和协作
- TensorBoard 用于训练指标

### 部署平台

- AWS SageMaker 用于托管机器学习基础设施
- Google Vertex AI 用于 GCP 部署
- Azure ML 用于 Azure 云
- OCI Data Science 用于 Oracle Cloud Infrastructure 部署
- Kubernetes + KServe 用于云无关的 serving

## 逐步披露

从基础开始，逐步增加复杂性：

1. **级别 1**：简单的线性管道（数据 → 训练 → 部署）
2. **级别 2**：添加验证和监控阶段
3. **级别 3**：实现超参数调整
4. **级别 4**：添加 A/B 测试和渐进式发布
5. **级别 5**：多模型管道与集成策略

## 常见模式

### 批量训练管道

```yaml
# 查看 assets/pipeline-dag.yaml.template
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

### 实时特征管道

```python
# 实时特征的流处理
# 与批量训练结合
# 查看 references/data-preparation.md
```

### 持续训练

```python
# 按计划自动重新训练
# 由数据漂移检测触发
# 查看 references/model-training.md
```

## 故障排除

### 常见问题

- **管道失败**：检查依赖关系和数据可用性
- **训练不稳定**：检查超参数和数据质量
- **部署问题**：验证模型工件和服务配置
- **性能下降**：监控数据漂移和模型指标

### 调试步骤

1. 检查每个阶段的管道日志
2. 在边界验证输入/输出数据
3. 独立测试组件
4. 查看实验跟踪指标
5. 检查模型工件和元数据

## 下一步

设置管道后：

1. 探索 **hyperparameter-tuning** 技能进行优化
2. 学习 **experiment-tracking-setup** 用于 MLflow/W&B 集成
3. 查看 **model-deployment-patterns** 用于 serving 策略
4. 使用可观察性工具实现监控

## 相关技能

- **experiment-tracking-setup**：MLflow 和 Weights & Biases 集成
- **hyperparameter-tuning**：自动超参数优化
- **model-deployment-patterns**：高级部署策略
