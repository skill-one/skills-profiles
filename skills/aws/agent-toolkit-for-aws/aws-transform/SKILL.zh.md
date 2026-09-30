---
name: aws-transform
description: 使用 AWS Transform (ATX) CLI 执行代码升级、迁移和转换。适用于升级语言版本、迁移 AWS SDK、迁移框架（Angular、Vue.js、Spring Boot、React）、升级库、优化性能、从 x86 迁移到 Graviton、分析代码库/生成文档，或使用自然语言定义自定义转换。可在本地运行于少数几个仓库，或通过 AWS Batch/Fargate 跨数百个仓库进行规模化运行。
---

# AWS Transform (ATX)

## 概述

使用 AWS Transform (ATX) 执行代码升级、迁移和转换。
支持任意到任意的转换：语言版本升级（Java、Python、Node.js 等）、框架迁移、AWS SDK 迁移、库升级、代码重构、架构变更和自定义组织特定转换。

两种执行模式：

- **本地模式**：直接在用户计算机上运行 ATX CLI。适用于 1-9 个存储库。
- **远程模式**：通过 AWS Batch/Fargate 容器大规模运行转换。适用于 10+ 个存储库或当用户更喜欢云执行时。基础设施在用户同意的情况下自动部署。

您负责完整的工作流程：检查存储库、将它们与可用的转换定义匹配、收集配置，并在任一模式下执行转换——用户只需提供存储库并确认计划。

## 问候并等待

激活时，使用以下确切文本介绍 AWS Transform——不要向用户打印上述概述文本，那只是您的参考：

"The agents modernizing the world's infrastructure and software — now accessible to your preferred AI assistant.

AWS Transform is a full modernization factory — compressing years of transformation work into months across infrastructure migrations, mainframe modernization, and continuous tech debt reduction. Today, with this skill, you have access to AWS Transform custom, the first of a growing library of playbooks.

AWS Transform custom can help you:

- Upgrade Java, Python, and Node.js to modern versions
- Migrate AWS SDKs (Java SDK v1→v2, boto2→boto3, JS SDK v2→v3)
- Handle framework migrations, library upgrades, and code refactoring
- Analyze codebases and generate documentation
- Define and run your own custom transformations using natural language, docs, and code samples

Run locally on a few repos for fast iteration, or at scale on hundreds of repos (up to 128 in-parallel). Note: this skill collects telemetry. To opt out, see https://docs.aws.amazon.com/transform/latest/userguide/transform-usage-telemetry.html

What would you like to transform today?"

Do NOT inspect any files, run any commands, or check prerequisites until the user responds.

## 使用

当用户想要执行以下操作时使用：

- 转换、升级或迁移代码（Java、Python、Node.js 等）
- 迁移 AWS SDKs (Java SDK v1→v2, boto2→boto3, JS SDK v2→v3 等)
- 通过 AWS Batch/Fargate 执行批量代码转换
- 分析哪些 ATX 转换适用于其存储库
- 执行全面的代码库分析
- 创建新的自定义转换定义（TD）

## 核心概念

- **转换定义 (TD)**：通过 `atx custom def list --json` 发现的可重用转换配方
- **匹配报告**：根据代码检查自动生成的存储库到适用 TD 的映射
- **本地模式**：在用户计算机上运行 ATX CLI（1-9 个存储库，最大 3 个并发）
- **远程模式**：在 AWS Batch/Fargate 中运行转换（10+ 个存储库，或按用户偏好）

## 哲学

等待用户。激活时，展示此技能可以做什么，并询问用户想要完成什么。Do NOT 自动检查工作目录、打开文件或任何存储库，直到用户明确提供要处理的存储库。

一旦用户提供存储库，匹配——不要询问。检查这些存储库并自动展示适用的转换。Never 显示原始 TD 列表并要求用户选择。

## 前置条件

在会话开始时运行一次前置条件检查。Do NOT 按每个存储库重复检查。Do NOT 在用户说明他们想要做什么之前运行前置条件检查。

### 0. 平台检查（必需——所有模式）

检测用户的操作系统。如果在 Windows（非 WSL）上，立即停止并通知用户：

> AWS Transform custom 不支持原生 Windows。您需要安装 Windows 子系统 for Linux (WSL) 并在 WSL 中运行此命令。
>
> 安装 WSL: 在 PowerShell（以管理员身份）中运行 `wsl --install`，然后重启。之后，打开 WSL 终端并从那里重新运行此技能。

通过运行检查：

```bash
uname -s
```

- `Linux` 或 `Darwin` → 正常继续
- `MINGW*`, `MSYS*`, `CYGWIN*` 或任何 Windows 样式的输出 → 阻止并显示上述 WSL 消息
- 命令失败、错误或未找到 → 视为原生 Windows，阻止并显示上述 WSL 消息

Do NOT 在原生 Windows 上执行任何其他步骤。

### 1. AWS CLI（必需——所有模式）

```bash
aws --version
```

如果未安装，引导用户：

- macOS: `brew install awscli` 或 `curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg" && sudo installer -pkg AWSCLIV2.pkg -target /`
- Linux: `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install`

Do NOT 继续直到 `aws --version` 成功。

### 2. AWS 凭证（必需——所有模式）

```bash
aws sts get-caller-identity
```

如果凭证未配置，引导用户设置：

```
AWS Transform custom 需要 AWS 凭证以使用服务进行身份验证。使用以下方法之一配置身份验证。

1. AWS CLI Configure (~/.aws/credentials):
   aws configure

2. AWS 凭证文件（手动）。在 ~/.aws/credentials 中配置凭证：

[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key

3. 环境变量。设置以下环境变量：

export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token

您还可以使用 AWS_PROFILE 环境变量指定配置文件：

export AWS_PROFILE=your_profile_name
```

Do NOT 继续直到凭证通过验证。设置后重新运行 `aws sts get-caller-identity`。

注意：通过 `export` 设置的环境变量不会在 shell 会话之间传递。如果代理启动了新的 shell，作为环境变量设置的凭证可能会丢失。优先选择 `aws configure` 或 `~/.aws/credentials` 以实现持久化。

### 3. ATX CLI（必需——所有模式）

所有模式下都需要它来发现 TD (`atx custom def list --json`)。本地模式下也用于转换执行。

```bash
atx --version
# 安装: curl -fsSL https://transform-cli.awsstatic.com/install.sh | bash
```

**强制执行：** 每次会话开始时始终运行一次 `atx update`，即使您最近刚刚运行过。这会捕获新的 ATX CLI 版本和新的 TD。在运行任何其他 ATX 命令（包括 `atx custom def list --json`）之前运行它：

```bash
atx update
```

Do NOT 跳过此步骤。Do NOT 询问用户是否要更新。Do NOT 根据CLI是否“需要”更新来决定。无条件运行它。

### 4. IAM 权限（必需——所有模式）

本地模式下需要 `transform-custom:*` 最小权限。通过运行 TD 列表进行验证：

```bash
atx custom def list --json
```

如果成功，权限足够——跳过本节其余部分。

如果因权限错误失败，调用者需要 `transform-custom:*` IAM 权限。向用户解释需要什么并确认后再继续：

> 您的身份需要 `transform-custom:*` 权限才能使用 ATX CLI。
> 我可以将 AWS 管理的策略 `AWSTransformCustomFullAccess` 附着到您的身份上。要继续吗？

只有在用户确认后，才附加管理策略：

```bash
CALLER_ARN=$(aws sts get-caller-identity --query Arn --output text)
if echo "$CALLER_ARN" | grep -q ":user/"; then
  IDENTITY_NAME=$(echo "$CALLER_ARN" | awk -F'/' '{print $NF}')
  aws iam attach-user-policy --user-name "$IDENTITY_NAME" \
    --policy-arn "arn:aws:iam::aws:policy/AWSTransformCustomFullAccess"
elif echo "$CALLER_ARN" | grep -Eq ":assumed-role/|:role/"; then
  ROLE_NAME=$(echo "$CALLER_ARN" | sed 's/.*:\(assumed-\)\{0,1\}role\///' | cut -d'/' -f1)
  aws iam attach-role-policy --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::aws:policy/AWSTransformCustomFullAccess"
fi
```

如果附加命令本身失败（例如，IAM 权限不足，或 SSO 管理的角色），通知用户他们需要请求 AWS 管理员将 `AWSTransformCustomFullAccess` AWS 管理策略附加到他们的身份。对于 SSO 用户（角色名以 `AWSReservedSSO_` 开头），必须将其添加到他们的 IAM Identity Center 权限集中——不能直接附加。

Do NOT 继续直到 `atx custom def list --json` 成功。

远程模式下需要额外的权限（Lambda 调用、S3、KMS、Secrets Manager、CloudWatch）。这些权限作为部署流程的一部分生成并附加——见 [references/remote-execution.md](references/remote-execution.md)。

见 [references/cli-reference.md](references/cli-reference.md) 获取完整权限列表。

### 5. AWS CDK（远程模式仅限）

用于部署远程基础设施。检查是否安装：

```bash
cdk --version
```

如果未安装，全局安装它：

```bash
npm install -g aws-cdk
```

Do NOT 在远程部署之前 `cdk --version` 成功之前继续。

### 6. 远程基础设施（远程模式仅限——延迟）

仅当用户选择远程模式时才验证。基础设施 CDK 脚本在运行时通过克隆 `https://github.com/aws-samples/aws-transform-custom-samples.git`（分支 `atx-remote-infra`）获取——它们不随此技能捆绑。见 [references/remote-execution.md](references/remote-execution.md)。

## 工作流程

生成一次会话时间戳并重用它此会话中所有路径：

```bash
SESSION_TS=$(date +%Y%m%d-%H%M%S)
```

### 步骤 1：收集存储库

询问用户本地路径或 git URL。接受一个或多个。Do NOT 假设当前工作目录或编辑器文件是目标——等待用户明确提供存储库。

接受的源格式：

- **本地路径**——用户计算机上的目录（例如，`/home/user/my-project`）
- **HTTPS git URL**——公共或私有（例如，`https://github.com/org/repo.git`）
- **SSH git URL**——例如，`git@github.com:org/repo.git`
- **S3 存储桶路径带 zips**——例如，`s3://my-bucket/repos/`
  包含存储库 zip 文件的存储桶。每个 zip 成为一次转换作业。

#### S3 存储桶输入

如果用户提供一个包含 zip 文件的 S3 路径，询问他们更喜欢哪种执行模式（如果尚未指定）。S3 输入适用于两种模式：

**远程模式**：将 zips 从用户的存储桶复制到管理的源存储桶，然后提交指向管理副本的作业：

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
SOURCE_BUCKET="atx-source-code-${ACCOUNT_ID}"

# 列出用户存储桶路径中的所有 zips
aws s3 ls s3://user-bucket/repos/ --recursive | grep '\.zip$'

# 将每个 zip 复制到管理的源存储桶
aws s3 sync s3://user-bucket/repos/ s3://${SOURCE_BUCKET}/repos/ --exclude "*" --include "*.zip"
```

然后提交一个批处理作业，每个 zip 一个作业，每个作业指向 `s3://${SOURCE_BUCKET}/repos/<filename>.zip`。容器会自动处理 zip 提取。见 [references/multi-transformation.md](references/multi-transformation.md) 获取批处理提交。
管理的源存储桶有 7 天的生命周期——复制的 zips 会自动删除。

**本地模式**：本地下载并提取每个 zip：

```bash
mkdir -p ~/.aws/atx/custom/atx-agent-session/repos
aws s3 sync s3://user-bucket/repos/ ~/.aws/atx/custom/atx-agent-session/repos/ --exclude "*" --include "*.zip"
for zip in ~/.aws/atx/custom/atx-agent-session/repos/*.zip; do
  name=$(basename "$zip" .zip)
  unzip -qo "$zip" -d "$HOME/.aws/atx/custom/atx-agent-session/repos/${name}-$SESSION_TS/"
done
```

使用提取的目录作为 `<repo-path>` 进行本地执行。标准本地模式限制适用（最多 3 个并发存储库）。

#### 私有存储库检测（远程模式）

**始终询问用户**——Do NOT 自己尝试确定存储库的可见性。Never 尝试克隆、curl 或探测 URL 来检查它是否为公共或私有。只需询问用户。一旦用户提供 git URL 并选择远程模式（或可能），询问：

> "这些存储库中有任何私有的吗？如果是，远程容器需要凭证来克隆它们——我会引导您完成设置。"

Do NOT 跳过此问题。Do NOT 尝试通过尝试克隆、curl 或任何其他网络请求来推断可见性。Just ask.

如果用户确认存储库是私有的，根据 URL 格式确定凭证类型：

首先，解析区域（用于以下 Secrets Manager 命令）：

```bash
REGION=${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null)}}
REGION=${REGION:-us-east-1}
```

**对于 HTTPS URL**——检查是否已配置 GitHub PAT：

```bash
aws secretsmanager describe-secret --secret-id "atx/github-token" --region "$REGION" 2>/dev/null \
  && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

如果 CONFIGURED，询问用户： "一个 GitHub PAT 已经存储。您想继续使用它，还是用一个新的替换它？" 如果他们想替换，告诉他们运行：

```
aws secretsmanager put-secret-value --secret-id "atx/github-token" --region "$REGION" --secret-string "YOUR_TOKEN_HERE"
```

如果 NOT_CONFIGURED，解释需要什么并告诉用户运行创建命令：
> "私有 HTTPS 存储库需要一个存储在 AWS Secrets Manager 中的 GitHub Personal Access Token (PAT)。远程容器在启动时使用它来克隆您的存储库。
> 令牌保留在您的 AWS 账户中——您可以随时删除它。
>
> PAT 需要对私有存储库具有 `repo` 范围。在 https://github.com/settings/tokens 创建一个，然后运行：
>
> ```
> aws secretsmanager create-secret --name "atx/github-token" --region "$REGION" --secret-string "YOUR_TOKEN_HERE"
> ```
>
> 随时删除： `aws secretsmanager delete-secret --secret-id atx-token --region "$REGION" --force-delete-without-recovery`"

Do NOT 询问用户在聊天中粘贴他们的令牌。他们自己运行命令。等待用户确认完成，然后验证：

```bash
aws secretsmanager describe-secret --secret-id "atx/github-token" --region "$REGION" 2>/dev/null \
  && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

**对于 SSH URL** (`git@...` 或 `ssh://...`)——检查是否配置了 SSH 密钥：

```bash
aws secretsmanager describe-secret --secret-id "atx/ssh-key" --region "$REGION" 2>/dev/null \
  && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

如果 CONFIGURED，询问用户： "一个 SSH 密钥已经存储。您想继续使用它，还是用一个新的替换它？" 如果他们想替换，告诉他们运行：

```
aws secretsmanager put-secret-value --secret-id "atx/ssh-key" --region "$REGION" --secret-string "$(cat <path-to-your-private-key>)"
```

如果 NOT_CONFIGURED，解释需要什么并告诉用户运行创建命令：
> "SSH 存储库需要一个存储在 AWS Secrets Manager 中的 SSH 私有密钥。远程容器在启动时使用它来克隆您的存储库。
>
> 运行：
>
> ```
> aws secretsmanager create-secret --name "atx/ssh-key" --region "$REGION" --secret-string "$(cat <path-to-your-private-key>)"
> ```
>
> 随时删除： `aws secretsmanager delete-secret --secret-id atx/ssh-key --region "$REGION" --force-delete-without-recovery`"

Do NOT 询问用户在聊天中粘贴他们的 SSH 密钥。他们自己运行命令。

对于本地模式，私有存储库凭证不是必需的——用户的本地 git 配置处理身份验证。对于本地模式，完全跳过此检查。

### 步骤 2：发现 TD（静默）

静默运行——Do NOT 向用户显示输出：

```bash
atx custom def list --json
```

直接检查 JSON 输出以构建可用 TD 的内部查找。Do NOT 将输出管道到 python、jq 或其他解析脚本——自己读取 JSON。Never 硬编码 TD 名称。

#### 创建新的 TD

**用户明确要求创建 TD**：Do NOT 尝试程序性地创建一个。告诉用户：

要创建一个新的转换定义，请打开一个新终端并运行：

```
atx -t
```

这将启动一个交互式会话，您可以在其中描述您想要构建的转换（例如，“将所有日志从 log4j 迁移到 SLF4J”、“将 Spring Boot 2 升级到 Spring Boot 3”）。ATX CLI 将引导您定义和测试 TD，然后将其发布到您的 AWS 账户。

发布后，请返回此处，当扫描您的可用 TD 时，我会自动获取它。

**没有现有的 TD 与用户的目標匹配：** 不要静默地重定向到 TD 创建。匹配逻辑可能不完美。相反，请先与用户确认：

> “我没有找到涵盖 [描述用户的目標] 的现有 TD。您想创建一个新的吗？”

只有在用户确认后才显示 `atx -t` 说明。如果他们说不，请询问他们正在寻找什么——他们可能知道 TD 的名称或想要不同的方法。

**不要自己运行 `atx -t`** — 它需要一个交互式终端会话，代理无法驱动。用户必须在单独的终端中手动运行它。

用户创建 TD 后返回，重新运行 `atx custom def list --json` 以获取新发布的 TD 并继续正常工作流程。

### 第 3 步：检查每个存储库

仅执行轻量级检查——检查配置文件以查找关键信号：

| 信号 | 要检查的文件 | 可能的 TD 类型 |
|------|-------------|----------------|
| Python 版本 | `.python-version`, `pyproject.toml`, `setup.cfg`, `requirements.txt` | Python 版本升级 |
| Java 版本 | `pom.xml` (`<java.version>`), `build.gradle` (`sourceCompatibility`), `.java-version` | Java 版本升级 |
| Node.js 版本 | `package.json` (`engines.node`), `.nvmrc`, `.node-version` | Node.js 版本升级 |
| Python boto2 | `import boto` (NOT boto3) | boto2→boto3 迁移 |
| Java SDK v1 | `com.amazonaws` 导入, `aws-java-sdk` 在 pom.xml 中 | Java SDK v1→v2 |
| Node.js SDK v2 | `"aws-sdk"` 在 package.json 中 (NOT `@aws-sdk`) | JS SDK v2→v3 |
| x86 Java | `x86_64`/`amd64` 在 Dockerfile 中, 构建配置 | Graviton 迁移 |

将检测到的信号与第 2 步中的 TD 进行交叉引用。仅匹配用户账户中实际存在的 TD。

有关完整的检测命令，请参阅 [references/repo-analysis.md](references/repo-analysis.md)。

### 第 4 步：显示匹配报告

格式：

```
转换匹配报告
=============================
存储库: <名称> (<路径>)
  语言: <语言> <版本>
  匹配的 TD:
    - <td 名称> — <描述>

摘要: 分析了 N 个存储库，M 个存储库有适用的转换 (T 个总任务)
```

显示匹配报告并等待用户确认后再继续。未经明确用户同意，不要开始任何转换。

### 第 5 步：收集配置

询问用户提供任何额外的计划上下文（例如，升级 TD 的目标版本）。这是强制性的——始终询问，即使 TD 不严格要求配置。用户可能有代理不知道的偏好或限制。如果用户明确表示不需要额外的上下文，则跳过。

### 第 6 步：验证运行时兼容性（远程和本地）

#### 远程模式

在提交远程作业之前，确定预构建镜像是否涵盖目标运行时，或者是否需要自定义 Docker 构建。

**预构建镜像包括：**

- **Java**: 8, 11, 17, 21, 25 (Amazon Corretto) 与 Maven 和 Gradle 9.4
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 (dnf + pyenv)
- **Node.js**: 16, 18, 20, 22, 24 (nvm) 与 yarn, pnpm, TypeScript, ts-node
- **构建工具**: gcc, g++, make, patch
- **CLI 工具**: AWS CLI v2, ATX CLI, git, jq, curl, unzip, tar
- **操作系统**: Amazon Linux 2023 (x86_64)

**决策逻辑：**

1. 基于转换需求（源运行时、目标运行时、构建工具和任何其他依赖项），确定上述预构建镜像中是否包含所有所需内容
2. 如果 **是** → 使用预构建镜像路径（无需 Docker）。使用 [references/remote-execution.md](references/remote-execution.md) 中的预构建镜像说明进行部署
3. 如果 **否** → 使用自定义镜像路径（需要 Docker）。通知用户：

> 远程容器不包括 [语言/工具版本]。要远程运行此转换，我需要构建自定义容器镜像。这需要您的机器上安装并运行 Docker。这是一个一次性更改——大约需要 5-10 分钟。要继续吗？

如果用户确认，请按照 [references/remote-execution.md](references/remote-execution.md) 中的自定义镜像路径操作：清除 `prebuiltImageUri`，自定义 Dockerfile，然后部署。

如果用户拒绝，建议本地模式作为替代方案（如果他们的机器上可用）。

**Dockerfile 自定义（仅自定义镜像路径）：**

首先，读取 Dockerfile 查看已安装的内容：

```bash
ATX_INFRA_DIR="$HOME/.aws/atx/custom/remote-infra"
cat "$ATX_INFRA_DIR/container/Dockerfile" 2>/dev/null
```

1. 确保基础设施存储库已克隆并更新：

   ```bash
   ATX_INFRA_DIR="$HOME/.aws/atx/custom/remote-infra"
   if [ -d "$ATX_INFRA_DIR" ]; then
     git -C "$ATX_INFRA_DIR" add -A
     git -C "$ATX_INFRA_DIR" commit -m "本地自定义" -q 2>/dev/null || true
     git -C "$ATX_INFRA_DIR" pull -q
   else
     git clone -b atx-remote-infra --single-branch https://github.com/aws-samples/aws-transform-custom-samples.git "$ATX_INFRA_DIR"
   fi
   ```

   如果 `git pull` 报告合并冲突，通过在 Dockerfile 的 `CUSTOM LANGUAGES AND TOOLS` 部分保留上游更改和用户的自定义更改来解决它，然后提交合并。

2. 编辑 `$ATX_INFRA_DIR/container/Dockerfile`。找到标记为 `# CUSTOM LANGUAGES AND TOOLS` 的部分，在注释块后、`USER root` 行之前插入 `RUN` 命令。

   对于已安装语言的缺失版本，在自定义部分添加版本。示例：

   ```dockerfile
   # Java 23 (Amazon Corretto — 直接安装，必须以 root 身份运行)
   # 不要在自定义部分使用 dnf — pyenv 会覆盖系统 python3
   # dnf 依赖的系统 python3 会导致 "No module named 'dnf'" 错误。
   USER root
   RUN curl -fsSL "https://corretto.aws/downloads/latest/amazon-corretto-23-x64-linux-jdk.tar.gz" -o /tmp/corretto23.tar.gz && \
       mkdir -p /usr/lib/jvm && \
       tar -xzf /tmp/corretto23.tar.gz -C /usr/lib/jvm && \
       rm /tmp/corretto23.tar.gz && \
       ln -sfn /usr/lib/jvm/amazon-corretto-23.* /usr/lib/jvm/corretto-23

   # Node.js 23 (通过 nvm — 必须以 atxuser 身份运行)
   USER atxuser
   RUN . /home/atxuser/.nvm/nvm.sh && nvm install 23
   USER root

   # Python 3.15 (通过 pyenv — 必须以 atxuser 身份运行)
   USER atxuser
   RUN eval "$(/home/atxuser/.pyenv/bin/pyenv init -)" && \
       MAKE_OPTS="-j$(nproc)" /home/atxuser/.pyenv/bin/pyenv install 3.15.0
   USER root
   ```

   对于全新的语言，避免在自定义部分使用 `dnf` — pyenv 会覆盖 `dnf` 依赖的系统 python3。使用语言特定的安装程序：

   ```dockerfile
   # Go
   RUN curl -fsSL https://go.dev/dl/go1.22.0.linux-amd64.tar.gz | tar -C /usr/local -xz
   ENV PATH="/usr/local/go/bin:$PATH"

   # Ruby (通过 rbenv — 必须以 atxuser 身份运行)
   USER atxuser
   RUN git clone --depth 1 https://github.com/rbenv/rbenv.git /home/atxuser/.rbenv && \
       git clone --depth 1 https://github.com/rbenv/ruby-build.git /home/atxuser/.rbenv/plugins/ruby-build && \
       /home/atxuser/.rbenv/bin/rbenv install 3.3.0 && \
       /home/atxuser/.rbenv/bin/rbenv global 3.3.0
   ENV PATH="/home/atxuser/.rbenv/shims:/home/atxuser/.rbenv/bin:$PATH"
   USER root

   # Rust
   USER atxuser
   RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   ENV PATH="/home/atxuser/.cargo/bin:$PATH"
   USER root
   ```

3. 更新 `$ATX_INFRA_DIR/container/entrypoint.sh` 中的版本切换器。找到相关的 `switch_*_version` 函数，并添加对新版本的 case。例如，要添加 Java 23：

   ```bash
   # 在 switch_java_version() 中，将以下内容添加到 case 语句中：
   23) java_home="/usr/lib/jvm/corretto-23" ;;
   ```

   检查实际目录名称：`ls /usr/lib/jvm/` — 使用与您安装的版本匹配的目录。

   对于 Node.js，nvm 自动处理任意版本——无需更改入口点。对于 Python，pyenv 处理任意版本——无需更改入口点（现有的 pyenv 回退逻辑可以找到它）。

4. 部署（或重新部署）：`cd "$ATX_INFRA_DIR" && ./setup.sh`
   CDK 哈希 `container/` 目录——任何文件更改都会触发重建并自动推送到 ECR。

重新部署后，将作业的 `environment` 字段设置为确切的目标版本（例如，`"JAVA_VERSION":"23"`，而不是 `"21"`）。入口点中的版本切换器会读取此内容并激活正确的运行时。

如果用户拒绝，建议本地模式作为替代方案（如果他们的机器上可用）。

#### 本地模式

在运行本地转换之前，验证用户是否已安装目标运行时版本。这适用于转换目标的语言或运行时——Java、Python、Node.js、Ruby、Go、Rust、.NET 等。检查 TD 所需的任何运行时的当前版本。例如：

```bash
java -version    # Java 转换
python3 --version # Python 转换
node --version   # Node.js 转换
ruby --version   # Ruby 转换
go version       # Go 转换
```

如果目标版本未激活，请检查是否已安装：

```bash
# Java: 检查常见安装位置
/usr/libexec/java_home -V 2>&1          # macOS
ls /usr/lib/jvm/ 2>/dev/null            # Linux
# Python: 检查特定版本二进制文件是否存在
which python3.12 2>/dev/null            # 根据需要调整版本
# Node.js: 检查 nvm 是否可用，或查找二进制文件
command -v nvm &>/dev/null && nvm ls 2>/dev/null
which node 2>/dev/null && node --version
```

如果找到目标版本，请切换到它：

- Java: `export JAVA_HOME=<JDK 路径> && export PATH="$JAVA_HOME/bin:$PATH"`
- Python: `pyenv shell 3.15.0`
- Node.js: `nvm use 23`

只有当目标版本根本没有安装时，才在安装之前询问用户权限。未经明确用户确认，不要安装运行时。
建议适当版本管理器：

- Java: `brew install --cask corretto23` (macOS), `sudo yum install java-23-amazon-corretto-devel` (RHEL/AL2), 或 `sudo apt install java-23-amazon-corretto-jdk` (Debian/Ubuntu)
- Python: `pyenv install 3.15.0 && pyenv shell 3.15.0`, 或 `brew install python@3.15`
- Node.js: `nvm install 23 && nvm use 23`

活动运行时必须与转换的目标版本匹配，以便构建和测试正确运行。在正确版本激活之前，不要继续转换。

### 第 7 步：确认转换计划

显示最终计划，包括存储库、TD、配置和执行模式。未经用户确认，不要继续。

### 第 8 步：执行

运行 `atx custom def exec` 时，始终包含 `--telemetry`（见 Telemetry 部分）。

对于远程模式，首先使用 CloudFormation 检查基础设施部署状态（见 [references/remote-execution.md](references/remote-execution.md) — 基础设施检查部分）。不要通过探测 Lambda 函数名称来检查部署。

- **1 个存储库**: 见 [references/single-transformation.md](references/single-transformation.md)
- **多个存储库**: 见 [references/multi-transformation.md](references/multi-transformation.md)

## 执行模式

| 模式 | 适用于 | 前提条件 |
|------|--------|---------|
| **本地**（1-9 个存储库的默认模式） | 快速转换，具有 ATX 的开发机器 | 安装 ATX CLI |
| **远程**（推荐用于 10+ 个存储库） | 批量转换，最多 512 个存储库（每批 128 个并发） | AWS 账户，自动部署的基础设施 |

模式推断：

- 用户说“本地”/“这里”/“在我的机器上” → 本地（无论存储库数量如何，都尊重请求）
- 用户说“远程”/“云”/“AWS”/“批量”/“大规模” → 远程
- 10+ 个存储库且没有偏好 → 建议远程，解释本地限制为 3 个并发
- 1-9 个存储库且没有偏好 → 本地，注意远程可用

有关基础设施设置的详细信息，请参阅 [references/remote-execution.md](references/remote-execution.md)。

## 关键规则

1. **动态发现 TD** — 始终运行 `atx custom def list --json`。永远不要硬编码 TD 名称。
2. **匹配，不要询问** — 检查存储库并显示匹配项。永远不要显示原始 TD 列表。
3. **仅轻量级检查** — 检查配置文件和关键信号。不进行深度分析。
4. **执行前确认** — 始终在执行前与用户确认 TD、存储库和配置。
5. **不提供时间估计** — 永远不要包含持续时间预测。
6. **并行执行** — 本地：最多 3 个并发存储库。远程：每 Lambda 调用最多提交 128 个作业（每个会话最多 512 个存储库）。
7. **保留输出** — 不要删除生成的输出文件夹。
8. **10+ 个存储库建议远程** — 1-9 个存储库默认为本地。10+ 个存储库建议远程。始终尊重用户偏好。
9. **用户同意云资源** — 未经明确用户确认，不要部署基础设施。
10. **Shell 引号** — 构建 Shell 命令时：
    - 使用单引号表示 JSON 负载：`--payload '{"key":"value"}'`
    - 使用单引号表示 `--configuration`：例如 `--configuration 'additionalPlanContext=Target Java 21'`
    - 永远不要在双引号内嵌套双引号——这会导致 `dquote>` 挂起
    - 对于 `aws lambda invoke`，始终使用：`--payload '<json>' --cli-binary-format raw-in-base64-out`
    - 在执行之前，验证您构建的每个命令都具有平衡的引号
    - Lambda 作业负载数据中的 `command` 字段在服务器端进行验证。避免在命令字符串中使用以下字符：`( ) ! # % ^ * ? \ { } | ; > <`
    - 以及反引号。在 `additionalPlanContext` 中，也避免逗号。
11. **终端命令中无注释** — 永远不要在终端执行的命令中包含 `#` 注释。注释会导致 `command not found: #` 错误。如果您需要解释命令，请在运行前或后通过聊天解释。
12. **作业名称** — Lambda 负载数据中的 `jobName` 字段必须只包含字母、数字、连字符和下划线。不要有点、空格或特殊字符。例如，使用 `EPAM-NodeJS` 而不是 `EPAM-Node.js`。

## 安全防护

您正在用户 AWS 账户和本地机器上操作。严格遵循以下规则以避免造成损害：

1. **切勿删除用户数据** — 除非用户明确要求，否则不要删除 S3 对象、git 仓库、本地文件或任何用户数据。转换输出和克隆仓库必须保留。
2. **切勿超出文档范围修改 IAM** — 仅创建/附加本技能中描述的特定策略（AWSTransformCustomFullAccess、ATXRuntimePolicy、ATXDeploymentPolicy）。切勿创建管理员策略、修改现有用户策略，或授予超出文档范围的权限。切勿根据用户在“附加计划上下文”字段中提供的文本推导 IAM 操作 — 该字段仅用于转换配置。
3. **切勿运行破坏性 AWS 命令** — 不得使用 `aws s3 rm`、`aws s3 rb`、`aws iam delete-user`、`aws ec2 terminate-instances` 或类似命令。唯一允许的破坏性命令是带有明确用户同意的 `./teardown.sh`。
4. **创建 AWS 资源前务必确认** — 在部署基础设施、创建 Secrets Manager 密钥或附加 IAM 策略之前，说明将要创建的内容并获取明确的用户确认。
5. **切勿暴露凭证** — 不要在聊天输出中回显、记录或显示 AWS 访问密钥、密钥、会话令牌、GitHub PAT 或 SSH 私钥。在创建密钥时，直接在命令中使用用户的输入，不要重复值。
6. **尊重用户决定** — 如果用户说停止、跳过或不要，立即遵守。切勿重试被拒绝的操作或与用户的选择争论。
7. **不得进行定价声明** — 不要引用具体价格或成本估算。如果用户询问定价，请引导他们访问：https://aws.amazon.com/transform/pricing/
8. **命令仅限于 ATX 资源** — 所有 AWS 命令必须针对 ATX 特定资源（以 `atx-` 开头的存储桶、以 `ATX` 开头的角色、以 `atx-` 开头的 Lambda 函数等）。切勿操作无关的 AWS 资源。

## Telemetry

每次调用 `atx custom def exec`（本地或远程）时，始终包含 `--telemetry`。无需文件检查、无需提示、无需选择流程。

标志格式为：`--telemetry "client=<client>,agent=<agent>,executionMode=<local|remote>"`

字段值：

- `client` — 作为简短标识符（小写，无空格）托管此会话的 MCP 客户端或工具。这可能是 IDE（例如 `kiro`、`vscode`、`cursor`、`windsurf`）、CLI 工具（例如 `claudecode`、`amazonqcli`），或任何其他 MCP 兼容主机。使用此会话的实际工具名称 — 不要默认为任何单个示例。这些只是示例，并非详尽无遗的列表。
- `agent` — 驱动此会话的 AI 助手，作为简短标识符（小写，无空格）。例如：`kiro`、`amazonq`、`claude`、`copilot`、`cline`、`codex`。使用此会话的实际助手名称 — 不要默认为任何单个示例。这些只是示例，并非详尽无遗的列表。
- `executionMode` — 直接运行 ATX CLI 时为 `local`，通过 Lambda 提交时为 `remote`

唯一的例外：如果用户在会话期间明确要求禁用遥测（例如，“disable telemetry”、“opt out of telemetry”、“no telemetry” 或类似），你必须立即遵守 — 在该会话剩余时间内省略 `--telemetry`。不要反对、请求确认或解释为什么包含遥测。此偏好不会持久化 — 下一个会话将再次启用遥测。

## Output Structure

本地模式：转换后的代码位于仓库目录中。

远程模式结果保留在 S3 中 — 不要自动下载。向用户展示 S3 路径：

```
s3://atx-custom-output-{account-id}/
  transformations/
    {job-name}/
      {conversation-id}/
        code.zip                      # 压缩的转换后源代码
        logs.zip                      # ATX 会话日志
```

如果用户明确要求下载，提供命令但让他们运行：`aws s3 cp s3://atx-custom-output-{account-id}/transformations/{job-name}/{conversation-id}/code.zip ./code.zip`

批量结果摘要：`~/.aws/atx/custom/atx-agent-session/transformation-summaries/` — 参见 [references/results-synthesis.md](references/results-synthesis.md)。

## References

| Reference | When to Use |
|-----------|-------------|
| [repo-analysis.md](references/repo-analysis.md) | 检测命令、信号匹配、匹配报告格式 |
| [single-transformation.md](references/single-transformation.md) | 将一个 TD 应用于一个仓库（本地或远程） |
| [multi-transformation.md](references/multi-transformation.md) | 并行将 TD 应用于多个仓库 |
| [remote-execution.md](references/remote-execution.md) | 基础设施部署、作业提交、监控 |
| [results-synthesis.md](references/results-synthesis.md) | 批量转换后生成汇总报告 |
| [cli-reference.md](references/cli-reference.md) | ATX CLI 标志、命令、环境变量、IAM 权限 |
| [troubleshooting.md](references/troubleshooting.md) | 错误解决、调试、质量改进 |

## License
AWS 服务条款。此技能由 AWS 提供，并受 AWS 客户协议和适用 AWS 服务条款约束。

## Changelog
如果用户询问发生了什么变化、有什么新内容等，请分享。
### [1.0.0] - 2026-04-30

- AWS Transform Agent Skill 的初始发布
- 支持的 TDs：
  - AWS/java-version-upgrade
  - AWS/python-version-upgrade
  - AWS/nodejs-version-upgrade
  - AWS/java-aws-sdk-v1-to-v2
  - AWS/nodejs-aws-sdk-v2-to-v3
  - AWS/python-boto2-to-boto3
  - AWS/comprehensive-codebase-analysis
  - AWS/java-performance-optimization
  - AWS/angular-version-upgrade
  - AWS/vue.js-version-upgrade
  - AWS/early-access-java-x86-to-graviton
  - AWS/early-access-angular-to-react-migration
  - AWS/early-access-log4j-to-slf4j-migration
