# GitHub CLI (gh)

GitHub CLI (gh) 的全面参考 - 从命令行无缝使用 GitHub。

**版本：** 2.85.0 (截至 2026 年 1 月的当前版本)

## 前置条件

### 安装

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Windows
winget install --id GitHub.cli

# 验证安装
gh --version
```

### 认证

```bash
# 交互式登录 (默认：github.com)
gh auth login

# 使用特定主机名登录
gh auth login --hostname enterprise.internal

# 使用令牌登录
gh auth login --with-token < mytoken.txt

# 检查认证状态
gh auth status

# 切换账户
gh auth switch --hostname github.com --user username

# 退出登录
gh auth logout --hostname github.com --user username
```

### 设置 Git 集成

```bash
# 配置 git 使用 gh 作为凭证辅助程序
gh auth setup-git

# 查看活动令牌
gh auth token

# 刷新认证范围
gh auth refresh --scopes write:org,read:public_key
```

## CLI 结构

```
gh                          # 根命令
├── auth                    # 认证
│   ├── login
│   ├── logout
│   ├── refresh
│   ├── setup-git
│   ├── status
│   ├── switch
│   └── token
├── browse                  # 在浏览器中打开
├── codespace               # GitHub 代码空间
│   ├── code
│   ├── cp
│   ├── create
│   ├── delete
│   ├── edit
│   ├── jupyter
│   ├── list
│   ├── logs
│   ├── ports
│   ├── rebuild
│   ├── ssh
│   ├── stop
│   └── view
├── gist                    # Gists
│   ├── clone
│   ├── create
│   ├── delete
│   ├── edit
│   ├── list
│   ├── rename
│   └── view
├── issue                   # Issues
│   ├── create
│   ├── list
│   ├── status
│   ├── close
│   ├── comment
│   ├── delete
│   ├── develop
│   ├── edit
│   ├── lock
│   ├── pin
│   ├── reopen
│   ├── transfer
│   ├── unlock
│   └── view
├── org                     # Organizations
│   └── list
├── pr                      # Pull Requests
│   ├── create
│   ├── list
│   ├── status
│   ├── checkout
│   ├── checks
│   ├── close
│   ├── comment
│   ├── diff
│   ├── edit
│   ├── lock
│   ├── merge
│   ├── ready
│   ├── reopen
│   ├── revert
│   ├── review
│   ├── unlock
│   ├── update-branch
│   └── view
├── project                 # Projects
│   ├── close
│   ├── copy
│   ├── create
│   ├── delete
│   ├── edit
│   ├── field-create
│   ├── field-delete
│   ├── field-list
│   ├── item-add
│   ├── item-archive
│   ├── item-create
│   ├── item-delete
│   ├── item-edit
│   ├── item-list
│   ├── link
│   ├── list
│   ├── mark-template
│   ├── unlink
│   └── view
├── release                 # Releases
│   ├── create
│   ├── list
│   ├── delete
│   ├── delete-asset
│   ├── download
│   ├── edit
│   ├── upload
│   ├── verify
│   ├── verify-asset
│   └── view
├── repo                    # 仓库
│   ├── create
│   ├── list
│   ├── archive
│   ├── autolink
│   ├── clone
│   ├── delete
│   ├── deploy-key
│   ├── edit
│   ├── fork
│   ├── gitignore
│   ├── license
│   ├── rename
│   ├── set-default
│   ├── sync
│   ├── unarchive
│   └── view
├── cache                   # Actions 缓存
│   ├── delete
│   └── list
├── run                     # Workflow 执行
│   ├── cancel
│   ├── delete
│   ├── download
│   ├── list
│   ├── rerun
│   ├── view
│   └── watch
├── workflow                # Workflows
│   ├── disable
│   ├── enable
│   ├── list
│   ├── run
│   └── view
├── agent-task              # Agent 任务
├── alias                   # 命令别名
│   ├── delete
│   ├── import
│   ├── list
│   └── set
├── api                     # API 请求
├── attestation             # Artifact 认证
│   ├── download
│   ├── trusted-root
│   └── verify
├── completion              # Shell 补全
├── config                  # 配置
│   ├── clear-cache
│   ├── get
│   ├── list
│   └── set
├── extension               # 扩展
│   ├── browse
│   ├── create
│   ├── exec
│   ├── install
│   ├── list
│   ├── remove
│   ├── search
│   └── upgrade
├── gpg-key                 # GPG 密钥
│   ├── add
│   ├── delete
│   └── list
├── label                   # 标签
│   ├── clone
│   ├── create
│   ├── delete
│   ├── edit
│   └── list
├── preview                 # 预览功能
├── ruleset                 # 规则集
│   ├── check
│   ├── list
│   └── view
├── search                  # 搜索
│   ├── code
│   ├── commits
│   ├── issues
│   ├── prs
│   └── repos
├── secret                  # 密钥
│   ├── delete
│   ├── list
│   └── set
├── ssh-key                 # SSH 密钥
│   ├── add
│   ├── delete
│   └── list
├── status                  # 状态概览
└── variable                # 变量
    ├── delete
    ├── get
    ├── list
    └── set
```

## 配置

### 全局配置

```bash
# 列出所有配置
gh config list

# 获取特定配置值
gh config list git_protocol
gh config get editor

# 设置配置值
gh config set editor vim
gh config set git_protocol ssh
gh config set prompt disabled
gh config set pager "less -R"

# 清除配置缓存
gh config clear-cache
```

### 环境变量

```bash
# GitHub 令牌 (用于自动化)
export GH_TOKEN=ghp_xxxxxxxxxxxx

# GitHub 主机名
export GH_HOST=github.com

# 禁用提示
export GH_PROMPT_DISABLED=true

# 自定义编辑器
export GH_EDITOR=vim

# 自定义分页器
export GH_PAGER=less

# HTTP 超时时间
export GH_TIMEOUT=30

# 自定义仓库 (覆盖默认值)
export GH_REPO=owner/repo

# 自定义 git 协议
export GH_ENTERPRISE_HOSTNAME=hostname
```

## 认证 (gh auth)

### 登录

```bash
# 交互式登录
gh auth login

# 基于 Web 的认证
gh auth login --web

# 使用剪贴板获取 OAuth 代码
gh auth login --web --clipboard

# 使用特定 git 协议
gh auth login --git-protocol ssh

# 使用自定义主机名 (GitHub 企业版)
gh auth login --hostname enterprise.internal

# 从标准输入登录令牌
gh auth login --with-token < token.txt

# 不安全存储 (明文)
gh auth login --insecure-storage
```

### 状态

```bash
# 显示所有认证状态
gh auth status

# 仅显示活动账户
gh auth status --active

# 显示特定主机名
gh auth status --hostname github.com

# 在输出中显示令牌
gh auth status --show-token

# JSON 输出
gh auth status --json hosts

# 使用 jq 过滤
gh auth status --json hosts --jq '.hosts | add'
```

### 切换账户

```bash
# 交互式切换
gh auth switch

# 切换到特定用户/主机
gh auth switch --hostname github.com --user monalisa
```

### 令牌

```bash
# 打印认证令牌
gh auth token

# 特定主机/用户的令牌
gh auth token --hostname github.com --user monalisa
```

### 刷新

```bash
# 刷新凭证
gh auth refresh

# 添加范围
gh auth refresh --scopes write:org,read:public_key

# 移除范围
gh auth refresh --remove-scopes delete_repo

# 重置为默认范围
gh auth refresh --reset-scopes

# 使用剪贴板
gh auth refresh --clipboard
```

### 设置 Git

```bash
# 设置 git 凭证辅助程序
gh auth setup-git

# 为特定主机设置
gh auth setup-git --hostname enterprise.internal

# 即使主机未知也强制设置
gh auth setup-git --hostname enterprise.internal --force
```

## 浏览 (gh browse)

```bash
# 在浏览器中打开仓库
gh browse

# 打开特定路径
gh browse script/
gh browse main.go:312

# 打开问题或 PR
gh browse 123

# 打开提交
gh browse 77507cd94ccafcf568f8560cfecde965fcfa63

# 使用特定分支打开
gh browse main.go --branch bug-fix

# 打开不同仓库
gh browse --repo owner/repo

# 打开特定页面
gh browse --actions       # Actions 标签页
gh browse --projects      # Projects 标签页
gh browse --releases      # Releases 标签页
gh browse --settings      # 设置页面
gh browse --wiki          # Wiki 页面

# 打印 URL 而不是打开
gh browse --no-browser
```

## 仓库 (gh repo)

### 创建仓库

```bash
# 创建新仓库
gh repo create my-repo

# 创建带描述
gh repo create my-repo --description "我的超棒项目"

# 创建公共仓库
gh repo create my-repo --public

# 创建私有仓库
gh repo create my-repo --private

# 创建带主页
gh repo create my-repo --homepage https://example.com

# 创建带许可证
gh repo create my-repo --license mit

# 创建带 gitignore
gh repo create my-repo --gitignore python

# 初始化为模板仓库
gh repo create my-repo --template

# 在组织内创建仓库
gh repo create org/my-repo

# 本地不克隆创建仓库
gh repo create my-repo --source=.

# 禁用问题
gh repo create my-repo --disable-issues

# 禁用 Wiki
gh repo create my-repo --disable-wiki
```

### 克隆仓库

```bash
# 克隆仓库
gh repo clone owner/repo

# 克隆到特定目录
gh repo clone owner/repo my-directory

# 使用不同分支克隆
gh repo clone owner/repo --branch develop
```

### 列出仓库

```bash
# 列出所有仓库
gh repo list

# 列出组织仓库
gh repo list owner

# 限制结果
gh repo list --limit 50

# 仅公共仓库
gh repo list --public

# 仅源仓库 (非分支)
gh repo list --source

# JSON 输出
gh repo list --json name,visibility,owner

# 表格输出
gh repo list --limit 100 | tail -n +2

# 使用 jq 过滤
gh repo list --json name --jq '.[].name'
```

### 查看仓库

```bash
# 查看仓库详情
gh repo view

# 查看特定仓库
gh repo view owner/repo

# JSON 输出
gh repo view --json name,description,defaultBranchRef

# 在浏览器中查看
gh repo view --web
```

### 编辑仓库

```bash
# 编辑描述
gh repo edit --description "新描述"

# 设置主页
gh repo edit --homepage https://example.com

# 更改可见性
gh repo edit --visibility private
gh repo edit --visibility public

# 启用/禁用功能
gh repo edit --enable-issues
gh repo edit --disable-issues
gh repo edit --enable-wiki
gh repo edit --disable-wiki
gh repo edit --enable-projects
gh repo edit --disable-projects

# 设置默认分支
gh repo edit --default-branch main

# 重命名仓库
gh repo rename new-name

# 归档仓库
gh repo archive
gh repo unarchive
```

### 删除仓库

```bash
# 删除仓库
gh repo delete owner/repo

# 无提示确认
gh repo delete owner/repo --yes
```

### 分支仓库

```bash
# 分支仓库
gh repo fork owner/repo

# 分支到组织
gh repo fork owner/repo --org org-name

# 分支后克隆
gh repo fork owner/repo --clone

# 分支的远程名称
gh repo fork owner/repo --remote-name upstream
```

### 同步分支

```bash
# 同步分支与上游
gh repo sync

# 同步特定分支
gh repo sync --branch feature

# 强制同步
gh repo sync --force
```

### 设置默认仓库

```bash
# 设置当前目录的默认仓库
gh repo set-default

# 明确设置默认值
gh repo set-default owner/repo

# 取消设置默认值
gh repo set-default --unset
```

### 仓库自动链接

```bash
# 列出自动链接
gh repo autolink list

# 添加自动链接
gh repo autolink add \
  --key-prefix JIRA- \
  --url-template https://jira.example.com/browse/<num>

# 删除自动链接
gh repo autolink delete 12345
```

### 仓库部署密钥

```bash
# 列出部署密钥
gh repo deploy-key list

# 添加部署密钥
gh repo deploy-key add ~/.ssh/id_rsa.pub \
  --title "生产服务器" \
  --read-only

# 删除部署密钥
gh repo deploy-key delete 12345
```

### Gitignore 和许可证

```bash
# 查看 gitignore 模板
gh repo gitignore

# 查看许可证模板
gh repo license mit

# 许可证带全名
gh repo license mit --fullname "John Doe"
```

## 问题 (gh issue)

### 创建问题

```bash
# 交互式创建问题
gh issue create

# 带标题创建问题
gh issue create --title "Bug: 登录不工作"

# 带标题和正文创建问题
gh issue create \
  --title "Bug: 登录不工作" \
  --body "重现步骤..."

# 从文件获取正文创建问题
gh issue create --body-file issue.md

# 带标签创建问题
gh issue create --title "修复 Bug" --labels bug,high-priority

# 带指派者创建问题
gh issue create --title "修复 Bug" --assignee user1,user2

# 在特定仓库创建问题
gh issue create --repo owner/repo --title "问题标题"

# 基于 Web 创建问题
gh issue create --web
```

### 列出问题

```bash
# 列出所有开放问题
gh issue list

# 列出所有问题 (包括已关闭)
gh issue list --state all

# 列出已关闭问题
gh issue list --state closed

# 限制结果
gh issue list --limit 50

# 按指派者过滤
gh issue list --assignee username
gh issue list --assignee @me

# 按标签过滤
gh issue list --labels bug,enhancement

# 按里程碑过滤
gh issue list --milestone "v1.0"

# 搜索/过滤
gh issue list --search "is:open is:issue label:bug"

# JSON 输出
gh issue list --json number,title,state,author

# 表格视图
gh issue list --json number,title,labels --jq '.[] | [.number, .title, .labels[].name] | @tsv'

# 显示评论数量
gh issue list --json number,title,comments --jq '.[] | [.number, .title, .comments]'

# 排序
gh issue list --sort created --order desc
```

### 查看问题

```bash
# 查看问题
gh issue view 123

# 带评论查看
gh issue view 123 --comments

# 在浏览器中查看
gh issue view 123 --web

# JSON 输出
gh issue view 123 --json title,body,state,labels,comments

# 查看特定字段
gh issue view 123 --json title --jq '.title'
```

### 编辑问题

```bash
# 交互式编辑
gh issue edit 123

# 编辑标题
gh issue edit 123 --title "新标题"

# 编辑正文
gh issue edit 123 --body "新描述"

# 添加标签
gh issue edit 123 --add-label bug,high-priority

# 移除标签
gh issue edit 123 --remove-label stale

# 添加指派者
gh issue edit 123 --add-assignee user1,user2

# 移除指派者
gh issue edit 123 --remove-assignee user1

# 设置里程碑
gh issue edit 123 --milestone "v1.0"
```

### 关闭/重新打开问题

```bash
# 关闭问题
gh issue close 123

# 带评论关闭问题
gh issue close 123 --comment "已修复于 PR #456"

# 重新打开问题
gh issue reopen 123
```

### 问题评论

```bash
# 添加评论
gh issue comment 123 --body "这看起来不错！"

# 编辑评论
gh issue comment 123 --edit 456789 --body "更新评论"

# 删除评论
gh issue comment 123 --delete 456789
```

### 问题状态

```bash
# 显示问题状态概览
gh issue status

# 特定仓库的状态
gh issue status --repo owner/repo
```

### 固定/取消固定问题

```bash
# 固定问题 (固定在仓库仪表板)
gh issue pin 123

# 取消固定问题
gh issue unpin 123
```

### 锁定/解锁问题

```bash
# 锁定对话
gh issue lock 123

# 带原因锁定
gh issue lock 123 --reason off-topic

# 解锁
gh issue unlock 123
```

### 转移问题

```bash
# 转移到另一个仓库
gh issue transfer 123 --repo owner/new-repo
```

### 删除问题

```bash
# 删除问题
gh issue delete 123

# 无提示确认
gh issue delete 123 --yes
```

### 开发问题 (草稿 PR)

```bash
# 从问题创建草稿 PR
gh issue develop 123

# 在特定分支创建
gh issue develop 123 --branch fix/issue-123

# 带基础分支创建
gh issue develop 123 --base main
```

## Pull Requests (gh pr)

### 创建 Pull Request

```bash
# 交互式创建 PR
gh pr create

# 带标题创建
gh pr create --title "功能：添加新功能"

# 带标题和正文创建
gh pr create \
  --title "功能：添加新功能" \
  --body "此 PR 添加..."

# 从模板填充正文
gh pr create --body-file .github/PULL_REQUEST_TEMPLATE.md

# 设置基础分支
gh pr create --base main

# 设置头分支（默认：当前分支）
gh pr create --head feature-branch

# 创建草稿 PR
gh pr create --draft

# 添加指派者
gh pr create --assignee user1,user2

# 添加审查者
gh pr create --reviewer user1,user2

# 添加标签
gh pr create --labels 增强,功能

# 关联到问题
gh pr create --issue 123

# 在特定仓库创建
gh pr create --repo owner/repo

# 创建后打开浏览器
gh pr create --web
```

### 列出 Pull Requests

```bash
# 列出开放的 PR
gh pr list

# 列出所有 PR
gh pr list --state all

# 列出已合并的 PR
gh pr list --state merged

# 列出已关闭（未合并）的 PR
gh pr list --state closed

# 按头分支筛选
gh pr list --head feature-branch

# 按基础分支筛选
gh pr list --base main

# 按作者筛选
gh pr list --author username
gh pr list --author @me

# 按指派者筛选
gh pr list --assignee username

# 按标签筛选
gh pr list --labels bug,增强

# 限制结果数量
gh pr list --limit 50

# 搜索
gh pr list --search "is:open is:pr label:需要审查"

# JSON 输出
gh pr list --json number,title,state,author,headRefName

# 显示检查状态
gh pr list --json number,title,statusCheckRollup --jq '.[] | [.number, .title, .statusCheckRollup[]?.status]'

# 排序
gh pr list --sort created --order desc
```

### 查看 Pull Request

```bash
# 查看 PR
gh pr view 123

# 带评论查看
gh pr view 123 --comments

# 在浏览器查看
gh pr view 123 --web

# JSON 输出
gh pr view 123 --json title,body,state,author,commits,files

# 查看差异
gh pr view 123 --json files --jq '.files[].path'

# 带 jq 查询查看
gh pr view 123 --json title,state --jq '"\(.title): \(.state)"'
```

### 检出 Pull Request

```bash
# 检出 PR 分支
gh pr checkout 123

# 指定分支名检出
gh pr checkout 123 --branch name-123

# 强制检出
gh pr checkout 123 --force
```

### 查看 Pull Request 差异

```bash
# 查看 PR 差异
gh pr diff 123

# 带颜色查看差异
gh pr diff 123 --color always

# 输出到文件
gh pr diff 123 > pr-123.patch

# 查看特定文件差异
gh pr diff 123 --name-only
```

### 合并 Pull Request

```bash
# 合并 PR
gh pr merge 123

# 指定合并方式
gh pr merge 123 --merge
gh pr merge 123 --squash
gh pr merge 123 --rebase

# 合并后删除分支
gh pr merge 123 --delete-branch

# 带注释合并
gh pr merge 123 --subject "合并 PR #123" --body "合并功能"

# 合并草稿 PR
gh pr merge 123 --admin

# 强制合并（跳过检查）
gh pr merge 123 --admin
```

### 关闭 Pull Request

```bash
# 关闭 PR（作为草稿，不合并）
gh pr close 123

# 带注释关闭
gh pr close 123 --comment "因...关闭..."
```

### 重新打开 Pull Request

```bash
# 重新打开已关闭的 PR
gh pr reopen 123
```

### 编辑 Pull Request

```bash
# 交互式编辑
gh pr edit 123

# 编辑标题
gh pr edit 123 --title "新标题"

# 编辑正文
gh pr edit 123 --body "新描述"

# 添加标签
gh pr edit 123 --add-label bug,增强

# 移除标签
gh pr edit 123 --remove-label 过期

# 添加指派者
gh pr edit 123 --add-assignee user1,user2

# 移除指派者
gh pr edit 123 --remove-assignee user1

# 添加审查者
gh pr edit 123 --add-reviewer user1,user2

# 移除审查者
gh pr edit 123 --remove-reviewer user1

# 标记为已准备好审查
gh pr edit 123 --ready
```

### 标记为已准备好审查

```bash
# 将草稿 PR 标记为已准备好
gh pr ready 123
```

### Pull Request 检查

```bash
# 查看 PR 检查
gh pr checks 123

# 实时监控检查
gh pr checks 123 --watch

# 设置监控间隔（秒）
gh pr checks 123 --watch --interval 5
```

### 在 Pull Request 上评论

```bash
# 添加评论
gh pr comment 123 --body "看起来不错！"

# 在特定行评论
gh pr comment 123 --body "修复这个问题" \
  --repo owner/repo \
  --head-owner owner --head-branch feature

# 编辑评论
gh pr comment 123 --edit 456789 --body "更新"

# 删除评论
gh pr comment 123 --delete 456789
```

### 审查 Pull Request

```bash
# 审查 PR（打开编辑器）
gh pr review 123

# 批准 PR
gh pr review 123 --approve --body "看起来不错！"

# 要求修改
gh pr review 123 --request-changes \
  --body "请修复这些问题"

# 在 PR 上评论
gh pr review 123 --comment --body "一些想法..."

# 忽略审查
gh pr review 123 --dismiss
```

### 更新分支

```bash
# 使用最新基础分支更新 PR 分支
gh pr update-branch 123

# 强制更新
gh pr update-branch 123 --force

# 使用合并策略
gh pr update-branch 123 --merge
```

### 锁定/解锁 Pull Request

```bash
# 锁定 PR 对话
gh pr lock 123

# 带原因锁定
gh pr lock 123 --reason 不相关

# 解锁
gh pr unlock 123
```

### 撤销 Pull Request

```bash
# 撤销已合并的 PR
gh pr revert 123

# 指定分支名撤销
gh pr revert 123 --branch revert-pr-123
```

### Pull Request 状态

```bash
# 显示 PR 状态概览
gh pr status

# 特定仓库的状态
gh pr status --repo owner/repo
```

## GitHub Actions

### Workflow Runs (gh run)

```bash
# 列出 workflow 运行
gh run list

# 列出特定 workflow
gh run list --workflow "ci.yml"

# 列出特定分支
gh run list --branch main

# 限制结果数量
gh run list --limit 20

# JSON 输出
gh run list --json databaseId,status,conclusion,headBranch

# 查看运行详情
gh run view 123456789

# 带详细日志查看运行
gh run view 123456789 --log

# 查看特定任务
gh run view 123456789 --job 987654321

# 在浏览器查看
gh run view 123456789 --web

# 实时监控运行
gh run watch 123456789

# 设置监控间隔
gh run watch 123456789 --interval 5

# 重新运行失败的运行
gh run rerun 123456789

# 重新运行特定任务
gh run rerun 123456789 --job 987654321

# 取消运行
gh run cancel 123456789

# 删除运行
gh run delete 123456789

# 下载运行产物
gh run download 123456789

# 下载特定产物
gh run download 123456789 --pattern "*.tar.gz"

# 下载到目录
gh run download 123456789 --dir ./downloads
```

### Workflows (gh workflow)

```bash
# 列出 workflows
gh workflow list

# 查看 workflow 详情
gh workflow view ci.yml

# 查看 workflow YAML
gh workflow view ci.yml --yaml

# 在浏览器查看
gh workflow view ci.yml --web

# 启用 workflow
gh workflow enable ci.yml

# 禁用 workflow
gh workflow disable ci.yml

# 手动运行 workflow
gh workflow run ci.yml

# 带输入运行 workflow
gh workflow run ci.yml \
  --raw-field \
  version="1.0.0" \
  environment="production"

# 从特定分支运行
gh workflow run ci.yml --ref develop
```

### Action Caches (gh cache)

```bash
# 列出缓存
gh cache list

# 列出特定分支的缓存
gh cache list --branch main

# 带限制列出缓存
gh cache list --limit 50

# 删除缓存
gh cache delete 123456789

# 删除所有缓存
gh cache delete --all
```

### Action Secrets (gh secret)

```bash
# 列出密钥
gh secret list

# 设置密钥（提示输入值）
gh secret set MY_SECRET

# 从环境变量设置密钥
echo "$MY_SECRET" | gh secret set MY_SECRET

# 为特定环境设置密钥
gh secret set MY_SECRET --env production

# 为组织设置密钥
gh secret set MY_SECRET --org orgname

# 删除密钥
gh secret delete MY_SECRET

# 从环境中删除密钥
gh secret delete MY_SECRET --env production
```

### Action Variables (gh variable)

```bash
# 列出变量
gh variable list

# 设置变量
gh variable set MY_VAR "some-value"

# 为环境设置变量
gh variable set MY_VAR "value" --env production

# 为组织设置变量
gh variable set MY_VAR "value" --org orgname

# 获取变量值
gh variable get MY_VAR

# 删除变量
gh variable delete MY_VAR

# 从环境中删除变量
gh variable delete MY_VAR --env production
```

## Projects (gh project)

```bash
# 列出项目
gh project list

# 列出属于用户的
gh project list --owner owner

# 打开项目
gh project list --open

# 查看项目
gh project view 123

# 查看项目项
gh project view 123 --format json

# 创建项目
gh project create --title "我的项目"

# 在组织内创建
gh project create --title "项目" --org orgname

# 带说明创建
gh project create --title "项目" --readme "说明"

# 编辑项目
gh project edit 123 --title "新标题"

# 删除项目
gh project delete 123

# 关闭项目
gh project close 123

# 复制项目
gh project copy 123 --owner target-owner --title "复制"

# 标记为模板
gh project mark-template 123

# 列出字段
gh project field-list 123

# 创建字段
gh project field-create 123 --title "状态" --datatype 单选

# 删除字段
gh project field-delete 123 --id 456

# 列出项目项
gh project item-list 123

# 创建项目项
gh project item-create 123 --title "新项目项"

# 将项目项添加到项目中
gh project item-add 123 --owner-owner --repo repo --issue 456

# 编辑项目项
gh project item-edit 123 --id 456 --title "更新标题"

# 删除项目项
gh project item-delete 123 --id 456

# 归档项目项
gh project item-archive 123 --id 456

# 链接项目项
gh project link 123 --id 456 --link-id 789

# 解除链接项目项
gh project unlink 123 --id 456 --link-id 789

# 在浏览器查看项目
gh project view 123 --web
```

## Releases (gh release)

```bash
# 列出发布
gh release list

# 查看最新发布
gh release view

# 查看特定发布
gh release view v1.0.0

# 在浏览器查看
gh release view v1.0.0 --web

# 创建发布
gh release create v1.0.0 \
  --notes "发布说明"

# 从文件创建发布
gh release create v1.0.0 --notes-file notes.md

# 指定目标分支创建发布
gh release create v1.0.0 --target main

# 创建草稿发布
gh release create v1.0.0 --draft

# 创建预发布
gh release create v1.0.0 --prerelease

# 带标题创建发布
gh release create v1.0.0 --title "版本 1.0.0"

# 上传发布文件
gh release upload v1.0.0 ./file.tar.gz

# 上传多个发布文件
gh release upload v1.0.0 ./file1.tar.gz ./file2.tar.gz

# 带标签上传（大小写敏感）
gh release upload v1.0.0 ./file.tar.gz --casing

# 删除发布
gh release delete v1.0.0

# 删除并清理标签
gh release delete v1.0.0 --yes

# 删除特定文件
gh release delete-asset v1.0.0 file.tar.gz

# 下载发布文件
gh release download v1.0.0

# 下载特定文件
gh release download v1.0.0 --pattern "*.tar.gz"

# 下载到目录
gh release download v1.0.0 --dir ./downloads

# 下载存档（zip/tar）
gh release download v1.0.0 --archive zip

# 编辑发布
gh release edit v1.0.0 --notes "更新说明"

# 验证发布签名
gh release verify v1.0.0

# 验证特定文件签名
gh release verify-asset v1.0.0 file.tar.gz
```

## Gists (gh gist)

```bash
# 列出 gists
gh gist list

# 列出所有 gists（包括私有）
gh gist list --public

# 限制结果数量
gh gist list --limit 20

# 查看 gist
gh gist view abc123

# 查看 gist 文件
gh gist view abc123 --files

# 创建 gist
gh gist create script.py

# 带描述创建 gist
gh gist create script.py --desc "我的脚本"

# 创建公开 gist
gh gist create script.py --public

# 创建多文件 gist
gh gist create file1.py file2.py

# 从标准输入创建 gist
echo "print('hello')" | gh gist create

# 编辑 gist
gh gist edit abc123

# 删除 gist
gh gist delete abc123

# 重命名 gist 文件
gh gist rename abc123 --filename old.py new.py

# 克隆 gist
gh gist clone abc123

# 克隆到目录
gh gist clone abc123 my-directory
```

## Codespaces (gh codespace)

```bash
# 列出 codespaces
gh codespace list

# 创建 codespace
gh codespace create

# 指定仓库创建 codespace
gh codespace create --repo owner/repo

# 指定分支创建 codespace
gh codespace create --branch develop

# 指定机器创建 codespace
gh codespace create --machine premiumLinux

# 查看 codespace 详情
gh codespace view

# SSH 进入 codespace
gh codespace ssh

# 带命令 SSH 进入 codespace
gh codespace ssh --command "cd /workspaces && ls"

# 在浏览器打开 codespace
gh codespace code

# 在 VS Code 打开
gh codespace code --codec

# 带路径打开 codespace
gh codespace code --path /workspaces/repo

# 停止 codespace
gh codespace stop

# 删除 codespace
gh codespace delete

# 查看日志
gh codespace logs

--tail 100

# 查看端口
gh codespace ports

# 转发端口
gh codespace cp 8080:8080

# 重建 codespace
gh codespace rebuild

# 编辑 codespace
gh codespace edit --machine standardLinux

# Jupyter 支持
gh codespace jupyter

# 在 codespace 之间复制文件
gh codespace cp file.txt :/workspaces/file.txt
gh codespace cp :/workspaces/file.txt ./file.txt
```

## Organizations (gh org)

```bash
# 列出组织
gh org list

# 列出用户的组织
gh org list --user username

# JSON 输出
gh org list --json login,name,description

# 查看组织
gh org view orgname

# 查看组织成员
gh org view orgname --json members --jq '.members[] | .login'
```

## Search (gh search)

```bash
# 搜索代码
gh search code "TODO"

# 在特定仓库搜索
gh search code "TODO" --repo owner/repo

# 搜索提交
gh search commits "fix bug"

# 搜索问题
gh search issues "label:bug state:open"

# 搜索 PRs
gh search prs "is:open is:pr review:required"

# 搜索仓库
gh search repos "stars:>1000 language:python"

# 限制结果数量
gh search repos "topic:api" --limit 50

# JSON 输出
gh search repos "stars:>100" --json name,description,stargazers

# 排序结果
gh search repos "language:rust" --order desc --sort stars

# 带扩展搜索
gh search code "import" --extension py

# 在浏览器搜索
gh search prs "is:open" --web
```

## Labels (gh label)

```bash
# 列出标签
gh label list

# 创建标签
gh label create bug --color "d73a4a" --description "某处出问题了"

# 带十六进制颜色创建标签
gh label create enhancement --color "#a2eeef"

# 编辑标签
gh label edit bug --name "bug报告" --color "ff0000"

# 删除标签
gh label delete bug

# 从仓库克隆标签
gh label clone owner/repo

# 指定仓库克隆标签
gh label clone owner/repo --repo target/repo
```

## SSH Keys (gh ssh-key)

```bash
# 列出 SSH 密钥
gh ssh-key list

# 添加 SSH 密钥
gh ssh-key add ~/.ssh/id_rsa.pub --title "我的笔记本电脑"

# 带类型添加密钥
gh ssh-key add ~/.ssh/id_ed25519.pub --type "authentication"

# 删除 SSH 密钥
gh ssh-key delete 12345

# 按标题删除密钥
gh ssh-key delete --title "我的笔记本电脑"
```

## GPG Keys (gh gpg-key)

```bash
# 列出 GPG 密钥
gh gpg-key list

# 添加 GPG 密钥
gh gpg-key add ~/.ssh/id_rsa.pub

# 删除 GPG 密钥
gh gpg-key delete 12345

# 按密钥 ID 删除
gh gpg-key delete ABCD1234
```

## Status (gh status)

```bash
# 显示状态概览
gh status

# 特定仓库的状态
gh status --repo owner/repo

# JSON 输出
gh status --json
```

## Configuration (gh config)

```bash
# 列出所有配置
gh config list

# 获取特定值
gh config get editor

# 设置值
gh config set editor vim

# 设置 git 协议
gh config set git_protocol ssh

# 清除缓存
gh config clear-cache

# 设置提示行为
gh config set prompt disabled
gh config set prompt enabled
```

## Extensions (gh extension)

```bash
# 列出已安装的扩展
gh extension list

# 搜索扩展
gh extension search github

# 安装扩展
gh extension install owner/extension-repo

# 从分支安装扩展
gh extension install owner/extension-repo --branch develop

# 升级扩展
gh extension upgrade extension-name

# 删除扩展
gh extension remove extension-name

# 创建新扩展
gh extension create my-extension

# 浏览扩展
gh extension browse

# 执行扩展命令
gh extension exec my-extension --arg value
```

## Aliases (gh alias)

```bash
# 列出别名
gh alias list

# 设置别名
gh alias set prview 'pr view --web'

# 设置 shell 别名
gh alias set co 'pr checkout' --shell

# 删除别名
gh alias delete prview

# 导入别名
gh alias import ./aliases.sh
```

## API 请求 (gh api)

```bash
# 发送 API 请求
gh api /user

# 使用方法的请求
gh api --method POST /repos/owner/repo/issues \
  --field title="Issue title" \
  --field body="Issue body"

# 带有请求头的请求
gh api /user \
  --header "Accept: application/vnd.github.v3+json"

# 分页请求
gh api /user/repos --paginate

# 原始输出（不格式化）
gh api /user --raw

# 在输出中包含请求头
gh api /user --include

# 静默模式（不显示进度输出）
gh api /user --silent

# 从文件中输入
gh api --input request.json

# 对响应进行 jq 查询
gh api /user --jq '.login'

# 从响应中获取字段
gh api /repos/owner/repo --jq '.stargazers_count'

# GitHub 企业版
gh api /user --hostname enterprise.internal

# GraphQL 查询
gh api graphql \
  -f query='
  {
    viewer {
      login
      repositories(first: 5) {
        nodes {
          name
        }
      }
    }
  }'
```

## 规则集 (gh ruleset)

```bash
# 列出规则集
gh ruleset list

# 查看规则集
gh ruleset view 123

# 检查规则集
gh ruleset check --branch feature

# 检查特定仓库
gh ruleset check --repo owner/repo --branch main
```

## 证明 (gh attestation)

```bash
# 下载证明
gh attestation download owner/repo \
  --artifact-id 123456

# 验证证明
gh attestation verify owner/repo

# 获取可信根
gh attestation trusted-root
```

## 补全 (gh completion)

```bash
# 生成 shell 补全
gh completion -s bash > ~/.gh-complete.bash
gh completion -s zsh > ~/.gh-complete.zsh
gh completion -s fish > ~/.gh-complete.fish
gh completion -s powershell > ~/.gh-complete.ps1

# 特定 shell 的说明
gh completion --shell=bash
gh completion --shell=zsh
```

## 预览 (gh preview)

```bash
# 列出预览功能
gh preview

# 运行预览脚本
gh preview prompter
```

## 代理任务 (gh agent-task)

```bash
# 列出代理任务
gh agent-task list

# 查看代理任务
gh agent-task view 123

# 创建代理任务
gh agent-task create --description "我的任务"
```

## 全局标志

| 标志                       | 描述                            |
| -------------------------- | -------------------------------------- |
| `--help` / `-h`            | 显示命令帮助                      |
| `--version`                | 显示 gh 版本                      |
| `--repo [HOST/]OWNER/REPO` | 选择另一个仓库                  |
| `--hostname HOST`          | GitHub 主机名                    |
| `--jq EXPRESSION`          | 过滤 JSON 输出                     |
| `--json FIELDS`            | 输出指定字段的 JSON              |
| `--template STRING`        | 使用 Go 模板格式化 JSON          |
| `--web`                    | 在浏览器中打开                    |
| `--paginate`               | 发送额外的 API 请求              |
| `--verbose`                | 显示详细输出                    |
| `--debug`                  | 显示调试输出                      |
| `--timeout SECONDS`        | 最大 API 请求持续时间           |
| `--cache CACHE`            | 缓存控制（默认，强制，绕过）     |

## 输出格式化

### JSON 输出

```bash
# 基本 JSON
gh repo view --json name,description

# 嵌套字段
gh repo view --json owner,name --jq '.owner.login + "/" + .name'

# 数组操作
gh pr list --json number,title --jq '.[] | select(.number > 100)'

# 复杂查询
gh issue list --json number,title,labels \
  --jq '.[] | {number, title: .title, tags: [.labels[].name]}'
```

### 模板输出

```bash
# 自定义模板
gh repo view \
  --template '{{.name}}: {{.description}}'

# 多行模板
gh pr view 123 \
  --template '标题: {{.title}}
作者: {{.author.login}}
状态: {{.state}}
'
```

## 常见工作流

### 从问题创建 PR

```bash
# 从问题创建分支
gh issue develop 123 --branch feature/issue-123

# 进行更改，提交，推送
git add .
git commit -m "修复问题 #123"
git push

# 创建链接到问题的 PR
gh pr create --title "修复 #123" --body "关闭 #123"
```

### 批量操作

```bash
# 关闭多个问题
gh issue list --search "label:stale" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue close {} --comment "作为过时关闭"

# 为多个 PR 添加标签
gh pr list --search "review:required" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh pr edit {} --add-label needs-review
```

### 仓库设置工作流

```bash
# 创建带初始设置的仓库
gh repo create my-project --public \
  --description "我的酷炫项目" \
  --clone \
  --gitignore python \
  --license mit

cd my-project

# 设置分支
git checkout -b develop
git push -u origin develop

# 创建标签
gh label create bug --color "d73a4a" --description "问题报告"
gh label create enhancement --color "a2eeef" --description "功能请求"
gh label create documentation --color "0075ca" --description "文档"
```

### CI/CD 工作流

```bash
# 运行工作流并等待
RUN_ID=$(gh workflow run ci.yml --ref main --jq '.databaseId')

# 监控运行
gh run watch "$RUN_ID"

# 完成后下载工件
gh run download "$RUN_ID" --dir ./artifacts
```

### 分叉同步工作流

```bash
# 分叉仓库
gh repo fork original/repo --clone

cd repo

# 添加上游远程
git remote add upstream https://github.com/original/repo.git

# 同步分叉
gh repo sync

# 或手动同步
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## 环境设置

### Shell 集成

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
eval "$(gh completion -s bash)"  # 或 zsh/fish

# 创建有用的别名
alias gs='gh status'
alias gpr='gh pr view --web'
alias gir='gh issue view --web'
alias gco='gh pr checkout'
```

### Git 配置

```bash
# 使用 gh 作为凭证助手
gh auth setup-git

# 设置 gh 为默认的仓库操作
git config --global credential.helper 'gh !gh auth setup-git'

# 或手动
git config --global credential.helper github
```

## 最佳实践

1. **认证**: 使用环境变量进行自动化

   ```bash
   export GH_TOKEN=$(gh auth token)
   ```

2. **默认仓库**: 设置默认值以避免重复

   ```bash
   gh repo set-default owner/repo
   ```

3. **JSON 解析**: 使用 jq 进行复杂的数据提取

   ```bash
   gh pr list --json number,title --jq '.[] | select(.title | contains("fix"))'
   ```

4. **分页**: 使用 --paginate 对于大型结果集

   ```bash
   gh issue list --state all --paginate
   ```

5. **缓存**: 使用缓存控制进行频繁访问的数据
   ```bash
   gh api /user --cache force
   ```

## 获取帮助

```bash
# 一般帮助
gh --help

# 命令帮助
gh pr --help
gh issue create --help

# 帮助主题
gh help formatting
gh help environment
gh help exit-codes
gh help accessibility
```

## 参考

- 官方手册: https://cli.github.com/manual/
- GitHub 文档: https://docs.github.com/en/github-cli
- REST API: https://docs.github.com/en/rest
- GraphQL API: https://docs.github.com/en/graphql
