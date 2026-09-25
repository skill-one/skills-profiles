# 报告复合工程插件 Bug

报告在使用 compound-engineering 插件时遇到的 Bug。此技能收集结构化信息并为维护者创建 GitHub 问题。

## 第 1 步：收集 Bug 信息

使用平台的阻塞问题工具询问用户以下问题：Claude Code 中的 `AskUserQuestion`（如果其模式未加载，请先使用 `ToolSearch` 调用 `select:AskUserQuestion`），Codex 中的 `request_user_input`，Gemini 中的 `ask_user`，Pi 中的 `ask_user`（需要 `pi-ask-user` 扩展）。仅在 harness 中不存在阻塞工具或调用出错时（例如 Codex 编辑模式）才回退到聊天中的编号选项——不是因为需要加载模式。永远不要无声地跳过问题：

**问题 1：Bug 类别**
- 您遇到的问题类型是什么？
- 选项：代理无法工作，命令无法工作，技能无法工作，MCP 服务器问题，安装问题，其他

**问题 2：具体组件**
- 哪个具体组件受到影响？
- 询问代理、命令、技能或 MCP 服务器的名称

**问题 3：发生了什么（实际行为）**
- 询问："使用此组件时发生了什么？"
- 获取实际行为的清晰描述

**问题 4：应该发生什么（预期行为）**
- 询问："您期望发生什么？"
- 获取预期行为的清晰描述

**问题 5：重现步骤**
- 询问："在 Bug 发生之前您采取了哪些步骤？"
- 获取重现步骤

**问题 6：错误消息**
- 询问："您看到任何错误消息吗？如果是，请分享它们。"
- 捕获任何错误输出

## 第 2 步：收集环境信息

自动收集环境详细信息。检测编码代理平台并收集可用信息：

**系统信息（所有平台）：**
```bash
uname -a
```

**插件版本：** 读取插件清单或已安装插件的元数据。常见位置：
- Claude Code：`~/.claude/plugins/installed_plugins.json`
- Codex：`.codex/plugins/` 或项目配置
- 其他平台：检查平台的插件注册表

**代理 CLI 版本：** 运行平台的版本命令：
- Claude Code：`claude --version`
- Codex：`codex --version`
- 其他平台：使用适当的 CLI 版本标志

如果其中任何一项失败，记为"未知"并继续——不要阻塞报告。

## 第 3 步：格式化 Bug 报告

创建结构良好的 Bug 报告，包含：

```markdown
## Bug 描述

**组件：** [类型] - [名称]
**摘要：** [从参数或收集的信息中获取的简要描述]

## 环境

- **插件版本：** [从插件清单/注册表]
- **代理平台：** [例如，Claude Code, Codex, Copilot, Pi, Kilo]
- **代理版本：** [从 CLI 版本命令]
- **操作系统：** [从 uname]

## 发生了什么

[实际行为描述]

## 预期行为

[预期行为描述]

## 重现步骤

1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

## 错误消息

[任何错误输出]

## 其他上下文

[任何其他相关信息]

---
*通过 `/ce-report-bug` 技能报告*
```

## 第 4 步：创建 GitHub 问题

使用 GitHub CLI 创建问题：

```bash
gh issue create \
  --repo EveryInc/compound-engineering-plugin \
  --title "[compound-engineering] Bug: [简要描述]" \
  --body "[格式化的 Bug 报告]" \
  --label "bug,compound-engineering"
```

**注意：** 如果标签不存在，则无标签创建：
```bash
gh issue create \
  --repo EveryInc/compound-engineering-plugin \
  --title "[compound-engineering] Bug: [简要描述]" \
  --body "[格式化的 Bug 报告]"
```

## 第 5 步：确认提交

创建问题后：
1. 向用户显示问题 URL
2. 感谢他们报告 Bug
3. 告知维护者（Kieran Klaassen）将收到通知

## 输出格式

```
Bug 报告提交成功！

问题：https://github.com/EveryInc/compound-engineering-plugin/issues/[NUMBER]
标题：[compound-engineering] Bug: [描述]

感谢您帮助改进复合工程插件！
维护者将尽快审查您的报告并回复。
```

## 错误处理

- 如果 `gh` CLI 未安装或未认证：提示用户先安装/认证
- 如果问题创建失败：显示格式化的报告以便用户手动创建问题
- 如果所需信息缺失：重新提示该特定字段

## 隐私声明

此技能不会收集：
- 个人信息
- API 密钥或凭证
- 项目中的私有代码
- 超出基本系统信息的文件路径

报告中仅包含关于 Bug 的技术信息。
