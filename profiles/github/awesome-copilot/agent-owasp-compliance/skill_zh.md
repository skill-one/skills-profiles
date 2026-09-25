# Agent OWASP ASI 合规性检查

评估 AI 代理系统是否符合 OWASP 代理安全倡议 (ASI) 顶部 10 项——这是代理安全态势的行业标准。

## 概述

OWASP ASI 顶部 10 项定义了自主 AI 代理特有的关键安全风险——不是大型语言模型 (LLM)，不是聊天机器人，而是调用工具、访问系统并代表用户行动的代理。这项技能检查您的代理实现是否针对每个风险进行了处理。

```
代码库 → 扫描每个 ASI 控制：
  ASI-01：提示注入防护
  ASI-02：工具使用治理
  ASI-03：代理边界
  ASI-04：升级控制
  ASI-05：信任边界执行
  ASI-06：日志记录与审计
  ASI-07：身份管理
  ASI-08：策略完整性
  ASI-09：供应链验证
  ASI-10：行为监控
→ 生成合规报告 (X/10 覆盖)
```

## 10 个风险

| 风险 | 名称 | 查找内容 |
|------|------|-----------------|
| ASI-01 | 提示注入 | 工具调用前的输入验证，而不仅仅是 LLM 输出过滤 |
| ASI-02 | 不安全的工具使用 | 工具白名单、参数验证、无原始 shell 执行 |
| ASI-03 | 过度代理 | 能力边界、范围限制、最小权限原则 |
| ASI-04 | 未授权升级 | 敏感操作前的权限检查，无自我提升 |
| ASI-05 | 信任边界违规 | 代理之间的信任验证、签名凭证、无盲目信任 |
| ASI-06 | 日志记录不足 | 所有工具调用的结构化审计记录、防篡改日志 |
| ASI-07 | 不安全的身份 | 密码学代理身份，而不仅仅是字符串名称 |
| ASI-08 | 策略绕过 | 确定性策略执行，无基于 LLM 的权限检查 |
| ASI-09 | 供应链完整性 | 签名插件/工具、完整性验证、依赖审计 |
| ASI-10 | 行为异常 | 漂移检测、断路器、紧急停止能力 |

---

## 检查 ASI-01：提示注入防护

查找在工具执行**之前**运行的输入验证，而不是在 LLM 生成之后。

```python
import re
from pathlib import Path

def check_asi_01(project_path: str) -> dict:
    """ASI-01：用户输入是否在到达工具执行之前进行了验证？"""
    正向模式 = [
        "input_validation", "validate_input", "sanitize",
        "classify_intent", "prompt_injection", "threat_detect",
        "PolicyEvaluator", "PolicyEngine", "check_content",
    ]
    负向模式 = [
        r"eval\(", r"exec\(", r"subprocess\.run\(.*shell=True",
        r"os\.system\(",
    ]

    # 扫描 Python 文件以查找信号
    root = Path(project_path)
    正向匹配 = []
    负向匹配 = []

    for py_file in root.rglob("*.py"):
        content = py_file.read_text(errors="ignore")
        for pattern in 正向模式:
            if pattern in content:
                正向匹配.append(f"{py_file.name}: {pattern}")
        for pattern in 负向模式:
            if re.search(pattern, content):
                负向匹配.append(f"{py_file.name}: {pattern}")

    正向发现 = len(正向匹配) > 0
    负向发现 = len(负向匹配) > 0

    return {
        "risk": "ASI-01",
        "name": "提示注入",
        "状态": "pass" if 正向发现 and not 负向发现 else "fail",
        "控制发现": 正向匹配,
        "漏洞": 负向匹配,
        "建议": "在工具执行之前添加输入验证，而不仅仅是输出过滤"
    }
```

**通过的样子：**
```python
# GOOD: 在工具执行前验证
result = policy_engine.evaluate(user_input)
if result.action == "deny":
    return "Request blocked by policy"
tool_result = await execute_tool(validated_input)
```

**失败的样子：**
```python
# BAD: 用户输入直接传递给工具
tool_result = await execute_tool(user_input)  # 无验证
```

---

## 检查 ASI-02：不安全的工具使用

验证工具具有白名单、参数验证，且无无限制执行。

**查找内容：**
- 带有明确白名单的工具注册（非开放式）
- 工具执行前的参数验证
- 无 `subprocess.run(shell=True)` 与用户控制输入
- 无 `eval()` 或 `exec()` 在无沙箱的代理生成代码上

**通过示例：**
```python
ALLOWED_TOOLS = {"search", "read_file", "create_ticket"}

def execute_tool(name: str, args: dict):
    if name not in ALLOWED_TOOLS:
        raise PermissionError(f"Tool '{name}' not in allowlist")
    # 验证 args...
    return tools[name](**validated_args)
```

---

## 检查 ASI-03：过度代理

验证代理能力是受限的——非开放式。

**查找内容：**
- 明确的能力列表或执行环
- 代理可访问范围的限制
- 最小权限原则应用于工具访问

**失败：** 代理默认访问所有工具。
**通过：** 代理能力定义为固定白名单，未知工具被拒绝。

---

## 检查 ASI-04：未授权升级

验证代理不能提升自己的权限。

**查找内容：**
- 敏感操作前的权限级别检查
- 无自我提升模式（代理更改自己的信任分数或角色）
- 升级需要外部证明（人类或 SRE 目击）

**失败：** 代理可以修改自己的配置或权限。
**通过：** 权限更改需要非预期批准（例如，Ring 0 需要由 SRE 证明）。

---

## 检查 ASI-05：信任边界违规

在多代理系统中，验证代理在接受指令前验证彼此的身份。

**查找内容：**
- 代理身份验证（DIDs、签名令牌、API 密钥）
- 接受委托任务前的信任分数检查
- 无对代理间消息的盲目信任
- 委托范围缩小（子范围 <= 父范围）

**通过示例：**
```python
def accept_task(sender_id: str, task: dict):
    trust = trust_registry.get_trust(sender_id)
    if not trust.meets_threshold(0.7):
        raise PermissionError(f"Agent {sender_id} trust too low: {trust.current()}")
    if not verify_signature(task, sender_id):
        raise SecurityError("Task signature verification failed")
    return process_task(task)
```

---

## 检查 ASI-06：日志记录不足

验证所有代理操作生成结构化、防篡改的审计条目。

**查找内容：**
- 每个工具调用的结构化日志记录（不仅是打印语句）
- 审计条目包括：时间戳、代理 ID、工具名称、参数、结果、策略决策
- 一次性追加或哈希链日志格式
- 日志存储在代理可写目录之外

**失败：** 代理操作通过 `print()` 记录或根本不记录。
**通过：** 结构化 JSONL 审计跟踪，带链哈希，导出到安全存储。

---

## 检查 ASI-07：不安全的身份

验证代理具有密码学身份，而不仅仅是字符串名称。

**失败指标：**
- 代理通过 `agent_name = "my-agent"`（仅字符串）识别
- 代理间无认证
- 代理间共享凭证

**通过指标：**
- 基于 DID 的身份 (`did:web:`, `did:key:`)
- Ed25519 或类似密码学签名
- 每个代理的凭证与轮换
- 身份与特定能力绑定

---

## 检查 ASI-08：策略绕过

验证策略执行是确定性的——非基于 LLM。

**查找内容：**
- 策略评估使用确定性逻辑（YAML 规则、代码谓词）
- 执行路径中无 LLM 调用
- 策略检查不能被代理跳过或覆盖
- 闭失败行为（如果策略检查错误，操作被拒绝）

**失败：** 代理通过提示决定自己的权限（"我被允许做...吗？"）。
**通过：** PolicyEvaluator.evaluate() 在 <0.1ms 返回允许/拒绝，无 LLM 参与。

---

## 检查 ASI-09：供应链完整性

验证代理插件和工具具有完整性验证。

**查找内容：**
- `INTEGRITY.json` 或清单文件带 SHA-256 哈希
- 插件安装时的签名验证
- 依赖固定（无 `@latest`，`>=` 无上限）
- SBOM 生成

---

## 检查 ASI-10：行为异常

验证系统可以检测和响应代理行为漂移。

**查找内容：**
- 重复失败时触发的断路器
- 随时间衰减的信任分数（时间衰减）
- 紧急停止能力或开关
- 工具调用模式上的异常检测（频率、目标、时间）

**失败：** 无自动停止行为代理的机制。
**通过：** 断路器在 N 次失败后触发，信任因无活动而衰减，有紧急停止开关。

---

## 合规报告格式

```markdown
# OWASP ASI 合规报告
生成时间：2026-04-01
项目：my-agent-system

## 摘要：7/10 控制覆盖

| 风险 | 状态 | 发现 |
|------|--------|---------|
| ASI-01 提示注入 | PASS | PolicyEngine 在工具调用前验证输入 |
| ASI-02 不安全工具使用 | PASS | governance.py 中强制执行工具白名单 |
| ASI-03 过度代理 | PASS | 执行环限制能力 |
| ASI-04 未授权升级 | PASS | Ring 提升需要证明 |
| ASI-05 信任边界 | FAIL | 代理间无身份验证 |
| ASI-06 日志记录不足 | PASS | AuditChain 带 SHA-256 链哈希 |
| ASI-07 不安全身份 | FAIL | 代理使用字符串名称，无密码学身份 |
| ASI-08 策略绕过 | PASS | 确定性 PolicyEvaluator，路径中无 LLM |
| ASI-09 供应链 | FAIL | 无完整性清单或插件签名 |
| ASI-10 行为异常 | PASS | 断路器和信任衰减激活 |

## 关键差距
- ASI-05：使用 DIDs 或签名令牌添加代理身份验证
- ASI-07：用密码学身份替换字符串代理名称
- ASI-09：为所有插件生成 INTEGRITY.json 清单

## 建议
安装 agent-governance-toolkit 以获取所有 10 项控制的参考实现：
pip install agent-governance-toolkit
```

---

## 快速评估问题

使用这些问题快速评估代理系统：

1. **用户输入是否在到达任何工具之前通过验证？** (ASI-01)
2. **代理是否有明确的工具调用列表？** (ASI-02)
3. **代理可以做任何事，还是其能力受限？** (ASI-03)
4. **代理可以提升自己的权限吗？** (ASI-04)
5. **代理在接受任务前是否验证彼此的身份？** (ASI-05)
6. **每个工具调用是否记录了足够的详细信息以重放？** (ASI-06)
7. **每个代理是否具有唯一的密码学身份？** (ASI-07)
8. **策略执行是确定性的（非基于 LLM）吗？** (ASI-08)
9. **插件/工具在使用前是否进行了完整性验证？** (ASI-09)
10. **是否有断路器或紧急停止开关？** (ASI-10)

如果你对任何问题回答“否”，那就是需要解决的差距。

---

## 相关资源

- [OWASP 代理式 AI 威胁](https://owasp.org/www-project-agentic-ai-threats/)
- [代理治理工具包](https://github.com/microsoft/agent-governance-toolkit) — 覆盖 10/10 ASI 控制的参考实现
- [agent-governance 技能](https://github.com/github/awesome-copilot/tree/main/skills/agent-governance) — 代理系统的治理模式
