## 目的

在没有混乱的情况下创建或更新 PM 技能。此工作流将粗略笔记、研讨会内容或半成品提示堆栈转化为符合规范的 `skills/<skill-name>/SKILL.md` 资产，这些资产实际上可以通过验证并属于此存储库。

当你想在不使用“我觉得看起来不错”的轮盘赌的情况下发布新技能时，请使用它。

## 输入

带来原始材料和意图——粗略的即可；工作流的存在是为了将其余部分完成：
- **最佳使用情况**：源内容（笔记、转录稿、框架、提示序列）或您想要更新的现有技能
- **也很有用**：预期的技能类型（组件/交互式/工作流）、目标受众和任何命名偏好

如果您在请求中内联提供这些信息（例如，“将 `research/pricing-workshop-notes.md` 转换为交互式顾问”），工作流将从阶段 1 开始使用该上下文——它不会重新询问您已经提供的内容。如果您提供 nothing，它将打开并询问您想要将其转换为技能的内容，并提供来自促进协议的入口模式。

示例：`Use skill-authoring-workflow: convert research/pricing-workshop-notes.md into an interactive pricing advisor.`

## 关键概念

### 首先自用

在使用自定义流程之前，使用存储库原生工具和标准：
- `scripts/find-a-skill.sh`
- `scripts/add-a-skill.sh`
- `scripts/build-a-skill.sh`
- `scripts/test-a-skill.sh`
- `scripts/check-skill-metadata.py`

### 选择正确的创建路径

- **引导式向导 (`build-a-skill.sh`)**：当您有一个想法但还没有最终文本时最佳。
- **内容优先生成器 (`add-a-skill.sh`)**：当您已经拥有源内容时最佳。
- **手动编辑 + 验证**：用于收紧现有技能的最佳方式。

### 完成（无例外）

只有当满足以下条件时，技能才算完成：
1. 前置信息有效 (`name`、`description`、`intent`、`type`)
2. 章节顺序合规（目的、输入、关键概念、应用、示例、常见陷阱、参考文献）
3. 尊重元数据限制 (`name` <= 64 个字符，`description` <= 200 个字符)
4. 描述说明技能的作用以及何时使用它
5. 输入部分说明用户可以带来什么，显示示例调用，指示代理使用内联输入而不是重新询问，并明确说明带有部分或零输入是允许的——用普通语言，而不是运行时模板语法，如 `$ARGUMENTS`（理由：CONTRIBUTING.md，“为什么我们不使用 `$ARGUMENTS`”）
6. 意图包含更完整的面向存储库的摘要，而不会取代触发式描述
7. 交叉引用解析
8. README 目录计数和表格已更新（如果添加/删除技能）

### 促进协议的真相来源

当以引导式对话运行此工作流时，使用 [`workshop-facilitation`](../workshop-facilitation/SKILL.md) 作为交互协议。

它定义了：
- 会话开场 + 入口模式（引导式、上下文堆栈、最佳猜测）
- 带有普通语言提示的单问题回合
- 进度标签（例如，Context Qx/8 和 Scoring Qx/5）
- 中断处理和暂停/恢复行为
- 决策点的编号建议
- 定期问题的快速选择编号响应选项（在需要时包含 `Other (specify)`）

此文件定义了工作流序列和特定领域的输出。如果有冲突，请遵循此文件的工作流逻辑。

## 应用

### 阶段 1：预检（避免重复工作）

1. 搜索重叠的技能：

```bash
./scripts/find-a-skill.sh --keyword "<topic>"
```

2. 确定类型：
- **组件**：一个工件/模板
- **交互式**：3-5 个自适应问题 + 编号选项
- **工作流**：多阶段编排

### 阶段 2：生成草稿

如果您有源材料：

```bash
./scripts/add-a-skill.sh research/your-framework.md
```

如果您需要引导式提示：

```bash
./scripts/build-a-skill.sh
```

### 阶段 3：收紧技能

手动检查：
- 清晰的“何时使用”指导
- 一个具体的示例——最好是两个，来自不同的业务领域（一个 SaaS，一个工业/非 SaaS），以便框架明显具有通用性；重用存储库的虚构宇宙（Fieldlight/Wrenchline 用于 SaaS，Helix/Northfield/Corvid 用于工业）并为第二个文件按领域后缀（`sample-industrial.md`）
- 当技能生成工件时，一个 `template.md`——输出模式作为可复制粘贴的填空，附带质量检查
- 一个明确的反模式
- 没有填充或模糊的顾问式语言

### 阶段 4：严格验证

在考虑提交之前运行严格检查：

```bash
./scripts/test-a-skill.sh --skill <skill-name> --smoke
python3 scripts/check-skill-metadata.py skills/<skill-name>/SKILL.md
python3 scripts/check-skill-triggers.py skills/<skill-name>/SKILL.md --show-cases
```

### 阶段 5：与存储库文档集成

如果这是一个新技能：
1. 将其添加到正确的 README 分类表格
2. 更新技能总数和分类计数
3. 验证链接路径解析

### 阶段 6：可选的打包

如果目标是 Claude 自定义技能上传：

```bash
./scripts/zip-a-skill.sh --skill <skill-name>
# 或打包一个分类：
./scripts/zip-a-skill.sh --type component --output dist/skill-zips
# 或使用一个精选的启动预设：
./scripts/zip-a-skill.sh --preset core-pm --output dist/skill-zips
```

## 示例

### 示例：将研讨会笔记转换为技能

输入：`research/pricing-workshop-notes.md`  
目标：新交互式顾问

```bash
./scripts/add-a-skill.sh research/pricing-workshop-notes.md
./scripts/test-a-skill.sh --skill <new-skill-name> --smoke
python3 scripts/check-skill-metadata.py skills/<new-skill-name>/SKILL.md
```

预期结果：
- 新技能文件夹存在
- 技能通过结构和元数据检查
- README 目录条目添加/更新

### 反模式示例

“我们写了一个很酷的技能，跳过了验证，忘记了 README 计数，但还是发布了。”

结果：
- 破坏的引用
- 不一致的目录编号
- 对贡献者和用户的困惑

## 常见陷阱

- 发布氛围，而不是标准。
- 当任务实际上是组件模板时，选择 `workflow`。
- 体积膨胀的描述，超过上传限制。
- 描述说明技能是什么，但没有说明何时 Claude 应该触发它。
- 描述在 200 个字符限制内被无声地截断，导致中途思考被切断。
- 让 `intent` 成为弱触发描述的替代品。
- 添加技能后忘记更新 README 计数。
- 在未经审查的情况下将生成输出视为最终版本。

## 参考文献

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/Building PM Skills.md`
- `docs/Add-a-Skill Utility Guide.md`
- Anthropic 的 [Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- `scripts/add-a-skill.sh`
- `scripts/build-a-skill.sh`
- `scripts/find-a-skill.sh`
- `scripts/test-a-skill.sh`
- `scripts/check-skill-metadata.py`
- `scripts/check-skill-triggers.py`
- `scripts/zip-a-skill.sh`
