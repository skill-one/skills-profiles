# Python 类型安全

利用 Python 的类型系统在静态分析时捕获错误。类型注解作为强制执行的文档，工具可以自动验证。

## 何时使用此技能

- 为现有代码添加类型提示
- 创建通用、可重用的类
- 定义具有协议的结构化接口
- 配置 mypy 或 pyright 进行严格检查
- 理解类型窄化（type narrowing）和守卫（guards）
- 构建类型安全的 API 和库

## 核心概念

### 1. 类型注解

为函数参数、返回值和变量声明预期类型。

### 2. 泛型

编写跨不同类型保留类型信息的可重用代码。

### 3. 协议

定义无需继承的结构化接口（使用类型安全的鸭子类型）。

### 4. 类型窄化

使用守卫和条件语句在代码块中窄化类型。

## 快速入门

```python
def get_user(user_id: str) -> User | None:
    """返回类型使 '可能不存在' 更加明确。"""
    ...

# 类型检查器强制处理 None 情况
user = get_user("123")
if user is None:
    raise UserNotFoundError("123")
print(user.name)  # 类型检查器知道此处 user 是 User 类型
```

## 基础模式

### 模式 1：注解所有公共签名

每个公共函数、方法和类都应该有类型注解。

```python
def get_user(user_id: str) -> User:
    """通过 ID 检索用户。"""
    ...

def process_batch(
    items: list[Item],
    max_workers: int = 4,
) -> BatchResult[ProcessedItem]:
    """并发处理项目。"""
    ...

class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_by_id(self, user_id: str) -> User | None:
        """找到则返回 User，否则返回 None。"""
        ...

    async def find_by_email(self, email: str) -> User | None:
        ...

    async def save(self, user: User) -> User:
        """保存并返回具有生成 ID 的用户。"""
        ...
```

在 CI 中使用 `mypy --strict` 或 `pyright` 以尽早捕获类型错误。对于现有项目，逐步使用模块级覆盖启用严格模式。

### 模式 2：使用现代联合语法

Python 3.10+ 提供更简洁的联合语法。

```python
# 推荐（3.10+）
def find_user(user_id: str) -> User | None:
    ...

def parse_value(v: str) -> int | float | str:
    ...

# 旧式（仍然有效，3.9 需要）
from typing import Optional, Union

def find_user(user_id: str) -> Optional[User]:
    ...
```

### 模式 3：使用守卫进行类型窄化

使用条件语句窄化类型以供类型检查器使用。

```python
def process_user(user_id: str) -> UserData:
    user = find_user(user_id)

    if user is None:
        raise UserNotFoundError(f"未找到用户 {user_id}")

    # 类型检查器知道此处 user 是 User 类型，而不是 User | None
    return UserData(
        name=user.name,
        email=user.email,
    )

def process_items(items: list[Item | None]) -> list[ProcessedItem]:
    # 过滤并窄化类型
    valid_items = [item for item in items if item is not None]
    # valid_items 现在是 list[Item]
    return [process(item) for item in valid_items]
```

### 模式 4：泛型类

创建类型安全的可重用容器。

```python
from typing import TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

class Result(Generic[T, E]):
    """表示成功值或错误。"""

    def __init__(
        self,
        value: T | None = None,
        error: E | None = None,
    ) -> None:
        if (value is None) == (error is None):
            raise ValueError("必须设置 value 或 error 中的一个")
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    def unwrap(self) -> T:
        """获取值或引发错误。"""
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore[return-value]

    def unwrap_or(self, default: T) -> T:
        """获取值或返回默认值。"""
        if self._error is not None:
            return default
        return self._value  # type: ignore[return-value]

# 使用时保留类型
def parse_config(path: str) -> Result[Config, ConfigError]:
    try:
        return Result(value=Config.from_file(path))
    except ConfigError as e:
        return Result(error=e)

result = parse_config("config.yaml")
if result.is_success:
    config = result.unwrap()  # 类型：Config
```

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md`。当上述导航摘要不足以说明时，请阅读该文件。

## 最佳实践总结

1. **注解所有公共 API** - 函数、方法、类属性
2. **使用 `T | None`** - 现代联合语法优于 `Optional[T]`
3. **运行严格类型检查** - 在 CI 中使用 `mypy --strict`
4. **使用泛型** - 在可重用代码中保留类型信息
5. **定义协议** - 结构化类型用于接口
6. **窄化类型** - 使用守卫帮助类型检查器
7. **绑定类型变量** - 限制泛型为有意义的类型
8. **创建类型别名** - 为复杂类型提供有意义的名称
9. **最小化 `Any`** - 使用具体类型或泛型。`Any` 可用于真正动态的数据或与未类型化的第三方代码交互时
10. **使用类型进行文档记录** - 类型是强制执行的文档
