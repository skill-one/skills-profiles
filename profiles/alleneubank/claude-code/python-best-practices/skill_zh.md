# Python 最佳实践

遵循 CLAUDE.md 中的类型优先、函数式和错误处理模式。这项技能仅涵盖语言特定的惯用法。

## 使非法状态无法表示

使用 Python 的类型系统在类型检查时防止无效状态。

**使用冻结数据类实现不可变领域模型：**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    id: str
    email: str
    name: str
    created_at: datetime

# 冻结数据类是不可变的——防止意外修改
```

**使用 Literal 实现区分联合类型：**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class Success:
    status: Literal["success"] = "success"
    data: str

@dataclass
class Failure:
    status: Literal["error"] = "error"
    error: Exception

RequestState = Success | Failure

def handle_state(state: RequestState) -> None:
    match state:
        case Success(data=data):
            render(data)
        case Failure(error=err):
            show_error(err)
```

**使用 NewType 为领域原语创建类型别名：**
```python
from typing import NewType

UserId = NewType("UserId", str)
OrderId = NewType("OrderId", str)

def get_user(user_id: UserId) -> User:
    # 类型检查器会阻止在此处传递 OrderId
    ...
```

**使用 Protocol 实现结构化类型：**
```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

def process_input(source: Readable) -> bytes:
    # 接受任何具有 read() 方法的对象——无需继承
    return source.read()
```

## Python 特定的错误处理

使用 `from err` 链式异常以保留原始堆栈跟踪：
```python
try:
    data = json.loads(raw)
except json.JSONDecodeError as err:
    raise ValueError(f"无效的 JSON 负载: {err}") from err
```

## 结构化日志记录

使用模块级日志记录器并使用 `%s` 格式化（延迟字符串插值）：
```python
import logging

logger = logging.getLogger("myapp.widgets")

def create_widget(name: str) -> Widget:
    logger.debug("创建小部件: %s", name)
    widget = Widget(name=name)
    logger.debug("创建小部件 id=%s", widget.id)
    return widget
```

## 可选：ty

为了快速类型检查，可以考虑 Astral（ruff 和 uv 的创建者）提供的 [ty](https://docs.astral.sh/ty/)。用 Rust 编写，比 mypy 或 pyright 快得多。

```bash
uvx ty check          # 直接运行，无需安装
uvx ty check src/     # 检查特定路径
```

```toml
# pyproject.toml
[tool.ty]
python-version = "3.12"
```

选择时机：
- `ty` — 速度最快，适合 CI 和大型代码库（早期阶段，快速演进）
- `pyright` — 最完整的类型推断，VS Code 集成
- `mypy` — 成熟，广泛的插件生态系统
