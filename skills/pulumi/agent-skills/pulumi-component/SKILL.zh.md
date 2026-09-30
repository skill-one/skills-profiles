---
name: pulumi-component
description: 编写 Pulumi ComponentResource 类的指南。在创建可重用基础设施组件、设计组件接口、设置多语言支持或分发组件包时使用。
---

# 编写 Pulumi 组件

ComponentResource 将相关的基础设施资源组合成一个可重用、逻辑上的单元。组件使基础设施更易于理解、重用和维护。在 `pulumi preview`/`pulumi up` 输出和 Pulumi Cloud 控制台中，组件表现为一个节点，其子节点嵌套在其下方。

本技能涵盖了完整的组件编写生命周期。对于一般的 Pulumi 编码模式（输出处理、密钥、别名、预览工作流），请使用 `pulumi-best-practices` 技能。

## 使用此技能的场景

在以下情况下调用此技能：

- 创建新的 ComponentResource 类
- 设计组件的 args 接口
- 使组件可从多个 Pulumi 语言使用
- 发布或分发组件包
- 将内联资源重构为可重用组件
- 调试组件行为（缺少输出、创建卡住、子节点在错误级别）

## 组件结构

每个组件都有四个必需元素：

1. **扩展 ComponentResource** 并使用类型 URN 调用 `super()`
2. **接受标准参数**：名称、args 和 `ComponentResourceOptions`
3. **在所有子资源上设置 `parent: this`**
4. **在构造函数末尾调用 `registerOutputs()`**

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
        // 1. 调用 super 并传入类型 URN：<package>:<module>:<type>
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

        // 4. 注册输出——始终是最后一行
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

| 段落 | 规范 | 示例 |
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
        // 缺少 registerOutputs——组件卡在“创建中”
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

**原因**：硬编码子名称在组件多次实例化时会导致冲突。

**错误**：

```typescript
// 如果存在多个组件实例，则会冲突
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

**原因**：`Input<T>` 接受普通值和来自其他资源的 `Output<T>`。如果没有它，消费者必须手动使用 `.apply()` 解包输出。

**错误**：

```typescript
interface WebServiceArgs {
    port: number;            // 强制消费者手动解包输出
    vpcId: string;           // 无法直接接受 vpc.id
}
```

**正确**：

```typescript
interface WebServiceArgs {
    port: pulumi.Input<number>;     // 接受 8080 或某个输出
    vpcId: pulumi.Input<string>;    // 接受 "vpc-123" 或 vpc.id
}
```

### 保持结构扁平

避免嵌套的 arg 对象。扁平接口更易于使用和演进。

```typescript
// 更倾向于扁平
interface DatabaseArgs {
    instanceClass: pulumi.Input<string>;
    storageGb: pulumi.Input<number>;
    enableBackups?: pulumi.Input<boolean>;
    backupRetentionDays?: pulumi.Input<number>;
}

// 避免深层嵌套
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

如果你需要接受多种形式，请使用单独的可选属性：

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

### 为可选属性使用默认值

在构造函数中设置合理的默认值，以便消费者只需配置他们需要的：

```typescript
interface SecureBucketArgs {
    enableVersioning?: pulumi.Input<boolean>;   // 默认为 true
    enableEncryption?: pulumi.Input<boolean>;   // 默认为 true
    blockPublicAccess?: pulumi.Input<boolean>;  // 默认为 true
}

class SecureBucket extends pulumi.ComponentResource {
    constructor(name: string, args: SecureBucketArgs, opts?: pulumi.ComponentResourceOptions) {
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

### 仅暴露消费者需要的值

组件通常会创建许多内部资源。仅暴露消费者需要的值，而不是每个内部资源。

**错误**：

```typescript
class Database extends pulumi.ComponentResource {
    // 暴露所有内容——消费者会看到实现细节
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
    // 仅暴露消费者需要的
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

### 派生复合输出

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

使用可选 args 控制子资源创建：

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
// 低级别组件
class VpcNetwork extends pulumi.ComponentResource {
    public readonly vpcId: pulumi.Output<string>;
    public readonly publicSubnetIds: pulumi.Output<string>[];
    public readonly privateSubnetIds: pulumi.Output<string>[];

    constructor(name: string, args: VpcNetworkArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:VpcNetwork", name, {}, opts);
        // ...创建VPC、子网、路由表...
        this.registerOutputs({ vpcId: this.vpcId });
    }
}

// 使用VpcNetwork的高级组件
class Platform extends pulumi.ComponentResource {
    public readonly kubeconfig: pulumi.Output<string>;

    constructor(name: string, args: PlatformArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:index:Platform", name, {}, opts);

        // 组合低级别组件
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

接受显式提供者以用于多区域或多账户部署。`ComponentResourceOptions`会自动将提供者配置传递给子组件：

```typescript
// 消费者传递不同区域的提供者
const usWest = new aws.Provider("us-west", { region: "us-west-2" });
const site = new StaticSite("west-site", { indexDocument: "index.html" }, {
    providers: [usWest],
});
```

带有`{ parent: this }`的子组件会自动继承提供者。组件内部无需额外代码。

---

## 多语言组件

如果您的组件将从多种Pulumi语言（TypeScript、Python、Go、C#、Java、YAML）中被消费，请将其作为多语言组件进行打包。

### 您需要多语言组件吗？

问：任何人会使用与组件编写语言不同的语言来消费这个组件吗？

**单语言组件**（无需打包）：

- 您的团队使用一种语言，并且组件保留在该代码库中
- 组件是单个项目或单一代码库的内部组件
- 无需`PulumiPlugin.yaml`——直接导入类即可

**多语言组件**（需要打包）：

- 其他团队使用不同的语言消费您的组件
- 平台团队为选择自己语言的开发者构建抽象
- YAML消费者需要访问——即使您使用TypeScript编写，YAML程序也需要多语言打包才能使用您的组件
- 为您的组织构建共享组件库
- 发布到Pulumi私有注册中心或公共注册中心是一个常见原因，但并非多语言支持所必需

**常见错误**：TypeScript平台团队构建的组件只能被TypeScript用户消费。如果应用程序开发者使用Python或YAML，则没有多语言打包，这些组件对他们来说是不可见的。

### 设置

在组件目录中创建一个`PulumiPlugin.yaml`来声明运行时：

```yaml
runtime: nodejs
```

或对于Python：

```yaml
runtime: python
```

### 序列化约束

为了实现多语言兼容性，args必须是可序列化的。这些约束无论编写语言如何都适用：

| 允许 | 不允许 |
|------|--------|
| `string`、`number`、`boolean` | 联合类型（`string \| number`） |
| `Input<T>`包装器 | 函数和回调 |
| 原始类型的数组和映射 | 复杂的嵌套泛型 |
| 枚举 | 平台特定类型 |

### 消费多语言组件

消费者使用`pulumi package add`安装组件，该命令会自动下载提供者插件，在消费者语言中生成本地SDK，并更新`Pulumi.yaml`：

```bash
# 从Git仓库
pulumi package add <git-repo-url>

# 从特定版本标签
pulumi package add <git-repo-url>@v1.0.0
```

对于全新的检出或CI环境，运行`pulumi install`以确保所有包依赖项都可用。消费者无需手动生成SDK。

发布SDK到包管理器（npm、PyPI等）的作者可以选择使用`pulumi package gen-sdk`生成语言特定的SDK进行发布。大多数组件作者不需要这个——`pulumi package add`会在消费者端处理SDK生成。

### 入口点

发布的多语言组件需要一个入口点来托管组件提供者进程。入口点模式因语言而异。

**TypeScript** (`runtime: nodejs`)：

从`index.ts`导出组件类。无需单独的入口点文件。Pulumi会自动introspect导出的类。

```typescript
// index.ts -- 导出是入口点
export { StaticSite, StaticSiteArgs } from "./staticSite";
export { SecureBucket, SecureBucketArgs } from "./secureBucket";
```

**Python** (`runtime: python`)：

创建一个`__main__.py`，调用`component_provider_host`并传入所有组件类：

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

创建一个`main.go`来构建和运行提供者：

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

创建一个`Program.cs`来提供组件提供者主机：

```csharp
using System.Threading.Tasks;

class Program
{
    public static Task Main(string[] args) =>
        Pulumi.Experimental.Provider.ComponentProviderHost.Serve(args);
}
```

对于跨所有语言的完整工作示例，请参阅 https://github.com/mikhailshilkov/comp-as-comp。

**参考**：https://www.pulumi.com/docs/iac/using-pulumi/pulumi-packages/

---

## 分发

根据您的受众选择分发方法：

| 受众 | 方法 | 如何 |
|------|------|------|
| 相同项目 | 直接导入 | 标准语言导入 |
| 相同组织 | 私有注册中心 | `pulumi package publish`到Pulumi Cloud |
| 相同组织 | Git仓库 | `pulumi package add <repo>`并使用版本标签 |
| 语言生态系统 | 包管理器 | 发布到npm、PyPI、NuGet或Maven |
| 公共社区 | Pulumi注册中心 | 通过pulumi/registry GitHub仓库提交 |

### Pulumi私有注册中心

私有注册中心是您组织组件的集中目录。它提供自动API文档、版本管理和所有团队的发现功能。

将组件发布到私有注册中心：

```bash
pulumi package publish https://github.com/myorg/my-component --publisher myorg
```

使用带`v`前缀的git标签来版本化组件：

```bash
git tag v1.0.0
git push origin v1.0.0
```

发布时需要README文件。Pulumi将其用作注册中心中组件的文档页面。

使用GitHub Actions和OIDC认证从GitHub Actions自动发布：

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

**前提条件**：在使用此工作流之前，请先配置GitHub OIDC与Pulumi Cloud的集成。

注册中心支持私有GitHub和GitLab仓库。对于非OIDC设置，使用`GITHUB_TOKEN`或`GITLAB_TOKEN`环境变量进行认证。

私有注册中心会自动为每个发布的组件生成SDK文档。通过向组件的输入和输出添加类型注解（TypeScript中的JSDoc、Python中的docstrings、Go中的`Annotate()`方法）来丰富生成的文档。

**参考**：https://www.pulumi.com/docs/idp/get-started/private-registry/

### Git仓库分发

为消费者标记发布版本：

```bash
git tag v1.0.0
git push origin v1.0.0
```

消费者使用：

```bash
pulumi package add https://github.com/myorg/my-component@v1.0.0
```

### 包管理器分发

发布语言特定的包以进行原生依赖管理：

- **npm**：`npm publish`用于TypeScript/JavaScript
- **PyPI**：`twine upload`用于Python
- **NuGet**：`dotnet nuget push`用于.NET
- **Maven Central**：标准的Maven发布用于Java

**参考**：https://www.pulumi.com/docs/iac/using-pulumi/pulumi-packages/

---

## 反模式

| 反模式 | 问题 | 解决方法 |
|------|------|------|
| 在`apply()`内部创建资源 | 在`pulumi preview`中不可见 | 将资源创建移出apply（参见`pulumi-best-practices`实践1） |
| 缺少`registerOutputs()` | 组件卡在"创建"状态 | 总是在构造函数的最后调用 |
| 缺少`parent: this` | 子组件出现在根级别 | 将`{ parent: this }`传递给所有子资源 |
| args中的联合类型 | 打破Python、Go、C# SDKs | 使用单一类型；为变体使用分离的属性 |
| args中的函数 | 无法跨语言序列化 | 使用配置属性代替 |
| 硬编码子组件名称 | 多个实例发生冲突 | 从`${name}-suffix`派生名称 |
| 过度暴露输出 | 泄露实现细节 | 仅导出消费者需要的内容 |
| 单用途组件 | 不必要的抽象开销 | 使用内联资源，直到模式重复 |
| 深层嵌套args | 难以使用和演进 | 保持接口扁平，使用可选属性 |

---

## 快速参考

| 主题 | 关键点 |
|------|------|
| 类型URN | `<package>:<module>:<type>`，模块通常为`index` |
| 构造函数 | `super(type, name, {}, opts)`，然后是子组件，最后是`registerOutputs()` |
| 子资源 | 总是`{ parent: this }`，从`${name}-suffix`派生名称 |
| args接口 | 包装在`Input<T>`中，无联合类型，无函数，扁平结构 |
| 输出 | 公开的只读`Output<T>`属性，仅暴露必需内容 |
| 默认值 | 使用`??`运算符在构造函数中应用合理的默认值 |
| 组合 | 低级别组件组合成高级别组件 |
| 多语言 | `PulumiPlugin.yaml` + 入口点；消费者使用`pulumi package add` |
| 分发 | 私有注册中心、git标签、包管理器或公共Pulumi注册中心 |

## 相关技能

- **pulumi-best-practices**：一般的Pulumi模式，包括Output处理、密钥和别名
- **pulumi-automation-api**：程序化编排，用于集成测试和多栈工作流
- **pulumi-esc**：组件部署的集中密钥和配置

## 参考

- https://www.pulumi.com/docs/iac/concepts/resources/components/
- https://www.pulumi.com/docs/iac/using-pulumi/pulumi-packages/
- https://www.pulumi.com/docs/idp/get-started/private-registry/
- https://www.pulumi.com/docs/iac/concepts/inputs-outputs/
- https://www.pulumi.com/docs/iac/concepts/resources/options/aliases/
