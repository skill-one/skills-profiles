# 复合技能

**目标：** 在工作流程中立即将验证后的洞察文档化，以构建可搜索的知识库。

## 概述

此技能会在洞察得到确认时立即捕捉，并以基于 YAML frontmatter 的结构化文档进行存储。它使用按类别划分的单文件架构，每个洞察都存储在 `knowledge/[category]/[filename].md` 中。

---

<critical_sequence name="insight-capture" enforce_order="strict">

## 7步流程

<step number="1" required="true">
### 第1步：触发检测

**自动检测语句（在对话中识别）：**

- "这个做得很好"
- "这种方式不错"
- "下次也这样做"
- "记录下来"
- "这个格式有效"
- "这个效果很好"
- "这样做有效"
- "需要记住"

**或者手动：** `/compound` 命令

**仅限非平凡（具有可重用价值的洞察）：**

- 可重复的模式
- 可应用于其他情况的教训
- 经历失败后发现的解决方案
- 在实践中得到验证的方法
- 带来结构化改进的发现

**跳过标准：**

- 仅限当前情况的一次性方法
- 简单事实记录（数字、日期等）
- 已文档化内容的重复
- 尚未验证的假设
</step>

<step number="2" required="true" depends_on="1">
### 第2步：收集上下文

从对话历史中提取：

**必要信息：**

- **domain**: work / learning / project / tool / personal
- **insight_type**: 洞察类型（参考 schema.yaml 中的枚举）
- **component**: domain 内的子组件（参考 schema.yaml 中的枚举）
- **context**: 洞察是在什么情况下产生的（1-3句话）
- **key_learning**: 核心教训一句话（可推广到其他情况）
- **impact**: critical / high / medium / low
- **tags**: 搜索关键词（小写，用连字符分隔）

**附加收集项：**

- 背景：在哪个项目/活动中
- 尝试过的方法：无效的方法
- 有效的方法：实际起作用的方法
- 原因：为什么有效
- 重现条件：何时可以使用此方法

**BLOCKING 条件：** 当 domain、insight_type、核心洞察不明确时，向用户提问并等待回复：

```
需要一些确认来文档化：

1. 哪个 domain？ (work/learning/project/tool/personal)
2. 洞察类型是什么？ (例如：workflow_pattern, problem_solving, tool_discovery...)
3. 用一句话总结核心教训？

[回复后继续]
```
</step>

<step number="3" required="false" depends_on="2">
### 第3步：搜索现有文档

在 `knowledge/` 中搜索相似洞察：

```bash
# 基于 domain、tags、insight_type 并行搜索
Grep: pattern="domain: [domain]" path=knowledge/ output_mode=files_with_matches
Grep: pattern="tags:.*[keyword]" path=knowledge/ output_mode=files_with_matches -i=true
Grep: pattern="insight_type: [type]" path=knowledge/ output_mode=files_with_matches
```

**发现相似文档时** 提供选项并等待用户：

```
发现相似文档：knowledge/[path]

怎么办？
1. 创建新文档 + 添加交叉引用（推荐）
2. 更新现有文档（如果是相同洞察的补充）
3. 其他

选择 (1-3): _
```

等待用户回复后执行选择的操作。

**没有相似文档时** 直接进入第4步。
</step>

<step number="4" required="true" depends_on="2">
### 第4步：创建文件名

格式：`YYYYMMDD-[sanitized-insight-slug].md`

**Sanitization 规则：**

- 小写
- 空格 → 连字符
- 删除特殊字符（连字符除外）
- 截断到80个字符以内

**示例：**

- `20260304-claude-code-skill-structure.md`
- `20260304-mcp-server-debugging-pattern.md`
- `20260304-prompt-iteration-framework.md`
</step>

<step number="5" required="true" depends_on="4" blocking="true">
### 第5步：YAML 验证 (BLOCKING)

**基于 schema.yaml 验证所有必要字段。**

<validation_gate name="yaml-schema" blocking="true">

**验证项：**

- `domain`: schema.yaml 中的枚举值之一
- `date`: YYYY-MM-DD 格式
- `insight_type`: schema.yaml 中的枚举值之一
- `component`: 对应 domain 的枚举值之一 (`domain_component_mapping` 检查)
- `context`: 20-300字，具体描述情况
- `key_learning`: 10-200字，可推广的教训
- `impact`: critical / high / medium / low
- `tags`: 1-8个，小写连字符分隔

**验证失败时阻止第6步：**

```
YAML 验证失败

错误：
- domain: 不是允许的值 → work, learning, project, tool, personal 之一
- component: domain 不允许的组件 → 参考 schema.yaml
- tags: 包含大写 → 需要转换为小写

请提供修改后的值。
```

**GATE 强制：** 在所有验证通过前禁止进行第6步。
</validation_gate>
</step>

<step number="6" required="true" depends_on="5">
### 第6步：文档编写

**确定类别目录：** 根据 schema.yaml 的 `category_mapping` 将 insight_type 映射到存储路径。

**文档创建：**

```bash
INSIGHT_TYPE="[验证后的 YAML]"
CATEGORY_DIR="[category_mapping 中的映射]"
FILENAME="[第4步创建]"
DOC_PATH="${CATEGORY_DIR}${FILENAME}"

# 如果目录不存在则创建
mkdir -p "${CATEGORY_DIR}"

# 基于 assets/resolution-template.md 创建文档
# (Step 2 中收集的上下文 + Step 5 中验证的 YAML frontmatter)
```

**结果：**

- 在类别目录中创建单个文件
- Enum 验证确保分类一致
</step>

<step number="7" required="false" depends_on="6">
### 第7步：交叉引用 & 模式检测

**如果第3步发现相似文档：**

```bash
# 在现有文档中添加 Related 部分
# 在新文档中也添加现有文档链接
```

**模式候选检测：**

如果同一类别中有3个或更多相似洞察：

```
检测到模式文档候选：[类别]中有相似洞察 X个
→ 要合并到 patterns/ 文档中吗？
```

**Critical Pattern 升级条件（禁止自动升级，需要用户决定）：**

- impact 为 `critical`
- 可横跨多个 domain 应用
- 必须记住的情况

如果这种情况，在 Decision Menu 中添加 "2. 添加到 Critical Pattern" 选项注释：

```
此洞察可以考虑升级为 Critical Pattern
```

</step>

</critical_sequence>

---

<decision_gate name="post-documentation" wait_for_user="true">

## 捕获后的决策菜单

文档化成功后提供选项并等待用户回复：

```
洞察已记录。

文件创建：
- knowledge/[category]/[filename].md

下一步操作：
1. 继续进行（推荐）
2. 添加到 Critical Pattern - 升级到 critical-patterns.md
3. 关联相关文档 - 与相似洞察交叉引用
4. 添加到现有技能 - 连接到 .claude/skills/
5. 查看文档 - 查看创建的内容

选择: _
```

**各选项处理：**

**Option 1: 继续进行**

- 返回当前工作/工作流
- 完成文档化

**Option 2: 添加到 Critical Pattern**

如果用户选择：
- 重复应用的模式
- 绝对不能忘记的教训
- 非直观但必要的规则

操作：
1. 从文档中提取模式
2. 基于 assets/critical-pattern-template.md 结构化
3. 添加到 `knowledge/patterns/critical-patterns.md`（保持顺序）
4. 在该文档中添加交叉引用
5. 确认： "已添加到 Critical Pattern"

**Option 3: 关联相关文档**

提示： "要关联哪个文档？ (文件名或主题描述)"
在 `knowledge/` 中搜索目标文档
添加双向交叉引用
确认： "已添加交叉引用"

**Option 4: 添加到现有技能**

提示： "要添加到哪个技能？"
在 `.claude/skills/[skill-name]/` 的适当文件中添加链接和说明
确认： "已添加到 [skill-name] 技能"

**Option 5: 查看文档**

显示创建的文档内容
再次显示 Decision Menu
</decision_gate>

---

<integration_protocol>

## 集成点

**触发器：**
- `/compound` 命令（主要接口）
- 对话中自动检测确认语句
- 工作流完成后手动调用

**调用技能/代理：**
- 无（terminal 技能 - 不委托给其他技能）

**Handoff 条件：**
调用前对话历史中必须有足够的上下文。
</integration_protocol>

---

<success_criteria>

## 成功标准

满足以下所有条件时文档化成功：

- YAML frontmatter 验证通过（所有必要字段、正确格式、有效 enum 值）
- 创建 `knowledge/[category]/[filename].md` 文件
- domain-component 映射与 schema.yaml 一致
- Context、What Worked、Why This Works 部分具体编写
- 发现相似文档时添加交叉引用
- 提供用户 Decision Menu 并确认操作

</success_criteria>

---

## 错误处理

**上下文不足：**

- 向用户询问缺失信息
- 在获取必要信息前禁止进行

**YAML 验证失败：**

- 显示具体错误项
- 使用修改后的值重试
- 阻止直到通过

**相似洞察模糊：**

- 显示所有候选
- 用户选择：新建文档 / 更新现有文档 / 分开关联

**类别映射不明确：**

- 提供建议的最近类别
- 确认后进行

---

## 执行指南

**必须做：**
- YAML frontmatter 验证（Step 5 validation gate 是 blocking 的）
- 验证 domain-component 映射的有效性
- 在写入文件前使用 `mkdir -p` 创建目录
- 上下文缺失时向用户提问并等待
- key_learning 必须可推广到其他情况

**绝对不能做：**
- 跳过 YAML 验证（validation gate 是 blocking 的）
- 使用模糊描述文档化（不可搜索）
- 文档化假设或未验证内容
- 自动升级 critical pattern（需要用户决定）

---

## 示例场景

**用户：** "在 Claude Code 中创建技能时，将示例放入 references/ 文件夹后，它更准确地执行了。下次也这样做。"

**技能激活：**

1. **触发检测：** "下次也这样做" → 自动激活
2. **上下文收集：**
   - domain: tool
   - insight_type: tool_discovery
   - component: claude-code
   - context: "在 Claude Code 技能编写时，与仅放置 SKILL.md 相比，在 references/ 文件夹中放置具体示例文件时，技能执行准确度显著提高"
   - key_learning: "AI 技能/提示编写时，与抽象指令相比，提供具体示例文件可提高执行准确度"
   - impact: high
   - tags: [claude-code, skill, references, accuracy, prompt-engineering]
3. **搜索现有文档：** 在 knowledge/tool-discoveries/ 搜索
4. **创建文件名：** `20260304-skill-references-improve-accuracy.md`
5. **YAML 验证：** 通过
6. **文档编写：** `knowledge/tool-discoveries/20260304-skill-references-improve-accuracy.md`
7. **交叉引用：** 无（无相似文档）

**输出：**

```
洞察已记录。

文件创建：
- knowledge/tool-discoveries/20260304-skill-references-improve-accuracy.md

下一步操作：
1. 继续进行（推荐）
2. 添加到 Critical Pattern - 升级到 critical-patterns.md
3. 关联相关文档 - 与相似洞察交叉引用
4. 添加到现有技能 - 连接到 .claude/skills/
5. 查看文档 - 查看创建的内容
```
