# 对象存储
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的对象存储扩展。

## 概述

此技能添加了链下文件/对象存储和链上引用。`MixinObjectStorage` 混合宏提供了文件操作的底层设施；您需要使用 `Storage.ExternalBlob` 在自己的数据结构中跟踪上传的文件。

## 必要的设置清单

所有四个步骤都是强制性的。跳过任何一个步骤都会在上传时导致 `403 Forbidden: Invalid payload` 错误。

1. **mops 依赖** — 将 `caffeineai-object-storage` 添加到 `mops.toml` 的 `[dependencies]` 下。
2. **混合宏调用** — 在 `main.mo` 中包含 `include MixinObjectStorage()`（从 `"mo:caffeineai-object-storage/Mixin"` 导入）。
3. **Storage.ExternalBlob 类型** — 每个表示文件的数据字段都必须使用 `Storage.ExternalBlob`，绝不能使用 `Text`。
4. **前端 npm 包** — 安装 `@caffeineai/object-storage` 并在调用位置使用 `ExternalBlob.fromBytes(bytes, file.type, file.name)`。

关键：前端包 (`@caffeineai/object-storage`) 没有后端 mops 包 (`caffeineai-object-storage`) 是无法工作的。仅安装 npm 包而不安装 mops 包会导致静默上传失败（来自存储网关的 403 错误）。您必须一起安装这两个包。

# 后端

文件内容存储在链下。后端使用来自 `mo:caffeineai-object-storage/Storage` 的 `Storage.ExternalBlob` 类型管理对外部文件的外部引用。前端处理实际的上传/下载；后端仅存储引用。

关键：任何表示文件、图像、照片、文档或媒体的数据字段都必须使用 `Storage.ExternalBlob` 作为其类型——绝不能使用 `Text`。使用 `Text` 会破坏上传/下载代理。接受文件上传的方法参数也必须使用 `Storage.ExternalBlob`，而不是 `Text`。

正确：
```
blob : Storage.ExternalBlob
```

错误：
```
blobId : Text
imageUrl : Text
fileRef : Text
```

## 模块 API

您唯一需要从 `mo:caffeineai-object-storage/Storage` 使用的是 `ExternalBlob`（它是 `Blob`）。`Storage.mo` 中的所有其他函数都是 `MixinObjectStorage` 使用的内部基础设施——不要直接调用它们。

## 在 main.mo 中设置

`include MixinObjectStorage()` 必须放在 `main.mo` 中，而不是在自定义混合宏文件中。您自己的文件跟踪逻辑放在一个单独的混合宏中。

```motoko filepath=src/backend/main.mo
import MixinObjectStorage "mo:caffeineai-object-storage/Mixin";
import Storage "mo:caffeineai-object-storage/Storage";

actor {
  include MixinObjectStorage();

   // 跟踪文件引用
  type Data = {
        id: Text;
        blob: Storage.ExternalBlob;
        name: Text;
        // 其他元数据
    };
};
```

## 错误：不要自己实现 Storage 方法

绝不要创建 `_immutableObjectStorageCreateCertificate` 或任何其他 `_immutableObjectStorage*` 方法的自定义实现。这些是平台保留的方法名，仅由 mops 包提供的 `MixinObjectStorage` 混合宏提供。手写的实现会产生错误的返回类型，并在上传时导致 `403 Forbidden: Invalid payload` 错误。

错误——在 main.mo 中内联存根：
```motoko filepath=wrong.mo
// 错误：不要这样写
public shared func _immutableObjectStorageCreateCertificate(fileHash : Text) : async Blob {
  CertifiedData.set(Blob.fromArray(hashBytes));
  Blob.fromArray([]);
};
```

错误——模仿平台形状的自定义混合宏文件：
```motoko filepath=wrong-mixin.mo
// 错误：不要创建 src/backend/mixins/object-storage-api.mo
import ObjectStorageMixin "mixins/object-storage-api";
include ObjectStorageMixin();
```

正确的导入路径始终是 `"mo:caffeineai-object-storage/Mixin"`——一个 mops 包，绝不使用相对路径。任何相对导入，如 `"mixins/object-storage-api"` 或 `"./ObjectStorage"`，都是错误的。

平台混合宏产生的正确签名是：
```
_immutableObjectStorageCreateCertificate : (blobHash : Text) -> async record { method : Text; blob_hash : Text }
```

任何其他返回类型（`Blob`、`()`、`Text` 等）都会导致网关验证失败。

# 前端

后端 `Blob` 字段在前端表示为 `ExternalBlob`。

```typescript
import { ExternalBlob } from "@caffeineai/object-storage";
import type { FileRecord } from "@caffeineai/object-storage";
```

## ExternalBlob API

```typescript
class ExternalBlob {
  getBytes(): Promise<Uint8Array<ArrayBuffer>>;
  getDirectURL(): string;
  static fromURL(url: string): ExternalBlob;
  static fromBytes(
    blob: Uint8Array<ArrayBuffer>,
    contentType?: string,
    filename?: string,
  ): ExternalBlob;
  withUploadProgress(onProgress: (percentage: number) => void): ExternalBlob;
}
```

## 上传文件

将浏览器的 `File` 类型和文件名传递给 `fromBytes`，以便网关的 blob 树存储 `Content-Type` 和 `Content-Disposition`（原始文件名）。同时将 `file.name` 传递给后端，以便应用程序记录在列表和 UI 中保留文件名。

```typescript
const handleUpload = async (file: File) => {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const blob = ExternalBlob.fromBytes(bytes, file.type, file.name).withUploadProgress((pct) => {
    setProgress(pct);
  });

  await actor.uploadFile(file.name, blob);
};
```

网关的 GET/HEAD 响应通过 `Content-Disposition` 回显存储的文件名。保留后端的 `filename` 字段进行查询和显示，而无需访问网关。

## 显示文件

使用 `getDirectURL()` 进行内联显示（图像、视频）。这返回一个不透明的代理 URL——它没有文件扩展名，因此永远不要检查 URL 来确定文件类型。

```typescript
<img src={record.blob.getDirectURL()} alt={record.filename} />
```

## 文件类型检测

关键：永远不要通过检查 `getDirectURL()` 返回的 URL 来检测文件类型。这些是不透明的代理 URL，没有扩展名。相反，使用后端记录中的 `filename` 字段：

```typescript
const isImage = (filename: string) =>
  /\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)$/i.test(filename);

// 条件渲染
{isImage(record.filename) ? (
  <img src={record.blob.getDirectURL()} alt={record.filename} />
) : (
  <div>{record.filename}</div>
)}
```

如果后端还返回一个 `mimeType` 字段，请优先使用它：

```typescript
const isImage = (mimeType?: string) => mimeType?.startsWith("image/");
```

## 下载文件

对于需要原始文件名的下载，使用 `getBytes()` 创建可下载的链接：

```typescript
const handleDownload = async (record: FileRecord) => {
  const bytes = await record.blob.getBytes();
  const blob = new Blob([bytes]);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = record.filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeURL(url);
};
```

使用 `getDirectURL()` 进行内联显示，`getBytes()` 进行保存为下载。

## 总结

| 使用场景 | 方法 | 备注 |
|---|---|---|
| 显示图像/视频 | `blob.getDirectURL()` | 流式传输，缓存 |
| 带文件名下载 | `blob.getBytes()` | 包裹在 Blob + 锚点 |
| 从浏览器上传 | `ExternalBlob.fromBytes(bytes, file.type, file.name)` | MIME + 文件名在网关头部 |
| 检测文件类型 | `filename` 或 `mimeType` 字段 | 绝不检查 URL |

# 验证设置

确认后端已安装 mops 依赖。检查 `src/backend/mops.toml`：

```toml
[dependencies]
caffeineai-object-storage = "0.1.2"
```

如果 `[dependencies]` 中缺少 `caffeineai-object-storage`，无论前端做什么，对象存储都不会工作。添加它，运行 `mops install`，然后重新构建。

# 故障排除

| 错误 | 原因 | 解决方法 |
|---|---|---|
| `403 Forbidden: Invalid payload` on `PUT /v1/blob-tree/` | 后端 canister 缺少 `_immutableObjectStorageCreateCertificate` 或返回错误类型 | 在 mops.toml 中安装 `caffeineai-object-storage`，在 main.mo 中包含 `include MixinObjectStorage()`，重新部署 |
| `403 Forbidden: Invalid payload`（所有文件） | `@caffeineai/object-storage` npm 已安装，但 `caffeineai-object-storage` mops 未安装 | 添加 mops 依赖并重新构建后端 |
| 方法存在但仍然 403 | 手写存根返回错误类型（例如 `Blob` 或 `()` 而不是 `record { method; blob_hash }`） | 删除自定义实现，改用平台混合宏 |
| `Forbidden: Owner does not have an account with the cashier` | Cashier 注册问题（与此技能无关） | 重新部署后端 canister 以触发自我修复注册 |
