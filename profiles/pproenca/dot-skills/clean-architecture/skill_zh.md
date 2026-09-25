# 清洁架构最佳实践

关于清洁架构原则的全面指南，用于设计可维护、可测试的软件系统。基于罗伯特·C·马丁（Robert C. Martin）的《清洁架构：软件结构与设计匠人指南》。包含8个类别中的42条规则，按架构影响优先级排序。

## 应用时机

在以下情况下参考这些指南：
- 设计新的软件系统或模块
- 结构化层之间的依赖关系
- 定义业务逻辑和基础设施之间的边界
- 审查代码以查找架构违规
- 重构耦合系统以实现更清晰的架构

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 依赖方向 | CRITICAL | `dep-` |
| 2 | 实体设计 | CRITICAL | `entity-` |
| 3 | 用例隔离 | HIGH | `usecase-` |
| 4 | 组件内聚性 | HIGH | `comp-` |
| 5 | 边界定义 | MEDIUM-HIGH | `bound-` |
| 6 | 接口适配器 | MEDIUM | `adapt-` |
| 7 | 框架隔离 | MEDIUM | `frame-` |
| 8 | 测试架构 | LOW-MEDIUM | `test-` |

## 快速参考

### 1. 依赖方向 (CRITICAL)

- [`dep-inward-only`](references/dep-inward-only.md) - 源依赖项仅指向内部
- [`dep-interface-ownership`](references/dep-interface-ownership.md) - 接口属于客户端而非实现者
- [`dep-no-framework-imports`](references/dep-no-framework-imports.md) - 避免在内部层中导入框架
- [`dep-data-crossing-boundaries`](references/dep-data-crossing-boundaries.md) - 使用简单数据结构跨边界
- [`dep-acyclic-dependencies`](references/dep-acyclic-dependencies.md) - 消除组件之间的循环依赖
- [`dep-stable-abstractions`](references/dep-stable-abstractions.md) - 依赖稳定抽象而非易变的具体实现

### 2. 实体设计 (CRITICAL)

- [`entity-pure-business-rules`](references/entity-pure-business-rules.md) - 实体仅包含企业业务规则
- [`entity-no-persistence-awareness`](references/entity-no-persistence-awareness.md) - 实体不得知道其持久化方式
- [`entity-encapsulate-invariants`](references/entity-encapsulate-invariants.md) - 在实体中封装业务不变量
- [`entity-value-objects`](references/entity-value-objects.md) - 使用值对象表示领域概念
- [`entity-rich-not-anemic`](references/entity-rich-not-anemic.md) - 构建丰富的领域模型而非贫血数据结构

### 3. 用例隔离 (HIGH)

- [`usecase-single-responsibility`](references/usecase-single-responsibility.md) - 每个用例有一个变更的原因
- [`usecase-input-output-ports`](references/usecase-input-output-ports.md) - 为用例定义输入和输出端口
- [`usecase-orchestrates-not-implements`](references/usecase-orchestrates-not-implements.md) - 用例协调实体而非实现业务规则
- [`usecase-no-presentation-logic`](references/usecase-no-presentation-logic.md) - 用例不得包含表示逻辑
- [`usecase-explicit-dependencies`](references/usecase-explicit-dependencies.md) - 在构造函数中显式声明所有依赖项
- [`usecase-transaction-boundary`](references/usecase-transaction-boundary.md) - 用例定义事务边界

### 4. 组件内聚性 (HIGH)

- [`comp-screaming-architecture`](references/comp-screaming-architecture.md) - 结构应体现领域而非框架
- [`comp-common-closure`](references/comp-common-closure.md) - 将一起变更的类分组
- [`comp-common-reuse`](references/comp-common-reuse.md) - 避免迫使客户端依赖未使用的代码
- [`comp-reuse-release-equivalence`](references/comp-reuse-release-equivalence.md) - 作为内聚单元发布组件
- [`comp-stable-dependencies`](references/comp-stable-dependencies.md) - 按稳定性方向依赖

### 5. 边界定义 (MEDIUM-HIGH)

- [`bound-humble-object`](references/bound-humble-object.md) - 在架构边界使用谦逊对象
- [`bound-partial-boundaries`](references/bound-partial-boundaries.md) - 当完全分离为时过早时使用部分边界
- [`bound-boundary-cost-awareness`](references/bound-boundary-cost-awareness.md) - 权衡边界成本与无知成本
- [`bound-main-component`](references/bound-main-component.md) - 将主组件视为应用程序的插件
- [`bound-defer-decisions`](references/bound-defer-decisions.md) - 推迟框架和数据库决策
- [`bound-service-internal-architecture`](references/bound-service-internal-architecture.md) - 服务必须具有内部清洁架构

### 6. 接口适配器 (MEDIUM)

- [`adapt-controller-thin`](references/adapt-controller-thin.md) - 保持控制器纤薄
- [`adapt-presenter-formats`](references/adapt-presenter-formats.md) - 呈现器为视图格式化数据
- [`adapt-gateway-abstraction`](references/adapt-gateway-abstraction.md) - 网关隐藏外部系统细节
- [`adapt-mapper-translation`](references/adapt-mapper-translation.md) - 使用映射器在层之间进行转换
- [`adapt-anti-corruption-layer`](references/adapt-anti-corruption-layer.md) - 为外部系统构建反腐败层

### 7. 框架隔离 (MEDIUM)

- [`frame-domain-purity`](references/frame-domain-purity.md) - 领域层没有框架依赖
- [`frame-orm-in-infrastructure`](references/frame-orm-in-infrastructure.md) - 将ORM使用保留在基础设施层
- [`frame-web-in-infrastructure`](references/frame-web-in-infrastructure.md) - Web框架关注点保留在接口层
- [`frame-di-container-edge`](references/frame-di-container-edge.md) - 依赖注入容器位于边缘
- [`frame-logging-abstraction`](references/frame-logging-abstraction.md) - 在领域接口后抽象日志记录

### 8. 测试架构 (LOW-MEDIUM)

- [`test-tests-are-architecture`](references/test-tests-are-architecture.md) - 测试是系统架构的一部分
- [`test-testable-design`](references/test-testable-design.md) - 从一开始就设计可测试性
- [`test-layer-isolation`](references/test-layer-isolation.md) - 独立测试每一层
- [`test-boundary-verification`](references/test-boundary-verification.md) - 使用测试验证架构边界

## 如何使用

阅读单个参考文件以获取详细说明和代码示例：

- [部分定义](references/_sections.md) - 类别结构和影响级别
- [规则模板](assets/templates/_template.md) - 添加新规则的模板

## 参考文件

| 文件 | 描述 |
|------|------|
| [references/_sections.md](references/_sections.md) | 类别定义和排序 |
| [assets/templates/_template.md](assets/templates/_template.md) | 新规则的模板 |
| [metadata.json](metadata.json) | 版本和参考信息 |
