# 一切克劳德代码 (ECC) — 代理套件性能系统

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

一切克劳德代码 (ECC) 是一个用于AI代理套件的、生产就绪的性能优化系统。它提供专门的子代理、可重用的技能、自定义的斜杠命令、内存持久化钩子、安全扫描和语言特定的规则——所有这些都源于10个月以上的日常实际使用。适用于克劳德代码、光标、代码、OpenCode和Antigravity。

---

## 安装

### 选项1：插件市场（推荐）

```bash
# 在克劳德代码中运行：
/plugin 市场place 添加 affaan-m/everything-claude-code
/plugin 安装 everything-claude-code@everything-claude-code
```

### 选项2：手动克隆

```bash
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code

# 安装适用于您的语言堆栈的规则
./install.sh typescript
# 多种语言：
./install.sh typescript python golang swift
# 目标特定IDE：
./install.sh --target cursor typescript
```

### 安装规则（始终需要）

克劳德代码插件不能自动分发规则——通过 `./install.sh` 手动安装或从 `rules/` 复制到您项目的 `.claude/rules/` 目录。

---

## 目录结构

```
everything-claude-code/
├── .claude-plugin/         # 插件和市场空间清单
│   ├── plugin.json
│   └── marketplace.json
├── agents/                 # 专门的子代理（规划者、架构师等）
├── commands/               # 斜杠命令 (/plan, /security-scan, 等)
├── skills/                 # 可重用的技能模块
├── hooks/                  # 生命周期钩子（SessionStart, Stop, PostEdit, 等）
├── rules/
│   ├── common/             # 与语言无关的规则
│   ├── typescript/
│   ├── python/
│   ├── golang/
│   └── swift/
├── scripts/                # 设置和实用脚本
└── install.sh              # 交互式安装程序
```

---

## 主要命令

安装后，使用命名空间形式（插件安装）或简短形式（手动安装）：

```bash
# 规划和架构
/everything-claude-code:plan "添加OAuth2登录流程"
/everything-claude-code:architect "设计一个多租户SaaS系统"

# 以研究为先的开发
/everything-claude-code:research "Node.js中最佳速率限制方法"

# 安全
/everything-claude-code:security-scan
/everything-claude-code:harness-audit

# 代理循环和编排
/everything-claude-code:loop-start
/everything-claude-code:loop-status
/everything-claude-code:quality-gate
/everything-claude-code:model-route

# 多代理工作流
/everything-claude-code:multi-plan
/everything-claude-code:multi-execute
/everything-claude-code:multi-backend
/everything-claude-code:multi-frontend

# 会话和内存
/everything-claude-code:sessions
/everything-claude-code:instinct-import

# PM2编排
/everything-claude-code:pm2

# 包管理器设置
/everything-claude-code:setup-pm
```

> 在手动安装时，删除 `everything-claude-code:` 前缀：`/plan`, `/sessions`, 等。

---

## 钩子运行时控制

ECC钩子在代理生命周期事件时触发。无需编辑文件即可在运行时控制严格性：

```bash
# 设置钩子严格性配置
export ECC_HOOK_PROFILE=minimal    # 最侵入性
export ECC_HOOK_PROFILE=standard   # 默认
export ECC_HOOK_PROFILE=strict     # 最大执行

# 通过ID禁用特定钩子（逗号分隔）
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"
```

覆盖的钩子事件：`SessionStart`, `Stop`, `PostEdit`, `PreBash`, `PostBash`, 等。

---

## 包管理器检测

ECC自动检测您的包管理器，优先级链如下：

1. `CLAUDE_PACKAGE_MANAGER` 环境变量
2. `.claude/package-manager.json`（项目级）
3. `package.json` → `packageManager` 字段
4. 锁文件检测 (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb`)
5. `~/.claude/package-manager.json`（全局）
6. 备用首选管理器

```bash
# 通过环境设置
export CLAUDE_PACKAGE_MANAGER=pnpm

# 全局设置
node scripts/setup-package-manager.js --global pnpm

# 项目设置
node scripts/setup-package-manager.js --project bun

# 检测当前设置
node scripts/setup-package-manager.js --detect
```

---

## 技能系统

技能是代理加载的markdown模块，以获得领域专业知识。可以单独安装或批量安装。

### 使用技能

```bash
# 在提示中显式引用技能
"使用search-first技能在实现之前找到正确的缓存方法"

# 或通过斜杠命令触发
/everything-claude-code:research "API响应内容哈希策略的最佳方法"
```

### 常见内置技能

| 技能 | 目的 |
|---|---|
| `search-first` | 编码前进行研究——避免幻觉API |
| `cost-aware-llm-pipeline` | 跨模型调用优化token消耗 |
| `content-hash-cache-pattern` | 通过内容哈希进行缓存失效 |
| `skill-stocktake` | 审计哪些技能被加载和激活 |
| `frontend-slides` | 无依赖HTML演示构建器 |
| `configure-ecc` | 指导交互式ECC设置向导 |
| `swift-actor-persistence` | Swift并发+持久化模式 |
| `regex-vs-llm-structured-text` | 决定何时使用正则表达式vs LLM解析 |

### 编写自定义技能

创建 `skills/my-skill.md`：

```markdown
---
name: my-skill
description: 这个技能的作用
triggers:
  - "激活这个技能的短语"
---

# 我的技能

## 使用场景
...

## 模式
\`\`\`typescript
// 具体示例
\`\`\`

## 规则
- 规则一
- 规则二
```

---

## Instincts系统（持续学习）

Instincts是会话提取的模式，用于重复使用。它们带有置信分数，并随着时间的推移而演变。

### 导出Instinct

```bash
/everything-claude-code:instinct-import
```

### Instinct文件格式

```markdown
---
name: prefer-zod-for-validation
confidence: 0.92
extracted_from: session-2026-02-14
---

# 行动
在TypeScript项目中始终使用Zod进行运行时模式验证。

# 证据
会话期间捕获了3个TypeScript单独遗漏的运行时类型错误。

# 示例
\`\`\`typescript
import { z } from 'zod'

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  role: z.enum(['admin', 'user'])
})

type User = z.infer<typeof UserSchema>
\`\`\`
```

---

## 规则架构

规则按语言执行编码标准。仅安装您的堆栈需要的规则。

```bash
# TypeScript + Python
./install.sh typescript python

# 检查已安装内容
ls .claude/rules/
```

### 规则目录布局

```
rules/
├── common/         # 适用于所有语言
│   ├── research-first.md
│   ├── security-baseline.md
│   └── verification-loops.md
├── typescript/
│   ├── no-any.md
│   ├── zod-validation.md
│   └── strict-mode.md
├── python/
│   ├── type-hints.md
│   └── django-patterns.md
└── golang/
    └── error-wrapping.md
```

---

## 代理（子代理委托）

代理是编排者委托的专门角色：

```bash
# 在您的提示中显式引用代理
"将架构决策委托给架构师代理"
"使用规划者代理将此功能分解为任务"
```

可用的代理包括：`planner`, `architect`, `researcher`, `verifier`, `security-auditor`, 等。每个代理都位于 `agents/<name>.md` 中，并具有自己的系统提示、工具列表和约束。

---

## AgentShield安全扫描

直接从克劳德代码运行安全扫描：

```bash
/everything-claude-code:security-scan
```

这会调用AgentShield扫描器（1282个测试，102条规则）针对您的代码库，并显示：
- 硬编码的密钥
- 注入漏洞
- 不安全的依赖
- 代理提示注入模式

---

## 内存持久化钩子

ECC钩子自动保存和恢复会话上下文：

```javascript
// hooks/session-start.js — 在新会话加载先前的上下文
const fs = require('fs')
const path = require('path')

const memoryPath = path.join(process.env.HOME, '.claude', 'session-memory.json')

if (fs.existsSync(memoryPath)) {
  const memory = JSON.parse(fs.readFileSync(memoryPath, 'utf8'))
  console.log('恢复会话上下文:', memory.summary)
}
```

```javascript
// hooks/stop.js — 退出时保存会话摘要
const summary = {
  timestamp: new Date().toISOString(),
  summary: process.env.ECC_SESSION_SUMMARY || '',
  skills_used: (process.env.ECC_SKILLS Used || '').split(',')
}

fs.writeFileSync(memoryPath, JSON.stringify(summary, null, 2))
```

---

## 跨平台支持

| 平台 | 支持 |
|---|---|
| Claude Code | 完整（代理、命令、技能、钩子、规则） |
| Cursor | 完整（通过 `--target cursor` 安装器标志） |
| OpenCode | 完整（插件系统，20+ 钩子事件类型，3个原生工具） |
| Codex CLI | 完整（通过 `/codex-setup` 生成的 `codex.md`） |
| Codex App | 完整（基于 `AGENTS.md`） |
| Antigravity | 完整（通过 `--target antigravity` 安装器标志） |

---

## 常见模式

### 以研究为先的开发

```
"在实现支付webhook处理程序之前，使用search-first技能验证当前的Stripe webhook验证最佳实践。"
```

### Token优化

```bash
# 将简单任务路由到更便宜的模型
/everything-claude-code:model-route "为这个纯函数编写单元测试"

# 使用后台进程进行长时间分析
/everything-claude-code:harness-audit
```

### 使用Git Worktrees进行并行化

```bash
# 为并行代理任务创建隔离的工作树
git worktree add ../feature-auth -b feature/auth
git worktree add ../feature-payments -b feature/payments

# 每个克劳德代码会话在其自己的工作树中运行
# 完成后合并
```

### 验证循环

```bash
/everything-claude-code:loop-start    # 开始跟踪循环
# ... 代理执行工作 ...
/everything-claude-code:loop-status   # 检查进度
/everything-claude-code:quality-gate  # 在合并前执行通过标准
```

---

## 故障排除

**安装后未找到插件命令**
```bash
/plugin 列表 everything-claude-code@everything-claude-code
# 如果为空，重新运行：/plugin 安装 everything-claude-code@everything-claude-code
```

**规则未应用**
```bash
# 规则需要手动安装——插件系统不能分发它们
cd everything-claude-code && ./install.sh typescript
# 验证：
ls ~/.claude/rules/   # 或项目根目录中的 .claude/rules/
```

**钩子未触发**
```bash
# 检查配置设置
echo $ECC_HOOK_PROFILE
# 检查禁用列表
echo $ECC_DISABLED_HOOKS
# 重置为默认值
unset ECC_HOOK_PROFILE
unset ECC_DISABLED_HOOKS
```

**Instinct导入丢失内容**
确保您使用的是v1.4.1+。较早版本中 `parse_instinct_file()` 存在一个bug，会静默丢失 Action/Evidence/Examples部分。拉取最新版本并重新运行。

**使用错误的包管理器**
```bash
node scripts/setup-package-manager.js --detect
export CLAUDE_PACKAGE_MANAGER=pnpm   # 明确覆盖
```

---

## 资源

- 主页：https://ecc.tools
- GitHub：https://github.com/affaan-m/everything-claude-code
- GitHub应用（市场）：https://github.com/marketplace/ecc-tools
- npm（通用）：`ecc-universal`
- npm（安全）：`ecc-agentshield`
- 简短指南：https://x.com/affaanmustafa/status/2012378465664745795
- 长指南：https://x.com/affaanmustafa/status/2014040193557471352
