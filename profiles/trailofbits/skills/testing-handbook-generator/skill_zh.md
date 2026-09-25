# 测试手册技能生成器

从 Trail of Bits 测试手册生成和维护 Claude Code 技能。

## 使用场景

**在以下情况调用此技能：**
- 从手册内容创建新的安全测试技能
- 用户提到“测试手册”、“appsec.guide”，或询问技能生成
- 需要批量生成或刷新技能

**不要用于：**
- 一般安全测试问题（使用生成的技能）
- 非手册技能创建

## 手册位置

该技能需要测试手册仓库。有关详细信息，请参阅 [discovery.md](discovery.md)。

**快速参考：** 检查 `./testing-handbook`、`../testing-handbook`、`~/testing-handbook` → 询问用户 → 不得已时克隆。

**仓库：** `https://github.com/trailofbits/testing-handbook`

## 工作流程概述

```
Phase 0: 设置              Phase 1: 发现
┌─────────────────┐        ┌─────────────────┐
│ 定位手册 │   →    │ 分析手册│
│ - 查找或克隆 │        │ - 扫描章节 │
│ - 确认路径  │        │ - 分类类型│
└─────────────────┘        └─────────────────┘
         ↓                          ↓
Phase 3: 生成        Phase 2: 规划
┌─────────────────┐        ┌─────────────────┐
│ 两阶段生成    │   ←    │ 生成计划   │
│ 第1阶段：内容 │        │ - 新技能    │
│ 第2阶段：交叉引用 │        │ - 更新       │
│ - 写入到 gen/ │        │ - 向用户展示 │
└─────────────────┘        └─────────────────┘
         ↓
Phase 4: 测试           Phase 5: 最终化
┌─────────────────┐        ┌─────────────────┐
│ 验证技能 │   →    │ 生成后处理 │
│ - 运行验证器 │        │ - 更新 README │
│ - 测试激活│       │ - 更新交叉引用 │
│ - 修复问题    │        │ - 自我改进  │
└─────────────────┘        └─────────────────┘
```

## 范围限制

**仅修改以下位置：**
- `plugins/testing-handbook-skills/skills/[skill-name]/*` - 生成的技能（作为 testing-handbook-generator 的同级目录）
- `plugins/testing-handbook-skills/skills/testing-handbook-generator/*` - 自我改进
- 仓库根目录 `README.md` - 将生成的技能添加到表格

**永远不要修改或分析：**
- 其他插件 (`plugins/property-based-testing/`、`plugins/static-analysis/` 等)
- 此插件外的其他技能

不要扫描或拉入任何 `testing-handbook-skills/` 之外的技能。仅根据手册内容和它引用的资源生成技能。

## 快速参考

### 章节→技能类型映射

| 手册章节 | 技能类型 | 模板 |
|------------------|------------|----------|
| `/static-analysis/[tool]/` | 工具技能 | tool-skill.md |
| `/fuzzing/[lang]/[fuzzer]/` | 漏洞注入器技能 | fuzzer-skill.md |
| `/fuzzing/techniques/` | 技巧技能 | technique-skill.md |
| `/crypto/[tool]/` | 领域技能 | domain-skill.md |
| `/web/[tool]/` | 工具技能 | tool-skill.md |

### 技能候选信号

| 信号 | 表示 |
|--------|-----------|
| `_index.md` with `bookCollapseSection: true` | 主要工具/主题 |
| 编号文件 (00-、10-、20-) | 结构化内容 |
| `techniques/` 子章节 | 方法论内容 |
| `99-resources.md` 或 `91-resources.md` | 包含外部链接 |

### 排除信号

| 信号 | 操作 |
|--------|--------|
| frontmatter 中的 `draft: true` | 跳过章节 |
| 空目录 | 跳过章节 |
| 模板/占位符文件 | 跳过章节 |
| 仅GUI工具 (例如，`web/burp/`) | 跳过章节 (Claude无法操作GUI工具) |

## 决策树

**开始技能生成？**

```
├─ 需要分析手册并构建计划？
│  └─ 阅读：discovery.md
│     (手册分析方法论，计划格式)
│
├─ 启动技能生成代理？
│  └─ 阅读：agent-prompt.md
│     (完整提示模板，变量引用，验证清单)
│
├─ 生成特定技能类型？
│  └─ 阅读 适用模板：
│     ├─ 工具 (Semgrep, CodeQL) → templates/tool-skill.md
│     ├─ 漏洞注入器 (libFuzzer, AFL++) → templates/fuzzer-skill.md
│     ├─ 技巧 (harness, coverage) → templates/technique-skill.md
│     └─ 领域 (crypto, web) → templates/domain-skill.md
│
├─ 验证生成的技能？
│  └─ 运行：scripts/validate-skills.py
│     然后 阅读：testing.md 进行激活测试
│
├─ 生成后最终化？
│  └─ 查看：生成后任务下方
│     (更新主 README，更新技能交叉引用，自我改进)
│
└─ 从特定章节快速生成？
   └─ 使用上方快速参考，直接应用模板
```

## 两阶段生成（第3阶段）

生成使用**两阶段方法**来解决正向引用问题（技能引用其他尚未存在的技能）。

### 第1阶段：内容生成（并行）

并行生成所有技能**不包含**相关技能部分：

```
第1阶段 - 并行生成5个技能：
├─ 代理1：libfuzzer (漏洞注入器) → skills/libfuzzer/SKILL.md
├─ 代理2：aflpp (漏洞注入器) → skills/aflpp/SKILL.md
├─ 代理3：semgrep (工具) → skills/semgrep/SKILL.md
├─ 代理4：harness-writing (技巧) → skills/harness-writing/SKILL.md
└─ 代理5：wycheproof (领域) → skills/wycheproof/SKILL.md

每个代理使用：pass=1 (仅内容，相关技能部分留空)
```

**第1阶段代理：**
- 生成所有部分，除外 Related Skills
- 留下占位符：`## Related Skills\n\n<!-- PASS2: 在所有技能存在后填充 -->`
- 输出报告包含 `references: DEFERRED`

### 第2阶段：交叉引用填充（顺序）

所有第1阶段代理完成后，运行第2阶段填充相关技能：

```
第2阶段 - 填充交叉引用：
├─ 从 skills/*/SKILL.md 读取所有生成的技能名称
├─ 对于每个技能，根据以下内容确定相关技能：
│   ├─ discovery 中的 related_sections (手册结构)
│   ├─ 技能类型关系 (漏洞注入器 → 技巧)
│   └─ 内容中的明确提及
└─ 更新每个 SKILL.md 的 Related Skills 部分
```

**第2阶段过程：**
1. 收集所有生成的技能名称：`ls -d skills/*/SKILL.md`
2. 对于每个技能，使用 discovery 中的映射识别相关技能
3. 编辑每个 SKILL.md 替换占位符为实际链接
4. 验证交叉引用是否存在（无断链）

### 代理提示模板

参见 **[agent-prompt.md](agent-prompt.md)** 获取完整提示模板，包含：
- 变量替换参考（包括 `pass` 变量）
- 预写验证清单
- Hugo 代码块转换规则
- 行数拆分规则
- 错误处理指南
- 输出报告格式

### 收集结果

第1阶段后：聚合输出报告，验证所有技能已生成。
第2阶段后：运行验证器检查交叉引用。

### 处理代理失败

如果代理失败或生成无效输出：

| 失败类型 | 检测 | 恢复操作 |
|--------------|-----------|-----------------|
| 代理崩溃 | 无输出报告 | 使用相同输入重新运行单个代理 |
| 验证失败 | 输出报告显示错误 | 检查差距/警告，手动修补或重新运行 |
| 技能类型错误 | 内容与模板不匹配 | 使用修正的 `type` 参数重新运行 |
| 内容缺失 | 输出报告列出差缺 | 如果轻微则接受，或提供额外的 `related_sections` |
| 第2阶段断链 | 验证器显示缺失技能 | 检查是否被跳过，更新引用 |

**重要：** 不要因单个代理失败而重新运行整个并行批次。独立修复单个失败。

### 单个技能重新生成

要重新生成单个技能而不重新运行整个批次：

```
# 重新生成单个技能（仅第1阶段 - 内容）
"使用 testing-handbook-generator 从 {section_path} 章节重新生成 {skill-name} 技能"

# 示例：
"使用 testing-handbook-generator 从 fuzzing/c-cpp/10-libfuzzer 章节重新生成 libfuzzer 技能"
```

**重新生成工作流程：**
1. 重新阅读手册章节以获取最新内容
2. 应用适当模板
3. 写入到 `skills/{skill-name}/SKILL.md`（覆盖现有文件）
4. 仅针对该技能重新运行第2阶段以更新交叉引用
5. 对单个技能运行验证：`uv run scripts/validate-skills.py --skill {skill-name}`

## 输出位置

生成的技能写入到：

```
skills/[skill-name]/SKILL.md
```

每个技能获得自己的目录，以备将来可能的辅助文件（作为 testing-handbook-generator 的同级目录）。

## 质量检查清单

在交付生成的技能前：

- [ ] 所有手册章节分析（第1阶段）
- [ ] 在生成前向用户展示计划（第2阶段）
- [ ] 启动并行代理 - 每个技能一个（第3阶段）
- [ ] 按技能类型正确应用模板
- [ ] 验证器通过：`uv run scripts/validate-skills.py`
- [ ] 激活测试通过 - 参见 [testing.md](testing.md)
- [ ] 更新主 `README.md` 添加生成的技能表格
- [ ] 更新 `README.md` 技能交叉引用图
- [ ] 捕获自我改进笔记
- [ ] 通知用户总结

## 生成后任务

### 1. 更新主 README

生成技能后，更新仓库的主 `README.md` 以列出它们。

**格式：** 将生成的技能添加到与 `testing-handbook-skills` 相同的“可用插件”表格，直接位于 `testing-handbook-skills` 之后。使用纯文本 `testing-handbook-generator` 作为作者（无链接）。

**示例：**

```markdown
| 插件 | 描述 | 作者 |
|--------|-------------|--------|
| ... 其他插件 ... |
| [testing-handbook-skills](plugins/testing-handbook-skills/) | 从测试手册生成技能的元技能 | Paweł Płatek |
| [libfuzzer](plugins/testing-handbook-skills/skills/libfuzzer/) | 使用 libFuzzer 为 C/C++ 进行覆盖率引导的漏洞注入 | testing-handbook-generator |
| [aflpp](plugins/testing-handbook-skills/skills/aflpp/) | 使用 AFL++ 进行多核漏洞注入 | testing-handbook-generator |
| [semgrep](plugins/testing-handbook-skills/skills/semgrep/) | 快速静态分析以查找错误 | testing-handbook-generator |
```

### 2. 更新技能交叉引用

生成技能后，更新 `README.md` 的 **技能交叉引用** 部分以包含显示技能关系的 mermaid 图。

**过程：**
1. 读取每个生成的技能的 `SKILL.md` 并提取其 `## Related Skills` 部分
2. 使用技能类型分组（漏洞注入器、技巧、工具、领域）构建 mermaid 图
3. 基于相关技能关系添加边：
   - 实线箭头 (`-->`) 用于主要技巧依赖
   - 虚线箭头 (`-.->`) 用于替代工具建议
4. 替换 README.md 中的现有 mermaid 代码块

**边分类：**
| 关系 | 箭头样式 | 示例 |
|--------------|-------------|---------|
| 漏洞注入器 → 技巧 | `-->` | `libfuzzer --> harness-writing` |
| 工具 → 工具（替代） | `-.->` | `semgrep -.-> codeql` |
| 漏洞注入器 → 漏洞注入器（替代） | `-.->` | `libfuzzer -.-> aflpp` |
| 技巧 → 技巧 | `-->` | `harness-writing --> coverage-analysis` |

**验证：** 更新后，运行 `validate-skills.py` 验证所有引用的技能是否存在。

### 3. 自我改进

每次生成运行后，反思未来运行可以改进的地方。

**捕获改进以：**
- 模板（缺失部分，更好的结构）
- 发现逻辑（遗漏模式，误报）
- 内容提取（未处理的代码块，格式问题）

**更新过程：**
1. 记录生成过程中遇到的问题
2. 识别导致问题的模式
3. 更新相关文件：
   - `SKILL.md` - 工作流程、决策树、快速参考更新
   - `templates/*.md` - 模板改进
   - `discovery.md` - 检测逻辑更新
   - `testing.md` - 新验证检查
4. 在提交信息中记录改进

**示例自我改进：**
```
问题：libFuzzer 技能缺少清理器标志表格
修复：更新 templates/fuzzer-skill.md 以包含 ## 编译标志部分
```

## 示例用法

### 完整发现和生成

```
用户："从测试手册生成技能"

1. 定位手册（检查常见位置，询问用户，或克隆）
2. 阅读 discovery.md 了解方法论
3. 扫描 {handbook_path}/content/docs/
4. 构建候选列表并分类类型
5. 向用户展示计划
6. 批准后，使用适当模板生成每个技能
7. 验证生成的技能
8. 更新主 README.md 添加生成的技能表格
9. 从 Related Skills 部分更新 README.md 技能交叉引用图
10. 自我改进：记录模板/发现问题以供未来运行
11. 报告结果
```

### 单个章节生成

```
用户："为 libFuzzer 章节创建技能"

1. 阅读 /testing-handbook/content/docs/fuzzing/c-cpp/10-libfuzzer/
2. 识别类型：漏洞注入器技能
3. 阅读 templates/fuzzer-skill.md
4. 提取内容，应用模板
5. 写入到 skills/libfuzzer/SKILL.md
6. 验证并报告
```

## 小贴士

**要：**
- 始终在生成前展示计划
- 使用适用于技能类型的适当模板
- 精确保留代码块
- 生成后验证

**不要：**
- 无用户批准就生成
- 跳过非视频外部资源（使用 WebFetch）
- 获取视频URL（YouTube、Vimeo - 仅标题）
- 直接包含手册图片
- 跳过验证步骤
- 每个SKILL.md超过500行

---

**首次使用：** 从 [discovery.md](discovery.md) 了解手册分析过程。

**模板参考：** 查看 [templates/](templates/) 目录获取技能类型模板。

**验证：** 查看 [testing.md](testing.md) 了解质量保证方法论。
