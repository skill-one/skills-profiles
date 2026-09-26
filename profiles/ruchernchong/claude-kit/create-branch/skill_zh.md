## 语言规范

**根据项目推断语言风格：**
- 分析现有分支、提交信息以及文档以检测项目的语言变体（美式英语、英式英语等）
- 匹配项目中发现的拼写规范（例如，“synchronize”与“synchronise”、“center”与“centre”）
- 在分支名称和命令输出中保持与项目已建立的语言风格的一致性

---

# 创建分支命令

此命令创建并切换到一个新的git分支，具有智能验证和GitHub问题集成功能。

## 优先级：GitHub问题集成

**重要提示**：如果用户提供了一个问题编号（例如，“#123”、“123”或“issue 123”），始终优先使用GitHub CLI的问题开发工作流：

1. **检查GitHub CLI的可用性**：
   ```bash
   gh --version
   ```
   如果不可用，通知用户并回退到手动分支创建。

2. **验证问题是否存在**：
   ```bash
   gh issue view <问题编号>
   ```
   显示问题标题和状态以确认。

3. **创建链接到问题的分支**：
   ```bash
   gh issue develop <问题编号> -c
   ```
   - `-c` 标志自动切换到新创建的分支
   - GitHub会根据问题标题自动生成适当的分支名称
   - 分支与问题关联，以便更好地进行项目跟踪

4. **跳转到远程推送步骤**（下文第8步）

## 手动分支创建工作流

如果未提供问题编号，请遵循此工作流：

### 1. 检查仓库状态

```bash
git status
```

验证：
- 干净的工作目录或可接受的未提交更改
- 当前分支信息
- 是否处于git仓库中

### 2. 获取分支名称输入

询问用户所需的分支名称。接受任何格式的输入 - 命令将处理格式化和验证。

### 3. 自动检测并应用前缀

分析分支名称输入中的关键词，并自动添加适当的前缀：

- **feature/** - 关键词：“add”、“implement”、“create”、“new”、“feature”
- **bugfix/** - 关键词：“fix”、“bug”、“resolve”、“patch”、“repair”
- **hotfix/** - 关键词：“hotfix”、“urgent”、“critical”、“emergency”
- **chore/** - 关键词：“chore”、“refactor”、“update”、“upgrade”、“maintain”
- **docs/** - 关键词：“docs”、“documentation”、“readme”、“guide”

如果用户的输入以已识别的前缀（feature/、bugfix/等）开头，则保持不变。

### 4. 验证分支名称

应用全面验证：

#### 凯撒拼写风格强制执行
- 转换为小写
- 将空格和下划线替换为连字符
- 确保格式为：`prefix/kebab-case-name`

#### 字符验证
拒绝包含以下内容的分支名称：
- 空格（转换为连字符）
- 特殊字符：`~`、`^`、`:`、`?`、`*`、`[`、`]`、`\`、`@{`、`..`
- 控制字符或非ASCII字符（连字符和斜杠除外）
- 开头或结尾的斜杠或连字符

#### 长度验证
- 最小：3个字符（不包括前缀）
- 最大：100个字符（总计）

### 5. 检查重复

检查本地和远程分支：

```bash
# 检查本地分支
git branch --list "<branch-name>"

# 检查远程分支
git ls-remote --heads origin "<branch-name>"
```

如果分支存在：
- **本地**：提供切换到现有分支的选项
- **远程**：警告用户并建议使用其他名称
- **两者**：通知用户并询问是否要切换或选择不同名称

### 6. 确定基础分支

使用智能默认值：

1. 检查是否存在`main`：
   ```bash
   git rev-parse --verify main
   ```

2. 如果不存在，检查是否存在`master`：
   ```bash
   git rev-parse --verify master
   ```

3. 如果两者都不存在，使用当前HEAD

4. 如果需要，允许用户指定不同的基础分支（在创建前询问）

### 7. 创建并切换分支

```bash
git checkout -b <已验证的分支名称> <基础分支>
```

用显示以下信息的消息确认成功创建：
- 分支名称
- 使用的基础分支
- 当前状态

### 8. 远程推送建议

询问用户：“您是否希望将此分支推送到远程并设置跟踪？”

如果同意：
```bash
git push -u origin <branch-name>
```

这将启用：
- 分支的远程备份
- 与团队成员的协作
- GitHub PR创建工作流
- GitHub UI中的分支可见性

## 错误处理

提供清晰、可操作的错误消息：

- **不是git仓库**：“此目录不是git仓库。使用`git init`初始化一个或导航到仓库。”
- **GitHub CLI不可用**：“GitHub CLI (`gh`)未安装。从https://cli.github.com安装它或使用手动分支创建。”
- **问题未找到**：“问题#123未找到。检查问题编号或手动创建分支。”
- **无效的分支名称**：“分支名称包含无效字符。建议：`feature/valid-branch-name`”
- **分支已存在**：“分支`feature/existing`已存在。使用`git checkout feature/existing`切换到它或选择不同名称。”
- **网络问题**：“无法检查远程分支。仅进行本地创建。”

## 示例

### 示例1：GitHub问题集成
```
用户：“为问题#456创建一个分支”
命令：gh issue view 456
输出：#456 - 添加用户认证（打开）
命令：gh issue develop 456 -c
输出：已创建并切换到分支：feature/456-add-user-authentication
```

### 示例2：手动自动前缀
```
用户：“创建分支：修复登录bug”
分析：包含“fix”→ 应用“bugfix/”前缀
验证：`bugfix/login-bug`
命令：git checkout -b bugfix/login-bug main
```

### 示例3：自定义前缀
```
用户：“创建分支：docs/update readme”
分析：已包含“docs/”前缀→ 保持不变
验证：`docs/update-readme`
命令：git checkout -b docs/update-readme main
```

## 最佳实践

1. **当提到问题编号时，始终优先使用GitHub问题工作流**
2. **在创建分支之前进行彻底验证，以避免git错误**
3. **使用描述性名称，清楚地表明目的**
4. **遵循团队规范** - 检查现有分支名称以查找模式
5. **尽早推送远程**以备份和协作
6. **尽可能将分支链接到问题**以更好地进行项目跟踪
