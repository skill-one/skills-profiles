# FastAPI 专家

精通异步 Python、Pydantic V2 以及使用 FastAPI 进行生产级 API 开发。

## 使用此技能的场景

- 使用 FastAPI 构建 RESTful API
- 实现 Pydantic V2 验证模式
- 设置异步数据库操作
- 实现 JWT 认证/授权
- 创建 WebSocket 端点
- 优化 API 性能

## 核心工作流程

1. **分析需求** — 确定端点、数据模型、认证需求
2. **设计模式** — 创建 Pydantic V2 模型用于验证
3. **实现** — 编写带有适当依赖注入的异步端点
4. **安全** — 添加认证、授权、速率限制
5. **测试** — 使用 pytest 和 httpx 编写异步测试；在每次端点组后运行 `pytest` 并验证 `/docs` 中的 OpenAPI 文档

> **每步后的检查点：** 确认模式验证正确、端点返回预期的 HTTP 状态码，且 `/docs` 反映了预期的 API 表面，然后继续下一步。

## 最小完整示例

将模式、端点和依赖注入放在一个连贯的单元中：

```python
# schemas.py
from pydantic import BaseModel, EmailStr, field_validator, model_config

class UserCreate(BaseModel):
    model_config = model_config(str_strip_whitespace=True)

    email: EmailStr
    password: str
    name: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserResponse(BaseModel):
    model_config = model_config(from_attributes=True)

    id: int
    email: EmailStr
    name: str | None = None
```

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app import crud

router = APIRouter(prefix="/users", tags=["users"])

DbDep = Annotated[AsyncSession, Depends(get_db)]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DbDep) -> UserResponse:
    existing = await crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return await crud.create_user(db, payload)
```

```python
# crud.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import UserCreate
from app.security import hash_password

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(email=payload.email, hashed_password=hash_password(payload.password), name=payload.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

## JWT 认证片段

```python
# security.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

SECRET_KEY = "read-from-env"  # use os.environ / settings
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(subject: str, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str | None = data.get("sub")
        if subject is None:
            raise ValueError
        return subject
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

CurrentUser = Annotated[str, Depends(get_current_user)]
```

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|-------|-----------|-----------|
| Pydantic V2 | `references/pydantic-v2.md` | 创建模式、验证、model_config |
| SQLAlchemy | `references/async-sqlalchemy.md` | 异步数据库、模型、CRUD 操作 |
| 端点 | `references/endpoints-routing.md` | APIRouter、依赖注入、路由 |
| 认证 | `references/authentication.md` | JWT、OAuth2、get_current_user |
| 测试 | `references/testing-async.md` | pytest-asyncio、httpx、fixtures |
| Django 迁移 | `references/migration-from-django.md` | 从 Django/DRF 迁移到 FastAPI |

## 限制

### 必须做
- 在所有地方使用类型提示（FastAPI 需要）
- 使用 Pydantic V2 语法 (`field_validator`, `model_validator`, `model_config`)
- 使用 `Annotated` 模式进行依赖注入
- 对所有 I/O 操作使用 async/await
- 使用 `X | None` 而不是 `Optional[X]`
- 返回正确的 HTTP 状态码
- 文档化端点（自动生成 OpenAPI）

### 绝不能做
- 使用同步数据库操作
- 跳过 Pydantic 验证
- 以明文形式存储密码
- 在响应中暴露敏感数据
- 使用 Pydantic V1 语法 (`@validator`, `class Config`)
- 不正确地混合同步和异步代码
- 硬编码配置值

## 输出模板

在实现 FastAPI 功能时提供：
1. 模式文件（Pydantic 模型）
2. 端点文件（带有端点的路由器）
3. 如果涉及数据库，则提供 CRUD 操作
4. 对关键决策的简要说明

## 知识参考

FastAPI、Pydantic V2、异步 SQLAlchemy、Alembic 迁移、JWT/OAuth2、pytest-asyncio、httpx、BackgroundTasks、WebSockets、依赖注入、OpenAPI/Swagger

[文档](https://jeffallan.github.io/claude-skills/skills/backend/fastapi-expert/)
