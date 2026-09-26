# 自主代理

自主代理是能够独立分解目标、规划行动、执行工具并自我纠正的AI系统，无需持续的人类指导。挑战不在于让它们具备能力，而在于让它们可靠。每一个额外的决策都会增加失败的概率。

这项技能涵盖代理循环（ReAct、计划-执行）、目标分解、反思模式和生产可靠性。关键洞察：复合错误率会摧毁自主代理。每步95%的成功率在第十步会降至60%。首先为可靠性构建，其次为自主性构建。

2025年课程：赢家是具有明确边界、特定领域的约束代理，而不是“自主一切”。将AI输出视为建议，而非真理。

## 详细指南

执行此技能前，请阅读[详细指南](references/detailed-guide.md)。它保留了完整流程和参考资料。将其安全、前提条件和验证要求视为强制性。对于专注工作，加载相关部分；对于端到端工作，完整阅读指南。

## 跟踪上下文使用
```python
class ContextManager:
    def __init__(self, max_tokens=100000):
        self.max_tokens = max_tokens
        self.messages = []

    def add(self, message):
        self.messages.append(message)
        self.maybe_compact()

    def maybe_compact(self):
        if self.token_count() > self.max_tokens * 0.8:
            self.compact()

    def compact(self):
        # 始终保留：系统提示
        system = self.messages[0]

        # 始终保留：最后N条消息
        recent = self.messages[-10:]

        # 总结：其他所有内容
        middle = self.messages[1:-10]
        if middle:
            summary = summarize_messages(middle)
            self.messages = [system, summary] + recent
```

## 使用时机
- 用户提及或暗示：自主代理
- 用户提及或暗示：autogpt
- 用户提及或暗示：babyagi
- 用户提及或暗示：自我提示
- 用户提及或暗示：目标分解
- 用户提及或暗示：react模式
- 用户提及或暗示：代理循环
- 用户提及或暗示：自我纠正代理
- 用户提及或暗示：反思代理
- 用户提及或暗示：langgraph
- 用户提及或暗示：agentic ai
- 用户提及或暗示：代理规划

## 示例

**用户请求：**

> 使用@autonomous-agents执行此任务：自主代理是能够独立分解目标、规划行动、执行工具并自我纠正的AI系统。
