# Python 测试模式

使用 pytest、Fixtures、Mocking、参数化以及测试驱动开发实践来实现 Python 中健壮测试策略的全面指南。

## 何时使用这项技能

- 为 Python 代码编写单元测试
- 设置测试套件和测试基础设施
- 实施测试驱动开发（TDD）
- 创建 API 和服务的集成测试
- Mocking 外部依赖和服务
- 测试异步代码和并发操作
- 在 CI/CD 中设置持续测试
- 实施属性驱动测试
- 测试数据库操作
- 调试失败的测试

## 核心概念

### 1. 测试类型

- **单元测试**：独立测试单个函数/类
- **集成测试**：测试组件之间的交互
- **功能测试**：端到端测试完整功能
- **性能测试**：测量速度和资源使用情况

### 2. 测试结构（AAA 模式）

- **Arrange**：设置测试数据和前提条件
- **Act**：执行待测试代码
- **Assert**：验证结果

### 3. 测试覆盖率

- 衡量测试执行了哪些代码
- 识别未测试的代码路径
- 追求有意义的覆盖率，而不仅仅是高百分比

### 4. 测试隔离

- 测试应该是独立的
- 测试之间没有共享状态
- 每个测试应该自我清理

## 快速入门

```python
# test_example.py
def add(a, b):
    return a + b

def test_add():
    """基本测试示例。"""
    result = add(2, 3)
    assert result == 5

def test_add_negative():
    """使用负数进行测试。"""
    assert add(-1, 1) == 0

# 使用 pytest test_example.py 运行
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 测试最佳实践

### 测试组织

```python
# tests/
#   __init__.py
#   conftest.py           # 共享 Fixtures
#   test_unit/            # 单元测试
#     test_models.py
#     test_utils.py
#   test_integration/     # 集成测试
#     test_api.py
#     test_database.py
#   test_e2e/            # 端到端测试
#     test_workflows.py
```

### 测试命名约定

常见模式：`test_<单元>_<场景>_<预期结果>`。根据团队偏好进行调整。

```python
# 模式：test_<单元>_<场景>_<预期>
def test_create_user_with_valid_data_returns_user():
    ...

def test_create_user_with_duplicate_email_raises_conflict():
    ...

def test_get_user_with_unknown_id_returns_none():
    ...

# 好的测试名称 - 清晰且描述性强
def test_user_creation_with_valid_data():
    """清晰名称描述了正在测试的内容。"""
    pass

def test_login_fails_with_invalid_password():
    """名称描述了预期行为。"""
    pass

def test_api_returns_404_for_missing_resource():
    """具体说明输入和预期结果。"""
    pass

# 坏的测试名称 - 避免这些
def test_1():  # 不描述性
    pass

def test_user():  # 太模糊
    pass

def test_function():  # 没有说明测试内容
    pass
```

### 测试重试行为

使用 Mock 侧效应验证重试逻辑是否正确。

```python
from unittest.mock import Mock

def test_retries_on_transient_error():
    """测试服务在临时失败时重试。"""
    client = Mock()
    # 失败两次，然后成功
    client.request.side_effect = [
        ConnectionError("Failed"),
        ConnectionError("Failed"),
        {"status": "ok"},
    ]

    service = ServiceWithRetry(client, max_retries=3)
    result = service.fetch()

    assert result == {"status": "ok"}
    assert client.request.call_count == 3

def test_gives_up_after_max_retries():
    """测试服务在最大尝试次数后停止重试。"""
    client = Mock()
    client.request.side_effect = ConnectionError("Failed")

    service = ServiceWithRetry(client, max_retries=3)

    with pytest.raises(ConnectionError):
        service.fetch()

    assert client.request.call_count == 3

def test_does_not_retry_on_permanent_error():
    """测试永久错误不会被重试。"""
    client = Mock()
    client.request.side_effect = ValueError("Invalid input")

    service = ServiceWithRetry(client, max_retries=3)

    with pytest.raises(ValueError):
        service.fetch()

    # 只调用一次 - ValueError 不会重试
    assert client.request.call_count == 1
```

### 使用 Freezegun Mocking 时间

使用 freezegun 控制测试中的时间，以实现可预测的时间依赖行为。

```python
from freezegun import freeze_time
from datetime import datetime, timedelta

@freeze_time("2026-01-15 10:00:00")
def test_token_expiry():
    """测试令牌在正确时间过期。"""
    token = create_token(expires_in_seconds=3600)
    assert token.expires_at == datetime(2026, 1, 15, 11, 0, 0)

@freeze_time("2026-01-15 10:00:00")
def test_is_expired_returns_false_before_expiry():
    """测试令牌在有效期内未过期。"""
    token = create_token(expires_in_seconds=3600)
    assert not token.is_expired()

@freeze_time("2026-01-15 12:00:00")
def test_is_expired_returns_true_after_expiry():
    """测试令牌在有效期后过期。"""
    token = Token(expires_at=datetime(2026, 1, 15, 11, 30, 0))
    assert token.is_expired()

def test_with_time_travel():
    """使用 freeze_time 上下文测试跨时间的行为。"""
    with freeze_time("2026-01-01") as frozen_time:
        item = create_item()
        assert item.created_at == datetime(2026, 1, 1)

        # 时间前进
        frozen_time.move_to("2026-01-15")
        assert item.age_days == 14
```

### 测试标记

```python
# test_markers.py
import pytest

@pytest.mark.slow
def test_slow_operation():
    """标记慢速测试。"""
    import time
    time.sleep(2)


@pytest.mark.integration
def test_database_integration():
    """标记集成测试。"""
    pass


@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    """临时跳过测试。"""
    pass


@pytest.mark.skipif(os.name == "nt", reason="仅限 Unix 测试")
def test_unix_specific():
    """条件跳过。"""
    pass


@pytest.mark.xfail(reason="已知错误 #123")
def test_known_bug():
    """标记预期失败。"""
    assert False


# 使用：
# pytest -m slow          # 仅运行慢速测试
# pytest -m "not slow"    # 跳过慢速测试
# pytest -m integration   # 运行集成测试
```

### 覆盖率报告

```bash
# 安装覆盖率
pip install pytest-cov

# 运行带覆盖率的测试
pytest --cov=myapp tests/

# 生成 HTML 报告
pytest --cov=myapp --cov-report=html tests/

# 如果覆盖率低于阈值则失败
pytest --cov=myapp --cov-fail-under=80 tests/

# 显示缺失行
pytest --cov=myapp --cov-report=term-missing tests/
```

有关高级模式（异步测试、monkeypatching、属性驱动测试、数据库测试、CI/CD 集成和配置），请参阅 [references/advanced-patterns.md](references/advanced-patterns.md)
