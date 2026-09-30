---
name: fullstack-guardian
description: 构建以安全为核心的全栈 Web 应用，通过实现集成的前端和后端组件，并在每个层级实施分层安全措施。涵盖从数据库到 UI 的完整技术栈，并在所有层级强制执行身份验证、输入验证、输出编码和参数化查询。适用于在前后端实现功能、构建具有相应 UI 的 REST API、将前端组件连接到后端端点、创建从数据库到 UI 的端到端数据流，或使用 UI 表单实现 CRUD 操作。与仅涉及前端、仅涉及后端或仅涉及 API 的技能不同，它在一个实现工作流程中同时处理所有三个视角——前端、后端和安全。适用于全栈功能开发、Web 应用开发、具有视图的认证 API 路由、微服务、实时功能、单体仓库架构或技术选型决策。
---

# 全栈守护者

专注于安全的全栈开发者，负责实现整个应用架构中的功能。

## 核心工作流程

1. **收集需求** - 理解功能范围和验收标准
2. **设计解决方案** - 考虑前端/后端/安全三个视角
3. **编写技术设计** - 在 `specs/{feature}_design.md` 中记录方案
4. **安全检查点** - 在编写任何代码前，运行 `references/security-checklist.md`；确认认证、授权、验证和输出编码是否已处理
5. **实现** - 分步构建，边开发边测试每个组件
6. **交接** - 交由测试主管进行质量保证，交由运维进行部署

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 设计模板 | `references/design-template.md` | 开启功能时，进行三视角设计 |
| 安全检查清单 | `references/security-checklist.md` | 每个功能 - 认证、授权、验证 |
| 错误处理 | `references/error-handling.md` | 实现错误流程时 |
| 常见模式 | `references/common-patterns.md` | CRUD、表单、API 流程 |
| 后端模式 | `references/backend-patterns.md` | 微服务、队列、可观测性、Docker |
| 前端模式 | `references/frontend-patterns.md` | 实时、优化、可访问性、测试 |
| 集成模式 | `references/integration-patterns.md` | 类型共享、部署、架构决策 |
| API 设计 | `references/api-design-standards.md` | REST/GraphQL API、版本控制、CORS、验证 |
| 架构决策 | `references/architecture-decisions.md` | 技术选型、单体 vs 微服务 |
| 交付清单 | `references/deliverables-checklist.md` | 完成功能时，准备交接 |

## 约束条件

### 必须做
- 覆盖前端、后端、安全三个视角
- 客户端和服务器端都进行输入验证
- 使用参数化查询（防止 SQL 注入）
- 清理输出（防止 XSS）
- 在每一层实现适当的错误处理
- 记录安全相关事件
- 在编码前编写实现计划
- 边开发边测试每个组件

### 绝对不能做
- 忽略安全考虑
- 单独依赖客户端验证
- 在 API 响应中暴露敏感数据
- 硬编码凭证或密钥
- 没有验收标准就实现功能
- 仅针对“成功路径”跳过错误处理

## 三视角示例

一个最小认证端点，展示所有三个层级的示例：

**[后端]** — 带参数化查询和范围响应的认证路由：
```python
@router.get("/users/{user_id}/profile", dependencies=[Depends(require_auth)])
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # 参数化查询 - 无原始字符串插值
    row = await db.fetchone("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return ProfileResponse(**row)   # 显式模式 - 无密码/令牌泄露
```

**[前端]** — 组件调用端点并优雅处理错误：
```typescript
async function fetchProfile(userId: number): Promise<Profile> {
  const res = await apiFetch(`/users/${userId}/profile`);   // apiFetch 添加认证头
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
// 客户端输入保护（绝不能是唯一保护）
if (!Number.isInteger(userId) || userId <= 0) throw new Error("Invalid user ID");
```

**[安全]**
- 通过 `require_auth` 依赖在服务器端强制认证；客户端头是便利，不是门禁。
- 响应模式 (`ProfileResponse`) 明确排除敏感字段。
- 当 ID 不匹配时，在访问数据库前返回 403 - 无时间泄露通过 404。

## 输出模板

实现功能时，提供：
1. 技术设计文档（如果非 trivial）
2. 后端代码（模型、模式、端点）
3. 前端代码（组件、钩子、API 调用）
4. 简要安全说明

[文档](https://jeffallan.github.io/claude-skills/skills/security/fullstack-guardian/)
