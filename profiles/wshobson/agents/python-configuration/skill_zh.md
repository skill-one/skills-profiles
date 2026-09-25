# Python 配置管理

使用环境变量和类型化设置将配置从代码中分离出来。良好的配置管理使相同代码能够在任何环境中无修改运行。

## 使用此技能的场景

- 设置新项目的配置系统
- 从硬编码值迁移到环境变量
- 使用 pydantic-settings 实现类型化配置
- 管理密钥和敏感值
- 创建特定环境的设置（开发/预发布/生产）
- 在应用程序启动时验证配置

## 核心概念

### 1. 分离配置

所有特定于环境的价值（URL、密钥、功能标志）都来自环境变量，而不是代码。

### 2. 类型化设置

在启动时将配置解析并验证为类型化对象，而不是分散在代码中。

### 3. 快速失败

在应用程序启动时验证所有必需的配置。缺少配置应立即以清晰的错误信息崩溃。

### 4. 合理的默认值

为本地开发提供合理的默认值，同时要求敏感设置显式值。

## 快速入门

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    api_key: str = Field(alias="API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")

settings = Settings()  # 从环境变量加载
```

## 基础模式

### 模式 1：使用 Pydantic 的类型化设置

创建一个中央设置类，加载和验证所有配置。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, ValidationError
import sys

class Settings(BaseSettings):
    """从环境变量加载的应用程序配置。"""

    # 数据库
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # API 密钥
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # 功能标志
    enable_new_feature: bool = Field(default=False, alias="ENABLE_NEW_FEATURE")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# 在模块加载时创建单例实例
try:
    settings = Settings()
except ValidationError as e:
    print(f"配置错误:\n{e}")
    sys.exit(1)
```

在整个应用程序中导入 `settings`：

```python
from myapp.config import settings

def get_database_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
```

### 模式 2：缺少配置时快速失败

必需的设置应立即以清晰的错误信息崩溃应用程序。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
import sys

class Settings(BaseSettings):
    # 必需的 - 无默认值意味着必须设置
    api_key: str = Field(alias="API_KEY")
    database_url: str = Field(alias="DATABASE_URL")

    # 带默认值的可选设置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

try:
    settings = Settings()
except ValidationError as e:
    print("=" * 60)
    print("配置错误")
    print("=" * 60)
    for error in e.errors():
        field = error["loc"][0]
        print(f"  - {field}: {error['msg']}")
    print("\n请设置必需的环境变量。")
    sys.exit(1)
```

启动时的清晰错误比请求中途的神秘 `None` 失败更好。

### 模式 3：本地开发默认值

为本地开发提供合理的默认值，同时要求敏感设置显式值。

```python
class Settings(BaseSettings):
    # 有本地默认值，但生产环境会覆盖
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")

    # 总是必需的 - 敏感设置无默认值
    db_password: str = Field(alias="DB_PASSWORD")
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # 开发便利性
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = {"env_file": ".env"}
```

为本地开发创建 `.env` 文件（切勿提交此文件）：

```bash
# .env (添加到 .gitignore)
DB_PASSWORD=local_dev_password
API_SECRET_KEY=dev-secret-key
DEBUG=true
```

### 模式 4：命名空间环境变量

为清晰性和易于调试而前缀相关变量。

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=admin
DB_PASSWORD=secret

# Redis 配置
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=10

# 身份验证
AUTH_SECRET_KEY=your-secret-key
AUTH_TOKEN_EXPIRY_SECONDS=3600
AUTH_ALGORITHM=HS256

# 功能标志
FEATURE_NEW_CHECKOUT=true
FEATURE_BETA_UI=false
```

使 `env | grep DB_` 对调试有用。

## 详细示例和模式

详细部分（以 `## 高级模式` 开头）位于 `references/details.md` 中。当上述导航摘要不足以说明时，请阅读该文件。

## 最佳实践总结

1. **切勿硬编码配置** - 所有特定于环境的价值来自环境变量
2. **使用类型化设置** - 使用 pydantic-settings 进行验证
3. **快速失败** - 在启动时因缺少必需配置而崩溃
4. **提供开发默认值** - 使本地开发变得容易
5. **切勿提交密钥** - 使用 `.env` 文件（忽略 git）或密钥管理器
6. **命名空间变量** - `DB_HOST`、`REDIS_URL` 为清晰性
7. **导入设置单例** - 不要在整个代码中调用 `os.getenv()`
8. **记录所有变量** - README 应列出必需的环境变量
9. **早期验证** - 在启动时检查配置正确性
10. **使用 secrets_dir** - 支持容器中挂载的密钥
