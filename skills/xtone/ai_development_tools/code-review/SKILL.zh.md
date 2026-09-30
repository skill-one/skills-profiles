---
name: code-review
description: 我们将执行通用代码评审，对代码质量、安全性和设计进行基于共同标准的评估，并据此做出批准/拒绝的判断。请用于“评审此PR”、“进行代码评审”、“合并前检查”等请求，或在执行`gh pr view`命令时使用。
---

# 代码审查

这是一项用于系统化审查 PR 或代码变更的通用技能。
结合了语言无关的通用审查标准以及语言/框架特有的最佳实践来使用。

## 目录结构

```
code-review/
├── SKILL.md (此文件)
└── references/
    ├── typescript-best-practices.md       # TypeScript特有的检查
    ├── authorization-review-general.md    # 授权审查角度（通用篇）
    ├── authorization-review-postgres-rls.md  # 授权审查角度（PostgreSQL RLS篇）
    ├── github-pr-review-actions.md        # GitHub PR审查操作
    ├── ci-optimized-workflow.md           # CI环境中的成本优化工作流
    ├── incremental-review.md             # 增量审查的详细说明
    ├── skill-review.md                    # Claude Code技能（SKILL.md）审查标准
    ├── skill-overview.md                  # 技能概述（官方文档）
    └── skill-best-practices.md            # 技能最佳实践（官方文档）
```

## 运行时文件

CI 运行时自动生成的文件。不要将它们提交到仓库。

| 文件 | 用途 | 生命周期 |
|------|------|----------|
| `.pr-triage.json` | 仲裁结果 | 每次生成 |
| `.pr-review-state.json` | 审查状态 | `actions/cache` 中运行间持久化 |

## 外部技能协作

React / Next.js 的最佳实践使用 Vercel 提供的 **vercel-react-best-practices** 技能。

- **仓库**: https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices
- **安装**: `npx -y skills add vercel-labs/agent-skills --skill vercel-react-best-practices --agent claude-code --yes`
- **覆盖范围**: 排除异步瀑布流、优化打包大小、服务器端性能、客户端数据获取、优化重渲染、渲染性能、高级模式、JavaScript性能（8个类别，40多条规则）

## 成本优化（CI环境）

在 GitHub Actions 等CI环境中运行时，将仲裁阶段委托给轻量级模型（Haiku）可以大幅降低成本。
详细信息请参阅 [references/ci-optimized-workflow.md](references/ci-optimized-workflow.md)。

### 仲裁结果的利用

如果CI环境执行了预仲裁，则工作目录中会存在 `.pr-triage.json` 文件。
如果存在此文件，则应用以下优化：

1. **跳过步骤1** — 使用仲裁结果的 `summary`
2. **选择性加载参考** — 只读取 `required_references` 中包含的内容
3. **省略表层检查** — `surface_issues` 中包含的 Minor/Suggestion 问题视为已检查，专注于 Critical/Major 分析
4. **高效确认差异** — 利用 `files` 的分类，优先审查重要性高的文件

```json
// .pr-triage.json 的结构
{
  "pr_number": 123,
  "summary": "添加认证中间件和创建新的用户API",
  "files": {
    "added": ["src/middleware/auth.ts", "src/api/users.ts"],
    "modified": ["src/routes/index.ts"],
    "deleted": []
  },
  "languages": ["typescript"],
  "frameworks": ["express"],
  "change_categories": {
    "has_auth_changes": true,
    "has_db_changes": false,
    "has_rls_changes": false,
    "has_api_changes": true,
    "has_test_changes": false,
    "has_config_changes": false,
    "has_skill_changes": false
  },
  "required_references": [
    "typescript-best-practices.md",
    "authorization-review-general.md"
  ],
  "surface_issues": [
    {
      "severity": "Minor",
      "file": "src/api/users.ts",
      "line": 15,
      "issue": "`any`类型被使用",
      "suggestion": "改为具体类型"
    }
  ],
  "diff_summary": "添加了认证中间件。实现了JWT令牌验证。创建了新的用户CRUD API。未添加测试。",
  "estimated_complexity": "medium",
  "focus_areas": ["安全: JWT验证实现", "授权: 用户API的访问控制"]
}
```

> **如果 `.pr-triage.json` 不存在**，则按传统方式从步骤1执行所有步骤（向后兼容）。

### 增量审查（PR更新时的差异优化）

在PR更新（`synchronize`事件）时，利用之前的审查状态减少令牌消耗。
详细信息请参阅 [references/incremental-review.md](references/incremental-review.md)。

> **如果 `.pr-review-state.json` 不存在**（首次审查）则不应用增量优化，执行全量仲裁。

## 审查工作流

复制以下检查清单以跟踪进度：

```
审查进度：
- [ ] 步骤1: 理解变更概要
- [ ] 步骤2: 通用质量检查
- [ ] 步骤3: 语言/框架特定检查
- [ ] 步骤4: approve/reject判定
- [ ] 步骤5: 输出审查结果
```

### 步骤1: 理解变更概要

> **如果 `.pr-triage.json` 存在**: 读取此文件，使用 `summary`、`files`、`change_categories`、`diff_summary`。跳过以下手动确认，直接进入步骤2。

理解变更内容。

1. **确认变更文件列表** - 了解变更的范围和范围
2. **确认代码差异** - 了解添加、修改、删除的内容
3. **理解变更意图** - 从PR说明或提交信息中确认目的

需要确认的要点：
- 变更是否专注于单一目标
- 范围是否适当（避免一个PR包含过多变更）
- 是否包含所有相关变更

### 步骤2: 通用质量检查

> **如果 `.pr-triage.json` 存在**: `surface_issues` 中包含的 Minor/Suggestion 问题已检查。此处专注于 Critical/Major 级别（安全、逻辑/准确性、性能的重大问题）的检测。表层问题（命名规范、解构等）无需重新检查。

执行语言无关的通用检查。

#### 2-1. 安全

| 检查项 | 重要度 |
|-------------|--------|
| 是否存在硬编码的敏感信息（API密钥、密码、令牌） | Critical |
| 是否有适当的用户输入验证和清理 | Critical |
| 是否存在SQL注入、XSS、命令注入漏洞 | Critical |
| 是否正确实现了认证和授权检查 | Critical |
| 是否存在不当地记录机密数据 | Major |
| CORS配置是否适当 | Major |

> **授权（Authorization）的详细审查**：如果存在与授权相关的变更，请参考 [references/authorization-review-general.md](references/authorization-review-general.md) 进行详细检查。如果使用PostgreSQL RLS，请额外参考 [references/authorization-review-postgres-rls.md](references/authorization-review-postgres-rls.md)。

#### 2-2. 逻辑/准确性

| 检查项 | 重要度 |
|-------------|--------|
| 是否正确处理了边界情况（null、空数组、边界值） | Major |
| 是否正确处理了错误（异常捕获、不当的catch） | Major |
| 条件分支逻辑是否正确（off-by-one、逻辑运算符错误） | Major |
| 是否存在异步处理的竞争条件（race condition） | Major |
| 是否确保资源正确释放（文件、连接、锁） | Major |

#### 2-3. 设计/可维护性

| 检查项 | 重要度 |
|-------------|--------|
| 函数/方法的职责是否单一 | Minor |
| DRY原则: 是否存在不必要的重复代码 | Minor |
| 命名是否准确表达意图 | Minor |
| 是否存在魔法数字或含义不明的字符串字面量 | Minor |
| 是否以适当的抽象度进行设计（过度抽象/不足） | Minor |
| 是否存在循环依赖或不适当的依赖关系 | Major |

#### 2-4. 性能

| 检查项 | 重要度 |
|-------------|--------|
| 是否存在N+1查询等低效的数据访问模式 | Major |
| 是否存在不必要的循环、嵌套、大量计算 | Minor |
| 是否存在内存泄漏的可能性 | Major |
| 是否对大量数据进行了适当的分页/流处理 | Minor |

#### 2-5. 测试

| 检查项 | 重要度 |
|-------------|--------|
| 是否添加/更新了针对变更的测试 | Major |
| 是否包含边界情况的测试 | Minor |
| 是否测试了行为而非实现细节 | Minor |
| 测试名称是否明确表达了测试行为 | Suggestion |

### 步骤3: 语言/框架特定检查

> **如果 `.pr-triage.json` 存在**: 仅加载 `required_references` 中记录的参考文件。不加载列表中未提及的参考（节省令牌）。

根据变更文件的言語/框架，参考相应的参考文件。

**可参考的参考：**

| 言語/FW | 参考目标 | 类型 |
|---------|--------|------|
| TypeScript | [references/typescript-best-practices.md](references/typescript-best-practices.md) | 内部参考 |
| React / Next.js | `vercel-react-best-practices` 技能（Vercel提供） | 外部技能 |

| 观点 | 参考目标 | 类型 |
|------|--------|------|
| 授权（通用） | [references/authorization-review-general.md](references/authorization-review-general.md) | 内部参考 |
| 授权（PostgreSQL RLS） | [references/authorization-review-postgres-rls.md](references/authorization-review-postgres-rls.md) | 内部参考 |
| GitHub PR审查 | [references/github-pr-review-actions.md](references/github-pr-review-actions.md) | 内部参考 |
| Claude Code技能 | [references/skill-review.md](references/skill-review.md) | 内部参考 |

**参考规则：**
- TypeScript变更 → 加载内部参考
- React / Next.js 变更 → 使用 `vercel-react-best-practices` 技能（如果已安装）
- 授权相关变更（认证/权限检查、数据访问控制等）→ 参考 授权参考（通用篇）
- 使用PostgreSQL RLS时 → 额外参考 授权参考（RLS篇）
- 在GitHub Actions等CI环境中执行PR审查时 → 参考 GitHub PR审查操作（评论发布/评估方法）
- 包含 SKILL.md 文件的变更 → 参考 技能审查参考，并执行技能质量检查
- 跨多个言語/FW的变更 → 参考所有相关参考
- 对于不存在的言語 → 仅执行步骤2的通用检查

### 步骤4: approve/reject判定

基于所有检查结果，使用以下标准判定 approve/reject。

#### 问题的严重程度和扣分

| 严重程度 | 说明 | 扣分 |
|--------|------|------|
| **Critical** | 必须在合并前修正。安全漏洞、数据丢失风险、重大错误 | -3分/项 |
| **Major** | 优先修正。逻辑问题、性能下降、测试不足 | -2分/项 |
| **Minor** | 建议改进。设计改进、可读性提升、轻微问题 | -1分/项 |
| **Suggestion** | 建议。最佳实践推荐、更优方法的提示 | -0.5分/项 |

#### 判定标准

满分10分，以下标准判定：

| 判定 | 条件 | 动作 |
|------|------|------|
| **Reject** | 存在Critical问题 | REQUEST_CHANGES |
| **Reject** | Major问题3个以上 | REQUEST_CHANGES |
| **Reject** | 分数低于5 | REQUEST_CHANGES |
| **Conditional Approve** | 无Critical问题、Major 1-2个、分数5以上 | APPROVE（评论改进点） |
| **Approve** | 无Critical/Major问题、分数8以上 | APPROVE |

#### 判定流程图

```
存在Critical问题？ → Yes → Reject（REQUEST_CHANGES）
       ↓ No
Major问题3个以上？ → Yes → Reject（REQUEST_CHANGES）
       ↓ No
分数低于5？ → Yes → Reject（REQUEST_CHANGES）
       ↓ No
Major问题1-2个？ → Yes → Conditional Approve
       ↓ No
分数8以上？ → Yes → Approve
       ↓ No
Conditional Approve
```

### 步骤5: 输出审查结果

> **如果 `.pr-triage.json` 存在**: 将仲裁阶段的 `surface_issues` 合并到审查结果的“检测到的问题”表格中（排除重复）。评分包含仲裁的指摘。

使用以下格式输出审查结果。

> **在GitHub上提交审查**：仅在GitHub Actions等CI环境中执行PR审查时，参考 [references/github-pr-review-actions.md](references/github-pr-review-actions.md) 使用 `gh` 命令或内联评论将审查结果提交到GitHub。本地环境执行时仅将结果输出到标准输出。
>
> **跟进已修正的问题**：如果 `.pr-triage.json` 包含 `resolved_issues`（增量审查时），请回复原内联评论报告修正。审查完成后，记录提交的评论ID到 `.pr-review-state.json`。

```markdown
## Code Review: [判定结果]

### 变更概要
- **范围**: [用1-2句话描述变更]
- **变更文件数**: [N]个文件
- **主要言語/FW**: [检测到的言語/FW]

### 分数: X/10

### 检测到的问题

| # | 严重程度 | 文件 | 问题 | 建议的解决方案 |
|---|--------|------|------|---------------|
| 1 | [Critical/Major/Minor/Suggestion] | [文件路径:行号] | [问题的描述] | [解决方案] |

### 好的方面
- [代码的好的方面，具体描述]

### 判定
- **结果**: [Approve / Conditional Approve / Reject]
- **理由**: [判定理由的摘要]

### 下一步
- [需要修正时的具体行动]
```

## 重要注意事项

- 审查的目的是提高代码质量，而非批评。请提供建设性反馈
- 指出问题时必须附带**具体的改进建议**
- 尊重变更的**意图**，以客观标准而非个人偏好进行判断
- 对于人类难以自动检测的领域知识或业务逻辑判断，委托给人工审查者
- Suggestion不是强制性的，是否采用由作者决定
