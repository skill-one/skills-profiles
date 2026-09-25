# Tigris 文件存储

使用 Tigris 对象存储存储和提供文件。涵盖 CLI 设置（存储桶、访问密钥、认证）以及 `@tigrisdata/storage` SDK 用于应用程序代码。

## 快速入门

```bash
# 1. 安装 CLI 并进行认证
npm install -g @tigrisdata/cli
tigris login

# 2. 创建存储桶和访问密钥
tigris buckets create my-app-uploads
tigris access-keys create "my-app-uploads-key"
# ⚠ 保存密钥访问密钥——仅显示一次
tigris access-keys assign tid_xxx --bucket my-app-uploads --role Editor

# 3. 安装 SDK
npm install @tigrisdata/storage
```

```bash
# .env
TIGRIS_STORAGE_ACCESS_KEY_ID=tid_xxx
TIGRIS_STORAGE_SECRET_ACCESS_KEY=tsec_yyy
TIGRIS_STORAGE_ENDPOINT=https://t3.storage.dev
TIGRIS_STORAGE_BUCKET=my-app-uploads
```

```typescript
import { put } from "@tigrisdata/storage";

// 文件默认为私密——只有经过认证的请求才能访问它们
const result = await put("avatars/user-123.jpg", file);
if (result.error) throw result.error;
console.log(result.data?.url);

// 只有当匿名用户需要直接 URL 访问时，才使用访问: "public"
// const result = await put("avatars/user-123.jpg", file, { access: "public" });
```

有关详细步骤，请参阅下方的 **使用 CLI 入门**。

---

## 使用 CLI 入门

### 第 1 步：安装 CLI

```bash
npm install -g @tigrisdata/cli
```

验证安装：

```bash
tigris --version
```

`t3` 是 `tigris` 的别名——所有命令都可以使用。

### 第 2 步：认证

```bash
tigris login
```

打开浏览器进行 OAuth。登录后，验证：

```bash
tigris whoami
```

对于 CI/CD 或非交互式环境：

```bash
tigris configure --access-key <key> --access-secret <secret>
```

### 第 3 步：创建存储桶

```bash
tigris buckets create my-app-uploads
```

要点：

- 存储桶默认为 **私密**。使用 `--public` 可公开读取对象。
- 存储桶默认为 **全局**。使用 `--locations` 可固定到特定区域。
- 在任何命令后输入 `help` 可查看其选项（例如，`tigris buckets create help`）。

### 第 4 步：创建访问密钥

```bash
tigris access-keys create "my-app-uploads-key"
```

这将输出访问密钥 ID (`tid_xxx`) 和密钥访问密钥 (`tsec_yyy`)。

**密钥访问密钥仅显示一次。** 立即复制它。名称字段仅用于人类识别——它没有功能影响。

### 第 5 步：配置环境

在项目根目录下创建 `.env`：

```bash
TIGRIS_STORAGE_ACCESS_KEY_ID=tid_xxx
TIGRIS_STORAGE_SECRET_ACCESS_KEY=tsec_yyy
TIGRIS_STORAGE_ENDPOINT=https://t3.storage.dev
TIGRIS_STORAGE_BUCKET=my-app-uploads
```

`TIGRIS_STORAGE_BUCKET` 设置所有 SDK 调用的默认存储桶。将 `.env` 添加到 `.gitignore`——永远不要提交凭证。

### 第 6 步：将访问密钥分配给存储桶

```bash
tigris access-keys assign tid_xxx --bucket my-app-uploads --role Editor
```

**角色：**

| 角色       | 权限                        | 使用场景                                 |
| ---------- | --------------------------- | ---------------------------------------- |
| `Editor`   | 读取 + 写入 + 删除对象      | 上传/删除文件的 App 服务器               |
| `ReadOnly` | 仅读取对象                  | 仅提供/下载文件的 App                   |

现在你有了：

- 一个存储桶 (`my-app-uploads`)
- 一个访问密钥 (`tid_xxx` / `tsec_yyy`)
- 将密钥分配给存储桶并具有 Editor 角色
- 一个准备用于 SDK 的 `.env` 文件

### 第 7 步：安装 SDK

```bash
npm install @tigrisdata/storage
# 或
yarn add @tigrisdata/storage
```

支持 ES Modules 和 CommonJS。

---

## SDK 参考

所有方法都返回 `TigrisStorageResponse<T, E>`。始终先检查 `error`：

```typescript
const result = await put("file.txt", "hello");
if (result.error) {
  console.error(result.error);
  return;
}
console.log(result.data);
```

### config — 覆盖默认配置

每个方法都接受一个可选的 `config` 参数，类型为 `TigrisStorageConfig`：

```typescript
type TigrisStorageConfig = {
  bucket?: string;          // 覆盖 TIGRIS_STORAGE_BUCKET
  accessKeyId?: string;     // 覆盖 TIGRIS_STORAGE_ACCESS_KEY_ID
  secretAccessKey?: string; // 覆盖 TIGRIS_STORAGE_SECRET_ACCESS_KEY
  endpoint?: string;        // 覆盖 TIGRIS_STORAGE_ENDPOINT
};
```

使用 `config` 可针对不同存储桶或每次调用使用不同凭证：

```typescript
// 上传到不同存储桶
await put("report.pdf", data, { config: { bucket: "reports-archive" } });

// 使用单独的只读密钥下载
await get("file.txt", "string", { config: { accessKeyId: "tid_ro", secretAccessKey: "tsec_ro" } });
```

### put — 上传

```typescript
put(path: string, body: string | ReadableStream | Blob | Buffer, options?: PutOptions)
```

```typescript
import { put } from "@tigrisdata/storage";

// 简单文本上传
const result = await put("notes/hello.txt", "Hello, World!");

// 带有公共访问权限的图片
const result = await put("avatars/user-123.jpg", file, {
  access: "public",
  contentType: "image/jpeg",
  addRandomSuffix: false,
});

// 大文件使用多部分上传和进度
const result = await put("videos/demo.mp4", fileStream, {
  multipart: true,
  onUploadProgress: ({ loaded, total, percentage }) => {
    console.log(`${loaded}/${total} bytes (${percentage}%)`);
  },
});

// 防止意外覆盖
const result = await put("config.json", data, {
  allowOverwrite: false,
});
```

**Put 选项：**

| 选项             | 值              | 默认    | 目的                       |
| ------------------ | ------------------- | ---------- | ----------------------------- |
| access             | `public`, `private` | `private`  | 对象可见性             |
| addRandomSuffix    | boolean             | `false`    | 为避免用户上传的文件名冲突而添加随机后缀 |
| allowOverwrite     | boolean             | `true`     | 允许替换现有文件         |
| contentType        | MIME 字符串         | 推断   | 内容类型标头           |
| contentDisposition | `inline`,`attachment`| `inline`  | 浏览器显示行为      |
| multipart          | boolean             | `false`    | 用于大文件             |
| onUploadProgress   | 回调            | —          | `{loaded, total, percentage}` |
| config             | `TigrisStorageConfig` | —        | 覆盖存储桶/凭证（见 config 部分） |

**响应数据：** `{ url, path, size, contentType, contentDisposition, modified }`

### get — 下载

```typescript
get(path: string, format: "string" | "file" | "stream", options?: GetOptions)
```

```typescript
import { get } from "@tigrisdata/storage";

// 读取为字符串（文本、JSON）
const result = await get("notes/hello.txt", "string");
console.log(result.data); // "Hello, World!"

// 作为文件提供（用于 API 路由）
const result = await get("avatars/user-123.jpg", "file", {
  contentDisposition: "inline",
});

// 触发浏览器下载
const result = await get("reports/q4.pdf", "file", {
  contentDisposition: "attachment",
});

// 流式传输大文件
const result = await get("videos/demo.mp4", "stream");
```

**Get 选项：**

| 选项             | 值               | 默认  | 目的               |
| ------------------ | -------------------- | -------- | --------------------- |
| contentDisposition | `inline`,`attachment`| `inline` | 显示 vs 下载   |
| contentType        | MIME 字符串          | 从上传 | 覆盖内容类型     |
| encoding           | string               | `utf-8`  | 文本编码         |
| config             | `TigrisStorageConfig` | —       | 覆盖存储桶/凭证（见 config 部分） |

### remove — 删除

```typescript
remove(path: string, options?: RemoveOptions)
```

```typescript
import { remove } from "@tigrisdata/storage";

const result = await remove("notes/hello.txt");
if (result.error) {
  console.error(result.error);
}
```

### list — 列出对象

```typescript
list(options?: ListOptions)
```

```typescript
import { list } from "@tigrisdata/storage";

// 列出所有对象
const result = await list();
console.log(result.data?.items);

// 按前缀过滤
const result = await list({ prefix: "avatars/" });

// 分页浏览所有对象
const allFiles = [];
let page = await list({ limit: 100 });
allFiles.push(...(page.data?.items ?? []));

while (page.data?.hasMore) {
  page = await list({
    limit: 100,
    paginationToken: page.data.paginationToken,
  });
  allFiles.push(...(page.data?.items ?? []));
}
```

**List 选项：**

| 选项          | 目的                                |
| --------------- | -------------------------------------- |
| prefix          | 过滤以该字符串开头的键              |
| delimiter       | 分组键（例如，`"/"` 用于文件夹）   |
| limit           | 每页最大对象数（默认：100）    |
| paginationToken | 从上一页继续                      |
| config          | `TigrisStorageConfig` — 覆盖存储桶/凭证（见 config 部分） |

**响应数据：** `{ items, paginationToken, hasMore }`

### head — 对象元数据

```typescript
head(path: string, options?: HeadOptions)
```

```typescript
import { head } from "@tigrisdata/storage";

const result = await head("avatars/user-123.jpg");
if (!result.error) {
  console.log(result.data);
  // { path, size, contentType, contentDisposition, modified, url }
}
```

### getPresignedUrl — 临时 URL

```typescript
getPresignedUrl(path: string, options: GetPresignedUrlOptions)
```

```typescript
import { getPresignedUrl } from "@tigrisdata/storage";

// 临时下载链接（1 小时）
const result = await getPresignedUrl("reports/q4.pdf", {
  operation: "get",
  expiresIn: 3600,
});
console.log(result.data?.url);

// 临时上传链接（10 分钟）
const result = await getPresignedUrl("uploads/photo.jpg", {
  operation: "put",
  expiresIn: 600,
});
```

**临时 URL 选项：**

| 选项      | 值      | 默认 | 目的           |
| ----------- | ----------- | ------- | ----------------- |
| operation   | `get`,`put` | —       | URL 目的       |
| expiresIn   | 秒       | `3600`  | 过期时间       |
| contentType | MIME 字符串 | —       | PUT 所需       |
| config      | `TigrisStorageConfig` | — | 覆盖存储桶/凭证（见 config 部分） |

**响应数据：** `{ url, method, expiresIn }`

---

## 客户端上传

直接从浏览器上传文件到 Tigris，而无需将字节路由到您的服务器。底层使用临时 URL。

### 服务器 — 处理上传请求

```typescript
// app/api/upload/route.ts
import { NextRequest, NextResponse } from "next/server";
import { handleClientUpload } from "@tigrisdata/storage";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { data, error } = await handleClientUpload(body);
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    return NextResponse.json({ data });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to process upload request" },
      { status: 500 },
    );
  }
}
```

### 客户端 — 直接上传

```typescript
"use client";

import { upload } from "@tigrisdata/storage/client";
import { useState } from "react";

export default function FileUpload() {
  const [progress, setProgress] = useState(0);
  const [url, setUrl] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const result = await upload(file.name, file, {
      url: "/api/upload",
      access: "private",
      multipart: true,
      partSize: 10 * 1024 * 1024,
      onUploadProgress: ({ percentage }) => {
        setProgress(percentage);
      },
    });

    setUrl(result.url);
  };

  return (
    <>
      <input type="file" onChange={handleFileChange} />
      {progress > 0 && progress < 100 && <div>{progress}%</div>}
      {url && <div>Uploaded: {url}</div>}
    </>
  );
}
```

**客户端上传选项：**

| 选项           | 必填 | 目的                              |
| ---------------- | -------- | ------------------------------------ |
| url              | 是      | 后端临时 URL 端点                |
| access           | 否       | `public` 或 `private` (默认)      |
| multipart        | 否       | 用于大文件                       |
| partSize         | 否       | 每个部分的字节数 (默认: 5 MiB)      |
| concurrency      | 否       | 并行部分上传 (默认: 4)             |
| contentType      | 否       | MIME 类型                          |
| onUploadProgress | 否       | `{loaded, total, percentage}`        |

### React 组件（可选）

`npm install @tigrisdata/react` 提供了一个即插即用的 `<Uploader>` 组件，内置了文件选择、进度和错误处理。有关用法，请参阅 `@tigrisdata/react` 文档。

---

## 严格规则

**始终：** 在 `result.data` 之前检查 `result.error` | 默认将文件上传为 `private`——只有当匿名用户需要直接 URL 访问时，才设置 `access: "public"` | 使用 `handleClientUpload` 进行浏览器上传（不要将字节路由到服务器） | 对于超过 100MB 的文件，使用 `multipart: true` | 使用 `hasMore` + `paginationToken` 分页 `list()` | 替换时删除旧文件（没有自动清理） | 明确设置 `contentType` 当它很重要时

**绝不：** 将访问密钥暴露给客户端（使用 `handleClientUpload` + `upload()` 从 `@tigrisdata/storage/client`） | 跳过错误检查 | 使用通用路径（如 `file.jpg`（使用 `avatars/${userId}.jpg` 或时间戳）） | 创建时忘记保存密钥访问密钥（仅显示一次）

---

## 已知问题

| 问题                        | 原因 & 修复                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| 上传时出现 "Access denied"      | 密钥未分配给存储桶。运行 `tigris access-keys assign tid_xxx --bucket <name> --role Editor` |
| SDK 显示 "Bucket not found"    | `.env` 中的存储桶名称错误。使用 `tigris buckets list` 验证                     |
| 失去密钥访问密钥         | 无法恢复。创建新的：`tigris access-keys create "new-key"` 并重新分配          |
| 文件无法公开访问          | 存储桶默认为私密。使用 `--public` 标志或 `put()` 上的 `access: "public"`      |
| 大文件上传挂起          | 为超过 100MB 的文件添加 `multipart: true` 到 put 选项                             |
| 列表返回不完整的结果    | 默认限制为 100。使用 `hasMore` + `paginationToken` 进行分页                    |
| 客户端上传失败（CORS/500） | 服务器路由必须使用 `@tigrisdata/storage` 的 `handleClientUpload`                   |

---

## CLI 快速参考

`t3` 是 `tigris` 的别名。在任何命令后输入 `help` 可获取选项。

```bash
# 认证
tigris login
tigris whoami

# 存储桶
tigris buckets create <name> [--public] [--locations <region>]
tigris buckets list
tigris buckets delete <name>

# 访问密钥
tigris access-keys create "<name>"
tigris access-keys assign <tid_xxx> --bucket <name> --role Editor

# 对象
tigris cp <src> <dest> [-r]         # 上传/下载/复制
tigris mv <src> <dest> [-rf]        # 移动或重命名
tigris rm <path> [-rf]              # 删除
tigris ls [bucket/prefix]           # 列出
tigris stat <path>                  # 元数据
tigris presign <path>               # 临时 URL
tigris touch <path>                 # 创建空对象
```

远程路径使用 `t3://` 前缀：`t3://my-bucket/path/file.txt`

---

## 框架集成指南

对于特定框架的上传/下载模式，请阅读您的框架资源文件：

| 框架 | SDK | 资源 |
|-----------|-----|----------|
| Next.js | `@tigrisdata/storage` (原生) | 阅读 `./resources/nextjs.md` — Server Actions, API Routes, next/image, 客户端上传 |
| Remix | `@tigrisdata/storage` (原生) | 阅读 `./resources/remix.md` — action 函数, loaders, 客户端上传 |
| Express | `@tigrisdata/storage` (原生) | 阅读 `./resources/express.md` — Multer, 流式上传, 客户端上传 |
| Rails | `aws-sdk-s3` (目前还没有原生的 Ruby SDK) | 阅读 `./resources/rails.md` — Active Storage, 直接上传, 图像变体 |
| Django | `tigris-boto3-ext` + `django-storages` | 使用 **tigris-python-sdk** 技能——涵盖 FileField, django-storages, 临时 URL |
| Laravel | `league/flysystem-aws-s3-v3` (目前还没有原生的 PHP SDK) | 阅读 `./resources/laravel.md` — Storage facade, Livewire 上传, 临时 URL |

### 部署

| 框架 | 平台 | 使用设置环境变量 |
|-----------|----------|-------------------|
| Next.js | Vercel | Dashboard → Settings → Environment Variables |
| Remix | Fly.io | `fly secrets set TIGRIS_STORAGE_ACCESS_KEY_ID=... ...` |
| Express | Docker | `-e` 标志或 `.env` 在 Compose |
| Rails | Fly.io / Kamal | `fly secrets set` 或 `kamal env push` |
| Laravel | Forge / Vapor | Dashboard → Environment 或 `vapor env:pull` |

---

## 相关技能

- **tigris-python-sdk** — 通过 boto3 的 Python 访问，Django 上传，快照，分支，Bundle API
- **tigris-bucket-management** — 高级存储桶选项（区域，层，快照）
- **tigris-object-operations** — 详细 SDK 函数参考
- **tigris-snapshots-forking** — 点时间恢复和存储桶分支

## 官方文档

- SDK: https://www.tigrisdata.com/docs/sdks/tigris/
- 客户端上传: https://www.tigrisdata.com/docs/sdks/tigris/client-uploads/
- 示例: https://www.tigrisdata.com/docs/sdks/tigris/examples/
