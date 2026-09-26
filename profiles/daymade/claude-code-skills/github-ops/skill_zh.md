# GitHub 操作

交付请求的 GitHub 状态，而不是看起来成功的命令。`200`、`201`、`202` 或 `204` 响应表明 GitHub 接受了请求；它不是证明所有请求的字段已更改、邀请已被接受、异步作业已完成或用户业务目标已实现的证据。

## 按操作路线

仅读取完成任务所需的参考：

| 任务 | 参考 |
|---|---|
| 创建、审阅、合并、关闭、比较或汇聚 PR；退役远程 PR 分支 | [`references/pr_operations.md`](references/pr_operations.md) |
| 创建、编辑、搜索、转移、关闭或批量管理问题 | [`references/issue_operations.md`](references/issue_operations.md) |
| 检查、克隆、创建、编辑、重命名、存档、转移、更改可见性或删除存储库 | [`references/repository_operations.md`](references/repository_operations.md) |
| 检查或更改协作者、团队、基础权限、成员特权或组织双因素认证 | [`references/organization_access_and_settings.md`](references/organization_access_and_settings.md) |
| 在允许协作者通过 PR 贡献的同时保护默认分支 | [`references/branch_protection.md`](references/branch_protection.md) |
| 触发、检查、重新运行、取消或清除操作；管理密钥或变量 | [`references/workflow_operations.md`](references/workflow_operations.md) |
| 将 Docker/OCI 镜像构建并发布到 GitHub 容器注册表 (GHCR) | [`references/ghcr_publishing.md`](references/ghcr_publishing.md) |
| 使用原始 REST/GraphQL 端点、分页、速率限制、Webhook 或企业主机 | [`references/api_reference.md`](references/api_reference.md) |
| 构建脚本、重试、批量操作或机器可读输出 | [`references/best_practices.md`](references/best_practices.md) |

对于本地 Git 恢复、脏工作树、包或丢失的提交，使用 `git-safety-net`。这项技能拥有 GitHub 托管的状态。

## 通用操作合同

### 1. 在接触 GitHub 之前对请求进行分类

- **回答、检查、诊断或审阅：** 只读。不要创建 PR、问题、评论、邀请、工作流运行或设置更改。
- **创建、更改、合并、关闭、授予权限、撤销、发布或删除：** 授权的命名状态更改。将目标和影响范围保持在该请求内。
- **破坏性、公开、与凭证相关的、触发生产或外部通信：** 需要精确的目标、后果和恢复路径。如果用户没有提供实质性的选择，例如存储库所有者、可见性或消息内容，则在写入之前停止。

不要因为修复看起来很明显而将只读调查转变为变更。不要发送评论、审阅、问题或邀请，其接收者或内容在当前任务中未经授权。

对于授权的贡献者，评估存储库访问权限与其持续的贡献角色，而不仅仅是今天的读取或同步命令。存储库写入访问权限和更新默认分支的权限是分开的决定。遵循用户选择贡献范围；使用分支保护和 PR 审阅来控制集成，而不是将贡献者无声地降低为只读。单独的诊断仍然不能授权授予。

### 2. 绑定身份、主机和目标

在第一次写入之前，验证活动账户并解析完整的目标：

```bash
gh auth status --hostname HOST
gh api --hostname HOST user --jq '.login'
gh repo view HOST/OWNER/REPO \
  --json nameWithOwner,visibility,isPrivate,viewerPermission,url
```

对于 `github.com`，`OWNER/REPO` 足够。永远不要使用 `gh auth status --show-token` 进行常规诊断，永远不要打印、粘贴或记录令牌。

在当前会话中第一次推送到远程之前，读取其实时可见性：

```bash
gh repo view OWNER/REPO \
  --json nameWithOwner,visibility,isPrivate,stargazerCount,forkCount,url
```

### 3. 读取当前权限并预览差异

使用 GitHub 托管的状态，而不是陈旧的本地引用或记忆中的设置。仅捕获证明请求转换所需的字段。在执行有后果的写入之前，使此计划明确：

```text
目标：完整的存储库、组织、PR、问题、运行或账户
当前：权威字段和不可变 ID/SHA
请求：精确的字段或状态转换
影响范围：受影响的人员、存储库、分支、运行或公共表面
恢复：精确的逆操作或明确的“不可恢复”
回读：独立的 GET/CLI 查询和预期结果
```

如果用户已经授权了此精确后果，则执行它。不要添加仪式性的第二次确认。如果目标、范围、公开暴露、删除、接收者或恢复仍然不明确，则在写入之前暂停。

### 4. 选择输入合同实际支持变更的界面

按顺序优先：

1. 专用的 `gh` 子命令；
2. 用于单个资源或权威回读的文档化 REST 端点；
3. 当所需的变异/查询是 GraphQL 仅有的或组合相关数据时使用 GraphQL；
4. 当设置没有支持的 API 输入时使用文档化的 GitHub UI。

响应字段不是自动可写的字段。在使用 `PATCH` 之前，将期望的键与操作的当前 **请求体参数** 进行比较，而不是 `GET` 返回的形状。GitHub 可能会忽略不支持的键，同时仍然返回成功的响应。不要仅仅为了让命令运行而切换 API 系列。

使用 `gh api` 进行显式方法。添加 `-f` 或 `-F` 会将默认方法更改为 `POST`；过滤的 GET 请求必须在 `-X GET` 中包含。

### 5. 一次变更；不要重试模糊

- 将存储库、对象编号、分支、运行 ID、用户名和预期 SHA 固定在支持操作的接口。
- 不要盲目重试非幂等的写入，如评论、邀请、工作流调度、发布或 PR/问题创建。在超时或 5xx 之后，首先读取以确定第一个请求是否成功到达。
- 对于批量更改，冻结并显示有限的目标列表，然后逐个处理目标并显示每个项目的结果。永远不要将未经审查的实时查询直接管道到破坏性的 `xargs` 命令。
- 不要绕过存储库钩子、必需的检查、分支保护、签名或可见性后果确认。

### 6. 通过独立的回读进行验证

运行一个不信任变异响应或缓存本地引用的实时读取：

| 变异 | 需要的接受证据 |
|---|---|
| PR 合并/关闭/编辑 | PR 状态加上在着陆时对获取的基础的接受行为 |
| 分支删除 | 托管的分支/引用不存在；本地远程跟踪清理是单独的检查 |
| 问题/评论/审阅 | 精确的对象存在，并具有预期的状态/内容 |
| 存储库创建/编辑/可见性 | 完整的存储库回读匹配所有者、可见性和请求的字段 |
| 协作者/团队权限 | 如果待定，则邀请状态，然后是有效权限；撤销时还识别剩余的基础/团队授权 |
| 组织设置 | 刷新的组织/设置回读返回所有请求的字段；仅 UI 设置需要 UI 回读加上任何可用的 API 信号 |
| 双因素认证要求 | 预热受影响的账户，UI 确认，API 回读，然后是成员/外部协作者的审计 |
| 工作流调度/重新运行/取消 | 期望的运行 ID 达到预期状态；命令接受不是完成 |
| 密钥/变量更改 | 元数据和消费者行为，永远不会披露密钥值 |

对于异步状态，使用有界的截止日期进行轮询，如果未观察到终端状态，则报告 `pending`。如果回读不同，则报告 `failed/no-op` 或 `partially applied`，显示不匹配的字段，并保持恢复可用。永远不要仅从写入收据上说“完成”。

### 7. 报告业务结果

以四种诚实的状态之一结束：

- **已更改并验证** — 请求的状态被独立观察到；
- **已满足** — 没有必要写入；
- **待定** — 已接受但尚未终端，有下一个权威检查；
- **失败/无操作或部分** — 请求和观察到的状态不同，有恢复和未解决的风险。

### 8. 仅对命名的写入进行身份验证

身份验证的范围仅限于授权的操作；它不是重新打开已授权的精确写入的原因。在开始交互式浏览器或设备流程之前，说明 GitHub 应用程序、活动账户、目标主机和精确的权限差异。继续浏览器在解释后可以完成的步骤。仅在需要用户的物理存在时才将控制权交给用户，例如 MFA、硬件密钥或账户选择决策。永远不要仅仅因为正常流程是交互式的而请求更广泛的范围、不同的账户或无关的批准。

不要在终端输出、URL、参数、提交的文件或报告中暴露凭证值。生产主机的仅拉取注册表凭证不是发布授权。当它已被验证为精确的写入时，重用当前的已授权凭证；使用临时的本地 Docker 配置，并在操作后删除该配置。GHCR 发布有自己的预检查和摘要回读；在构建或推送镜像之前加载 `references/ghcr_publishing.md`。

## 高影响边界

- 存储库创建需要一个明确的 `OWNER/REPO` 和可见性。永远不要将通用示例默认为 `--public`；公开暴露是一个产品决策。
- 存储库可见性更改可能会暴露代码、操作日志、工件、分支和历史记录。只有在授权后果和精确存储库之后，才使用 `gh repo edit --visibility ... --accept-visibility-change-consequences`，然后回读。
- 合并、分支删除、存储库创建/删除/转移/可见性更改、组织范围的权限、双因素认证执行和密钥轮换需要其操作特定的参考。
- PR 和问题标题格式是存储库策略。检查模板、贡献指导、检查或接受的最近示例；不要发明通用的 JIRA 前缀。
- 企业策略可以覆盖组织或存储库控制。明确保留 `HOST` 并报告较低层无法更改强制状态时的情况。

## 安全只读快速参考

```bash
gh pr list -R OWNER/REPO --state open --json number,title,state,url
gh pr view 123 -R OWNER/REPO --json number,title,state,headRefOid,baseRefOid,url
gh issue list -R OWNER/REPO --state open --json number,title,state,url
gh workflow list -R OWNER/REPO
gh run list -R OWNER/REPO --limit 20 \
  --json databaseId,status,conclusion,headSha,url
gh api -X GET 'repos/OWNER/REPO/branches?per_page=100' --paginate --jq '.[].name'
```

使用 `--json`/`--jq` 进行决策。人类格式的输出用于阅读，而不是解析。
