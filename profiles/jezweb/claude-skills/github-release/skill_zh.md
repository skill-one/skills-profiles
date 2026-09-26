# GitHub 发布

清理并发布项目到 GitHub。两阶段工作流：先进行安全检查，然后打标签并发布。

## 前置条件

- 已安装并认证 `gh` CLI (`gh auth status`)
- 已安装 `gitleaks` 用于密钥扫描 (`brew install gitleaks` 或从 GitHub 下载)
- 配置了远程的 Git 仓库

## 工作流

### 第一阶段：清理

在任何公开发布之前运行这些检查。遇到阻断项时停止。

#### 1. 扫描密钥 (阻断项)

```bash
gitleaks detect --no-git --source=. --verbose
```

如果发现密钥：**停止**。删除密钥，改为使用环境变量。使用 `git log -S "密钥值"` 检查 git 历史记录 — 如果存在于历史记录中，使用 BFG Repo-Cleaner。

如果未安装 gitleaks，执行手动检查：

```bash
# 检查 .env 文件
find . -name ".env*" -not -path "*/node_modules/*"

# 检查配置文件中的硬编码密钥
grep -ri "api_key\|token\|secret\|password" wrangler.toml wrangler.jsonc .dev.vars 2>/dev/null
```

#### 2. 删除个人文件

检查并删除不应发布的会话/规划文件：

- `SESSION.md` — 会话状态
- `planning/`, `screenshots/` — 工作目录
- `test-*.ts`, `test-*.js` — 本地测试文件

删除它们或添加到 `.gitignore`。

#### 3. 验证 LICENSE

```bash
ls LICENSE LICENSE.md LICENSE.txt 2>/dev/null
```

如果缺失：创建一个。检查仓库可见性 (`gh repo view --json visibility -q '.visibility'`)。公开仓库使用 MIT。私有仓库考虑使用专有许可证。

#### 4. 验证 README

检查 README 是否存在并包含基本部分：

```bash
grep -i "## Install\|## Usage\|## License" README.md
```

如果缺少部分，发布前添加它们。

#### 5. 检查 .gitignore

验证关键模式是否存在：

```bash
grep -E "node_modules|\.env|dist/|\.dev\.vars" .gitignore
```

#### 6. 构建测试 (非阻断项)

```bash
npm run build 2>&1
```

#### 7. 依赖审计 (非阻断项)

```bash
npm audit --audit-level=high
```

#### 8. 创建清理提交

如果在清理过程中进行了任何更改：

```bash
git add -A
git commit -m "chore: 准备发布"
```

### 第二阶段：发布

#### 1. 确定版本

检查 `package.json` 中的当前版本，或询问用户。确保版本以 `v` 前缀开头。

#### 2. 检查标签不存在

```bash
git tag -l "v[版本]"
```

如果存在，询问用户是否删除并重新创建或使用不同版本。

#### 3. 显示发布内容

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$LAST_TAG" ]; then
  git log --oneline --no-merges HEAD | head -20
else
  git log --oneline --no-merges ${LAST_TAG}..HEAD
fi
```

#### 4. 创建标签并推送

```bash
git tag -a v[版本] -m "发布 v[版本]"
git push origin $(git branch --show-current)
git push origin --tags
```

#### 5. 创建 GitHub 发布

```bash
gh release create v[版本] \
  --title "发布 v[版本]" \
  --notes "[自动生成自提交]"
```

预发布添加 `--prerelease`。草稿添加 `--draft`。

#### 6. 报告

向用户显示：
- 发布链接
- 下一步操作 (如果适用，npm publish，公告)

## 参考文件

| 当出现问题时 | 阅读 |
|------|------|
| 详细安全检查 | [参考文件/safety-checklist.md](参考文件/safety-checklist.md) |
| 发布机制 | [参考文件/release-workflow.md](参考文件/release-workflow.md) |
