# Tigris 对象操作

## 前置条件

**在其他任何操作之前**，如果 Tigris CLI 尚未安装，请执行以下命令进行安装：

```bash
tigris help || npm install -g @tigrisdata/cli
```

如果需要安装，请告知用户："我正在安装 Tigris CLI (`@tigrisdata/cli`)，以便我们可以使用 Tigris 对象存储。"

## 概述

Tigris 存储 提供对象操作：上传（put）、下载（get）、删除（remove）、列出、元数据（head）和预签名 URL。

所有方法都返回 `TigrisStorageResponse<T, E>` - 首先检查 `error` 属性。

## 快速参考

| 操作     | 函数                         | 关键参数                    |
| -------- | ---------------------------- | --------------------------- |
| 上传     | `put(path, body, options)`   | path、body、access、contentType |
| 下载     | `get(path, format, options)` | path、format（string/file/stream） |
| 删除     | `remove(path, options)`      | path                        |
| 列出     | `list(options)`              | prefix、limit、paginationToken |
| 元数据   | `head(path, options)`        | path                        |
| 预签名 URL | `getPresignedUrl(path, options)` | path、operation（get/put） |

## 上传 (put)

```typescript
import { put } from "@tigrisdata/storage";

// 简单上传
const result = await put("simple.txt", "Hello, World!");
if (result.error) {
  console.error("Error:", result.error);
} else {
  console.log("Uploaded:", result.data?.url);
}

// 大文件带进度
const result = await put("large.mp4", fileStream, {
  multipart: true,
  onUploadProgress: ({ loaded, total, percentage }) => {
    console.log(`${loaded}/${total} bytes (${percentage}%)`);
  },
});

// 防止覆盖
const result = await put("config.json", config, {
  allowOverwrite: false,
});
```

## Put 选项

| 选项             | 值             | 默认值  | 目的                  |
| ---------------- | -------------- | ------- | --------------------- |
| access           | public/private | -       | 对象可见性            |
| addRandomSuffix  | boolean        | false   | 避免命名冲突          |
| allowOverwrite   | boolean        | true    | 允许替换现有对象      |
| contentType       | string         | inferred | MIME 类型             |
| contentDisposition | inline/attachment | inline | 下载行为              |
| multipart        | boolean        | false   | 启用大文件上传        |
| onUploadProgress | callback      | -       | 跟踪上传进度          |

## 下载 (get)

```typescript
import { get } from "@tigrisdata/storage";

// 下载为字符串
const result = await get("object.txt", "string");
if (result.error) {
  console.error("Error:", result.error);
} else {
  console.log("Content:", result.data);
}

// 下载为文件（浏览器触发下载）
const result = await get("object.pdf", "file", {
  contentDisposition: "attachment",
});

// 下载为流
const result = await get("video.mp4", "stream");
const reader = result.data?.getReader();
// 处理流...
```

## Get 选项

| 选项             | 值             | 默认值     | 目的            |
| ---------------- | -------------- | --------- | -------------- |
| contentDisposition | inline/attachment | inline    | 下载行为        |
| contentType       | string         | from upload | MIME 类型       |
| encoding         | string         | utf-8     | 文本编码        |
| snapshotVersion  | string         | -         | 从快照读取      |

## 删除 (remove)

```typescript
import { remove } from "@tigrisdata/storage";

const result = await remove("object.txt");
if (result.error) {
  console.error("Error:", result.error);
} else {
  console.log("Deleted successfully");
}
```

## 列出对象

```typescript
import { list } from "@tigrisdata/storage";

// 列出所有对象
const result = await list();
console.log("Objects:", result.data?.items);

// 带前缀的列表（文件夹）
const result = await list({ prefix: "images/" });

// 分页列表
const allFiles = [];
let currentPage = await list({ limit: 10 });
allFiles.push(...currentPage.data?.items);

while (currentPage.data?.hasMore) {
  currentPage = await list({
    limit: 10,
    paginationToken: currentPage.data?.paginationToken,
  });
  allFiles.push(...currentPage.data?.items);
}
```

## List 选项

| 选项          | 目的                              |
| ------------- | -------------------------------- |
| prefix        | 过滤以 prefix 开头的键            |
| delimiter     | 分组键（例如，'/' 用于文件夹）     |
| limit         | 返回的最大对象数量（默认：100）    |
| paginationToken | 继续之前的列表                   |
| snapshotVersion | 从快照列出                       |

## 对象元数据 (head)

```typescript
import { head } from "@tigrisdata/storage";

const result = await head("object.txt");
if (result.error) {
  console.error("Error:", result.error);
} else {
  console.log("Metadata:", result.data);
  // { path, size, contentType, modified, url, contentDisposition }
}
```

## 预签名 URL

```typescript
import { getPresignedUrl } from "@tigrisdata/storage";

// GET 的预签名 URL（临时访问）
const result = await getPresignedUrl("object.txt", {
  operation: "get",
  expiresIn: 3600, // 1 小时
});
console.log("URL:", result.data?.url);

// PUT 的预签名 URL（允许客户端上传）
const result = await getPresignedUrl("upload.txt", {
  operation: "put",
  expiresIn: 600, // 10 分钟
});
```

## 预签名 URL 选项

| 选项      | 值       | 默认值 | 目的         |
| --------- | -------- | ------ | ----------- |
| operation | get/put | -      | URL 目的     |
| expiresIn | 秒       | 3600   | URL 过期时间 |
| contentType | string   | -      | PUT 需要的值 |

## 常见错误

| 错误                      | 修复                                                  |
| ------------------------- | ---------------------------------------------------- |
| 先不检查 `error`          | 总是检查 `if (result.error)` 之后再 `result.data`     |
| `get()` 中的格式错误      | 使用 'string'、'file' 或 'stream'                    |
| 忘记 `multipart: true`    | 对于大于 100MB 的文件启用                          |
| 忽略分页                  | 使用 `hasMore` 和 `paginationToken`                  |

## 客户端上传

对于浏览器上传，使用客户端包直接上传到 Tigris：

```typescript
import { upload } from "@tigrisdata/storage/client";

const result = await upload(file.name, file, {
  url: "/api/upload", // 您的后端端点
  onUploadProgress: ({ percentage }) => {
    console.log(`${percentage}%`);
  },
});
```

对于初始设置，请参阅 **file-storage**。
