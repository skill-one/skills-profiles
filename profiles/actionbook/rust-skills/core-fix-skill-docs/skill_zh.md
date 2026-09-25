# 修复技能文档

> **版本:** 2.1.0 | **最后更新:** 2025-01-27

检查并修复动态技能中缺失的引用文件。

## 使用方法

```
/fix-skill-docs [crate_name] [--check-only] [--remove-invalid]
```

**参数:**
- `crate_name`: 要检查的特定 crate (可选，默认检查所有)
- `--check-only`: 仅报告问题，不进行修复
- `--remove-invalid`: 删除无效引用而不是创建文件

## 执行模式检测

**关键: 检查代理基础设施是否可用。**

此技能可在两种模式下运行：
- **代理模式**: 使用后台代理进行文档获取
- **内联模式**: 直接使用 agent-browser CLI 或 WebFetch 执行

---

## 代理模式 (插件安装)

**当代理基础设施可用时，使用后台代理进行获取：**

### 说明

#### 1. 扫描技能目录

```bash
# 如果提供了 crate_name
skill_dir=~/.claude/skills/{crate_name}

# 否则扫描所有
for dir in ~/.claude/skills/*/; do
    # 处理每个技能
done
```

#### 2. 解析 SKILL.md 获取引用

从文档部分提取引用文件：

```markdown
## 文档
- `./references/file1.md` - 描述
```

#### 3. 检查文件是否存在

```bash
if [ ! -f "{skill_dir}/references/{filename}" ]; then
    echo "缺失: {filename}"
fi
```

#### 4. 报告状态

```
=== {crate_name} ===
SKILL.md: 正常
references/:
  - sync.md: 正常
  - runtime.md: 缺失

需要操作: 1 个文件缺失
```

#### 5. 修复缺失文件 (代理模式)

启动后台代理获取文档：

```
Task(
  subagent_type: "general-purpose",
  run_in_background: true,
  prompt: "从 docs.rs 获取 {crate_name}/{module} 的文档。
           使用 agent-browser CLI 导航到 https://docs.rs/{crate_name}/latest/{crate_name}/{module}/
           提取主要文档并保存到 ~/.claude/skills/{crate_name}/references/{module}.md"
)
```

---

## 内联模式 (仅技能安装)

**当代理基础设施不可用时，直接执行：**

### 第一步: 扫描技能目录

```bash
# 列出所有技能
ls ~/.claude/skills/

# 或检查特定技能
ls ~/.claude/skills/{crate_name}/
```

### 第二步: 解析 SKILL.md 获取引用

读取 SKILL.md 并提取所有 `./references/*.md` 模式：

```bash
# 使用 Read 工具
Read("~/.claude/skills/{crate_name}/SKILL.md")

# 查找类似以下行:
# - `./references/sync.md` - 同步原语
# - `./references/runtime.md` - 运行时配置
```

### 第三步: 检查文件是否存在

```bash
# 检查每个引用文件
for ref in references; do
  if [ ! -f "~/.claude/skills/{crate_name}/references/${ref}.md" ]; then
    echo "缺失: ${ref}.md"
  fi
done
```

### 第四步: 报告状态

输出格式：
```
=== {crate_name} ===
SKILL.md: 正常
references/:
  - sync.md: 正常
  - runtime.md: 缺失

需要操作: 1 个文件缺失
```

### 第五步: 修复缺失文件 (内联)

对每个缺失文件：

**使用 agent-browser CLI:**
```bash
agent-browser open "https://docs.rs/{crate_name}/latest/{crate_name}/{module}/"
agent-browser get text ".docblock"
# 将输出保存到 ~/.claude/skills/{crate_name}/references/{module}.md
agent-browser close
```

**使用 WebFetch 降级方案:**
```
WebFetch("https://docs.rs/{crate_name}/latest/{crate_name}/{module}/",
         "提取此模块的主要文档内容")
```

然后写入内容：
```bash
Write("~/.claude/skills/{crate_name}/references/{module}.md", <fetched_content>)
```

### 第六步: 更新 SKILL.md (如果 --remove-invalid)

如果设置了 `--remove-invalid` 标志且文件无法获取：

```bash
# 读取当前 SKILL.md
Read("~/.claude/skills/{crate_name}/SKILL.md")

# 删除无效引用行
Edit("~/.claude/skills/{crate_name}/SKILL.md",
     old_string="- `./references/{invalid_file}.md` - 描述",
     new_string="")
```

---

## 工具优先级

1. **agent-browser CLI** - 主要用于获取文档的工具
2. **WebFetch** - 如果 agent-browser 不可用时的降级方案
3. **Edit SKILL.md** - 用于删除无效引用 (--remove-invalid 仅限)

---

## 示例

### 检查所有技能 (--check-only)

```bash
/fix-skill-docs --check-only

# 输出:
=== tokio ===
SKILL.md: 正常
references/:
  - sync.md: 正常
  - runtime.md: 缺失
  - task.md: 正常

=== serde ===
SKILL.md: 正常
references/:
  - derive.md: 正常

摘要: 1 个文件缺失在 1 个技能中
```

### 修复特定 Crate

```bash
/fix-skill-docs tokio

# 从 docs.rs 获取缺失的 runtime.md
# 报告成功
```

### 删除无效引用

```bash
/fix-skill-docs tokio --remove-invalid

# 如果 runtime.md 无法获取:
# 将从 SKILL.md 中删除引用
```

---

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 代理不可用 | 仅技能安装 | 使用内联模式 |
| 技能目录为空 | 未安装技能 | 先运行 /sync-crate-skills |
| docs.rs 不可用 | 网络问题 | 重试或使用 --remove-invalid |
| 权限被拒绝 | 目录问题 | 检查 ~/.claude/skills/ 权限 |
| SKILL.md 格式无效 | 技能损坏 | 重新生成技能 |
