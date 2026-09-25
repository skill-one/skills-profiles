# FastAPI 项目模板

生产就绪的 FastAPI 项目结构，包含异步模式、依赖注入、中间件以及构建高性能 API 的最佳实践。

## 使用此技能的场景

- 从零开始创建新的 FastAPI 项目
- 使用 Python 实现异步 REST API
- 构建高性能的 Web 服务和微服务
- 使用 PostgreSQL、MongoDB 创建异步应用程序
- 设置具有良好结构和测试的 API 项目

## 核心概念

### 1. 项目结构

**推荐布局：**

```
app/
├── api/                    # API 路由
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── users.py
│   │   │   ├── auth.py
│   │   │   └── items.py
│   │   └── router.py
│   └── dependencies.py     # 共享依赖
├── core/                   # 核心配置
│   ├── config.py
│   ├── security.py
│   └── database.py
├── models/                 # 数据库模型
│   ├── user.py
│   └── item.py
├── schemas/                # Pydantic 模式
│   ├── user.py
│   └── item.py
├── services/               # 业务逻辑
│   ├── user_service.py
│   └── auth_service.py
├── repositories/           # 数据访问
│   ├── user_repository.py
│   └── item_repository.py
└── main.py                 # 应用程序入口
```

### 2. 依赖注入

FastAPI 的内置依赖注入系统使用 `Depends`：

- 数据库会话管理
- 身份验证/授权
- 共享业务逻辑
- 配置注入

### 3. 异步模式

正确的异步/await 使用：

- 异步路由处理器
- 异步数据库操作
- 异步后台任务
- 异步中间件

## 详细的工作示例和模式

详细的章节（以 `## 实现模式` 开头）位于 `references/details.md` 中。当上面的导航摘要不足以说明时，请阅读该文件。

## 测试

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# tests/test_users.py
import pytest

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
```
