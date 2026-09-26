# 编写 Pulumi 组件

ComponentResource 将相关的基础设施资源组合成一个可重用、逻辑上的单元。组件使基础设施更易于理解、重用和维护。组件在 `pulumi preview`/`pulumi up` 输出中和 Pulumi Cloud 控制台中显示为单个节点，其子节点嵌套在其下方。

本技能涵盖了完整的组件编写生命周期。对于一般的 Pulumi 编码模式（输出处理、密钥、别名、预览工作流），请使用 `pulumi-best-practices` 技能。

## 何时使用此技能

在以下情况下调用此技能：

- 创建新的 ComponentResource 类
- 设计组件的 args 接口
- 使组件可从多个 Pulumi 语言使用
- 发布或分发组件包
- 将内联资源重构为可重用的组件
- 调试组件行为（缺少输出、创建卡住、子节点在错误级别）

## 组件结构

每个组件都有四个必需元素：

1. **扩展 ComponentResource** 并使用类型 URN 调用 `super()`
2. **接受标准参数**：名称、args 和 `ComponentResourceOptions`
3. **在所有子资源上设置 `parent: this`**
4. **在构造函数的末尾调用 `registerOutputs()`**

### TypeScript

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface StaticSiteArgs {
    indexDocument?: pulumi.Input<string>;
    errorDocument?: pulumi.Input<string>;
}

class StaticSite extends pulumi.ComponentResource {
    public readonly bucketName: pulumi.Output<string>;
    public readonly websiteUrl: pulumi.Output<string>;

    constructor(name: string, args: StaticSiteArgs, opts?: pulumi.ComponentResourceOptions) {
        // 1. 使用类型 URN 调用 super：<package>:<module>:<type>
        super("myorg:index:StaticSite", name, {}, opts);

        // 2. 使用 parent: this 创建子资源
        const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, { parent: this });

        const website = new aws.s3.BucketWebsiteConfigurationV2(`${name}-website`, {
            bucket: bucket.id,
            indexDocument: { suffix: args.indexDocument ?? "index.html" },
            errorDocument: { key: args.errorDocument ?? "error.html" },
        }, { parent: this });

        // 3. 将输出暴露为类属性
        this.bucketName = bucket.id;
        this.websiteUrl = website.websiteEndpoint;

        // 4. 注册输出 -- 始终是最后一行
        this.registerOutputs({
            bucketName: this.bucketName,
            websiteUrl: this.websiteUrl,
        });
    }
}

// 使用示例
const site = new StaticSite("marketing", {
    indexDocument: "index.html",
});
export const url = site.websiteUrl;
```

### Python

```python
import pulumi
import pulumi_aws as aws

class StaticSiteArgs:
    def __init__(self,
                 index_document: pulumi.Input[str] = "index.html",
                 error_document: pulumi.Input[str] = "error.html"):
        self.index_document = index_document
        self.error_document = error_document

class StaticSite(pulumi.ComponentResource):
    bucket_name: pulumi.Output[str]
    website_url: pulumi.Output[str]

    def __init__(self, name: str, args: StaticSiteArgs,
                 opts: pulumi.ResourceOptions = None):
        super().__init__("myorg:index:StaticSite", name, None, opts)

        bucket = aws.s3.Bucket(f"{name}-bucket",
            opts=pulumi.ResourceOptions(parent=self))

        website = aws.s3.BucketWebsiteConfigurationV2(f"{name}-website",
            bucket=bucket.id,
            index_document=aws.s3.BucketWebsiteConfigurationV2IndexDocumentArgs(
                suffix=args.index_document,
            ),
            error_document=aws.s3.BucketWebsiteConfigurationV2ErrorDocumentArgs(
                key=args.error_document,
            ),
            opts=pulumi.ResourceOptions(parent=self))

        self.bucket_name = bucket.id
        self.website_url = website.website_endpoint

        self.register_outputs({
            "bucket_name": self.bucket_name,
            "website_url": self.website_url,
        })

site = StaticSite("marketing", StaticSiteArgs())
pulumi.export("url", site.website_url)
```

### Type URN 格式

`super()` 的第一个参数是类型 URN：`<package>:<module>:<type>`。

| 段落 | 惯例 | 示例 |
|------|------|------|
| package | 组织或包名 | `myorg`, `acme`, `pkg` |
| module | 通常为 `index` | `index` |
| type | PascalCase 类名 | `StaticSite`, `VpcNetwork` |

完整示例：`myorg:index:StaticSite`, `acme:index:KubernetesCluster`

### registerOutputs 是必需的

**原因**：如果没有 `registerOutputs()`，组件在 Pulumi 控制台中会显示为“创建中”状态，输出不会持久化到状态中。

**错误**：

```typescript
class MyComponent extends pulumi.ComponentResource {
    public readonly url: pulumi.Output<string>;

    constructor(name: string, args: MyArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:MyComponent", name, {}, opts);
        const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, { parent: this });
        this.url = bucket.bucketRegionalDomainName;
        // 缺少 registerOutputs -- 组件“创建中”卡住
    }
}
```

**正确**：

```typescript
class MyComponent extends pulumi.ComponentResource {
    public readonly url: pulumi.Output<string>;

    constructor(name: string, args: MyArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:MyComponent", name, {}, opts);
        const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, { parent: this });
        this.url = bucket.bucketRegionalDomainName;

        this.registerOutputs({ url: this.url });
    }
}
```

### 从组件名称派生子名称

**原因**：硬编码子名称会在组件多次实例化时导致冲突。

**错误**：

```typescript
// 如果存在两个此组件的实例，则会冲突
const bucket = new aws.s3.Bucket("my-bucket", {}, { parent: this });
```

**正确**：

```typescript
// 每个组件实例唯一
const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, { parent: this });
```

---

## 设计 Args 接口

args 接口是最具影响力的设计决策。它定义了消费者可以配置的内容以及组件的可组合性。

### 将属性包装在 Input<T> 中

**原因**：`Input<T>` 接受纯值和来自其他资源的 `Output<T>`。如果没有它，消费者必须手动使用 `.apply()` 解包输出。

**错误**：

```typescript
interface WebServiceArgs {
    port: number;            // 强制消费者手动解包 Outputs
    vpcId: string;           // 无法直接接受 vpc.id
}
```

**正确**：

```typescript
interface WebServiceArgs {
    port: pulumi.Input<number>;     // 接受 8080 或 someOutput
    vpcId: pulumi.Input<string>;    // 接受 "vpc-123" 或 vpc.id
}
```

### 保持结构扁平

避免深度嵌套的 arg 对象。扁平接口更易于使用和演进。

```typescript
// 更倾向于扁平
interface DatabaseArgs {
    instanceClass: pulumi.Input<string>;
    storageGb: pulumi.Input<number>;
    enableBackups?: pulumi.Input<boolean>;
    backupRetentionDays?: pulumi.Input<number>;
}

// 避免深度嵌套
interface DatabaseArgs {
    instance: {
        compute: { class: pulumi.Input<string> };
        storage: { sizeGb: pulumi.Input<number> };
    };
    backup: {
        config: { enabled: pulumi.Input<boolean>; retention: pulumi.Input<number> };
    };
}
```

### 没有联合类型

联合类型会破坏多语言 SDK 生成。Python、Go 和 C# 无法表示 `string | number`。

**错误**：

```typescript
interface MyArgs {
    port: pulumi.Input<string | number>;  // 在 Python、Go、C# 中失败
}
```

**正确**：

```typescript
interface MyArgs {
    port: pulumi.Input<number>;  // 单一类型，在任何地方都有效
}
```

如果您需要接受多种形式，请使用单独的可选属性：

```typescript
interface StorageArgs {
    sizeGb?: pulumi.Input<number>;      // 指定 GB 大小
    sizeMb?: pulumi.Input<number>;      // 或指定 MB 大小
}
```

### 没有函数或回调

函数无法跨语言边界序列化。

**错误**：

```typescript
interface MyArgs {
    nameTransform: (name: string) => string;  // 无法序列化
}
```

**正确**：

```typescript
interface MyArgs {
    namePrefix?: pulumi.Input<string>;   // 使用配置而不是回调
    nameSuffix?: pulumi.Input<string>;
}
```

### 使用默认值

在构造函数中设置合理的默认值，以便消费者只需配置他们需要的：

```typescript
interface SecureBucketArgs {
    enableVersioning?: pulumi.Input<boolean>;   // 默认为 true
    enableEncryption?: pulumi.Input<boolean>;   // 默认为 true
    blockPublicAccess?: pulumi.Input<boolean>;  // 默认为 true
}

class SecureBucket extends pulumi.ComponentResource {
    constructor(name: string, args: SecureBucketArgs = {}, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:SecureBucket", name, {}, opts);

        const enableVersioning = args.enableVersioning ?? true;
        const enableEncryption = args.enableEncryption ?? true;
        const blockPublicAccess = args.blockPublicAccess ?? true;

        // 应用默认值...
    }
}

// 消费者仅覆盖他们需要的
const bucket = new SecureBucket("data", { enableVersioning: false });
```

---

## 暴露输出

### 仅暴露消费者需要的内容

组件通常会创建许多内部资源。仅暴露消费者需要的值，而不是每个内部资源。

**错误**：

```typescript
class Database extends pulumi.ComponentResource {
    // 暴露所有内容 -- 消费者看到实现细节
    public readonly cluster: aws.rds.Cluster;
    public readonly primaryInstance: aws.rds.ClusterInstance;
    public readonly replicaInstance: aws.rds.ClusterInstance;
    public readonly subnetGroup: aws.rds.SubnetGroup;
    public readonly securityGroup: aws.ec2.SecurityGroup;
    public readonly parameterGroup: aws.rds.ClusterParameterGroup;
    // ...
}
```

**正确**：

```typescript
class Database extends pulumi.ComponentResource {
    // 仅暴露消费者需要的内容
    public readonly endpoint: pulumi.Output<string>;
    public readonly port: pulumi.Output<number>;
    public readonly securityGroupId: pulumi.Output<string>;

    constructor(name: string, args: DatabaseArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:Database", name, {}, opts);

        const sg = new aws.ec2.SecurityGroup(`${name}-sg`, { /* ... */ }, { parent: this });
        const cluster = new aws.rds.Cluster(`${name}-cluster`, { /* ... */ }, { parent: this });

        this.endpoint = cluster.endpoint;
        this.port = cluster.port;
        this.securityGroupId = sg.id;

        this.registerOutputs({
            endpoint: this.endpoint,
            port: this.port,
            securityGroupId: this.securityGroupId,
        });
    }
}
```

### 派生组合输出

使用 `pulumi.interpolate` 或 `pulumi.concat` 构建派生值：

```typescript
this.connectionString = pulumi.interpolate`postgresql://${args.username}:${args.password}@${cluster.endpoint}:${cluster.port}/${args.databaseName}`;

this.registerOutputs({ connectionString: this.connectionString });
```

---

## 组件设计模式

### 合理的默认值与覆盖

将最佳实践编码为默认值。允许消费者在具有特定需求时覆盖。

```typescript
interface SecureBucketArgs {
    enableVersioning?: pulumi.Input<boolean>;
    enableEncryption?: pulumi.Input<boolean>;
    blockPublicAccess?: pulumi.Input<boolean>;
    tags?: pulumi.Input<Record<string, pulumi.Input<string>>>;
}

class SecureBucket extends pulumi.ComponentResource {
    public readonly bucketId: pulumi.Output<string>;
    public readonly arn: pulumi.Output<string>;

    constructor(name: string, args: SecureBucketArgs = {}, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:SecureBucket", name, {}, opts);

        const bucket = new aws.s3.Bucket(`${name}-bucket`, {
            tags: args.tags,
        }, { parent: this });

        // 默认启用版本控制
        if (args.enableVersioning !== false) {
            new aws.s3.BucketVersioningV2(`${name}-versioning`, {
                bucket: bucket.id,
                versioningConfiguration: { status: "Enabled" },
            }, { parent: this });
        }

        // 默认启用加密
        if (args.enableEncryption !== false) {
            new aws.s3.BucketServerSideEncryptionConfigurationV2(`${name}-encryption`, {
                bucket: bucket.id,
                rules: [{ applyServerSideEncryptionByDefault: { sseAlgorithm: "AES256" } }],
            }, { parent: this });
        }

        // 默认阻止公共访问
        if (args.blockPublicAccess !== false) {
            new aws.s3.BucketPublicAccessBlock(`${name}-public-access`, {
                bucket: bucket.id,
                blockPublicAcls: true,
                blockPublicPolicy: true,
                ignorePublicAcls: true,
                restrictPublicBuckets: true,
            }, { parent: this });
        }

        this.bucketId = bucket.id;
        this.arn = bucket.arn;
        this.registerOutputs({ bucketId: this.bucketId, arn: this.arn });
    }
}
```

### 条件资源创建

使用可选 args 来控制子资源的创建：

```typescript
interface WebServiceArgs {
    image: pulumi.Input<string>;
    port: pulumi.Input<number>;
    enableMonitoring?: pulumi.Input<boolean>;
    alarmEmail?: pulumi.Input<string>;
}

class WebService extends pulumi.ComponentResource {
    constructor(name: string, args: WebServiceArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:WebService", name, {}, opts);

        const service = new aws.ecs.Service(`${name}-service`, {
            // ...服务配置...
        }, { parent: this });

        // 仅在启用监控时创建警报基础设施
        if (args.enableMonitoring) {
            const topic = new aws.sns.Topic(`${name}-alerts`, {}, { parent: this });

            if (args.alarmEmail) {
                new aws.sns.TopicSubscription(`${name}-alert-email`, {
                    topic: topic.arn,
                    protocol: "email",
                    endpoint: args.alarmEmail,
                }, { parent: this });
            }

            new aws.cloudwatch.MetricAlarm(`${name}-cpu-alarm`, {
                // ...警报配置引用服务...
                alarmActions: [topic.arn],
            }, { parent: this });
        }

        this.registerOutputs({});
    }
}
```

### 组合

从较低级别的组件构建更高级别的组件。每个级别管理单个关注点。

```typescript
// 较低级别的组件
class VpcNetwork extends pulumi.ComponentResource {
    public readonly vpcId: pulumi.Output<string>;
    public readonly publicSubnetIds: pulumi.Output<string>[];
    public readonly privateSubnetIds: pulumi.Output<string>[];

    constructor(name: string, args: VpcNetworkArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:VpcNetwork", name, {}, opts);
        // ...创建 VPC、子网、路由表...
        this.registerOutputs({ vpcId: this.vpcId });
    }
}

// 更高级别的组件，使用 VpcNetwork
class Platform extends pulumi.ComponentResource {
    public readonly kubeconfig: pulumi.Output<string>;

    constructor(name: string, args: PlatformArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:Platform", name, {}, opts);

        // 组合较低级别的组件
        const network = new VpcNetwork(`${name}-network`, {
            cidrBlock: args.cidrBlock,
        }, { parent: this });

        const cluster = new aws.eks.Cluster(`${name}-cluster`, {
            vpcConfig: {
                subnetIds: network.privateSubnetIds,
            },
        }, { parent: this });

        this.kubeconfig = cluster.kubeconfig;
        this.registerOutputs({ kubeconfig: this.kubeconfig });
    }
}
```

### 提供者传递

接受显式的提供者用于多区域或多帐户部署。`ComponentResourceOptions` 会自动将提供者配置传递给子资源：

```typescript
// 消费者传递不同区域的提供者
const usWest = new aws.Provider("us-west", { region: "us-west-2" });
const site = new StaticSite("west-site", { indexDocument: "index.html" }, {
    providers: [usWest],
});
```

具有 `{ parent: this }` 的子资源会自动继承提供者。组件内部不需要额外代码。

---

## 多语言组件

如果您的组件将被多种 Pulumi 语言（TypeScript、Python、Go、C#、Java、YAML）消费，请将其作为多语言组件打包。

### 您需要多语言吗？

问：任何人都会使用与编写组件不同的语言来消费此组件吗？

**单语言组件**（无需打包）：

- 您的团队使用一种语言，组件保留在该代码库中
- 组件属于单个项目或单一代码库
- 无需 `PulumiPlugin.yaml` -- 直接导入类

**多语言组件**（需要打包）：

- 其他团队使用不同语言消费您的组件
- 平台团队为选择自己语言的开发者构建抽象
- YAML 消费者需要访问 -- 即使您使用 TypeScript 编写，YAML 程序也需要多语言打包才能使用您的组件
- 为您的组织构建共享组件库
- 发布到 Pulumi 私有注册中心或公共注册中心是一个常见原因，但不是多语言支持所必需的

**常见错误**：TypeScript 平台团队构建的组件只能被 TypeScript 用户消费。如果应用程序开发者使用 Python 或 YAML，则这些组件在无需多语言打包的情况下对它们不可见。

### 设置

在组件目录中创建 `PulumiPlugin.yaml` 来声明运行时：

```yaml
runtime: nodejs
```

或对于 Python：

```yaml
runtime: python
```

### 序列化约束

为了多语言兼容性，args 必须可序列化。这些约束适用于任何编写语言：

| 允许 | 不允许 |
|------|--------|
| `string`, `number`, `boolean` | 联合类型 (`string \| number`) |
| `Input<T>` 包装器 | 函数和回调 |
| 基本类型的数组和映射 | 复杂的嵌套泛型 |
| 枚举 | 平台特定类型 |

### 消费多语言组件

消费者使用 `pulumi package add` 安装组件，这会自动下载提供者插件，在消费者语言中生成本地 SDK，并更新 `Pulumi.yaml`：

```bash
# 从 Git 仓库
pulumi package add <git-repo-url>

# 从特定版本标签
pulumi package add <git-repo-url>@v1.0.0
```

对于全新的检出或 CI 环境，运行 `pulumi install` 以确保所有包依赖项可用。消费者无需手动生成 SDK。

发布 SDK 到包管理器（npm、PyPI、NuGet 或 Maven）的作者可以选择使用 `pulumi package gen-sdk` 生成特定语言的 SDK 以供发布。大多数组件作者不需要这样做 -- `pulumi package add` 在消费者端处理 SDK 生成。

### 入口点

发布的多语言组件需要一个托管组件提供者进程的入口点。入口点模式因语言而异。

**TypeScript** (`runtime: nodejs`)：

从 `index.ts` 导出组件类。无需单独的入口点文件。Pulumi 会自动introspect导出的类。

```typescript
// index.ts -- 导出是入口点
export { StaticSite, StaticSiteArgs } from "./staticSite";
export { SecureBucket, SecureBucketArgs } from "./secureBucket";
```

**Python** (`runtime: python`)：

创建一个 `__main__.py`，调用 `component_provider_host` 并传入所有组件类：

```python
from pulumi.provider.experimental import component_provider_host
from static_site import StaticSite
from secure_bucket import SecureBucket

if __name__ == "__main__":
    component_provider_host(
        name="my-components",
        components=[StaticSite, SecureBucket],
    )
```

**Go** (`runtime: go`)：

创建一个 `main.go`，构建并运行提供者：

```go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/pulumi/pulumi-go-provider/infer"
)

func main() {
    p, err := infer.NewProviderBuilder().
        WithComponents(
            infer.ComponentF(NewStaticSite),
            infer.ComponentF(NewSecureBucket),
        ).
        Build()
    if err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
    if err := p.Run(context.Background(), "my-components", "0.1.0"); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
```

**C#** (`runtime: dotnet`)：

创建一个 `Program.cs`，提供组件提供者主机：

```csharp
using System.Threading.Tasks;

class Program
{
    public static Task Main(string[] args) =>
        Pulumi.Experimental.Provider.ComponentProviderHost.Serve(args);
}
```

对于跨所有语言的完整工作示例，请参阅 https://github.com/mikhailshilkov/comp-as-comp。

**参考**：https://www.pulumi.com/docs/iac/concepts/resources/components/
- https://www.pulumi.com/docs/iac/using-pulumi/pulumi-packages/
- https://www.pulumi.com/docs/idp/get-started/private-registry/
- https://www.pulumi.com/docs/iac/concepts/inputs-outputs/
- https://www.pulumi.com/docs/iac/concepts/resources/options/aliases/

---

## 发布

根据您的受众选择发布方法：

| 受众 | 方法 | 如何 |
|------|------|------|
| 同一项目 | 直接导入 | 标准语言导入 |
| 同一组织 | 私有注册中心 | `pulumi package publish` 到 Pulumi Cloud |
| 同一组织 | Git 仓库 | `pulumi package add <repo>` 使用版本标签 |
| 语言生态系统 | 包管理器 | 发布到 npm、PyPI、NuGet 或 Maven |
| 公共社区 | Pulumi 注册中心 | 通过 pulumi/registry GitHub 仓库提交 |

### Pulumi 私有注册中心

私有注册中心是您组织组件的集中目录。它提供自动 API 文档、版本管理和所有团队的发现性。

将组件发布到私有注册中心：

```bash
pulumi package publish https://github.com/myorg/my-component --publisher myorg
```

使用带有 `v` 前缀的 git 标签进行组件版本管理：

```bash
git tag v1.0.0
git push origin v1.0.0
```

发布时需要 README 文件。Pulumi 将其用作注册中心中组件的文档页面。

使用 GitHub Actions 使用 OIDC 身份验证自动发布：

```yaml
name: 发布组件
on:
  push:
    tags:
      - "v*"

permissions:
  id-token: write
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    env:
      PULUMI_ORG: myorg
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: pulumi/auth-actions@v1
        with:
          organization: ${{ env.PULUMI_ORG }}
          requested-token-type: urn:pulumi:token-type:access_token:organization
      - run: pulumi package publish https://github.com/${{ github.repository }} --publisher ${{ env.PULUMI_ORG }}
```

**前提条件**：在使用此工作流之前，请先配置 GitHub OIDC 集成与 Pulumi Cloud。

私有注册中心支持私有 GitHub 和 GitLab 仓库。对于非 OIDC 设置，使用 `GITHUB_TOKEN` 或 `GITLAB_TOKEN` 环境变量进行身份验证。

私有注册中心自动为每个发布的组件生成 SDK 文档。通过在组件的输入和输出中添加类型注解（TypeScript 中的 JSDoc、Python 中的 docstrings、Go 中的 `Annotate()` 方法）来丰富生成的文档。

**参考**：https://www.pulumi.com/docs/idp/get-started/private-registry/

### Git 仓库发布

为消费者标记发布版本：

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 包管理器发布

发布语言特定的包以进行原生依赖管理：

- **npm**: `npm publish` 用于 TypeScript/JavaScript
- **PyPI**: `twine upload` 用于 Python
- **NuGet**: `dotnet nuget push` 用于 .NET
- **Maven Central**: 标准 Maven 发布用于 Java

**参考**：https://www.pulumi.com/docs/iac/using-pulumi/pulumi-packages/

---

## 反模式

| 反模式 | 问题 | 修复 |
|-------|------|------|
| `apply()` 中的资源 | 在 `pulumi preview` 中不可见 | 将资源创建移出 apply（见 `pulumi-best-practices` 实践 1） |
| 缺少 `registerOutputs()` | 组件“创建中”卡住 | 始终作为构造函数的最后一行调用 |
| 缺少 `parent: this` | 子节点出现在根级别 | 将 `{ parent: this }` 传递给所有子资源 |
| args 中的联合类型 | 破坏 Python、Go、C# SDKs | 使用单一类型；使用单独的属性表示变体 |
| args 中的函数 | 无法跨语言边界序列化 | 使用配置属性而不是函数 |
| 硬编码子名称 | 多个实例冲突 | 从 `${name}-suffix` 派生子名称 |
| 过度暴露输出 | 泄露实现细节 | 仅暴露消费者需要的内容 |
| 单用途组件 | 不必要的抽象开销 | 使用内联资源，直到模式重复 |
| 深度嵌套的 args | 难以使用和演进 | 使用扁平的接口和可选属性 |

---

## 快速参考

| 主题 | 关键点 |
|------|------|
| 类型 URN | `<package>:<module>:<type>`，模块通常为 `index` |
| 构造函数 | `super(type, name, {}, opts)` 然后 children 然后 `registerOutputs()` |
| 子资源 | 始终 `{ parent: this }`，从 `${name}-suffix` 派生子名称 |
| Args 接口 | 包装在 `Input<T>` 中，没有联合类型，没有函数，扁平结构 |
| 输出 | 公共只读 `Output<T>` 属性，仅暴露必需的内容 |
| 默认值 | 在构造函数中使用 `??` 运算符应用合理的默认值 |
| 组合 | 从较低级别的组件构建更高级别的组件 |
| 多语言 | `PulumiPlugin.yaml` + 入口点；消费者使用 `pulumi package add` |
| 发布 | 私有注册中心、git 标签、包管理器或公共 Pulumi 注册中心 |

## 相关技能

- **pulumi-best-practices**: 一般 Pulumi 模式，包括输出处理、密钥和别名
- **pulumi-automation-api**: 程序化编排用于集成测试和多栈工作流
- **pulumi-esc**: 用于组件部署的集中密钥和配置

## 参考

- https://www.pulumi.com/docs/iac/concepts/resources/components/
- https://www.pulumi.com/docs/iac/using-pulumi/pulumi-packages/
- https://www.pulumi.com/docs/idp/get-started/private-registry/
- https://www.pulumi.com/docs/iac/concepts/inputs-outputs/
- https://www.pulumi.com/docs/iac/concepts/resources/options/aliases/
