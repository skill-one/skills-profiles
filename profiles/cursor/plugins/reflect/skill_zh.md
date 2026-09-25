# 反思

从当前对话中挖掘可持久的经验教训，然后将它们路由到技能编辑中。

## 调用时机

当用户说“reflect”或“/reflect”时调用。如果对话琐碎、离题或已被父代理正确执行的现有技能覆盖，则跳过。一次性事件不是经验教训。

## 流程

### 1. 定位活动对话记录

父代理在扩展之前找到自己的对话记录文件。系统提示会命名活动工作区的`agent-transcripts/`目录。使用该路径。不要在`~/.cursor/projects/*/`中通配符搜索。这会跨越工作区边界并读取与无关项目相关的私密聊天。

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

三种对话记录布局：遗留扁平布局（`<id>.jsonl`）、当前嵌套布局（`<id>/<id>.jsonl`）和子代理布局（`<parent>/subagents/<child>.jsonl`）。

对于每个候选记录，读取第一行JSONL并检查`message.content[0].text`是否包含对话的起始用户提示。获取匹配的路径。如果没有路径解析，则写入会话的紧凑摘要并传递该摘要。

### 2. 并行生成三个审查者

一条消息，三个`Task`调用，`subagent_type: generalPurpose`，`model`设置如下，代理模式（`readonly: false`）。审查者需要MCP访问权限以进行上下文查找（工单、聊天线程、对话记录中引用的可观察性跟踪）。只读模式会移除MCP。

每个审查者和合成器在`pstack-models.mdc`规则中命名一个角色行和一个默认值。将`model`设置为该行值，如果规则或该行缺失，则设置为默认值。如果`Task`工具拒绝一个slug，使用默认值并说明。如果它拒绝默认值，则使用其错误消息中同一系列的最近有效slug。

| 透镜 | 角色行 | 默认`model` | 提示模板 |
|---|---|---|---|
| 判断 | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-max` | `references/judgment-reviewer.md` |
| 工具 | `reflect tooling` | `gpt-5.6-sol-max` | `references/tooling-reviewer.md` |
| 分散 | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-max` | `references/divergent-reviewer.md` |

逐字传递每个模板，在标记处替换对话记录路径或摘要。审查者通过`Task`响应正文返回发现结果。

### 3. 合成

一个`Task`调用，`subagent_type: generalPurpose`，`model`来自`reflect judgment, divergent, synthesizer`行（默认`claude-opus-5-5-max`），代理模式（`readonly: false`）。合成器的质量检查包括抽查验证引用，这可能需要MCP访问权限。只读模式会移除MCP。逐字使用`references/synthesizer.md`，在标记处内嵌每个审查者的完整输出。合成器返回结构化的接受/拒绝/待办列表。

### 4. 结构强制检查

检查合成器的接受列表。对于任何可以通过lint规则、脚本、元数据标志或运行时检查更可靠地强制执行的项目，将其从接受移动到待办。参见**encode-lessons-in-structure**原则技能。

### 5. 应用

在应用任何接受编辑之前，向用户展示合成器的完整接受/拒绝/待办输出并等待明确批准。用户选择要应用哪个子集并可能重定向路由。技能更改会影响组织中的所有未来代理。不要自动应用。

待办项目自动归档到团队使用的任何devex/待办跟踪器中。只有接受列表等待批准。

对于每个批准的接受项目，精确遵循路由字段：

- 简单现有技能编辑（一个点状列表、一个紧缩的句子、一个过时的事实更正）：父代理直接执行。
- 重大现有技能编辑（一个新部分、一个新模式表、超过~10行）：交给Cursor内置的`create-skill`技能并运行其草稿/测试/迭代循环。
- `tune description: <技能路径>`（技能存在但未在应该触发时触发）：交给`create-skill`并运行其描述优化循环。
- `new skill via create-skill: <kebab-name>`：将创建交给`create-skill`。不要临时设计形状。

如果你的环境提供`SKILL.md`验证器，在声明完成之前在所有修改的技能上运行它。如果没有，则跳过此步骤。

### 6. 为用户总结

简短列表，无前缀：

- 应用编辑：`<技能路径>`。每行一个，说明更改内容。
- 创建新技能：`<技能路径>`。每行一个（罕见）。
- 待办归档到devex跟踪器：`<问题标题>`（`<标签>`）。每行一个。
- 被拒绝：每个拒绝发现+合成器中原因，每行一个。
