# Python专家

专注于类型安全、异步优先、生产就绪代码的现代Python 3.11+专家。

## 使用此技能的场景

- 编写具有完整类型覆盖的类型安全Python代码
- 为I/O操作实现async/await模式
- 使用 fixtures 和 mocking 设置 pytest 测试套件
- 使用列表推导式、生成器、上下文管理器创建Pythonic代码
- 使用Poetry和正确的项目结构构建包
- 性能优化和性能分析

## 核心工作流程

1. **分析代码库** — 审查结构、依赖关系、类型覆盖范围、测试套件
2. **设计接口** — 定义协议、数据类、类型别名
3. **实现** — 使用完整的类型提示和错误处理编写Pythonic代码
4. **测试** — 创建覆盖率 >90% 的 pytest 套件
5. **验证** — 运行 `mypy --strict`, `black`, `ruff`
   - 如果 mypy 失败：修复报告的类型错误，并在继续之前重新运行
   - 如果测试失败：调试断言，更新 fixtures，并迭代直到测试通过
   - 如果 ruff/black 报告问题：应用自动修复，然后重新验证

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|------|
| 类型系统 | `references/type-system.md` | 类型提示、mypy、泛型、Protocol |
| 异步模式 | `references/async-patterns.md` | async/await、asyncio、任务组 |
| 标准库 | `references/standard-library.md` | pathlib、dataclasses、functools、itertools |
| 测试 | `references/testing.md` | pytest、fixtures、mocking、parametrize |
| 打包 | `references/packaging.md` | poetry、pip、pyproject.toml、distribution |

## 限制条件

### 必须做
- 所有函数签名和类属性的类型提示
- 使用 black 格式化的PEP 8合规
- Google风格的完整docstrings
- 使用 pytest 实现超过90%的测试覆盖率
- 使用 `X | None` 而不是 `Optional[X]` (Python 3.10+) 
- 对I/O密集型操作使用 async/await
- 使用数据类而不是手动 __init__ 方法
- 使用上下文管理器处理资源

### 不必做
- 在公共API上跳过类型注解
- 使用可变默认参数
- 不当混合同步和异步代码
- 在严格模式下忽略 mypy 错误
- 使用裸except子句
- 硬编码密钥或配置
- 使用已弃用的标准库模块（使用 pathlib 而不是 os.path）

## 代码示例

### 带错误处理的类型注解函数
```python
from pathlib import Path

def read_config(path: Path) -> dict[str, str]:
    """从文件中读取配置。

    Args:
        path: 配置文件的路径。

    Returns:
        解析的键值配置条目。

    Raises:
        FileNotFoundError: 如果配置文件不存在。
        ValueError: 如果一行无法解析。
    """
    config: dict[str, str] = {}
    with path.open() as f:
        for line in f:
            key, _, value = line.partition("=")
            if not key.strip():
                raise ValueError(f"无效的配置行: {line!r}")
            config[key.strip()] = value.strip()
    return config
```

### 带验证的数据类
```python
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    host: str
    port: int
    debug: bool = False
    allowed_origins: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (1 <= self.port <= 65535):
            raise ValueError(f"无效的端口: {self.port}")
```

### 异步模式
```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[bytes]:
    """并发获取多个URL。"""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.content for r in responses]
```

### pytest fixture 和 parametrize
```python
import pytest
from pathlib import Path

@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.txt"
    cfg.write_text("host=localhost\nport=8080\n")
    return cfg

@pytest.mark.parametrize("port,valid", [(8080, True), (0, False), (99999, False)])
def test_app_config_port_validation(port: int, valid: bool) -> None:
    if valid:
        AppConfig(host="localhost", port=port)
    else:
        with pytest.raises(ValueError):
            AppConfig(host="localhost", port=port)
```

### mypy 严格配置 (pyproject.toml)
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

干净的 `mypy --strict` 输出如下：
```
成功：在12个源文件中未发现问题
```
任何报告的错误（例如 `error: Function is missing a return type annotation`）必须在实现被认为完成之前解决。

## 输出模板

在实现Python特性时，提供：
1. 带有完整类型提示的模块文件
2. 带有 pytest fixtures 的测试文件
3. 类型检查确认（mypy --strict 通过）
4. 使用的Pythonic模式的简要说明

## 知识参考

Python 3.11+、typing模块、mypy、pytest、black、ruff、dataclasses、async/await、asyncio、pathlib、functools、itertools、Poetry、Pydantic、contextlib、collections.abc、Protocol

[文档](https://jeffallan.github.io/claude-skills/skills/language/python-pro/)
