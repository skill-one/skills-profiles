---
name: core-dynamic-skills
description: 动态 Rust crate 技能管理的内部命令支持。仅在 /sync-crate-skills、/clean-crate-skills 或 /update-crate-skill 明确调用时使用。
---

# 动态技能管理器

> **版本:** 2.1.0 | **最后更新:** 2025-01-27

根据项目依赖关系，按需生成特定于容器的技能。

## 概念

动态技能是：
- 在本地生成于 `~/.claude/skills/`
- 基于Cargo.toml依赖关系
- 使用docs.rs中的llms.txt创建
- 具有版本控制且可更新
- 不提交到rust-skills仓库

## 触发场景

### 打开时提示

当进入包含Cargo.toml的目录时：
1. 检测Cargo.toml（单个或工作区）
2. 解析依赖列表
3. 检查哪些容器缺少技能
4. 如果缺少： "发现X个缺少技能的依赖。立即同步？"
5. 如果确认：运行 `/sync-crate-skills`

### 手动命令

- `/sync-crate-skills` - 同步所有依赖
- `/clean-crate-skills [容器名]` - 删除技能
- `/update-crate-skill <容器名>` - 更新特定技能

## 执行模式检测

**关键：检查代理和命令基础设施是否可用。**

尝试读取：`../../agents/` 目录
检查 `/create-llms-for-skills` 和 `/create-skills-via-llms` 命令是否可用。

---

## 代理模式（插件安装）

**当完整插件基础设施可用时：**

### 架构

```
Cargo.toml
    ↓
解析依赖关系
    ↓
对于每个容器：
  ├─ 检查 ~/.claude/skills/{容器}/
  ├─ 如果缺少：检查actionbook中的llms.txt
  │     ├─ 找到：/create-skills-via-llms
  │     └─ 未找到：先运行 /create-llms-for-skills
  └─ 加载技能
```

### 工作流优先级

1. **actionbook MCP** - 检查预生成的llms.txt
2. **/create-llms-for-skills** - 从docs.rs生成llms.txt
3. **/create-skills-via-llms** - 从llms.txt创建技能

### 同步命令

```bash
/sync-crate-skills [--force]
```

1. 解析Cargo.toml中的依赖关系
2. 对于每个依赖：
   - 检查 `~/.claude/skills/{容器}/` 是否存在技能
   - 如果缺少（或 --force）：生成技能
3. 报告结果

---

## 内联模式（仅技能安装）

**当代理/命令基础设施不可用时，手动执行：**

### 第一步：解析Cargo.toml

```bash
# 读取依赖
cat Cargo.toml | grep -A 100 '\[dependencies\]' | grep -E '^[a-zA-Z]'
```

或使用Read工具解析Cargo.toml并提取：
- `[dependencies]` 部分
- `[dev-dependencies]` 部分（可选）
- 工作区成员（如果是工作区项目）

### 第二步：检查现有技能

```bash
# 列出现有技能
ls ~/.claude/skills/
```

将依赖与现有技能进行比较，查找缺失的技能。

### 第三步：生成缺失技能

对于每个缺失的容器：

```bash
# 1. 获取容器文档
agent-browser open "https://docs.rs/{容器}/latest/{容器}/"
agent-browser get text ".docblock"
# 保存内容

# 2. 创建技能目录
mkdir -p ~/.claude/skills/{容器}
mkdir -p ~/.claude/skills/{容器}/references

# 3. 创建 SKILL.md
# 使用rust-skill-creator内联模式的模板

# 4. 为关键模块创建参考文件
agent-browser open "https://docs.rs/{容器}/latest/{容器}/{模块}/"
agent-browser get text ".docblock"
# 保存到 ~/.claude/skills/{容器}/references/{模块}.md

agent-browser close
```

**WebFetch回退：**
```
WebFetch("https://docs.rs/{容器}/latest/{容器}/", "提取API文档概述、关键类型和使用示例")
```

### 第四步：工作区支持

对于Cargo工作区项目：

```bash
# 1. 解析根Cargo.toml以获取工作区成员
cat Cargo.toml | grep -A 10 '\[workspace\]'

# 2. 对于每个成员，解析其Cargo.toml
for member in members; do
  cat ${member}/Cargo.toml | grep -A 100 '\[dependencies\]'
done

# 3. 汇总和去重依赖
# 4. 为缺失的容器生成技能
```

### 清理命令（内联）

```bash
# 清理特定容器
rm -rf ~/.claude/skills/{容器名}

# 清理所有生成的技能
rm -rf ~/.claude/skills/*
```

### 更新命令（内联）

```bash
# 删除旧技能
rm -rf ~/.claude/skills/{容器名}

# 重新生成（与单个容器的同步相同）
# 按照上述步骤3为特定容器执行
```

---

## 本地技能目录

```
~/.claude/skills/
├── tokio/
│   ├── SKILL.md
│   └── references/
├── serde/
│   ├── SKILL.md
│   └── references/
└── axum/
    ├── SKILL.md
    └── references/
```

---

## 相关命令

- `/sync-crate-skills` - 主要同步命令
- `/clean-crate-skills` - 清理命令
- `/update-crate-skill` - 更新命令
- `/create-llms-for-skills` - 生成llms.txt（仅代理模式）
- `/create-skills-via-llms` - 从llms.txt创建技能（仅代理模式）

## 错误处理

| 错误 | 原因 | 解决方案 |
|-------|-------|----------|
| 命令未找到 | 仅技能安装 | 使用内联模式 |
| Cargo.toml未找到 | 不在Rust项目中 | 导航到项目根目录 |
| docs.rs不可用 | 网络问题 | 重试或跳过容器 |
| 权限被拒绝 | 目录问题 | 检查 ~/.claude/skills/ 权限 |
