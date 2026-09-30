---
name: laravel-best-practices
description: 在编写、审阅或重构 Laravel PHP 代码时，始终应用此技能。这包括创建或修改控制器、模型、数据迁移、表单请求（Form Requests）、策略（Policies）、任务（Jobs）、计划执行的命令、服务类（Service classes）以及 Eloquent 查询。当涉及 N+1 问题与查询性能优化、缓存策略、授权与安全模式、验证、错误处理、队列与任务配置、路由定义以及架构决策时，均应触发使用此技能。在 Laravel 代码审查以及重构现有 Laravel 代码以遵循最佳实践时，也应使用本技能。它涵盖所有涉及 Laravel 后端 PHP 代码模式的任务。
---

# Laravel 最佳实践

Laravel 最佳实践，以规则文件索引的形式组织。每个规则文件都解释了应该做什么以及为什么这样做。有关确切的 API 语法，请使用 `search-docs` 进行验证。

## 首先保持一致性

在应用任何规则之前，检查应用程序已经做了什么。Laravel 提供了多种有效的做法，最佳选择是代码库已经使用的做法，即使另一种模式在理论上可能更好。不一致性比次优模式更糟糕。

检查兄弟文件、相关的控制器、模型或测试中已建立的模式。如果存在，请遵循它。不要引入第二种方式。这些规则是在尚无模式存在时使用的默认值，而不是覆盖。

## 如何应用

1.  检查更改的文件、附近代码、项目配置和相关的测试，以查找已建立的模式。仅当存在正确性或安全缺陷时才偏离，并明确指出这种偏离。
2.  将每个受影响的关注点映射到下方的规则索引。编辑前阅读每个映射的规则文件。跳过不相关的规则文件。
3.  进行最小的连贯更改。保持应用程序的架构和命名，而不是为同一工作引入第二种模式。
4.  使用 `search-docs` 验证与安装版本相关的 Laravel API，或者在无法获取时检查已安装的框架。
5.  当更改值得时，首先运行最窄的相关测试，然后运行项目的格式化和静态分析检查。
6.  完成前，重新阅读与每个映射的规则对应的差异。

## 规则索引

跨切面更改通常需要多个规则文件。

| 关注点 | 阅读 |
| --- | --- |
| 查询计数、预加载、索引、大数据集 | [`rules/db-performance.md`](rules/db-performance.md) |
| 子查询、聚合、复杂的排序和查询计划 | [`rules/advanced-queries.md`](rules/advanced-queries.md) |
| 模型、关系、作用域、类型转换 | [`rules/eloquent.md`](rules/eloquent.md) |
| 身份验证、授权、输入安全、密钥、上传 | [`rules/security.md`](rules/security.md) |
| 表单请求和验证规则 | [`rules/validation.md`](rules/validation.md) |
| 控制器、路由绑定、资源、中间件 | [`rules/routing.md`](rules/routing.md) |
| 模式更改、列、外键、索引 | [`rules/migrations.md`](rules/migrations.md) |
| 任务、重试、唯一性、批次、Horizon | [`rules/queue-jobs.md`](rules/queue-jobs.md) |
| 缓存生命周期、失效、锁、缓存 | [`rules/caching.md`](rules/caching.md) |
| 出站请求、重试、超时、模拟 | [`rules/http-client.md`](rules/http-client.md) |
| 异常、报告、渲染、日志上下文 | [`rules/error-handling.md`](rules/error-handling.md) |
| 事件和通知 | [`rules/events-notifications.md`](rules/events-notifications.md) |
| 可发送邮件和邮件断言 | [`rules/mail.md`](rules/mail.md) |
| 定时任务和重叠保护 | [`rules/scheduling.md`](rules/scheduling.md) |
| 集合、惰性迭代、批量操作 | [`rules/collections.md`](rules/collections.md) |
| Blade 组件、属性、作曲家 | [`rules/blade-views.md`](rules/blade-views.md) |
| 环境值和应用程序配置 | [`rules/config.md`](rules/config.md) |
| 测试：覆盖率、工厂、模拟和断言 | `testing-best-practices` 技能 |
| 命名、辅助函数、文件边界、PHP 风格 | [`rules/style.md`](rules/style.md) |
| 行为、服务、依赖项、应用程序结构 | [`rules/architecture.md`](rules/architecture.md) |

## 决策规则

- 优先选择框架功能和现有的应用程序抽象，而不是新的辅助函数或依赖项。
- 避免推测性抽象。当提取代码创建清晰的领域边界、消除有意义的重复或使行为可以独立测试时，再提取代码。
- 将数据库访问排除在 Blade 视图之外，并防止在控制器、资源、任务和序列化中隐藏的 N+1 查询。
