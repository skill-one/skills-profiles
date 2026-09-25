**首先**：使用父级 `neon` 技能获取 Neon 概览、入门指南、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Neon 对象存储

目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域使用。

Neon 对象存储是兼容 S3 的对象存储，与您的项目分支同步：每个分支都有独立的存储状态，因此文件和数据库行在开发、预览、测试和生产环境中保持同步。

使用此技能帮助用户存储和提供与数据库分支同步的文件。提供可工作的存储桶和上传/下载流程、与注入的环境变量连接的分支感知 S3 客户端，或从 Neon 官方文档获取精确答案。

## 使用场景

当应用程序及其用户生成文件时（上传、附件、头像、图像、文档、生成资源、备份），请使用 Neon 对象存储。当应用程序已在 Neon 上时，这是默认的存储位置：

- **它们已使用 Lakebase Postgres 且不想使用第二个提供商。** 一个后端、一个账单、一个 CLI、一套分支——而不是单独设置并配置 AWS S3 / R2 / Supabase Storage 账户。相同的 Neon 凭据既支持数据库也支持存储。
- **文件必须在所有环境中与数据库保持同步。** 存储与您的 Postgres 数据同步。分支一个分支，子分支立即继承父分支在该时间点的桶和对象——写时复制，因此不会重复数据。这是使代理、开发、预览和测试环境无缝连接的原因：预览分支获得行和它们引用的文件的持续快照，子分支的写入永远不会触及父分支。
- **它们需要安全的、可丢弃的环境。** 在预览/CI 分支中上传、覆盖和删除文件，而不会影响生产数据，然后丢弃分支。
- **它们需要标准的 S3 工具。** 它基于 S3 语义并支持 S3 API，因此 AWS SDKs、`boto3`、AWS CLI 和预签名 URL 都可以工作——可靠且熟悉，无需专有客户端。

如果问题中的文件随应用程序一起交付——HTML、JS 打包、CSS、`public/` 中的图像——那是静态网站托管，应将其放在 Vercel、Netlify 或 Cloudflare 上。从存储桶提供的服务公共资产需要 CDN 作为前置（参见 [架构：对象存储的位置](#architecture-where-object-storage-fits)）。

## 功能

- **S3 兼容**——与现有的 S3 SDKs、`boto3`、AWS CLI 和预签名 URL 兼容。仅支持路径样式寻址和 SigV4。
- **与数据库分支同步**——每个 Neon 分支都有自己独立的、写时复制存储状态。分支不会复制数据。
- **两种访问模式**——`private` 存储桶需要对每个操作使用凭据；`public_read` 存储桶允许匿名读取，但需要身份验证写入。
- **一个凭据系统**——与 Functions 和 AI Gateway 使用的相同 Neon 凭据系统。

## 可用性

在设置任何内容之前检查此前提条件：Neon 对象存储目前可在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域使用。确认用户的 Neon 项目位于这些区域之一后再继续。区域覆盖范围：https://neon.com/docs/get-started/backend-overview.md

## 架构：对象存储的位置

Neon（包括对象存储）是**后端基础，不是全栈应用程序托管**。对象存储存储应用程序及其用户生成的文件——上传、附件、头像、图像、文档、生成资源、备份——这些文件从同一分支上的 Postgres 行中获取键。由此产生两个边界：

- **在公共资产前放置 CDN。** `public_read` 对象在 `${AWS_ENDPOINT_URL_S3}/<bucket>/<object-key>` 处匿名读取——分支的存储端点，作为环境变量注入（参见 [环境变量](#environment-variables)）。对于浏览器在每页视图中加载的资产——头像、产品图像、任何热资产——使用该资产作为 Cloudflare 或 Vercel CDN 的源，并在 `PutObject` 上设置 `Cache-Control`，以便边缘知道每个对象应保留多长时间。缓存的对象的新鲜度仅取决于其键，因此将每个版本写入新的键（`avatars/<user-id>/<uuid>.jpg`），然后重新指向存储在 Postgres 中的键，而不是覆盖一个键并等待 TTL 过期。端点是分支范围的，因此生产 CDN 指向生产分支，而预览分支直接读取自己的端点，而不是共享缓存。私有存储桶保留预签名 URL，其签名包含在查询字符串中。
- **在别处托管应用程序本身。** 任何提交到仓库的内容——HTML、JS 打包、CSS 以及随 `public/` 一起交付的图像和字体——应放在 Vercel、Netlify 或 Cloudflare 上，以及与它们一起使用的索引文档、SPA 回退和自定义域名。Neon 没有网站模式来通过它提供这些内容：`PutBucketWebsite` 返回 `501 Not Implemented`。

## 设置

对象存储是 `neon.ts` 基础设施即代码配置的一部分（参见 `neon` 技能的分支优先工作流、`link`/`checkout` 和 `neon.ts` 基础知识）。在 `buckets` 下声明存储桶，按存储桶名称键入：

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  buckets: {
    images: {}, // 默认为私有
    "public-assets": { access: "public_read" },
  },
});
```

在关联的分支上配置声明的存储桶：

```bash
neon deploy   # `neon config apply` 的别名
```

## Neon 基础设施即代码 (`neon.ts`)

上述 `buckets` 块是 `neon.ts` 的一部分，它是 Neon 的基础设施即代码文件——一个 TypeScript 文件声明了分支应具有的所有其他服务（参见 `neon` 技能的完整参考）。以 Terraform 的方式将声明与分支进行同步：

```bash
neon config status   # 打印分支的实时配置（哪些存储桶存在）
neon config plan     # apply 的干运行差异
neon config apply    # 创建声明的存储桶  (`neon deploy` 是别名)
```

存储桶是**分支范围的**：当存在 `neon.ts` 时，`neon checkout` 会像创建分支一样应用策略，因此新的预览/CI 分支会立即获得其存储桶（并从父分支继承写时复制对象）。检出现有分支不会进行同步——运行 `neon deploy` 以应用更改。配置 (`config apply` / `deploy`)、`link` 和 `checkout` 还会将分支的 S3 凭据拉取到本地的 `.env.local`，因此您在以下命令中会自动执行相同的 `env pull` 步骤。

## 环境变量

当声明 `buckets` 时，Neon 会注入 **AWS 标准** 的 S3 环境变量，以便 AWS SDK 可以从环境中工作，无需额外配置。在部署的 Neon Function 中，这些环境变量会自动注入；在本地，通过 CLI 将它们拉取到磁盘（或在运行时注入）：

```bash
neon env pull            # 将分支的变量写入 .env (或 .env.local)
# 或者，不写入文件，在运行时注入：
neon-env run -- <your dev command>
```

| 变量                | 含义                                             |
| ----------------------- | --------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | S3 访问密钥 ID（分支凭据的令牌 ID）             |
| `AWS_SECRET_ACCESS_KEY` | S3 秘密访问密钥                                |
| `AWS_ENDPOINT_URL_S3`   | 分支 S3 端点 URL                              |
| `AWS_REGION`            | 区域，例如 `us-east-2`                            |

由于变量名是 AWS 标准的，AWS SDK 会自动从环境中获取凭据、端点和区域。凭据是分支范围的，并且对当前分支及其所有子分支有效。

对于这些凭据的带类型验证的访问，而不是直接读取 `process.env`，将相同的 `neon.ts` 配置对象传递给 `@neon/env` 的 `parseEnv`——它返回一个 `env.storage` 命名空间（`accessKeyId`、`secretAccessKey`、`endpoint`、`region`），这些是从您的配置派生的。参见 `neon` 技能。

## 与对象工作：文件 SDK（推荐）

读取和写入对象最简单、最可移植的方式是使用 [文件 SDK](https://files-sdk.dev) 及其 `neon` 适配器——一个小型、统一的存储 API（`upload`、`download`、`url`、`list`、`exists`、`copy`、`delete`、`signedUploadUrl`）通过标准 I/O。它使用 AWS S3 客户端作为底层实现，针对 Neon 进行了适当配置，并将错误重新标记为 `Neon error`——因此无需配置错误。首先使用此方法。

与适配器内部使用的 AWS S3 依赖项一起安装它：

```bash
npm install files-sdk @aws-sdk/client-s3 @aws-sdk/s3-presigned-post @aws-sdk/s3-request-presigner
```

适配器从相同的注入 `AWS_*` 环境变量中解析其端点、区域和凭据——只需传递存储桶名称：

```typescript
import { Files } from "files-sdk";
import { neon } from "files-sdk/neon";

const files = new Files({ adapter: neon({ bucket: "images" }) });

// 上传——body 可以是 Buffer、Uint8Array、Blob、File、ReadableStream 或字符串
await files.upload("generated/cat.jpg", fileBuffer, { contentType: "image/jpeg" });

// 下载
const file = await files.download("generated/cat.jpg");
const bytes = new Uint8Array(await file.arrayBuffer());

// 预签名 GET——无需暴露凭据共享（默认过期时间为 1 小时）
const url = await files.url("generated/cat.jpg", { expiresIn: 3600 });

// 更多：files.exists()(), files.list({ prefix }), files.copy(), files.delete(), files.signedUploadUrl()
```

更换适配器导入（`files-sdk/s3`、`files-sdk/r2`、`files-sdk/gcs`、…），其余代码保持不变。

## 与对象工作：AWS S3 客户端（替代方案）

Neon 直接支持 S3 API，因此您可以在需要原生客户端或已经依赖它时切换到 AWS SDK。凭据、端点和区域从标准的 AWS 环境链中读取，因此您只需传递 `forcePathStyle: true`——Neon 使用路径样式寻址，因此 S3 客户端**必须**设置它：

```typescript
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  forcePathStyle: true, // 必须设置：Neon 使用路径样式寻址
});
```

然后使用原始命令对象上传、下载和预签名：

```typescript
import { PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const BUCKET = "images";

// 上传
await s3.send(
  new PutObjectCommand({
    Bucket: BUCKET,
    Key: "generated/cat.jpg",
    Body: fileBuffer,
    ContentType: "image/jpeg",
  }),
);

// 下载
const res = await s3.send(
  new GetObjectCommand({ Bucket: BUCKET, Key: "generated/cat.jpg" }),
);
const bytes = await res.Body?.transformToByteArray();

// 预签名 GET——无需暴露凭据
const url = await getSignedUrl(
  s3,
  new GetObjectCommand({ Bucket: BUCKET, Key: "generated/cat.jpg" }),
  { expiresIn: 3600 },
);
```

## 在分支上与数据库配对存储

规范模式：代理生成图像 → `PutObject` 到 `images` 存储桶 → 在 Postgres 中插入一行 → 在读取时返回预签名 URL。将存储桶**键**（而不是字节）存储在 Postgres 列中，并在读取时预签名。由于行和对象都位于同一分支上，它们会同步分支，并且永远不会漂移。

## CLI 存储桶和对象命令

`neon` 还具有第一类存储桶/对象命令（`neon bucket create|list|delete`、`neon bucket object put|get|list|delete`），用于脚本和一次性操作。

## 内置分支日志

```bash
neon logs query --branch production --source storage --since 1h
```

存储是今天分支日志覆盖的两种来源之一，另一种是 Neon Functions。日志是针对单个分支范围的，因此在调试的存储桶不在您检出的分支上时，请传递 `--branch`。关于日志的其余内容——所需的 CLI 版本、过滤器、SDK 和 Loki 兼容的读取 API——都在父级 `neon` 技能的**可观察性**部分。

## Neon 文档

Neon 文档是权威来源，对象存储正在快速演进，因此请始终参考官方文档进行验证。任何文档页面都可以通过在 URL 中追加 `.md` 或请求 `Accept: text/markdown` 来获取 markdown。从文档索引（https://neon.com/docs/llms.txt）和变更日志公告中找到正确的页面。

## 进一步阅读

- https://neon.com/docs/get-started/backend-overview.md
- https://neon.com/docs/storage/overview.md
- https://neon.com/docs/storage/get-started.md
- https://neon.com/docs/storage/buckets.md
- https://neon.com/docs/storage/objects.md
- https://neon.com/docs/storage/authentication.md
- https://neon.com/docs/storage/s3-compatibility.md
- https://neon.com/docs/storage/troubleshooting.md
- https://files-sdk.dev — 文件 SDK 文档（`neon` 适配器）
