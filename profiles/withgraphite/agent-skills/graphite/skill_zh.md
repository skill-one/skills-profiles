# Graphite 功能

使用 Graphite (`gt`) 进行创建、导航和管理堆叠的拉取请求。

## 快速参考

| 我想... | 命令 |
|--------|------|
| 创建新的分支/PR | `gt create branch-name -m "message"` |
| 修改当前分支 | `gt modify -m "message"` |
| 向上导航堆栈 | `gt up` |
| 向下导航堆栈 | `gt down` |
| 跳转到堆栈顶部 | `gt top` |
| 跳转到堆栈底部 | `gt bottom` |
| 查看堆栈结构 | `gt ls` |
| 提交堆栈进行审查 | `gt submit --no-interactive` |
| 在主干上重置堆栈 | `gt restack` |
| 更改分支父级 | `gt track --parent <branch>` |
| 重命名当前分支 | `gt rename <new-name>` |
| 在堆栈中移动分支 | `gt move` |

---

## 好的 PR 的标准是什么？

按重要性大致降序排列：

- **原子性/封闭性** - 与其他更改独立；将通过 CI 并可以安全地单独部署
- **语义范围狭窄** - 仅对模块 X 进行更改，或在模块 X、Y、Z 中进行相同的更改
- **小的 diff** - （启发式算法）小的总 diff 行数

**不要担心创建过多的拉取请求。** 创建更多的拉取请求总是比创建较少的拉取请求更好。

**任何更改都不算太小：** 微小的 PR 允许中等/较大的 PR 更加清晰。

只要它们独立地通过构建，就始终主张创建更多的 PR。

---

## 分支命名规范

在堆栈中命名 PR 时，请遵循此语法：

`terse-stack-feature-name/terse-description-of-change`

例如，一个 4 PR 堆栈：

```
auth-bugfix/reorder-args
auth-bugfix/improve-logging
auth-bugfix/improve-documentation
auth-bugfix/handle-401-status-codes
```

---

## 创建堆栈

### 基本工作流程

1. 修改文件
2. 暂存更改：`git add <files>`
3. 创建分支：`gt create branch-name -m "commit message"`
4. 重复每个 PR 在堆栈中的步骤
5. 提交：`gt submit --no-interactive`

### 处理未跟踪的分支（与工作树常见）

在创建分支之前，检查当前分支是否被跟踪：

```bash
gt branch info
```

如果你看到 "ERROR: Cannot perform this operation on untracked branch"：

**选项 A（推荐）：临时跟踪，然后重新父级**
1. 跟踪当前分支：`gt track -p main`
2. 正常使用 `gt create` 创建你的堆栈
3. 创建所有分支后，将你的第一个新分支重新父级到 main：
   ```bash
   gt checkout <your-first-branch-of-your-stack>
   gt track -p main
   gt restack
   ```

**选项 B：暂存更改并从 main 开始**
1. `git stash`
2. `git checkout main && git pull`
3. 创建新分支并取消暂存：`git checkout -b temp-working && git stash pop`
4. 继续使用 `gt track -p main` 和 `gt create`

---

## 导航堆栈

```bash
# 向上移动一个分支（朝向堆栈顶部）
gt up

# 向下移动一个分支（朝向主干）
gt down

# 跳转到堆栈顶部
gt top

# 跳转到堆栈底部（主干上方的第一个分支）
gt bottom

# 查看完整的堆栈结构
gt ls
```

---

## 修改堆栈

### 修改当前分支

```bash
git add <files>
gt modify -m "updated commit message"
```

### 重新排序分支

使用 `gt move` 来重新排序堆栈中的分支。这比尝试使用 `gt create --insert` 更简单。

### 重新父级堆栈

如果你在功能分支上创建了一个堆栈，但希望它基于 main：

```bash
# 跳转到你的堆栈的第一个分支
gt checkout <first-branch>

# 将其父级更改为 main
gt track --parent main

# 重置整个堆栈
gt restack
```

### 重命名分支

```bash
gt rename new-branch-name
```

---

## 将提交重置为未暂存的更改

如果更改已经提交，但你希望以不同的方式重新堆栈它们：

```bash
# 重置最后一个提交，保留更改未暂存
git reset HEAD^

# 重置多个提交（例如，最后 2 个提交）
git reset HEAD~2

# 查看差异以了解你要处理的内容
git diff HEAD
```

---

## 提交前

### 验证堆栈是否以 main 为根

在运行 `gt submit` 之前，验证第一个 PR 是否以 `main` 为父级：

```bash
gt ls
```

如果第一个分支的父级不是 `main`：
```bash
gt checkout <first-branch>
gt track -p main
gt restack
```

### 运行验证

在创建每个 PR 后，运行适当的代码检查、构建和测试：

1. 参考项目的 CLAUDE.md 以获取特定命令
2. 如果验证失败，修复问题，暂存更改，并使用 `gt modify`

---

## 提交和更新 PR

### 提交堆栈

```bash
gt submit --no-interactive
```

### 更新 PR 描述

提交后，使用 `gh pr edit` 设置正确的标题和描述。

**重要提示：** 不要使用 Bash 带有 heredoc 的 PR 描述 - shell 脱逸会破坏 Markdown 表格、代码块等。相反：

1. 使用 `Write` 工具创建 `/tmp/pr-body.md`，其中包含完整的 Markdown 内容
2. 使用 `gh pr edit` 与 `--body-file`：

```bash
gh pr edit <PR_NUMBER> --title "stack-name: description" --body-file /tmp/pr-body.md
```

PR 描述必须包括：
- **堆栈上下文**：这个堆栈的更大目标是什么？
- **什么？**（对于小更改可选）：非常简洁，重点是什么而不是为什么
- **为什么？**：是什么促使了更改？为什么是这个解决方案？它如何适应堆栈？

**示例**（对于一个添加警告功能的 3-PR 堆栈的 PR）：

```markdown
## 堆栈上下文

这个堆栈在合并按钮上添加了一个警告，当用户绕过 GitHub 规则集时。

## 为什么？

可以绕过规则集的用户（通过组织管理员或团队成员资格）目前看不到他们正在绕过分支保护。这个 PR 将服务器绕过数据传递到前端警告（PR 2），以显示它。
```

---

## 故障排除

| 问题 | 解决方案 |
|------|--------|
| "Cannot perform this operation on untracked branch" | 首先运行 `gt track -p main` |
| 堆栈以错误的分支为父级 | 使用 `gt track -p main` 然后使用 `gt restack` |
| 需要重新排序 PR | 使用 `gt move` |
| 重置期间出现冲突 | 解决冲突，然后 `git rebase --continue` |
| 想要拆分 PR | 重置提交 (`git reset HEAD^`)，选择性地暂存，创建新分支 |
| 需要删除分支（非交互式） | `gt delete <branch> -f -q` |
| `gt restack` 撞到无关的冲突 | 使用有针对性的 `git rebase <target>`（见下文） |
| 重置中断在冲突中 | 检查文件是否已解决但未暂存，然后 `git add` + `git rebase --continue` |

---

## 高级：复杂堆栈中的手术式重置

在具有许多兄弟分支的深度嵌套堆栈中，`gt restack` 可能会有问题：
- 它会重置所有需要重置的分支，而不仅仅是你的堆栈
- 可能会在完全无关的分支中遇到冲突
- 是全有或全无 - 很难进行手术

### 何时使用 `git rebase` 而不是 `gt restack`

当您只想更新堆栈中的特定分支时使用直接 `git rebase`：
- `gt restack` 撞到无关的分支中的冲突
- 您需要在重置期间跳过过时的提交

### 目标重置工作流程

```bash
# 1. 检出您要重置的分支
git checkout my-feature-branch

# 2. 在目标上重置（例如，更新的父分支）
git rebase target-branch

# 3. 如果您遇到冲突：
#    - 在文件中解决冲突
#    - 暂存它：git add <file>
#    - 继续：git rebase --continue

# 4. 如果提交过时并应跳过：
git rebase --skip

# 5. 重置后，使用 gt modify 同步 Graphite 的跟踪
gt modify --no-edit
```

### 从中断的重置中恢复（上下文重置）

如果重置被中断（例如，Claude 会话超出了上下文）：

1. **检查状态：**
   ```bash
   git status
   # 查找 "interactive rebase in progress" 和 "Unmerged paths"
   ```

2. **阅读 "未合并" 文件** - 它们可能已经解决（没有冲突标记）

3. **如果已经解决，只需暂存并继续：**
   ```bash
   git add <resolved-files>
   git rebase --continue
   ```

4. **如果仍有冲突标记**，首先解决它们，然后暂存并继续

### 从堆栈中删除分支

```bash
# 删除分支（非交互式，即使未合并）
gt delete branch-to-delete -f -q

# 还删除所有子分支（上堆栈）
gt delete branch-to-delete -f -q --upstack

# 还删除所有祖先（下堆栈）
gt delete branch-to-delete -f -q --downstack
```

**标志：**
- `-f` / `--force`：即使未合并或关闭也删除
- `-q` / `--quiet`：意味着 `--no-interactive`，最小化输出

**删除中间分支后**，子分支会自动重置到父分支。如果您需要手动更新跟踪：
```bash
gt checkout child-branch
gt track --parent new-parent-branch
```
