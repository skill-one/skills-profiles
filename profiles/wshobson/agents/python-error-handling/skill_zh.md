# Python 错误处理

使用正确的输入验证、有意义的异常和优雅的失败处理来构建健壮的 Python 应用程序。良好的错误处理使调试更轻松，系统更可靠。

## 何时使用这项技能

- 验证用户输入和 API 参数
- 为应用程序设计异常层次结构
- 处理批处理操作中的部分失败
- 将外部数据转换为领域类型
- 构建用户友好的错误消息
- 实现快速失败验证模式

## 核心概念

### 1. 快速失败

在执行昂贵的操作之前尽早验证输入。尽可能一次性报告所有验证错误。

### 2. 有意义的异常

使用适当的异常类型并附带上下文。消息应说明失败的内容、原因以及如何修复。

### 3. 部分失败

在批处理操作中，不要让一个失败导致所有操作中止。分别跟踪成功和失败的情况。

### 4. 保留上下文

链式异常以保留完整的错误跟踪信息用于调试。

## 快速入门

```python
def fetch_page(url: str, page_size: int) -> Page:
    if not url:
        raise ValueError("'url' is required")
    if not 1 <= page_size <= 100:
        raise ValueError(f"'page_size' must be 1-100, got {page_size}")
    # 现在可以安全地继续执行...
```

## 基础模式

### 模式 1：早期输入验证

在开始任何处理之前，在 API 边界验证所有输入。

```python
def process_order(
    order_id: str,
    quantity: int,
    discount_percent: float,
) -> OrderResult:
    """验证后处理订单。"""
    # 验证必需字段
    if not order_id:
        raise ValueError("'order_id' is required")

    # 验证范围
    if quantity <= 0:
        raise ValueError(f"'quantity' must be positive, got {quantity}")

    if not 0 <= discount_percent <= 100:
        raise ValueError(
            f"'discount_percent' must be 0-100, got {discount_percent}"
        )

    # 验证通过，继续处理
    return _process_validated_order(order_id, quantity, discount_percent)
```

### 模式 2：早期转换为领域类型

在系统边界将字符串和外部数据解析为带类型的领域对象。

```python
from enum import Enum

class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"

def parse_output_format(value: str) -> OutputFormat:
    """将字符串解析为 OutputFormat 枚举。

    Args:
        value: 用户输入的格式字符串。

    Returns:
        验证后的 OutputFormat 枚举成员。

    Raises:
        ValueError: 如果格式不被识别。
    """
    try:
        return OutputFormat(value.lower())
    except ValueError:
        valid_formats = [f.value for f in OutputFormat]
        raise ValueError(
            f"Invalid format '{value}'. "
            f"Valid options: {', '.join(valid_formats)}"
        )

# 在 API 边界使用
def export_data(data: list[dict], format_str: str) -> bytes:
    output_format = parse_output_format(format_str)  # 快速失败
    # 函数其余部分使用带类型的 OutputFormat
    ...
```

### 模式 3：使用 Pydantic 进行复杂验证

使用 Pydantic 模型进行结构化输入验证，并自动生成错误消息。

```python
from pydantic import BaseModel, Field, field_validator

class CreateUserInput(BaseModel):
    """用户创建的输入模型。"""

    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()

# 使用
try:
    user_input = CreateUserInput(
        email="user@example.com",
        name="john doe",
        age=25,
    )
except ValidationError as e:
    # Pydantic 提供详细的错误信息
    print(e.errors())
```

### 模式 4：将错误映射到标准异常

适当地使用 Python 的内置异常类型，并在需要时添加上下文。

| 失败类型 | 异常 | 示例 |
|----------|------|------|
| 无效输入 | `ValueError` | 坏的参数值 |
| 类型错误 | `TypeError` | 期望字符串，得到整数 |
| 缺失项 | `KeyError` | 字典键未找到 |
| 操作失败 | `RuntimeError` | 服务不可用 |
| 超时 | `TimeoutError` | 操作耗时过长 |
| 文件未找到 | `FileNotFoundError` | 路径不存在 |
| 权限被拒绝 | `PermissionError` | 访问被禁止 |

```python
# 好：带上下文的特定异常
raise ValueError(f"'page_size' must be 1-100, got {page_size}")

# 避免：通用异常，无上下文
raise Exception("Invalid parameter")
```

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md` 文件中。当上面的导航摘要不足以说明时，请阅读该文件。

## 最佳实践总结

1. **尽早验证** - 在昂贵的操作之前检查输入
2. **使用特定异常** - `ValueError`、`TypeError`，而不是通用 `Exception`
3. **包含上下文** - 消息应说明内容、原因以及如何修复
4. **在边界转换类型** - 尽早将字符串解析为枚举/领域类型
5. **链式异常** - 使用 `raise ... from e` 保留调试信息
6. **处理部分失败** - 不要在单个项错误时中止批处理
7. **使用 Pydantic** - 用于复杂输入验证和结构化错误
8. **记录失败模式** - 文档字符串应列出可能的异常
9. **带上下文记录** - 包括 ID、计数和其他调试信息
10. **测试错误路径** - 验证异常是否正确抛出
