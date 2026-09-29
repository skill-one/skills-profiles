---
name: nestjs-best-practices
description: 构建生产就绪型应用程序的 NestJS 最佳实践和架构模式。在编写、审查或重构 NestJS 代码时，应使用此技能以确保模块、依赖注入、安全性和性能的正确模式。
---

# NestJS 最佳实践

NestJS 应用的全面最佳实践指南。包含 10 个类别中的 40 条规则，按影响程度排序，以指导自动化重构和代码生成。

## 应用场景

在以下情况下参考这些指南：

- 编写新的 NestJS 模块、控制器或服务
- 实现身份验证和授权
- 审查代码以发现架构和安全问题
- 重构现有的 NestJS 代码库
- 优化性能或数据库查询
- 构建微服务架构

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 架构 | CRITICAL | `arch-` |
| 2 | 依赖注入 | CRITICAL | `di-` |
| 3 | 错误处理 | HIGH | `error-` |
| 4 | 安全 | HIGH | `security-` |
| 5 | 性能 | HIGH | `perf-` |
| 6 | 测试 | MEDIUM-HIGH | `test-` |
| 7 | 数据库 & ORM | MEDIUM-HIGH | `db-` |
| 8 | API 设计 | MEDIUM | `api-` |
| 9 | 微服务 | MEDIUM | `micro-` |
| 10 | DevOps & 部署 | LOW-MEDIUM | `devops-` |

## 快速参考

### 1. 架构 (CRITICAL)

- `arch-avoid-circular-deps` - 避免 循环模块依赖
- `arch-feature-modules` - 按 功能组织，而非 技术层级
- `arch-module-sharing` - 正确的模块导出/导入，避免重复提供者
- `arch-single-responsibility` - 专注服务而非 "神服务"
- `arch-use-repository-pattern` - 抽象数据库逻辑以增强可测试性
- `arch-use-events` - 使用事件驱动架构实现解耦

### 2. 依赖注入 (CRITICAL)

- `di-avoid-service-locator` - 避免 服务定位器 反模式
- `di-interface-segregation` - 接口分离原则 (ISP)
- `di-liskov-substitution` - 里氏替换原则 (LSP)
- `di-prefer-constructor-injection` - 构造函数优于 属性注入
- `di-scope-awareness` - 理解 单例/请求/瞬时 作用域
- `di-use-interfaces-tokens` - 使用 注入令牌处理接口

### 3. 错误处理 (HIGH)

- `error-use-exception-filters` - 中央化异常处理
- `error-throw-http-exceptions` - 使用 NestJS HTTP 异常
- `error-handle-async-errors` - 正确处理 异步错误

### 4. 安全 (HIGH)

- `security-auth-jwt` - 安全的 JWT 身份验证
- `security-validate-all-input` - 使用 class-validator 进行验证
- `security-use-guards` - 身份验证和授权守卫
- `security-sanitize-output` - 防止 XSS 攻击
- `security-rate-limiting` - 实现速率限制

### 5. 性能 (HIGH)

- `perf-async-hooks` - 正确的 异步生命周期钩子
- `perf-use-caching` - 实现缓存策略
- `perf-optimize-database` - 优化数据库查询
- `perf-lazy-loading` - 懒加载模块以加快启动速度

### 6. 测试 (MEDIUM-HIGH)

- `test-use-testing-module` - 使用 NestJS 测试工具
- `test-e2e-supertest` - 使用 Supertest 进行 E2E 测试
- `test-mock-external-services` - 模拟外部依赖

### 7. 数据库 & ORM (MEDIUM-HIGH)

- `db-use-transactions` - 事务管理
- `db-avoid-n-plus-one` - 避免 N+1 查询问题
- `db-use-migrations` - 使用迁移处理模式变更

### 8. API 设计 (MEDIUM)

- `api-use-dto-serialization` - DTO 和响应序列化
- `api-use-interceptors` - 跨切面关注点
- `api-versioning` - API 版本化策略
- `api-use-pipes` - 使用 管道进行输入转换

### 9. 微服务 (MEDIUM)

- `micro-use-patterns` - 消息和事件模式
- `micro-use-health-checks` - 用于编排的健康检查
- `micro-use-queues` - 背景任务处理

### 10. DevOps & 部署 (LOW-MEDIUM)

- `devops-use-config-module` - 环境配置
- `devops-use-logging` - 结构化日志
- `devops-graceful-shutdown` - 零停机时间部署

## 如何使用

阅读单个规则文件以获取详细说明和代码示例：

```
rules/arch-avoid-circular-deps.md
rules/security-validate-all-input.md
rules/_sections.md
```

每个规则文件包含：
- 规则重要性的简要说明
- 带说明的 错误代码示例
- 带说明的正确代码示例
- 额外上下文和参考

## 完整编译文档

要查看包含所有规则的单个文档的完整指南，请参阅
[仓库中的 AGENTS.md](https://github.com/Kadajett/agent-nestjs-skills/blob/main/AGENTS.md)。
