# 技能审查器

对照官方最佳实践审查和改进 Claude Code 技能。

## 快速入门

使用 `uv` 明确声明 PyYAML 运行捆绑的审查器：

```bash
uv run --with PyYAML python <this-skill-path>/scripts/review_skill.py <target-skill-path>
uv run --with PyYAML python <this-skill-path>/scripts/review_skill.py <target-skill-path> --json
```

审查器将 YAML、模式（schema）和内部路径验证委托给同一套件中捆绑的标准 `skill-creator` 验证器。然后它会检查 frontmatter 质量、目录结构、SKILL.md 大小、硬编码路径和密钥、脚本卫生、`subagent_type` 有效性以及指令式启发式规则。

按以下方式解释退出代码：0 = 清洁，1 = 仅警告，2 = 审查错误，3 = 调用或运行时失败。代码 1 和 2 描述目标技能；代码 3 表示审查器无法完成可信的审查。

使用同级的 `skill-creator` 脚本进行更深入的安全扫描和打包检查。

## 三种模式

### 模式 1：自我审查

在发布前检查自己的技能。

**自动化审查：**

```bash
uv run --with PyYAML python <this-skill-path>/scripts/review_skill.py <target-skill>
```

**扩展安全验证：**

```bash
# 安全扫描
uv run python <this-skill-path>/../skill-creator/scripts/security_scan.py <target-skill> --verbose
```

**手动评估**：参见 `references/evaluation_checklist.md`。

### 模式 2：外部审查

评估其他人的技能仓库。

```
审查工作流程：
- [ ] 将仓库克隆到 /tmp/
- [ ] 首先阅读所有文档
- [ ] 确定作者的意图
- [ ] 运行评估清单
- [ ] 生成改进报告
```

### 模式 3：自动 PR

分支、改进并向外部技能仓库提交 PR。

```
自动 PR 工作流程：
- [ ] 分支仓库 (gh repo fork)
- [ ] 创建功能分支
- [ ] 仅应用增量改进
- [ ] 自我审查：尊重检查是否通过？
- [ ] 创建带详细说明的 PR
```

## 评估清单（快速）

| 类别 | 检查项 | 状态 |
|------|-------|------|
| **Frontmatter** | 名称是否存在？ | |
| | 描述是否存在？ | |
| | 描述是否使用第三人称？ | |
| | 是否包含触发条件？ | |
| **指令** | 是否使用祈使句？ | |
| | 是否少于 500 行？ | |
| | 是否使用工作流模式？ | |
| **资源** | 是否没有硬编码路径？ | |
| | 脚本是否有错误处理？ | |

完整清单：`references/evaluation_checklist.md`

## 核心原则：仅增量改进

改进外部技能时，永远不要：

- 删除现有文件
- 移除功能
- 更改主要语言
- 重命名组件

始终：

- 添加新功能
- 保留原始内容
- 解释每次变更

```
❌ "删除了 metadata.json (非标准)"
✅ "添加了 marketplace.json (metadata.json 保留)"

❌ "将 README 改为英文"
✅ "添加了 README.en.md (中文保留为默认)"
```

## 常见问题及修复方法

### 问题：描述未使用第三人称

```yaml
# 之前
description: 浏览 YouTube 视频并总结它们。

# 之后
description: 浏览 YouTube 视频并生成摘要。使用时...
```

### 问题：缺少触发条件

```yaml
# 之前
description: 处理 PDF 文件。

# 之后
description: 从 PDF 中提取文本。使用时处理 PDF 文件、提及 PDF、表单或文档提取。
```

### 问题：没有工作流模式

为复杂任务添加清单：

```markdown
## 工作流

复制此清单：

\`\`\`
任务进度：
- [ ] 步骤 1：...
- [ ] 步骤 2：...
\`\`\`
```

### 问题：缺少市场支持

添加或验证 `marketplace.json`（插件边界、`source`/`skills` 布局、技能是否可独立切换）是 `marketplace-dev` 技能的领域——不要从这里从模板编写它。调用 `daymade-claude-code:marketplace-dev`，然后遵循其工作流程及其缓存和源模式参考。

## PR 指南

向外部仓库提交 PR 时：

### 语气

```
❌ "您的技能不符合最佳实践"
✅ "此 PR 符合最佳实践，以提升可发现性"

❌ "修正了错误的描述"
✅ "通过添加触发条件改进了描述"
```

### 必须包含的部分

1. **摘要** - 此 PR 的作用
2. **未变更内容** - 尊重原始内容
3. **理由** - 每次变更为何有帮助
4. **测试计划** - 如何验证

模板：`references/pr_template.md`

## 自我审查清单

提交任何 PR 前：

```
尊重检查：
- [ ] 是否没有删除文件？
- [ ] 是否没有移除功能？
- [ ] 是否保留原始语言？
- [ ] 是否尊重作者的决策？
- [ ] 所有变更是否为增量？
- [ ] PR 是否解释了 "为何"？
```

## 参考文献

- `scripts/review_skill.py` - 基于 `skill-creator` 验证的后盾自动化审查器
- `references/evaluation_checklist.md` - 完整评估清单
- `references/pr_template.md` - PR 描述模板
- 最佳实践：https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
