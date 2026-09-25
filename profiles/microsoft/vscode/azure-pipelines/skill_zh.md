# 验证 Azure Pipeline 更改

在修改 Azure DevOps pipeline 文件（位于 `build/azure-pipelines/` 中的 YAML 文件），您可以在提交之前使用 Azure CLI 本地验证更改。这避免了推送更改、等待 CI 和检查结果的缓慢反馈循环。

## 前置条件

1. **检查是否已安装 Azure CLI**：
   ```bash
   az --version
   ```

   如果未安装，请安装它：
   ```bash
   # macOS
   brew install azure-cli

   # Windows (以管理员身份运行 PowerShell)
   winget install Microsoft.AzureCLI

   # Linux (Debian/Ubuntu)
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. **检查是否已安装 DevOps 扩展**：
   ```bash
   az extension show --name azure-devops
   ```

   如果未安装，请添加它：
   ```bash
   az extension add --name azure-devops
   ```

3. **进行身份验证**：
   ```bash
   az login
   az devops configure --defaults organization=https://dev.azure.com/monacotools project=Monaco
   ```

## VS Code 主构建

主 VS Code 构建pipeline：
- **组织**：`monacotools`
- **项目**：`Monaco`
- **定义 ID**：`111`
- **URL**：https://dev.azure.com/monacotools/Monaco/_build?definitionId=111

## VS Code Insider 定时构建

有两个 Insider 构建自动按计划运行：
- **早上构建**：约 CET 7:00
- **晚上构建**：约 CET 19:00

这些定时构建使用相同的 pipeline 定义（`111`），但在 `main` 分支上运行以生成 Insider 发布。

---

## 排队构建

使用 [排队命令](./azure-pipeline.ts) 排队验证构建：

```bash
# 在当前分支排队构建
node .github/skills/azure-pipelines/azure-pipeline.ts queue

# 指定源分支排队
node .github/skills/azure-pipelines/azure-pipeline.ts queue --branch my-feature-branch

# 使用自定义参数排队
node .github/skills/azure-pipelines/azure-pipeline.ts queue --parameter "VSCODE_BUILD_WEB=false" --parameter "VSCODE_PUBLISH=false"

# 带空格的参数值
node .github/skills/azure-pipelines/azure-pipeline.ts queue --parameter "VSCODE_BUILD_TYPE=Product Build"
```

> **重要提示**：在排队新构建之前，取消您不再需要的同一分支上的任何先前构建。这可以释放构建代理并减少资源浪费：
> ```bash
> # 从状态中查找构建 ID，然后取消它
> node .github/skills/azure-pipelines/azure-pipeline.ts status
> node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id <id>
> node .github/skills/azure-pipelines/azure-pipeline.ts queue
> ```

### 脚本选项

| 选项 | 描述 |
|------|-------------|
| `--branch <name>` | 要构建的源分支（默认：当前 git 分支） |
| `--definition <id>` | pipeline 定义 ID（默认：111） |
| `--parameter <entry>` | pipeline 参数，格式为 `KEY=VALUE`（可重复）；**当值包含空格时使用此选项** |
| `--parameters <list>` | 空格分隔的参数，格式为 `KEY=VALUE KEY2=VALUE2`；值**不能**包含空格 |
| `--dry-run` | 打印命令而不执行 |

### 产品构建排队参数 (`build/azure-pipelines/product-build.yml`)

| 名称 | 类型 | 默认值 | 允许的值 | 描述 |
|------|------|---------|----------------|-------------|
| `VSCODE_QUALITY` | string | `insider` | `exploration`, `insider`, `stable` | 构建质量通道 |
| `VSCODE_BUILD_TYPE` | string | `Product Build` | `Product`, `CI` | 产品与 CI 的构建模式 |
| `NPM_REGISTRY` | string | `https://pkgs.dev.azure.com/monacotools/Monaco/_packaging/vscode/npm/registry/` | 任何 URL | 自定义 npm 注册中心 |
| `CARGO_REGISTRY` | string | `sparse+https://pkgs.dev.azure.com/monacotools/Monaco/_packaging/vscode/Cargo/index/` | 任何 URL | 自定义 Cargo 注册中心 |
| `VSCODE_BUILD_WIN32` | boolean | `true` | `true`, `false` | 构建 Windows x64 |
| `VSCODE_BUILD_WIN32_ARM64` | boolean | `true` | `true`, `false` | 构建 Windows arm64 |
| `VSCODE_BUILD_LINUX` | boolean | `true` | `true`, `false` | 构建 Linux x64 |
| `VSCODE_BUILD_LINUX_SNAP` | boolean | `true` | `true`, `false` | 构建 Linux x64 Snap |
| `VSCODE_BUILD_LINUX_ARM64` | boolean | `true` | `true`, `false` | 构建 Linux arm64 |
| `VSCODE_BUILD_LINUX_ARMHF` | boolean | `true` | `true`, `false` | 构建 Linux armhf |
| `VSCODE_BUILD_ALPINE` | boolean | `true` | `true`, `false` | 构建 Alpine x64 |
| `VSCODE_BUILD_ALPINE_ARM64` | boolean | `true` | `true`, `false` | 构建 Alpine arm64 |
| `VSCODE_BUILD_MACOS` | boolean | `true` | `true`, `false` | 构建 macOS x64 |
| `VSCODE_BUILD_MACOS_ARM64` | boolean | `true` | `true`, `false` | 构建 macOS arm64 |
| `VSCODE_BUILD_MACOS_UNIVERSAL` | boolean | `true` | `true`, `false` | 构建 macOS universal（需要 macOS 架构） |
| `VSCODE_BUILD_WEB` | boolean | `true` | `true`, `false` | 构建 Web 产物 |
| `VSCODE_PUBLISH` | boolean | `true` | `true`, `false` | 发布到 builds.code.visualstudio.com |
| `VSCODE_RELEASE` | boolean | `false` | `true`, `false` | 如果成功，触发发布流程 |
| `VSCODE_STEP_ON_IT` | boolean | `false` | `true`, `false` | 跳过测试 |
| `VSCODE_USE_LEGACY_OSS_NOTICE` | boolean | `false` | `true`, `false` | 保留 legacy mixin ThirdPartyNotices.txt 而不是 Component Governance 通知 |

示例：运行快速 CI 方向的验证，并最小化发布/发布影响：

```bash
node .github/skills/azure-pipelines/azure-pipeline.ts queue \
   --parameter "VSCODE_BUILD_TYPE=CI Build" \
   --parameter "VSCODE_PUBLISH=false" \
   --parameter "VSCODE_RELEASE=false"
```

---

## 检查构建状态

使用 [状态命令](./azure-pipeline.ts) 监控正在运行的构建：

```bash
# 获取最新构建的状态
node .github/skills/azure-pipelines/azure-pipeline.ts status

# 通过 ID 获取特定构建的概述
node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id 123456

# 监控构建状态（每 30 秒刷新一次）
node .github/skills/azure-pipelines/azure-pipeline.ts status --watch

# 自定义间隔监控（60 秒）
node .github/skills/azure-pipelines/azure-pipeline.ts status --watch 60
```

### 脚本选项

| 选项 | 描述 |
|------|-------------|
| `--build-id <id>` | 特定构建 ID（默认：当前分支上的最新构建） |
| `--branch <name>` | 按分支名称过滤构建（显示该分支的最后 20 个构建） |
| `--reason <reason>` | 按原因过滤构建：`manual`, `individualCI`, `batchedCI`, `schedule`, `pullRequest` |
| `--definition <id>` | pipeline 定义 ID（默认：111） |
| `--watch [seconds]` | 持续轮询状态直到构建完成（默认：30 秒） |
| `--download-log <id>` | 下载特定日志到 /tmp |
| `--download-artifact <name>` | 下载产物到 /tmp |
| `--json` | 输出原始 JSON 以供程序化消费 |

---

## 取消构建

使用 [取消命令](./azure-pipeline.ts) 停止正在运行的构建：

```bash
# 通过 ID 取消构建（使用状态命令查找 ID）
node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id 123456

# 干运行（显示将要取消的内容）
node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id 123456 --dry-run
```

### 脚本选项

| 选项 | 描述 |
|------|-------------|
| `--build-id <id>` | 要取消的构建 ID（必需） |
| `--definition <id>` | pipeline 定义 ID（默认：111） |
| `--dry-run` | 打印将要取消的内容而不执行 |

---

## 测试 Pipeline 更改

当用户要求**测试 Azure Pipelines 构建中的更改**时，请遵循此工作流程：

1. **在当前分支排队新构建**
2. **轮询完成**，通过定期检查构建状态直到其完成

### 轮询构建完成

使用带有 `sleep` 的 shell 循环轮询构建状态。`sleep` 命令在所有主要操作系统上均可工作：

```bash
# 排队构建并从输出中记下构建 ID（例如，123456）
node .github/skills/azure-pipelines/azure-pipeline.ts queue

# 每 60 秒轮询一次直到完成（适用于 macOS、Linux 和 Windows 的 Git Bash/WSL）
# 将 <BUILD_ID> 替换为排队命令返回的实际构建 ID
while true; do
  node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id <BUILD_ID> --json 2>/dev/null | grep -q '"status": "completed"' && break
  sleep 60
done

# 检查最终结果
node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id <BUILD_ID>
```

或者，使用内置的 `--watch` 标志自动处理轮询：

```bash
node .github/skills/azure-pipelines/azure-pipeline.ts queue
# 使用排队命令返回的构建 ID
node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id <BUILD_ID> --watch
```

> **注意**：`--watch` 标志默认每 30 秒轮询一次。使用 `--watch 60` 设置 60 秒间隔以减少 API 调用。

---

## 常见工作流程

### 1. 快速 Pipeline 验证

```bash
# 修改 YAML 文件后，执行：
git add -A && git commit -m "test: pipeline changes"
git push origin HEAD

# 检查此分支上的任何先前构建并取消（如果需要）
node .github/skills/azure-pipelines/azure-pipeline.ts status
node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id <id>  # 如果有活动构建

# 排队并监控新构建
node .github/skills/azure-pipelines/azure-pipeline.ts queue
node .github/skills/azure-pipelines/azure-pipeline.ts status --watch
```

### 2. 调查构建

```bash
# 获取构建概述（显示阶段、产物和日志 ID）
node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id 123456

# 下载特定日志进行深入检查
node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id 123456 --download-log 5

# 下载产物
node .github/skills/azure-pipelines/azure-pipeline.ts status --build-id 123456 --download-artifact unsigned_vscode_cli_win32_x64_cli
```

### 3. 使用修改后的参数测试

```bash
# 自定义构建矩阵以快速验证
node .github/skills/azure-pipelines/azure-pipeline.ts queue \
   --parameter "VSCODE_BUILD_TYPE=CI Build" \
   --parameter "VSCODE_BUILD_WEB=false" \
   --parameter "VSCODE_BUILD_ALPINE=false" \
   --parameter "VSCODE_BUILD_ALPINE_ARM64=false" \
   --parameter "VSCODE_PUBLISH=false"
```

### 4. 取消正在运行的构建

```bash
# 首先，找到构建 ID
node .github/skills/azure-pipelines/azure-pipeline.ts status

# 通过 ID 取消特定构建
node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id 123456

# 干运行以查看将要取消的内容
node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id 123456 --dry-run
```

### 5. 迭代 Pipeline 更改

在迭代 pipeline YAML 更改时，始终在排队新构建之前取消过时的构建：

```bash
# 推送新更改
git add -A && git commit --amend --no-edit
git push --force-with-lease origin HEAD

# 查找过时的构建 ID 并取消它
node .github/skills/azure-pipelines/azure-pipeline.ts status
node .github/skills/azure-pipelines/azure-pipeline.ts cancel --build-id <id>

# 排队全新构建并监控
node .github/skills/azure-pipelines/azure-pipeline.ts queue
node .github/skills/azure-pipelines/azure-pipeline.ts status --watch
```

---

## 故障排除

### 身份验证问题
```bash
# 重新身份验证
az logout
az login

# 检查当前账户
az account show
```

### 扩展未找到
```bash
az extension add --name azure-devops --upgrade
```

### 速率限制

如果您遇到速率限制，请添加 API 调用之间的延迟或使用 `--watch` 并设置较长的间隔。
