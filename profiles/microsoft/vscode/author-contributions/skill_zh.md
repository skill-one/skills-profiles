当被要求查找特定作者在某个分支（与主分支或其他上游分支相比）所贡献的所有文件时，请遵循以下步骤。目标是生成一个人类和大型语言模型（LLM）都能理解的简单表格。

## 作为子代理运行

这项技能涉及许多顺序执行的 git 命令。将其委托给具有如下提示的子代理：

> 查找作者 "全名" 在分支 `<branch>` 上相对于 `<upstream>` 所贡献的每个文件。通过文件重命名追踪贡献。返回一个 markdown 表格，列包括：状态（DIRECT 或 VIA_RENAME）、文件路径和行数（+/-）。在末尾包含一条总结行。

## 程序步骤

### 1. 确定作者的确切 git 身份

```bash
git log --format="%an <%ae>" <upstream>..<branch> | sort -u
```

将请求的人匹配到他们的确切 `--author=` 字符串。不要猜测——短用户名不会匹配全显示名称（通过 `git log` 或 GitHub MCP `get_me` 工具解决）。

### 2. 收集作者直接提交的所有文件

```bash
git log --author="<确切名称>" --format="%H" <upstream>..<branch>
```

对于每个提交哈希，提取被修改的文件：

```bash
git diff-tree --no-commit-id --name-only -r <哈希>
```

将所有结果合并为一个集合（`author_files`）。

### 3. 跨整个分支构建重命名映射

对于分支上的**每个**提交（不仅仅是作者的），提取重命名：

```bash
git diff-tree --no-commit-id -r -M <哈希>
```

解析状态为 `R` 的行来构建映射：`new_path → {old_paths}`。

### 4. 获取合并差异文件列表

```bash
git diff --name-only <upstream>..<branch>
```

这些是分支合并时实际会合并的文件。

### 5. 对合并差异中的每个文件进行分类

对于步骤 4 中的每个文件：
- 如果它在 `author_files` 中 → **DIRECT**
- 否则，递归地遍历重命名映射（跟随链：当前 → 旧 → 更旧）并检查任何祖先是否在 `author_files` 中 → **VIA_RENAME**
- 否则 → 不是这位作者的贡献

### 6. 获取差异统计

```bash
git diff --stat <upstream>..<branch> -- <file1> <file2> ...
```

### 7. 返回表格

将结果格式化为一个 markdown 表格：

```
| 状态 | 文件 | +/- |
|------|------|-----|
| DIRECT | src/vs/foo/bar.ts | +120/-5 |
| VIA_RENAME | src/vs/baz/qux.ts | +300 |
| ... | ... | ... |

**总计：N 个文件，+X/-Y 行**
```

## 重要提示

- **使用 Python 进行重体力劳动。** zsh 中的带内联注释的 Shell 循环会中断。编写一个临时的 `.py` 脚本，运行它，然后删除它。
- **作者匹配是精确的。** 始终首先运行步骤 1。`--author` 进行子字符串匹配，但你必须验证是否匹配了正确的人（例如，查找 "Josh S." 时不要匹配 "Joshua Smith"）。使用 GitHub MCP `get_me` 工具或 `git log` 输出来解决正确的全名。
- **重命名可以是多跳的。** 一个文件可能从 `contrib/chat/` → `agentSessions/` → `sessions/` 移动。必须递归地遍历重命名映射。
- **仅报告合并差异中的文件**（步骤 4）。作者触摸但后来完全删除的文件不应出现——它们不会合并到上游。
- **重命名映射必须包括所有作者提交**，而不仅仅是目标作者的提交。其他人经常执行重命名提交（例如，批量重构/移动）。

## 示例 Python 脚本

```python
import subprocess, os

os.chdir('<repo_root>')
UPSTREAM = 'main'
AUTHOR = '<作者名称>'  # 通过 `git log` 或 GitHub MCP `get_me` 解决

# 步骤 2：作者的文件
commits = subprocess.check_output(
    ['git', 'log', f'--author={AUTHOR}', '--format=%H', f'{UPSTREAM}..HEAD'],
    text=True).strip().split('\n')
author_files = set()
for h in (c for c in commits if c):
    files = subprocess.check_output(
        ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', h],
        text=True).strip().split('\n')
    author_files.update(f for f in files if f)

# 步骤 3：所有提交的重命名映射
all_commits = subprocess.check_output(
    ['git', 'log', '--format=%H', f'{UPSTREAM}..HEAD'],
    text=True).strip().split('\n')
rename_map = {}  # new_name → set(old_names)
for h in (c for c in all_commits if c):
    out = subprocess.check_output(
        ['git', 'diff-tree', '--no-commit-id', '-r', '-M', h],
        text=True, timeout=5).strip()
    for line in out.split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 3 and 'R' in parts[0]:
            rename_map.setdefault(parts[2], set()).add(parts[1])

# 步骤 4：合并差异
diff_files = subprocess.check_output(
    ['git', 'diff', '--name-only', f'{UPSTREAM}..HEAD'],
    text=True).strip().split('\n')

# 步骤 5：分类
results = []
for f in (x for x in diff_files if x):
    if f in author_files:
        results.append(('DIRECT', f))
    else:
        # 遍历重命名链
        chain, to_check = set(), [f]
        while to_check:
            cur = to_check.pop()
            if cur in chain:
                continue
            chain.add(cur)
            to_check.extend(rename_map.get(cur, []))
        chain.discard(f)
        if chain & author_files:
            results.append(('VIA_RENAME', f))

# 步骤 6：统计
if results:
    stat = subprocess.check_output(
        ['git', 'diff', '--stat', f'{UPSTREAM}..HEAD', '--'] +
        [f for _, f in results], text=True)
    print(stat)

# 步骤 7：表格
for kind, f in sorted(results, key=lambda x: x[1]):
    print(f'| {kind:12s} | {f} |')
print(f'\nTotal: {len(results)} files')
```

### 替代脚本

在遵循上述流程后，运行此脚本以交叉检查作者修改的文件与分支差异。你可以带或不带 `src/vs/sessions` 进行此操作。

```
AUTHOR=""

# 1. 查找分支上（不在主分支上）作者的提交
git log main...HEAD --author="$AUTHOR" --format="%H"

# 2. 获取所有这些提交中唯一被修改的文件，排除 src/vs/sessions/
git log main...HEAD --author="$AUTHOR" --format="%H" \
  | xargs -I{} git diff-tree --no-commit-id -r --name-only {} \
  | sort -u \
  | grep -v '^src/vs/sessions/'

# 3. 与分支差异交叉引用以仅保留与主分支相比仍被修改的文件
git log main...HEAD --author="$AUTHOR" --format="%H" \
  | xargs -I{} git diff-tree --no-commit-id -r --name-only {} \
  | sort -u \
  | grep -v '^src/vs/sessions/' \
  | while read f; do git diff main...HEAD --name-only -- "$f" 2>/dev/null; done \
  | sort -u
```
