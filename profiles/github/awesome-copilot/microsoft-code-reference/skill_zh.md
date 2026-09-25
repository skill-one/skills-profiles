# Microsoft 代码参考

## 工具

| 需求 | 工具 | 示例 |
|------|------|---------|
| API 方法/类查找 | `microsoft_docs_search` | `"BlobClient UploadAsync Azure.Storage.Blobs"` |
| 可工作的代码示例 | `microsoft_code_sample_search` | `query: "upload blob managed identity", language: "python"` |
| 完整 API 参考 | `microsoft_docs_fetch` | 从 `microsoft_docs_search` 获取 URL（用于重载、完整签名） |

## 查找代码示例

使用 `microsoft_code_sample_search` 获取官方、可工作的示例：

```
microsoft_code_sample_search(query: "upload file to blob storage", language: "csharp")
microsoft_code_sample_search(query: "authenticate with managed identity", language: "python")
microsoft_code_sample_search(query: "send message service bus", language: "javascript")
```

**使用时机：**
- 编写代码前——找到可遵循的工作模式
- 出现错误后——将你的代码与已知良好的示例进行比较
- 不确定初始化/设置——示例展示完整上下文

## API 查找

```
# 验证方法是否存在（包含命名空间以实现精确匹配）
"BlobClient UploadAsync Azure.Storage.Blobs"
"GraphServiceClient Users Microsoft.Graph"

# 查找类/接口
"DefaultAzureCredential class Azure.Identity"

# 查找正确包
"Azure Blob Storage NuGet 包"
"azure-storage-blob pip 包"
```

当方法有多个重载或需要完整参数详细信息时，获取完整页面。

## 错误排查

使用 `microsoft_code_sample_search` 查找可工作的代码示例，并与你的实现进行比较。对于特定错误，使用 `microsoft_docs_search` 和 `microsoft_docs_fetch`：

| 错误类型 | 查询 |
|------------|-------|
| 方法未找到 | `"[ClassName] methods [Namespace]"` |
| 类型未找到 | `"[TypeName] NuGet package namespace"` |
| 签名错误 | `"[ClassName] [MethodName] overloads"` → 获取完整页面 |
| 已弃用警告 | `"[OldType] migration v12"` |
| 身份验证失败 | `"DefaultAzureCredential troubleshooting"` |
| 403 禁止访问 | `"[ServiceName] RBAC 权限"` |

## 需要验证的情况

始终在以下情况下验证：
- 方法名看起来“过于方便”（例如 `UploadFile` 对比实际 `Upload`）
- 混合 SDK 版本（v11 `CloudBlobClient` 对比 v12 `BlobServiceClient`）
- 包名不符合规范（.NET 使用 `Azure.*`，Python 使用 `azure-*`）
- 首次使用 API

## 验证工作流程

在使用 Microsoft SDKs 生成代码前，验证其正确性：

1. **确认方法或包是否存在** — `microsoft_docs_search(query: "[ClassName] [MethodName] [Namespace]")`
2. **获取完整详细信息**（用于重载/复杂参数）— `microsoft_docs_fetch(url: "...")`
3. **查找可工作的示例** — `microsoft_code_sample_search(query: "[任务]", language: "[语言]")`

对于简单查找，仅需步骤 1 即可。对于复杂 API 使用，完成所有三个步骤。

## CLI 替代方案

如果 Learn MCP 服务器不可用，可在终端或 shell（例如 Bash、PowerShell 或 cmd）中使用 `mslearn` CLI：

```sh
# 直接运行（无需安装）
npx @microsoft/learn-cli search "BlobClient UploadAsync Azure.Storage.Blobs"

# 或全局安装后运行
npm install -g @microsoft/learn-cli
mslearn search "BlobClient UploadAsync Azure.Storage.Blobs"
```

| MCP 工具 | CLI 命令 |
|----------|-------------|
| `microsoft_docs_search(query: "...")` | `mslearn search "..."` |
| `microsoft_code_sample_search(query: "...", language: "...")` | `mslearn code-search "..." --language ...` |
| `microsoft_docs_fetch(url: "...")` | `mslearn fetch "..."` |

向 `search` 或 `code-search` 传递 `--json` 以获取原始 JSON 输出以进行进一步处理。
