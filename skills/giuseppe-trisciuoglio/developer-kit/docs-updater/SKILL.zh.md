---
name: docs-updater
description: 通过分析当前分支与最后一个发布标签之间的git变更，提供自动化的文档更新。执行git diff分析以识别修改，然后按照Keep a Changelog标准更新README.md和CHANGELOG.md，并发现文档文件夹以进行上下文相关的更新。在准备发布、维护文档同步或创建pull request之前使用。在"update docs"、"update changelog"、"sync documentation"、"update readme"、"prepare release documentation"等操作时触发。
---

# 通用文档更新器

分析自最新发布标签以来的 git 变更，并更新应随这些变更而变化的文档文件。

## 概述

使用 git 历史记录来识别与发布相关的变更，然后更新 `README.md`、`CHANGELOG.md` 以及任何相关的文档文件夹。保持工作流程专注于明确用户审批、精确编辑和特定于存储库的文档结构。

## 何时使用

在以下情况下使用此技能：

- 准备发布说明或 `Unreleased` 变更日志更新
- 在功能工作完成后同步 `README.md` 或文档
- 在 PR 或发布之前审查自上次发布以来的变更

## 前置条件

开始之前，请验证以下条件是否满足：

```bash
# 验证我们是否在 git 仓库中
git rev-parse --git-dir

# 检查 git 标签是否存在
git tag --list | head -5

# 验证文档文件是否存在
test -f README.md || echo "README.md 未找到"
test -f CHANGELOG.md || echo "CHANGELOG.md 未找到"
```

如果不存在标签，请告知用户此技能至少需要一个发布标签进行比较。

## 说明

### 第一阶段：检测最后一个发布版本

**目标**：识别最新的已发布版本以进行比较。

**操作**：

1. 检测比较基线并显示它：

```bash
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

if [ -z "$LATEST_TAG" ]; then
    echo "未找到 git 标签。此技能至少需要一个发布标签。"
    echo "请先创建一个发布标签（例如，git tag -a v1.0.0 -m '初始发布'）"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
VERSION=$(echo "$LATEST_TAG" | sed -E 's/^[^0-9]*([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

echo "最新发布标签：$LATEST_TAG"
echo "检测到的版本：$VERSION"
echo "比较：$LATEST_TAG -> $CURRENT_BRANCH"
```

### 第二阶段：执行 Git 差分分析

**目标**：分析自上次发布到当前分支的所有变更。

**操作**：

1. 获取提交范围和统计信息：

```bash
# 获取标签和 HEAD 之间的提交数量
COMMIT_COUNT=$(git rev-list --count ${LATEST_TAG}..HEAD 2>/dev/null || echo "0")
echo "自 $LATEST_TAG 以来的提交：$COMMIT_COUNT"

# 获取文件变更统计信息
git diff --stat ${LATEST_TAG}..HEAD
```

2. 提取用于分析的提交信息：

```bash
# 获取范围内的所有提交信息
COMMITS=$(git log ${LATEST_TAG}..HEAD --pretty=format:"%h|%s|%b" --reverse)

# 显示提交以供审查
echo "$COMMITS"
```

3. 获取详细的文件变更：

```bash
# 获取已更改文件的列表
CHANGED_FILES=$(git diff --name-only ${LATEST_TAG}..HEAD)

# 显示添加/修改/删除状态以快速分类
git diff --name-status ${LATEST_TAG}..HEAD
```

4. 根据文件路径识别组件区域：

```bash
# 检测哪些组件/区域已更改
echo "$CHANGED_FILES" | grep -E "^plugins/" | cut -d'/' -f2 | sort -u
```

### 第三阶段：发现文档结构

**目标**：识别项目中所有相关的文档位置。

**操作**：

1. 查找标准文档文件夹：

```bash
# 检查常见的文档位置
DOC_FOLDERS=()

[ -d "docs" ] && DOC_FOLDERS+=("docs/")
[ -d "documentation" ] && DOC_FOLDERS+=("documentation/")
[ -d "doc" ] && DOC_FOLDERS+=("doc/")

# 查找特定于插件的文档
for plugin_dir in plugins/*/; do
    if [ -d "${plugin_dir}docs" ]; then
        DOC_FOLDERS+=("${plugin_dir}docs/")
    fi
done

echo "找到的文档文件夹："
printf '  - %s\n' "${DOC_FOLDERS[@]}"
```

2. 识别现有的文档文件：

```bash
# 检查标准的 doc 文件
DOC_FILES=()

[ -f "README.md" ] && DOC_FILES+=("README.md")
[ -f "CHANGELOG.md" ] && DOC_FILES+=("CHANGELOG.md")
[ -f "CONTRIBUTING.md" ] && DOC_FILES+=("CONTRIBUTING.md")
[ -f "docs/GUIDE.md" ] && DOC_FILES+=("docs/GUIDE.md")

echo "找到的文档文件："
printf '  - %s\n' "${DOC_FILES[@]}"
```

### 第四阶段：生成 CHANGELOG 更新

**目标**：按照 Keep a Changelog 标准创建分类的 changelog 条目。

**操作**：

1. 使用常规提交语义解析提交，并将它们映射到 Keep a Changelog 部分如 `Added`、`Changed`、`Fixed`、`Removed` 和 `Security`。

2. 读取现有的 CHANGELOG.md 以了解结构，然后按照 Keep a Changelog 格式生成新条目。

参见 `references/examples.md` 以获取详细的 bash 命令和 changelog 模板。

### 第五阶段：更新 README.md

**目标**：使用相关的高级变更更新主 README。

**操作**：

1. 读取当前的 README.md 以了解其结构
2. 识别需要更新的部分（功能列表、技能/代理、设置说明、版本引用）
3. 使用 Edit 工具应用更新：保留结构、保持语气、更新版本号

### 第六阶段：更新文档文件夹

**目标**：将变更传播到 docs/ 文件夹中的相关文档。

**操作**：

1. 对于每个找到的文档文件夹，检查是否有文件引用已更改的代码
2. 将已更改的文件映射到其文档
3. 生成更新：添加新功能文档、更新 API 引用、修复过时的示例

参见 `references/examples.md` 以获取详细的发现模式和更新策略。

### 第七阶段：展示变更以供审查

**目标**：在应用变更之前向用户展示将要更新的内容。

**操作**：

1. 展示拟议变更的摘要：

```markdown
## 拟议的文档更新

### 版本信息
- 以前的发布：$LATEST_TAG
- 当前分支：$CURRENT_BRANCH
- 分析的提交：$COMMIT_COUNT

### 要更新的文件
- [ ] CHANGELOG.md - 添加新的版本部分，包含分类变更
- [ ] README.md - 更新 [特定部分]
- [ ] docs/[特定文件] - 更新文档

### 变更摘要
**新增**：N 个新功能
**变更**：N 个修改
**修复**：N 个错误修复
**破坏性**：N 个破坏性变更
```

2. 通过 **AskUserQuestion** 向用户确认：

- 确认要更新的文件
- 询问是否应修改任何变更
- 获取继续的批准

### 第八阶段：应用文档更新

**目标**：写入批准的更新，然后验证它们是否正确应用。

**操作**：

1. 更新 CHANGELOG.md：

```bash
# 读取当前 changelog
CURRENT_CHANGELOG=$(cat CHANGELOG.md)

# 预先添加新部分
cat > CHANGELOG.md << 'EOF'
# Changelog

此项目所有值得注意的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
本项目遵循 [语义版本控制](https://semver.org/spec/v2.0.0.html)。

## [未发布]
[新内容放在这里]

[现有的其他 changelog]
EOF
```

2. 使用 Edit 工具更新 README.md：

- 对特定部分进行有针对性的编辑
- 保留整体结构
- 如适用，更新版本号

3. 更新文档文件：

```bash
# 对于需要更新的每个文档文件
# 使用 Edit 工具进行精确的更改
```

4. 验证应用的变更：

```bash
# 确认编辑后关键文件仍然存在
test -f CHANGELOG.md && echo "CHANGELOG.md 存在"
test -f README.md && echo "README.md 存在"

# 审查 markdown 变更的范围
git diff --stat -- '*.md'

# 检查实际写入的内容
git diff -- '*.md' | sed -n '1,240p'
```

5. 如果存储库已经定义了文档或 markdown 验证命令，请在完成前运行它们。

## 示例

### 示例 1：功能开发后的更新

**用户请求**："更新我刚刚添加的新功能的文档"

**输出**：
- 最新标签：v2.4.1 → 当前分支：develop
- 分析了 5 个提交
- 为新的 Spring Boot Actuator 技能生成了 CHANGELOG 条目
- 更新了 README.md 技能列表

### 示例 2：准备发布文档

**用户请求**："为 v2.5.0 发布准备文档"

**输出**：
- 自 v2.4.1 以来分析了 47 个提交
- 检测到 15 个功能、8 个修复、3 个破坏性变更
- 生成了完整的 CHANGELOG.md [2.5.0] 部分
- 更新了 README.md 和插件文档

### 示例 3：增量同步

**用户请求**："同步文档，我已进行了一些更改"

**输出**：
- 分析了 2 个提交
- 针对 github-issue-workflow 技能变更进行了集中的 CHANGELOG 更新
- 无需更新 README 或插件文档

参见 `references/examples.md` 以获取详细的会话记录和故障排除。

## 最佳实践

1. **写入前预览，写入后验证**：首先显示计划，然后在编辑后确认最终的 diff
2. **遵循 Keep a Changelog**：保持一致的 changelog 格式
3. **正确分类**：使用正确的分类（Added、Changed、Fixed 等）
4. **具体说明**：在 changelog 条目中包含插件/组件名称
5. **保留结构**：保持现有的文档结构和风格
6. **引用提交**：在有助于可追溯性时包含提交哈希
7. **处理破坏性变更**：使用迁移说明明确突出破坏性变更
8. **更新版本引用**：在文档中保持版本号一致

## 限制和警告

1. **需要 git 标签**：此技能仅在存储库至少有一个发布标签时才有效
2. **只读分析**：此技能分析变更但会请求写入
3. **需要手动审查**：生成的 changelog 条目应审查其准确性
4. **常规提交**：最好用于使用常规提交格式的项目
5. **不创建标签**：此技能更新文档但不创建发布标签
6. **不自动提交**：文档变更准备但不自动提交
7. **项目特定模式**：某些项目可能有自定义的 changelog 格式需要尊重
8. **文件路径**：所有文件路径使用正斜杠（Unix 风格）以实现跨平台兼容性
