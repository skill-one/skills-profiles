# index-knowledge

生成层级结构的 AGENTS.md 文件。根目录 + 基于复杂度评分的子目录。

## 使用方法

```
--create-new   # 读取现有 → 删除所有 → 从头重新生成
--max-depth=2  # 限制目录深度（默认：5）
```

默认：更新模式（修改现有 + 在必要时创建新文件）

---

## 工作流程（高层级）

1. **发现与分析**（并行执行）
   - 启动并行探索代理（一个消息中包含多个 Task 调用）
   - 主会话：bash 结构 + LSP 代码映射 + 读取现有的 AGENTS.md
2. **评分与决策** - 根据合并后的发现确定 AGENTS.md 的位置
3. **生成** - 先生成根目录，然后并行生成子目录
4. **审查** - 去重、精简、验证

<关键>
**TodoWrite 所有阶段。实时标记 in_progress → 完成。**
  
```
TodoWrite([
  { id: "discovery", content: "启动探索代理 + LSP 代码映射 + 读取现有", status: "pending", priority: "高" },
  { id: "scoring", content: "评分目录，确定位置", status: "pending", priority: "高" },
  { id: "generate", content: "生成 AGENTS.md 文件（根目录 + 子目录）", status: "pending", priority: "高" },
  { id: "review", content: "去重、验证、精简", status: "pending", priority: "中" }
])
```
</关键>

---

## 阶段 1：发现与分析（并行执行）

**将 "discovery" 标记为 in_progress。**

### 启动并行探索代理

一个消息中的多个 Task 调用并行执行。结果直接返回。

```
// 所有 Task 调用在一个消息中 = 并行执行

Task(
  description="项目结构",
  subagent_type="explore",
  prompt="项目结构：预测检测到的语言的 PREDICT 标准模式 → 仅报告偏差"
)

Task(
  description="入口点",
  subagent_type="explore",
  prompt="入口点：查找主文件 → 报告非标准组织"
)

Task(
  description="约定",
  subagent_type="explore",
  prompt="约定：查找配置文件 (.eslintrc, pyproject.toml, .editorconfig) → 报告项目特定规则"
)

Task(
  description="反模式",
  subagent_type="explore",
  prompt="反模式：查找 'DO NOT', 'NEVER', 'ALWAYS', 'DEPRECATED' 注释 → 列出禁止模式"
)

Task(
  description="构建/CI",
  subagent_type="explore",
  prompt="构建/CI：查找 .github/workflows, Makefile → 报告非标准模式"
)

Task(
  description="测试模式",
  subagent_type="explore",
  prompt="测试模式：查找测试配置、测试结构 → 报告独特约定"
)
```

<dynamic-agents>
**动态代理生成**：在 bash 分析后，根据项目规模生成额外的探索代理：

| 因素 | 阈值 | 额外代理 |
|------|------|----------|
| **总文件数** | >100 | 每 100 个文件 +1 |
| **总行数** | >10k | 每 10k 行 +1 |
| **目录深度** | ≥4 | 深度探索 +2 |
| **大文件（>500 行）** | >10 个 | 复杂度热点 +1 |
| **单体仓库** | 检测到 | 每个包/工作区 +1 |
| **多种语言** | >1 | 每种语言 +1 |

```bash
# 首先测量项目规模
total_files=$(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l)
total_lines=$(find . -type f \( -name "*.ts" -o -name "*.py" -o -name "*.go" \) -not -path '*/node_modules/*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
large_files=$(find . -type f \( -name "*.ts" -o -name "*.py" \) -not -path '*/node_modules/*' -exec wc -l {} + 2>/dev/null | awk '$1 > 500 {count++} END {print count+0}')
max_depth=$(find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' | awk -F/ '{print NF}' | sort -rn | head -1)
```

示例生成（所有在一个消息中 = 并行执行）：
```
// 500 个文件，50k 行，深度 6，15 个大文件 → 生成额外代理
Task(
  description="大文件分析",
  subagent_type="explore",
  prompt="大文件分析：查找文件 >500 行，报告复杂度热点"
)

Task(
  description="深度模块",
  subagent_type="explore",
  prompt="深度 4+ 的模块：查找隐藏模式，内部约定"
)

Task(
  description="跨切面",
  subagent_type="explore",
  prompt="跨切面关注：查找跨目录的共享工具"
)
// ... 更多基于计算
```
</dynamic-agents>

### 主会话：并行分析

**Task 代理执行时**，主会话执行：

#### 1. Bash 结构分析
```bash
# 目录深度 + 文件计数
find . -type d -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/venv/*' -not -path '*/dist/*' -not -path '*/build/*' | awk -F/ '{print NF-1}' | sort -n | uniq -c

# 每个目录的文件数（前 30）
find . -type f -not -path '*/\.*' -not -path '*/node_modules/*' | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -30

# 代码集中度按扩展名
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.go" -o -name "*.rs" \) -not -path '*/node_modules/*' | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -20

# 现有的 AGENTS.md / CLAUDE.md
find . -type f \( -name "AGENTS.md" -o -name "CLAUDE.md" \) -not -path '*/node_modules/*' 2>/dev/null
```

#### 2. 读取现有的 AGENTS.md
```
对于每个找到的现有文件：
  读取(filePath=file)
  提取：关键见解、约定、反模式
  存储在 EXISTING_AGENTS 映射中
```

如果 `--create-new`：首先读取所有现有文件（保留上下文）→ 然后删除所有 → 重新生成。

#### 3. LSP 代码映射（如果可用）
```
lsp_servers()  # 检查可用性

# 入口点（并行）
lsp_document_symbols(filePath="src/index.ts")
lsp_document_symbols(filePath="main.py")

# 关键符号（并行）
lsp_workspace_symbols(filePath=".", query="class")
lsp_workspace_symbols(filePath=".", query="interface")
lsp_workspace_symbols(filePath=".", query="function")

# 顶级导出的中心性
lsp_find_references(filePath="...", line=X, character=Y)
```

**LSP 回退**：如果不可用，依赖探索代理 + AST-grep。

**合并：bash + LSP + 现有 + Task 代理结果。标记 "discovery" 为 completed。**

---

## 阶段 2：评分与位置决策

**将 "scoring" 标记为 in_progress。**

### 评分矩阵

| 因素 | 权重 | 高阈值 | 来源 |
|------|------|--------|------|
| 文件计数 | 3x | >20 | bash |
| 子目录计数 | 2x | >5 | bash |
| 代码比率 | 2x | >70% | bash |
| 独特模式 | 1x | 有自己的配置 | explore |
| 模块边界 | 2x | 有 index.ts/__init__.py | bash |
| 符号密度 | 2x | >30 个符号 | LSP |
| 导出计数 | 2x | >10 个导出 | LSP |
| 引用中心性 | 3x | >20 个引用 | LSP |

### 决策规则

| 评分 | 操作 |
|------|------|
| **根 (.)** | 总是创建 |
| **>15** | 创建 AGENTS.md |
| **8-15** | 如果有独立领域则创建 |
| **<8** | 跳过（父目录覆盖） |

### 输出
```
AGENTS_LOCATIONS = [
  { path: ".", type: "root" },
  { path: "src/hooks", score: 18, reason: "高复杂度" },
  { path: "src/api", score: 12, reason: "独立领域" }
]
```

**标记 "scoring" 为 completed。**

---

## 阶段 3：生成 AGENTS.md

**将 "generate" 标记为 in_progress。**

### 根目录 AGENTS.md（完整处理）

```markdown
# 项目知识库

**生成时间：** {TIMESTAMP}
**提交：** {SHORT_SHA}
**分支：** {BRANCH}

## 概述
{1-2 句话：什么 + 核心栈}

## 结构
\`\`\`
{root}/
├── {dir}/    # {非明显用途仅}
└── {入口}
\`\`\`

## 去哪里查找
| 任务 | 位置 | 备注 |
|------|------|------|

## 代码映射
{从 LSP - 如果不可用或项目 <10 个文件则跳过}

| 符号 | 类型 | 位置 | 引用 | 角色 |

## 约定
{仅标准偏差}

## 反模式（此项目）
{明确禁止在此处}

## 独特风格
{项目特定}

## 命令
\`\`\`bash
{dev/test/build}
\`\`\`

## 备注
{陷阱}
```

**质量门**：50-150 行，无通用建议，无明显信息。

### 子目录 AGENTS.md（并行）

为每个位置启动通用代理（一个消息中 = 并行执行）：

```
// 所有在一个消息中 = 并行
Task(
  description="AGENTS.md for src/hooks",
  subagent_type="general",
  prompt="生成 AGENTS.md for: src/hooks
    - 原因：高复杂度
    - 最大 30-80 行
    - NEVER 重复父目录内容
    - 部分：OVERVIEW（1 行），STRUCTURE（如果 >5 个子目录），WHERE TO LOOK，CONVENTIONS（如果不同），ANTI-PATTERNS
    - 直接写入 src/hooks/AGENTS.md"
)

Task(
  description="AGENTS.md for src/api",
  subagent_type="general",
  prompt="生成 AGENTS.md for: src/api
    - 原因：独立领域
    - 最大 30-80 行
    - NEVER 重复父目录内容
    - 部分：OVERVIEW（1 行），STRUCTURE（如果 >5 个子目录），WHERE TO LOOK，CONVENTIONS（如果不同），ANTI-PATTERNS
    - 直接写入 src/api/AGENTS.md"
)
// ... 每个 AGENTS_LOCATIONS 条目一个 Task
```

**结果直接返回。标记 "generate" 为 completed。**

---

## 阶段 4：审查与去重

**将 "review" 标记为 in_progress。**

对于每个生成的文件：
- 移除通用建议
- 移除父目录重复
- 精简到大小限制
- 验证电文风格

**标记 "review" 为 completed。**

---

## 最终报告

```
=== index-knowledge 完成 ===

模式：{update | create-new}

文件：
  ✓ ./AGENTS.md (根目录，{N} 行)
  ✓ ./src/hooks/AGENTS.md ({N} 行)

分析目录数：{N}
创建 AGENTS.md：{N}
更新 AGENTS.md：{N}

层级：
  ./AGENTS.md
  └── src/hooks/AGENTS.md
```

---

## 反模式

- **静态代理计数**：必须根据项目规模/深度变化代理
- **顺序执行**：必须并行（一个消息中多个 Task 调用）
- **忽略现有**：即使 --create-new 也必须先读取现有
- **过度文档化**：不是每个目录都需要 AGENTS.md
- **冗余**：子目录永不重复父目录
- **通用内容**：移除适用于所有项目的任何内容
- **冗长风格**：电文风格或死亡
