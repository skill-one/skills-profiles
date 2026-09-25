# 🎭 代理机构代理 — AI 专家个性

> 技能由 [ara.so](https://ara.so) 提供 — 2026 每日技能集合。

这是一个精选的 50 多个专业 AI 代理个性的集合，适用于 Claude Code、Cursor、Aider、Windsurf、Copilot 等。每个代理都具有深厚的领域专业知识、独特的个性、定义的工作流程和可衡量的交付成果 — 涵盖工程、设计、营销、销售、付费媒体等。

---

## 安装

### 前置条件

```bash
git clone https://github.com/msitarzewski/agency-agents.git
cd agency-agents
```

### Claude Code（推荐）

```bash
# 将所有代理复制到 Claude 的代理目录
cp -r agency-agents/* ~/.claude/agents/

# 或者创建符号链接以自动更新
ln -s /path/to/agency-agents ~/.claude/agents/agency
```

然后在任何 Claude Code 会话中：
```
嘿 Claude，激活前端开发者模式并帮助我构建一个 React 组件
```

### 其他所有工具（交互式安装器）

```bash
# 第一步：为所有支持的工具生成集成文件
./scripts/convert.sh

# 第二步：自动检测已安装的工具并交互式安装
./scripts/install.sh

# 或者针对特定工具
./scripts/install.sh --tool cursor
./scripts/install.sh --tool copilot
./scripts/install.sh --tool aider
./scripts/install.sh --tool windsurf
```

### 每个工具手动安装

| 工具 | 安装路径 |
|------|-------------|
| Claude Code | `~/.claude/agents/` |
| Cursor | 项目根目录下的 `.cursor/rules/` |
| Copilot | `.github/copilot-instructions.md` |
| Aider | `.aider.conf.yml` 或通过 `--system-prompt` 传递 |
| Windsurf | 项目根目录下的 `.windsurf/rules/` |

---

## 代理名册

### 工程部门

```
engineering/engineering-frontend-developer.md       React/Vue/Angular, UI, 核心网络指标
engineering/engineering-backend-architect.md        API 设计, 数据库, 可扩展性
engineering/engineering-mobile-app-builder.md       iOS/Android, React Native, Flutter
engineering/engineering-ai-engineer.md              机器学习模型, AI 集成, 数据管道
engineering/engineering-devops-automator.md         CI/CD, 基础设施自动化, 云操作
engineering/engineering-rapid-prototyper.md         MVP, POC, 竞赛速度
engineering/engineering-senior-developer.md         Laravel/Livewire, 高级模式
engineering/engineering-security-engineer.md        威胁建模, 安全代码审查
engineering/engineering-code-reviewer.md            PR 审查, 代码质量门禁
engineering/engineering-database-optimizer.md       PostgreSQL/MySQL 调整, 慢查询
engineering/engineering-git-workflow-master.md      分支, 传统的提交
engineering/engineering-software-architect.md       系统设计, DDD, 权衡分析
engineering/engineering-sre.md                      SLO, 错误预算, 混沌工程
engineering/engineering-incident-response-commander.md  事件管理, 事后分析
engineering/engineering-technical-writer.md         开发者文档, API 参考
engineering/engineering-data-engineer.md            数据管道, 湖泊, ETL/ELT
```

### 设计部门

```
design/design-ui-designer.md                        视觉设计, 组件库
design/design-ux-researcher.md                      用户测试, 行为分析
design/design-ux-architect.md                       CSS 系统, 技术用户体验
design/design-brand-guardian.md                     品牌身份和一致性
design/design-whimsy-injector.md                    微交互, 乐趣, 复活节彩蛋
design/design-image-prompt-engineer.md              Midjourney/DALL-E/SD 提示
design/design-inclusive-visuals-specialist.md       表现, 偏见缓解
```

### 营销、销售和付费媒体

```
marketing/marketing-growth-hacker.md
marketing/marketing-content-creator.md
paid-media/paid-media-ppc-strategist.md
paid-media/paid-media-creative-strategist.md
sales/sales-outbound-strategist.md
sales/sales-deal-strategist.md
sales/sales-discovery-coach.md
```

---

## 在 Claude Code 中使用代理

### 激活单个代理

```
# 在 Claude Code 聊天中：
激活后端架构师代理并帮助我设计一个多租户 SaaS 应用的 REST API。
```

### 按顺序使用多个代理

```
# 首先，设计系统
激活软件架构师代理。设计电子商务平台的领域模型。

# 然后，实现
现在激活高级开发者代理并在 Laravel 中实现订单聚合。

# 然后，审查
激活代码审查者代理并审查上述实现。
```

### 直接引用代理文件

```bash
# 在 Claude CLI 中将代理作为系统提示传递
claude --system-prompt "$(cat ~/.claude/agents/engineering-frontend-developer.md)" \
  "使用 Tailwind CSS 在 React 中构建一个响应式产品卡片组件"
```

---

## 在 Cursor 中使用代理

运行 `./scripts/install.sh --tool cursor` 后，代理规则将位于 `.cursor/rules/`。在聊天中引用它们：

```
@engineering-frontend-developer 构建一个具有排序和分页的数据表格组件。
```

或者设置 `.cursor/rules/default.mdc` 中的默认规则：

```markdown
---
alwaysApply: true
---

你正在作为 The Agency 的高级开发者代理运行。
参考 .cursor/rules/engineering-senior-developer.md 获取你的完整个性和工作流程。
```

---

## 在 Aider 中使用代理

```bash
# 使用单个代理作为系统提示
aider --system-prompt "$(cat agency-agents/engineering/engineering-security-engineer.md)"

# 或者参考 .aider.conf.yml
echo "system-prompt: agency-agents/engineering/engineering-devops-automator.md" >> .aider.conf.yml
```

---

## 在 Windsurf 中使用代理

```bash
./scripts/install.sh --tool windsurf
# 代理被写入到 .windsurf/rules/
```

在聊天中激活：
```
使用 .windsurf/rules/ 中的 UX 架构师代理规则来审查我的 CSS 架构。
```

---

## 实际工作流示例

### 多代理全栈功能

```bash
# 第一步：架构阶段
cat > task.md << 'EOF'
我需要在我的 Node.js + React 应用中添加实时通知。
用户应该看到应用内警报，并可以选择接收电子邮件摘要。
EOF

# 调用软件架构师
claude --system-prompt "$(cat ~/.claude/agents/engineering-software-architect.md)" < task.md

# 第二步：后端实现
claude --system-prompt "$(cat ~/.claude/agents/engineering-backend-architect.md)" \
  "根据上述架构使用 PostgreSQL LISTEN/NOTIFY 和 Socket.io 实现通知服务"

# 第三步：前端实现
claude --system-prompt "$(cat ~/.claude/agents/engineering-frontend-developer.md)" \
  "构建一个连接到 Socket.io 源的 React 通知铃组件"

# 第四步：安全审查
claude --system-prompt "$(cat ~/.claude/agents/engineering-security-engineer.md)" \
  "审查通知系统实现中的安全问题"
```

### 代码审查工作流

```bash
# 生成一个 diff 并管道到代码审查者代理
git diff main..feature/payment-integration | \
  claude --system-prompt "$(cat ~/.claude/agents/engineering-code-reviewer.md)" \
  "审查这个 PR 差异。重点关注安全性、正确性和可维护性。"
```

### 数据库优化

```bash
# 粘贴慢查询日志并激活数据库优化器
claude --system-prompt "$(cat ~/.claude/agents/engineering-database-optimizer.md)" << 'EOF'
这是我们 PostgreSQL 日志中的一个慢查询（平均 4200ms）：

SELECT u.*, p.*, o.*
FROM users u
LEFT JOIN profiles p ON p.user_id = u.id
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '30 days'
ORDER BY o.created_at DESC;

表大小：users=2M 行, orders=18M 行。没有在 created_at 列上创建索引。
EOF
```

### 事件响应

```bash
# 结构化事件启动
claude --system-prompt "$(cat ~/.claude/agents/engineering-incident-response-commander.md)" << 'EOF'
SEV-1 事件：支付处理自 14:32 UTC 开始返回 503 错误。
错误率：94%。受影响：结账、订阅续订。
最近的部署：payment-service v2.4.1 在 14:15 UTC。
EOF
```

---

## 创建自定义代理

代理文件遵循一致的 markdown 结构：

```markdown
# 🎯 代理名称

## 身份
你是 [名称]，The Agency 的 [角色]...

## 核心使命
[这个代理优化的内容]

## 个性与沟通风格
- [特征 1]
- [特征 2]

## 工作流程

### [工作流程名称]
1. [步骤 1]
2. [步骤 2]

## 交付成果
- [具体输出 1]
- [具体输出 2]

## 成功指标
- [可衡量的结果]
```

将自定义代理保存到 `agency-agents/custom/` 并重新运行 `./scripts/convert.sh` 以生成工具集成。

---

## 贡献新代理

```bash
# 分叉并克隆
git clone https://github.com/YOUR_USERNAME/agency-agents.git

# 在适当的部门创建你的代理
cp engineering/engineering-senior-developer.md \
   engineering/engineering-YOUR-SPECIALTY.md

# 编辑文件，然后测试它
claude --system-prompt "$(cat engineering/engineering-YOUR-SPECIALTY.md)" \
  "给我一个样本交付成果以展示你的能力"

# 提交 PR
git checkout -b agent/your-specialty
git add engineering/engineering-YOUR-SPECIALTY.md
git commit -m "feat: 添加 Your Specialty 代理"
git push origin agent/your-specialty
```

---

## 故障排除

**Claude Code 中找不到代理**
```bash
ls ~/.claude/agents/
# 如果为空，重新运行：
cp -r /path/to/agency-agents/* ~/.claude/agents/
```

**`convert.sh` 因权限错误失败**
```bash
chmod +x scripts/convert.sh scripts/install.sh
./scripts/convert.sh
```

**Cursor 没有获取到代理规则**
```bash
# 规则必须在项目根目录下的 .cursor/rules/
ls .cursor/rules/
# 重新运行针对 cursor 的安装器
./scripts/install.sh --tool cursor
```

**代理个性没有激活**
- 明确：*"激活前端开发者代理"* 而不是仅仅引用主题
- 如果工具集成不工作，直接将代理文件内容粘贴到系统提示中
- 对于 Claude Code，确认代理目录：`claude config get agentsDir`

**使用多个代理时发生冲突**
- 每个对话会话激活一个代理
- 对于多代理工作流，使用单独的会话或 Claude Code 的子代理功能
- 明确按顺序激活代理：架构师 → 实现 → 审查

---

## 项目结构

```
agency-agents/
├── engineering/          # 23 个工程专家代理
├── design/               # 8 个设计专家代理
├── marketing/            # 营销和增长代理
├── sales/                # 8 个销售专家代理
├── paid-media/           # 7 个付费媒体专家代理
├── scripts/
│   ├── convert.sh        # 生成特定于工具的集成文件
│   └── install.sh        # 交互式安装器（自动检测工具）
└── README.md
```

---

## 关键事实

- **许可证**: MIT
- **51,000+ 星** — 由大型社区经过实战检验
- **无需 API 密钥** — 代理是提示文件，不是服务
- **工具无关** — 适用于任何接受系统提示的 LLM 工具
- **可扩展** — 按照相同的 markdown 模式添加自定义代理
- **欢迎 PR** — 名册通过社区贡献不断增长
