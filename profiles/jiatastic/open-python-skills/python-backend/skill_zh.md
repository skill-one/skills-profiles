# python-backend

适用于 FastAPI、SQLAlchemy 和 Upstash 的生产级 Python 后端模式。

## 使用此技能的场景

- 使用 FastAPI 构建 REST API
- 实现 JWT/OAuth2 身份验证
- 设置 SQLAlchemy 异步数据库
- 集成 Redis/Upstash 缓存和速率限制
- 重构 AI 生成的 Python 代码
- 设计 API 模式和项目结构

## 核心原则

1. **以异步优先** - 使用 async/await 进行 I/O 操作
2. **类型注解** - 使用 Pydantic 模型进行验证
3. **依赖注入** - 使用 FastAPI 的 Depends()
4. **快速失败** - 早期验证，使用 HTTPException
5. **默认安全** - 不信任用户输入

## 快速模式

### 项目结构

```
src/
├── auth/
│   ├── router.py      # 端点
│   ├── schemas.py     # Pydantic 模型
│   ├── models.py      # 数据库模型
│   ├── service.py     # 业务逻辑
│   └── dependencies.py
├── posts/
│   └── ...
├── config.py
├── database.py
└── main.py
```

### 异步路由

```python
# BAD - 阻塞事件循环
@router.get("/")
async def bad():
    time.sleep(10)  # 阻塞！

# GOOD - 在线程池中运行
@router.get("/")
def good():
    time.sleep(10)  # 同步函数中可以

# BEST - 非阻塞
@router.get("/")
async def best():
    await asyncio.sleep(10)  # 非阻塞
```

### Pydantic 验证

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    age: int = Field(ge=18)
```

### 依赖注入

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    user = await get_user(payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    return user

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user
```

### SQLAlchemy 异步

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
```

### Redis 缓存

```python
from upstash_redis import Redis

redis = Redis.from_env()

@app.get("/data/{id}")
def get_data(id: str):
    cached = redis.get(f"data:{id}")
    if cached:
        return cached
    data = fetch_from_db(id)
    redis.setex(f"data:{id}", 600, data)
    return data
```

### 速率限制

```python
from upstash_ratelimit import Ratelimit, SlidingWindow

ratelimit = Ratelimit(
    redis=Redis.from_env(),
    limiter=SlidingWindow(max_requests=10, window=60),
)

@app.get("/api/resource")
def protected(request: Request):
    result = ratelimit.limit(request.client.host)
    if not result.allowed:
        raise HTTPException(429, "Rate limit exceeded")
    return {"data": "..."}
```

## 参考资料

有关详细模式的更多信息，请参阅：

| 文档 | 内容 |
|----------|---------|
| `references/fastapi_patterns.md` | 项目结构、异步、Pydantic、依赖注入、测试 |
| `references/security_patterns.md` | JWT、OAuth2、密码哈希、CORS、API 密钥 |
| `references/database_patterns.md` | SQLAlchemy 异步、事务、即时加载、迁移 |
| `references/upstash_patterns.md` | Redis、速率限制、QStash 后台任务 |

## 资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/)
- [Upstash 文档](https://upstash.com/docs)
- [Pydantic 文档](https://docs.pydantic.dev/)
