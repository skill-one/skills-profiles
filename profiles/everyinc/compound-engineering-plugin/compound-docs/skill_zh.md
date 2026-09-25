# compound-docs 技能

**目的：** 自动化记录已解决的问题，构建基于分类组织的可搜索机构知识库（枚举验证的问题类型）。

## 概述

该技能在确认后立即捕获问题解决方案，创建结构化文档，作为未来会话的可搜索知识库。

**组织：** 单文件架构 - 每个问题在其症状分类目录中记录为一个 markdown 文件（例如，`docs/solutions/performance-issues/n-plus-one-briefs.md`）。文件使用 YAML 前置内容进行元数据和可搜索性。

---

<critical_sequence name="documentation-capture" enforce_order="strict">

## 7步流程

<step number="1" required="true">
### 第1步：检测确认

**自动触发后短语：**

- "那行了"
- "已修复"
- "现在正常了"
- "问题解决了"
- "那行了"

**或手动：** `/doc-fix` 命令

**仅限非平凡问题：**

- 需要多次调查的问题
- 耗时复杂的调试问题
- 非显而易见的解决方案
- 未来会话将受益

**跳过文档记录：**

- 简单的拼写错误
- 明显的语法错误
- 立即修正的琐碎修复
</step>

<step number="2" required="true" depends_on="1">
### 第2步：收集上下文

从对话历史中提取：

**必需信息：**

- **模块名称**：出现问题的模块或组件
- **症状**：可观察的错误/行为（精确的错误消息）
- **调查尝试**：什么没起作用以及原因
- **根本原因**：实际问题的技术解释
- **解决方案**：修复它的方法（代码/配置更改）
- **预防措施**：如何在未来避免

**环境细节：**

- Rails 版本
- 阶段（0-6 或实施后）
- 操作系统版本
- 文件/行引用

**阻断要求：** 如果关键上下文缺失（模块名称、精确错误、阶段或解决步骤），请要求用户并等待响应后再继续到第3步：

```
我需要一些详细信息来正确记录：

1. 哪个模块出现了这个问题？ [ModuleName]
2. 精确的错误消息或症状是什么？
3. 你处于哪个阶段？ (0-6 或实施后)

[用户提供详细信息后继续]
```
</step>

<step number="3" required="false" depends_on="2">
### 第3步：检查现有文档

在 `docs/solutions/` 中搜索类似问题：

```bash
# 通过错误消息关键词搜索
grep -r "exact error phrase" docs/solutions/

# 通过症状分类搜索
ls docs/solutions/[category]/
```

**如果找到类似问题：**

则提供决策选项：

```
找到类似问题：docs/solutions/[path]

下一步是什么？
1. 创建带交叉引用的新文档（推荐）
2. 更新现有文档（仅当根本原因相同）
3. 其他

选择 (1-3)： _
```

等待用户响应，然后执行所选操作。

**否则**（未找到类似问题）：

直接继续到第4步（无需用户交互）。
</step>

<step number="4" required="true" depends_on="2">
### 第4步：生成文件名

格式：`[sanitized-symptom]-[module]-[YYYYMMDD].md`

**清理规则：**

- 全部小写
- 空格替换为连字符
- 移除除连字符外的特殊字符
- 截断为合理长度（< 80 个字符）

**示例：**

- `missing-include-BriefSystem-20251110.md`
- `parameter-not-saving-state-EmailProcessing-20251110.md`
- `webview-crash-on-resize-Assistant-20251110.md`
</step>

<step number="5" required="true" depends_on="4" blocking="true">
### 第5步：验证 YAML 模式

**关键：** 所有文档都需要经过验证的 YAML 前置内容，并使用枚举验证。

<validation_gate name="yaml-schema" blocking="true">

**根据模式验证：**
加载 `schema.yaml` 并根据 [yaml-schema.md](./references/yaml-schema.md) 中定义的枚举值对问题进行分类。确保所有必需字段都存在且与允许值完全匹配。

**如果验证失败：**

```
❌ YAML 验证失败

错误：
- problem_type：必须是 schema 枚举值之一，得到 "compilation_error"
- severity：必须是 [critical, high, medium, low] 之一，得到 "invalid"
- symptoms：必须是包含 1-5 项的数组，得到字符串

请提供修正后的值。
```

**门禁执行：** 在 `schema.yaml` 中定义的所有验证规则通过之前，**不要**继续到第6步（创建文档）。

</validation_gate>
</step>

<step number="6" required="true" depends_on="5">
### 第6步：创建文档

**根据 problem_type 确定分类：** 使用 [yaml-schema.md](./references/yaml-schema.md) 中定义的分类映射（第49-61行）。

**创建文档文件：**

```bash
PROBLEM_TYPE="[从验证的 YAML]"
CATEGORY="[映射自 problem_type]"
FILENAME="[生成的文件名].md"
DOC_PATH="docs/solutions/${CATEGORY}/${FILENAME}"

# 如果需要，创建目录
mkdir -p "docs/solutions/${CATEGORY}"

# 使用 assets/resolution-template.md 中的模板写入文档
# （内容使用第2步收集的上下文和第5步验证的 YAML 前置内容填充）
```

**结果：**
- 分类目录中的单个文件
- 枚举验证确保分类一致性

**创建文档：** 使用 `assets/resolution-template.md` 的结构，用第2步收集的上下文和第5步验证的 YAML 前置内容填充。
</step>

<step number="7" required="false" depends_on="6">
### 第7步：交叉引用和关键模式检测

如果在第3步找到类似问题：

**更新现有文档：**

```bash
# 在类似文档中添加相关问题链接
echo "- See also: [$FILENAME]($REAL_FILE)" >> [similar-doc.md]
```

**更新新文档：**
已包含来自第6步的交叉引用。

**如果适用，更新模式：**

如果这代表一个常见模式（3个或更多类似问题）：

```bash
# 添加到 docs/solutions/patterns/common-solutions.md
cat >> docs/solutions/patterns/common-solutions.md << 'EOF'

## [模式名称]

**常见症状：** [描述]
**根本原因：** [技术解释]
**解决方案模式：** [通用方法]

**示例：**
- [链接到文档1]
- [链接到文档2]
- [链接到文档3]
EOF
```

**关键模式检测（可选的主动建议）：**

如果此问题有自动指示器表明它可能是关键的：
- 严重性：YAML 中的 `critical`
- 影响多个模块或基础阶段（阶段2或3）
- 非显而易见的解决方案

然后在决策菜单（第8步）中添加注释：
```
💡 这可能值得添加到必读内容（选项2）
```

但**永远不要自动提升**。用户通过决策菜单（选项2）决定。

**关键模式添加模板：**

当用户选择选项2（添加到必读内容）时，使用 `assets/critical-pattern-template.md` 中的模板来构建模式条目。根据 `docs/solutions/patterns/critical-patterns.md` 中现有模式的顺序进行编号。
</step>

</critical_sequence>

---

<decision_gate name="post-documentation" wait_for_user="true">

## 捕获后的决策菜单

成功记录后，提供选项并等待用户响应：

```
✓ 解决方案已记录

创建的文件：
- docs/solutions/[category]/[filename].md

下一步是什么？
1. 继续工作流（推荐）
2. 添加到必读内容 - 提升为关键模式（critical-patterns.md）
3. 链接相关问题 - 连接到类似问题
4. 添加到现有技能 - 添加到学习技能（例如，hotwire-native）
5. 创建新技能 - 提取到新的学习技能
6. 查看文档 - 查看捕获的内容
7. 其他
```

**处理响应：**

**选项1：继续工作流**

- 返回调用技能/工作流
- 文档记录完成

**选项2：添加到必读内容** ⭐ 关键模式的 PRIMARY 路径

当用户选择此选项时：
- 系统在不同模块中多次犯此错误
- 解决方案非显而易见但必须每次遵循
- 基础要求（Rails, Rails API, 线程等）

操作：
1. 从文档中提取模式
2. 格式化为 ❌ 错误 vs ✅ 正确，附带代码示例
3. 添加到 `docs/solutions/patterns/critical-patterns.md`
4. 添加回此文档的交叉引用
5. 确认： "✓ 添加到必读内容。所有子代理在代码生成前都会看到此模式。"

**选项3：链接相关问题**

- 提示： "链接哪个文档？（提供文件名或描述）"
- 在 docs/solutions/ 中搜索文档
- 在两个文档中添加交叉引用
- 确认： "✓ 添加了交叉引用"

**选项4：添加到现有技能**

当用户选择此选项时，记录的解决方案与现有学习技能相关：

操作：
1. 提示： "哪个技能？ (hotwire-native, 等等)"
2. 确定要更新的参考文件（resources.md, patterns.md 或 examples.md）
3. 在适当部分添加链接和简要描述
4. 确认： "✓ 添加到 [skill-name] 技能在 [file] 中"

示例：对于 Hotwire Native Tailwind 变体解决方案：
- 添加到 `hotwire-native/references/resources.md` 在 "Project-Specific Resources" 下
- 添加到 `hotwire-native/references/examples.md` 并链接到解决方案文档

**选项5：创建新技能**

当用户选择此选项时，解决方案代表一个新的学习领域开始：

操作：
1. 提示： "新技能应该叫什么名字？ (例如，stripe-billing, email-processing)"
2. 运行 `python3 .claude/skills/skill-creator/scripts/init_skill.py [skill-name]`
3. 创建初始参考文件并将此解决方案作为第一个示例
4. 确认： "✓ 创建了新的 [skill-name] 技能，并将此解决方案作为第一个示例"

**选项6：查看文档**

- 显示创建的文档
- 再次显示决策菜单

**选项7：其他**

- 询问他们想做什么

</decision_gate>

---

<integration_protocol>

## 集成点

**被调用：**
- /compound 命令（主要接口）
- 在对话中确认解决方案后手动调用
- 可以通过检测确认短语如 "那行了"、"已修复" 等触发

**调用：**
- 无（终端技能 - 不委托给其他技能）

**交接预期：**
在调用之前，对话历史中应包含所有记录文档所需的上下文。

</integration_protocol>

---

<success_criteria>

## 成功标准

当所有以下条件都满足时，文档记录成功：

- ✅ YAML 前置内容验证（所有必需字段，正确格式）
- ✅ 在 docs/solutions/[category]/[filename].md 中创建文件
- ✅ 枚举值与 schema.yaml 完全匹配
- ✅ 解决方案部分包含代码示例
- ✅ 如果找到相关问题，添加交叉引用
- ✅ 用户被提供决策菜单并确认操作

</success_criteria>

---

## 错误处理

**上下文缺失：**

- 要求用户提供缺失的详细信息
- 在提供关键信息之前不要继续

**YAML 验证失败：**

- 显示具体错误
- 提供使用修正值重试的机会
- BLOCK 直到有效

**类似问题歧义：**

- 显示多个匹配项
- 让用户选择：创建新文档、更新现有文档或作为重复链接

**模块不在模块文档中：**

- 警告但不要阻断
- 继续记录文档
- 建议： "如果不在那里，请将 [Module] 添加到模块文档中"

---

## 执行指南

**必须做：**
- 验证 YAML 前置内容（根据第5步验证门禁无效则 BLOCK）
- 从对话中提取精确的错误消息
- 在解决方案部分包含代码示例
- 在写入文件前创建目录 (`mkdir -p`)
- 如果关键上下文缺失，要求用户并等待

**必须不做：**
- 跳过 YAML 验证（验证门禁是阻塞的）
- 使用模糊描述（不可搜索）
- 省略代码示例或交叉引用

---

## 质量指南

**好的文档具有：**

- ✅ 精确的错误消息（从输出中复制粘贴）
- ✅ 具体的文件:行引用
- ✅ 可观察的症状（你看到的，不是解释）
- ✅ 记录失败的尝试（有助于避免错误路径）
- ✅ 技术解释（不仅是 "什么"，而且是 "为什么"）
- ✅ 代码示例（如果适用，前后对比）
- ✅ 预防指导（如何早期捕获）
- ✅ 交叉引用（相关问题）

**避免：**

- ❌ 模糊描述（"出了点问题"）
- ❌ 缺失技术细节（"修复了代码"）
- ❌ 无上下文（哪个版本？哪个文件？）
- ❌ 只有代码堆栈（解释为什么它有效）
- ❌ 无预防指导
- ❌ 无交叉引用

---

## 示例场景

**用户：** "那行了！N+1 查询已修复。"

**技能激活：**

1. **检测确认：** "那行了！" 触发自动调用
2. **收集上下文：**
   - 模块：Brief System
   - 症状：Brief 生成超过 5 秒，加载电子邮件线程时出现 N+1 查询
   - 失败尝试：添加分页（无效），检查后台作业性能
   - 解决方案：在 Brief 模型中添加 `includes(:emails)` 的 eager loading
   - 根本原因：缺少 eager loading 导致每个电子邮件线程单独进行数据库查询
3. **检查现有：** 未找到类似问题
4. **生成文件名：** `n-plus-one-brief-generation-BriefSystem-20251110.md`
5. **验证 YAML：**
   ```yaml
   module: Brief System
   date: 2025-11-10
   problem_type: performance_issue
   component: rails_model
   symptoms:
     - "N+1 query when loading email threads"
     - "Brief generation taking >5 seconds"
   root_cause: missing_include
   severity: high
   tags: [n-plus-one, eager-loading, performance]
   ```
   ✅ 有效
6. **创建文档：**
   - `docs/solutions/performance-issues/n-plus-one-brief-generation-BriefSystem-20251110.md`
7. **交叉引用：** 无需（未找到类似问题）

**输出：**

```
✓ 解决方案已记录

创建的文件：
- docs/solutions/performance-issues/n-plus-one-brief-generation-BriefSystem-20251110.md

下一步是什么？
1. 继续工作流（推荐）
2. 添加到必读内容 - 提升为关键模式（critical-patterns.md）
3. 链接相关问题 - 连接到类似问题
4. 添加到现有技能 - 添加到学习技能（例如，hotwire-native）
5. 创建新技能 - 提取到新的学习技能
6. 查看文档 - 查看捕获的内容
7. 其他
```

---

## 未来增强

**不在第7阶段范围内，但潜在：**

- 按日期范围搜索
- 按严重性筛选
- 基于标签的搜索界面
- 指标（最常见问题，解决时间）
- 导出为可共享格式（社区知识共享）
- 导入社区解决方案
