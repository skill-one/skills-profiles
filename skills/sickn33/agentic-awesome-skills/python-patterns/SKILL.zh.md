---
name: python-patterns
description: Python 开发原则与决策。框架选择、异步模式、类型提示、项目结构。授人以渔，而非授人以鱼。
---

# Python 模式

> 2025年 Python 开发原则与决策指南。
> **学会思考，而非死记硬背模式。**

## 使用场景
在做出 Python 架构决策、选择框架、设计异步模式或构建 Python 项目时使用此技能。

---

## ⚠️ 如何使用此技能

此技能教授的是**决策原则**，而非固定代码模板。

- 模糊不清时向用户询问框架偏好
- 根据上下文选择异步或同步
- 每次不默认使用同一框架

---

## 1. 框架选择（2025年）

### 决策树

```
你要构建什么？
│
├── API优先 / 微服务
│   └── FastAPI（异步、现代、高效）
│
├── 全栈 Web / CMS / 管理后台
│   └── Django（开箱即用）
│
├── 简单 / 脚本 / 学习
│   └── Flask（极简、灵活）
│
├── AI/ML API 服务
│   └── FastAPI（Pydantic、异步、uvicorn）
│
└── 后台任务
    └── Celery + 任何框架
```

### 对比原则

| 因素 | FastAPI | Django | Flask |
|------|---------|--------|-------|
| **最适合** | API、微服务 | 全栈、CMS | 简单、学习 |
| **异步** | 原生支持 | Django 5.0+ | 通过扩展 |
| **管理后台** | 手动构建 | 内置 | 通过扩展 |
| **ORM** | 自定义选择 | Django ORM | 自定义选择 |
| **学习曲线** | 低 | 中等 | 低 |

### 选择问题清单：
1. 这是纯 API 还是全栈？
2. 是否需要管理后台？
3. 团队是否熟悉异步？
4. 现有基础设施？

---

## 2. 异步与同步决策

### 使用异步的场景

```
当以下情况使用 async def 更好时：
├── I/O 密集型操作（数据库、HTTP、文件）
├── 多并发连接
├── 实时功能
├── 微服务通信
└── FastAPI/Starlette/Django ASGI

def (同步) 更好的场景：
├── CPU 密集型操作
├── 简单脚本
├── 遗留代码库
├── 团队不熟悉异步
└── 阻塞库（无异步版本）
```

### 黄金法则

```
I/O 密集型 → async（等待外部）
CPU 密集型 → sync + multiprocessing（计算）

不要：
├── 随意混合同步和异步
├── 在异步代码中使用同步库
└── 强制异步处理 CPU 工作
```

### 异步库选择

| 需求 | 异步库 |
|------|--------|
| HTTP 客户端 | httpx |
| PostgreSQL | asyncpg |
| Redis | aioredis / redis-py 异步 |
| 文件 I/O | aiofiles |
| 数据库 ORM | SQLAlchemy 2.0 异步，Tortoise |

---

## 3. 类型提示策略

### 使用类型提示的场景

```
始终使用类型提示：
├── 函数参数
├── 返回类型
├── 类属性
├── 公共 API

可以跳过：
├── 局部变量（让推断工作）
├── 一次性脚本
├── 测试（通常）
```

### 常见类型模式

```python
# 这些是模式，理解它们：

# 可选 → 可能是 None
from typing import Optional
def find_user(id: int) -> Optional[User]: ...

# 联合类型 → 多种类型之一
def process(data: str | dict) -> None: ...

# 泛型集合
def get_items() -> list[Item]: ...
def get_mapping() -> dict[str, int]: ...

# Callable
from typing import Callable
def apply(fn: Callable[[int], str]) -> str: ...
```

### Pydantic 用于验证

```
何时使用 Pydantic：
├── API 请求/响应模型
├── 配置/设置
├── 数据验证
├── 序列化

优势：
├── 运行时验证
├── 自动生成 JSON schema
├── 与 FastAPI 原生集成
└── 清晰的错误信息
```

---

## 4. 项目结构原则

### 结构选择

```
小型项目 / 脚本：
├── main.py
├── utils.py
└── requirements.txt

中型 API：
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── schemas/
├── tests/
└── pyproject.toml

大型应用：
├── src/
│   └── myapp/
│       ├── core/
│       ├── api/
│       ├── services/
│       ├── models/
│       └── ...
├── tests/
└── pyproject.toml
```

### FastAPI 结构原则

```
按功能或层级组织：

按层级：
├── routes/（API 端点）
├── services/（业务逻辑）
├── models/（数据库模型）
├── schemas/（Pydantic 模型）
└── dependencies/（共享依赖）

按功能：
├── users/
│   ├── routes.py
│   ├── service.py
│   └── schemas.py
└── products/
    └── ...
```

---

## 5. Django 原则（2025年）

### Django 异步（Django 5.0+）

```
Django 支持异步：
├── 异步视图
├── 异步中间件
├── 异步 ORM（有限）
└── ASGI 部署

何时在 Django 中使用异步：
├── 外部 API 调用
├── WebSocket（Channels）
├── 高并发视图
└── 触发后台任务
```

### Django 最佳实践

```
模型设计：
├── 脂肪模型，瘦视图
├── 使用 managers 处理常见查询
├── 抽象基类处理共享字段

视图：
├── 类视图处理复杂 CRUD
├── 函数视图处理简单端点
├── 使用 viewsets 与 DRF

查询：
├── select_related() 处理外键
├── prefetch_related() 处理多对多
├── 避免 N+1 查询
└── 使用 .only() 获取特定字段
```

---

## 6. FastAPI 原则

### async def vs def in FastAPI

```
使用 async def 的情况：
├── 使用异步数据库驱动
├── 进行异步 HTTP 调用
├── I/O 密集型操作
└── 需要处理并发

使用 def 的情况：
├── 阻塞操作
├── 同步数据库驱动
├── CPU 密集型工作
└── FastAPI 自动在 threadpool 中运行
```

### 依赖注入

```
使用依赖注入：
├── 数据库会话
├── 当前用户 / 认证
├── 配置
├── 共享资源

优势：
├── 可测试性（模拟依赖）
├── 清晰的分离
├── 自动清理（yield）
```

### Pydantic v2 集成

```python
# FastAPI + Pydantic 紧密集成：

# 请求验证
@app.post("/users")
async def create(user: UserCreate) -> UserResponse:
    # user 已被验证
    ...
```

---

## 7. 后台任务

### 选择指南

| 解决方案 | 最适合 |
|----------|--------|
| **BackgroundTasks** | 简单、进程内任务 |
| **Celery** | 分布式、复杂工作流 |
| **ARQ** | 异步、基于 Redis |
| **RQ** | 简单 Redis 队列 |
| **Dramatiq** | 基于 Actor、比 Celery 简单 |

### 何时使用每种方案

```
FastAPI BackgroundTasks：
├── 快速操作
├── 无需持久化
├── 一次性操作
└── 同一进程

Celery/ARQ：
├── 长时运行任务
├── 需要重试逻辑
├── 分布式工作进程
├── 持久化队列
└── 复杂工作流
```

---

## 8. 错误处理原则

### 异常策略

```
在 FastAPI 中：
├── 创建自定义异常类
├── 注册异常处理器
├── 返回一致的错误格式
└── 不暴露内部细节进行日志记录

模式：
├── 在服务中抛出领域异常
├── 在处理器中捕获和转换
└── 客户端获取干净的错误响应
```

### 错误响应哲学

```
包含：
├── 错误码（程序化）
├── 消息（人类可读）
├── 详情（适用时按字段）
└── 不包含堆栈跟踪（安全）
```

---

## 9. 测试原则

### 测试策略

| 类型 | 目的 | 工具 |
|------|------|------|
| **单元测试** | 业务逻辑 | pytest |
| **集成测试** | API 端点 | pytest + httpx/TestClient |
| **端到端测试** | 全流程 | pytest + DB |

### 异步测试

```python
# 使用 pytest-asyncio 进行异步测试

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users")
        assert response.status_code == 200
```

### 测试数据策略

```
常见测试数据：
├── db_session → 数据库连接
├── client → 测试客户端
├── authenticated_user → 带令牌的用户
└── sample_data → 测试数据设置
```

---

## 10. 决策清单

实施前：

- [ ] **询问用户框架偏好？**
- [ ] **为当前场景选择框架？**（不只是默认）
- [ ] **决定异步 vs 同步？**
- [ ] **规划类型提示策略？**
- [ ] **定义项目结构？**
- [ ] **规划错误处理？**
- [ ] **考虑后台任务？**

---

## 11. 应避免的反模式

### ❌ 不要：
- 简单 API 默认使用 Django（FastAPI 可能更好）
- 在异步代码中使用同步库
- 公共 API 跳过类型提示
- 将业务逻辑放在路由/视图
- 忽略 N+1 查询
- 随意混合异步和同步

### ✅ 应：
- 根据上下文选择框架
- 询问异步需求
- 使用 Pydantic 进行验证
- 分离关注点（路由 → 服务 → 仓库）
- 测试关键路径

---

> **记住**：Python 模式是关于为你的特定上下文做出决策。不要复制代码——思考什么最适合你的应用。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少所需输入、权限、安全边界或成功标准，请停止并请求澄清。
