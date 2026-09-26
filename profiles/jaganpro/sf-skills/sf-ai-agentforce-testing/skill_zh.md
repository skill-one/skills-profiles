# sf-ai-agentforce-testing：Agentforce 测试执行与覆盖率分析

当用户需要**正式的 Agentforce 测试**时使用此技能：多轮对话验证、CLI 测试中心规范、主题/操作覆盖率分析、预览检查，或在发布后进行结构化的测试-修复循环。

## 此技能拥有任务的时机

当工作涉及以下内容时，使用 `sf-ai-agentforce-testing`：
- `sf agent test` 工作流
- 多轮 Agent 运行时 API 测试
- 主题路由、操作调用、上下文保留、护栏或升级验证
- 测试规范生成和覆盖率分析
- 发布后/激活后测试-修复循环

当用户处于以下情况时，将任务委派给其他技能：
- 构建或编辑代理本身 → [sf-ai-agentforce](../sf-ai-agentforce/SKILL.md) 或 [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)
- 运行 Apex 单元测试 → [sf-testing](../sf-testing/SKILL.md)
- 为操作创建种子数据 → [sf-data](../sf-data/SKILL.md)
- 分析会话遥测/STDM 跟踪 → [sf-ai-agentforce-observability](../sf-ai-agentforce-observability/SKILL.md)

---

## 核心操作规则

- 测试在部署/发布/激活**之后**进行。
- 当对话连续性重要时，使用**多轮 API 测试**作为主要路径。
- 使用**CLI 测试中心**作为次要路径，用于单语句和受组织支持的测试中心工作流。
- 交互式和程序化 CLI 预览使用标准的 `sf org login web` 认证；**ECA 仅适用于 Agent 运行时 API 测试**，不适用于实时预览。
- 当需要 Agent 脚本更改时，将代理的修复委托给 **[sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)**。
- 在 ECA 流中**不要**使用原始 `curl` 进行 OAuth 令牌验证；使用提供的凭证工具。

### 脚本路径规则
使用现有的脚本，位于：
- `~/.claude/skills/sf-ai-agentforce-testing/hooks/scripts/`

这些脚本已预先批准。不要重新创建它们。

---

<a id="phase-0-prerequisites--agent-discovery"></a>

## 首先收集的必要上下文

请求或推断：
- 代理 API 名称/开发者名称
- 目标组织别名
- 测试目标：冒烟测试、回归、覆盖率扩展或错误重现
- 代理是否已发布和激活
- 组织是否提供**Agent 测试中心**
- 是否有**ECA 凭证**用于 Agent 运行时 API 测试

预检：
1. 发现代理
2. 确认发布/激活状态
3. 验证依赖项（流程、Apex、数据）
4. 选择测试路径

---

## 双轨工作流

### 路径 A — 多轮 API 测试（主要）
当您需要以下内容时使用：
- 多轮对话测试
- 主题重新匹配验证
- 上下文保留检查
- 跨轮次的升级或操作链分析

要求：
- ECA / 认证设置
- 代理运行时访问

### 路径 B — CLI 测试中心（次要）
当您需要以下内容时使用：
- 组织本地的 `sf agent test` 工作流
- 测试规范 YAML 执行
- 快速单语句验证
- CLI 中心的 CI/CD 使用，其中测试中心可用

### 快速手动路径
对于无需完整正式测试的手动验证，首先使用预览工作流，然后根据需要升级到路径 A 或 B。

---

## 推荐工作流

### 1. 发现和验证
- 在目标组织中定位代理
- 确认其已发布和激活
- 确认所需的操作/流程/Apex 存在
- 确定路径 A 或 B 是否适合请求

### 2. 规划测试
至少覆盖：
- 主要主题
- 预期操作
- 护栏/离题处理
- 升级行为
- 语句变化

### 3. 执行正确的路径
#### 路径 A
- 使用提供的工具验证 ECA 凭证
- 获取生成场景所需的元数据
- 使用提供的 Python 脚本运行多轮场景
- 分析每轮次的失败和覆盖率

#### 路径 B
- 生成或细化平面 YAML 测试规范
- 运行 `sf agent test` 命令
- 检查结构化结果和详细操作输出

### 4. 分类失败
典型失败类别：
- 主题未匹配
- 错误的主题匹配
- 操作未调用
- 错误的操作选择
- 操作调用失败
- 上下文保留失败
- 护栏失败
- 升级失败

### 5. 运行修复循环
当失败暗示代理编写问题时：
- 将修复委托给 [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)
- 如有必要重新发布/重新激活
- 在完整回归之前重新运行聚焦测试

---

## 测试护栏

永远不要跳过以下内容：
- 在发布/激活后仅进行测试
- 包括有害/离题/拒绝场景
- 每个重要主题使用多个语句
- API 测试后清理会话
- 保持群组执行小而受控

避免这些反模式：
- 测试未发布的代理
- 将一个 happy-path 语句视为覆盖率
- 将 ECA 密钥存储在存储库文件中
- 使用易碎的 shell 扩展 `curl` 命令进行认证调试
- 同时更改测试和代理而不隔离原因

---

## 输出格式

完成任务后，按以下顺序报告：
1. **使用的测试路径**
2. **执行的内容**
3. **通过/失败摘要**
4. **覆盖率差距**
5. **根本原因主题**
6. **推荐的修复循环/下一步测试**

建议格式：

```text
代理： <名称>
路径： 多轮 API | CLI 测试中心 | 预览
执行： <规范/场景/轮次>
结果： <通过/部分/失败>
覆盖率： <主题、操作、护栏、上下文>
问题： <最高信号失败>
下一步： <修复、重新发布、重新运行或扩展覆盖率>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 修复 Agent Script 逻辑 | [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md) | 编写和确定性修复循环 |
| 创建测试数据 | [sf-data](../sf-data/SKILL.md) | 操作就绪数据设置 |
| 修复基于流程的操作 | [sf-flow](../sf-flow/SKILL.md) | 流程修复 |
| 修复基于 Apex 的操作 | [sf-apex](../sf-apex/SKILL.md) | Apex 修复 |
| 为 Agent 运行时 API 设置 ECA / OAuth | [sf-connected-apps](../sf-connected-apps/SKILL.md) | 认证和应用配置 |
| 分析会话遥测 | [sf-ai-agentforce-observability](../sf-ai-agentforce-observability/SKILL.md) | STDM / 跟踪分析 |

---

## 参考地图

### 从这里开始
- [references/interview-wizard.md](references/interview-wizard.md)
- [references/multi-turn-testing.md](references/multi-turn-testing.md)
- [references/cli-commands.md](references/cli-commands.md)
- [references/test-spec-reference.md](references/test-spec-reference.md)

### 执行 / 认证
- [references/execution-protocol.md](references/execution-protocol.md)
- [references/multi-turn-execution.md](references/multi-turn-execution.md)
- [references/eca-setup-guide.md](references/eca-setup-guide.md)
- [references/credential-convention.md](references/credential-convention.md)
- [references/connected-app-setup.md](references/connected-app-setup.md)

### 覆盖率 / 修复循环
- [references/coverage-analysis.md](references/coverage-analysis.md)
- [references/agentic-fix-loops.md](references/agentic-fix-loops.md)
- [references/results-scoring.md](references/results-scoring.md)
- [references/known-issues.md](references/known-issues.md)

### 高级 / 专用
- [references/agentscript-agents.md](references/agentscript-agents.md)
- [references/agentscript-testing-patterns.md](references/agentscript-testing-patterns.md)
- [references/cli-testing-details.md](references/cli-testing-details.md)
- [references/deep-conversation-history-patterns.md](references/deep-conversation-history-patterns.md)
- [references/swarm-execution.md](references/swarm-execution.md)
- [references/trace-analysis.md](references/trace-analysis.md)
- [references/agent-api-reference.md](references/agent-api-reference.md)

### 模板 / 资产
- [references/test-templates.md](references/test-templates.md)
- [references/test-plan-format.md](references/test-plan-format.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 生产就绪的测试信心 |
| 80–89 | 强覆盖，有轻微差距 |
| 70–79 | 可接受，但建议扩展覆盖率 |
| 60–69 | 部分验证 |
| < 60 | 信心不足；阻止发布 |
