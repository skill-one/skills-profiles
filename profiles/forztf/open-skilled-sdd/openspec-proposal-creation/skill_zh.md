# 规范提案创建

遵循规范驱动开发方法论，创建全面的变更提案。

## 快速入门

创建规范提案涉及三个主要输出：
1. **proposal.md** - 为什么、做什么以及影响摘要
2. **tasks.md** - 编号实现清单
3. **spec-delta.md** - 正式需求变更（ADDED/MODIFIED/REMOVED）

**基本工作流程**：生成变更ID → 搭建目录结构 → 起草提案 → 创建规范变更 → 验证结构

## 工作流程

复制此清单并跟踪进度：

```
提案进度：
- [ ] 第1步：审查现有规范
- [ ] 第2步：生成唯一变更ID
- [ ] 第3步：搭建目录结构
- [ ] 第4步：起草 proposal.md（为什么/做什么/影响）
- [ ] 第5步：创建 tasks.md 实现清单
- [ ] 第6步：使用 EARS 格式编写 spec deltas
- [ ] 第7步：验证提案结构
- [ ] 第8步：提交用户审批
```

### 第1步：审查现有规范

在创建提案前，了解当前状态：

```bash
# 列出所有现有规范
find spec/specs -name "spec.md" -type f

# 列出活跃变更以避免冲突
find spec/changes -maxdepth 1 -type d -not -path "*/archive"

# 搜索相关需求
grep -r "### 需求：" spec/specs/
```

### 第2步：生成唯一变更ID

选择描述性强且URL安全的标识符：

**格式**：`add-<功能>`，`fix-<问题>`，`update-<组件>`，`remove-<功能>`

**示例**：
- `add-user-authentication`
- `fix-payment-validation`
- `update-api-rate-limits`
- `remove-legacy-endpoints`

**验证**：检查是否存在冲突：
```bash
ls spec/changes/ | grep -i "<proposed-id>"
```

### 第3步：搭建目录结构

创建具有标准结构的变更文件夹：

```bash
# 将 {change-id} 替换为实际ID
mkdir -p spec/changes/{change-id}/specs/{capability-name}
```

**示例**：
```bash
mkdir -p spec/changes/add-user-auth/specs/authentication
```

### 第4步：起草 proposal.md

使用 [templates/proposal.md](templates/proposal.md) 中的模板作为起点。

**必需部分**：
- **为什么**：驱动此变更的问题或机遇
- **变更内容**：修改的要点列表
- **影响**：受影响的规范、代码、API、用户

**语气**：清晰、简洁、以决策为导向。避免不必要的背景信息。

### 第5步：创建 tasks.md 实现清单

将实现分解为具体、可测试的任务。使用 [templates/tasks.md](templates/tasks.md) 中的模板。

**格式**：
```markdown
# 实现任务

1. [第一个具体任务]
2. [第二个具体任务]
3. [测试任务]
4. [文档任务]
```

**最佳实践**：
- 每个任务可独立完成
- 包含测试和验证任务
- 按依赖顺序排序（数据库优先于API等）
- 5-15个任务为典型值；如有需要可拆分

### 第6步：使用 EARS 格式编写 spec deltas

这是最关键的一步。规范变更使用 **EARS格式**（Easy Approach to Requirements Syntax）。

**有关完整的EARS指南**，请参阅 [reference/EARS_FORMAT.md](reference/EARS_FORMAT.md)

**变更操作**：
- `## ADDED Requirements` - 新增功能
- `## MODIFIED Requirements` - 改变行为（包含完整的更新文本）
- `## REMOVED Requirements` - 已弃用的功能

**基本需求结构**：
```markdown
## ADDED Requirements

### 需求：用户登录
当用户提交有效凭证时，
系统应验证用户并创建会话。

#### 场景：成功登录
给定一个具有邮箱 "user@example.com" 和密码 "correct123" 的用户
当用户提交登录表单时
系统应创建认证会话
并将用户重定向到仪表板
```

**有关验证模式**，请参阅 [reference/VALIDATION_PATTERNS.md](reference/VALIDATION_PATTERNS.md)

### 第7步：验证提案结构

在提交给用户前运行这些检查：

```markdown
结构检查清单：
- [ ] 目录存在：`spec/changes/{change-id}/`
- [ ] proposal.md 包含为什么/做什么/影响部分
- [ ] tasks.md 包含编号任务列表（5-15项）
- [ ] 规范变更包含操作标题（ADDED/MODIFIED/REMOVED）
- [ ] 需求遵循 `### 需求： <名称>` 格式
- [ ] 场景使用 `#### 场景:` 格式（4个井号）
```

**自动检查**：
```bash
# 统计变更操作数量（应大于0）
grep -c "## ADDED\|MODIFIED\|REMOVED" spec/changes/{change-id}/specs/**/*.md

# 验证场景格式（应显示行号）
grep -n "#### Scenario:" spec/changes/{change-id}/specs/**/*.md

# 检查需求标题
grep -n "### Requirement:" spec/changes/{change-id}/specs/**/*.md
```

### 第8步：提交用户审批

清晰总结提案：

```markdown
## 提案摘要

**变更ID**：{change-id}
**范围**：{简要描述}

**创建的文件**：
- spec/changes/{change-id}/proposal.md
- spec/changes/{change-id}/tasks.md
- spec/changes/{change-id}/specs/{capability}/spec-delta.md

**下一步**：
审查提案。如获批准，请说 "openspec implement" 或 "应用变更" 以开始实施。
```

## 高级主题

**EARS格式细节**：请参阅 [reference/EARS_FORMAT.md](reference/EARS_FORMAT.md)
**验证模式**：请参阅 [reference/VALIDATION_PATTERNS.md](reference/VALIDATION_PATTERNS.md)
**完整示例**：请参阅 [reference/EXAMPLES.md](reference/EXAMPLES.md)

## 常见模式

### 模式1：新功能提案

添加全新功能时：
- 使用 `ADDED Requirements` 变更
- 包含正向场景和错误处理
- 在场景中考虑边缘情况

### 模式2：破坏性变更提案

更改现有行为时：
- 使用 `MODIFIED Requirements` 变更
- 包含完整的更新需求文本
- 在 proposal.md 中记录变更内容和原因
- 在 tasks.md 中考虑迁移任务

### 模式3：弃用提案

移除功能时：
- 使用 `REMOVED Requirements` 变更
- 在 proposal.md 中记录弃用理由
- 在 tasks.md 中包含清理任务
- 在影响部分考虑用户迁移

## 应避免的反模式

**不要**：
- 跳过验证检查（始终运行 grep 模式）
- 在审查现有规范前创建提案
- 使用模糊的任务描述（"修复那个东西"）
- 编写无场景的需求
- 忘记错误处理场景
- 在一个提案中混合多个不相关的变更

**要**：
- 在创建变更ID前检查冲突
- 编写具体、可测试的任务
- 包含正向和负向场景
- 每个提案只关注一个问题
- 在提交前验证结构

## 文件模板

所有模板都在 `templates/` 目录中：
- [proposal.md](templates/proposal.md) - 提案结构
- [tasks.md](templates/tasks.md) - 任务清单格式
- [spec-delta.md](templates/spec-delta.md) - 规范变更模板

## 参考资料

- [EARS_FORMAT.md](reference/EARS_FORMAT.md) - 完整EARS语法指南
- [VALIDATION_PATTERNS.md](reference/VALIDATION_PATTERNS.md) - Grep/bash验证
- [EXAMPLES.md](reference/EXAMPLES.md) - 真实世界的提案示例

---

**令牌预算**：此 SKILL.md 大约450行，在建议的500行限制之内。参考文件仅在需要时加载，以实现渐进式披露。
