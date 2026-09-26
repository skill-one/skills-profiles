# AWS Transform (ATX)

## 概述

使用 AWS Transform (ATX) 执行代码升级、迁移和转换。
支持任何到任何的转换：语言版本升级（Java、Python、Node.js 等）、框架迁移、AWS SDK 迁移、库升级、代码重构、架构变更和自定义组织特定转换。

两种执行模式：

- **本地模式**：直接在用户机器上运行 ATX CLI。适用于 1-9 个存储库。
- **远程模式**：通过 AWS Batch/Fargate 容器大规模运行转换。适用于 10+ 个存储库或当用户更喜欢云执行时。基础设施在用户同意的情况下自动部署。

您处理完整的工作流程：检查存储库、将它们与可用的转换定义匹配、收集配置，并在任何模式下执行转换——用户只需提供存储库并确认计划。

## 问候和等待

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

在用户响应之前，不要检查任何文件、运行任何命令或检查先决条件。

## 使用

当用户想要执行以下操作时使用：

- 转换、升级或迁移代码（Java、Python、Node.js 等）
- 迁移 AWS SDKs (Java SDK v1→v2, boto2→boto3, JS SDK v2→v3 等)
- 通过 AWS Batch/Fargate 执行大规模代码转换
- 分析哪些 ATX 转换适用于其存储库
- 执行全面代码库分析
- 创建新的自定义转换定义 (TD)

## 核心概念

- **转换定义 (TD)**：通过 `atx custom def list --json` 发现的可重用转换配方
- **匹配报告**：根据代码检查自动生成的存储库到适用 TD 的映射
- **本地模式**：在用户机器上运行 ATX CLI（1-9 个存储库，最大 3 个并发）
- **远程模式**：在 AWS Batch/Fargate 中运行转换（10+ 个存储库，或按用户偏好）

## 哲学

等待用户。激活时，展示此技能可以做什么，并询问用户他们想要完成什么。不要自动检查工作目录、打开文件或任何存储库，直到用户明确提供要与之工作的存储库。

一旦用户提供存储库，就匹配——不要询问。检查这些存储库并自动展示哪些转换适用。永远不要显示原始 TD 列表并要求用户选择。

## 先决条件

在会话开始时运行一次先决条件检查。不要按每个存储库重复检查。在用户说明他们想要做什么之前，不要运行先决条件检查。

### 0. 平台检查（必需——所有模式）

检测用户的操作系统。如果是在 Windows（不是 WSL）上，请立即停止并通知用户：

> AWS Transform custom 不支持原生 Windows。您需要安装 Windows 子系统 for Linux (WSL) 并在 WSL 中运行此命令。
>
> 安装 WSL：在 PowerShell 中以管理员身份运行 `wsl --install`，然后重新启动。
> 然后打开 WSL 终端并从那里重新运行此技能。

通过运行以下命令进行检查：

```bash
uname -s
```

- `Linux` 或 `Darwin` → 正常进行
- `MINGW*`, `MSYS*`, `CYGWIN*` 或任何 Windows 类似输出 → 阻止并显示上述 WSL 消息
- 命令失败、错误或未找到 → 治为原生 Windows，阻止并显示上述 WSL 消息

不要在原生 Windows 上执行任何其他步骤。

### 1. AWS CLI（必需——所有模式）

```bash
aws --version
```

如果未安装，请指导用户：

- macOS: `brew install awscli` 或 `curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg" && sudo installer -pkg AWSCLIV2.pkg -target /`
- Linux: `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install`

不要在 `aws --version` 成功之前继续。

### 2. AWS 凭证（必需——所有模式）

```bash
aws sts get-caller-identity
```

如果凭证未配置，请引导用户进行设置：

```
AWS Transform custom 需要 AWS 凭证来验证服务。使用以下方法之一配置验证。

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

您也可以使用 AWS_PROFILE 环境变量指定配置文件：

export AWS_PROFILE=your_profile_name
```

不要在凭证验证之前继续。设置后重新运行 `aws sts get-caller-identity`。

注意：通过 `export` 设置的环境变量不会在 shell 会话之间传递。如果代理生成新的 shell，则可能丢失通过环境变量设置的凭证。优先使用 `aws configure` 或 `~/.aws/credentials` 以实现持久化。

### 3. ATX CLI（必需——所有模式）

所有模式下都需要它来发现 TD (`atx custom def list --json`)。本地模式下也用于转换执行。

```bash
atx --version
# 安装: curl -fsSL https://transform-cli.awsstatic.com/install.sh | bash
```

**强制执行：** 在每个会话开始时始终运行 `atx update`，即使您最近刚刚运行过它。这可以捕获新的 ATX CLI 版本和新的 TD。在运行任何其他 ATX 命令（包括 `atx custom def list --json`）之前运行它：

```bash
atx update
```

不要跳过此步骤。不要询问用户是否要更新。不要根据 CLI 是否“需要”更新来决定。无条件运行它。

### 4. IAM 权限（必需——所有模式）

本地模式下需要 `transform-custom:*` 最小权限。通过运行 TD 列表进行验证：

```bash
atx custom def list --json
```

如果它成功，权限就足够了——跳过本节的其余部分。

如果它因权限错误而失败，调用者需要 `transform-custom:*` IAM 权限。向用户解释需要什么，并在继续之前获得确认：

> 您的身份需要 `transform-custom:*` 权限才能使用 ATX CLI。
> 我可以将 AWS 管理的策略 `AWSTransformCustomFullAccess` 附加到您的身份。您要继续吗？

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

如果附加命令本身失败（例如，IAM 权限不足，或 SSO 管理的角色），请告知用户他们需要请求他们的 AWS 管理员将 `AWSTransformCustomFullAccess` AWS 管理策略附加到他们的身份。对于 SSO 用户（角色名以 `AWSReservedSSO_` 开头），必须在他们的 IAM Identity Center 权限集中添加此内容——不能直接附加。

不要在 `atx custom def list --json` 成功之前继续。

远程模式下需要额外的权限（Lambda 调用、S3、KMS、Secrets Manager、CloudWatch）。这些是在部署流程中生成和附加的——请参阅 [references/remote-execution.md](references/remote-execution.md)。

参见 [references/cli-reference.md](references/cli-reference.md) 获取完整权限列表。

### 5. AWS CDK（远程模式仅）

仅用于部署远程基础设施。检查是否安装：

```bash
cdk --version
```

如果未安装，请全局安装它：

```bash
npm install -g aws-cdk
```

不要在远程部署之前 `cdk --version` 成功之前继续。

### 6. 远程基础设施（远程模式仅——延迟）

仅在使用远程模式时验证。基础设施 CDK 脚本在运行时通过克隆 `https://github.com/aws-samples/aws-transform-custom-samples.git`（分支 `atx-remote-infra`）获取——它们不随此技能捆绑。请参阅 [references/remote-execution.md](references/remote-execution.md)。

## 工作流程

生成一次会话时间戳，并在本会话的所有路径中重用它：

```bash
SESSION_TS=$(date +%Y%m%d-%H%M%S)
```

### 第 1 步：收集存储库

询问用户本地路径或 git URL。接受一个或多个。不要假设当前工作目录或打开的编辑器文件是目标——等待用户明确提供存储库。

接受的源格式：

- **本地路径**——用户机器上的目录（例如，`/home/user/my-project`）
- **HTTPS git URL**——公共或私有（例如，`https://github.com/org/repo.git`）
- **SSH git URL**——例如，`git@github.com:org/repo.git`
- **S3 存储桶路径与 zip 文件**——例如，`s3://my-bucket/repos/`
  包含存储库 zip 文件的存储桶。每个 zip 变成一个转换作业。

#### S3 桶输入

如果用户提供一个包含 zip 文件的 S3 路径，请询问他们更喜欢哪种执行模式（如果尚未指定）。S3 输入适用于两种模式：

**远程模式**：将 zips 从用户的桶复制到管理的源桶，然后提交指向管理副本的作业：

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
SOURCE_BUCKET="atx-source-code-${ACCOUNT_ID}"

# 列出用户桶路径中的所有 zips
aws s3 ls s3://user-bucket/repos/ --recursive | grep '\.zip$'

# 将每个 zip 复制到管理的源桶
aws s3 sync s3://user-bucket/repos/ s3://${SOURCE_BUCKET}/repos/ --exclude "*" --include "*.zip"
```

然后提交一个批处理作业，每个 zip 一个作业，每个作业都指向 `s3://${SOURCE_BUCKET}/repos/<filename>.zip`。容器自动处理 zip 提取。参见 [references/multi-transformation.md](references/multi-transformation.md) 以批处理方式提交。管理的源桶具有 7 天的生命周期——复制的 zips 将自动删除。

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

**始终询问用户**——不要尝试自行确定存储库的可见性。永远不要尝试克隆、curl 或探测 URL 来检查它是否为公共或私有。只需询问用户。一旦用户提供 git URL 并选择远程模式（或可能），请询问：

> "这些存储库中有任何私有的吗？如果是，远程容器需要凭证来克隆它们——我将引导您进行设置。"

不要跳过此问题。不要尝试通过尝试克隆、curl 或任何其他网络请求来推断可见性。只需询问。

如果用户确认存储库是私有的，根据 URL 格式确定凭证类型：

首先，解析区域（用于所有 Secrets Manager 命令）：

```bash
REGION=${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null)}}
REGION=${REGION:-us-east-1}
```

**对于 HTTPS URL**——检查是否已经配置了 GitHub PAT：

```bash
aws secretsmanager describe-secret --secret-id "atx/github-token" --region "$REGION" 2>/dev/null \
  && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

如果 CONFIGURED，询问用户："已经存储了 GitHub PAT。您想继续使用它，还是用新的替换它？" 如果他们想替换它，告诉他们运行：

```
aws secretsmanager put-secret-value --secret-id "atx/github-token" --region "$REGION" --secret-string "YOUR_TOKEN_HERE"
```

如果 NOT_CONFIGURED，解释需要什么，并告诉用户运行创建命令：
> "私有 HTTPS 存储库需要存储在 AWS Secrets Manager 中的 GitHub Personal Access Token (PAT)。远程容器在启动时获取它来克隆您的存储库。
> 该令牌保留在您的 AWS 账户中——您可以随时删除它。
>
> PAT 需要对私有存储库具有 `repo` 范围。在 https://github.com/settings/tokens 中创建一个，然后运行：
>
> ```
> aws secretsmanager create-secret --name "atx/github-token" --region "$REGION" --secret-string "YOUR_TOKEN_HERE"
> ```
>
> 随时可以删除：`aws secretsmanager delete-secret --secret-id atx-token --region "$REGION" --force-delete-without-recovery"`

不要要求用户在聊天中粘贴他们的令牌。他们自己运行命令。等待用户确认它已完成，然后验证：

```bash
aws secretsmanager describe-secret --secret-id "atx/github-token" --region "$REGION" 2>/dev/null \
  && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

**对于 SSH URL** (`git@...` 或 `ssh://...`)——检查是否配置了 SSH 密钥：

```bash
aws secretsmanager describe-secret --secret-id "atx/ssh-key" --region "$REGION" 2>/dev/null \
  && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

如果 CONFIGURED，询问用户："已经存储了 SSH 密钥。您想继续使用它，还是用新的替换它？" 如果他们想替换它，告诉他们运行：

```
aws secretsmanager put-secret-value --secret-id "atx/ssh-key" --region "$REGION" --secret-string "$(cat <path-to-your-private-key>)"
```

如果 NOT_CONFIGURED，解释需要什么，并告诉用户运行创建命令：
> "SSH 存储库需要存储在 AWS Secrets Manager 中的 SSH 私有密钥。远程容器在启动时获取它来克隆您的存储库。
>
> 运行：
>
> ```
> aws secretsmanager create-secret --name "atx/ssh-key" --region "$REGION" --secret-string "$(cat <path-to-your-private-key>)"
> ```
>
> 随时可以删除：`aws secretsmanager delete-secret --secret-id atx-key --region "$REGION" --force-delete-without-recovery"`

不要要求用户在聊天中粘贴他们的 SSH 密钥。他们自己运行命令。

对于本地模式，不需要私有库凭证——用户的本地 git 配置处理身份验证。对于本地模式，完全跳过此检查。

### 第 2 步：发现 TD（静默）

静默运行——不要向用户显示输出：

```bash
atx custom def list --json
```

直接检查 JSON 输出以构建内部可用 TD 查找表。不要将输出管道到 python、jq 或其他解析脚本——自己读取 JSON。永远不要硬编码 TD 名称。

#### 创建新的 TD

**用户明确要求创建 TD**：不要尝试以编程方式创建一个。告诉用户：

> 要创建新的转换定义，请打开一个新终端并运行：
>
> ```
> atx -t
> ```
>
> 这将启动一个交互式会话，您可以在其中描述您想要构建的转换（例如，“将所有日志从 log4j 迁移到 SLF4J”，“将 Spring Boot 2 升级到 Spring Boot 3”）。ATX CLI 将引导您完成 TD 的定义和测试，然后将其发布到您的 AWS 账户。
>
> 一旦它发布，回来这里，当扫描您的可用 TD 时，我会自动获取它。

**没有现有的 TD 匹配用户的 goal**：不要默默地重定向到 TD 创建。匹配逻辑可能不完美。相反，首先与用户确认：

> "我没有找到现有的 TD 可以覆盖 [描述用户的 goal]。您想创建一个新的吗？"

只有在用户确认后，才显示 `atx -t` 说明。如果他们说不，请询问他们到底在寻找什么——他们可能知道 TD 名称或想要不同的方法。

不要自己运行 `atx -t`——它需要交互式终端会话，代理无法驱动。用户必须在单独的终端中手动运行它。

用户返回创建 TD 后，重新运行 `atx custom def list --json` 以获取新发布的 TD 并继续正常工作流程。

### 第 1 步：检查每个存储库

仅执行轻量级检查——检查配置文件以检查关键信号：

| 信号 | 要检查的文件 | 可能的 TD 类型 |
|------|-------------|----------------|
| Python 版本 | `.python-version`, `pyproject.toml`, `setup.cfg`, `requirements.txt` | Python 版本升级 |
| Java 版本 | `pom.xml` (`<java.version>`), `build.gradle` (`sourceCompatibility`), `.java-version` | Java 版本升级 |
| Node.js 版本 | `package.json` (`engines.node`), `.nvmrc`, `.node-version` | Node.js 版本升级 |
| Python boto2 | `import boto` (NOT boto3) | boto2→boto3 迁移 |
| Java SDK v1 | `com.amazonaws` 导入, `aws-java-sdk` 在 pom.xml | Java SDK v1→v2 |
| Node.js SDK v2 | `"aws-sdk"` in package.json (NOT `@aws-sdk`) | JS SDK v2→v3 |
| x86 Java | Dockerfiles 中的 `x86_64`/`amd64`, 构建配置 | Graviton 迁移 |

将检测到的信号与第 2 步中的 TD 进行交叉引用。仅匹配用户帐户中实际存在的 TD。

参见 [references/repo-analysis.md](references/repo-analysis.md) 获取完整的检测命令。

### 第 2 步：展示匹配报告

格式：

```
转换匹配报告
=============================
存储库: <name> (<path>)
  语言: <lang> <version>
  匹配的 TD:
    - <td-name> — <description>

摘要: N 个存储库分析，M 个有适用的转换 (T 个作业)
```

展示匹配报告并等待用户确认后再继续。不要在未经明确用户同意的情况下开始任何转换。

### 第 3 步：收集配置

询问用户任何额外的计划上下文（例如，升级 TDs 的目标版本）。这是强制性的——始终询问，即使 TD 不严格要求配置。用户可能有代理不知道的偏好或限制。只有在用户明确表示不需要任何额外上下文的情况下才跳过。

### 第 1 步：验证运行时兼容性（远程和本地）

#### 远程模式

在提交远程作业之前，确定预构建镜像是否包含目标运行时或是否需要自定义 Docker 构建。

**预构建镜像包括：**

- **Java**: 8, 11, 17, 21, 25 (Amazon Corretto) 与 Maven 和 Gradle 9.4
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 (dnf + pyenv)
- **Node.js**: 16, 18, 20, 22, 24 (nvm) 与 yarn, pnpm, TypeScript, ts-node
- **构建工具**: gcc, g++, make, patch
- **CLI 工具**: AWS CLI v2, ATX CLI, git, jq, curl, unzip, tar
- **操作系统**: Amazon Linux 2023 (x86_64)

**决策逻辑：**

1. 根据转换要求（源运行时、目标运行时、构建工具和任何其他依赖项），确定所有需要的内容是否都包含在上述预构建镜像中
2. 如果 **是** → 使用预构建镜像路径（无需 Docker）。继续使用预构建镜像说明在 [references/remote-execution.md](references/remote-execution.md) 中的部署。
3. 如果 **否** → 使用自定义镜像路径（需要 Docker）。通知用户：

> 远程容器不包含 [语言/工具版本]。要远程运行此转换，我需要构建一个自定义容器镜像。这需要 Docker 安装并运行在您的机器上。这是一个一次性更改——大约需要 5-10 分钟。您要继续吗？

如果用户确认，请按照 [references/remote-execution.md](references/remote-execution.md) 中的自定义镜像路径：清除 `prebuiltImageUri`，自定义 Dockerfile，并部署。

如果用户拒绝，建议本地模式作为替代方案（如果他们的机器上有可用的工具）。

**Dockerfile 自定义（自定义镜像路径仅限）：**

首先，读取 Dockerfile 以查看已安装的内容：

```bash
ATX_INFRA_DIR="$HOME/.aws/atx/custom/remote-infra"
cat "$ATX_INFRA_DIR/container/Dockerfile" 2>/dev/null
```

1. 确保基础设施存储库已克隆并更新：

   ```bash
   ATX_INFRA_DIR="$HOME/.aws/atx/custom/remote-infra"
   if [ -d "$ATX_INFRA_DIR" ]; then
     git -C "$ATX_INFRA_DIR" add -A
     git -C "$ATX_INFRA_DIR" commit -m "Local customizations" -q 2>/dev/null || true
     git -C "$ATX_INFRA_DIR" pull -q
   else
     git clone -b atx-remote-infra --single-branch https://github.com/aws-samples/aws-transform-custom-samples.git "$ATX_INFRA_DIR"
   fi
   ```

如果 `git pull` 报告合并冲突，通过保留上游更改和用户的自定义化内容来解决：在 Dockerfile 的 `# CUSTOM LANGUAGES AND TOOLS` 部分中保留两者，然后提交合并。

2. 编辑 `$ATX_INFRA_DIR/container/Dockerfile`。找到标记为 `# CUSTOM LANGUAGES AND TOOLS` 的部分，在注释块之后、`USER root` 行之前插入 `RUN` 命令。

   对于已安装语言的缺失版本，在自定义部分添加版本。示例：

   ```dockerfile
   # Java 23 (Amazon Corretto — 直接安装，必须以 root 身份运行)
   # 不要在自定义部分使用 dnf——pyenv 会覆盖 dnf 依赖的系统 python3，导致 "No module named 'dnf'" 错误。
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

   对于完全新的语言，避免在自定义部分使用 dnf——pyenv 会覆盖 dnf 依赖的系统 python3。使用语言特定的安装程序：

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

3. 更新 `$ATX_INFRA_DIR/container/entrypoint.sh` 中的版本切换器。
   找到相关的 `switch_*_version` 函数，并添加新版本的 case。对于通过直接下载安装的 Java 版本，找到 `/usr/lib/jvm/` 下的提取目录名。例如，要添加 Java 23：

   ```bash
   # 在 switch_java_version() 中添加到 case 语句：
   23) java_home="/usr/lib/jvm/corretto-23" ;;
   ```

   实际目录名称：`ls /usr/lib/jvm/`——使用与您安装的版本匹配的目录。

   对于 Node.js，nvm 处理任意版本，无需更改入口点。对于 Python，pyenv 处理任意版本，无需更改入口点（pyenv 落后的逻辑可以找到它）。

4. 部署（或重新部署）：`cd "$ATX_INFRA_DIR" && ./setup.sh`
   CDK 对 `container/` 目录进行哈希处理——任何文件更改都会触发重建和自动推送到 ECR。

重新部署后，将作业的 `environment` 字段设置为确切的目标版本（例如，`"JAVA_VERSION":"23"`，而不是 `"21"`）。入口点中的版本切换器读取此内容并激活正确的运行时。

如果用户拒绝，建议本地模式作为替代方案（如果他们的机器上有可用的工具）。

#### 本地模式

在运行本地转换之前，验证用户是否安装了目标运行时版本。这适用于任何语言或运行时，Java、Python、Node.js、Ruby、Go、Rust、.NET 等。检查所需运行时的当前版本。例如：

```bash
java -version    # Java 转换
python3 --version # Python 转换
node --version   # Node.js 转换
ruby --version   # Ruby 转换
go version       # Go 转换
```

如果目标版本不存在，请检查是否已安装：

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

如果找到目标版本，切换到它：

- Java: `export JAVA_HOME=<path to JDK> && export PATH="$JAVA_HOME/bin:$PATH"`
- Python: `pyenv shell 3.15.0`
- Node.js: `nvm use 23`

只有在目标版本完全未安装时，才在用户明确同意安装后询问用户。不要在未经明确用户确认的情况下安装运行时。
建议使用适当的版本管理器：

- Java: `brew install --cask corretto23` (macOS), `sudo yum install java-23-amazon-corretto-devel` (RHEL/AL2), 或 `sudo apt install java-23-amazon-corretto-jdk` (Debian/Ubuntu)
- Python: `pyenv install 3.15.0 && pyenv shell 3.15.0`, 或 `brew install python@3.15`
- Node.js: `nvm install 23 && nvm use 23`

活动的运行时必须与转换的目标版本匹配，以便构建和测试运行正确。在正确的版本激活之前，不要继续转换。

### 第 7 步：确认转换计划

展示最终计划，包括存储库、TD、配置和执行模式。在用户确认之前，不要继续。

### 第 8 步：执行

运行 `atx custom def exec` 时，始终包含 `--telemetry`（参见 telemetry 部分）。

对于远程模式，首先检查基础设施部署状态，使用 CloudFormation（参见 [references/remote-execution.md](references/remote-execution.md) 中的 Infrastructure Check 部分）。不要通过探测 Lambda 函数名称来检查部署。

- **1 个存储库**: 见 [references/single-transformation.md](references/single-transformation.md)
- **多个存储库**: 见 [references/multi-transformation.md](references/multi-transformation.md)

## 执行模式

| 模式 | 最佳用途 | 先决条件 |
|------|----------|---------------|
| **本地**（1-9 个存储库的默认模式） | 快速转换，开发机器上安装了 ATX | ATX CLI 安装 |
| **远程**（10+ 个存储库推荐） | 批量转换，最多 512 个存储库（最多 128 个并发每个批次） | AWS 账户，自动部署的基础设施 |

模式推断：

- 用户说 "本地"/"这里"/"在我的机器上" → 本地（无论存储库数量如何，都尊重用户请求）
- 用户说 "远程"/"云"/"AWS"/"batch"/"大规模" → 远程
- 10+ 个存储库，没有偏好 → 推荐远程，解释本地最多 3 个并发的限制
- 1-9 个存储库，没有偏好 → 本地，注意远程可用

参见 [references/remote-execution.md](references/remote-execution.md) 获取基础设施设置。

## 关键规则

1. **动态发现 TDs** — 始终运行 `atx custom def list --json`。永远不要硬编码 TD 名称。
2. **匹配，不要询问** — 检查存储库并自动展示匹配项。永远不要显示原始 TD 列表并要求用户选择。
3. **仅轻量级检查** — 检查配置文件和关键信号。不要进行深度分析。
4. **执行前确认** — 始终在执行 TD、存储库和配置之前与用户确认。
5. **不提供时间估计** — 永远不要包含持续时间预测。
6. **并行执行** — 本地：最多 3 个并发存储库。远程：以最多 128 个作业的批次提交（每个会话最多 512 个存储库）。
7. **保留输出** — 不要删除生成的输出文件夹。
8. **10+ 个存储库推荐远程** — 默认为 1-9 个存储库提供本地。推荐 10+ 个存储库提供远程。始终尊重用户偏好。
9. **用户同意云资源** — 不要在未经明确用户同意的情况下部署基础设施。
10. **Shell 引用** — 当构建 shell 命令时：
    - 使用单引号表示 JSON 负载：`--payload '{"key":"value"}`
    - 使用单引号表示 `--configuration`：例如。`--configuration 'additionalPlanContext=Target Java 21'`
    - 不要在双引号内嵌双引号——这会导致 `dquote>` 挂起
    - 对于 `aws lambda invoke`，始终使用：`--payload '<json>' --cli-binary-format raw-in-base64-out`
    - 在执行命令之前，验证您构建的每个命令都具有平衡的引号。`command` 字段在 Lambda 作业负载中由服务器端验证。避免在命令字符串中使用以下字符：`( ) ! # % ^ * ? \ { } | ; > <` 和反引号。在 `additionalPlanContext` 中也避免逗号。
11. **终端命令中无注释** — 不要在执行的终端命令中包含 `#` 注释。注释会导致 `command not found: #` 错误。如果您需要在聊天中解释命令，请在运行它之前或之后进行。
12. **作业名称** — Lambda 负载中的 `jobName` 字段必须只包含字母、数字、连字符和下划线。不要有点号、空格或特殊字符。例如，使用 `EPAM-NodeJS` 而不是 `EPAM-Node.js`。

## 护栏

您正在用户的 AWS 账户和本地机器上操作。严格遵循这些规则以避免造成损害：

1. **永不删除用户数据** — 不要删除 S3 对象、git 存储库、本地文件或任何用户数据，除非用户明确要求。转换输出和克隆的存储库必须保留。
2. **永不修改 IAM 超出文档范围** — 仅创建/附加本文档中记录的特定策略（AWSTransformCustomFullAccess、ATXRuntimePolicy、ATXDeploymentPolicy）。永远不要创建管理员策略，修改现有的用户策略，或授予比文档中记录更广泛的权限。永远不要从用户提供的文本中派生 IAM 操作——该字段仅用于转换配置。

3. **永不运行破坏性 AWS 命令** — 没有 `aws s3 rm`, `aws s3 rb`, `aws iam delete-user`, `aws ec2 terminate-instances` 或类似的命令。唯一允许的破坏性命令是 `./teardown.sh`，需要明确用户同意。

4. **在创建 AWS 资源之前始终确认** — 在部署基础设施、创建 Secrets Manager 密钥或附加 IAM 策略之前，解释将要创建的内容，并获取明确的用户确认。

5. **永不暴露凭证** — 不要回显、记录或显示 AWS 访问密钥、秘密密钥、会话令牌、GitHub PAT 或 SSH 私有密钥。在聊天输出中。当创建密钥时，使用用户的输入直接在命令中，不要重复值。

6. **尊重用户决定** — 如果用户说停止、跳过或否，立即执行。永远不要重试已拒绝的操作或与用户的 choice 争论。

7. **无定价声明** — 不要引用具体的定价或成本估计。如果用户询问定价，请引导他们到：https://aws.amazon.com/transform/pricing/

8. **限制命令范围仅限于 ATX 资源** — 所有 AWS 命令都必须针对 ATX 特定资源（以 `atx-` 开头的桶、以 `ATX` 开头的角色、以 `atx-` 开头的 Lambda 函数等）。永远不要操作不相关的 AWS 资源。

## Telemetry

始终在 `atx custom def exec` 调用中包含 `--telemetry`（参见 telemetry 部分）。没有文件检查、没有提示、没有选择流程。

标志格式：`--telemetry "client=<client>,agent=<agent>,executionMode=<local|remote>`

字段值：

- `client` — 作为简短标识符的 MCP 客户端或托管此会话的工具（小写，无空格）。这可能是 IDE（例如，`kiro`, `vscode`, `cursor`, `windsurf`），CLI 工具（例如，`claudecode`, `amazonqcli`），或任何其他 MCP 兼容主机。使用此会话的真实工具名称——不要默认为任何单个示例。这些只是示例，不是详尽无遗的列表。

- `agent` — 驱动此会话的 AI 助手作为简短标识符（小写，无空格）。例如：`kiro`, `amazonq`, `claude`, `copilot`, `cline`, `codex`。使用此会话的真实助手名称——不要默认为任何单个示例。这些只是示例，不是详尽无遗的列表。

- `executionMode` — `local` 当直接运行 ATX CLI 时，`remote` 当通过 Lambda 提交时

唯一的例外：如果用户明确要求在会话期间禁用 telemetry（例如，“禁用 telemetry”, “opt out of telemetry”, “no telemetry” 或类似内容），您必须立即遵守——在会话的其余部分中省略 `--telemetry`。不要推回、询问确认或解释为什么 telemetry 包含在内。此偏好不是持久的——下一个会话重新启用 telemetry。

## 输出结构

本地模式：转换后的代码位于存储库目录中。

远程模式结果保留在 S3 中——不要自动下载。向用户展示 S3 路径：

```
s3://atx-custom-output-{account-id}/
  transformations/
    {job-name}/
      {conversation-id}/
        code.zip                      # 压缩的转换源代码
        logs.zip                      # ATX 会话日志
```

如果用户明确要求下载，请提供命令，但让他们自己运行它：
`aws s3 cp s3://atx-custom-output-{account-id}/transformations/{job-name}/{conversation-id}/code.zip ./code.zip`

批量结果摘要：`~/.aws/atx/custom/atx-agent-session/transformation-summaries/`——请参阅 [references/results-synthesis.md](references/results-synthesis.md)。

## 参考

| 参考 | 使用场景 |
|-----------|-------------|
| [repo-analysis.md](references/repo-analysis.md) | 检测命令、信号匹配、匹配报告格式 |
| [single-transformation.md](references/single-transformation.md) | 将一个 TD 应用于一个存储库（本地或远程） |
| [multi-transformation.md](references/multi-transformation.md) | 在多个存储库中并行应用 TDs |
| [remote-execution.md](references/remote-execution.md) | 基础设施部署、作业提交、监控 |
| [results-synthesis.md](references/results-synthesis.md) | 批量转换后生成综合报告 |
| [cli-reference.md](references/cli-reference.md) | ATX CLI 标志、命令、环境变量、IAM 权限 |
| [troubleshooting.md](references/troubleshooting.md) | 错误解决、调试、质量改进 |

## 许可证
AWS 服务条款。此技能由 AWS 提供，并受 AWS 客户协议和适用的 AWS 服务条款约束。

## 更新日志
如果用户询问发生了什么变化、有什么新内容等。

### [1.0.0] - 2026-04-30

- AWS Transform Agent Skill 的初始发布
- 支持的 TDs:
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
  -
