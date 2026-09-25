# 在 ASP.NET Core 最小 API 中实现文件上传

## 使用场景
- ASP.NET Core 最小 API (.NET 8+) 中的文件上传端点
- 处理 IFormFile 或 IFormFileCollection 参数
- 当您需要大小限制、内容类型验证或流式传输大文件时

## 不适用场景
- MVC 控制器 → `[FromForm] IFormFile` 可直接通过属性工作
- 简单的 JSON 正文 → 无需文件上传
- 非常大的文件 (> 1GB) → 使用 `MultipartReader` 进行流式传输

## 输入

| 输入 | 是否必需 | 描述 |
|------|----------|-------|
| 文件参数 | 是 | IFormFile 或 IFormFileCollection |
| 大小限制 | 是 | 最大文件/请求大小 |
| 允许类型 | 否 | 内容类型或扩展名限制 |

## 工作流程

### 第 1 步：关键 — 理解最小 API 中的 IFormFile 绑定

```csharp
// 在 .NET 8+ 最小 API 中，当 IFormFile 是唯一复杂参数时，
// 它会自动从 multipart/form-data 绑定。
app.MapPost("/upload", (IFormFile file) => ...);

// 关键：当您混合文件与其他表单字段时，对所有表单绑定参数使用 [FromForm]
//（或将其分组为单个 [FromForm] DTO）。
app.MapPost("/upload-with-metadata",
    ([FromForm] IFormFile file, [FromForm] string description) =>
{
    return Results.Ok(new { file.FileName, Description = description });
});

// 多个文件：IFormFileCollection 也自动从 multipart/form-data 绑定。
// 如果您混合了其他表单字段，则只需要 [FromForm]，如上所示。
app.MapPost("/upload-multiple", (IFormFileCollection files) =>
{
    return Results.Ok(files.Select(f => new { f.FileName, f.Length }));
});
```

### 第 2 步：关键 — 文件大小限制与请求大小限制是分开的

```csharp
// 关键：有两组不同的限制，您需要配置两者

// 1. 请求正文大小限制（Kestrel 级别）— 默认为 30MB
builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.MaxRequestBodySize = 10 * 1024 * 1024; // 10 MB
});

// 2. 表单选项 — 多部分正文长度限制 — 默认为 128MB
builder.Services.Configure<FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 10 * 1024 * 1024; // 10 MB
    options.ValueLengthLimit = 1024 * 1024; // 1 MB 用于表单值
    options.MultipartHeadersLengthLimit = 16384; // 16 KB 用于部分头
});

// 常见错误：仅增加 Kestrel MaxRequestBodySize
// 上传仍然失败，因为 FormOptions.MultipartBodyLengthLimit 超限

// 常见错误：仅增加 FormOptions
// 上传在到达表单解析之前就因 "Request body too large" 而失败

// 关键：使用 RequestSizeLimit 属性按端点覆盖限制
app.MapPost("/upload-large", [RequestSizeLimit(200_000_000)] (IFormFile file) =>
{
    return Results.Ok(new { file.FileName, file.Length });
});

// 关键：完全禁用限制（用于流式传输）
app.MapPost("/upload-unlimited", [DisableRequestSizeLimit] async (HttpContext context) =>
{
    // 手动处理
});
```

### 第 3 步：关键 — .NET 8+ 中自动验证表单上传的防伪造

```csharp
// 关键：在 .NET 8+ 的 UseAntiforgery() 中，所有表单绑定端点
// 自动验证防伪造令牌，包括文件上传

builder.Services.AddAntiforgery();
var app = builder.Build();
app.UseAntiforgery();

// 此端点现在需要防伪造令牌：
app.MapPost("/upload", (IFormFile file) => Results.Ok(file.FileName));
// 无令牌 → 400 Bad Request

// 关键：对于仅 API 文件上传（无需防伪造），选择退出：
app.MapPost("/api/upload", (IFormFile file) => Results.Ok(file.FileName))
    .DisableAntiforgery();  // 关键：必须显式选择退出

// 常见错误：文件上传时出现 400 错误，而未意识到 UseAntiforgery() 在管道中

// 警告：DisableAntiforgery() 对于未认证端点和使用 JWT 带宽认证的端点是安全的。
// 但是，对于使用 Cookie 认证的端点，禁用防伪造会移除 CSRF 保护，
// 并使端点暴露于跨站请求伪造攻击。
// 对于 Cookie 认证的端点，请包含有效的防伪造令牌。
```

### 第 4 步：关键 — 仅验证文件内容，而不仅仅是扩展名

```csharp
app.MapPost("/upload", async (IFormFile file) =>
{
    // 关键：检查内容类型和文件签名（魔术字节）
    // 绝不单独信任文件扩展名 — 它可以被欺骗

    // 默认仅允许 JPEG/PNG。要支持更多（例如，GIF），
    // 请在此处添加 MIME 类型，并在下方验证其魔术字节。
    var allowedTypes = new[] { "image/jpeg", "image/png" };
    if (!allowedTypes.Contains(file.ContentType, StringComparer.OrdinalIgnoreCase))
        return Results.BadRequest("不允许的文件类型");

    // 关键：检查魔术字节以验证文件类型
    using var stream = file.OpenReadStream();
    var header = new byte[8];
    var bytesRead = await stream.ReadAsync(header, 0, header.Length);
    if (bytesRead < 4)
        return Results.BadRequest("文件内容太短或无效");

    // JPEG: FF D8 FF
    // PNG: 89 50 4E 47
    var isJpeg = header[0] == 0xFF && header[1] == 0xD8 && header[2] == 0xFF;
    var isPng = header[0] == 0x89 && header[1] == 0x50 && header[2] == 0x4E && header[3] == 0x47;

    // 从魔术字节确定实际内容类型
    string? detectedContentType = isJpeg ? "image/jpeg" : isPng ? "image/png" : null;
    if (detectedContentType is null)
        return Results.BadRequest("文件内容不是支持的有效图像格式（仅允许 JPEG 和 PNG）。");

    // 确保声明的 Content-Type 与魔术字节检测到的匹配
    if (!string.Equals(file.ContentType, detectedContentType, StringComparison.OrdinalIgnoreCase))
        return Results.BadRequest("文件内容类型与声明的 ContentType 头不匹配。");

    // 关键：绝不要直接使用用户提供的文件名作为保存路径 — 它可能包含路径遍历字符（例如，"../../../etc/passwd"）。
    // 生成安全文件名；从验证的内容中派生扩展名，而不是用户输入。
    var extension = detectedContentType == "image/jpeg" ? ".jpg" : ".png";
    var safeFileName = $"{Guid.NewGuid()}{extension}";
    // 绝不：var path = Path.Combine("uploads", file.FileName);     // 路径遍历！

    var filePath = Path.Combine("uploads", safeFileName);
    Directory.CreateDirectory("uploads");
    stream.Position = 0;
    using var fileStream = File.Create(filePath);
    await stream.CopyToAsync(fileStream);

    return Results.Ok(new { FileName = safeFileName, file.Length });
});
```

### 第 5 步：关键 — 无缓冲流式传输大文件

```csharp
// 关键：IFormFile 依赖于 multipart form 解析，该解析在内存中缓冲内容（达到阈值后）
// 然后溢出到磁盘临时文件。对于非常大的上传，
// 如果您可以按块处理数据，则此开销是不必要的。
// 使用 MultipartReader 直接流式传输 — 例如，到最终存储位置 —
// 而无需先缓冲整个文件。

app.MapPost("/upload-stream",
    [DisableRequestSizeLimit]
    async (HttpContext context) =>
{
    // 从 Content-Type 头中提取 multipart 边界
    var contentType = context.Request.ContentType;
    if (contentType == null)
        return Results.BadRequest("缺少 Content-Type");

    // 安全解析 Content-Type 头以避免 MediaTypeHeaderValue.Parse 引发的 FormatException
    if (!MediaTypeHeaderValue.TryParse(contentType, out var mediaType))
        return Results.BadRequest("无效的 Content-Type");

    var boundary = HeaderUtilities.RemoveQuotes(mediaType.Boundary).Value;
    if (string.IsNullOrWhiteSpace(boundary))
        return Results.BadRequest("不是 multipart 请求");

    var reader = new MultipartReader(boundary, context.Request.Body);

    // 关键：ReadNextSectionAsync 在没有更多部分时返回 null
    while (await reader.ReadNextSectionAsync() is { } section)
    {
        // 解析 Content-Disposition 以识别文件部分
        if (!ContentDispositionHeaderValue.TryParse(section.ContentDisposition, out var contentDisposition))
            continue;

        if (contentDisposition.DispositionType.Equals("form-data")
            && !string.IsNullOrEmpty(contentDisposition.FileName.Value))
        {
            // 对用户提供的文件名进行清理以防止路径遍历
            var originalFileName = contentDisposition.FileName.Value ?? string.Empty;
            var sanitizedFileName = Path.GetFileName(originalFileName.Trim('"'));
            var safeFile = $"{Guid.NewGuid()}";

            // 关键：直接流式传输到磁盘 — 避免内存中缓冲
            Directory.CreateDirectory("uploads");
            using var fileStream = File.Create(Path.Combine("uploads", safeFile));
            await section.Body.CopyToAsync(fileStream);
        }
    }

    return Results.Ok("上传成功");
}).DisableAntiforgery();

// 常见错误：使用 IFormFile 处理非常大的文件
// 多部分表单解析可能会缓冲大型上传并消耗内存/磁盘。
// 使用 MultipartReader 直接流式传输到存储。
```

## 常见错误

1. **仅配置一个大小限制**：必须配置 Kestrel `MaxRequestBodySize` 和 `FormOptions.MultipartBodyLengthLimit`。
2. **防伪造的 400 错误**：在 .NET 8+ 中，`UseAntiforgery()` 自动验证表单上传。对于 API 端点，使用 `.DisableAntiforgery()`（适用于 JWT/未认证；对于 Cookie 认证端点，请勿禁用）。
3. **信任文件.FileName**：用户提供的文件名可能包含路径遍历。使用 `Guid.NewGuid()` 生成安全文件名，并从验证的内容类型中派生扩展名。
4. **仅信任 Content-Type**：内容类型可以被客户端欺骗。始终检查魔术字节以验证实际文件类型。
5. **使用 IFormFile 处理非常大的文件**：多部分表单解析会缓冲内容（达到内存阈值后）然后溢出到磁盘临时文件。使用 `MultipartReader` 按块流式传输数据直接到存储，而无需缓冲整个文件。
6. **从用户输入派生文件扩展名**：优先从验证的内容类型或魔术字节中派生扩展名，而不是 `Path.GetExtension(file.FileName)`。如果必须保留原始扩展名，请验证它与检测到的内容类型匹配。
