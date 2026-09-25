# 使用 Conventional Commits 进行 Git 提交

## 概述

使用 Conventional Commits 规范创建标准化的、语义化的 git 提交。通过分析实际的 diff 来确定合适的类型、范围和消息。

## Conventional Commit 格式

```
<类型>[可选范围]: <描述>

[可选正文]

[可选页脚]
```

## 提交类型

| 类型       | 目的                        |
| ---------- | ------------------------------ |
| `feat`     | 新功能                      |
| `fix`      | 修复 Bug                    |
| `docs`     | 仅文档                      |
| `style`    | 格式化/样式（无逻辑变更）    |
| `refactor` | 代码重构（无功能/修复）      |
| `perf`     | 性能改进                    |
| `test`     | 添加/更新测试                |
| `build`    | 构建系统/依赖关系            |
| `ci`       | CI 配置变更                  |
| `chore`    | 维护/杂项                  |
| `revert`   | 撤销提交                    |

## 不兼容变更

```
# 在类型/范围后加感叹号
feat!: 移除已弃用的端点

# BREAKING CHANGE 页脚
feat: 允许配置扩展其他配置

BREAKING CHANGE: `extends` 键的行为已变更
```

## 工作流程

### 1. 分析 Diff

```bash
# 如果文件已暂存，使用暂存 diff
git diff --staged

# 如果没有暂存，使用工作区 diff
git diff

# 同时检查状态
git status --porcelain
```

### 2. 暂存文件（如果需要）

如果未暂存任何文件或想以不同的方式分组变更：

```bash
# 暂存特定文件
git add path/to/file1 path/to/file2

# 按模式暂存
git add *.test.*
git add src/components/*

# 交互式暂存
git add -p
```

**永远不要提交秘密信息** (.env, credentials.json, 私有密钥)。

### 3. 生成提交消息

通过分析 diff 确定：

- **类型**：这次变更是什么类型的？
- **范围**：受影响的区域/模块是什么？
- **描述**：对变更的一行总结（现在时态，祈使语气，<72 字符）

### 4. 执行提交

```bash
# 单行
git commit -m "<类型>[范围]: <描述>"

# 多行带正文/页脚
git commit -m "$(cat <<'EOF'
<类型>[范围]: <描述>

<可选正文>

<可选页脚>
EOF
)"
```

## 最佳实践

- 每个提交一个逻辑变更
- 使用现在时态：使用 "add" 而不是 "added"
- 使用祈使语气：使用 "fix bug" 而不是 "fixes bug"
- 引用问题：`Closes #123`, `Refs #456`
- 描述保持在 72 字符以内

## Git 安全协议

- 永远不要更新 git 配置
- 永远不要在没有明确请求的情况下运行破坏性命令（--force, hard reset）
- 永远不要跳过钩子（--no-verify）除非用户请求
- 永远不要强制推送至 main/master
- 如果提交因钩子失败，请修复并创建新的提交（不要 amend）
