## 核心原则
**简洁至上。** 上下文窗口是系统提示、技能、对话历史和推理共享的资源。SKILL.md 中的每一行都与其他所有内容竞争。只添加您已知的内容——不要记录系统提示中可见的工具参数，不要为您可以弄清楚的事情规定逐步工作流程。专注于领域知识、解释指南、决策框架和常见问题。

**渐进式披露。** 技能加载分为三个级别：
1. **始终在上下文中** — 名称、表情符号和描述在每个对话中出现在 `<available_skills>` 中。这是您决定激活哪个技能的方式。描述必须是一个强烈的触发器。
2. **在激活时** — 当您决定技能相关时，通过 `read_file` 加载完整的 SKILL.md 正文。这是工作流程、指南和决策树所在的地方。
3. **按需加载** — `scripts/`、`references/` 和 `assets/` 仅在明确需要时加载。大量内容放在这里，而不是正文。

这意味着：保持 SKILL.md 正文精简（<500 行）。将详细的 API 文档放在 `references/` 中。将自动化放在 `scripts/` 中。正文应该是您开始工作时需要的，而不是一部百科全书。

**自由度的程度。** 根据任务的易碎性匹配指令的特定性：

- **高自由度**（文本指导）— 当多种方法都有效时。用自然语言解释“什么”和“为什么”，而不是逐步的“如何”。例如：“检查资金利率和社会情绪来衡量市场情绪。”
- **中等自由度**（伪代码 + 参数）— 当存在首选模式，但细节可以变化时。用关键参数描述方法。例如：“使用周期为 14 的 RSI，低于 30 时买入，高于 70 时卖出。”
- **低自由度**（`scripts/` 中的脚本）— 当操作易碎、需要精确语法或重复的样板代码时。将代码放在独立的脚本中执行，而不是加载到上下文中。例如：使用精确的颜色代码和 API 调用进行图表渲染。

默认假设：您已经很聪明。只添加您已有的上下文。

## 技能的构成
```
my-skill/
├── SKILL.md          # 必须的：Frontmatter + 指令
├── scripts/          # 可选的：可执行代码（低自由度）
│   └── render.py     #   通过 bash 运行，不加载到上下文中
├── references/       # 可选的：按需加载的文档（中等自由度）
│   └── api-guide.md  #   需要时通过 read_file 加载
└── assets/           # 可选的：模板、图像、数据文件
    └── template.json #   不加载到上下文中，用于输出
```

**何时使用每个：**

| 目录 | 加载到上下文中？ | 用于 |
|-------|---------------------|---------|
| SKILL.md 正文 | 激活时 | 核心工作流程、决策树、常见问题 |
| `scripts/` | 从不（执行） | 易碎操作、精确语法、样板代码 |
| `references/` | 按需 | 详细的 API 文档、长指南、查找表 |
| `assets/` | 从不 | 模板、图像、输出中使用的文件 |

## 创建技能
### 第 1 步：理解请求

在搭建之前，了解您正在构建什么：

- **什么能力？** API 集成、工作流程自动化、知识领域？
- **什么触发它？** 何时应该代理激活此技能？（这将成为描述。）
- **什么自由度级别？** 代理可以即兴发挥，还是需要精确脚本？
- **什么依赖项？** API 密钥、二进制文件、Python 包？

示例：
- “我想生成图表” → 图表技能，带有脚本（低自由度渲染）
- “帮助我思考交易策略” → 知识技能（高自由度，对话式）
- “与 Binance API 集成” → API 技能，带有环境要求和参考文档

### 第 2 步：搭建

使用初始化脚本：

```bash
python skills/skill-creator/scripts/init_skill.py my-new-skill --path ./workspace/skills
```

带有资源目录：

```bash
python skills/skill-creator/scripts/init_skill.py api-helper --path ./workspace/skills --resources scripts,references
```

带有示例文件：

```bash
python skills/skill-creator/scripts/init_skill.py my-skill --path ./workspace/skills --resources scripts --examples
```

### 第 3 步：规划可重用内容

在编写之前，决定什么放在哪里：

- **SKILL.md 正文**：代理每次激活此技能时需要的核心指令。决策树、解释指南、“何时做 X 而不是 Y”的逻辑。
- **scripts/**：任何必须按原样运行的代码——带有特定认证的 API 调用、使用精确格式的渲染、数据处理管道。
- **references/**：代理偶尔可能需要的详细文档——完整的 API 端点列表、模式定义、故障排除指南。
- **assets/**：代理复制/修改以用于输出的输出模板、图像、配置文件。

### 第 4 步：编写 SKILL.md

先规划内容——frontmatter 触发器、正文结构、自由度级别。然后：

1. **Frontmatter** — 更新描述（关键触发器）、添加要求、设置表情符号
2. **Body** — 为代理编写，而不是为用户编写。短段落优于墙上的项目符号。观点优于模棱两可。

正文的设计模式：

- **基于工作流程** — 逐步过程（图表：获取数据 → 配置图表 → 渲染 → 提供）
- **基于任务** — 按用户可能询问的内容组织（交易：“分析一枚硬币” / “比较策略” / “检查情绪”）
- **参考/指南** — 规则和框架（策略：核心真理、对话风格、何时获取数据）
- **基于功能** — 按技能能做什么组织（市场数据：价格工具 / 衍生品工具 / 社交工具）

### 第 5 步：通过 `skill_manage` 创建/更新

**`skill_manage` 是主要工作流程** — 它验证 frontmatter、运行安全扫描并自动重新加载缓存。不要使用 `write_file` 作为主要路径。

**创建新技能：**
```python
skill_manage(action="create", name="my-skill", content="---\nname: my-skill\n...")
```

**修补现有技能（针对特定更改的首选方法）：**
```python
# 总是先 read_file 获取确切的空格/内容
skill_manage(action="patch", name="my-skill", old_string="exact old text", new_string="new text")
```

**现有技能的完整重写：**
```python
skill_manage(action="edit", name="my-skill", content="---\nname: my-skill\n...")
```

⚠️ **已知常见问题：**
- `create` 错误如果技能已存在 → 使用 `edit` 或 `patch` 代替。
- `edit`/`patch` 错误如果技能不存在 → 首先使用 `create`。
- `patch` 需要 `old_string` 的精确匹配（包括空格）→ 在修补之前始终 `read_file`。
- `execute()` 必须接受 `**kwargs` — 如果您看到 `unexpected keyword argument 'action'`，这是工具实现中的错误（修复：`def execute(self, **kwargs)`）。

**仅作为后备** — 如果 `skill_manage` 不可用，请手动使用 `write_file` + `skill_refresh()`。

### 第 6 步：验证

```bash
python skills/skill-creator/scripts/validate_skill.py ./workspace/skills/my-new-skill
```

在 `skill_manage` 之后，验证是可选的（自动重新加载），但运行它以尽早捕获模式问题。

## Frontmatter 格式
Frontmatter 使用 `metadata.starchild` 用于 Star Child 特定字段：

```yaml
---
name: skill-name
version: 1.0.0
description: "这个技能做什么。在 [特定触发场景] 时使用。"

metadata:
  starchild:
    emoji: "🔧"
    skillKey: skill-name
    requires:
      env: [API_KEY_NAME]
      bins: [python]
      anyBins: [curl, wget]
    install:
      - kind: pip
        package: pandas
      - kind: apt
        package: curl
        bins: [curl]

user-invocable: true
disable-model-invocation: false
---
```

**字段参考：**

| 字段 | 位置 | 必须的 | 目的 |
|-------|----------|----------|---------|
| `name` | 顶层 | 是 | 技能标识符（小写连字符） |
| `version` | 顶层 | 是 | 语义版本（例如 `1.0.0`）。发布时必需。始终包含。 |
| `description` | 顶层 | 是 | 触发文本 — 何时应该代理使用此技能？ |
| `emoji` | `metadata.starchild` | 否 | 显示表情符号 |
| `skillKey` | `metadata.starchild` | 否 | 唯一标识符 |
| `requires.env` | `metadata.starchild` | 否 | 必需的环境变量 |
| `requires.bins` | `metadata.starchild` | 否 | 必需的二进制文件（所有都必须存在） |
| `requires.anyBins` | `metadata.starchild` | 否 | 必需的二进制文件（任意一个） |
| `install` | `metadata.starchild` | 否 | 如何安装依赖项（pip、apt、npm 等） |
| `user-invocable` | 顶层 | 否 | 用户是否可以通过 /command 触发（默认：true） |
| `disable-model-invocation` | 顶层 | 否 | 隐藏 `<available_skills>` 中（默认：false） |

## 链上技能 — 钱包策略先决条件
如果技能涉及**任何链上操作**（发送交易、代币批准、交换、桥接、签名、存款、提款、智能合约交互），在 SKILL.md 顶部附近添加一个先决条件部分：

```markdown

## 先决条件 — 钱包策略
在执行任何 [操作] 之前，必须激活钱包策略。
加载 **wallet-policy** 技能并提议标准通配符策略（拒绝密钥导出 + 允许 `*`）。这涵盖了所有 [skill-name]
跨所有链的操作。
```

这确保代理在尝试任何交易之前提议一个钱包策略。没有它，第一个交易会因为策略违规而失败。

## 不应包含的内容
- **README.md** — SKILL.md 就是自述文件。不要重复。
- **CHANGELOG.md** — 技能不是版本化软件包。
- **代理已有的文档** — 不要重复系统提示中来自工具的描述。
- **简单任务的逐步说明** — 代理可以弄清楚“读取文件然后处理它。”
- **通用编程建议** — “使用错误处理”是噪音。具体的常见问题才是信号。

## 最佳实践
1. **描述是触发器。** 这是代理决定激活您的技能的方式。包含“在 [具体场景] 时使用”的特定情况。不好：“交易工具。” 好：“在真实历史数据上测试交易策略。在策略需要验证或提交交易方法之前使用。”
2. **为代理编写，而不是为用户编写。** 技能是 AI 的指令。使用直接语言：“您生成图表”而不是“此技能可用于生成图表。”
3. **脚本无需加载即可执行。** 适用于大型自动化。代理仅在需要时读取脚本，保持上下文干净。
4. **不要重复系统提示。** 代理已经看到工具名称和描述。专注于它没有的知识：解释指南、决策树、特定领域的常见问题。
5. **最后请求凭证。** 先设计技能，然后请求用户 API 密钥。
6. **始终验证** 之前刷新 — 运行 `validate_skill.py` 以尽早发现问题。
