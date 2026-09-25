# Context7 文档查询技能

通过 Context7 REST API 获取当前库文档、API 参考 和 代码示例。

## 使用场景

当用户询问库 API、框架模式或版本特定行为时，使用此技能。触发条件：

- 库问题："如何使用 [库]？"、"[库] API 文档"、"[库] 模式"
- 导入语句：`import`、`require`、`from` 后跟库名称
- 框架特定主题：钩子、路由、中间件、ORM 查询、模式定义

## 不适用场景

- 通用编程概念（闭包、递归、设计模式）
- 代码审查或重构任务
- 调试业务逻辑
- 在没有库特定问题的前提下从头编写脚本

## 核心工作流程

1. **搜索库 ID**：
   ```bash
   scripts/context7.sh search "库名称"
   ```

2. **选择最佳结果**：选择得分最高且描述最相关的 ID。优先选择官方来源（例如，`/vercel/next.js` 而非社区分支）。

3. **获取聚焦主题的文档**：
   ```bash
   scripts/context7.sh docs "<库ID>" "<主题>" "<模式>"
   ```

始终从用户问题中提取特定主题。对于 "React Suspense 如何与服务器组件一起工作？"，使用主题 `suspense server components`。

## 参数

| 参数 | 必填 | 描述 |
|-------|------|------|
| `library-id` | 是 | 来自搜索结果，格式 `/vendor/library` |
| `topic` | 否 | 从用户查询中提取的聚焦区域（例如，`hooks`、`routing`、`validation`） |
| `mode` | 否 | `code`（默认）用于 API 参考；`info` 用于概念指南 |

## 示例

```bash
# React 钩子 API
scripts/context7.sh search "react"
scripts/context7.sh docs "/facebook/react" "hooks" "code"

# Next.js App Router 概念指南
scripts/context7.sh search "nextjs"
scripts/context7.sh docs "/vercel/next.js" "app router" "info"

# Django ORM 查询
scripts/context7.sh search "django"
scripts/context7.sh docs "/django/django" "queryset filter" "code"

# Laravel Eloquent 关系
scripts/context7.sh search "laravel"
scripts/context7.sh docs "/laravel/framework" "eloquent relationships" "code"
```

## 环境配置

设置 `CONTEXT7_API_KEY` 以获得更高的速率限制（可选）：

```bash
export CONTEXT7_API_KEY="your-api-key"
```

---

> **贡献指南**：https://github.com/netresearch/context7-skill
