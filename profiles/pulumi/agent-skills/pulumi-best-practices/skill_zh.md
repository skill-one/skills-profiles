# Pulumi 最佳实践

## 何时使用此技能

在以下情况下调用此技能：

- 编写新的 Pulumi 程序或组件
- 审查 Pulumi 代码的正确性
- 重构现有的 Pulumi 基础设施
- 调试资源依赖问题
- 设置配置和密钥

## 实践

### 1. 永远不要在 `apply()` 中创建资源

**原因**：在 `apply()` 中创建的资源不会出现在 `pulumi preview` 中，导致更改不可预测。Pulumi 无法正确跟踪依赖关系，从而导致竞争条件和部署失败。

**检测信号**：

- `.apply()` 回调中包含 `new aws.` 或其他资源构造函数
- 在 `pulumi.all([...]).apply()` 中创建资源
- 在 apply 中在运行时动态确定资源数量

**错误示例**：

```typescript
const bucket = new aws.s3.Bucket("bucket");

bucket.id.apply(bucketId => {
    // 错误：此资源不会出现在预览中
    new aws.s3.BucketObject("object", {
        bucket: bucketId,
        content: "hello",
    });
});
```

**正确示例**：

```typescript
const bucket = new aws.s3.Bucket("bucket");

// 直接传递输出 - Pulumi 处理依赖关系
const object = new aws.s3.BucketObject("object", {
    bucket: bucket.id,  // Output<string> 在这里有效
    content: "hello",
});
```

**apply 何时适用**：

- 转换输出值以用于标签、名称或计算字符串
- 日志记录或调试（不是资源创建）
- 影响资源属性的条件逻辑，而不是资源存在

**参考**：https://www.pulumi.com/docs/concepts/inputs-outputs/

---

### 2. 直接将输出作为输入传递

**原因**：Pulumi 基于输入/输出关系构建有向无环图（DAG）。直接传递输出可确保正确的创建顺序。手动解包值会破坏依赖链，导致资源以错误顺序部署或引用尚未存在的值。

**检测信号**：

- 从 `.apply()` 中提取变量用作资源输入
- 在 apply 外部对输出值使用 `await`
- 使用输出值进行字符串连接而不是 `pulumi.interpolate`

**错误示例**：

```typescript
const vpc = new aws.ec2.Vpc("vpc", { cidrBlock: "10.0.0.0/16" });

// 错误：提取值会破坏依赖链
let vpcId: string;
vpc.id.apply(id => { vpcId = id; });

const subnet = new aws.ec2.Subnet("subnet", {
    vpcId: vpcId,  // 可能未定义，没有跟踪的依赖关系
    cidrBlock: "10.0.1.0/24",
});
```

**正确示例**：

```typescript
const vpc = new aws.ec2.Vpc("vpc", { cidrBlock: "10.0.0.0/16" });

const subnet = new aws.ec2.Subnet("subnet", {
    vpcId: vpc.id,  // 直接传递 Output
    cidrBlock: "10.0.1.0/24",
});
```

**用于字符串插值**：

```typescript
// 错误
const name = bucket.id.apply(id => `prefix-${id}-suffix`);

// 正确 - 使用 pulumi.interpolate 进行模板字面量
const name = pulumi.interpolate`prefix-${bucket.id}-suffix`;

// 正确 - 使用 pulumi.concat 进行简单连接
const name = pulumi.concat("prefix-", bucket.id, "-suffix");
```

**参考**：https://www.pulumi.com/docs/concepts/inputs-outputs/

---

### 3. 使用组件管理相关资源

**原因**：ComponentResource 类将相关资源分组为可重用、逻辑单元。没有组件，资源图是扁平的，这使得难以理解哪些资源属于一起，跨堆栈重用模式，或在更高层次上推理基础设施。

**检测信号**：

- 顶级创建多个相关资源而没有分组
- 堆栈中重复的资源模式应该被抽象
- 从 Pulumi 控制台难以理解资源关系

**错误示例**：

```typescript
// 扁平结构 - 没有逻辑分组，难以重用
const bucket = new aws.s3.Bucket("app-bucket");
const bucketPolicy = new aws.s3.BucketPolicy("app-bucket-policy", {
    bucket: bucket.id,
    policy: policyDoc,
});
const originAccessIdentity = new aws.cloudfront.OriginAccessIdentity("app-oai");
const distribution = new aws.cloudfront.Distribution("app-cdn", { /* ... */ });
```

**正确示例**：

```typescript
interface StaticSiteArgs {
    domain: string;
    content: pulumi.asset.AssetArchive;
}

class StaticSite extends pulumi.ComponentResource {
    public readonly url: pulumi.Output<string>;

    constructor(name: string, args: StaticSiteArgs, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:components:StaticSite", name, args, opts);

        // 在这里创建资源 - 参考实践 4 的父级设置
        const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, { parent: this });
        // ...

        this.url = distribution.domainName;
        this.registerOutputs({ url: this.url });
    }
}

// 可跨堆栈重用
const site = new StaticSite("marketing", {
    domain: "marketing.example.com",
    content: new pulumi.asset.FileArchive("./dist"),
});
```

**组件最佳实践**：

- 使用一致的类型 URN 模式：`organization:module:ComponentName`
- 在构造函数末尾调用 `registerOutputs()`
- 将输出作为类属性暴露给消费者
- 接受 `ComponentResourceOptions` 以允许调用者设置提供程序、别名等

对于深入的组件编写指南（args 设计、多语言支持、测试、分发），使用技能 `pulumi-component`。

**参考**：https://www.pulumi.com/docs/concepts/resources/components/

---

### 4. 在组件中始终设置 `parent: this`

**原因**：在 ComponentResource 中创建资源而不设置 `parent: this` 时，这些资源会出现在堆栈状态的根级别。这会破坏逻辑层次结构，使 Pulumi 控制台难以导航，并可能导致别名和重构问题。父关系是组件实际分组其子项的关键。

**检测信号**：

- 没有 `{ parent: this }` 传递给子资源的 ComponentResource 类
- 组件中的资源在控制台出现在根级别
- 添加别名到组件时出现意外行为

**错误示例**：

```typescript
class MyComponent extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:components:MyComponent", name, {}, opts);

        // 错误：没有父级设置 - 此存储桶出现在根级别
        const bucket = new aws.s3.Bucket(`${name}-bucket`);
    }
}
```

**正确示例**：

```typescript
class MyComponent extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:components:MyComponent", name, {}, opts);

        // 正确：父级建立层次结构
        const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, {
            parent: this
        });

        const policy = new aws.s3.BucketPolicy(`${name}-policy`, {
            bucket: bucket.id,
            policy: policyDoc,
        }, {
            parent: this
        });
    }
}
```

**`parent: this` 提供的功能**：

- 资源在 Pulumi 控制台中嵌套在组件下
- 删除组件会删除所有子项
- 组件上的别名自动应用于子项
- 状态文件中清晰的拥有权

**参考**：https://www.pulumi.com/docs/concepts/resources/components/

---

### 5. 从一开始就加密密钥

**原因**：标记为 `--secret` 的密钥在状态文件中加密，在 CLI 输出中掩码，并通过转换进行跟踪。从明文配置开始并稍后转换需要凭证旋转、引用更新以及对日志和状态历史记录中泄露值的审计。

**检测信号**：

- 密码、API 密钥、令牌存储为明文配置
- 嵌入凭证的连接字符串
- 明文私钥或证书

**错误示例**：

```bash
# 明文 - 将在状态和日志中可见
pulumi config set databasePassword hunter2
pulumi config set apiKey sk-1234567890
```

**正确示例**：

```bash
# 从一开始就加密
pulumi config set --secret databasePassword hunter2
pulumi config set --secret apiKey sk-1234567890
```

**在代码中**：

```typescript
const config = new pulumi.Config();

// 此处检索密钥 - 值保持加密
const dbPassword = config.requireSecret("databasePassword");

// 从密钥创建输出以保留机密性
const connectionString = pulumi.interpolate`postgres://user:${dbPassword}@host/db`;
// connectionString 也是密钥 Output

// 明确标记值为密钥
const computed = pulumi.secret(someValue);
```

**使用 Pulumi ESC 进行集中密钥管理**：

```yaml
# Pulumi.yaml
environment:
  - production-secrets  # 从 ESC 环境中获取
```

```bash
# ESC 在堆栈之间集中管理密钥
esc env set production-secrets db.password --secret "hunter2"
```

**符合密钥标准的**：

- 密码和短语
- API 密钥和令牌
- 私钥和证书
- 包含凭证的连接字符串
- OAuth 客户端密钥
- 加密密钥

**参考**：

- https://www.pulumi.com/docs/concepts/secrets/
- https://www.pulumi.com/docs/esc/

---

### 6. 重构时使用别名

**原因**：重命名资源、将它们移动到组件中或更改父级会导致 Pulumi 将它们视为新资源。如果没有别名，重构会销毁并重新创建资源，可能会导致停机或数据丢失。别名通过重构保留资源身份。

**检测信号**：

- 没有别名重命名资源
- 将资源移动到或从 ComponentResource 中移出
- 更改资源的父级
- 预览显示删除+创建，而实际上意图是更新

**错误示例**：

```typescript
// 之前：名为 "my-bucket" 的资源
const bucket = new aws.s3.Bucket("my-bucket");

// 之后：没有别名重命名 - 销毁存储桶
const bucket = new aws.s3.Bucket("application-bucket");
```

**正确示例**：

```typescript
// 之后：使用别名重命名 - 保留现有存储桶
const bucket = new aws.s3.Bucket("application-bucket", {}, {
    aliases: [{ name: "my-bucket" }],
});
```

**移动到组件中**：

```typescript
// 之前：顶级资源
const bucket = new aws.s3.Bucket("my-bucket");

// 之后：在组件中 - 需要使用旧父级的别名
class MyComponent extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("myorg:components:MyComponent", name, {}, opts);

        const bucket = new aws.s3.Bucket("bucket", {}, {
            parent: this,
            aliases: [{
                name: "my-bucket",
                parent: pulumi.rootStackResource,  // 以前在根级别
            }],
        });
    }
}
```

**别名类型**：

```typescript
// 简单名称更改
aliases: [{ name: "old-name" }]

// 父级更改
aliases: [{ name: "resource-name", parent: oldParent }]

// 完整 URN（当你知道确切的旧 URN 时）
aliases: ["urn:pulumi:stack::project::aws:s3/bucket:Bucket::old-name"]
```

**生命周期**：

1. 在重构期间添加别名
2. 在所有堆栈上运行 `pulumi up`
3. 所有堆栈更新后删除别名（可选，但保持代码清洁）

**参考**：https://www.pulumi.com/docs/iac/concepts/resources/options/aliases/

---

### 7. 部署前预览

**原因**：`pulumi preview` 显示将创建、更新或删除的内容。生产中的意外情况来自跳过预览。当资源显示为“替换”而你期望的是“更新”时，这意味着即将进行的销毁和重新创建。

**检测信号**：

- 交互式运行 `pulumi up --yes` 而不审查更改
- 对于给定更改的 CI/CD 工作流中没有任何预览步骤
- 预览输出在合并或部署批准之前未审查

**错误示例**：

```bash
# 盲目部署
pulumi up --yes
```

**正确示例**：

```bash
# 始终先预览
pulumi preview

# 审查输出，然后部署
pulumi up
```

**预览中要查找的内容**：

- `+ create` - 新资源将被创建
- `~ update` - 现有资源将在原地修改
- `- delete` - 资源将被销毁
- `+-replace` - 资源将被销毁并重新创建（可能导致停机）
- `~+-replace` - 资源将被更新，然后重新创建

**警告信号**：

- 意外的 `replace` 操作（检查不可变属性更改）
- 被删除而不应删除的资源
- 代码差异中比预期更多的更改

**CI/CD 集成**：

```yaml
# GitHub Actions 示例
jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Pulumi Preview
        uses: pulumi/actions@v5
        with:
          command: preview
          stack-name: production
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}

  deploy:
    needs: preview
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Pulumi Up
        uses: pulumi/actions@v5
        with:
          command: up
          stack-name: production
```

**PR 工作流**：

- 在每个 PR 上运行预览
- 将预览输出作为 PR 评论发布
- 在合并前要求预览审查
- 仅在合并到 main 时部署

**参考**：

- https://www.pulumi.com/docs/cli/commands/pulumi_preview/
- https://www.pulumi.com/docs/iac/packages-and-automation/continuous-delivery/github-actions/

---

## 快速参考

| 实践 | 关键信号 | 修复 |
|------|-----------|-----|
| 没有资源在 apply | `.apply()` 中 `new Resource()` | 将资源移出，直接传递 Output |
| 直接传递输出 | 使用 `.apply()` 提取的值作为输入 | 使用 Output 对象，`pulumi.interpolate` |
| 使用组件 | 扁平结构，重复模式 | 创建 ComponentResource 类 |
| 始终设置 `parent: this` | 组件子项在根级别 | 将 `{ parent: this }` 传递给所有子资源 |
| 从一开始就加密密钥 | 配置中明文密码/密钥 | 使用 `--secret` 标志，ESC |
| 重构时使用别名 | 预览中删除+创建 | 添加具有旧名称/父级的别名 |
| 部署前预览 | `pulumi up --yes` | 始终先运行 `pulumi preview` |

## 验证清单

在审查 Pulumi 代码时验证：

- [ ] 没有资源构造函数在 `apply()` 回调中
- [ ] 输出直接传递给依赖资源
- [ ] 相关资源分组在 ComponentResource 类中
- [ ] 子资源具有 `{ parent: this }`
- [ ] 敏感值使用 `config.requireSecret()` 或 `--secret`
- [ ] 重构资源具有保留身份的别名
- [ ] 部署过程包括预览步骤

## 相关技能

- **pulumi-overview**：入门技能，引导代理跨三个 Pulumi 表面（`pulumi do` CLI、IaC 项目和 Pulumi Cloud）并路由到专业技能。当任务以通用基础设施措辞开始或跨越多个 Pulumi 表面时，首先加载它。使用技能 `pulumi-overview`。
- **pulumi-component**：深入指南，用于编写 ComponentResource 类、设计 args 接口、多语言支持、测试和分发。使用技能 `pulumi-component`。
- **pulumi-automation-api**：多个堆栈的程序化编排。使用技能 `pulumi-automation-api`。
- **pulumi-esc**：集中密钥和配置管理。使用技能 `pulumi-esc`。
