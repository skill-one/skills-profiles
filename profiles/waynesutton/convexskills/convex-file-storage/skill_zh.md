# 凸面文件存储

在凸面应用程序中，使用正确的模式处理图像、文档和生成文件的文件上传、存储、服务和管理工作。

## 文档来源

在实现之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/file-storage
- 上传文件：https://docs.convex.dev/file-storage/upload-files
- 服务文件：https://docs.convex.dev/file-storage/serve-files
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 文件存储概述

凸面提供内置文件存储，具有：

- 自动生成服务文件的 URL
- 支持任何文件类型（图像、PDF、视频等）
- 通过 `_storage` 系统表获取文件元数据
- 与突变和动作集成

### 生成上传 URL

```typescript
// convex/files.ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const generateUploadUrl = mutation({
  args: {},
  returns: v.string(),
  handler: async (ctx) => {
    return await ctx.storage.generateUploadUrl();
  },
});
```

### 客户端上传

```typescript
// React 组件
import { useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { useState } from "react";

function FileUploader() {
  const generateUploadUrl = useMutation(api.files.generateUploadUrl);
  const saveFile = useMutation(api.files.saveFile);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      // 第一步：获取上传 URL
      const uploadUrl = await generateUploadUrl();

      // 第二步：将文件上传到存储
      const result = await fetch(uploadUrl, {
        method: "POST",
        headers: { "Content-Type": file.type },
        body: file,
      });

      const { storageId } = await result.json();

      // 第三步：将文件引用保存到数据库
      await saveFile({
        storageId,
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size,
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={handleUpload}
        disabled={uploading}
      />
      {uploading && <p>正在上传...</p>}
    </div>
  );
}
```

### 保存文件引用

```typescript
// convex/files.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const saveFile = mutation({
  args: {
    storageId: v.id("_storage"),
    fileName: v.string(),
    fileType: v.string(),
    fileSize: v.number(),
  },
  returns: v.id("files"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("files", {
      storageId: args.storageId,
      fileName: args.fileName,
      fileType: args.fileType,
      fileSize: args.fileSize,
      uploadedAt: Date.now(),
    });
  },
});
```

### 通过 URL 服务文件

```typescript
// convex/files.ts
export const getFileUrl = query({
  args: { storageId: v.id("_storage") },
  returns: v.union(v.string(), v.null()),
  handler: async (ctx, args) => {
    return await ctx.storage.getUrl(args.storageId);
  },
});

// 使用 URL 获取文件
export const getFile = query({
  args: { fileId: v.id("files") },
  returns: v.union(
    v.object({
      _id: v.id("files"),
      fileName: v.string(),
      fileType: v.string(),
      fileSize: v.number(),
      url: v.union(v.string(), v.null()),
    }),
    v.null()
  ),
  handler: async (ctx, args) => {
    const file = await ctx.db.get(args.fileId);
    if (!file) return null;

    const url = await ctx.storage.getUrl(file.storageId);
    
    return {
      _id: file._id,
      fileName: file.fileName,
      fileType: file.fileType,
      fileSize: file.fileSize,
      url,
    };
  },
});
```

### 在 React 中显示文件

```typescript
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function FileDisplay({ fileId }: { fileId: Id<"files"> }) {
  const file = useQuery(api.files.getFile, { fileId });

  if (!file) return <div>加载中...</div>;
  if (!file.url) return <div>文件未找到</div>;

  // 处理不同文件类型
  if (file.fileType.startsWith("image/")) {
    return <img src={file.url} alt={file.fileName} />;
  }

  if (file.fileType === "application/pdf") {
    return (
      <iframe
        src={file.url}
        title={file.fileName}
        width="100%"
        height="600px"
      />
    );
  }

  return (
    <a href={file.url} download={file.fileName}>
      下载 {file.fileName}
    </a>
  );
}
```

### 从动作中存储生成文件

```typescript
// convex/generate.ts
"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

export const generatePDF = action({
  args: { content: v.string() },
  returns: v.id("_storage"),
  handler: async (ctx, args) => {
    // 生成 PDF（示例使用库）
    const pdfBuffer = await generatePDFFromContent(args.content);

    // 转换为 Blob
    const blob = new Blob([pdfBuffer], { type: "application/pdf" });

    // 存储到 Convex
    const storageId = await ctx.storage.store(blob);

    return storageId;
  },
});

// 生成并保存图像
export const generateImage = action({
  args: { prompt: v.string() },
  returns: v.id("_storage"),
  handler: async (ctx, args) => {
    // 调用外部 API 生成图像
    const response = await fetch("https://api.example.com/generate", {
      method: "POST",
      body: JSON.stringify({ prompt: args.prompt }),
    });

    const imageBuffer = await response.arrayBuffer();
    const blob = new Blob([imageBuffer], { type: "image/png" });

    return await ctx.storage.store(blob);
  },
});
```

### 访问文件元数据

```typescript
// convex/files.ts
import { query } from "./_generated/server";
import { v } from "convex/values";
import { Id } from "./_generated/dataModel";

type FileMetadata = {
  _id: Id<"_storage">;
  _creationTime: number;
  contentType?: string;
  sha256: string;
  size: number;
};

export const getFileMetadata = query({
  args: { storageId: v.id("_storage") },
  returns: v.union(
    v.object({
      _id: v.id("_storage"),
      _creationTime: v.number(),
      contentType: v.optional(v.string()),
      sha256: v.string(),
      size: v.number(),
    }),
    v.null()
  ),
  handler: async (ctx, args) => {
    const metadata = await ctx.db.system.get(args.storageId);
    return metadata as FileMetadata | null;
  },
});
```

### 删除文件

```typescript
// convex/files.ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const deleteFile = mutation({
  args: { fileId: v.id("files") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const file = await ctx.db.get(args.fileId);
    if (!file) return null;

    // 从存储中删除
    await ctx.storage.delete(file.storageId);

    // 删除数据库记录
    await ctx.db.delete(args.fileId);

    return null;
  },
});
```

### 带预览的图像上传

```typescript
import { useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { useState, useRef } from "react";

function ImageUploader({ onUpload }: { onUpload: (id: Id<"files">) => void }) {
  const generateUploadUrl = useMutation(api.files.generateUploadUrl);
  const saveFile = useMutation(api.files.saveFile);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith("image/")) {
      alert("请选择图像文件");
      return;
    }

    // 验证文件大小（最大 10MB）
    if (file.size > 10 * 1024 * 1024) {
      alert("文件大小必须小于 10MB");
      return;
    }

    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);

    // 上传
    setUploading(true);
    try {
      const uploadUrl = await generateUploadUrl();
      const result = await fetch(uploadUrl, {
        method: "POST",
        headers: { "Content-Type": file.type },
        body: file,
      });

      const { storageId } = await result.json();
      const fileId = await saveFile({
        storageId,
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size,
      });

      onUpload(fileId);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        style={{ display: "none" }}
      />
      
      <button
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
      >
        {uploading ? "正在上传..." : "选择图像"}
      </button>

      {preview && (
        <img
          src={preview}
          alt="预览"
          style={{ maxWidth: 200, marginTop: 10 }}
        />
      )}
    </div>
  );
}
```

## 示例

### 文件存储模式

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  files: defineTable({
    storageId: v.id("_storage"),
    fileName: v.string(),
    fileType: v.string(),
    fileSize: v.number(),
    uploadedBy: v.id("users"),
    uploadedAt: v.number(),
  })
    .index("by_user", ["uploadedBy"])
    .index("by_type", ["fileType"]),

  // 用户头像
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarStorageId: v.optional(v.id("_storage")),
  }),

  // 带图像的帖子
  posts: defineTable({
    authorId: v.id("users"),
    content: v.string(),
    imageStorageIds: v.array(v.id("_storage")),
    createdAt: v.number(),
  }).index("by_author", ["authorId"]),
});
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何 git 命令
- 在上传之前在客户端验证文件类型和大小
- 将文件元数据（名称、类型、大小）存储在您自己的表中
- 仅将 `_storage` 系统表用于 Convex 元数据
- 删除数据库引用时删除存储文件
- 上传时使用适当的 Content-Type 标头
- 考虑对大图像进行优化

## 常见陷阱

1. **未设置 Content-Type 标头** - 文件可能无法正确服务
2. **忘记删除存储** - 或phaned 文件浪费存储
3. **未验证文件类型** - 对恶意上传构成安全风险
4. **没有进度的大文件上传** - 对用户体验不佳
5. **使用已弃用的 getMetadata** - 使用 ctx.db.system.get 代替

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- 文件存储：https://docs.convex.dev/file-storage
- 上传文件：https://docs.convex.dev/file-storage/upload-files
- 服务文件：https://docs.convex.dev/file-storage/serve-files
