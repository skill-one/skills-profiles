# 高级数据工程师

世界级高级数据工程师技能，适用于生产级AI/ML/数据系统。

## 快速入门

### 主要能力

```bash
# 核心工具1
python scripts/pipeline_orchestrator.py --input data/ --output results/

# 核心工具2  
python scripts/data_quality_validator.py --target project/ --analyze

# 核心工具3
python scripts/etl_performance_optimizer.py --config config.yaml --deploy
```

## 核心专长

此技能涵盖世界级的能力，包括：

- 高级生产模式和架构
- 可扩展系统设计和实现
- 大规模性能优化
- MLOps和数据Ops最佳实践
- 实时处理和推理
- 分布式计算框架
- 模型部署和监控
- 安全和合规
- 成本优化
- 团队领导和指导

## 技术栈

**语言：** Python, SQL, R, Scala, Go
**ML框架：** PyTorch, TensorFlow, Scikit-learn, XGBoost
**数据工具：** Spark, Airflow, dbt, Kafka, Databricks
**LLM框架：** LangChain, LlamaIndex, DSPy
**部署：** Docker, Kubernetes, AWS/GCP/Azure
**监控：** MLflow, Weights & Biases, Prometheus
**数据库：** PostgreSQL, BigQuery, Snowflake, Pinecone

## 参考文档

### 1. 数据管道架构

在 `references/data_pipeline_architecture.md` 中提供全面指南，涵盖：

- 高级模式和最佳实践
- 生产实施策略
- 性能优化技术
- 可扩展性考虑
- 安全和合规
- 实际案例研究

### 2. 数据建模模式

在 `references/data_modeling_patterns.md` 中提供完整工作流文档，包括：

- 步骤化流程
- 架构设计模式
- 工具集成指南
- 性能调优策略
- 故障排除程序

### 3. 数据Ops最佳实践

在 `references/dataops_best_practices.md` 中提供技术参考指南，包括：

- 系统设计原则
- 实施示例
- 配置最佳实践
- 部署策略
- 监控和可观察性

## 生产模式

### 模式1：可扩展数据处理

企业级数据处理的分布式计算：

- 水平扩展架构
- 容错设计
- 实时和批量处理
- 数据质量验证
- 性能监控

### 模式2：ML模型部署

高可用性生产ML系统：

- 低延迟模型服务
- A/B测试基础设施
- 特征存储集成
- 模型监控和漂移检测
- 自动化重训练管道

### 模式3：实时推理

高吞吐量推理系统：

- 批处理和缓存策略
- 负载均衡
- 自动扩展
- 延迟优化
- 成本优化

## 最佳实践

### 开发

- 测试驱动开发
- 代码审查和结对编程
- 文档即代码
- 一切版本控制
- 持续集成

### 生产

- 监控所有关键指标
- 自动化部署
- 发布功能标志
- 金丝雀发布
- 全面日志记录

### 团队领导

- 指导初级工程师
- 推动技术决策
- 建立编码标准
- 培养学习文化
- 跨职能协作

## 性能目标

**延迟：**
- P50: < 50ms
- P95: < 100ms
- P99: < 200ms

**吞吐量：**
- 请求/秒: > 1000
- 并发用户: > 10,000

**可用性：**
- 运行时间: 99.9%
- 错误率: < 0.1%

## 安全与合规

- 身份验证和授权
- 数据加密（静态和传输中）
- 个人身份信息处理和匿名化
- GDPR/CCPA合规
- 定期安全审计
- 漏洞管理

## 常用命令

```bash
# 开发
python -m pytest tests/ -v --cov
python -m black src/
python -m pylint src/

# 训练
python scripts/train.py --config prod.yaml
python scripts/evaluate.py --model best.pth

# 部署
docker build -t service:v1 .
kubectl apply -f k8s/
helm upgrade service ./charts/

# 监控
kubectl logs -f deployment/service
python scripts/health_check.py
```

## 资源

- 高级模式: `references/data_pipeline_architecture.md`
- 实施指南: `references/data_modeling_patterns.md`
- 技术参考: `references/dataops_best_practices.md`
- 自动化脚本: `scripts/` 目录

## 高级职责

作为世界级高级专业人士：

1. **技术领导**
   - 推动架构决策
   - 指导团队成员
   - 建立最佳实践
   - 确保代码质量

2. **战略思维**
   - 与业务目标保持一致
   - 评估权衡
   - 规划扩展
   - 管理技术债务

3. **协作**
   - 跨团队工作
   - 有效沟通
   - 建立共识
   - 分享知识

4. **创新**
   - 跟踪最新研究
   - 尝试新方法
   - 为社区做出贡献
   - 推动持续改进

5. **生产卓越**
   - 确保高可用性
   - 主动监控
   - 优化性能
   - 响应事件
