# 自我提升技能

将学习成果和错误记录到 markdown 文件中，以实现持续改进。编码代理之后可以处理这些记录生成修正方案，重要的学习成果会被提升为项目记忆。

## 首次使用初始化

在记录任何内容之前，确保项目或工作区根目录中存在 `.learnings/` 目录和文件。如果任何文件缺失，创建它们：

```bash
mkdir -p .learnings
[ -f .learnings/LEARNINGS.md ] || printf "# Learnings\n\n在开发过程中捕获的修正、见解和知识空白。\n\n**类别**: 修正 | 见解 | 知识空白 | 最佳实践\n\n---\n" > .learnings/LEARNINGS.md
[ -f .learnings/ERRORS.md ] || printf "# Errors\n\n命令失败和集成错误。\n\n---\n" > .learnings/ERRORS.md
[ -f .learnings/FEATURE_REQUESTS.md ] || printf "# Feature Requests\n\n用户请求的功能。\n\n---\n" > .learnings/FEATURE_REQUESTS.md
```

不要覆盖现有文件。如果 `.learnings/` 已经初始化，这是一个空操作。

除非用户明确要求，否则不要记录秘密、令牌、私钥、环境变量或完整的源/配置文件。优先使用简短的摘要或经过脱敏的摘录，而不是原始的命令输出或完整的会话记录。

如果您需要自动提醒或设置协助，请使用 [钩子集成](#钩子集成) 中描述的自愿钩子工作流。

## 快速参考

| 情况 | 操作 |
|------|------|
| 命令/操作失败 | 记录到 `.learnings/ERRORS.md` |
| 用户纠正您 | 记录到 `.learnings/LEARNINGS.md` 并使用类别 `correction` |
| 用户需要缺失的功能 | 记录到 `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | 记录到 `.learnings/ERRORS.md` 并包含集成细节 |
| 知识已过时 | 记录到 `.learnings/LEARNINGS.md` 并使用类别 `knowledge_gap` |
| 发现更好的方法 | 记录到 `.learnings/LEARNINGS.md` 并使用类别 `best_practice` |
| 简化/硬化重复模式 | 记录/更新 `.learnings/LEARNINGS.md` 并设置 `Source: simplify-and-harden` 和稳定的 `Pattern-Key` |
| 与现有条目相似 | 使用 `**See Also**` 链接，考虑提升优先级 |
| 广泛适用的学习成果 | 提升至 `CLAUDE.md`、`AGENTS.md` 和/或 `.github/copilot-instructions.md` |
| 工作流改进 | 提升至 `AGENTS.md`（OpenClaw 工作区） |
| 工具陷阱 | 提升至 `TOOLS.md`（OpenClaw 工作区） |
| 行为模式 | 提升至 `SOUL.md`（OpenClaw 工作区） |

## OpenClaw 设置（推荐）

OpenClaw 是此技能的主要平台。它使用基于工作区的提示注入和自动技能加载。

### 安装

**通过 ClawdHub（推荐）**:
```bash
clawdhub install self-improving-agent
```

**手动**:
```bash
git clone https://github.com/peterskoett/self-improving-agent.git ~/.openclaw/skills/self-improving-agent
```

从原始仓库重新制作用于 OpenClaw：https://github.com/pskoett/pskoett-ai-skills - https://github.com/pskoett/pskoett-ai-skills/tree/main/skills/self-improvement

### 工作区结构

OpenClaw 将这些文件注入到每个会话中：

```
~/.openclaw/workspace/
├── AGENTS.md          # 多代理工作流、委托模式
├── SOUL.md            # 行为指南、个性、原则
├── TOOLS.md           # 工具功能、集成陷阱
├── MEMORY.md          # 长期记忆（仅主会话）
├── memory/            # 每日记忆文件
│   └── YYYY-MM-DD.md
└── .learnings/        # 此技能的日志文件
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

### 创建学习文件

```bash
mkdir -p ~/.openclaw/workspace/.learnings
```

然后创建日志文件（或从 `assets/` 复制）：
- `LEARNINGS.md` — 修正、知识空白、最佳实践
- `ERRORS.md` — 命令失败、异常
- `FEATURE_REQUESTS.md` — 用户请求的功能

### 提升目标

当学习成果具有广泛适用性时（不是一次性修复），将其提升到永久项目记忆中。

### 提升时机

- 学习成果适用于多个文件/功能
- 任何贡献者（人类或 AI）都应该知道的知识
- 防止重复错误
- 记录项目特定约定

### 提升目标

| 目标 | 属于那里 |
|------|--------|
| `CLAUDE.md` | 项目事实、约定、所有 Claude 交互的陷阱 |
| `AGENTS.md` | 代理特定工作流、工具使用模式、自动化规则 |
| `.github/copilot-instructions.md` | 项目上下文和约定（GitHub Copilot） |
| `SOUL.md` | 行为指南、沟通风格、原则（OpenClaw 工作区） |
| `TOOLS.md` | 工具功能、使用模式、集成陷阱（OpenClaw 工作区） |

### 提升方法

1. **提炼** 学习成果为简洁的规则或事实
2. **添加** 到目标文件中的适当部分（如果需要创建文件）
3. **更新** 原始条目：
   - 将 `**Status**: pending` → `**Status**: promoted`
   - 添加 `**Promoted**: CLAUDE.md`、`AGENTS.md` 或 `.github/copilot-instructions.md`

### 提升示例

**学习**（详细）:
> 项目使用 pnpm workspaces。尝试 `npm install` 但失败。锁文件是 `pnpm-lock.yaml`。必须使用 `pnpm install`。

**在 CLAUDE.md**（简洁）:
```markdown
## 构建和依赖
- 包管理器：pnpm（不是 npm） - 使用 `pnpm install`
```

**学习**（详细）:
> 修改 API 端点时，必须重新生成 TypeScript 客户端。
> 忘记这一点会导致运行时类型不匹配。

**在 AGENTS.md**（可操作）:
```markdown
## API 修改后
1. 重新生成客户端：`pnpm run generate:api`
2. 检查类型错误：`pnpm tsc --noEmit`
```

## 重复模式检测

如果记录的内容与现有条目相似：

1. **首先搜索**：`grep -r "keyword" .learnings/`
2. **链接条目**：在元数据中添加 `**See Also**: ERR-20250110-001`
3. **提升优先级** 如果问题持续发生
4. **考虑系统性修复**：重复问题通常表明：
   - 缺少文档（→ 提升至 CLAUDE.md 或 .github/copilot-instructions.md）
   - 缺少自动化（→ 添加到 AGENTS.md）
   - 架构问题（→ 创建技术债务工单）

## 简化与硬化输入

使用此工作流将 `simplify-and-harden` 技能中的重复模式摄取为持久的提示指导。

### 摄取工作流

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

当所有条件都满足时，将重复模式提升到代理上下文/系统提示文件中：

- `Recurrence-Count >= 3`
- 在至少 2 个不同任务中看到
- 在 30 天窗口期内发生

提升目标：
- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `SOUL.md` / `TOOLS.md` 用于 OpenClaw 工作区级别的指导（适用时）

将提升的规则写为简短的预防规则（编码前/中应做什么），而不是长的事故记录。

## 定期审查

在自然断点时审查 `.learnings/`：

### 审查时机

- 开始新的大任务前
- 完成一个功能后
- 在有过去学习成果的领域工作
- 活跃开发期间每周

### 快速状态检查
```bash
# 计算待处理项
grep -h "Status\*\*: pending" .learnings/*.md | wc -l

# 列出高优先级待处理项
grep -B5 "Priority\*\*: high" .learnings/*.md | grep "^## \["

# 查找特定领域的学习成果
grep -l "Area\*\*: backend" .learnings/*.md
```

### 审查操作

- 解决已固定的条目
- 提升适用的学习成果
- 链接相关条目
- 提升重复问题

## 检测触发器

在您注意到时自动记录：

**修正**（→ 使用 `correction` 类别的学习）:
- "不，那不对..."
- "实际上，应该是..."
- "你错了..."
- "那已经过时了..."

**功能请求**（→ 功能请求）:
- "你也能..."
- "我希望你能..."
- "有办法..."
- "为什么你不能..."

**知识空白**（→ 使用 `knowledge_gap` 类别的学习）:
- 用户提供了您不知道的信息
- 您参考的文档已过时
- API 行为与您的理解不同

**错误**（→ 错误条目）:
- 命令返回非零退出代码
- 异常或堆栈跟踪
- 预期之外的输出或行为
- 超时或连接失败

## 优先级指南

| 优先级 | 使用时机 |
|------|--------|
| `critical` | 阻塞核心功能、数据丢失风险、安全问题 |
| `high` | 显著影响、影响常见工作流、重复问题 |
| `medium` | 中等影响、存在替代方案 |
| `low` | 轻微不便、边缘情况、锦上添花 |

## 区域标签

用于按代码库区域筛选学习成果：

| 区域 | 范围 |
|------|------|
| `frontend` | UI、组件、客户端代码 |
| `backend` | API、服务、服务器端代码 |
| `infra` | CI/CD、部署、Docker、云 |
| `tests` | 测试文件、测试工具、覆盖率 |
| `docs` | 文档、注释、README |
| `config` | 配置文件、环境、设置 |

## 最佳实践

1. **立即记录** - 上下文在问题发生后最鲜活
2. **具体** - 未来代理需要快速理解
3. **包含重现步骤** - 尤其是对于错误
4. **链接相关文件** - 使修复更容易
5. **提出具体的修复方案** - 不仅仅是 "调查"
6. **使用一致的类别** - 启用筛选
7. **积极提升** - 如果不确定，添加到 CLAUDE.md 或 .github/copilot-instructions.md
8. **定期审查** - 过时的学习成果会失去价值

## Gitignore 选项

**保持学习成果本地**（每个开发者）:
```gitignore
.learnings/
```

此仓库使用该默认值，以避免意外提交敏感或嘈杂的本地日志。

**在仓库中跟踪学习成果**（团队）:
不要添加到 .gitignore - 学习成果成为共享知识。

**混合**（跟踪模板，忽略条目）:
```gitignore
.learnings/*.md
!.learnings/.gitkeep
```

## 钩子集成

通过代理钩子启用自动提醒。这是 **自愿选择** - 您必须明确配置钩子。

### 快速设置（Claude Code / Codex）

在您的项目中创建 `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/activator.sh"
      }]
    }]
  }
}
```

这将注入一个学习评估提醒，每次提示后（约 50-100 个 token 开销）。

### 高级设置（带错误检测）

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/activator.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/error-detector.sh"
      }]
    }]
  }
}
```

这是可选的。推荐的默认设置是仅 activator 的配置；仅当您对钩子脚本检查命令输出以查找错误模式感到舒适时，才启用 `PostToolUse`。

### 可用的钩子脚本

| 脚本 | 钩子类型 | 目的 |
|------|--------|------|
| `scripts/activator.sh` | UserPromptSubmit | 任务后提醒评估学习成果 |
| `scripts/error-detector.sh` | PostToolUse (Bash) | 命令错误时触发 |

有关详细配置和故障排除，请参阅 `references/hooks-setup.md`。

## 自动技能提取

当学习成果足够有价值以成为可重用技能时，使用提供的辅助工具提取它。

### 技能提取标准

当满足以下任一条件时，学习成果有资格进行技能提取：

| 标准 | 描述 |
|------|------|
| **重复** | 有 2 个或更多 `See Also` 链接到相似问题 |
| **验证** | 状态为 `resolved` 且修复方案有效 |
| **非显而易见** | 需要实际调试/调查才能发现 |
| **广泛适用** | 不是项目特定的；适用于多个代码库 |
| **用户标记** | 用户说 "保存此为技能" 或类似 |

### 提取工作流

1. **识别候选**：学习成果满足提取标准
2. **运行辅助工具**（或手动创建）:
   ```bash
   ./skills/self-improving-agent/scripts/extract-skill.sh skill-name --dry-run
   ./skills/self-improving-agent/scripts/extract-skill.sh skill-name
   ```
3. **自定义 SKILL.md**：用学习内容填写模板
4. **更新学习成果**：设置状态为 `promoted_to_skill`，添加 `Skill-Path`
5. **验证**：在全新会话中阅读技能，确保其自包含

### 手动提取

如果您更喜欢手动创建：

1. 创建 `skills/<skill-name>/SKILL.md`
2. 使用 `assets/SKILL-TEMPLATE.md` 中的模板
3. 参考 [Agent Skills 规范](https://agentskills.io/specification):
   - YAML 前置信息，包含 `name` 和 `description`
   - 名称必须与文件夹名称匹配
   - 技能文件夹内不能有 README.md

### 提取检测触发器

注意以下信号，表明学习成果应成为技能：

**在对话中**:
- "保存此为技能"
- "我不断遇到这个"
- "这对其他项目很有用"
- "记住这个模式"

**在学习条目中**:
- 多个 `See Also` 链接（重复问题）
- 高优先级 + 已解决状态
- 类别：`best_practice` 且具有广泛适用性
- 用户反馈赞扬解决方案

### 技能质量门槛

提取前验证：

- [ ] 解决方案经过测试且有效
- [ ] 描述清晰，无需原始上下文
- [ ] 代码示例是自包含的
- [ ] 没有项目特定的硬编码值
- [ ] 遵循技能命名约定（小写，连字符）

## 多代理支持

此技能支持不同 AI 编码代理，具有代理特定激活。

### Claude Code

**激活**：钩子（UserPromptSubmit, PostToolUse）
**设置**：`.claude/settings.json` 中的钩子配置
**检测**：通过钩子脚本自动检测

### Codex CLI

**激活**：钩子（与 Claude Code 相同模式）
**设置**：`.codex/settings.json` 中的钩子配置
**检测**：通过钩子脚本自动检测

### GitHub Copilot

**激活**：手动（无钩子支持）
**设置**：添加到 `.github/copilot-instructions.md`:

```markdown
## 自我提升

解决非明显问题时，考虑记录到 `.learnings/`：
1. 使用自我提升技能的格式
2. 使用 See Also 链接相关条目
3. 提升高价值学习成果为技能

在聊天中询问： "我应该记录这个作为学习吗？"
```

**检测**：会话结束时手动审查
