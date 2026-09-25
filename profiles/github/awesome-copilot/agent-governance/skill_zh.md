# 代理治理模式

为 AI 代理系统添加安全、信任和策略执行的模式。

## 概述

治理模式确保 AI 代理在定义的边界内运行——控制它们可以调用的工具、可以处理的内容、可以执行的程度，并通过审计跟踪保持问责制。

```
用户请求 → 意图分类 → 策略检查 → 工具执行 → 审计日志
                     ↓                      ↓               ↓
              威胁检测         允许/拒绝      信任更新
```

## 使用场景

- **具有工具访问权限的代理**：任何调用外部工具（API、数据库、shell 命令）的代理
- **多代理系统**：代理委托给其他代理需要信任边界
- **生产部署**：合规性、审计和安全要求
- **敏感操作**：金融交易、数据访问、基础设施管理

---

## 模式 1：治理策略

定义代理被允许执行的操作，作为可组合、可序列化的策略对象。

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re

class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"  # 标记为需要人工审核

@dataclass
class GovernancePolicy:
    """声明式策略控制代理行为。"""
    name: str
    allowed_tools: list[str] = field(default_factory=list)       # 允许列表
    blocked_tools: list[str] = field(default_factory=list)       # 阻止列表
    blocked_patterns: list[str] = field(default_factory=list)    # 内容过滤器
    max_calls_per_request: int = 100                             # 流量限制
    require_human_approval: list[str] = field(default_factory=list)  # 需要人工批准的工具

    def check_tool(self, tool_name: str) -> PolicyAction:
        """检查此策略是否允许工具。"""
        if tool_name in self.blocked_tools:
            return PolicyAction.DENY
        if tool_name in self.require_human_approval:
            return PolicyAction.REVIEW
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return PolicyAction.DENY
        return PolicyAction.ALLOW

    def check_content(self, content: str) -> Optional[str]:
        """检查内容是否匹配阻止模式。返回匹配的模式或 None。"""
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return pattern
        return None
```

### 策略组合

组合多个策略（例如，组织级 + 团队级 + 代理特定）：

```python
def compose_policies(*policies: GovernancePolicy) -> GovernancePolicy:
    """合并策略，使用最严格的语义。"""
    combined = GovernancePolicy(name="composed")

    for policy in policies:
        combined.blocked_tools.extend(policy.blocked_tools)
        combined.blocked_patterns.extend(policy.blocked_patterns)
        combined.require_human_approval.extend(policy.require_human_approval)
        combined.max_calls_per_request = min(
            combined.max_calls_per_request,
            policy.max_calls_per_request
        )
        if policy.allowed_tools:
            if combined.allowed_tools:
                combined.allowed_tools = [
                    t for t in combined.allowed_tools if t in policy.allowed_tools
                ]
            else:
                combined.allowed_tools = list(policy.allowed_tools)

    return combined


# 使用：从广泛到特定分层策略
org_policy = GovernancePolicy(
    name="org-wide",
    blocked_tools=["shell_exec", "delete_database"],
    blocked_patterns=[r"(?i)(api[_-]?key|secret|password)\s*[:=]"],
    max_calls_per_request=50
)
team_policy = GovernancePolicy(
    name="data-team",
    allowed_tools=["query_db", "read_file", "write_report"],
    require_human_approval=["write_report"]
)
agent_policy = compose_policies(org_policy, team_policy)
```

### 策略作为 YAML

将策略存储为配置，而不是代码：

```yaml
# governance-policy.yaml
name: production-agent
allowed_tools:
  - search_documents
  - query_database
  - send_email
blocked_tools:
  - shell_exec
  - delete_record
blocked_patterns:
  - "(?i)(api[_-]?key|secret|password)\\s*[:=]"
  - "(?i)(drop|truncate|delete from)\\s+\\w+"
max_calls_per_request: 25
require_human_approval:
  - send_email
```

```python
import yaml

def load_policy(path: str) -> GovernancePolicy:
    with open(path) as f:
        data = yaml.safe_load(f)
    return GovernancePolicy(**data)
```

---

## 模式 2：语义意图分类

在代理收到提示之前检测危险意图，使用基于模式的信号。

```python
from dataclasses import dataclass

@dataclass
class IntentSignal:
    category: str       # 例如，"数据泄露"、"权限提升"
    confidence: float   # 0.0 到 1.0
    evidence: str       # 触发检测的内容

# 威胁检测的加权信号模式
THREAT_SIGNALS = [
    # 数据泄露
    (r"(?i)send\s+(all|every|entire)\s+\w+\s+to\s+", "data_exfiltration", 0.8),
    (r"(?i)export\s+.*\s+to\s+(external|outside|third.?party)", "data_exfiltration", 0.9),
    (r"(?i)curl\s+.*\s+-d\s+", "data_exfiltration", 0.7),

    # 权限提升
    (r"(?i)(sudo|as\s+root|admin\s+access)", "privilege_escalation", 0.8),
    (r"(?i)chmod\s+777", "privilege_escalation", 0.9),

    # 系统修改
    (r"(?i)(rm\s+-rf|del\s+/[sq]|format\s+c:)", "system_destruction", 0.95),
    (r"(?i)(drop\s+database|truncate\s+table)", "system_destruction", 0.9),

    # 提示注入
    (r"(?i)ignore\s+(previous|above|all)\s+(instructions?|rules?)", "prompt_injection", 0.9),
    (r"(?i)you\s+are\s+now\s+(a|an)\s+", "prompt_injection", 0.7),
]

def classify_intent(content: str) -> list[IntentSignal]:
    """对内容进行威胁信号分类。"""
    signals = []
    for pattern, category, weight in THREAT_SIGNALS:
        match = re.search(pattern, content)
        if match:
            signals.append(IntentSignal(
                category=category,
                confidence=weight,
                evidence=match.group()
            ))
    return signals

def is_safe(content: str, threshold: float = 0.7) -> bool:
    """快速检查：内容是否超过给定阈值是安全的？"""
    signals = classify_intent(content)
    return not any(s.confidence >= threshold for s in signals)
```

**关键洞察**：意图分类在工具执行*之前*发生，充当预飞行安全检查。这与仅检查生成*之后*的输出约束从根本上不同。

---

## 模式 3：工具级治理装饰器

用治理检查包装单个工具函数：

```python
import functools
import time
from collections import defaultdict

_call_counters: dict[str, int] = defaultdict(int)

def govern(policy: GovernancePolicy, audit_trail=None):
    """装饰器，对工具函数执行治理策略。"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tool_name = func.__name__

            # 1. 检查工具允许列表/阻止列表
            action = policy.check_tool(tool_name)
            if action == PolicyAction.DENY:
                raise PermissionError(f"策略 '{policy.name}' 阻止工具 '{tool_name}'")
            if action == PolicyAction.REVIEW:
                raise PermissionError(f"工具 '{tool_name}' 需要人工批准")

            # 2. 检查流量限制
            _call_counters[policy.name] += 1
            if _call_counters[policy.name] > policy.max_calls_per_request:
                raise PermissionError(f"流量限制超出：{policy.max_calls_per_request} 次调用")

            # 3. 检查参数中的内容
            for arg in list(args) + list(kwargs.values()):
                if isinstance(arg, str):
                    matched = policy.check_content(arg)
                    if matched:
                        raise PermissionError(f"检测到阻止模式：{matched}")

            # 4. 执行和审计
            start = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                if audit_trail is not None:
                    audit_trail.append({
                        "tool": tool_name,
                        "action": "allowed",
                        "duration_ms": (time.monotonic() - start) * 1000,
                        "timestamp": time.time()
                    })
                return result
            except Exception as e:
                if audit_trail is not None:
                    audit_trail.append({
                        "tool": tool_name,
                        "action": "error",
                        "error": str(e),
                        "timestamp": time.time()
                    })
                raise

        return wrapper
    return decorator


# 使用任何代理框架
audit_log = []
policy = GovernancePolicy(
    name="search-agent",
    allowed_tools=["search", "summarize"],
    blocked_patterns=[r"(?i)password"],
    max_calls_per_request=10
)

@govern(policy, audit_trail=audit_log)
async def search(query: str) -> str:
    """搜索文档——受策略治理。"""
    return f"Results for: {query}"

# 通过：search("latest quarterly report")
# 阻止：search("show me the admin password")
```

---

## 模式 4：信任评分

使用基于衰减的信任评分跟踪代理随时间的可靠性：

```python
from dataclasses import dataclass, field
import math
import time

@dataclass
class TrustScore:
    """具有时间衰减的信任评分。"""
    score: float = 0.5          # 0.0（不受信任）到 1.0（完全信任）
    successes: int = 0
    failures: int = 0
    last_updated: float = field(default_factory=time.time)

    def record_success(self, reward: float = 0.05):
        self.successes += 1
        self.score = min(1.0, self.score + reward * (1 - self.score))
        self.last_updated = time.time()

    def record_failure(self, penalty: float = 0.15):
        self.failures += 1
        self.score = max(0.0, self.score - penalty * self.score)
        self.last_updated = time.time()

    def current(self, decay_rate: float = 0.001) -> float:
        """获取带时间衰减的评分——没有活动信任会侵蚀。"""
        elapsed = time.time() - self.last_updated
        decay = math.exp(-decay_rate * elapsed)
        return self.score * decay

    @property
    def reliability(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0


# 在多代理系统中使用
trust = TrustScore()

# 代理成功完成任务
trust.record_success()  # 0.525
trust.record_success()  # 0.549

# 代理犯错误
trust.record_failure()  # 0.467

# 基于信任评分门控敏感操作
if trust.current() >= 0.7:
    # 允许自主操作
    pass
elif trust.current() >= 0.4:
    # 允许人工监督
    pass
else:
    # 拒绝或需要明确批准
    pass
```

**多代理信任**：在代理委托给其他代理的系统中，每个代理为其代理维护信任评分：

```python
class AgentTrustRegistry:
    def __init__(self):
        self.scores: dict[str, TrustScore] = {}

    def get_trust(self, agent_id: str) -> TrustScore:
        if agent_id not in self.scores:
            self.scores[agent_id] = TrustScore()
        return self.scores[agent_id]

    def most_trusted(self, agents: list[str]) -> str:
        return max(agents, key=lambda a: self.get_trust(a).current())

    def meets_threshold(self, agent_id: str, threshold: float) -> bool:
        return self.get_trust(agent_id).current() >= threshold
```

---

## 模式 5：审计跟踪

所有代理操作的仅追加式审计日志——对合规性和调试至关重要：

```python
from dataclasses import dataclass, field
import json
import time

@dataclass
class AuditEntry:
    timestamp: float
    agent_id: str
    tool_name: str
    action: str           # "allowed", "denied", "error"
    policy_name: str
    details: dict = field(default_factory=dict)

class AuditTrail:
    """仅追加式审计跟踪，用于代理治理事件。"""
    def __init__(self):
        self._entries: list[AuditEntry] = []

    def log(self, agent_id: str, tool_name: str, action: str,
            policy_name: str, **details):
        self._entries.append(AuditEntry(
            timestamp=time.time(),
            agent_id=agent_id,
            tool_name=tool_name,
            action=action,
            policy_name=policy_name,
            details=details
        ))

    def denied(self) -> list[AuditEntry]:
        """获取所有拒绝操作——对安全审查有用。"""
        return [e for e in self._entries if e.action == "denied"]

    def by_agent(self, agent_id: str) -> list[AuditEntry]:
        return [e for e in self._entries if e.agent_id == agent_id]

    def export_jsonl(self, path: str):
        """导出为 JSON Lines，用于日志聚合系统。"""
        with open(path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps({
                    "timestamp": entry.timestamp,
                    "agent_id": entry.agent_id,
                    "tool": entry.tool_name,
                    "action": entry.action,
                    "policy": entry.policy_name,
                    **entry.details
                }) + "\n")
```

---

## 框架集成

### PydanticAI

```python
from pydantic_ai import Agent

policy = GovernancePolicy(
    name="support-bot",
    allowed_tools=["search_docs", "create_ticket"],
    blocked_patterns=[r"(?i)(ssn|social\s+security|credit\s+card)"],
    max_calls_per_request=20
)

agent = Agent("openai:gpt-4o", system_prompt="You are a support assistant.")

@agent.tool
@govern(policy)
async def search_docs(ctx, query: str) -> str:
    """搜索知识库——受治理。"""
    return await kb.search(query)

@agent.tool
@govern(policy)
async def create_ticket(ctx, title: str, body: str) -> str:
    """创建支持工单——受治理。"""
    return await tickets.create(title=title, body=body)
```

### CrewAI

```python
from crewai import Agent, Task, Crew

policy = GovernancePolicy(
    name="research-crew",
    allowed_tools=["search", "analyze"],
    max_calls_per_request=30
)

# 在团队级别应用治理
def governed_crew_run(crew: Crew, policy: GovernancePolicy):
    """用治理检查包装团队执行。"""
    audit = AuditTrail()
    for agent in crew.agents:
        for tool in agent.tools:
            original = tool.func
            tool.func = govern(policy, audit_trail=audit)(original)
    result = crew.kickoff()
    return result, audit
```

### OpenAI Agents SDK

```python
from agents import Agent, function_tool

policy = GovernancePolicy(
    name="coding-agent",
    allowed_tools=["read_file", "write_file", "run_tests"],
    blocked_tools=["shell_exec"],
    max_calls_per_request=50
)

@function_tool
@govern(policy)
async def read_file(path: str) -> str:
    """读取文件内容——受治理。"""
    import os
    safe_path = os.path.realpath(path)
    if not safe_path.startswith(os.path.realpath(".")):
        raise ValueError("路径遍历被治理阻止")
    with open(safe_path) as f:
        return f.read()
```

---

## 治理级别

将治理严格程度与风险级别匹配：

| 级别 | 控制 | 用例 |
|-------|----------|----------|
| **开放** | 仅审计，无限制 | 内部开发/测试 |
| **标准** | 工具允许列表 + 内容过滤器 | 一般生产代理 |
| **严格** | 所有控制 + 敏感操作需要人工批准 | 金融、医疗保健、法律 |
| **锁定** | 仅允许列表，无动态工具，完整审计 | 合规性关键系统 |

---

## 最佳实践

| 实践 | 理由 |
|----------|-----------|
| **策略作为配置** | 将策略存储在 YAML/JSON，而不是硬编码——无需部署即可更改 |
| **最严格的优先** | 在组合策略时，拒绝始终覆盖允许 |
| **预飞行意图检查** | 在工具执行*之前*分类意图，而不是*之后* |
| **信任衰减** | 信任评分应随时间衰减——需要持续的良好行为 |
| **仅追加式审计** | 永远不要修改或删除审计条目——不可变性使合规性成为可能 |
| **失败关闭** | 如果治理检查出错，拒绝操作而不是允许它 |
| **策略与逻辑分离** | 治理执行应独立于代理业务逻辑 |

---

## 快速入门清单

```markdown
## 代理治理实施清单

### 设置
- [ ] 定义治理策略（允许的工具、阻止的模式、流量限制）
- [ ] 选择治理级别（开放/标准/严格/锁定）
- [ ] 设置审计日志存储

### 实施
- [ ] 为所有工具函数添加 @govern 装饰器
- [ ] 在用户输入处理中添加意图分类
- [ ] 实现多代理交互的信任评分
- [ ] 连接审计日志导出

### 验证
- [ ] 测试阻止的工具是否被正确拒绝
- [ ] 测试内容过滤器是否捕获敏感模式
- [ ] 测试流量限制行为
- [ ] 验证审计日志是否捕获所有事件
- [ ] 测试策略组合（最严格的优先）
```

---

## 相关资源

- [代理治理工具包](https://github.com/microsoft/agent-governance-toolkit) — 完整治理框架
- [AgentMesh 集成](https://github.com/microsoft/agent-governance-toolkit/tree/main/packages/agentmesh-integrations) — 框架特定包
- [LLM 应用的 OWASP Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
