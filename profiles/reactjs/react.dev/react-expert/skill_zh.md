# React 专家级研究技能

## 概述

此技能通过搜索权威来源（测试、源代码、PR、问题）来生成关于任何 React API 或概念的详尽文档研究，而不是依赖 LLM 训练知识。

<CRITICAL>
**怀疑主义准则：** 你必须对你的知识持怀疑态度。Claude 通常在过时或错误的 React 模式上进行训练。将源材料视为唯一权威。如果发现的结果与你的先前理解相矛盾，请明确标记这种差异。

**危险信号 - 如果你发现自己这样想，请立即停止：**
- "我知道这个 API 做X" → 首先查找源证据
- "常见模式是Y" → 在测试文件中验证
- 生成示例代码 → 必须有源文件引用
</CRITICAL>

## 调用

```
/react-expert useTransition
/react-expert suspense boundaries
/react-expert startTransition
```

## 来源（优先级顺序）

1. **React 仓库测试** - 最具权威性，用于实际行为
2. **React 源代码** - 警告、错误、实现细节
3. **Git 历史记录** - 带上下文的提交信息
4. **GitHub PRs & 评论** - 设计原理（通过 `gh` CLI）
5. **GitHub 问题** - 混乱/问题（react/react + reactjs/react.dev）
6. **React 工作组** - 新 API 的设计讨论
7. **Flow 类型** - 类型签名的唯一来源
8. **TypeScript 类型** - 注意与 Flow 的差异
9. **当前 react.dev 文档** - 基线（不被视为完整）

**禁止网络搜索** - 禁止使用 Stack Overflow、博客文章或网络搜索。允许通过 `gh` CLI 使用 GitHub API。

## 工作流程

### 第 1 步：设置 React 仓库

首先，确保本地可用 React 仓库：

```bash
# 检查 React 仓库是否存在，克隆或更新
if [ -d ".claude/react" ]; then
  cd .claude/react && git pull origin main
else
  git clone --depth=100 https://github.com/react/react.git .claude/react
fi
```

获取当前研究文档的提交哈希：
```bash
cd .claude/react && git rev-parse --short HEAD
```

### 第 2 步：分派 6 个并行研究代理

使用任务工具并行生成这些代理。每个代理都会收到怀疑主义前言：

> "你正在研究 React 的 `<TOPIC>`。CRITICAL：不要依赖你对这个 API 的先前知识。你的训练可能包含过时或错误的模式。只报告你在源文件中找到的内容。如果你的发现与常见理解相矛盾，请明确突出显示这种差异。"

| 代理 | subagent_type | 重点 | 指令 |
|-------|---------------|-------|--------------|
| test-explorer | 探索 | 测试文件中的使用模式 | 在 `.claude/react/packages/*/src/__tests__/` 中搜索提及主题的测试文件。提取实际使用示例，并附带文件路径和行号。 |
| source-explorer | 探索 | 源代码中的警告/错误 | 在 `.claude/react/packages/*/src/` 中搜索提及主题的 `console.error`、`console.warn` 和错误消息。记录触发条件。 |
| git-historian | 探索 | 提交信息 | 在 `.claude/react` 中运行 `git log --all --grep="<topic>" --oneline -50`。阅读完整提交信息以获取上下文。 |
| pr-researcher | 探索 | 引入/修改 API 的 PR | 运行 `gh pr list -R react/react --search "<topic>" --state all --limit 20`。阅读关键的 PR 描述和评论。 |
| issue-hunter | 探索 | 显示困惑的问题 | 在 `react/react` 和 `reactjs/react.dev` 仓库中搜索问题。寻找常见问题和误解。 |
| types-inspector | 探索 | Flow + TypeScript 签名 | 在 `.claude/react/packages/*/src/*.js` 中查找 Flow 类型（查找 `@flow` 注释）。在 `.claude/react/packages/*/index.d.ts` 中查找 TypeScript 类型。注意差异。 |

### 第 3 步：代理提示

在生成代理时使用这些确切提示：

#### test-explorer
```
你正在研究 React 的 <TOPIC>。

CRITICAL：不要依赖你对这个 API 的先前知识。只报告你在源文件中找到的内容。

你的任务：查找演示 <TOPIC> 使用的测试文件。

1. 搜索测试文件：使用 glob 搜索 `**/__tests__/**/*<topic>*` 和 `**/__tests__/**/*.js`，然后使用 grep 搜索 <topic>
2. 对于每个相关测试文件，提取：
   - 测试描述（describe/it 块）
   - 实际使用代码
   - 任何关于行为的断言
   - 正在测试的边缘情况
3. 使用精确的文件路径和行号报告结果

格式化你的输出为：
## 测试文件：<路径>
### 测试："<测试描述>"
```javascript
<来自测试的精确代码>
```
**行为：** <测试断言的内容>
```

#### source-explorer
```
你正在研究 React 的 <TOPIC>。

CRITICAL：不要依赖你对这个 API 的先前知识。只报告你在源文件中找到的内容。

你的任务：查找 <TOPIC> 的警告、错误和实现细节。

1. 搜索 .claude/react/packages/*/src/：
   - 提及 <topic> 的 console.error
   - 提及 <topic> 的 console.warn
   - 提及 <topic> 的错误消息
   - 主要实现文件
2. 对于每个警告/错误，记录：
   - 精确的消息文本
   - 触发它的条件
   - 源文件和行号

格式化你的输出为：
## 警告和错误
| 消息 | 触发条件 | 源 |
|---------|------------------|--------|
| "<精确消息>" | <条件> | <文件:行> |

## 实现说明
<来自源代码的关键细节>
```

#### git-historian
```
你正在研究 React 的 <TOPIC>。

CRITICAL：不要依赖你对这个 API 的先前知识。只报告你在 git 历史中找到的内容。

你的任务：查找解释 <TOPIC> 设计决策的提交信息。

1. 运行：cd .claude/react && git log --all --grep="<topic>" --oneline -50
2. 对于重要的提交，阅读完整信息：git show <hash> --stat
3. 寻找：
   - API 的初始引入
   - 错误修复（揭示边缘情况）
   - 行为变化
   - 废弃通知

格式化你的输出为：
## 关键提交
### <短哈希> - <主题>
**日期：** <日期>
**上下文：** <为什么做出这个更改>
**影响：** <行为发生了什么变化>
```

#### pr-researcher
```
你正在研究 React 的 <TOPIC>。

CRITICAL：不要依赖你对这个 API 的先前知识。只报告你在 PR 中找到的内容。

你的任务：查找引入或修改 <TOPIC> 的 PR。

1. 运行：gh pr list -R react/react --search "<topic>" --state all --limit 20 --json number,title,url
2. 对于有希望的 PR，阅读详细信息：gh pr view <number> -R react/react
3. 寻找：
   - 原始的 RFC/动机
   - 评论中的设计讨论
   - 考虑的替代方法
   - 打破变化

格式化你的输出为：
## 关键 PR
### PR #<number>: <标题>
**URL：** <url>
**摘要：** <它引入/更改了什么>
**设计原理：** <为什么采取这种方法>
**讨论亮点：** <评论中的关键点>
```

#### issue-hunter
```
你正在研究 React 的 <TOPIC>。

CRITICAL：不要依赖你对这个 API 的先前知识。只报告你在问题中找到的内容。

你的任务：查找揭示对 <TOPIC> 常见困惑的问题。

1. 搜索 react/react：gh issue list -R react/react --search "<topic>" --state all --limit 20 --json number,title,url
2. 搜索 reactjs/react.dev：gh issue list -R reactjs/react.dev --search "<topic>" --state all --limit 20 --json number,title,url
3. 对于每个问题，识别：
   - 用户困惑的内容
   - 解决方案是什么
   - 任何陷阱

格式化你的输出为：
## 常见困惑
### 问题 #<number>: <标题>
**仓库：** <react/react 或 reactjs/react.dev>
**困惑：** <他们误解了什么>
**解决方案：** <正确理解>
**陷阱：** <如果适用>
```

#### types-inspector
```
你正在研究 React 的 <TOPIC>。

CRITICAL：不要依赖你对这个 API 的先前知识。只报告你在类型定义中找到的内容。

你的任务：查找并比较 Flow 和 TypeScript 类型签名，用于 <TOPIC>。

1. Flow 类型（唯一来源）：搜索 .claude/react/packages/*/src/*.js 中的 @flow 注释，与 <topic> 相关
2. TypeScript 类型：搜索 .claude/react/packages/*/index.d.ts 和 @types/react
3. 比较并记录任何差异

格式化你的输出为：
## Flow 类型（唯一来源）
**文件：** <路径>
```flow
<精确的类型定义>
```

## TypeScript 类型
**文件：** <路径>
```typescript
<精确的类型定义>
```

## 差异
<Flow 和 TS 定义之间的任何差异>
```

### 第 4 步：综合结果

所有代理完成后，将他们的发现综合成一个研究文档。

**不要添加你自己的知识。** 只包括代理在来源中找到的内容。

### 第 5 步：保存输出

将最终文档写入 `.claude/research/<topic>.md`

将主题中的空格替换为连字符（例如，"suspense boundaries" → "suspense-boundaries.md"）

## 输出文档模板

```markdown
# React 研究：<topic>

> 由 /react-expert 于 YYYY-MM-DD 生成
> 来源：React 仓库（提交 <hash>），N 个 PR，M 个问题

## 摘要

[仅基于来源发现的简要摘要，不包括先前知识]

## API 签名

### Flow 类型（唯一来源）

[来自 types-inspector 代理]

### TypeScript 类型

[来自 types-inspector 代理]

### 差异

[Flow 和 TS 之间的任何差异]

## 使用示例

### 来自测试

[来自 test-explorer 代理 - 带有文件:行引用]

### 来自 PRs/Issues

[来自讨论的现实模式]

## 注意事项和陷阱

[每个都有来源链接]

- **<陷阱>** - 来源：<链接>

## 警告和错误

| 消息 | 触发条件 | 源文件 |
|---------|------------------|-------------|
[来自 source-explorer 代理]

## 常见困惑

[来自 issue-hunter 代理]

## 设计决策

[来自 git-historian 和 pr-researcher 代理]

## 来源链接

### 提交
- <hash>: <描述>

### 拉取请求
- PR #<number>: <标题> - <url>

### 问题
- 问题 #<number>: <标题> - <url>
```

## 常见错误

1. **信任先前知识** - 如果你“知道”关于 API 的内容，仍然查找来源证据
2. **生成示例代码** - 每个代码示例必须来自实际的源文件
3. **跳过代理** - 所有 6 个代理必须运行；每个代理提供独特的视角
4. **没有来源就总结** - 每个声明都需要文件:行或 PR/问题引用
5. **使用网络搜索** - 不使用 Stack Overflow、博客文章、社交媒体

## 验证清单

在最终确定研究文档之前：

- [ ] React 仓库位于 `.claude/react`，具有已知的提交哈希
- [ ] 所有 6 个代理都并行生成
- [ ] 每个代码示例都有源文件引用
- [ ] 警告/错误表格有源位置
- [ ] 没有声明没有来源证据
- [ ] Flow/TS 类型差异已记录
- [ ] 来源链接部分完整
