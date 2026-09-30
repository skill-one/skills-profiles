---
name: gitlab-cli-skills
description: 全面的 GitLab CLI (glab) 命令参考和终端操作流程，适用于所有 GitLab 操作。当用户提及 GitLab CLI、glab 命令、GitLab 自动化、通过 CLI 管理 MR/问题、CI/CD 管道命令、Artifact Registry 令牌交换、仓库操作、身份验证设置或任何 GitLab 终端操作时使用。路由至专门子技能，包括身份验证、CI、MR、问题、发布、仓库等，以及 30 多个其他 glab 命令。触发条件为 glab、GitLab CLI、GitLab 命令、GitLab 终端、GitLab 自动化。
---

# GitLab CLI 技能

全面的 GitLab CLI (glab) 命令参考和工作流。

## 快速入门

```bash
# 首次设置
glab auth login

# 常见操作
glab mr create --fill              # 从当前分支创建 MR
glab issue create                  # 创建问题
glab ci view                       # 查看管道状态
glab repo view --web              # 在浏览器中打开仓库
```

## 多代理身份注意

当你希望不同的代理以不同的 GitLab 用户身份出现时，给每个代理一个自己的 GitLab 机器人/服务账户。同一 GitLab 用户上的多个个人访问令牌仍然作为同一个可见身份。

使用 **Actor 身份** 用于 actor 创建的 GitLab 评论、回复、批准和其他写入操作。仅在 GitLab 操作明确是代理自己的工作产品时才使用 **代理身份**。在第一次 GitLab 写入之前选择预期的可见 actor。

默认情况下将 shell 身份视为粘性且不安全。如果同一 shell/会话中之前源了另一个 env 文件，除非你故意切换并验证，否则 `glab` 可能仍然会以之前加载的身份写入。

一个实用的模式是每个 actor 一个 env 文件，例如 `~/.config/openclaw/env/gitlab-actor.env`、`~/.config/openclaw/env/gitlab-reviewer.env` 和 `~/.config/openclaw/env/gitlab-release.env`。将这些 env 文件放在版本控制之外，限制它们的权限（例如 `chmod 600`），注意备份暴露，并使用最低权限的机器人/服务账户令牌。在可重用的 shell 中，首先清除过时的 GitLab 认证变量或启动一个新的 shell。如果这些文件使用普通的 `KEY=value` 行，请在运行 `glab` 之前使用导出的变量加载它们：

```bash
unset GITLAB_TOKEN GITLAB_ACCESS_TOKEN OAUTH_TOKEN GITLAB_HOST
set -a
source ~/.config/openclaw/env/gitlab-<actor>.env
set +a
```

普通的 `source` 更新当前 shell，但可能不会将变量导出到子进程，例如 `glab`。如果令牌/主机变量没有被导出，`glab` 可能会静默地回退到来自活动全局 glab 配置文件的活动存储认证，这可能会使错误的账户看起来执行了操作。

### 任何 GitLab 写入前的必要预检查

在任何 GitLab 写入之前立即运行以下命令，包括 `glab mr note`、审查回复/批准以及任何 `glab api` `POST`/`PATCH`/`PUT`/`DELETE` 调用：

```bash
glab auth status --hostname "$GITLAB_HOST"
glab api --hostname "$GITLAB_HOST" user
```

这假设目标 actor env 文件为你要修改的 GitLab 实例设置了 `GITLAB_HOST`。在两个命令都清楚地显示在该主机上预期的可见 actor 之前不要写入。

### 错误身份修复

如果评论或回复是以错误身份发布的：

1. 停止发布。
2. 如果需要清理，删除错误的评论或回复。
3. `unset GITLAB_TOKEN GITLAB_ACCESS_TOKEN OAUTH_TOKEN GITLAB_HOST` 或启动一个新的 shell。
4. 使用 `set -a; source ...; set +a` 源入正确的 env 文件。
5. 重新运行 `glab auth status --hostname "$GITLAB_HOST"` 和 `glab api --hostname "$GITLAB_HOST" user`。
6. 以正确的 actor 重新发布。
7. 验证线程不再显示替代消息的错误可见作者。

如果错误身份的写入改变了状态，而不仅仅是评论或回复，不要将评论清理步骤视为足够的。像上面一样重新认证，然后在正确的 actor 和主机下使用匹配的 GitLab 逆转操作，例如取消批准 MR 或发送补偿的 `glab api --hostname "$GITLAB_HOST"` 变化以更改的确切资源。

## 技能组织

此技能通过 GitLab 域路由到专门的子技能。每个都是兄弟目录中的一个独立技能；打开它的 `SKILL.md` 获取详细信息。

**核心工作流：**
- [`glab-mr`](../glab-mr/SKILL.md) - 合并请求：创建、审查、批准、合并
- [`glab-issue`](../glab-issue/SKILL.md) - 问题：创建、列出、更新、关闭、评论
- [`glab-ci`](../glab-ci/SKILL.md) - CI/CD：管道、作业、日志、工件
- [`glab-repo`](../glab-repo/SKILL.md) - 仓库：克隆、创建、分支、管理

**项目管理：**
- [`glab-milestone`](../glab-milestone/SKILL.md) - 发布计划和里程碑跟踪
- [`glab-iteration`](../glab-iteration/SKILL.md) - Sprint/迭代管理
- [`glab-label`](../glab-label/SKILL.md) - 标签管理和组织
- [`glab-release`](../glab-release/SKILL.md) - 软件发布和版本控制
- [`glab-packages`](../glab-packages/SKILL.md) - 项目包注册表列出、过滤和通用包上传

**认证和配置：**
- [`glab-auth`](../glab-auth/SKILL.md) - 登录、注销、Docker 注册表认证
- [`glab-config`](../glab-config/SKILL.md) - CLI 配置和默认值
- [`glab-ssh-key`](../glab-ssh-key/SKILL.md) - SSH 密钥管理
- [`glab-gpg-key`](../glab-gpg-key/SKILL.md) - 用于提交签名的 GPG 密钥
- [`glab-token`](../glab-token/SKILL.md) - 个人和项目访问令牌
- [`glab-todo`](../glab-todo/SKILL.md) - 个人 GitLab 待办事项分类和完成

**CI/CD 管理：**
- [`glab-job`](../glab-job/SKILL.md) - 单个作业操作
- [`glab-schedule`](../glab-schedule/SKILL.md) - 定时管道和 cron 作业
- [`glab-variable`](../glab-variable/SKILL.md) - CI/CD 变量和密钥
- [`glab-securefile`](../glab-securefile/SKILL.md) - 用于管道的安全文件
- [`glab-runner`](../glab-runner/SKILL.md) - 运行器管理：列出、分配/取消分配、检查作业/管理器、暂停/取消暂停、删除
- [`glab-runner-controller`](../glab-runner-controller/SKILL.md) - 运行器控制器、范围和令牌管理（实验性，仅管理员）

**协作：**
- [`glab-user`](../glab-user/SKILL.md) - 用户配置文件和信息
- [`glab-snippet`](../glab-snippet/SKILL.md) - 代码片段（GitLab gist）
- [`glab-incident`](../glab-incident/SKILL.md) - 事件管理
- [`glab-workitems`](../glab-workitems/SKILL.md) - 工作项：任务、OKRs、关键结果、下一代史诗

**高级：**
- [`glab-api`](../glab-api/SKILL.md) - 直接 REST API 调用
- [`glab-artifact-registry`](../glab-artifact-registry/SKILL.md) - 实验性短期 Artifact 注册表令牌交换和访问检查
- [`glab-cluster`](../glab-cluster/SKILL.md) - Kubernetes 集群集成
- [`glab-container-registry`](../glab-container-registry/SKILL.md) - 容器注册表存储库和标签
- [`glab-dependency-firewall`](../glab-dependency-firewall/SKILL.md) - 实验性 Bundler、gem、Gradle、Maven、npm、pip、Pipenv、pnpm、Poetry、Twine 和 uv 的 Dependency Firewall 包装器，以及本地活动摘要
- [`glab-deploy-key`](../glab-deploy-key/SKILL.md) - 自动化部署密钥
- [`glab-orbit`](../glab-orbit/SKILL.md) - 管理的 Orbit CLI 工作流，用于远程图状态/查询/发现和本地代码图索引/搜索（实验性）
- [`glab-quick-actions`](../glab-quick-actions/SKILL.md) - GitLab 切割命令快速操作，用于批量状态更改
- [`glab-security`](../glab-security/SKILL.md) - 项目安全扫描配置文件启用/禁用/状态管理（实验性）
- [`glab-stack`](../glab-stack/SKILL.md) - 堆叠/依赖的合并请求
- [`glab-opentofu`](../glab-opentofu/SKILL.md) - Terraform/OpenTofu 状态管理

**工具：**
- [`glab-alias`](../glab-alias/SKILL.md) - 自定义命令别名
- [`glab-completion`](../glab-completion/SKILL.md) - Shell 自动补全
- [`glab-help`](../glab-help/SKILL.md) - 命令帮助和文档
- [`glab-version`](../glab-version/SKILL.md) - 版本信息
- [`glab-check-update`](../glab-check-update/SKILL.md) - 更新检查器
- [`glab-whatsnew`](../glab-whatsnew/SKILL.md) - 自上次查看或升级基线以来的发布说明
- [`glab-changelog`](../glab-changelog/SKILL.md) - 更改日志生成
- [`glab-attestation`](../glab-attestation/SKILL.md) - 软件供应链安全
- [`glab-duo`](../glab-duo/SKILL.md) - GitLab Duo AI 助手
- [`glab-mcp`](../glab-mcp/SKILL.md) - AI 助手集成的模型上下文协议服务器（实验性）
- [`glab-skills`](../glab-skills/SKILL.md) - 安装和管理捆绑代理技能（实验性）

## 何时使用 glab 而不是 Web UI

**使用 glab 时：**
- 在脚本中自动化 GitLab 操作
- 在以终端为中心的工作流中工作
- 批量操作（多个 MR/问题）
- 与其他 CLI 工具集成
- CI/CD 管道工作流
- 无需浏览器上下文切换的快速导航

**使用 Web UI 时：**
- 复杂的差异审查与内联评论
- 可视化合并冲突解决
- 配置仓库设置和权限
- 跨项目的高级搜索/过滤
- 审查安全扫描结果
- 管理组/实例级设置

## 常见工作流

### 日常开发

```bash
# 开始在问题工作上
glab issue view 123
git checkout -b 123-feature-name

# 准备好时创建 MR
glab mr create --fill --draft

# 标记为准备审查
glab mr update --ready

# 审批后合并
glab mr merge --when-pipeline-succeeds --remove-source-branch
```

### 代码审查

```bash
# 列出你的审查队列
glab mr list --reviewer=@me --state=opened

# 审查 MR
glab mr checkout 456
glab mr diff
npm test

# 批准
glab mr approve 456
glab mr note 456 -m "LGTM! 很好的错误处理工作。"
```

### CI/CD 调试

```bash
# 检查管道状态
glab ci status

# 查看失败的作业
glab ci view

# 获取作业日志
glab ci trace <job-id>

# 重试失败作业
glab ci retry <job-id>
```

## 决策树

### "我应该先创建 MR 还是先处理问题？"

```
需要跟踪工作吗？
├─ 是 → 先创建问题 (glab issue create)
│         然后：glab mr for <issue-id>
└─ 否 → 直接 MR (glab mr create --fill)
```

**使用 `glab issue create` + `glab mr for` 时：**
- 工作需要讨论/批准才能编码
- 跟踪功能请求或错误
- Sprint 计划和分配
- 想要问题在 MR 合并时自动关闭

**直接使用 `glab mr create` 时：**
- 快速修复或拼写错误
- 从现有问题工作
- 热修复或紧急更改

### "我应该使用哪个 CI 命令？"

```
你需要什么？
├─ 整体管道状态 → glab ci status
├─ 可视化管道视图 → glab ci view
├─ 特定作业日志 → glab ci trace <job-id>
├─ 下载构建工件 → glab ci artifact <ref> <job-name>
├─ 验证配置文件 → glab ci lint
├─ 触发新运行 → glab ci run
└─ 列出所有管道 → glab ci list
```

**快速参考：**
- 管道级：`glab ci status`、`glab ci view`、`glab ci run`
- 作业级：`glab ci trace`、`glab job retry`、`glab job view`
- 工件：`glab ci artifact`（通过管道）或作业工件通过 `glab job`

### "克隆还是分支？"

```
你与仓库的关系是什么？
├─ 你有写入权限 → glab repo clone group/project
├─ 为他人项目贡献：
│   ├─ 一次性贡献 → glab repo fork + 工作 + MR
│   └─ 持续贡献 → glab repo fork，然后定期同步
└─ 只是阅读/探索 → glab repo clone（或 view --web）
```

**分支时：**
- 你没有对原始仓库的写入权限
- 为开源项目贡献
- 不影响原始的实验
- 需要你自己的副本进行长期工作

**克隆时：**
- 你是项目成员并有写入权限
- 在组织/团队仓库上工作
- 没有必要创建个人副本

### "项目还是组标签？"

```
标签应该放在哪里？
├─ 跨多个项目使用 → glab label create --group <group>
└─ 特定于一个项目 → 在项目目录中 glab label create
```

**组级标签：**
- 跨组织的标签一致性
- 示例：priority::high、type::bug、status::blocked
- 集中管理，项目继承

**项目级标签：**
- 项目特定工作流
- 示例：needs-ux-review、deploy-to-staging
- 由项目维护者管理

## 相关技能

**MR 和问题工作流：**
- 从 `glab-issue` 开始创建/跟踪工作
- 使用 `glab-mr` 创建关闭问题的 MR
- 脚本：`scripts/create-mr-from-issue.sh` 自动化此过程

**CI/CD 调试：**
- 使用 `glab-ci` 进行管道级操作
- 使用 `glab-job` 进行单个作业操作
- 脚本：`scripts/ci-debug.sh` 用于快速故障诊断

**仓库操作：**
- 使用 `glab-repo` 进行仓库管理
- 使用 `glab-auth` 进行认证设置
- 脚本：`scripts/sync-fork.sh` 用于分支同步

**配置：**
- 使用 `glab-auth` 进行初始认证
- 使用 `glab-config` 设置默认值和偏好
- 使用 `glab-alias` 创建自定义快捷方式
