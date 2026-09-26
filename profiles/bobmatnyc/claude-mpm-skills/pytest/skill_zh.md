# pytest - 专业 Python 测试

## 概述

pytest 是业界标准的 Python 测试框架，提供强大的特性，如 fixtures（固定装置）、参数化、标记、插件，并能与 FastAPI、Django 和 Flask 无缝集成。它提供了一种简单、可扩展的方法，从单元测试到复杂的集成场景进行测试。

**主要特性**：
- 依赖注入的 fixture 系统用于测试
- 参数化用于数据驱动测试
- 丰富的断言内省（无需 `self.assertEqual`）
- 插件生态系统（pytest-cov、pytest-asyncio、pytest-mock、pytest-django）
- 支持 async/await
- 使用 pytest-xdist 进行并行测试执行
- 测试发现和组织
- 详细失败报告

**安装**：
```bash
# 基础 pytest
pip install pytest

# 带常见插件
pip install pytest pytest-cov pytest-asyncio pytest-mock

# 用于 FastAPI 测试
pip install pytest httpx pytest-asyncio

# 用于 Django 测试
pip install pytest pytest-django

# 用于异步数据库
pip install pytest-asyncio aiosqlite
```

## 基本测试模式

### 1. 简单测试函数

```python
# test_math.py
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_add_negative():
    assert add(-2, -3) == -5
```

**运行测试**：
```bash
# 发现并运行所有测试
pytest

# 详细输出
pytest -v

# 显示打印语句
pytest -s

# 运行特定测试文件
pytest test_math.py

# 运行特定测试函数
pytest test_math.py::test_add
```

### 2. 测试类用于组织

```python
# test_calculator.py
class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

class TestCalculator:
    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_multiply(self):
        calc = Calculator()
        assert calc.multiply(4, 5) == 20

    def test_add_negative(self):
        calc = Calculator()
        assert calc.add(-1, -1) == -2
```

### 3. 断言和预期失败

```python
import pytest

# 测试异常抛出
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

def test_divide_success():
    assert divide(10, 2) == 5.0

# 测试近似相等
def test_float_comparison():
    assert 0.1 + 0.2 == pytest.approx(0.3)

# 测试包含
def test_list_contains():
    result = [1, 2, 3, 4]
    assert 3 in result
    assert len(result) == 4
```

## Fixtures - 依赖注入

### 基本Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def sample_data():
    """为测试提供示例数据。"""
    return {"name": "Alice", "age": 30, "email": "alice@example.com"}

@pytest.fixture
def empty_list():
    """提供空列表。"""
    return []

# test_fixtures.py
def test_sample_data(sample_data):
    assert sample_data["name"] == "Alice"
    assert sample_data["age"] == 30

def test_empty_list(empty_list):
    empty_list.append(1)
    assert len(empty_list) == 1
```

### Fixture 范围

```python
import pytest

# 函数范围（默认）- 每个测试运行一次
@pytest.fixture(scope="function")
def user():
    return {"id": 1, "name": "Alice"}

# 类范围 - 每个测试类运行一次
@pytest.fixture(scope="class")
def database():
    db = setup_database()
    yield db
    db.close()

# 模块范围 - 每个测试模块运行一次
@pytest.fixture(scope="module")
def api_client():
    client = APIClient()
    yield client
    client.shutdown()

# 会话范围 - 整个测试会话运行一次
@pytest.fixture(scope="session")
def app_config():
    return load_config()
```

### Fixture 设置和清理

```python
import pytest
import tempfile
import shutil

@pytest.fixture
def temp_directory():
    """为测试创建临时目录。"""
    temp_dir = tempfile.mkdtemp()
    print(f"
设置：创建 {temp_dir}")

    yield temp_dir  # 提供给测试目录

    # 清理：测试后清理
    shutil.rmtree(temp_dir)
    print(f"
清理：删除 {temp_dir}")

def test_file_creation(temp_directory):
    file_path = f"{temp_directory}/test.txt"
    with open(file_path, "w") as f:
        f.write("test content")

    assert os.path.exists(file_path)
```

### Fixture 依赖

```python
import pytest

@pytest.fixture
def database_connection():
    """数据库连接。"""
    conn = connect_to_db()
    yield conn
    conn.close()

@pytest.fixture
def database_session(database_connection):
    """数据库会话依赖于连接。"""
    session = create_session(database_connection)
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def user_repository(database_session):
    """用户仓库依赖于会话。"""
    return UserRepository(database_session)

def test_create_user(user_repository):
    user = user_repository.create(name="Alice", email="alice@example.com")
    assert user.name == "Alice"
```

## Parametrization - 数据驱动测试

### 基本参数化

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (5, 7, 12),
    (-1, 1, 0),
    (0, 0, 0),
    (100, 200, 300),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
```

### 多参数

```python
@pytest.mark.parametrize("operation,a,b,expected", [
    ("add", 2, 3, 5),
    ("subtract", 10, 5, 5),
    ("multiply", 4, 5, 20),
    ("divide", 10, 2, 5),
])
def test_calculator_operations(operation, a, b, expected):
    calc = Calculator()
    result = getattr(calc, operation)(a, b)
    assert result == expected
```

### Parametrize with IDs

```python
@pytest.mark.parametrize("input_data,expected", [
    pytest.param({"name": "Alice"}, "Alice", id="valid_name"),
    pytest.param({"name": ""}, None, id="empty_name"),
    pytest.param({}, None, id="missing_name"),
], ids=lambda x: x if isinstance(x, str) else None)
def test_extract_name(input_data, expected):
    result = extract_name(input_data)
    assert result == expected
```

### 间接参数化（Fixtures）

```python
@pytest.fixture
def user_data(request):
    """根据参数创建用户。"""
    return {"name": request.param, "email": f"{request.param}@example.com"}

@pytest.mark.parametrize("user_data", ["Alice", "Bob", "Charlie"], indirect=True)
def test_user_creation(user_data):
    assert "@example.com" in user_data["email"]
```

## Test Markers

### 内置标记

```python
import pytest

# 跳过测试
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

# 条件性跳过
@pytest.mark.skipif(sys.platform == "win32", reason="Unix-only test")
def test_unix_specific():
    pass

# 预期失败
@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug():
    assert False

# 慢速测试标记
@pytest.mark.slow
def test_expensive_operation():
    time.sleep(5)
    assert True
```

### 自定义标记

```python
# pytest.ini
[pytest]
markers =
    slow: 标记测试为慢速（使用 '-m "not slow"' 取消选择）
    integration: 标记测试为集成测试
    unit: 标记测试为单元测试
    smoke: 标记测试为冒烟测试

# test_custom_markers.py
import pytest

@pytest.mark.unit
def test_fast_unit():
    assert True

@pytest.mark.integration
@pytest.mark.slow
def test_slow_integration():
    # 集成测试与数据库
    pass

@pytest.mark.smoke
def test_critical_path():
    # 关键功能的冒烟测试
    pass
```

**按标记运行测试**：
```bash
# 仅运行单元测试
pytest -m unit

# 运行所有除了慢速测试的
pytest -m "not slow"

# 运行集成测试
pytest -m integration

# 运行单元测试和集成测试
pytest -m "unit or integration"

# 仅运行冒烟测试
pytest -m smoke
```

## FastAPI 测试

### 基本 FastAPI 测试设置

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.post("/items")
def create_item(item: Item):
    return {"name": item.name, "price": item.price, "id": 123}
```

### FastAPI 测试客户端

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI 测试客户端。"""
    return TestClient(app)

# test_api.py
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_read_item(client):
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "name": "Item 1"}

def test_read_item_not_found(client):
    response = client.get("/items/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_create_item(client):
    response = client.post(
        "/items",
        json={"name": "Widget", "price": 9.99}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert "id" in data
```

### 异步 FastAPI 测试

```python
# conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def async_client():
    """异步测试客户端用于 FastAPI。"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# test_async_api.py
import pytest

@pytest.mark.asyncio
async def test_read_root_async(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_create_item_async(async_client):
    response = await async_client.post(
        "/items",
        json={"name": "Gadget", "price": 19.99}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Gadget"
```

### FastAPI 与数据库测试

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库。"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """覆盖数据库依赖。"""
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

# test_users.py
def test_create_user(client):
    response = client.post(
        "/users",
        json={"email": "test@example.com", "password": "secret"}  # pragma: allowlist secret
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_read_users(client):
    # 首先创建用户
    client.post("/users", json={"email": "user1@example.com", "password": "pass1"})  # pragma: allowlist secret
    client.post("/users", json={"email": "user2@example.com", "password": "pass2"})  # pragma: allowlist secret

    # 读取用户
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
```

## Django 测试

### Django pytest 配置

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings
python_files = tests.py test_*.py *_tests.py

# conftest.py
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```

### Django 模型测试

```python
# models.py
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

# test_models.py
import pytest
from myapp.models import User

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create(
        email="test@example.com",
        name="Test User"
    )
    assert user.email == "test@example.com"
    assert user.is_active is True

@pytest.mark.django_db
def test_user_unique_email():
    User.objects.create(email="test@example.com", name="User 1")

    with pytest.raises(Exception):  # IntegrityError
        User.objects.create(email="test@example.com", name="User 1")
```

### Django 视图测试

```python
# views.py
from django.http import JsonResponse
from django.views import View

class UserListView(View):
    def get(self, request):
        users = User.objects.all()
        return JsonResponse({
            "users": list(users.values("id", "email", "name"))
        })

# test_views.py
import pytest
from django.test import Client
from myapp.models import User

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_user_list_view(client):
    # 创建测试数据
    User.objects.create(email="user1@example.com", name="User 1")
    User.objects.create(email="user2@example.com", name="User 2")

    # 测试视图
    response = client.get("/users/")
    assert response.status_code == 200

    data = response.json()
    assert len(data["users"]) == 2
```

### Django REST Framework 测试

```python
# serializers.py
from rest_framework import serializers
from myapp.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'is_active']

# views.py
from rest_framework import viewsets
from myapp.models import User
from myapp.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# test_api.py
import pytest
from rest_framework.test import APIClient
from myapp.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_list_users(api_client):
    User.objects.create(email="user1@example.com", name="User 1")
    User.objects.create(email="user2@example.com", name="User 2")

    response = api_client.get("/api/users/")
    assert response.status_code == 200
    assert len(response.data) == 2

@pytest.mark.django_db
def test_create_user(api_client):
    data = {"email": "new@example.com", "name": "New User"}
    response = api_client.post("/api/users/", data)

    assert response.status_code == 201
    assert User.objects.filter(email="new@example.com").exists()
```

## Mocking and Patching

### pytest-mock (pytest.fixture.mocker)

```python
# 安装: pip install pytest-mock

# service.py
import requests

def get_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

# test_service.py
def test_get_user_data(mocker):
    # Mock requests.get
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}

    mocker.patch("requests.get", return_value=mock_response)

    result = get_user_data(1)
    assert result["name"] == "Alice"
```

### Mocking 类方法

```python
class UserService:
    def get_user(self, user_id):
        # 数据库调用
        return database.fetch_user(user_id)

    def get_user_name(self, user_id):
        user = self.get_user(user_id)
        return user["name"]

def test_get_user_name(mocker):
    service = UserService()

    # Mock the get_user 方法
    mocker.patch.object(
        service,
        "get_user",
        return_value={"id": 1, "name": "Alice"}
    )

    result = service.get_user_name(1)
    assert result == "Alice"
```

### Mocking with Side Effects

```python
def test_retry_on_failure(mocker):
    # 第一次调用失败，第二次成功
    mock_api = mocker.patch("requests.get")
    mock_api.side_effect = [
        requests.exceptions.Timeout(),  # 第一次调用
        mocker.Mock(json=lambda: {"status": "ok"})  # 第二次调用
    ]

    result = api_call_with_retry()
    assert result["status"] == "ok"
    assert mock_api.call_count == 2
```

### Spy on Calls

```python
def test_function_called_correctly(mocker):
    spy = mocker.spy(module, "function_name")

    # 调用代码使用函数
    module.run_workflow()

    # 验证是否被调用
    assert spy.call_count == 1
    spy.assert_called_once_with(arg1="value", arg2=42)
```

## Coverage and Reporting

### pytest-cov 配置

```bash
# 安装
pip install pytest-cov

# 带覆盖运行测试
pytest --cov=app --cov-report=html --cov-report=term

# 生成覆盖报告
pytest --cov=app --cov-report=term-missing

# 带最小阈值覆盖
pytest --cov=app --cov-fail-under=80
```

### pytest.ini 覆盖配置

```ini
# pytest.ini
[pytest]
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 覆盖报告

```bash
# HTML 报告（在浏览器中打开）
pytest --cov=app --cov-report=html
open htmlcov/index.html

# 终端报告带缺失行
pytest --cov=app --cov-report=term-missing

# XML 报告（用于 CI/CD）
pytest --cov=app --cov-report=xml

# JSON 报告
pytest --cov=app --cov-report=json
```

## Async Testing

### pytest-asyncio

```python
# 安装: pip install pytest-asyncio

# conftest.py
import pytest

# 启用 asyncio 模式
pytest_plugins = ('pytest_asyncio',)

# async_service.py
import asyncio
import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# test_async_service.py
import pytest

@pytest.mark.asyncio
async def test_fetch_data(mocker):
    # Mock aiohttp 响应
    mock_response = mocker.AsyncMock()
    mock_response.json.return_value = {"data": "test"}

    mock_session = mocker.AsyncMock()
    mock_session.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    result = await fetch_data("https://api.example.com/data")
    assert result["data"] == "test"
```

### Async Fixtures

```python
@pytest.fixture
async def async_db_session():
    """异步数据库会话。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(async_engine) as session:
        yield session

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_user_async(async_db_session):
    user = User(email="test@example.com", name="Test")
    async_db_session.add(user)
    await async_db_session.commit()

    result = await async_db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    assert result.scalar_one().name == "Test"
```

## Local pytest Profiles (Your Repos)

您项目中的 `pyproject.toml` 中的常见设置：

- `asyncio_mode = "auto"`（mcp-browser、mcp-memory、claude-mpm、edgar 中的默认值）
- `addopts` 包括 `--strict-markers` 和 `--strict-config` 用于 CI 的一致性
- 覆盖标志：`--cov=<package>`, `--cov-report=term-missing`, `--cov-report=xml`
- 选择性忽略（mcp-vector-search）：`--ignore=tests/manual`, `--ignore=tests/e2e`
- `pythonpath = ["src"]` 用于可编辑导入解析（mcp-ticketer）

典型标记：

- `unit`, `integration`, `e2e`
- `slow`, `benchmark`, `performance`
- `requires_api`（edgar）

参考：请参阅 `claude-mpm`, `edgar`, `mcp-vector-search`, `mcp-ticketer` 和 `kuzu-memory` 中的 `pyproject.toml` 以获取完整列表。

## Best Practices

### 1. 测试组织

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── services.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # 共享 fixtures
│   ├── test_models.py       # 模型测试
│   ├── test_services.py     # 服务测试
│   ├── test_api.py          # API 测试
│   └── integration/
│       ├── __init__.py
│       └── test_workflows.py
└── pytest.ini
```

### 2. 命名约定

```python
# ✅ 好的：清晰的测试名称
def test_user_creation_with_valid_email():
    pass

def test_user_creation_raises_error_for_duplicate_email():
    pass

# ❌ 坏的：模糊的名称
def test_user1():
    pass

def test_case2():
    pass
```

### 3. Arrange-Act-Assert 模式

```python
def test_user_service_creates_user():
    # Arrange：设置测试数据和依赖
    service = UserService(database=mock_db)
    user_data = {"email": "test@example.com", "name": "Test"}

    # Act：执行被测试的操作
    result = service.create_user(user_data)

    # Assert：验证结果
    assert result.email == "test@example.com"
    assert result.id is not None
```

### 4. 使用 Fixtures for Common Setup

```python
# ❌ 坏的：重复设置
def test_user_creation():
    db = setup_database()
    user = create_user(db)
    assert user.id is not None
    db.close()

def test_user_deletion():
    db = setup_database()
    user = create_user(db)
    delete_user(db, user.id)
    db.close()

# ✅ 好的：基于 fixture 的设置
@pytest.fixture
def db():
    database = setup_database()
    yield database
    database.close()

@pytest.fixture
def user(db):
    return create_user(db)

def test_user_creation(user):
    assert user.id is not None

def test_user_deletion(db, user):
    delete_user(db, user.id)
    assert not user_exists(db, user.id)
```

### 5. Parametrize Similar Tests

```python
# ❌ 坏的：重复的测试代码
def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-2, -3) == -5

def test_add_zero():
    assert add(0, 0) == 0

# ✅ 好的：参数化测试
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-2, -3, -5),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### 6. Test One Thing Per Test

```python
# ❌ 坏的：测试多个事物
def test_user_workflow():
    user = create_user()
    assert user.id is not None

    updated = update_user(user.id, name="New Name")
    assert updated.name == "New Name"

    deleted = delete_user(user.id)
    assert deleted is True

# ✅ 好的：分离测试
def test_user_creation():
    user = create_user()
    assert user.id is not None

def test_user_update():
    user = create_user()
    updated = update_user(user.id, name="New Name")
    assert updated.name == "New Name"

def test_user_deletion():
    user = create_user()
    result = delete_user(user.id)
    assert result is True
```

### 7. Use Markers for Test Organization

```python
@pytest.mark.unit
def test_pure_function():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_database_integration():
    pass

@pytest.mark.smoke
def test_critical_path():
    pass
```

### 8. Mock External Dependencies

```python
# ✅ 好的：Mock 外部 API
def test_fetch_user_data(mocker):
    mocker.patch("requests.get", return_value=mock_response)
    result = fetch_user_data(user_id=1)
    assert result["name"] == "Alice"

# ❌ 坏的：测试中调用真实 API 调用
def test_fetch_user_data():
    result = fetch_user_data(user_id=1)  # 真实 HTTP 请求！
    assert result["name"] == "Alice"
```

## Common Pitfalls

### ❌ Anti-Pattern 1: Test Depends on Execution Order

```python
# WRONG: 测试应该独立于执行顺序
class TestUserWorkflow:
    user_id = None

    def test_create_user(self):
        user = create_user()
        TestUserWorkflow.user_id = user.id

    def test_update_user(self):
        # 如果 test_create_user 没有运行，测试会失败！
        update_user(TestUserWorkflow.user_id, name="New")
```

**正确**：
```python
# 使用 pytest 的 built-in debugging
pytest tests/test_auth.py -vv --pdb  # 在失败时进入调试器
pytest tests/test_auth.py -x         # 第一个失败就停止
pytest tests/test_auth.py -k "auth"  # 只运行与 auth 相关的测试

# 添加策略打印/日志
def test_complex_workflow():
    user = create_user({'username': 'test'})
    print(f"DEBUG: 创建用户 {user.id}")  # 可见 pytest -s
    result = process_user(user)
    print(f"DEBUG: 结果状态 {result.status}")
    assert result.success
```

## Resources

- **官方文档**：https://docs.pytest.org/
- **pytest-asyncio**：https://pytest-asyncio.readthedocs.io/
- **pytest-cov**：https://pytest-cov.readthedocs.io/
- **pytest-mock**：https://pytest-mock.readthedocs.io/
- **pytest-django**：https://pytest-django.readthedocs.io/
- **FastAPI Testing**：https://fastapi.tiangolo.com/tutorial/testing/

## Related Skills

使用 pytest 时，请考虑这些互补技能：

- **fastapi-local-dev**：FastAPI 开发服务器模式和测试 fixtures
- **test-driven-development**：完整的 TDD 工作流（RED/GREEN/REFACTOR 循环）
- **systematic-debugging**：失败测试的根本原因调查

### 快速 TDD 工作流参考（用于独立使用）

**RED → GREEN → REFACTOR 循环**：

1. **RED 阶段：编写失败的测试**
   ```python
   def test_should_authenticate_user_when_credentials_valid():
       # 描述所需行为的测试
       user = User(username='alice', password='secret123')
       result = authenticate(user)
       assert result.is_authenticated is True
       # 测试将失败，因为 authenticate() 还不存在
   ```

2. **GREEN 阶段：让测试通过**
   ```python
   def authenticate(user):
       # 最小代码让测试通过
       if user.username == 'alice' and user.password == 'secret123':  # pragma: allowlist secret
           return AuthResult(is_authenticated=True)
       return AuthResult(is_authenticated=False)
   ```

3. **REFACTOR 阶段：改进代码**
   ```python
   def authenticate(user):
       # 在保持测试绿色的情况下进行清理
       hashed_password = hash_password(user.password)
       stored_user = database.get_user(user.username)
       return AuthResult(
           is_authenticated=(stored_user.password_hash == hashed_password)
       )
   ```

**测试结构：Arrange-Act-Assert (AAA)**
```python
def test_user_creation():
    # Arrange：设置测试数据
    user_data = {'username': 'alice', 'email': 'alice@example.com'}

    # Act：执行被测试的操作
    user = create_user(user_data)

    # Assert：验证结果
    assert user.username == 'alice'
    assert user.email == 'alice@example.com'
```

### 快速调试参考（用于独立使用）

**阶段 1：根本原因调查**
- 读取完整的错误消息（堆栈跟踪、行号）
- 保持一致地重现（记录确切步骤）
- 检查最近的更改（git log, git diff）
- 了解发生了什么以及为什么它可能导致失败

**阶段 2：隔离问题**
```python
# 使用 pytest 的 built-in debugging
pytest tests/test_auth.py -vv --pdb  # 在失败时进入调试器
pytest tests/test_auth.py -x         # 停止第一个失败
pytest tests/test_auth.py -k "auth"  # 只运行 auth 相关的测试

# 添加策略打印/日志
def test_complex_workflow():
    user = create_user({'username': 'test'})
    print(f"DEBUG: 创建用户 {user.id}")  # 可见 pytest -s
    result = process_user(user)
    print(f"DEBUG: 结果状态 {result.status}")
    assert result.success
```

**阶段 1：根本原因调查**
- 读取完整的错误消息（堆栈跟踪、行号）
- 保持一致地重现（记录确切步骤）
- 检查最近的更改（git log, git diff）
- 了解发生了什么以及为什么它可能导致失败

**阶段 2：隔离问题**
```python
# 使用 pytest 的 built-in debugging
pytest tests/test_auth.py -vv --pdb  # 在失败时进入调试器
pytest tests/test_auth.py -x         # 停止第一个失败
pytest tests/test_auth.py -k "auth"  # 只运行 auth 相关的测试

# 添加策略打印/日志
def test_complex_workflow():
    user = create_user({'username': 'test'})
    print(f"DEBUG: 创建用户 {user.id}")  # 可见 pytest -s
    result = process_user(user)
    print(f"DEBUG: 结果状态 {result.status}")
    assert result.success
```

[完整 TDD 和调试工作流在相关技能中如果一起部署则可用]

---

## Python Code-Quality Anti-Patterns

测试中的干净代码更容易测试，一些 Python 质量缺陷直接导致不稳定或静默通过的测试（过于宽泛的 `except`、格式不正确的异常类、身份与相等性错误）。测试中的代码质量反模式现在有自己的专用技能，而不是测试技能：

参见 **python-code-quality** 技能 (`toolchains/python/quality/code-quality`) 中最有价值的 Python 反模式——异常层次结构的正确性、单例身份比较、狭窄的异常处理、通配符导入避免、魔法数字命名和死本地删除——以及不合规与合规示例以及如何测试每个。对于项目范围的严重性标记审查清单，请参阅 `code-review-standards` 技能。

---

**pytest 版本兼容性**：本技能涵盖 pytest 7.0+，并反映了 2025 年 Python 测试的最佳实践。
