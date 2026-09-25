# Python 反模式清单

一份常见错误和反模式的 Python 代码参考清单。在最终确定实现之前进行审查，以便及早发现问题。

## 何时使用此技能

- 合并前审查代码
- 调试疑难问题
- 教学或学习 Python 最佳实践
- 建立团队编码规范
- 重构遗留代码

**注意**：此技能侧重于应避免的内容。有关积极模式和架构的指导，请参阅 `python-design-patterns` 技能。

## 基础设施反模式

### 分散的超时/重试逻辑

```python
# BAD: 超时逻辑处处重复
def fetch_user(user_id):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("获取用户超时")
        return None

def fetch_orders(user_id):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("获取订单超时")
        return None
```

**修复**：在装饰器或客户端包装器中集中处理。

```python
# GOOD: 集中重试逻辑
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def http_get(url: str) -> Response:
    return requests.get(url, timeout=30)
```

### 双重重试

```python
# BAD: 多层重试
@retry(max_attempts=3)  # 应用层重试
def call_service():
    return client.request()  # 客户端也配置了重试！
```

**修复**：只在单层重试。了解基础设施的重试行为。

### 硬编码配置

```python
# BAD: 代码中包含密钥和配置
DB_HOST = "prod-db.example.com"
API_KEY = "sk-12345"

def connect():
    return psycopg.connect(f"host={DB_HOST}...")
```

**修复**：使用带类型设置的環境变量。

```python
# GOOD
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    api_key: str = Field(alias="API_KEY")

settings = Settings()
```

## 架构反模式

### 暴露内部类型

```python
# BAD: 泄露 ORM 模型到 API
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:  # SQLAlchemy 模型
    return db.query(UserModel).get(id)
```

**修复**：使用 DTO/响应模型。

```python
# GOOD
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse.from_orm(user)
```

### 混合 I/O 和业务逻辑

```python
# BAD: SQL 嵌入业务逻辑
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    # 业务逻辑与数据访问混合
    if len(orders) > 10:
        return 0.15
    return 0.0
```

**修复**：仓库模式。保持业务逻辑纯净。

```python
# GOOD
def calculate_discount(user: User, orders: list[Order]) -> float:
    # 纯业务逻辑，易于测试
    if len(orders) > 10:
        return 0.15
    return 0.0
```

## 错误处理反模式

### 空异常处理

```python
# BAD: 捕获所有异常
try:
    process()
except Exception:
    pass  # 静默失败 - 错误永远隐藏
```

**修复**：捕获特定异常。适当记录或处理。

```python
# GOOD
try:
    process()
except ConnectionError as e:
    logger.warning("连接失败，将重试", error=str(e))
    raise
except ValueError as e:
    logger.error("无效输入", error=str(e))
    raise BadRequestError(str(e))
```

### 忽略部分失败

```python
# BAD: 遇到第一个错误就停止
def process_batch(items):
    results = []
    for item in items:
        result = process(item)  # 出错时抛出异常 - 批次中止
        results.append(result)
    return results
```

**修复**：捕获成功和失败。

```python
# GOOD
def process_batch(items) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded, failed)
```

### 缺少输入验证

```python
# BAD: 无验证
def create_user(data: dict):
    return User(**data)  # 输入错误时代码深处崩溃
```

**修复**：在 API 边界早期验证。

```python
# GOOD
def create_user(data: dict) -> User:
    validated = CreateUserInput.model_validate(data)
    return User.from_input(validated)
```

## 资源反模式

### 未关闭的资源

```python
# BAD: 文件未关闭
def read_file(path):
    f = open(path)
    return f.read()  # 如果抛出异常会怎样？
```

**修复**：使用上下文管理器。

```python
# GOOD
def read_file(path):
    with open(path) as f:
        return f.read()
```

### 异步中阻塞

```python
# BAD: 阻塞整个事件循环
async def fetch_data():
    time.sleep(1)  # 阻塞所有操作！
    response = requests.get(url)  # 也阻塞！
```

**修复**：使用原生异步库。

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

## 类型安全反模式

### 缺少类型提示

```python
# BAD: 无类型
def process(data):
    return data["value"] * 2
```

**修复**：为所有公共函数添加注解。

```python
# GOOD
def process(data: dict[str, int]) -> int:
    return data["value"] * 2
```

### 未类型化的集合

```python
# BAD: 无类型参数的泛型列表
def get_users() -> list:
    ...
```

**修复**：使用类型参数。

```python
# GOOD
def get_users() -> list[User]:
    ...
```

## 测试反模式

### 仅测试成功路径

```python
# BAD: 仅测试成功情况
def test_create_user():
    user = service.create_user(valid_data)
    assert user.id is not None
```

**修复**：测试错误条件和边界情况。

```python
# GOOD
def test_create_user_success():
    user = service.create_user(valid_data)
    assert user.id is not None

def test_create_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user(invalid_email_data)

def test_create_user_duplicate_email():
    service.create_user(valid_data)
    with pytest.raises(ConflictError):
        service.create_user(valid_data)
```

### 过度模拟

```python
# BAD: 模拟所有内容
def test_user_service():
    mock_repo = Mock()
    mock_cache = Mock()
    mock_logger = Mock()
    mock_metrics = Mock()
    # 测试未验证实际行为
```

**修复**：对关键路径使用集成测试。仅模拟外部服务。

## 快速审查清单

在最终确定代码之前验证：

- [ ] 无分散的超时/重试逻辑（集中处理）
- [ ] 无双重重试（应用层+基础设施）
- [ ] 无硬编码配置或密钥
- [ ] 无暴露内部类型（ORM 模型、protobuf）
- [ ] 无混合 I/O 和业务逻辑
- [ ] 无 `except Exception: pass`
- [ ] 无批次中的忽略部分失败
- [ ] 无缺少输入验证
- [ ] 无未关闭的资源（使用上下文管理器）
- [ ] 无异步代码中的阻塞调用
- [ ] 所有公共函数都有类型提示
- [ ] 集合有类型参数
- [ ] 测试了错误路径
- [ ] 覆盖了边界情况

## 常见修复总结

| 反模式 | 修复 |
|-------|------|
| 分散重试逻辑 | 集中装饰器 |
| 硬编码配置 | 環境变量 + pydantic-settings |
| 暴露 ORM 模型 | DTO/响应模式 |
| 混合 I/O + 逻辑 | 仓库模式 |
| 空异常 | 捕获特定异常 |
| 批次出错就停止 | 返回包含成功/失败的 BatchResult |
| 无验证 | 使用 Pydantic 在边界验证 |
| 未关闭资源 | 上下文管理器 |
| 异步中阻塞 | 原生异步库 |
| 缺少类型 | 所有公共 API 添加类型注解 |
| 仅测试成功路径 | 测试错误和边界情况 |
