# Azure DevOps CLI

使用 Azure CLI 和 Azure DevOps 扩展管理 Azure DevOps 资源。

**CLI 版本：** 2.81.0（截至 2025 年的当前版本）

## 前置条件

```bash
# 安装 Azure CLI
brew install azure-cli  # macOS
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux

# 安装 Azure DevOps 扩展
az extension add --name azure-devops
```

## 身份验证

```bash
# 使用 PAT 令牌登录
az devops login --organization https://dev.azure.com/{org} --token YOUR_PAT_TOKEN

# 设置默认组织和项目（避免重复 --org/--project）
# 注意：遗留 URL https://{org}.visualstudio.com 应替换为 https://dev.azure.com/{org}
az devops configure --defaults organization=https://dev.azure.com/{org} project={project}

# 列出当前配置
az devops configure --list
```

## CLI 结构

```
az devops          # 主 DevOps 命令
├── admin          # 管理（横幅）
├── extension      # 扩展管理
├── project        # 团队项目
├── security       # 安全操作
│   ├── group      # 安全组
│   └── permission # 安全权限
├── service-endpoint # 服务连接
├── team           # 团队
├── user           # 用户
├── wiki           # 维基
├── configure      # 设置默认值
├── invoke         # 调用 REST API
├── login          # 身份验证
└── logout         # 清除凭证

az pipelines       # Azure Pipelines
├── agent          # 代理
├── build          # 构建
├── folder         # 管道文件夹
├── pool           # 代理池
├── queue          # 代理队列
├── release        # 发布
├── runs           # 管道运行
├── variable       # 管道变量
└── variable-group # 变量组

az boards          # Azure Boards
├── area           # 区域路径
├── iteration      # 迭代
└── work-item      # 工作项

az repos           # Azure Repos
├── import         # Git 导入
├── policy         # 分支策略
├── pr             # 拉取请求
└── ref            # Git 引用

az artifacts       # Azure Artifacts
└── universal      # 通用包
```

## 参考文件

根据用户的任务阅读相关参考文件。每个文件包含其领域的完整命令语法和示例。

| 文件 | 阅读时机 | 涵盖内容 |
|---|---|---|
| `references/repos-and-prs.md` | 仓库、分支、拉取请求、分支策略 | 仓库、导入、PRs（创建/列表/投票/审阅者/策略）、Git 引用、分支策略 |
| `references/pipelines-and-builds.md` | 管道、构建、发布、工件 | 管道 CRUD、运行、构建、发布、工件下载/上传 |
| `references/boards-and-iterations.md` | 工作项、冲刺、区域路径 | 工作项（WIQL创建/更新/关系）、区域路径、迭代、团队迭代 |
| `references/variables-and-agents.md` | 管道变量、代理池 | 管道变量、变量组、管道文件夹、代理池/队列 |
| `references/org-and-security.md` | 项目、团队、用户、权限、维基 | 项目、扩展、团队、用户、安全组/权限、服务连接、维基、管理 |
| `references/advanced-usage.md` | 输出格式化、JMESPath 查询 | 输出格式、JMESPath 查询（基本+高级）、全局参数、常用参数、Git 别名 |
| `references/workflows-and-patterns.md` | 自动化脚本、最佳实践、错误处理 | 常见工作流、最佳实践、错误处理、脚本模式、实际示例 |
| `references/long-comments-on-windows.md` | Windows 上长 `--discussion`、`--description` 或 `--content` 值失败 | `az.cmd` 的 `cmd.exe` 8191 字符限制、外壳检测和三种验证的解决方案（`azps.ps1`、原生 `--file-path`、`az devops invoke --in-file`） |
