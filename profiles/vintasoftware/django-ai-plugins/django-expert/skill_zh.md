# Django 专家

## 概述

本技能为 Django 后端开发提供专家级指导，全面涵盖模型、视图、Django REST Framework、表单、认证、测试和性能优化。它遵循官方 Django 最佳实践和现代 Python 惯例，帮助您构建健壮、可维护的应用程序。

**主要功能：**
- 使用优化的 ORM 模式进行模型设计
- 视图实现（FBV、CBV、DRF 视图集）
- Django REST Framework API 开发
- 查询优化和性能调优
- 认证和权限
- 测试策略和模式
- 安全最佳实践

## 何时使用

在遇到以下触发器时调用此技能：

**模型与数据库工作：**
- "为...创建 Django 模型"
- "优化此查询集/数据库查询"
- "生成迁移文件..."
- "设计数据库模式..."
- "修复 N+1 查询问题"

**视图与 API 开发：**
- "为...创建 API 端点"
- "构建一个执行...的 Django 视图"
- "实现 DRF 序列化器/视图集"
- "为 API 添加过滤/分页"

**认证与安全：**
- "实现认证/权限"
- "创建自定义用户模型"
- "保护此端点/视图"

**测试与质量：**
- "为这个 Django 应用编写测试"
- "调试此 Django 错误/问题"
- "审查 Django 代码以查找问题"

**性能与优化：**
- "这个 Django 视图很慢"
- "优化数据库查询"
- "为...添加缓存"

**生产部署：**
- "将 Django 部署到生产环境"
- "为 Django 配置生产环境"
- "为 Django 设置 HTTPS/SSL"
- "生产环境设置清单"
- "配置生产数据库/缓存"

## 指令

处理 Django 开发请求时，请遵循以下工作流程：

### 1. 分析请求并收集上下文

**识别任务类型：**
- 模型设计（数据库模式、关系、迁移）
- 视图/API 开发（FBV、CBV、DRF 视图集、序列化器）
- 查询优化（N+1 问题、数据库性能）
- 认证/权限（用户模型、访问控制）
- 测试（单元测试、集成测试、数据集）
- 安全审查（CSRF、XSS、SQL 注入、权限）
- 生产部署（设置、HTTPS、数据库、缓存、监控）
- 模板渲染（Django 模板、上下文处理器）

**利用现有上下文：**
- 如果 `django-ai-boost` MCP 服务器可用，使用它来理解项目结构和现有模式
- 阅读相关现有代码以了解惯例
- 检查 Django 版本以考虑兼容性问题

### 2. 加载相关参考文档

根据任务类型，参考适当的捆绑文档：

- **模型/ORM 工作** -> `references/models-and-orm.md`
  - 模型设计模式和字段选择
  - 关系配置（ForeignKey、ManyToMany）
  - 自定义管理器和 QuerySet 方法
  - 迁移策略

- **视图/API 开发** -> `references/views-and-urls.md` + `references/drf-guidelines.md`
  - FBV 与 CBV 的决策标准
  - DRF 序列化器、视图集和路由器
  - URL 配置模式
  - 中间件和请求/响应处理

- **性能问题** -> `references/performance-optimization.md`
  - 查询优化技术（select_related、prefetch_related）
  - 缓存策略（Redis、Memcached、数据库缓存）
  - 数据库索引和查询分析
  - 连接池和异步模式

- **生产部署** -> `references/production-deployment.md`
  - 关键设置（DEBUG、SECRET_KEY、ALLOWED_HOSTS）
  - HTTPS 和 SSL/TLS 配置
  - 数据库和缓存配置
  - 静态/媒体文件服务
  - 错误监控和日志记录
  - 部署流程和健康检查

- **安全问题** -> `references/security-checklist.md`
  - CSRF/XSS/SQL 注入防护
  - 认证和授权模式
  - 安全配置实践
  - 输入验证和清理

- **测试任务** -> `references/testing-strategies.md`
  - 测试结构和组织
  - 数据集和工厂
  - 模拟外部依赖
  - 测试数据库优化
  - CI/CD 集成

### 3. 遵循 Django 最佳实践进行实现

**代码质量标准：**
- 遵循 PEP 8 和 Django 编码风格
- 尽可能使用 Django 内建功能而非第三方包
- 保持视图简洁，使用服务/管理器处理业务逻辑
- 使用描述性变量名，为复杂逻辑添加文档字符串
- 使用适当的异常处理来优雅地处理错误

**Django 特定模式：**
- 使用 `select_related()` 处理 ForeignKey/OneToOne，使用 `prefetch_related()` 处理反向 ForeignKey/M2M
- 利用类视图和混入进行代码复用
- 使用 Django 表单/序列化器进行验证
- 遵循 Django 的迁移工作流程（切勿编辑已应用的迁移）
- 使用 Django 的内建安全功能（CSRF 令牌、认证装饰器）

**API 开发（DRF）：**
- 使用 ModelSerializer 进行标准 CRUD 操作
- 实现适当的分页和过滤
- 使用合适的权限类
- 遵循 RESTful 规范进行端点设计
- 在进行破坏性变更时版本 API

### 4. 验证和测试

在呈现解决方案之前：

**代码审查：**
- 检查 N+1 查询问题（在脑海中使用 Django Debug Toolbar）
- 验证适当的错误处理和边缘情况
- 确保遵循安全最佳实践
- 确认迁移干净且可逆

**测试考虑：**
- 建议或编写新功能的适当测试
- 验证关键路径的测试覆盖率
- 检查数据集/工厂的可维护性

**性能检查：**
- 审查数据库查询的效率
- 考虑缓存机会
- 验证数据库索引的正确使用

## 捆绑资源

**references/** - 根据需要将全面的 Django 文档加载到上下文中

这些参考文件提供了超出此 SKILL.md 概述的详细指导：

- **`references/models-and-orm.md`** (~11k 字)
  - 模型字段类型和最佳实践
  - 关系配置（ForeignKey、OneToOne、ManyToMany）
  - 自定义管理器和 QuerySet 方法
  - 迁移模式和常见陷阱
  - 数据库级约束和索引

- **`references/views-and-urls.md`** (~17k 字)
  - FBV 与 CBV 的权衡
  - CBV 混入和继承模式
  - URL 路由和反向解析
  - 中间件实现
  - 请求/响应生命周期

- **`references/drf-guidelines.md`** (~18k 字)
  - 序列化器模式（ModelSerializer、嵌套序列化器）
  - 视图集和路由器配置
  - 分页、过滤和搜索
  - 认证和权限类
  - API 版本化策略
  - API 性能优化

- **`references/testing-strategies.md`** (~18k 字)
  - 测试组织和结构
  - 工厂模式与数据集
  - 测试视图、模型和序列化器
  - 模拟外部服务
  - 测试数据库优化
  - CI/CD 集成

- **`references/security-checklist.md`** (~12k 字)
  - CSRF 保护实现
  - XSS 防护技术
  - SQL 注入防御
  - 认证最佳实践
  - 权限和授权模式
  - 安全设置配置

- **`references/performance-optimization.md`** (~14k 字)
  - 查询优化（select_related、prefetch_related、only、defer）
  - 数据库索引策略
  - 缓存层（Redis、Memcached、数据库缓存）
  - 数据库连接池
  - 分析和监控工具
  - 异步视图和后台任务

- **`references/production-deployment.md`** (~20k 字)
  - 关键设置（DEBUG、SECRET_KEY、ALLOWED_HOSTS）
  - 数据库配置和连接池
  - HTTPS/SSL 配置和安全头
  - 静态和媒体文件服务
  - 使用 Redis/Memcached 的缓存
  - 生产环境邮件配置
  - 使用 Sentry 的错误监控
  - 日志记录和健康检查
  - 零停机时间部署策略

- **`references/examples.md`** - 实际实现示例
  - 使用自定义管理器的模型设计
  - N+1 查询优化
  - DRF API 端点实现
  - 编写 Django 测试

## 其他说明

**Django 版本兼容性：**
- 考虑 LTS 版本（4.2、5.2）用于生产环境
- 升级时检查弃用警告
- 使用 `django-upgrade` 工具进行自动迁移

**常见陷阱避免：**
- 循环导入（使用延迟引用）
- 关系缺少 `related_name`
- 忘记为频繁查询的字段添加数据库索引
- 使用 `get()` 而无异常处理
- 模板和序列化器中的 N+1 查询
