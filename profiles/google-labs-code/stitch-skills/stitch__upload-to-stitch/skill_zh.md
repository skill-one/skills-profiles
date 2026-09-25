# 上传至Stitch

使用提供的上传脚本将本地资源（图像、模型图、HTML和markdown文件）上传到Stitch项目，该脚本绕过了MCP工具的base64输出令牌限制。

> [!NOTE]
> AI模型不能直接通过MCP工具上传文件，因为即使是小文件的base64编码也超过了模型的输出令牌限制（约16K令牌）。此脚本读取文件并直接通过HTTP发送。

## 步骤

### 1. 确定目标项目

使用`list_projects`找到正确的`projectId`。

### 2. 获取API密钥

定位您的活跃MCP服务器配置文件并提取API密钥：
- **Antigravity**：`.gemini/antigravity/mcp_config.json` 或 `.gemini/jetski/mcp_config.json`
- **Gemini CLI**：`~/.gemini/settings.json` 或 `~/.gemini/extensions/Stitch/gemini-extension.json`
- **Claude Code**：`~/.claude.json`

提取：
- **API密钥**：从`X-Goog-Api-Key`头部或认证参数
- **MCP URL**（可选）：从`httpUrl`或端点参数（默认为`https://stitch.googleapis.com`）

> [!IMPORTANT]
> 如果您无法在任何这些位置找到API密钥，或者无法访问这些文件，您必须要求用户提供Stitch API密钥。没有有效的API密钥，请勿继续操作。

### 3. 运行上传脚本

> [!WARNING]
> **检查点 — 需要用户确认。**
> 在运行上传脚本之前，您**必须**暂停并展示要上传的文件（路径、大小和类型）给用户，并等待明确的批准。在用户确认之前**不要**执行上传脚本。

使用`run_command`执行Python脚本：

```bash
python3 <SKILL_DIR>/scripts/upload_to_stitch.py \
  --project-id <PROJECT_ID> \
  --file-path <PATH_TO_FILE> \
  --api-key <API_KEY> \
  [--api-url <STITCH_API_URL>] \
  [--title <SCREEN_TITLE>] \
  [--generated-by <GENERATED_BY>]
```

> [!TIP]
> **macOS / SSL证书故障排除：**
> 如果上传失败并显示`ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`，这意味着您的Python安装没有配置根证书颁发机构。
>
> 脚本会自动尝试使用`certifi`包加载CA证书包，如果您的python环境中安装了`certifi`。如果未安装`certifi`，您可以安装它（`pip install certifi`）或在上传脚本时手动提供`SSL_CERT_FILE`环境变量：
> ```bash
> SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())") python3 <SKILL_DIR>/scripts/upload_to_stitch.py \
>   --project-id <PROJECT_ID> \
>   --file-path <PATH_TO_FILE> \
>   --api-key <API_KEY> \
>   [--api-url <STITCH_API_URL>] \
>   [--title <SCREEN_TITLE>] \
>   [--generated-by <GENERATED_BY>]
> ```

### 支持的文件类型

| 扩展名 | MIME类型 |
|:---|:---|
| `.png` | `image/png` |
| `.jpg`, `.jpeg` | `image/jpeg` |
| `.webp` | `image/webp` |
| `.html`, `.htm` | `text/html` |
| `.md` | `text/markdown` |

脚本自动根据文件扩展名检测MIME类型。

### 脚本选项

- `--project-id`：**必需**。Stitch项目ID。
- `--file-path`：**必需**。要上传的本地文件路径。
- `--api-key`：**必需**。用于Stitch授权的API密钥。
- `--api-url`：可选。Stitch API的基础URL。默认为`https://stitch.googleapis.com`。
- `--title`：可选。上传屏幕的标题。当从Web应用中上传提取的HTML时，将此设置为页面的**路由路径**（例如，`'/dashboard'`，`'/settings/profile'`，`'/inbox'`），以便Stitch中的屏幕名称/标题能明确标识路由。
- `--generated-by`：可选。指定上传文件是如何生成的（例如，'stitch::extract-static-html'技能，'Claude Code'，'Codex'，'Gemini'等）。
