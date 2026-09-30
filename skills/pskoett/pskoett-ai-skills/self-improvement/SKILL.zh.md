---
name: self-improvement
description: 捕获学习成果、错误、更正和功能请求，以实现持续改进。使用场景包括：(1) 用户更正Claude（例如：“不，那不对…”、“实际上…”），(2) 用户请求不存在的能力，(3) Claude意识到其知识过时或错误，(4) 发现针对重复任务的更优方法，(5) 接收来自自我修复（在Recurrence-Count >= 3时重复验证修复）的Handoff块，以提炼到记忆文件或新技能中。对于需要代理在任务中途应用并验证修复的ACTIVE运行时失败，应使用`self-healing`（它会提交带有证明的HEAL-条目；自我改进则促进累积模式）。此外，在执行重大任务前应先回顾学习成果。对于仅限CI/无头学习捕获，使用self-improvement-ci。
---

# 自我提升技能

## 安装

```bash
gh skill install pskoett/pskoett-skills 自我提升
```

仅用于 CI 执行时，使用：

```bash
gh skill install pskoett/pskoett-skills 自我提升-ci
```

使用 Agent Skills CLI 备用：

```bash
npx skills add pskoett/pskoett-skills/skills/自我提升
npx skills add pskoett/pskoett-skills/skills/自我提升-ci
```

将学习内容和错误记录到 markdown 文件中，以实现持续改进。编码代理可以在之后处理这些内容以进行修复，重要的学习内容会被提升到项目记忆中。

**与 [`自我修复`](../自我修复/SKILL.md) 配合使用：** 自我修复是主动的运行时恢复原语——它诊断、修复、验证，并在任务中途出现问题时将 `HEAL-` 条目记录到 `.learnings/HEALS.md` 中。自我提升（此技能）是被动的积累和提升层——它记录更正、知识差距和功能请求，并将重复的修复传递提升到永久记忆中。它们共享 `.learnings/` 但写入不同的文件；验证纪律存在于自我修复中，提升逻辑存在于这里。

## 快速参考

| 情况 | 操作 |
|------|------|
| 任务中途出现主动故障——代理需要立即修复 | **使用 `自我修复`**（文件验证 HEAL- 到 `.learnings/HEALS.md`） |
| 过去命令/操作失败（非主动修复） | 记录到 `.learnings/ERRORS.md` |
| 用户纠正你 | 记录到 `.learnings/LEARNINGS.md`，类别为 `correction` |
| 用户希望缺少功能 | 记录到 `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | 记录到 `.learnings/ERRORS.md`，包含集成详细信息 |
| 自我修复传递块满足提升规则（见下文提升规则） | 将浓缩规则提升到 `CLAUDE.md` / `AGENTS.md` / 新技能 |
| 知识已过时 | 记录到 `.learnings/LEARNINGS.md`，类别为 `knowledge_gap` |
| 发现更好的方法 | 记录到 `.learnings/LEARNINGS.md`，类别为 `best_practice` |
| 简化/硬化重复模式 | 记录/更新 `.learnings/LEARNINGS.md`，`Source: simplify-and-harden` 和稳定的 `Pattern-Key` |
| 与现有条目相似 | 使用 `**See Also**` 链接，考虑提升优先级 |
| 广泛适用的学习 | 提升到 `CLAUDE.md`、`AGENTS.md` 和/或 `.github/copilot-instructions.md` |
| OpenClaw 工作区目标（SOUL.md、TOOLS.md） | 查看 `references/openclaw-integration.md` |

## 设置

如果项目根目录下不存在 `.learnings/` 目录，请创建：

```bash
mkdir -p .learnings
```

从 `assets/` 复制文件模板（`LEARNINGS.md`、`ERRORS.md`、`FEATURE_REQUESTS.md`）或创建带标题的文件。

## 记录格式

### 学习条目

追加到 `.learnings/LEARNINGS.md`：

```markdown
## [LRN-YYYYMMDD-XXX] 类别

**记录时间**: ISO-8601 时间戳
**优先级**: 低 | 中 | 高 | 危急
**状态**: 待处理
**领域**: 前端 | 后端 | 基础设施 | 测试 | 文档 | 配置

### 摘要
对所学内容的单行描述

### 详细信息
完整上下文：发生了什么，哪里不对，什么正确

### 建议操作
具体的修复或改进建议

### 元数据
- 来源：对话 | 错误 | 用户反馈
- 相关文件：/path/to/file.ext
- 标签：tag1, tag2
- 参见：LRN-20250110-001（如果与现有条目相关）
- Pattern-Key：simplify.dead_code | harden.input_validation（可选，用于重复模式跟踪）
- 重复次数：1（可选）
- 首次出现：2025-01-15（可选）
- 最后出现：2025-01-15（可选）

---
```

### 错误条目

追加到 `.learnings/ERRORS.md`：

```markdown
## [ERR-YYYYMMDD-XXX] 技能或命令名

**记录时间**: ISO-8601 时间戳
**优先级**: 高
**状态**: 待处理
**领域**: 前端 | 后端 | 基础设施 | 测试 | 文档 | 配置

### 摘要
失败内容的简要描述

### 错误
```
实际错误消息或输出
```

### 上下文
- 尝试的命令/操作
- 使用输入或参数
- 如果相关，环境详细信息

### 建议修复
如果可识别，可能解决此问题

### 元数据
- 可重复：是 | 否 | 未知
- 相关文件：/path/to/file.ext
- 参见：ERR-20250110-001（如果重复）

---
```

### 功能请求条目

追加到 `.learnings/FEATURE_REQUESTS.md`：

```markdown
## [FEAT-YYYYMMDD-XXX] 功能名

**记录时间**: ISO-8601 时间戳
**优先级**: 中
**状态**: 待处理
**领域**: 前端 | 后端 | 基础设施 | 测试 | 文档 | 配置

### 请求功能
用户想做什么

### 用户上下文
为什么需要它，解决了什么问题

### 复杂性估计
简单 | 中 | 复杂

### 建议实现
如何构建，可能扩展什么

### 元数据
- 频率：首次 | 重复
- 相关功能：现有功能名

---
```

## ID 生成

格式：`TYPE-YYYYMMDD-XXX`
- TYPE：`LRN`（学习）、`ERR`（错误）、`FEAT`（功能）
- YYYYMMDD：当前日期
- XXX：序列号或随机 3 个字符（例如，`001`、`A7B`）

示例：`LRN-20250115-001`、`ERR-20250115-A3F`、`FEAT-20250115-002`

## 解决条目

当问题被修复时，更新条目：

1. 将 `**状态**: 待处理` 更改为 `**状态**: 已解决`
2. 在元数据后添加解决块：

```markdown
### 解决方案
- **解决时间**: 2025-01-16T09:00:00Z
- **提交/PR**: abc123 或 #42
- **备注**: 对所做工作的简要描述
```

其他状态值：
- `in_progress` - 正在积极处理
- `wont_fix` - 决定不处理（在解决方案备注中添加原因）
- `promoted` - 提升到 CLAUDE.md、AGENTS.md 或 .github/copilot-instructions.md
- `promoted_to_skill` - 提取为可重用技能（见自动技能提取）

## 提升到项目记忆

当学习内容具有广泛适用性（不是一次性修复）时，将其提升到永久项目记忆中。

### 提升时机

- 学习内容适用于多个文件/功能
- 任何贡献者（人类或 AI）都应该知道的知识
- 防止重复错误
- 记录项目特定约定

### 提升目标

| 目标 | 属于那里 |
|------|----------|
| `CLAUDE.md` | 项目事实、约定、所有与 Claude 交互的陷阱 |
| `AGENTS.md` | 代理特定工作流、工具使用模式、自动化规则 |
| `.github/copilot-instructions.md` | 项目上下文和约定，用于 GitHub Copilot |

OpenClaw 工作区目标（`SOUL.md`、`TOOLS.md`）在 `references/openclaw-integration.md` 中涵盖。

### 提升方法

1. **浓缩** 学习内容为简洁的规则或事实
2. **添加** 到目标文件中的适当部分（如果需要创建文件）
3. **更新** 原始条目：
   - 将 `**状态**: 待处理` 更改为 `**状态**: 已提升`
   - 添加 `**提升**: CLAUDE.md`、`AGENTS.md` 或 `.github/copilot-instructions.md`

### 提升示例

**学习**（详细）：
> 项目使用 pnpm workspaces。尝试 `npm install` 但失败。
> 锁文件是 `pnpm-lock.yaml`。必须使用 `pnpm install`。

**在 CLAUDE.md**（简洁）：
```markdown
## 构建和依赖
- 包管理器：pnpm（不是 npm）- 使用 `pnpm install`
```

**学习**（详细）：
> 修改 API 端点时，必须重新生成 TypeScript 客户端。
> 忘记这一点会导致运行时类型不匹配。

**在 AGENTS.md**（可操作）：
```markdown
## API 修改后
1. 重新生成客户端：`pnpm run generate:api`
2. 检查类型错误：`pnpm tsc --noEmit`
```

## 重复模式检测

如果记录的内容与现有条目相似：

1. **首先搜索**：`grep -r "keyword" .learnings/`
2. **链接条目**：在元数据中添加 `**See Also**: ERR-20250110-001`
3. **提升优先级** 如果问题重复出现
4. **考虑系统修复**：重复问题通常表明：
   - 缺少文档（→ 提升到 CLAUDE.md 或 .github/copilot-instructions.md）
   - 缺少自动化（→ 添加到 AGENTS.md）
   - 架构问题（→ 创建技术债务工单）

## 简化与硬化输入

使用此工作流程从 `simplify-and-harden` 技能中摄取重复模式，并将它们转换为持久的提示指导。

### 摄取工作流程

1. 从任务摘要中读取 `simplify_and_harden.learning_loop.candidates`。
2. 对于每个候选者，使用 `pattern_key` 作为稳定的去重键。
3. 在 `.learnings/LEARNINGS.md` 中搜索具有该键的现有条目：
   - `grep -n "Pattern-Key: <pattern_key>" .learnings/LEARNINGS.md`
4. 如果找到：
   - 增加`重复次数`
   - 更新 `Last-Seen`
   - 添加 `See Also` 链接到相关条目/任务
5. 如果未找到：
   - 创建新的 `LRN-...` 条目
   - 设置 `Source: simplify-and-harden`
   - 设置 `Pattern-Key`、`重复次数: 1` 和 `首次出现`/`最后出现`

### 提升规则（系统提示反馈）

当所有条件都满足时，将重复模式提升到代理上下文/系统提示文件中：

- `重复次数 >= 3`
- 在至少 2 个不同任务中出现过
- 在 30 天窗口期内发生

提升目标：
- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- OpenClaw 工作区文件（适用时）——参见 `references/openclaw-integration.md`

此三条件规则是此技能的唯一提升阈值。自我修复传递块和聚合技能（`learning-aggregator`、`learning-aggregator-ci`）都使用此相同规则。

将提升的规则作为简短的预防规则（编码前/中做什么），而不是长的事故记录。

## 定期审查

在自然断点时审查 `.learnings/`：

### 审查时机
- 开始新的大任务前
- 完成一个功能后
- 在有过去学习内容的领域工作
- 活跃开发期间的每周

### 快速状态检查
```bash
# 计算待处理项
grep -h "状态\*\*: 待处理" .learnings/*.md | wc -l

# 列出高优先级待处理项
grep -B5 "优先级\*\*: 高" .learnings/*.md | grep "^## \["

# 查找特定领域的学习内容
grep -l "领域\*\*: 后端" .learnings/*.md
```

### 审查操作
- 修复已解决的条目
- 提升适用的学习内容
- 链接相关条目
- 提升重复问题

## 检测触发器

在注意到以下情况时自动记录：

**更正**（→ 带有 `correction` 类别的学习）：
- "不，那不对..."
- "实际上，应该是..."
- "你错了..."
- "那已经过时了..."

**功能请求**（→ 功能请求）：
- "你能也..."
- "我希望你能..."
- "有办法吗..."
- "为什么你不能..."

**知识差距**（→ 带有 `knowledge_gap` 类别的学习）：
- 用户提供了你不知道的信息
- 你参考的文档已过时
- API 行为与你的理解不同

**错误**（→ 错误条目）：
- 命令返回非零退出代码
- 异常或堆栈跟踪
- 预期之外的输出或行为
- 超时或连接失败

## 优先级指南

| 优先级 | 使用时机 |
|------|----------|
| `危急` | 阻塞核心功能、数据丢失风险、安全问题 |
| `高` | 显著影响，影响常见工作流、重复问题 |
| `中` | 中等影响，存在替代方案 |
| `低` | 轻微不便、边缘情况、锦上添花 |

## 领域标签

用于按代码库区域过滤学习内容：

| 领域 | 范围 |
|------|------|
| `前端` | UI、组件、客户端代码 |
| `后端` | API、服务、服务器端代码 |
| `基础设施` | CI/CD、部署、Docker、云 |
| `测试` | 测试文件、测试工具、覆盖率 |
| `文档` | 文档、注释、READMEs |
| `配置` | 配置文件、环境、设置 |

## 最佳实践

1. **立即记录** - 上下文在问题发生后最新
2. **具体** - 未来代理需要快速理解
3. **包含重现步骤** - 特别是对于错误
4. **链接相关文件** - 使修复更容易
5. **提出具体修复** - 不仅仅是“调查”
6. **使用一致的类别** - 支持过滤
7. **积极提升** - 如果不确定，添加到 CLAUDE.md 或 .github/copilot-instructions.md
8. **定期审查** - 过时的学习会失去价值

## Gitignore 选项

**保持学习内容本地**（每个开发者）：
```gitignore
.learnings/
```

**在仓库中跟踪学习内容**（团队）：
不要添加到 .gitignore - 学习内容成为共享知识。

**混合**（跟踪模板，忽略条目）：
```gitignore
.learnings/*.md
!.learnings/.gitkeep
```

## Hook 集成

通过代理钩子启用自动提醒。这是**可选的** - 你必须明确配置钩子。相同的两个脚本在 Claude Code 和 Codex CLI 中工作（两者都在 stdin 上提供 JSON 并接受相同的 `additionalContext` 输出形状）；Copilot 钩子可以记录但不能注入上下文，因此 Copilot 使用指令文件通道。包括 Codex 和 Copilot 的每个代理设置：`references/hooks-setup.md`。

### 快速设置（Claude Code）

在项目中创建 `.claude/settings.json`。命令路径必须指向技能实际安装的位置：`.claude/skills/self-improvement/` 对于 `gh skill install` / `npx skills add`，或如果此存储库已作为依赖项包含在项目中，则为 `skills/self-improvement/`。相对路径从项目根目录解析。

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/self-improvement/scripts/activator.sh"
      }]
    }]
  }
}
```

这会在每次提示后注入学习评估提醒（约 50-100 个 token 开销）。

### 完整设置（带错误检测）

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/self-improvement/scripts/activator.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/self-improvement/scripts/error-detector.sh"
      }]
    }]
  }
}
```

钩子接收作为 stdin 上的 JSON 的事件有效负载。错误检测器解析该 JSON 中的 `tool_response` 并返回其提醒作为 `additionalContext` JSON 输出，这是 PostToolUse 输出到模型所必需的。

### 可用 Hook 脚本

| 脚本 | 钩子类型 | 目的 |
|------|----------|------|
| `scripts/activator.sh` | UserPromptSubmit (Claude Code, Codex) | 提醒在任务后评估学习内容（纯 stdout 被添加到两个代理的此事件上下文中） |
| `scripts/error-detector.sh` | PostToolUse (Claude Code, Codex), postToolUse (Copilot, 仅记录) | 解析 stdin JSON 有效负载中的错误模式，跨三个代理的有效负载形状；发出 `additionalContext` 提醒 |

参见 `references/hooks-setup.md` 获取详细配置和故障排除。

## 自动技能提取

当学习内容足够有价值以成为可重用技能时，使用提供的辅助工具进行提取。

### 技能提取标准

当满足以下任一条件时，学习内容有资格进行技能提取：

| 标准 | 描述 |
|------|------|
| **重复** | 有 `See Also` 链接到 2+ 类似问题 |
| **已验证** | 状态为 `已解决` 且有工作修复 |
| **非显而易见** | 需要实际调试/调查才能发现 |
| **广泛适用** | 不是项目特定的；跨代码库有用 |
| **用户标记** | 用户说“保存为技能”或类似内容 |

### 提取工作流程

1. **识别候选者**：学习内容满足提取标准
2. **运行辅助工具**（或手动创建）：
   ```bash
   ./skills/self-improvement/scripts/extract-skill.sh 技能名 --dry-run
   ./skills/self-improvement/scripts/extract-skill.sh 技能名
   ```
3. **自定义 SKILL.md**：用学习内容填充模板
4. **更新学习内容**：将状态设置为 `promoted_to_skill`，添加 `Skill-Path`
5. **验证**：在全新会话中阅读技能，确保它是自包含的

### 手动提取

如果你更喜欢手动创建：

1. 创建 `skills/<技能名>/SKILL.md`
2. 使用来自 `assets/SKILL-TEMPLATE.md` 的模板
3. 遵循 [Agent Skills 规范](https://agentskills.io/specification)：
   - 使用带有 `name` 和 `description` 的 YAML 前置信息
   - 名称必须与文件夹名称匹配
   - 技能文件夹内不能包含 README.md

### 提取检测触发条件

留意以下信号，表明学习内容应转化为技能：

**在对话中：**
- "保存为技能"
- "我经常遇到这个问题"
- "这对其他项目很有用"
- "记住这个模式"

**在学习条目中：**
- 多个 `See Also` 链接（重复出现的问题）
- 高优先级 + 已解决状态
- 类别：`best_practice` 且适用范围广
- 用户反馈称赞解决方案

### 技能质量门槛

提取前需验证：

- [ ] 解决方案已测试且可用
- [ ] 描述清晰且无需原始上下文
- [ ] 代码示例自包含
- [ ] 无项目特定的硬编码值
- [ ] 遵循技能命名规范（小写、连字符）

## 多代理支持

此技能适用于不同 AI 编码代理，并具有代理特定的激活方式。

### Claude 代码

**激活**：钩子（UserPromptSubmit, PostToolUse）
**设置**：`.claude/settings.json` 中的钩子配置
**检测**：通过钩子脚本自动检测

### Codex CLI

**激活**：钩子（`UserPromptSubmit`, `PostToolUse`）—— 实验性，需在 `config.toml` 中设置 `codex_hooks = true`
**设置**：`<repo>/.codex/hooks.json` 或 `~/.codex/hooks.json`；与 Claude 代码使用相同脚本、相同 payload/输出格式
**检测**：通过钩子脚本自动检测；配置详情见 `references/hooks-setup.md`
**备用方案**：若钩子不可用，将自我改进指导添加到 `AGENTS.md`

### GitHub Copilot

**激活**：指令文件（Copilot 钩子存在于 `.github/hooks/*.json`，但其输出被忽略，仅用于记录，不注入上下文）
**设置**：添加到 `.github/copilot-instructions.md`：

```markdown
## 自我改进

解决非明显问题时，考虑记录到 `.learnings/`：
1. 使用自我改进技能的格式
2. 通过 See Also 链接关联条目
3. 将高价值学习内容提升为技能

在聊天中询问："我应该将此记录为学习内容吗？"
```

**检测**：会话结束时手动审查

### OpenClaw（可选）

OpenClaw 特定的设置、提升目标及混合使用细节保留在
`references/openclaw-integration.md` 中，以便此主技能专注于编码代理的核心自我改进工作流。

### 代理无关指导

无论使用哪种代理，当出现以下情况时应用自我改进：

1. **发现非明显内容** - 解决方案并非显而易见
2. **自我修正** - 初始方法错误
3. **学习项目规范** - 发现未记录的模式
4. **遇到意外错误** - 尤其是诊断困难时
5. **找到更优方法** - 改进原始解决方案

### Copilot 聊天集成

对于 Copilot 用户，在相关情况下添加以下提示：

> 完成此任务后，评估是否应使用自我改进技能的格式记录到 `.learnings/`。

或使用快速提示：
- "记录到学习内容"
- "从此解决方案创建技能"
- "检查 .learnings/ 中的相关问题"
