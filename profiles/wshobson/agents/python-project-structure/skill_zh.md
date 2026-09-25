# Python 项目结构与模块架构

设计结构清晰、模块边界明确、接口公开且目录结构可维护的 Python 项目。良好的组织使代码易于发现，变更更具可预测性。

## 何时使用此技能

- 从零开始创建新的 Python 项目
- 为现有代码库进行重组以增强清晰度
- 使用 `__all__` 定义模块公共接口
- 在扁平结构和嵌套结构之间进行选择
- 确定测试文件放置策略
- 创建可重用的库包

## 核心概念

### 1. 模块内聚性

将一起变更的相关代码分组。每个模块应具有单一、明确的目的。

### 2. 显式接口

使用 `__all__` 定义公共部分。未列出的内容均为内部实现细节。

### 3. 扁平层级

优先使用浅层目录结构。仅在存在真实子域时才增加深度。

### 4. 一致的规范

在整个项目中统一应用命名和组织模式。

## 快速入门

```
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── services/
│       ├── models/
│       └── api/
├── tests/
├── pyproject.toml
└── README.md
```

## 基础模式

### 模式 1：每个文件对应一个概念

每个文件应专注于单一概念或紧密相关的函数集。当文件：

- 处理多个不相关的职责
- 超过 300-500 行（因复杂度而异）
- 包含因不同原因而变更的类

时，应考虑拆分。

```python
# 良好：专注的文件
# user_service.py - 用户业务逻辑
# user_repository.py - 用户数据访问
# user_models.py - 用户数据结构

# 避免：杂项文件
# user.py - 包含服务、仓库、模型、工具等...
```

### 模式 2：使用 `__all__` 定义显式公共接口

为每个模块定义公共接口。未列出的成员为内部实现细节。

```python
# mypackage/services/__init__.py
from .user_service import UserService
from .order_service import OrderService
from .exceptions import ServiceError, ValidationError

__all__ = [
    "UserService",
    "OrderService",
    "ServiceError",
    "ValidationError",
]

# 内部辅助函数通过省略保持私有
# from .internal_helpers import _validate_input  # 未导出
```

### 模式 3：扁平目录结构

优先使用最小嵌套。深层结构使导入语句冗长且导航困难。

```
# 优先：扁平结构
project/
├── api/
│   ├── routes.py
│   └── middleware.py
├── services/
│   ├── user_service.py
│   └── order_service.py
├── models/
│   ├── user.py
│   └── order.py
└── utils/
    └── validation.py

# 避免：深层嵌套
project/core/internal/services/impl/user/
```

仅在存在需要隔离的真实子域时才添加子包。

### 模式 4：测试文件组织

选择一种方法并在整个项目中一致应用。

**选项 A：文件内联测试**

```
src/
├── user_service.py
├── test_user_service.py
├── order_service.py
└── test_order_service.py
```

优点：测试代码紧邻其验证的代码。易于发现覆盖率缺口。

**选项 B：并行测试目录**

```
src/
├── services/
│   ├── user_service.py
│   └── order_service.py
tests/
├── services/
│   ├── test_user_service.py
│   └── test_order_service.py
```

优点：生产代码和测试代码清晰分离。大型项目标准做法。

## 高级模式

### 模式 5：包初始化

使用 `__init__.py` 为包消费者提供干净的公共接口。

```python
# mypackage/__init__.py
"""MyPackage - 一个用于执行有用操作的库。"""

from .core import MainClass, HelperClass
from .exceptions import PackageError, ConfigError
from .config import Settings

__all__ = [
    "MainClass",
    "HelperClass",
    "PackageError",
    "ConfigError",
    "Settings",
]

__version__ = "1.0.0"
```

消费者可以直接从包导入：

```python
from mypackage import MainClass, Settings
```

### 模式 6：分层架构

按架构层组织代码以实现清晰的职责分离。

```
myapp/
├── api/           # HTTP 处理、请求/响应
│   ├── routes/
│   └── middleware/
├── services/      # 业务逻辑
├── repositories/  # 数据访问
├── models/        # 领域实体
├── schemas/       # API 模式（Pydantic）
└── config/        # 配置
```

每一层只能依赖其下层的层，不能依赖其上层的层。

### 模式 7：领域驱动结构

对于复杂应用，按业务领域而非技术层级组织。

```
ecommerce/
├── users/
│   ├── models.py
│   ├── services.py
│   ├── repository.py
│   └── api.py
├── orders/
│   ├── models.py
│   ├── services.py
│   ├── repository.py
│   └── api.py
└── shared/
    ├── database.py
    └── exceptions.py
```

## 文件和模块命名

### 规范

- 所有文件和模块名使用 `snake_case`：`user_repository.py`
- 避免意义模糊的缩写：`user_repository.py` 而不是 `usr_repo.py`
- 类名应与文件名匹配：`UserService` 在 `user_service.py` 中

### 导入风格

使用绝对导入以增强清晰度和可靠性：

```python
# 优先：绝对导入
from myproject.services import UserService
from myproject.models import User

# 避免：相对导入
from ..services import UserService
from . import models
```

相对导入在模块移动或重组时可能失效。

## 最佳实践总结

1. **保持文件专注** - 每个文件对应一个概念，考虑在 300-500 行（因复杂度而异）时拆分
2. **明确定义 `__all__`** - 使公共接口清晰
3. **优先扁平结构** - 仅在存在真实子域时增加深度
4. **使用绝对导入** - 更可靠且清晰
5. **保持一致性** - 在整个项目中统一应用模式
6. **名称与内容匹配** - 文件名应描述其用途
7. **分离关注点** - 保持层清晰且依赖单向流动
8. **记录结构** - 包含 README 解释组织方式
