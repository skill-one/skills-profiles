# Git 工作流

针对常见 Git 操作的引导式工作流，这些工作流受益于结构化的步骤。

## PR 准备

在准备拉取请求时：

1. **收集上下文**
   - `git log main..HEAD --oneline` — 列出分支上的所有提交
   - `git diff main...HEAD --stat` — 查看所有已更改的文件
   - `git status` — 检查未提交的工作

2. **草拟 PR 内容**
   - 标题：不超过 70 个字符，描述变更（不是分支名称）
   - 正文：总结“为什么”，列出关键变更，添加测试计划
   - 使用提交历史来编写摘要 — 不要依赖记忆

3. **推送并创建**
   ```bash
   git push -u origin HEAD
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## 摘要
   - ...

   ## 测试计划
   - [ ] ...

   🤖 由 [Claude Code](https://claude.com/claude-code) 自动生成
   EOF
   )"
   ```

4. **验证** — `gh pr view --web` 在浏览器中打开

## 分支清理

安全清理已合并的分支：

1. **切换到 main 并拉取最新**
   ```bash
   git checkout main && git pull
   ```

2. **列出已合并的分支**（排除 main/master/develop）
   ```bash
   git branch --merged main | grep -vE '^\*|main|master|develop'
   ```

3. **删除本地已合并的分支**
   ```bash
   git branch --merged main | grep -vE '^\*|main|master|develop' | xargs -r git branch -d
   ```

4. **修剪远程跟踪引用**
   ```bash
   git fetch --prune
   ```

5. **列出没有本地跟踪的远程分支**（可选）
   ```bash
   git branch -r --merged origin/main | grep -vE 'main|master|develop|HEAD'
   ```

## 合并冲突解决

当 PR 存在冲突时：

1. **评估冲突范围**
   ```bash
   git fetch origin
   git merge origin/main --no-commit --no-ff
   git diff --name-only --diff-filter=U  # 列出冲突的文件
   ```

2. **针对每个冲突的文件**，阅读文件并解决：
   - 如果变更在不同区域，保留两个变更
   - 如果架构上不兼容，优先采用 main 分支的方法，并在顶部重新应用 PR 的意图

3. **如果变基更干净**（提交较少，没有共享历史）：
   ```bash
   git rebase origin/main
   # 按提交解决冲突，然后：
   git rebase --continue
   ```

4. **如果变基很混乱**（冲突较多，架构差异）：
   - 中断：`git rebase --abort` 或 `git merge --abort`
   - 提取有用代码：`git show origin/branch:path/to/file > /tmp/extracted.txt`
   - 手动将变更应用到 main
   - 关闭原始 PR 并说明原因

5. **验证** — 运行测试，检查差异是否正确

## 单一代码库发布标签

在单一代码库中，将标签范围限定到包：

```bash
# ❌ 在单一代码库中模糊
git tag v2.1.0

# ✅ 限定到包
git tag contextbricks-v2.1.0
git push origin contextbricks-v2.1.0
```

模式：`{包名}-v{semver}`

## .gitignore-首次初始化

在创建新代码库时，始终在第一次 `git add` 之前创建 `.gitignore`：

```bash
cat > .gitignore << 'EOF'
node_modules/
.wrangler/
dist/
.dev.vars
*.log
.DS_Store
.env
.env.local
EOF

git init && git add . && git commit -m "Initial commit"
```

**如果 node_modules 已经被跟踪：**
```bash
git rm -r --cached node_modules/
git commit -m "从跟踪中移除 node_modules"
```

## 私有代码库许可证审计

在发布或共享私有代码库之前：

```bash
gh repo view --json visibility -q '.visibility'
```

如果 `PRIVATE`，确保：
- `LICENSE` 包含专有声明（不是 MIT/Apache）
- `package.json` 包含 `"license": "UNLICENSED"` 和 `"private": true`
- 没有 `CONTRIBUTING.md` 或 README 中的“欢迎贡献”
