# 自我提升技能

## 安装

```bash
gh skill install pskoett/pskoett-skills 自我提升
```

仅用于CI执行时，使用：

```bash
gh skill install pskoett/pskoett-skills 自我提升-ci
```

使用Agent Skills CLI回退：

```bash
npx skills add pskoett/pskoett-skills/skills/自我提升
npx skills add pskoett/pskoett-skills/skills/自我提升-ci
```

将学习内容和错误记录到markdown文件中，以实现持续改进。编码代理可以在之后处理这些内容以进行修复，重要的学习内容会被提升到项目记忆中。

**与 [`自我修复`](../self-healing/SKILL.md) 配合：** 自我修复是主动的运行时恢复原语——当任务执行中途出现问题时，它会诊断、修复、验证并将 `HEAL-` 条目记录到 `.learnings/HEALS.md` 中。自我提升（此技能）是被动积累和提升层——它记录修正、知识空白和功能请求，并将反复的自我修复转交提升到永久记忆中。它们共享 `.learnings/` 但写入不同的文件；验证纪律存在于自我修复中，提升逻辑存在于这里。

## 快速参考

| 情况 | 操作 |
|------|------|
| 任务执行中途出现主动故障——代理需要立即修复 | **使用 `自我修复`**（文件验证 HEAL- 到 `.learnings/HEALS.md`） |
| 过去命令/操作失败（非主动修复） | 记录到 `.learnings/ERRORS.md` |
| 用户纠正你 | 使用类别 `correction` 记录到 `.learnings/LEARNINGS.md` |
| 用户希望缺少功能 | 记录到 `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | 使用集成详细信息记录到 `.learnings/ERRORS.md` |
| 自我修复转交块满足提升规则（见下文提升规则） | 将浓缩规则提升到 `CLAUDE.md` / `AGENTS.md` / 新技能 |
| 知识已过时 | 使用类别 `knowledge_gap` 记录到 `.learnings/LEARNINGS.md` |
| 发现更好的方法 | 使用类别 `best_practice` 记录到 `.learnings/LEARNINGS.md` |
| 简化/硬化反复模式 | 使用 `Source: simplify-and-harden` 和稳定的 `Pattern-Key` 记录/更新 `.learnings/LEARNINGS.md` |
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
进行的具体修复或改进

### 元数据
- 来源：对话 | 错误 | 用户反馈
- 相关文件：/path/to/file.ext
- 标签：tag1, tag2
- 参见：LRN-20250110-001（如果与现有条目相关）
- 模式键：simplify.dead_code | harden.input_validation（可选，用于反复模式跟踪）
- 反复计数：1（可选）
- 首次发现：2025-01-15（可选）
- 最后发现：2025-01-15（可选）

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
简短描述失败内容

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
- 参见：ERR-20250110-001（如果反复出现）

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
用户想要做什么

### 用户上下文
为什么需要它，解决了什么问题

### 复杂性估计
简单 | 中 | 复杂

### 建议实现
如何构建，可能扩展什么

### 元数据
- 频率：首次 | 反复
- 相关功能：现有功能名

---
```

## ID 生成

格式：`TYPE-YYYYMMDD-XXX`
- TYPE: `LRN`（学习）、`ERR`（错误）、`FEAT`（功能）
- YYYYMMDD：当前日期
- XXX：序列号或随机3个字符（例如，`001`、`A7B`）

示例：`LRN-20250115-001`、`ERR-20250115-A3F`、`FEAT-20250115-002`

## 解决条目

当问题修复时，更新条目：

1. 将 `**状态**: 待处理` 更改为 `**状态**: 已解决`
2. 在元数据后添加解决块：

```markdown
### 解决方案
- **解决时间**: 2025-01-16T09:00:00Z
- **提交/PR**: abc123 或 #42
- **备注**: 对所做工作的简短描述
```

其他状态值：
- `in_progress` - 正在积极处理
- `wont_fix` - 决定不处理（在解决方案备注中添加原因）
- `promoted` - 提升到 CLAUDE.md 或 .github/copilot-instructions.md
- `promoted_to_skill` - 提取为可重用技能（见自动技能提取）

## 提升到项目记忆

当学习内容广泛适用（不是一次性修复）时，将其提升到永久项目记忆中。

### 提升时机

- 学习内容适用于多个文件/功能
- 任何贡献者（人类或AI）都应该知道的知识
- 防止反复出现错误
- 记录项目特定约定

### 提升目标

| 目标 | 属于那里 |
|------|--------|
| `CLAUDE.md` | 项目事实、约定、所有与Claude交互的陷阱 |
| `AGENTS.md` | 代理特定工作流、工具使用模式、自动化规则 |
| `.github/copilot-instructions.md` | 项目上下文和约定，用于GitHub Copilot |

OpenClaw工作区目标（SOUL.md、TOOLS.md）在 `references/openclaw-integration.md` 中涵盖。

### 提升方法

1. **浓缩** 学习内容为简洁的规则或事实
2. **添加** 到目标文件中的适当部分（如果需要创建文件）
3. **更新** 原始条目：
   - 将 `**状态**: 待处理` 更改为 `**状态**: 已提升`
   - 添加 `**提升**: CLAUDE.md`、`AGENTS.md` 或 `.github/copilot-instructions.md`

### 提升示例

**学习**（详细）：
> 项目使用 pnpm 工作区。尝试 `npm install` 但失败。 
> 锁文件是 `pnpm-lock.yaml`。必须使用 `pnpm install`。

**在 CLAUDE.md**（简洁）：
```markdown
## 构建和依赖
- 包管理器：pnpm（不是 npm） - 使用 `pnpm install`
```

**学习**（详细）：
> 修改API端点时，必须重新生成TypeScript客户端。
> 忘记这一点会导致运行时类型不匹配。

**在 AGENTS.md**（可操作）：
```markdown
## API更改后
1. 重新生成客户端：`pnpm run generate:api`
2. 检查类型错误：`pnpm tsc --noEmit`
```

## 反复模式检测

如果记录的内容与现有条目相似：

1. **首先搜索**：`grep -r "keyword" .learnings/`
2. **链接条目**：在元数据中添加 `**See Also**: ERR-20250110-001`
3. **提升优先级** 如果问题反复出现
4. **考虑系统修复**：反复问题通常表明：
   - 缺少文档（→ 提升到 CLAUDE.md 或 .github/copilot-instructions.md）
   - 缺少自动化（→ 添加到 AGENTS.md）
   - 架构问题（→ 创建技术债务工单）

## 简化与硬化输入

使用此工作流程从 `simplify-and-harden` 技能中摄取反复模式，并将它们转换为持久的提示指导。

### 摄取工作流程

1. 从任务摘要中读取 `simplify_and_harden.learning_loop.candidates`。
2. 对于每个候选，使用 `pattern_key` 作为稳定的去重键。
3. 在 `.learnings/LEARNINGS.md` 中搜索具有该键的现有条目：
   - `grep -n "Pattern-Key: <pattern_key>" .learnings/LEARNINGS.md`
4. 如果找到：
   - 增加`Recurrence-Count`
   - 更新 `Last-Seen`
   - 添加 `See Also` 链接到相关条目/任务
5. 如果未找到：
   - 创建新的 `LRN-...` 条目
   - 设置 `Source: simplify-and-harden`
   - 设置 `Pattern-Key`、`Recurrence-Count: 1` 和 `First-Seen`/`Last-Seen`

### 提升规则（系统提示反馈）

当所有条件都为真时，将反复模式提升到代理上下文/系统提示文件中：

- `Recurrence-Count >= 3`
- 至少在2个不同任务中看到
- 在30天内发生

提升目标：
- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- OpenClaw工作区文件（适用时）——见 `references/openclaw-integration.md`

这三个条件规则是此技能的唯一提升阈值。自我修复转交块的快速参考行和聚合技能（`learning-aggregator`、`learning-aggregator-ci`）都使用相同的规则。

将提升的规则作为简短的预防规则编写（在编码前/中做什么），而不是长的事故记录。

## 定期审查

在自然断点处审查 `.learnings/`：

### 审查时机
- 开始新的大任务前
- 完成一个功能后
- 在有过去学习内容的领域工作
- 活动开发期间每周

### 快速状态检查
```bash
# 计算待处理项
grep -h "状态\*\*: 待处理" .learnings/*.md | wc -l

# 列出待处理的高优先级项
grep -B5 "优先级\*\*: 高" .learnings/*.md | grep "^## \["

# 查找特定领域的学习内容
grep -l "领域\*\*: 后端" .learnings/*.md
```

### 审查操作
- 修复已解决的条目
- 提升适用的学习内容
- 链接相关条目
- 提升反复问题

## 检测触发器

在注意到时自动记录：

**修正**（→ 带有 `correction` 类别的学习）：
- "不，那不对..."
- "实际上，应该是..."
- "你错了..."
- "那已经过时了..."

**功能请求**（→ 功能请求）：
- "你能也..."
- "我希望你能..."
- "有办法吗..."
- "为什么你不能..."

**知识空白**（→ 带有 `knowledge_gap` 类别的学习）：
- 用户提供了你不知道的信息
- 你参考的文档已过时
- API行为与你的理解不同

**错误**（→ 错误条目）：
- 命令返回非零退出代码
- 异常或堆栈跟踪
- 预期之外的输出或行为
- 超时或连接失败

## 优先级指南

| 优先级 | 使用时机 |
|------|--------|
| `critical` | 阻塞核心功能、数据丢失风险、安全问题 |
| `high` | 显著影响，影响常见工作流，反复出现的问题 |
| `medium` | 中等影响，存在替代方案 |
| `low` | 轻微不便，边缘情况，锦上添花 |

## 领域标签

用于按代码库区域过滤学习内容：

| 领域 | 范围 |
|------|------|
| `frontend` | UI、组件、客户端代码 |
| `backend` | API、服务、服务器端代码 |
| `infra` | CI/CD、部署、Docker、云 |
| `tests` | 测试文件、测试工具、覆盖率 |
| `docs` | 文档、注释、READMEs |
| `config` | 配置文件、环境、设置 |

## 最佳实践

1. **立即记录** - 上下文在问题发生后最新鲜
2. **具体** - 未来代理需要快速理解
3. **包括重现步骤** - 特别是对于错误
4. **链接相关文件** - 使修复更容易
5. **提出具体修复** - 不仅仅是“调查”
6. **使用一致的类别** - 支持过滤
7. **积极提升** - 如果不确定，添加到 CLAUDE.md 或 .github/copilot-instructions.md
8. **定期审查** - 过时的学习内容会失去价值

## Gitignore选项

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

## Hook集成

通过代理hook启用自动提醒。这是**可选**的——你必须明确配置hook。相同的两个脚本在 Claude Code 和 Codex CLI（两者都在stdin上提供JSON并接受相同的 `additionalContext` 输出形状）上工作；Copilot hooks可以记录但不能注入上下文，所以 Copilot 使用指令文件通道。包括 Codex 和 Copilot 的完整每代理设置：`references/hooks-setup.md`。

### 快速设置（Claude Code）

在项目中创建 `.claude/settings.json`。命令路径必须指向技能实际安装的位置：`.claude/skills/self-improvement/` 对于 `gh skill install` / `npx skills add`，或 `skills/self-improvement/` 如果此仓库已作为项目依赖项。相对路径从项目根目录解析。

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

这将注入一个学习评估提醒，每次提示后（约50-100个token的开销）。

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

Hook接收事件有效负载作为stdin上的JSON。错误检测器解析 `tool_response` 从该JSON并返回其提醒作为 `additionalContext` JSON输出，这是PostToolUse输出到达模型所需的。

### 可用Hook脚本

| 脚本 | Hook类型 | 目的 |
|------|--------|------|
| `scripts/activator.sh` | UserPromptSubmit (Claude Code, Codex) | 提醒在任务后评估学习内容（纯stdout被添加到两个代理的此事件上下文中） |
| `scripts/error-detector.sh` | PostToolUse (Claude Code, Codex), postToolUse (Copilot, 仅记录) | 解析stdin JSON有效负载中的错误模式（跨三个代理的有效负载形状）；发出 `additionalContext` 提醒 |

见 `references/hooks-setup.md` 了解详细配置和故障排除。

## 自动技能提取

当学习内容足够有价值以成为可重用技能时，使用提供的助手提取它。

### 技能提取标准

当任何以下条件适用时，学习内容有资格进行技能提取：

| 标准 | 描述 |
|------|------|
| **反复** | 有 `See Also` 链接到2个或更多相似问题 |
| **已验证** | 状态是 `已解决` 且修复有效 |
| **非显而易见** | 需要实际调试/调查才能发现 |
| **广泛适用** | 不是项目特定的；适用于不同代码库 |
| **用户标记** | 用户说“保存此为技能”或类似 |

### 提取工作流程

1. **识别候选**：学习内容满足提取标准
2. **运行助手**（或手动创建）：
   ```bash
   ./skills/self-improvement/scripts/extract-skill.sh skill-name --dry-run
   ./skills/self-improvement/scripts/extract-skill.sh skill-name
   ```
3. **自定义 SKILL.md**：用学习内容填充模板
4. **更新学习**：将状态设置为 `promoted_to_skill`，添加 `Skill-Path`
5. **验证**：在全新会话中阅读技能，确保它是自包含的

### 手动提取

如果你更喜欢手动创建：

1. 创建 `skills/<skill-name>/SKILL.md`
2. 使用 `assets/SKILL-TEMPLATE.md` 中的模板
3. 参考 [Agent Skills spec](https://agentskills.io/specification)：
   - YAML 前置文本，包含 `name` 和 `description`
   - 名称必须与文件夹名称匹配
   - 技能文件夹内没有 README.md

### 提取检测触发器

注意以下信号，表明学习内容应成为技能：

**在对话中：**
- "保存此为技能"
- "我反复遇到这个"
- "这对其他项目很有用"
- "记住这个模式"

**在学习条目中：**
- 多个 `See Also` 链接（反复问题）
- 高优先级 + 已解决状态
- 类别：`best_practice`，具有广泛适用性
- 用户反馈赞扬解决方案

### 技能质量门

提取前验证：

- [ ] 解决方案经过测试且有效
- [ ] 描述清晰，无需原始上下文
- [ ] 代码示例是自包含的
- [ ] 没有项目特定的硬编码值
- [ ] 遵循技能命名约定（小写，连字符）

## 多代理支持

此技能在不同AI编码代理中工作，具有代理特定激活。

### Claude Code

**激活**：Hooks (UserPromptSubmit, PostToolUse)
**设置**：`.claude/settings.json` 带有hook配置
**检测**：通过hook脚本自动检测

### Codex CLI

**激活**：Hooks (`UserPromptSubmit`, `PostToolUse`) — 实验，在 `config.toml` 中 `codex_hooks = true`
**设置**：`<repo>/.codex/hooks.json` 或 `~/.codex/hooks.json`；与 Claude Code 相同脚本，相同有效负载/输出形状；见 `references/hooks-setup.md` 了解配置
**检测**：通过hook脚本自动检测；见 `references/hooks-setup.md` 了解配置
**回退**：如果hook不可用，将自我提升指导添加到 `AGENTS.md`

### GitHub Copilot

**激活**：指令文件（Copilot hooks 存在于 `.github/hooks/*.json`，但它们对提示/工具事件输出被忽略——它们可以记录，不能注入上下文）
**设置**：添加到 `.github/copilot-instructions.md`：

```markdown
## 自我提升

在解决非明显问题时，考虑记录到 `.learnings/`：
1. 使用自我提升技能的格式
2. 使用 See Also 链接相关条目
3. 提升高价值学习内容到技能

在聊天中询问： "我应该记录这个作为学习吗？"
```

**检测**：会话结束时手动审查

### OpenClaw（可选）

OpenClaw特定设置、提升目标、混合使用细节保留在
`references/openclaw-integration.md` 中，以便此主技能专注于编码代理的核心自我提升工作流程。

### 代理无关指导

无论代理如何，当你：

1. **发现非明显内容** - 解决方案不是立即的
2. **纠正自己** - 初始方法错误
3. **学习项目约定** - 发现未记录的模式
4. **遇到预期之外的错误** - 特别是如果诊断困难
5. **找到更好的方法** - 改进原始解决方案

### Copilot 聊天集成

对于 Copilot 用户，在相关时添加此内容到你的提示：

> 完成此任务后，评估是否应使用自我提升技能格式记录到 `.learnings/`。

或使用快速提示：
- "记录到学习内容"
- "从这个解决方案创建技能"
- "检查 .learnings/ 中的相关问题"
