# Pulumi ESC（环境、密钥和配置）

Pulumi ESC 是一个集中式服务，用于跨云基础设施和应用程序管理环境、密钥和配置。

## 什么是 ESC？

ESC 使团队能够：

- **集中管理密钥和配置** 在一个安全的位置
- **组合环境** 通过导入和叠加配置
- **通过 OIDC 为 AWS、Azure、GCP 生成动态凭证**
- **集成外部密钥存储**（AWS 密钥管理器、Azure 密钥保管库、Vault、1Password）
- **版本控制和审计** 所有配置更改
- **使用细粒度 RBAC 控制访问**

## 基本 CLI 命令

```bash
# 创建新环境
pulumi env init <org>/<project-name>/<environment-name>

# 编辑环境（在编辑器中打开）
pulumi env edit <org>/<project-name>/<environment-name>

# 设置值
pulumi env set <org>/<project-name>/<environment-name> <key> <value>
pulumi env set <org>/<project-name>/<environment-name> <key> <value> --secret

# 查看定义（密钥隐藏）
pulumi env get <org>/<project-name>/<environment-name>

# 打开并解析（显示密钥）
pulumi env open <org>/<project-name>/<environment-name>

# 使用环境运行命令
pulumi env run <org>/<project-name>/<environment-name> -- <command>

# 链接到 Pulumi 栈
pulumi config env add <project-name>/<environment-name>
```

## 关键概念

### 命令区别

- **`pulumi env get`**：显示静态定义，密钥显示为 `[secret]`
- **`pulumi env open`**：解析并显示所有值，包括密钥和动态凭证
- **`pulumi env run`**：加载环境变量后执行命令
- **`pulumi config env add`**：仅接受 `<project-name>/<environment-name>` 部分

### 环境结构

环境是具有保留顶级键的 YAML 文档：

- **`imports`**：导入和组合其他环境
- **`values`**：定义配置和密钥

`values` 下保留的子键：

- **`environmentVariables`**：将值映射到 shell 环境变量
- **`pulumiConfig`**：配置 Pulumi 栈设置
- **`files`**：使用环境数据生成文件

### 基本示例

```yaml
imports:
  - common/base-config

values:
  environment: production
  region: us-west-2

  dbPassword:
    fn::secret: super-secure-password

  environmentVariables:
    AWS_REGION: ${region}
    DB_PASSWORD: ${dbPassword}

  pulumiConfig:
    aws:region: ${region}
    app:dbPassword: ${dbPassword}
```

### 读取其他栈的输出

使用 `fn::open::pulumi-stacks` 提供商来消费其他栈的输出。下方的 `stacks` 和 `network` 键是您任意选择的名字。一旦函数解析，它会将 `stacks.network` 替换为命名栈的输出——因此输出名称（`vpcId`、`subnetIds`）不会出现在静态 YAML 中；它们来自生产栈的导出。两件容易出错的事情：

- 栈由单个项目限定 `stack: <project>/<stackName>` 字段命名——**不是**分开的 `projectName`/`stackName` 字段。
- 输出直接在栈名称下解析——**没有** `.outputs.` 层级（使用 `${stacks.network.vpcId}`，而不是 `${stacks.network.outputs.vpcId}`）。

示例——用您自己的栈名称和输出名称替换：

```yaml
values:
  stacks:
    fn::open::pulumi-stacks:
      stacks:
        network:                 # 参考栈的任意本地名称
          stack: my-project/dev  # 要从中读取输出的生产栈
  pulumiConfig:
    # vpcId / subnetIds 是生产栈导出的任何内容；函数解析后可直接在 `stacks.network` 下获取（没有 `.outputs.`）。
    vpcId: ${stacks.network.vpcId}
    subnetIds: ${stacks.network.subnetIds}
```

完整架构：https://www.pulumi.com/docs/esc/providers/pulumi-stacks/

### 在 Pulumi Cloud 控制台查看环境

环境的控制台 URL 是 `https://app.pulumi.com/<org>/esc/<project>/<environment>`。路由段是 `esc`，而不是 `environments`。

## 与用户协作

### 简单问题

如果用户问基本问题，如“如何创建环境？”或“get 和 open 的区别是什么？”，直接使用上述信息回答。

### 需要详细文档

当用户需要更多信息时，使用 web-fetch 工具从官方 Pulumi ESC 文档获取内容：

- **完整的 YAML 语法和函数** → https://www.pulumi.com/docs/esc/environments/syntax/
- **提供者集成**（AWS、Azure、GCP、Vault、1Password）：
  - AWS: https://www.pulumi.com/docs/esc/integrations/dynamic-login-credentials/aws-login/
  - Azure: https://www.pulumi.com/docs/esc/integrations/dynamic-login-credentials/azure-login/
  - GCP: https://www.pulumi.com/docs/esc/integrations/dynamic-login-credentials/gcp-login/
  - 短期凭证（OIDC）提供者：https://www.pulumi.com/docs/esc/integrations/dynamic-login-credentials/
  - 动态密钥提供者：https://www.pulumi.com/docs/esc/integrations/dynamic-secrets/
  - Pulumi 栈输出（`fn::open::pulumi-stacks`）：https://www.pulumi.com/docs/esc/providers/pulumi-stacks/
  - 所有提供者（索引）：https://www.pulumi.com/docs/esc/providers/
- **入门指南** → https://www.pulumi.com/docs/esc/get-started/
- **CLI 参考** → https://www.pulumi.com/docs/esc/cli/commands/
  - 优先使用 `pulumi env` 子命令，而不是 `esc` CLI。

使用 web-fetch 工具和具体提示从这些文档中提取相关信息。

### 复杂任务

在帮助用户时：

1. **理解目标**：他们是设置新环境、从栈配置迁移还是调试？
2. **检查现有设置**：使用 `pulumi env` 命令列出环境或读取定义
3. **获取相关文档**：使用 web-fetch 获取官方文档中的特定示例或语法
4. **提供分步指导**：使用特定命令逐步引导
5. **验证**：帮助他们使用 `pulumi env get` 或 `pulumi preview` 测试
  - 仅在需要完整解析值时使用 `pulumi env open`，但需谨慎使用，因为它会显示密钥。

### 示例：帮助 AWS OIDC 设置

```text
用户："如何在 ESC 中设置 AWS OIDC 凭证？"

1. 使用 web-fetch 工具从 "https://www.pulumi.com/docs/esc/integrations/dynamic-login-credentials/aws-login/" 获取 AWS OIDC 文档
2. 向用户提供配置
3. 询问用户是否已有预定义角色或需要为他们创建角色
4. 尽可能设置环境，然后引导用户完成您无法为他们完成的步骤
5. 如有必要，帮助他们使用 `pulumi env get` 或 `pulumi env open` 测试
```

## 常见工作流

### 创建环境

```bash
pulumi env init my-org/my-project/dev-config
# 编辑环境（接受来自文件的新的定义，更适合代理，对用户更难）
pulumi env edit --file /tmp/example.yml my-org/my-project/dev-config
```

### 链接到栈

```bash
pulumi config env add my-project/dev-config
pulumi config  # 验证环境值是否可访问
```

### API 访问（罕见）

**始终优先使用 CLI 命令。** 仅在绝对必要时（例如批量操作、自动化）使用 API。

可用的 API 端点包括：

- `GET /api/esc/environments/{orgName}` - 列出环境
- `GET /api/esc/environments/{orgName}/{projectName}/{envName}` - 读取环境定义
- `GET /api/esc/providers?orgName={orgName}` - 列出可用提供者

使用 `pulumi api` CLI 子命令在需要时发起请求，例如 `pulumi api /api/esc/providers -F orgName={orgName}`。

## 最佳实践

1. 始终使用 `fn::secret` 处理敏感值
2. 优先使用 OIDC 而不是静态密钥
3. 使用描述性名称，如 `<org>/my-app/production-aws` 而不是 `<org>/app/prod`
4. 叠加环境：基础 → 云提供者 → 栈特定
5. 链接到环境后，验证 `pulumi config` 显示预期值
6. 优先使用 `pulumi env run` 处理需要环境变量的命令
7. 仅在绝对必要时使用 `pulumi env open`，因为它会显示密钥
8. 在使用现有环境之前，验证其账户和角色并获取用户的确认；仅通过名称选择是错误的。从未在未明确用户确认的情况下将环境链接到栈（`pulumi config env add`），也从未传递 `--yes`。

## 处理凭证错误和现有环境

### 凭证错误

从错误消息中的补救措施开始。过期或缺失的登录通常只需要用户重新认证，大多数提供者会命名修复方法或命令：

- AWS SSO: `Failed to refresh cached SSO credentials. Please refresh SSO login.`
  → `aws sso login`
- AWS 短期凭证: `ExpiredToken: The security token included in the
  request is expired` → 刷新会话或密钥
- Azure: 重新运行 `az login`
- GCP: 重新运行 `gcloud auth application-default login`
- Pulumi Cloud（401 / 未授权）: `pulumi login`

转达修复方法并让用户重试。如果错误没有命名修复方法（例如一个简单的 `Unable to locate credentials`，或一个可能表示错误账户或配置的访问拒绝），不要猜测——确定项目如何认证（提供者配置、活动配置文件、任何链接的 ESC 环境）并解决这些问题。

更改项目获取凭证的位置（添加或切换 ESC 环境、编辑提供者配置）是故意的更改，而不是过期会话的反射性修复。仅在用户需要时才这样做，并遵循以下规则。

### 从未通过名称选择现有环境

不要因为环境名称看起来相关（`*-aws-oidc`、`*-creds`、`*-workshop` 等）而选择环境。匹配的名称并不意味着它是正确的或属于此用户的工 作。

在建议任何现有环境之前：

1. 使用 `pulumi env get <org>/<project>/<env>` 检查它。
2. 确认其认证目标与用户资源实际所在的账户匹配。OIDC `roleArn` 指定特定的 AWS 账户——如果它指向不同的账户（一个共享工作坊、一个讲师角色、另一个团队），它就是错误的环境，并将针对错误的账户运行操作或失败。
3. 向用户展示候选环境并确认它是他们的且正确的，然后使用它。

### 链接环境会更改凭证操作——先确认

`pulumi config env add` 编辑栈配置（`Pulumi.<stack>.yaml`）并更改 Pulumi 操作运行的凭证。从未在未明确用户确认的情况下运行它，也从未传递 `--yes` 跳过确认。告诉用户会发生什么变化，让他们决定。

### 验证后再声称成功

链接后，解析的凭证值通常显示为 `[unknown]`，直到环境打开或运行。不要声称错误已修复或下一个操作将成功，直到您验证它——检查 `pulumi config`，并确认凭证解析到预期的账户，然后再宣布成功。

### 快速故障排除

- **"Environment not found"**：使用 `pulumi env ls -o <org>` 检查权限
- **"Secret decryption failed"**：使用 `pulumi env open` 而不是 `pulumi env get`
- **"Stack can't read values"**：验证 `pulumi config env ls` 以确保栈被列出。
  - 确保环境仅以项目名称/环境名称格式引用。
  - 使用 `pulumi env get <org>/<project-name>/<environment-name>` 获取特定环境定义。
  - 验证 `pulumiConfig` 键存在，并嵌套在 `values` 键下。
