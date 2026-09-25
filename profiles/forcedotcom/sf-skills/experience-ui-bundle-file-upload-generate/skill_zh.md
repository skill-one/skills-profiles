# 文件上传 API (工作流)

当用户需要在 React UI 包中实现文件上传功能时，请遵循此工作流。此功能仅提供 **API** — 您必须使用提供的 API 自行构建 UI 组件。

## 关键：这是一个仅提供 API 的包

该包导出 **程序化 API**，而不是 React 组件或钩子。您将：

- 使用 `upload()` 函数处理带进度跟踪的文件上传
- 构建自己的自定义 UI（文件输入框、拖放区域、进度条等）
- 通过 `onProgress` 回调跟踪上传进度

**不要：**

- 期待预构建的组件，如 `<FileUpload />` — 它们不会被导出
- 尝试导入 React 钩子，如 `useFileUpload` — 它们不会被导出
- 寻找拖放组件 — 它们不会被导出

源代码包含用于演示的参考组件，但它们是 **不可导入** 的。使用它们作为构建自己的 UI 的示例。

## 1. 安装包

```bash
npm install @salesforce/ui-bundle-template-feature-react-file-upload
```

依赖项将自动安装：

- `@salesforce/ui-bundle` (API 客户端)
- `@salesforce/platform-sdk` (数据 SDK；旧 `@salesforce/sdk-data` 的名称已过时 — 请参阅 `experience-ui-bundle-salesforce-data-access` 技能)

## 2. 了解三种上传模式

### 模式 A：基本上传（无记录链接）

将文件上传到 Salesforce 并获取每个文件的 `contentBodyId`。不会创建 ContentVersion 记录。

**何时使用：**

- 用户希望先上传文件，然后稍后创建/链接到记录
- 构建多步骤表单，其中记录尚不存在
- 延迟记录链接场景

```tsx
import { upload } from "@salesforce/ui-bundle-template-feature-react-file-upload";

const results = await upload({
  files: [file1, file2],
  onProgress: (progress) => {
    console.log(`${progress.fileName}: ${progress.status} - ${progress.progress}%`);
  },
});

// results[0].contentBodyId: "069..." (始终可用)
// results[0].contentVersionId: undefined (未链接到记录)
```

### 模式 B：立即记录链接上传

上传文件并立即通过创建 ContentVersion 记录将它们链接到现有的 Salesforce 记录。

**何时使用：**

- 记录已存在（账户、机会、案例等）
- 用户希望文件立即附加到记录
- 直接上传并附加场景

```tsx
import { upload } from "@salesforce/ui-bundle-template-feature-react-file-upload";

const results = await upload({
  files: [file1, file2],
  recordId: "001xx000000yyyy", // 现有记录 ID
  onProgress: (progress) => {
    console.log(`${progress.fileName}: ${progress.status} - ${progress.progress}%`);
  },
});

// results[0].contentBodyId: "069..." (始终可用)
// results[0].contentVersionId: "068..." (链接到记录)
```

### 模式 C：延迟记录链接（记录创建流程）

上传文件而不带记录，然后在记录创建后链接它们。

**何时使用：**

- 构建“带附件创建记录”表单
- 记录在表单提交时才存在
- 需要在知道最终记录 ID 之前上传文件

```tsx
import {
  upload,
  createContentVersion,
} from "@salesforce/ui-bundle-template-feature-react-file-upload";

// 第 1 步：上传文件（无 recordId）
const uploadResults = await upload({
  files: [file1, file2],
  onProgress: (progress) => console.log(progress),
});

// 第 2 步：创建记录
const newRecordId = await createRecord(formData);

// 第 3 步：将上传的文件链接到新记录
for (const file of uploadResults) {
  const contentVersionId = await createContentVersion(
    new File([""], file.fileName),
    file.contentBodyId,
    newRecordId,
  );
}
```

## 3. 构建自定义 UI

该包提供后端 — 您构建前端。以下是一个最小示例：

```tsx
import {
  upload,
  type FileUploadProgress,
} from "@salesforce/ui-bundle-template-feature-react-file-upload";
import { useState } from "react";

function CustomFileUpload({ recordId }: { recordId?: string }) {
  const [progress, setProgress] = useState<Map<string, FileUploadProgress>>(new Map());

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);

    await upload({
      files,
      recordId,
      onProgress: (fileProgress) => {
        setProgress((prev) => new Map(prev).set(fileProgress.fileName, fileProgress));
      },
    });
  };

  return (
    <div>
      <input type="file" multiple onChange={handleFileSelect} />

      {Array.from(progress.entries()).map(([fileName, fileProgress]) => (
        <div key={fileName}>
          {fileName}: {fileProgress.status} - {fileProgress.progress}%
          {fileProgress.error && <span>Error: {fileProgress.error}</span>}
        </div>
      ))}
    </div>
  );
}
```

## 4. 跟踪上传进度

`onProgress` 回调会在文件通过各个阶段时多次触发：

| 状态         | 触发时间                                       | 进度值       |
| -------------- | ---------------------------------------------- | -------------------- |
| `"pending"`    | 文件排队等待上传                         | `0`                  |
| `"uploading"`  | 上传进行中 (XHR)                       | `0-100` (百分比) |
| `"processing"` | 创建 ContentVersion (如果提供了 recordId) | `0`                  |
| `"success"`    | 上传完成                                | `100`                |
| `"error"`      | 上传失败                                  | `0`                  |

**始终提供视觉反馈：**

- 显示文件名
- 显示当前状态
- 为“uploading”状态渲染进度条
- 如果状态为“error”，则显示错误消息

## 5. 取消上传（可选）

使用 `AbortController` 允许用户取消上传：

```tsx
const abortController = new AbortController();

const handleUpload = async (files: File[]) => {
  try {
    await upload({
      files,
      signal: abortController.signal,
      onProgress: (progress) => console.log(progress),
    });
  } catch (error) {
    console.error("Upload cancelled or failed:", error);
  }
};

const cancelUpload = () => {
  abortController.abort();
};
```

## 6. 链接到当前用户（特殊情况）

如果用户希望将文件上传到他们自己的个人资料或个人库：

```tsx
import {
  upload,
  getCurrentUserId,
} from "@salesforce/ui-bundle-template-feature-react-file-upload";

const userId = await getCurrentUserId();
await upload({ files, recordId: userId });
```

## API 参考

### upload(options)

处理完整流程并带进度跟踪的主上传 API。

```typescript
interface UploadOptions {
  files: File[];
  recordId?: string | null; // 如果提供，则创建 ContentVersion
  onProgress?: (progress: FileUploadProgress) => void;
  signal?: AbortSignal; // 可选取消
}

interface FileUploadProgress {
  fileName: string;
  status: "pending" | "uploading" | "processing" | "success" | "error";
  progress: number; // 0-100 用于 uploading，其他状态为 0
  error?: string;
}

interface FileUploadResult {
  fileName: string;
  size: number;
  contentBodyId: string; // 始终可用
  contentVersionId?: string; // 仅当提供了 recordId 时可用
}
```

**返回：** `Promise<FileUploadResult[]>`

### createContentVersion(file, contentBodyId, recordId)

手动从先前上传的文件创建 ContentVersion 记录。

```typescript
async function createContentVersion(
  file: File,
  contentBodyId: string,
  recordId: string,
): Promise<string | undefined>;
```

**参数：**

- `file` — 文件对象（用于元数据，如名称）
- `contentBodyId` — 上传前的内容 Body ID
- `recordId` — 用于 FirstPublishLocationId 的记录 ID

**返回：** 成功时返回 ContentVersion ID

### getCurrentUserId()

获取当前用户的 Salesforce ID。

```typescript
async function getCurrentUserId(): Promise<string>;
```

**返回：** 当前用户 ID

## 常见 UI 模式

### 带按钮的文件输入

```tsx
<input type="file" multiple accept=".pdf,.doc,.docx,.jpg,.png" onChange={handleFileSelect} />
```

### 拖放区域

使用原生事件构建自己的拖放区域：

```tsx
function DropZone({ onDrop }: { onDrop: (files: File[]) => void }) {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    onDrop(files);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      style={{ border: "2px dashed #ccc", padding: "2rem" }}
    >
      Drop files here
    </div>
  );
}
```

### 进度条

```tsx
{
  progress.status === "uploading" && (
    <div style={{ width: "100%", background: "#eee" }}>
      <div
        style={{
          width: `${progress.progress}%`,
          background: "#0176d3",
          height: "8px",
        }}
      />
    </div>
  );
}
```

## 代理决策树

**用户要求文件上传功能：**

1. **询问记录上下文：**
   - “您希望将上传的文件链接到特定记录，还是先上传文件然后链接？”

2. **根据响应：**
   - **链接到现有记录** → 使用 Pattern B 并提供 `recordId`
   - **先上传后链接** → 使用 Pattern A（无 recordId），然后使用 Pattern C 进行链接
   - **链接到当前用户** → 使用 Pattern B 并调用 `getCurrentUserId()`

3. **构建 UI：**
   - 创建文件输入或拖放区域（包不提供）
   - 为每个文件添加进度显示（状态 + 进度条）
   - 在 UI 中处理错误

4. **测试实现：**
   - 验证进度回调是否正确触发
   - 检查是否返回 `contentBodyId`
   - 如果提供了 `recordId`，验证是否返回 `contentVersionId`

## 参考实现

该包在 `src/features/fileupload/` 中包含参考实现，包括：

- `FileUpload.tsx` — 带拖放区域和对话框的完整组件
- `FileUploadDialog.tsx` — 进度跟踪对话框
- `FileUploadDropZone.tsx` — 拖放区域
- `useFileUpload.ts` — 用于状态管理的 React 钩子

**这些组件不会被导出**，但可以作为示例查看。阅读源文件以了解构建自己的 UI 的模式。

## 故障排除

**上传失败并显示 CORS 错误：**

- 确保UI包已正确部署到 Salesforce 或在 `localhost` 上运行
- 检查组织是否在 CORS 设置中允许该源

**没有进度更新：**

- 验证是否提供了 `onProgress` 回调
- 检查回调函数是否正确更新 React 状态

**未创建 ContentVersion：**

- 验证是否向 `upload()` 函数提供了 `recordId`
- 检查记录 ID 是否有效且存在于组织中
- 确保用户具有创建 ContentVersion 记录的权限

**文件上传但未出现在记录中：**

- 验证 `recordId` 是否正确
- 检查是否创建了 ContentVersion（在结果中查找 `contentVersionId`）
- 确认用户有权查看记录上的文件

## 不要做这些事情

- 从头开始构建 XHR/fetch 上传逻辑 — 使用 `upload()` API
- 尝试导入 `<FileUpload />` 组件 — 它没有被导出
- 尝试导入 `useFileUpload` 钩子 — 它没有被导出
- 使用第三方文件上传库（当此功能存在时）
- 忽略进度跟踪 — 始终提供用户反馈
- 忽略错误 — 始终处理并显示错误消息
