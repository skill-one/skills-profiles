# FastAPI 技能

使用 Pydantic v2、SQLAlchemy 2.0 异步和 JWT 认证进行生产测试的 FastAPI 模式。

**最新版本**（截至 2026 年 1 月验证）：
- FastAPI: 0.128.0
- Pydantic: 2.11.7
- SQLAlchemy: 2.0.30
- Uvicorn: 0.35.0
- python-jose: 3.3.0

**要求**：
- Python 3.9+（FastAPI 0.125.0 中不再支持 Python 3.8）
- Pydantic v2.7.0+（FastAPI 0.128.0 中完全移除了对 Pydantic v1 的支持）

---

## 快速入门

### 使用 uv 设置项目

```bash
# 创建项目
uv init my-api
cd my-api

# 添加依赖
uv add fastapi[standard] sqlalchemy[asyncio] aiosqlite python-jose[cryptography] passlib[bcrypt]

# 运行开发服务器
uv run fastapi dev src/main.py
```

### 最小可工作示例

```python
# src/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="我的 API")

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/items")
async def create_item(item: Item):
    return item
```

运行：`uv run fastapi dev src/main.py`

文档可在：`http://127.0.0.1:8000/docs`

---

## 项目结构（基于领域）

为了可维护性，按领域组织而不是按文件类型组织：

```
my-api/
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用初始化
│   ├── config.py            # 全局设置
│   ├── database.py          # 数据库连接
│   │
│   ├── auth/                # 认证领域
│   │   ├── __init__.py
│   │   ├── router.py        # 认证端点
│   │   ├── schemas.py       # Pydantic 模型
│   │   ├── models.py        # SQLAlchemy 模型
│   │   ├── service.py       # 业务逻辑
│   │   └── dependencies.py  # 认证依赖
│   │
│   ├── items/               # 项目领域
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   └── service.py
│   │
│   └── shared/              # 共享工具
│       ├── __init__.py
│       └── exceptions.py
└── tests/
    └── test_main.py
```

---

## 核心模式

### Pydantic 模式（验证）

```python
# src/items/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class ItemStatus(str, Enum):
    DRAFT = "草稿"
    PUBLISHED = "已发布"
    ARCHIVED = "已归档"

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="价格必须为正数")
    status: ItemStatus = ItemStatus.DRAFT

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    status: ItemStatus | None = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**要点**：
- 使用 `Field()` 进行验证约束
- 分离创建/更新/响应模式
- `from_attributes=True` 启用 SQLAlchemy 模型转换
- 使用 `str | None`（Python 3.10+）而不是 `Optional[str]`

### SQLAlchemy 模型（数据库）

```python
# src/items/models.py
from sqlalchemy import String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.database import Base
from src.items.schemas import ItemStatus

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[ItemStatus] = mapped_column(
        SQLEnum(ItemStatus), default=ItemStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
```

### 数据库设置（异步 SQLAlchemy 2.0）

```python
# src/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 路由模式

```python
# src/items/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.items import schemas, models

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=list[schemas.ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Item).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Item).where(models.Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="项目未找到")
    return item

@router.post("", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: schemas.ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    item = models.Item(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
```

### 主应用

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import engine, Base
from src.items.router import router as items_router
from src.auth.router import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭：清理（如果需要）

app = FastAPI(title="我的 API", lifespan=lifespan)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 你的前端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth_router)
app.include_router(items_router)
```

---

## JWT 认证

### 认证模式

```python
# src/auth/schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None
```

### 认证服务

```python
# src/auth/service.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return None
```

### 认证依赖

```python
# src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.auth import service, models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = service.decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(
        select(models.User).where(models.User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user
```

### 认证路由

```python
# src/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.auth import schemas, models, service
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 检查现有用户
    result = await db.execute(
        select(models.User).where(models.User.email == user_in.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已注册")

    user = models.User(
        email=user_in.email,
        hashed_password=service.hash_password(user_in.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(models.User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    access_token = service.create_access_token(data={"sub": str(user.id)})
    return schemas.Token(access_token=access_token)

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
```

### 保护路由

```python
# 在任何路由中
from src.auth.dependencies import get_current_user
from src.auth.models import User

@router.post("/items")
async def create_item(
    item_in: schemas.ItemCreate,
    current_user: User = Depends(get_current_user),  # 需要认证
    db: AsyncSession = Depends(get_db)
):
    item = models.Item(**item_in.model_dump(), user_id=current_user.id)
    # ...
```

---

## 配置

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./database.db"
    SECRET_KEY: str = "在生产环境中更改你的密钥"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

创建 `.env`：
```
DATABASE_URL=sqlite+aiosqlite:///./database.db
SECRET_KEY=你的超级密钥在这里
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 严格规则

### 必须做

1. **将 Pydantic 模式与 SQLAlchemy 模式分离** - 不同的工作，不同的文件
2. **使用异步进行 I/O 操作** - 数据库，HTTP 调用，文件访问
3. **使用 Pydantic Field() 进行验证** - 约束，默认值，描述
4. **使用依赖注入** - `Depends()` 用于数据库，认证，验证
5. **返回正确的状态码** - 创建返回 201，删除返回 204 等

### 绝对不要做

1. **绝对不要在异步路由中使用阻塞调用** - 不要 `time.sleep()`，使用 `asyncio.sleep()`
2. **绝对不要在路由中放置业务逻辑** - 使用服务层
3. **绝对不要硬编码密钥** - 使用环境变量
4. **绝对不要跳过验证** - 始终使用 Pydantic 模式
5. **在生产环境中绝对不要使用 `*` 在 CORS 原点上** - 指定确切的源

---

## 已知问题预防

此技能可防止来自官方 FastAPI GitHub 和发布说明的 **7** 个已知问题。

### 问题 #1：表单数据丢失字段设置元数据

**错误**：使用 `model.model_fields_set` 时，当使用 `Form()` 时会包含默认值
**来源**：[GitHub 问题 #13399](https://github.com/fastapi/fastapi/issues/13399)
**发生原因**：表单数据解析会预加载默认值并将其传递给验证器，这使得无法区分用户显式设置的字段和使用默认值的字段。此错误仅影响表单数据，不影响 JSON 正文数据。

**预防**：
```python
# ✗ 避免：使用 Form 的 Pydantic 模式（在 0.114.0+ 中会破坏字段设置元数据）
from typing import Annotated
from fastapi import Form

@app.post("/form")
async def endpoint(model: Annotated[MyModel, Form()]):
    fields = model.model_fields_set  # 不可靠！❌

# ✓ 使用：单独的表单字段或 JSON 正文
@app.post("/form-individual")
async def endpoint(
    field_1: Annotated[bool, Form()] = True,
    field_2: Annotated[str | None, Form()] = None
):
    # 你确切地知道提供了什么 ✓

# ✓ 或者：当需要元数据时使用 JSON 正文
@app.post("/json")
async def endpoint(model: MyModel):
    fields = model.model_fields_set  # 正确 ✓
```

### 问题 #2：BackgroundTasks 被自定义响应静默覆盖

**错误**：通过 `BackgroundTasks` 依赖添加的背景任务不会运行
**来源**：[GitHub 问题 #11215](https://github.com/fastapi/fastapi/issues/11215)
**发生原因**：当你返回一个具有 `background` 参数的自定义 `Response` 时，它会覆盖注入的 `BackgroundTasks` 依赖中的所有任务。这没有记录，并会导致静默失败。

**预防**：
```python
# ✗ 错误：混合使用这两种机制
from fastapi import BackgroundTasks
from starlette.responses import Response, BackgroundTask

@app.get("/")
async def endpoint(tasks: BackgroundTasks):
    tasks.add_task(send_email)  # 这将被丢失！❌
    return Response(
        content="Done",
        background=BackgroundTask(log_event)  # 只有这个会运行
    )

# ✓ 正确：仅使用 BackgroundTasks 依赖
@app.get("/")
async def endpoint(tasks: BackgroundTasks):
    tasks.add_task(send_email)
    tasks.add_task(log_event)
    return {"status": "done"}  # 所有任务都会运行 ✓

# ✓ 或者：仅使用 Response background（但不能注入依赖）
@app.get("/")
async def endpoint():
    return Response(
        content="Done",
        background=BackgroundTask(log_event)
    )
```

**规则**：选择一种机制并坚持使用。不要混合注入的 `BackgroundTasks` 和 `Response(background=...)`。

### 问题 #3：可选表单字段在 TestClient 中破坏（回归）

**错误**：`422: "输入应该是 'abc' 或 'def'"` 对于可选的 Literal 字段
**来源**：[GitHub 问题 #12245](https://github.com/fastapi/fastapi/issues/12245)
**发生原因**：从 FastAPI 0.114.0 开始，具有 `Literal` 类型的可选表单字段在通过 TestClient 传递 `None` 时会失败验证。在 0.113.0 中可以工作。

**预防**：
```python
from typing import Annotated, Literal, Optional
from fastapi import Form
from fastapi.testclient import TestClient

# ✗ 问题：可选的 Literal 与 Form（在 0.114.0+ 中会破坏）
@app.post("/")
async def endpoint(
    attribute: Annotated[Optional[Literal["abc", "def"]], Form()
):
    return {"attribute": attribute}

client = TestClient(app)
data = {"attribute": None}  # 或者省略字段
response = client.post("/", data=data)  # 返回 422 ❌

# ✓ 解决方案 1：不要显式传递 None，省略字段
data = {}  # 省略而不是 None
response = client.post("/", data=data)  # 工作 ✓

# ✓ 解决方案 2：避免在可选表单字段中使用 Literal 类型
@app.post("/")
async def endpoint(attribute: Annotated[str | None, Form()] = None):
    # 在应用逻辑中验证
    if attribute and attribute not in ["abc", "def"]:
        raise HTTPException(400, "无效的属性")
```

### 问题 #4：Pydantic v2 路径参数联合类型破坏性变更

**错误**：具有 `int | str` 的路径参数在 Pydantic v2 中始终解析为 `str`
**来源**：[GitHub 问题 #11251](https://github.com/fastapi/fastapi/issues/11251) | 社区贡献
**发生原因**：从 Pydantic v1 迁移到 Pydantic v2 时的重大破坏性变更。路径/查询参数中的 `str` 联合类型现在始终解析为 `str`（v1 中正确工作）。

**预防**：
```python
from uuid import UUID

# ✗ 问题：路径参数中的联合类型包含 str
@app.get("/int/{path}")
async def int_path(path: int | str):
    return str(type(path))
    # Pydantic v1: 返回 <class 'int'> 对于 "123"
    # Pydantic v2: 返回 <class 'str'> 对于 "123" ❌

@app.get("/uuid/{path}")
async def uuid_path(path: UUID | str):
    return str(type(path))
    # Pydantic v1: 返回 <class 'uuid.UUID'> 对于有效的 UUID
    # Pydantic v2: 返回 <class 'str'> ❌

# ✓ 正确：避免在路径/查询参数中使用联合类型包含 str
@app.get("/int/{path}")
async def int_path(path: int):
    return str(type(path))  # 正确 ✓

# ✓ 替代方案：如果需要类型转换，使用验证器
from pydantic import field_validator

class PathParams(BaseModel):
    path: int | str

    @field_validator('path')
    def coerce_to_int(cls, v):
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v
```

### 问题 #5：Annotated 与 ForwardRef 破坏 OpenAPI 生成

**错误**：OpenAPI 模式缺失或不正确的 OpenAPI 模式
**来源**：[GitHub 问题 #13056](https://github.com/fastapi/fastapi/issues/13056)
**发生原因**：当使用 `Annotated` 与 `Depends()` 和前向引用（从 `__future__ import annotations`）时，OpenAPI 模式生成会失败或生成不正确的模式。

**预防**：
```python
# ✗ 问题：前向引用与 Depends
from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def get_potato() -> Potato:  # 前向引用
    return Potato(color='red', size=10)

@app.get('/')
async def read_root(potato: Annotated[Potato, Depends(get_potato)]):
    return {'Hello': 'World'}
# OpenAPI 模式不包含 Potato 定义正确 ✓

@dataclass
class Potato:
    color: str
    size: int

# ✓ 解决方案 1：不要在路由文件中使用 __future__ annotations
# 删除：from __future__ import annotations

# ✓ 解决方案 анимация 2：使用字符串字面量作为类型提示
def get_potato() -> "Potato":
    return Potato(color='red', size=10)

# ✓ 解决方案 3：在依赖中使用之前定义类
@dataclass
class Potato:
    color: str
    size: int

def get_potato() -> Potato:  # 现在可以工作 ✓
```

### 问题 #6：Pydantic v2 路径参数联合类型破坏性变更

**错误**：路径参数具有 `int | str` 在 Pydantic v2 中始终解析为 `str`
**来源**：[GitHub 问题 #11251](https://github.com/fastapi/fastapi/issues/11251) | 社区贡献
**发生原因**：从 Pydantic v1 迁移到 Pydantic v2 时的重大破坏性变更。路径/查询参数中的 `str` 联合类型现在始终解析为 `str`（v1 中正确工作）。

**预防**：
```python
from uuid import UUID

# ✗ 问题：路径参数中的联合类型包含 str
@app.get("/int/{path}")
async def int_path(path: int | str):
    return str(type(path))
    # Pydantic v1: 返回 <class 'int'> 对于 "123"
    # Pydantic v2: 返回 <class 'str'> 对于 "123" ❌

@app.get("/uuid/{path}")
async def uuid_path(path: UUID | str):
    return str(type(path))
    # Pydantic v1: 返回 <class 'uuid.UUID'> 对于有效的 UUID
    # Pydantic v2: 返回 <class 'str'> ❌

# ✓ 正确：避免在路径/查询参数中使用联合类型包含 str
@app.get("/int/{path}")
async def int_path(path: int):
    return str(type(path))  # 正确 ✓

# ✓ 替代方案：如果需要类型转换，使用验证器
from pydantic import field_validator

class PathParams(BaseModel):
    path: int | str

    @field_validator('path')
    def coerce_to_int(cls, v):
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v
```

### 问题 #7：field_validator 中的 ValueError 返回 500 而不是 422

**错误**：在 Pydantic `@field_validator` 中引发 `ValueError` 时，FastAPI 返回 500 Internal Server Error 而不是预期的 422 Unprocessable Entity 验证错误
**来源**：[GitHub 讨论 #10779](https://github.com/fastapi/fastapi/discussions/10779) | 社区贡献
**发生原因**：当在 Pydantic `@field_validator` 中引发 `ValueError` 且具有 Form 字段时，FastAPI 返回 500 Internal Server Error 而不是预期的 422 Unprocessable Entity 验证错误。

**预防**：
```python
from typing import Annotated
from fastapi import Form
from pydantic import BaseModel, field_validator, ValidationError, Field

# ✗ 错误：在验证器中引发 ValueError
class MyForm(BaseModel):
    value: int

    @field_validator('value')
    def validate_value(cls, v):
        if v < 0:
            raise ValueError("值必须为正数")  # 返回 500! ❌

# ✓ 正确 1：使用 ValidationError 代替
class MyForm(BaseModel):
    value: Annotated[int, Field(gt=0)]  # 内置验证，返回 422 ✓

# ✓ 正确 2：使用 Pydantic 的内置约束
class MyForm(BaseModel):
    value: Annotated[int, Field(gt=1)]  # 内置验证，返回 422 ✓
```

---

## 测试

```python
# tests/test_main.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post(
        "/items",
        json={"name": "测试", "price": 9.99}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "测试"
```

运行：`uv run pytest`

---

## 部署

### Uvicorn（开发）
```bash
uv run fastapi dev src/main.py
```

### Uvicorn（生产）
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Gunicorn + Uvicorn（生产，使用工作进程）
```bash
uv add gunicorn
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 参考

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [FastAPI 最佳实践](https://github.com/zhanymkanov/fastapi-best-practices)
- [Pydantic v2 文档](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 异步](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [uv 包管理器](https://docs.astral.sh/uv/)

---

**最后验证**：2026-01-21 | **技能版本**：1.1.0 | **变更**：添加了 7 个已知问题（表单数据错误，背景任务，Pydantic v2 迁移陷阱），扩展了异步阻塞指导与生产模式
**维护者**：Jezweb | jeremy@jezweb.net
