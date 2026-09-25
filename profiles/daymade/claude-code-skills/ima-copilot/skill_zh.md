# IMA Copilot

单命令安装器、故障排除器和个性化层，用于官方腾讯IMA技能。

## 概述

官方腾讯IMA技能（ima-skill）提供了一个强大的OpenAPI用于笔记和知识库操作，但其安装流程是为特定专有代理设计的，且最近的版本中包含的子模块文件无法通过严格的SKILL.md加载器。IMA Copilot解决了这两个问题：

1. 通过 [vercel-labs/skills](https://github.com/vercel-labs/skills) 开放式安装器，使用单个命令将 ima-skill 安装到 Claude Code、Codex 和 OpenClaw。
2. 通过实时验证调用引导用户设置API密钥。
3. 检测已知上游问题，并在明确用户同意的情况下就地修复，而永远不会分支、供应商化或镜像任何上游包的任何部分。
4. 提供一个分叉搜索策略，该策略尊重用户配置的知识库优先级和提升，并了解每个知识库100个结果的截断限制。

## 架构原则（不可违反）

此技能是围绕 ima-skill 的一个**包装层**。包装合同是不可协商的：

- **永不供应商化上游文件。** 此技能目录不包含 ima-skill 自身内容的任何副本、分支或摘录。当 ima-skill 发布新版本时，用户会获得新版本，而不会受到此包装层的任何干扰。
- **修复发生在运行时，而不是发布时。** 如果上游错误需要修补，此技能携带的是如何修补的*说明*，而不是修补后的文件。运行修复是幂等的：在上游更新后重新运行会重新检测和修复任何恢复的问题。
- **在触摸上游文件之前始终询问。** 修改 `~/.claude/skills/ima-skill/**`、`~/.agents/skills/ima-skill/**` 或任何其他上游安装目录需要通过 AskUserQuestion 进行明确用户同意。不进行静默修补。
- **教导而非隐藏。** 当应用修复时，向用户展示确切的变化位置和备份位置。这就是用户学习维护自己的安装的方式。

## 此技能的功能

| 功能 | 入口 | 详情 |
|---|---|---|
| 1. 将上游 ima-skill 安装到3个代理 | `scripts/install_ima_skill.sh` | 见 `references/installation_flow.md` |
| 2. 配置API凭证（XDG风格） | 内联工作流下方 | 见 `references/api_key_setup.md` |
| 3. 诊断和修复已知上游问题 | `scripts/diagnose.sh` + 工作流下方 | 见 `references/known_issues.md` |
| 4. 带优先级提升的分叉搜索 | `scripts/search_fanout.py` | 见 `references/search_best_practices.md` |

## 路由

当此技能被触发时，分类用户的意图并跳转到相应的能力：

| 用户说类似… | 跳转到 |
|---|---|
| "装 ima"、"install ima-skill"、"把 ima 装一下"、"我想用 ima" | **能力1** |
| "配 ima 的 key"、"configure ima credentials"、"ima API key" | **能力2** |
| "ima 报错"、"SKILL.md warning"、"frontmatter 错误"、"ima 加载失败" | **能力3** |
| "搜 X"、"在 ima 里搜 X"、"跨知识库搜索"、"扇出搜 X" | **能力4** |
| "帮我从头跑一遍 ima" | 1 → 2 → 3 → 4 按顺序 |

如有疑问，从能力3（诊断）开始——它会显示哪些能力被阻塞以及按什么顺序。

## 能力1：安装上游 ima-skill

安装器从 `https://app-dl.ima.qq.com/skills/` 下载最新官方版本，在临时目录中暂存，然后交由 `npx skills add <local-path>` 分发到 Claude Code、Codex 和 OpenClaw。

运行方式：

```bash
bash scripts/install_ima_skill.sh
```

脚本自动检测用户机器上安装了哪三个目标代理。对于不存在的代理，它将静默跳过而不是在用户未选择的地方安装。对于存在的代理，它将全局安装（`-g`）在vercel skills的默认符号链接模式下：第一个检测到的代理目录成为规范副本，其余代理都符号链接到它。这意味着一次修复或升级将自动传播到每个代理——`diagnose.sh` 检测到这种共享并消除其报告，以免多次看到相同的问题。

对于版本覆盖、检测逻辑、故障排除以及安装器生成的完整文件按文件布局，请阅读 `references/installation_flow.md`。

## 能力2：配置API凭证

凭证存储在XDG风格中，与任何代理的技能目录解耦：

- `~/.config/ima/client_id`（模式 `600`）
- `~/.config/ima/api_key`（模式 `600`）
- `~/.config/ima/`（模式 `700`）

环境变量 `IMA_OPENAPI_CLIENTID` 和 `IMA_OPENAPI_APIKEY` 作为后备覆盖——包装器首先读取环境，然后读取配置文件。

与用户逐步进行设置：

1. 打开 `https://ima.qq.com/agent-interface` 并创建一个新的 Client ID 和 API Key。
2. 将两个值写入XDG配置路径（或导出环境变量）。
3. 对 `https://ima.qq.com/openapi/wiki/v1/search_knowledge_base` 进行一次单次活动调用，使用 `{"query": "", "cursor": "", "limit": 1}` 以确认凭证被接受——`code: 0, msg: success` 的响应表示已准备好。

完整脚本和确切的请求/响应模式位于 `references/api_key_setup.md`。

## 能力3：诊断和修复已知问题

这是此技能存在的原因。上游包中有实际错误会导致在某些代理上加载失败，而修复是众所周知的但需要用户同意才能应用。诊断/修复工作流是此技能的**核心合同**。

### 第1步——运行只读诊断

```bash
bash scripts/diagnose.sh
```

`diagnose.sh` **永远不会修改任何文件**。它打印一个结构化报告，每行一个检查：

```
✅ upstream ima-skill installed (claude-code)
✅ upstream ima-skill installed (codex)
❌ upstream ima-skill NOT installed (openclaw)
✅ API credentials valid (search_knowledge_base returned 12 KBs)
⚠️ ISSUE-001: notes/SKILL.md missing YAML frontmatter (claude-code)
⚠️ ISSUE-001: knowledge-base/SKILL.md missing YAML frontmatter (claude-code)
⚠️ ISSUE-001: notes/SKILL.md missing YAML frontmatter (codex)
⚠️ ISSUE-001: knowledge-base/SKILL.md missing YAML frontmatter (codex)
```

### 第2步——解析报告并询问用户

对于每个 `⚠️` 或 `❌` 行，在 `references/known_issues.md` 中查找问题。该文件是修复来源的真相：

- 问题的本质（症状、根本原因）
- 存在哪些修复策略（`A`、`B`、`skip`）
- 每个策略的确切shell命令
- 每个策略修改的文件
- 为什么上游维护者可能还没有修复它

### 第3步——在触摸上游文件之前请求明确同意

对于每个有多个修复策略的问题，使用 **AskUserQuestion**。直白地表达——用户可能不知道“YAML frontmatter”是什么意思。用用户术语描述错误对用户的影响（“loader静默跳过两个文件，所以笔记搜索和知识库搜索实际上不起作用”），然后描述每个策略的结果，而不是机制。

当存在多个策略时，永远不要提供一个“直接修复”选项。用户的选择可能基于技能无法观察的因素——例如，如果他们计划手动与上游比较，他们可能更喜欢策略B（最小差异）。

### 第4步——执行选择的策略

`references/known_issues.md` 中的每个修复命令都编写为：

- **幂等**——在修复已应用后重新运行不会造成危害，并打印清晰的“已修复”消息。
- **备份**——修复将原始文件复制到 `/tmp/ima-copilot-backups/<timestamp>/<relative-path>` 之前修改任何内容，然后告诉用户备份位置。
- **可逆**——用户可以使用在末尾显示的 `cp` 命令从备份中恢复。

### 第5步——重新运行诊断以确认

修复后，再次运行 `diagnose.sh` 并向用户展示差异。问题应该从 `⚠️` 变为 `✅`。如果它没有，停止并展示原始的before/after给用户，而不是静默重试——这里意外的失败通常意味着上游意外地更改了内容。

### 关于上游更新的重要说明

每个修复都是**暂时性的，因为ima-skill升级会替换所有内容**。这是设计的意图：技能不会与上游争夺持久状态。当用户通过能力1升级ima-skill时，诊断的第4步将再次标记已修复的问题，用户可以重新运行修复。这是一个特性，而不是一个错误——如果上游最终修复了问题，修复将变得不必要，`diagnose.sh` 将报告 ✅ 而没有任何提示。

## 能力4：个性化分叉搜索

IMA的OpenAPI有三个硬约束，任何认真的搜索工作流都必须考虑：

1. **没有跨知识库端点。** `search_knowledge` 要求每个调用使用单个 `knowledge_base_id`。跨KB搜索是客户端分叉，而不是API功能。
2. **结果中没有相关性分数。** `info_list` 项目只携带 `media_id`、`title`、`parent_folder_id` 和 `highlight_content`。任何插入顺序之外的排名都必须在客户端发生。
3. **静默100结果截断。** `search_knowledge` 最多返回每个KB的100个命中，响应中没有 `is_end` 或 `next_cursor` 字段。高频查询被静默限制。

`scripts/search_fanout.py` 实现了完整的工作around：

```bash
python3 scripts/search_fanout.py "<query>"
```

脚本读取 `~/.config/ima/copilot.json` 进行个性化（优先级KB、跳过列表、策略），调用 `search_knowledge_base` 列出KBs，并行分叉 `search_knowledge` 调用，通过确切的100长度匹配检测截断，并将结果按KB分组显示，优先级组在顶部。

个性化文件是**每个用户的**和私有的。此技能只附带一个模板——见 `config-template/copilot.json.example`。没有配置文件的用戶将获得中性默认值：分叉所有可访问的KBs，按命中数排序组，不提升。

完整算法、截断处理策略、渲染格式，以及一个基于证据的决策（允许“子集KB跳过”，例如，一个严格是主KB子集的精选KB可以安全地跳过以减少重复命中）的逐步说明，请阅读 `references/search_best_practices.md`。

## 此技能拒绝做的事情

- **永不供应商化上游内容。** 此目录不包含且永远不会包含 `ima-skill/SKILL.md`、`ima-skill/notes/**`、`ima-skill/knowledge-base/**` 或任何其他上游文件。任何将此类文件添加到此技能的人应被拒绝。
- **永不将上游版本固定在SKILL.md中。** 安装器脚本携带默认版本以供后备使用，但SKILL.md本身是版本无关的，以便在上游发布时无需技能升级即可生存。
- **永不静默修补上游文件。** 每个修改路径都需要明确的 AskUserQuestion 和用户主动选择。
- **永不硬编码用户的知识库名称。** `copilot.json` 中的 `priority_kbs` 和 `skip_kbs` 字段完全是用户配置的。`config-template/copilot.json.example` 中的示例值仅供参考。
- **永不跳过执行修复时的备份步骤**，无论差异多么微不足道。
