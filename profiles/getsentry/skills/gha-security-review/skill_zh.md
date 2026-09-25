<!-- 攻击模式与现实世界案例源自 StepSecurity（2025年）对 HackerBot Claw GitHub Actions 利用分析的贡献：https://www.stepsecurity.io/blog/hackerbot-claw-github-actions-exploitation -->

# GitHub Actions 安全审查

在 GitHub Actions 工作流中查找可利用的漏洞。每个发现**必须**包含具体的利用场景——如果你无法构建攻击，请不要报告。

这项技能编码了来自现实 GitHub Actions 利用中的攻击模式——不是通用的 CI/CD 理论。

## 范围

审查提供的工作流（文件、差异或仓库）。在报告之前，根据需要研究代码库以追踪完整的攻击路径。

### 需要审查的文件

- `.github/workflows/*.yml` — 所有工作流定义
- `action.yml` / `action.yaml` — 仓库中的组合动作
- `.github/actions/*/action.yml` — 本地可重用动作
- 工作流加载的配置文件：`CLAUDE.md`，`AGENTS.md`，`Makefile`，`.github/` 下的 shell 脚本

### 不在范围内

- 其他仓库中的工作流（仅注明依赖关系）
- GitHub App 安装权限（如相关则注明）

## 威胁模型

仅报告**外部攻击者**可利用的漏洞——某人**没有**对仓库的写入权限。攻击者可以打开来自分支的 PR，创建问题，发表评论。他们无法推送分支，触发 `workflow_dispatch` 或触发手动工作流。

**不要标记**需要写入权限才能利用的漏洞：
- `workflow_dispatch` 输入注入——需要写入权限才能触发
- 受保护分支上 `push` 仅工作流中的表达式注入
- 所有调用者都是内部用户的 `workflow_call` 输入注入
- `workflow_dispatch`/`schedule` 仅工作流中的密钥

## 置信度

仅报告**高**和**中**置信度的发现。不要报告理论问题。

| 置信度 | 标准 | 操作 |
|---|---|---|
| **高** | 追踪了完整的攻击路径，确认可利用 | 报告并附带利用场景和修复方案 |
| **中** | 部分确认攻击路径，不确定的关联 | 报告为需要验证 |
| **低** | 理论上的或已在其他地方缓解 | 不要报告 |

对于每个高置信度发现，提供所有五个要素：

1. **入口点**——攻击者如何进入？（分支 PR，问题评论，分支名等）
2. **有效载荷**——攻击者发送什么？（实际代码/YAML/输入）
3. **执行机制**——有效载荷如何运行？（表达式扩展，检出 + 脚本等）
4. **影响**——攻击者获得什么？（令牌窃取，代码执行，仓库写入权限）
5. **PoC 草图**——攻击者会遵循的具体步骤

如果你无法构建所有五个要素，报告为中等（需要验证）。

---

## 第 1 步：分类触发器并加载参考

对于每个工作流，识别触发器并加载相应的参考：

| 触发器 / 模式 | 加载参考 |
|---|---|
| `pull_request_target` | `references/pwn-request.md` |
| 带命令解析的 `issue_comment` | `references/comment-triggered-commands.md` |
| `run:` 块中的 `${{ }}` | `references/expression-injection.md` |
| PATs / 部署密钥 / 提升权限的凭证 | `references/credential-escalation.md` |
| 检出 PR 代码 + 配置文件加载 | `references/ai-prompt-injection-via-ci.md` |
| 第三方动作（尤其是未固定） | `references/supply-chain.md` |
| `permissions:` 块或密钥使用 | `references/permissions-and-secrets.md` |
| 自托管运行器，缓存/工件使用 | `references/runner-infrastructure.md` |
| 任何确认的发现 | `references/real-world-attacks.md` |

有选择地加载参考——仅与发现的触发器相关的参考。

## 第 2 步：检查漏洞类别

### 检查 1：Pwn Request

工作流是否使用 `pull_request_target` **并且**检出了分支代码？
- 查找 `actions/checkout`，其 `ref:` 指向 PR 头
- 查找来自分支的本地动作（`./.github/actions/`）
- 检查任何 `run:` 步骤是否执行来自检出的 PR 的代码

### 检查 2：表达式注入

`run:` 块中是否在可外部触发的工作流中使用了 `${{ }}` 表达式？
- 在每个 `run:` 步骤中映射每个 `${{ }}` 表达式
- 确认值受攻击者控制（PR 标题，分支名，评论正文——不是数字 ID，SHA 或仓库名）
- 确认表达式在 `run:` 块中，而不是 `if:`，`with:` 或作业级 `env:`

### 检查 3：未授权的命令执行

`issue_comment` 触发的工作流是否未经授权执行命令？
- 是否有 `author_association` 检查？
- 任何 GitHub 用户都可以触发命令吗？
- 命令处理程序是否也使用可注入的表达式？

### 检查 4：凭证提升

提升权限的凭证（PATs，部署密钥）是否可被不受信任的代码访问？
- 每个密钥的爆炸半径是什么？
- 被攻陷的工作流是否可以窃取长期令牌？

### 检查 5：配置文件中毒

工作流是否从 PR 提供的文件加载配置？
- AI 代理指令：`CLAUDE.md`，`AGENTS.md`，`.cursorrules`
- 构建配置：`Makefile`，shell 脚本

### 检查 6：供应链

第三方动作是否安全地固定到完整的 SHA？
- 仅固定第三方/外部动作和可重用工作流
- 不要标记第一方 `actions/*` 或 `github/*` 在版本标签上
- 不要标记同仓库/分发的（`./.github/actions/...`）作为供应链固定问题
- 仅在作业有密钥、OIDC、写入令牌、发布、部署、打包或签名权限时报告——无特权的只读 CI 不是发现

### 检查 7：权限和密钥

工作流权限是否最小化？密钥是否正确作用域？

### 检查 8：运行器基础设施

是否安全使用自托管运行器、缓存或工件？

## 安全模式（不要标记）

在报告之前，检查模式是否实际上安全：

| 模式 | 为什么安全 |
|---|---|
| 没有**检出分支代码**的 `pull_request_target` | 从不执行攻击者代码 |
| `run:` 中的 `${{ github.event.pull_request.number }}` | 仅数字——不可注入 |
| `${{ github.repository }}` / `github.repository_owner` | 仓库所有者控制此内容 |
| `${{ secrets.* }}` | 不是表达式注入向量 |
| `if:` 条件中的 `${{ }}` | 由 Actions 运行时评估，不是 shell |
| `with:` 输入中的 `${{ }}` | 作为字符串参数传递，不是 shell 评估 |
| 固定到完整 SHA 的第三方动作 | 不可变引用 |
| 版本标签上的第一方 `actions/*` / `github/*` | 在第三方固定策略之外——不要标记 |
| 同仓库/分发的本地动作 | 不是第三方供应链（单独审查 pwn-request） |
| `pull_request` 触发器（不是 `_target`） | 在分支上下文中以只读令牌运行 |
| `workflow_dispatch`/`schedule`/受保护分支 `push` 中的任何表达式 | 需要写入权限——在威胁模型之外 |

**关键区别：** `${{ }}` 在 `run:` 块中危险（shell 扩展），但在 `if:`, `with:` 和作业/步骤级别的 `env:` 中安全（Actions 运行时评估）。

## 第 3 步：报告前验证

在包含任何发现之前，阅读实际的工作流 YAML 并追踪完整的攻击路径：

1. **阅读完整工作流**——不要仅依赖 grep 输出
2. **追踪触发器**——确认事件并检查 `if:` 条件以控制执行
3. **追踪表达式/检出**——确认它在 `run:` 块中或实际引用分支代码
4. **确认攻击者控制**——验证值映射到外部攻击者可以设置的内容
5. **检查现有缓解措施**——环境变量包装，`author_association` 检查，限制权限，SHA 固定

如果任何环节中断，标记为中等（需要验证）或放弃该发现。

**如果没有检查产生发现，报告零发现。不要编造问题。**

## 第 4 步：报告发现

````markdown
## GitHub Actions 安全审查

### 发现

#### [GHA-001] [标题]（严重性：严重/高/中）
- **工作流**：`.github/workflows/release.yml:15`
- **触发器**：`pull_request_target`
- **置信度**：高——通过攻击路径追踪确认
- **利用场景**：
  1. [分步攻击]
- **影响**：[攻击者获得什么]
- **修复**：[修复问题的代码]

### 需要验证
[中等置信度项及其需要验证的解释]

### 已审查并清除
[已审查并确认安全的工作流]
````

如果没有发现： "未发现可利用的漏洞。所有工作流已审查并清除。"
