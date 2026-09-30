---
name: mempalace
description: MemPalace — 将您的项目和对话转化为可搜索的记忆宫殿。当用户询问MemPalace、记忆宫殿、挖掘记忆、搜索记忆、宫殿设置、翼、房间或抽屉时使用；或者当他们想要回忆过去可能已经存放在他们宫殿中的工作。
---

# MemPalace

一个可搜索的记忆宫殿，用于AI——管理项目与对话，然后进行语义搜索。原文存储，本地优先，默认不使用外部API。

## 前置条件

确保已安装 `mempalace`：

```bash
mempalace --version
```

如果未安装（推荐使用uv）：

```bash
uv tool install mempalace   # 或: pip install mempalace
```

## 动态、版本正确的指令

MemPalace 通过CLI暴露针对操作的特定指令，以便此技能随着MemPalace的演进保持准确。要获取任何操作的指令：

```bash
mempalace instructions <command>
```

当CLI输出与本文内容不一致时，始终优先考虑CLI输出——CLI是安装版本的事实来源。

## 常用操作

以下是用户最常请求的六个操作。每个操作封装了一个MemPalace CLI子命令。使用 `mempalace instructions <name>` 形式将返回完整的、版本正确的指导。

### `help` — 探索MemPalace的功能

```bash
mempalace instructions help
```

在用户是新用户、不确定可能的功能，或询问“你能做什么”时使用。

### `init` — 首次运行时的宫殿设置

```bash
mempalace instructions init
```

在用户刚刚安装MemPalace、尚未存在宫殿，或用户明确要求设置/配置/重新初始化其宫殿时使用。

### `mine` — 导入项目或对话目录

```bash
mempalace instructions mine
```

在用户希望将项目文件整合到其宫殿中，或将导出的对话转录文本导入宫殿作为可搜索的记忆时使用。

### `search` — 通过语义查询查找原文记忆

```bash
mempalace instructions search
```

在用户希望回忆过去的事情、查找之前的决策，或重新发现已经写过的代码/笔记/对话时使用。

### `status` — 当前宫殿中的内容

```bash
mempalace instructions status
```

在用户询问“我的宫殿里有什么”、“我的宫殿有多大”，或希望了解翼、房间和抽屉数量的摘要时使用。

### `audit` — 宫殿的整理程度，以及修复会话

```bash
mempalace instructions audit
```

在用户询问宫殿的整理程度或“混乱”程度、为什么范围搜索或唤醒会遗漏内容，或希望清理翼、房间、隧道、走廊或知识图谱时使用。在用户决定每个修复之前，此操作为只读。

## MCP工具（优先于CLI）

在Antigravity内部，MemPalace MCP服务器注册了一套丰富的工具。使用这些工具代替向CLI发出命令进行实时操作（搜索、日记写入、添加抽屉、知识图谱查询、宫殿状态）。MCP工具始终反映当前宫殿状态，而无需启动子进程。

MCP服务器在安装此插件时自动注册于 `~/.gemini/config/plugins/mempalace/`。如果服务器未出现在Antigravity的MCP商店中，运行 `mempalace-mcp --version` 验证二进制文件是否在PATH上，然后重启Antigravity。

## 设计原则（原文引用自项目）

- **始终原文** — 永不总结、释义或以有损方式压缩用户数据。
- **本地优先，默认不使用外部API** — 提取、嵌入和LLM辅助的精炼都在用户的机器上完成。
- **架构级隐私** — 系统从不调用外部服务进行核心操作。
- **性能预算** — 钩子小于500ms；启动注入小于100ms。
- **后台处理一切** — 文件归档、索引和时间戳通过后台钩子完成；聊天窗口中不花费任何token进行账本管理。

如果请求违反任何这些原则，请拒绝并解释——即使这在技术上很方便。

## 版本意识

版本检查是可选的。在启用每周检查前询问，使用
`mempalace update configure --enable --installer uv-tool`（或 `pipx` / `pip`，与安装方式匹配）；默认是禁用的。启用检查会联系PyPI，但不会发送宫殿内容、身份或遥测数据。当 `mempalace_status` 报告有可用版本时，区分 `updates.server` 与本地代理的 `updates.client`。仅使用本地更新计划进行客户端范围；远程服务器更新必须在中心主机上由其操作员计划并授权。未经明确用户授权，切勿安装更新。

## 宫殿健康：审计和修复会话

当用户询问宫殿的整理程度、记忆是否“混乱”、为什么范围搜索或唤醒会遗漏内容，或调用 `/mempalace:audit` 时，运行审计，然后提供修复会话：

```bash
mempalace instructions audit
```

遵循返回的指令。简而言之：运行 `mempalace audit --json`（只读，在MCP服务器运行时安全），展示五个层级评分和发现，然后逐步引导用户进行修复**一次一个结构化问题**，并首先提供推荐选项：合并拼写方式不同的翼和房间、折叠 stub 翼、删除通用token上的隧道和自我链接走廊、商定知识图谱谓词词汇表，以及决定如何处理下一次mine中的通用房间集中。删除操作优先于行动，原文内容始终。最后重新运行审计，并记录前后评分和做出的每个决策。
