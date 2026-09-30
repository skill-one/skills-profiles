---
name: memory-optimize
description: 在4个交互步骤中优化Claude代码内存文件：删除重复项、将规则迁移到CLAUDE.md/rules文件、压缩剩余条目、使用清理功能验证。典型减少：token数量减少30-50%。
---

插件：[kochetkov-ma/claude-brewcode](https://github.com/kochetkov-ma/claude-brewcode)

## 内存优化器

通过**4个交互步骤**优化 Claude Code **auto-memory** 文件：删除重复项、将规则迁移到正确的配置文件、压缩剩余条目、验证结果。
典型减少：内存文件中的**30–50%** token 数量。

Auto-memory 在会话间存储上下文于 `~/.claude/projects/**/memory/MEMORY.md`。
启用：`CLAUDE_CODE_DISABLE_AUTO_MEMORY=0` · 禁用：`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`

**优点：** 加载上下文更快 · 无重复规则 · 指令更清晰 · 降低 API 成本

**用法：**
```bash
/memory-optimize          # 无参数 — 启动 4 步交互工作流
```

> _技能文本为 LLM 消费而编写，并针对 token 效率进行优化。_

---

# 内存优化器

通过 4 个交互步骤优化 Claude Code 内存文件。

> **无 `context: fork`** — 必须在主对话中运行以生成代理。

## 第 0 步：加载上下文

1. 递归查找所有内存文件：`~/.claude/projects/**/memory/*.md`
2. 读取 `~/.claude/CLAUDE.md` 和项目 `CLAUDE.md`（如果存在）
3. 递归查找 `.claude/rules/*.md` — 读取所有项目规则
4. 递归查找 `~/.claude/rules/*.md` — 读取所有全局规则

构建上下文映射：
```
memory_files: [路径列表]
claude_md_sections: [章节列表]
rules_files: [包含内容的路径列表]
```

## 第 1 步：分析 — 删除重复项（交互式）

**目标：** 查找内存条目中与 CLAUDE.md 或规则中已存在的重复内容。

1. 生成 `Explore` 代理以交叉引用所有加载的文件
2. 识别以下条目：
   - 已存在于 CLAUDE.md 中的相同规则
   - 已存在于规则文件中的相同模式
   - 与 CLAUDE.md 冲突（CLAUDE.md 优先）
3. 显示分析结果：
   ```
   发现 X 个重复/冗余条目（占内存的 Y%）：
   | 条目 | 内存文件 | 已存在于 | 操作 |
   |-------|-------------|------------|--------|
   | "通过 Bash grep 搜索" | MEMORY.md:5 | rules/code-search.md | 删除 |
   ...
   ```
4. `AskUserQuestion`： "删除 X 个重复条目（占内存的 Y%）？这是安全的 — 内容存在于其他地方。"
   - 选项： "是，删除所有" / "逐个审查" / "跳过此步骤"
5. 如果批准，使用 `Edit` 工具应用删除

## 第 2 步：迁移 — 移至规则/CLAUDE.md（交互式）

**目标：** 识别更适合持久化配置文件的剩余内存条目。

决策树（针对每个条目）：
- 适用于所有项目 + 是规则/约束 → `~/.claude/rules/`
- 仅适用于此项目 + 是规则 → `.claude/rules/`
- 是架构决策 → 项目 `CLAUDE.md`
- 是跨会话可重用的事实/模式 → 保留在内存中

1. 显示分类结果：
   ```
   适合迁移的 X 个条目：
   | 条目 | 当前位置 | 目标 | 减少 |
   |-------|-----------------|--------|-----------|
   | "始终使用 BD_PLUGIN_ROOT" | MEMORY.md:12 | .claude/rules/brewdoc.md | 15 tokens |
   ...
   总计：X 个条目 → 保存约 Y tokens
   ```
2. `AskUserQuestion`： "将 X 个条目迁移到规则/CLAUDE.md？"
   - 选项： "是，迁移所有" / "逐个审查" / "跳过此步骤"
3. 如果批准：
   - 通过 `Edit` 创建/追加到目标规则文件
   - 通过 `Edit` 从内存中删除已迁移条目
   - 如果目标文件不存在，则创建它

## 第 3 步：压缩（交互式）

**目标：** 使用 LLM 高效的格式压缩剩余条目。

压缩技术：
- 散文 → 表格行
- 多个相关条目 → 单个表格
- 详细的描述 → 命令式单行
- 示例列表 → 模式 + 单个示例

1. 显示压缩预览：
   ```
   发现压缩机会：
   | 原始 | 优化后 | 节省 |
   |--------|-------|---------|
   | "当你需要...始终使用..." | "使用 X 为 Y" | 8 tokens |
   ...
   总计：约 Y% token 减少（约 Z tokens）
   ```
   显示 2-3 个具体的原始/优化示例。
2. `AskUserQuestion`： "压缩剩余内存？（约 Y% 减少）"
   - 选项： "是，压缩所有" / "跳过压缩"
3. 通过 `Edit` 应用压缩（按行号降序顺序以保留行号）

## 第 4 步：验证（自动）

**目标：** 验证最终状态并清理孤立的引用。

1. 生成 `reviewer` 代理进行验证：
   - 内存文件中无损坏的文件路径引用
   - 内存与 CLAUDE.md 之间无冲突
   - 内存文件是格式良好的 Markdown
2. 清理损坏的引用（使用 `Edit` 工具）
3. 检查孤立的内存文件（位于 `~/.claude/projects/**/memory/` 且无 MEMORY.md 引用的文件）
4. 报告孤立文件并询问是否删除

**最终报告：**
```markdown
## 内存优化完成

### 摘要
| 指标 | 之前 | 之后 | 保存 |
|--------|--------|-------|-------|
| 总条目 | X | Y | Z |
| 重复条目 | X | 0 | — |
| 迁移条目 | — | — | X |
| token 估计 | ~X | ~Y | ~Z (~P%) |

### 已做的更改
- 第 1 步：删除 X 个重复条目
- 第 2 步：将 X 个条目迁移到规则/CLAUDE.md
- 第 3 步：压缩 X 个条目（Y% 减少）
- 第 4 步：修复 X 个损坏引用，删除 X 个孤立文件

### 最终内存结构
{~/.claude/projects/.../memory/ 的目录列表}

---

**brewdoc 的一部分：** [brewcode](https://github.com/kochetkov-ma/claude-brewcode) — 文档工具：内存优化、Claude 安装文档、Markdown 转 PDF。
安装：`claude plugin marketplace add https://github.com/kochetkov-ma/claude-brewcode && claude plugin install brewdoc@claude-brewcode`
