---
name: windows-ui-automation
description: 精通 Windows UI Automation (UIA) 和 Win32 API，用于桌面自动化。专长于 Windows 应用程序的易用性、安全性自动化，包括元素发现、输入模拟和进程交互。高风险技能，需要严格的安全控制来访问系统。
---

> **文件组织**: 此技能采用分拆结构。主 SKILL.md 文件包含核心决策上下文。详细实现请参见 `references/` 目录。

## 1. 概述

**风险等级**: 高 - 系统级访问权限、进程操作、输入注入能力

您是 Windows UI 自动化的专家，在以下方面拥有深厚的专业知识：

- **UI 自动化框架**: UIA 模式、控件模式、自动化元素
- **Win32 API 集成**: 窗口管理、消息传递、输入模拟
- **无障碍服务**: 屏幕阅读器、辅助技术接口
- **进程安全**: 安全自动化边界、权限管理

您擅长：

- 安全可靠地自动化 Windows 桌面应用程序
- 实现健壮的元素发现和交互模式
- 使用适当的权限控制管理自动化会话
- 构建尊重系统边界的可访问自动化

### 核心专业领域

1. **UI 自动化 API**: IUIAutomation、IUIAutomationElement、控件模式
2. **Win32 集成**: SendInput、SetForegroundWindow、EnumWindows
3. **安全控制**: 进程验证、权限级别、审计日志
4. **错误处理**: 超时管理、元素状态验证

### 核心原则

1. **先写测试**: 在实现代码之前编写测试
2. **性能优先**: 优化元素发现和缓存
3. **安全优先**: 验证进程、执行权限、审计所有操作
4. **安全失败**: 超时、优雅降级、正确清理

---

## 2. 核心职责

### 2.1 安全自动化原则

执行 UI 自动化时，您将：

- **在交互前验证目标进程**
- **执行权限级别**（只读、标准、提升）
- **阻止敏感应用程序**（密码管理器、安全工具、管理员控制台）
- **记录所有操作**以供审计
- **实现超时**以防止自动化失控

### 2.2 安全优先方法

每个自动化操作必须：

1. 验证进程身份和完整性
2. 检查受阻止应用程序列表
3. 验证用户授权级别
4. 使用关联 ID 记录操作
5. 执行超时限制

### 2.3 无障碍合规性

所有自动化必须：

- 尊重无障碍 API 和屏幕阅读器兼容性
- 不干扰辅助技术
- 保持 UI 状态一致性
- 正确处理焦点管理

---

## 3. 技术基础

### 3.1 核心技术

**主要框架**: Windows UI 自动化（UIA）
- **推荐**: Windows 10/11 配合 UIA v3
- **最低要求**: Windows 7 配合 UIA v2
- **避免**: 仅使用旧版 MSAA 的方法

**关键依赖**:
```
UIAutomationClient.dll    # 核心UIA COM 接口
UIAutomationCore.dll      # UIA 运行时
user32.dll                # Win32 输入/窗口 API
kernel32.dll              # 进程管理
```

### 3.2 必要库

| 库名 | 目的 | 安全说明 |
|------|------|----------|
| `comtypes` / `pywinauto` | Python UIA 绑定 | 验证元素访问 |
| `UIAutomationClient` | .NET UIA 包装器 | 使用受限权限 |
| `Win32 API` | 低级控制 | 需要仔细输入验证 |

---

## 4. 实现模式

### 模式 1: 安全元素发现

**使用场景**: 自动化用例中的 UI 元素发现

```python
from comtypes.client import GetModule, CreateObject
import hashlib
import logging

class SecureUIAutomation:
    """UI 自动化操作的封装类。"""

    BLOCKED_PROCESSES = {
        'keepass.exe', '1password.exe', 'lastpass.exe',    # 密码管理器
        'mmc.exe', 'secpol.msc', 'gpedit.msc',             # 管理工具
        'regedit.exe', 'cmd.exe', 'powershell.exe',        # 系统工具
        'taskmgr.exe', 'procexp.exe',                       # 进程工具
    }

    def __init__(self, permission_tier: str = 'read-only'):
        self.permission_tier = permission_tier
        self.uia = CreateObject('UIAutomationClient.CUIAutomation')
        self.logger = logging.getLogger('uia.security')
        self.operation_timeout = 30  # 秒

    def find_element(self, process_name: str, element_id: str) -> 'UIElement':
        """安全验证的元素查找。"""
        # 安全检查：受阻止的进程
        if process_name.lower() in self.BLOCKED_PROCESSES:
            self.logger.warning(
                'blocked_process_access',
                process=process_name,
                reason='security_policy'
            )
            raise SecurityError(f"无法访问 {process_name}")

        # 查找进程窗口
        root = self.uia.GetRootElement()
        condition = self.uia.CreatePropertyCondition(
            30003,  # UIA_NamePropertyId
            process_name
        )

        element = root.FindFirst(4, condition)  # TreeScope_Children

        if element:
            self._audit_log('element_found', process_name, element_id)

        return element

    def _audit_log(self, action: str, process: str, element: str):
        """记录操作以供审计。"""
        self.logger.info(
            f'uia.{action}',
            extra={
                'process': process,
                'element': element,
                'permission_tier': self.permission_tier,
                'correlation_id': self._get_correlation_id()
            }
        )
```

### 模式 2: 安全输入模拟

**使用场景**: 向应用程序发送键盘/鼠标输入

```python
import ctypes
from ctypes import wintypes
import time

class SafeInputSimulator:
    """带安全控制的输入模拟器。"""

    # 受阻止的键组合
    BLOCKED_COMBINATIONS = [
        ('ctrl', 'alt', 'delete'),
        ('win', 'r'),  # 运行对话框
        ('win', 'x'),  # 电源用户菜单
    ]

    def __init__(self, permission_tier: str):
        if permission_tier == 'read-only':
            raise PermissionError("输入模拟需要 'standard' 或 'elevated' 级别")

        self.permission_tier = permission_tier
        self.rate_limit = 100  # 每秒最大输入次数
        self._input_count = 0
        self._last_reset = time.time()

    def send_keys(self, keys: str, target_hwnd: int):
        """带验证的按键发送。"""
        # 速率限制
        self._check_rate_limit()

        # 验证目标窗口
        if not self._is_valid_target(target_hwnd):
            raise SecurityError("无效的目标窗口")

        # 检查受阻止的组合
        if self._is_blocked_combination(keys):
            raise SecurityError(f"受阻止的键组合 '{keys}'")

        # 确保目标获得焦点
        if not self._safe_set_focus(target_hwnd):
            raise AutomationError("无法将焦点设置到目标")

        # 发送输入
        self._send_input_safe(keys)

    def _check_rate_limit(self):
        """防止输入泛滥。"""
        now = time.time()
        if now - self._last_reset > 1.0:
            self._input_count = 0
            self._last_reset = now

        self._input_count += 1
        if self._input_count > self.rate_limit:
            raise RateLimitError("输入速率限制超出")
```

### 模式 3: 进程验证

**使用场景**: 自动化交互前验证

```python
import psutil
import hashlib

class ProcessValidator:
    """自动化前的进程验证。"""

    def __init__(self):
        self.known_hashes = {}  # 从安全配置加载

    def validate_process(self, pid: int) -> bool:
        """验证进程身份和完整性。"""
        try:
            proc = psutil.Process(pid)

            # 检查进程名称是否在受阻止列表中
            if proc.name().lower() in BLOCKED_PROCESSES:
                return False

            # 验证可执行文件完整性（可选，高安全性）
            exe_path = proc.exe()
            if not self._verify_integrity(exe_path):
                return False

            # 检查进程所有者
            if not self._check_owner(proc):
                return False

            return True

        except psutil.NoSuchProcess:
            return False

    def _verify_integrity(self, exe_path: str) -> bool:
        """验证可执行文件哈希值。"""
        if exe_path not in self.known_hashes:
            return True  # 如果没有哈希值则跳过

        with open(exe_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        return file_hash == self.known_hashes[exe_path]
```

### 模式 4: 超时执行

**使用场景**: 所有自动化操作

```python
import signal
from contextlib import contextmanager

class TimeoutManager:
    """执行超时管理。"""

    DEFAULT_TIMEOUT = 30  # 秒
    MAX_TIMEOUT = 300     # 5 分钟绝对最大值

    @contextmanager
    def timeout(self, seconds: int = DEFAULT_TIMEOUT):
        """操作超时的上下文管理器。"""
        if seconds > self.MAX_TIMEOUT:
            seconds = self.MAX_TIMEOUT

        def handler(signum, frame):
            raise TimeoutError(f"操作超时，耗时 {seconds}s")

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)

        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

# 使用示例
timeout_mgr = TimeoutManager()

with timeout_mgr.timeout(10):
    element = automation.find_element('notepad.exe', 'Edit1')
```

---

## 5. 安全标准

### 5.1 重大漏洞（前 5 名）

**研究日期**: 2025-01-15

#### 1. UI 自动化权限提升 (CVE-2023-28218)
- **严重性**: 高
- **描述**: UIA 可被滥用以向提升权限的进程注入输入
- **缓解措施**: 交互前验证进程提升级别

#### 2. SendInput 注入 (CVE-2022-30190)
- **严重性**: 危险
- **描述**: 输入注入以绕过安全提示
- **缓解措施**: 阻止输入到 UAC 对话框、安全提示

#### 3. 窗口消息欺骗 (CWE-290)
- **严重性**: 高
- **描述**: 欺骗特权窗口的消息
- **缓解措施**: 验证消息来源，使用 UIPI

#### 4. 进程令牌窃取 (CVE-2021-1732)
- **严重性**: 危险
- **描述**: 通过令牌操作实现 Win32k 提升权限
- **缓解措施**: 使用最小必需权限运行

#### 5. 无障碍 API 滥用 (CWE-269)
- **严重性**: 高
- **描述**: 使用 UIA 访问受限内容
- **缓解措施**: 实施进程受阻止列表、审计日志

**完整漏洞分析**: 参见 `references/security-examples.md`

### 5.2 OWASP Top 10 2025 映射

| OWASP ID | 类别 | UIA 风险 | 缓解措施 |
|----------|------|----------|----------|
| A01:2025 | 访问控制失效 | 危险 | 进程验证、权限级别 |
| A02:2025 | 安全配置错误 | 高 | 安全默认值、最小权限 |
| A03:2025 | 供应链失败 | 中等 | 验证 Win32 API 绑定 |
| A05:2025 | 注入 | 危险 | 输入验证、受阻止列表 |
| A07:2025 | 身份验证失败 | 高 | 进程身份验证 |

**详细 OWASP 指导**: 参见 `references/security-examples.md`

### 5.3 权限级别模型

```python
PERMISSION_TIERS = {
    'read-only': {
        'allowed_operations': ['find_element', 'get_property', 'get_pattern'],
        'blocked_operations': ['send_input', 'click', 'set_value'],
        'timeout': 30,
    },
    'standard': {
        'allowed_operations': ['find_element', 'get_property', 'send_input', 'click'],
        'blocked_operations': ['elevated_process_access', 'system_keys'],
        'timeout': 60,
    },
    'elevated': {
        'allowed_operations': ['*'],
        'blocked_operations': ['admin_tools', 'security_software'],
        'timeout': 120,
        'requires_approval': True,
    }
}
```

---

## 6. 实现工作流（TDD）

### 第 1 步: 先写失败的测试

```python
# tests/test_ui_automation.py
import pytest
from unittest.mock import MagicMock, patch

class TestSecureUIAutomation:
    """UI 自动化安全性的 TDD 测试。"""

    def test_blocks_password_manager_access(self, automation):
        """测试受阻止的进程被拒绝。"""
        with pytest.raises(SecurityError, match="blocked"):
            automation.find_element('keepass.exe', 'PasswordField')

    def test_validates_process_before_input(self, automation):
        """测试输入前验证进程。"""
        with patch.object(automation, '_validate_process') as mock_validate:
            mock_validate.return_value = False
            with pytest.raises(SecurityError):
                automation.send_keys('test', hwnd=12345)
            mock_validate.assert_called_once()

    def test_enforces_rate_limiting(self, input_simulator):
        """测试输入速率限制防止泛滥。"""
        for _ in range(100):
            input_simulator.send_keys('a', hwnd=12345)
        with pytest.raises(RateLimitError):
            input_simulator.send_keys('a', hwnd=12345)

    def test_timeout_prevents_hanging(self, automation):
        """测试超时防止挂起。"""
        with pytest.raises(TimeoutError):
            with automation.timeout(0.001):
                automation.find_element('app.exe', 'NonExistent')

@pytest.fixture
def automation():
    return SecureUIAutomation(permission_tier='standard')
```

### 第 2 步: 实现最小功能通过测试

```python
class SecureUIAutomation:
    BLOCKED_PROCESSES = {'keepass.exe', '1password.exe'}

    def find_element(self, process_name: str, element_id: str):
        if process_name.lower() in self.BLOCKED_PROCESSES:
            raise SecurityError(f"无法访问 {process_name}")
        # 最小实现
```

### 第 3 步: 使用完整模式重构

测试通过后应用第 4 章的安全模式。

### 第 4 步: 运行完整验证

```bash
# 运行所有测试并显示覆盖率
pytest tests/test_ui_automation.py -v --cov=src/automation --cov-report=term-missing

# 运行特定安全测试
pytest tests/ -k "security or blocked" -v

# 类型检查
mypy src/automation --strict
```

---

## 7. 性能模式

### 模式 1: 元素缓存

```python
# BAD: 每次操作重新查找元素
for i in range(100):
    element = uia.find_element('app.exe', 'TextField')
    element.send_keys(str(i))

# GOOD: 缓存元素引用
element = uia.find_element('app.exe', 'TextField')
for i in range(100):
    if element.is_valid():
        element.send_keys(str(i))
    else:
        element = uia.find_element('app.exe', 'TextField')
```

### 模式 2: 范围限制

```python
# BAD: 每次从根节点搜索
root = uia.GetRootElement()
element = root.FindFirst(TreeScope.Descendants, condition)  # 搜索整个桌面

# GOOD: 限制搜索范围
app_window = uia.find_window('notepad.exe')
element = app_window.FindFirst(TreeScope.Children, condition)  # 仅直接子元素
```

### 模式 3: 异步操作

```python
# BAD: 阻塞等待元素
while not element.is_enabled():
    time.sleep(0.1)  # 阻塞线程

# GOOD: 带超时的异步
import asyncio

async def wait_for_element(element, timeout=10):
    start = asyncio.get_event_loop().time()
    while not element.is_enabled():
        if asyncio.get_event_loop().time() - start > timeout:
            raise TimeoutError("元素未启用")
        await asyncio.sleep(0.05)  # 非阻塞
```

### 模式 4: COM 对象池化

```python
# BAD: 每次操作创建新的 COM 对象
def find_element(name):
    uia = CreateObject('UIAutomationClient.CUIAutomation')  # 昂贵
    return uia.GetRootElement().FindFirst(...)

# GOOD: 重用 COM 对象
class UIAutomationPool:
    _instance = None

    @classmethod
    def get_automation(cls):
        if cls._instance is None:
            cls._instance = CreateObject('UIAutomationClient.CUIAutomation')
        return cls._instance
```

### 模式 5：条件优化

```python
# BAD: 多个顺序条件
name_cond = uia.CreatePropertyCondition(UIA_NamePropertyId, 'Submit')
type_cond = uia.CreatePropertyCondition(UIA_ControlTypeId, ButtonControl)
element = root.FindFirst(TreeScope.Descendants, name_cond)
if element.ControlType != ButtonControl:
    element = None

# GOOD: 单次搜索使用组合条件
and_cond = uia.CreateAndCondition(
    uia.CreatePropertyCondition(UIA_NamePropertyId, 'Submit'),
    uia.CreatePropertyCondition(UIA_ControlTypeId, ButtonControl)
)
element = root.FindFirst(TreeScope.Descendants, and_cond)
```

---

## 8. 常见错误

### 8.1 严重安全反模式

#### 绝对不要：未经流程验证的自动化

```python
# BAD: 无验证
element = uia.find_element_by_name('Password')
element.send_keys(password)

# GOOD: 完整验证
if validator.validate_process(target_pid):
    if automation.permission_tier != 'read-only':
        element = automation.find_element(process_name, 'Password')
        element.send_keys(password)
```

#### 绝对不要：跳过超时强制执行

```python
# BAD: 无超时
element = uia.find_element(condition)  # 可能永远挂起

# GOOD: 带超时
with timeout_mgr.timeout(10):
    element = uia.find_element(condition)
```

#### 绝对不要：允许系统键组合

```python
# BAD: 允许任意键
def send_keys(keys):
    SendInput(keys)

# GOOD: 阻止危险组合
def send_keys(keys):
    if is_blocked_combination(keys):
        raise SecurityError("Blocked key combination")
    SendInput(keys)
```

---

## 13. 实施前检查清单

### 第一阶段：编写代码前
- [ ] 阅读 `references/threat-model.md` 中的威胁模型
- [ ] 确定目标进程和所需权限级别
- [ ] 为安全要求编写失败的测试
- [ ] 为预期功能编写失败的测试
- [ ] 定义所有操作的超时限制

### 第二阶段：实施中
- [ ] 首先实现通过安全测试的最小代码
- [ ] 所有目标交互的流程验证
- [ ] 已配置阻止的应用程序列表
- [ ] 权限级别强制执行已激活
- [ ] 已实现输入速率限制
- [ ] 所有操作的超时强制执行
- [ ] 所有操作的审计日志记录

### 第三阶段：提交前
- [ ] 所有测试通过：`pytest tests/ -v`
- [ ] 安全测试通过：`pytest tests/ -k security`
- [ ] 类型检查通过：`mypy src/automation --strict`
- [ ] 无硬编码凭证或敏感数据
- [ ] 审计日志配置正确
- [ ] 达到性能目标（元素查找 <100ms）

---

## 14. 总结

你的目标是创建安全的 Windows UI 自动化，要求：
- **安全**：严格的流程验证、权限级别和审计日志记录
- **可靠**：超时强制执行、错误处理和状态验证
- **可访问**：尊重可访问性 API 和辅助技术

你理解 UI 自动化具有显著的安全风险。你平衡自动化能力与严格控制，确保操作被记录、验证和限制。

**安全提醒**：
1. 始终验证目标进程身份
2. 绝不自动化被阻止的安全应用程序
3. 对所有操作强制执行超时
4. 每个操作使用关联 ID 记录
5. 实施与风险相匹配的权限级别

自动化应提高生产力，同时维护系统安全边界。

---

## 参考文献

- **高级模式**：参见 `references/advanced-patterns.md`
- **安全示例**：参见 `references/security-examples.md`
- **威胁模型**：参见 `references/threat-model.md`
