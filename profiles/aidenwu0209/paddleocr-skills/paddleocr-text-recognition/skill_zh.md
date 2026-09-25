# PaddleOCR 文本识别技能

## 何时使用此技能

**触发关键词（路由）**：中英双语触发词（中文和英文）在 YAML `description` 部分列出——使用该字段进行发现和路由。

**使用此技能用于**：

- 从图像（截图、照片、扫描件）中提取文本
- 从 PDF 或文档图像中提取文本，当目标是 **行/框级文本** 而不是恢复表格网格、公式或完整阅读顺序布局时
- 从指向图像/PDF 的 URL 或本地文件中提取文本

**不要使用**：

- 纯文本文件、代码文件或可直接作为文本读取的 markdown 文档
- 包含表格、公式、图表或复杂布局的文档——使用文档解析
- 不涉及图像到文本转换的任务

## 安装

脚本声明其依赖项（[PEP 723](https://peps.python.org/pep-0723/)）。无需单独的安装步骤——[uv](https://docs.astral.sh/uv/) 自动解析依赖项：

```bash
uv run scripts/ocr_caller.py --help
```

## 如何使用此技能

> **工作目录**：所有 `uv run scripts/...` 命令应从此技能的根目录（包含此 SKILL.md 文件的目录）运行。

### 基本工作流程

1. **识别输入源**：
   - 用户提供 URL：使用 `--file-url` 参数
   - 用户提供本地文件路径：使用 `--file-path` 参数

2. **执行 OCR**：

   ```bash
   uv run scripts/ocr_caller.py --file-url "用户提供的 URL" --pretty
   ```

   或对于本地文件：

   ```bash
   uv run scripts/ocr_caller.py --file-path "文件路径" --pretty
   ```

   > **性能说明**：解析时间随文档复杂度增加。单页图像通常在 1-3 秒内完成；大型 PDF（50+ 页）可能需要几分钟。在假设超时之前，请预留充足时间。

   **默认行为：将原始 JSON 保存到临时文件**：
   - 如果省略 `--output`，脚本会自动保存到系统临时目录下
   - 默认路径模式：`<系统临时目录>/paddleocr/text-recognition/results/result_<时间戳>_<ID>.json`
   - 如果提供 `--output`，它会覆盖默认临时文件目的地
   - 如果提供 `--stdout`，JSON 将打印到 stdout 且不保存文件
   - 在保存模式下，脚本会在 stderr 上打印绝对保存路径：`Result saved to: /绝对路径/...`
   - 在默认/自定义保存模式下，在响应之前读取并解析保存的 JSON 文件
   - 仅在明确希望跳过文件持久化时使用 `--stdout`

3. **解析 JSON 响应**：
   - 在默认/自定义保存模式下，从脚本显示的保存文件路径加载 JSON
   - 检查 `ok` 字段：`true` 表示成功，`false` 表示错误
   - 提取文本：`text` 字段包含所有识别的文本
   - 如果使用 `--stdout`，直接解析 stdout 中的 JSON
   - 处理错误：如果 `ok` 为 false，显示 `error.message`

4. **向用户展示结果**：
   - 以可读格式显示提取的文本
   - 如果文本为空，图像可能不包含文本
   - 在保存模式下，始终告知用户保存的文件路径，并说明完整的原始 JSON 可在该路径下获取

### 提取后要做什么

获得识别文本后，常见的下一步操作：

- **保存到文件**：将 `text` 字段写入 `.txt` 或 `.md` 文件
- **搜索内容**：在保存的输出文件中搜索关键词
- **传递给另一个流程**：`text` 字段是干净的纯文本，准备好进行下游处理
- **结果不佳**：在重试之前，请参阅下方的“获取更好结果的技巧”

### 完整输出显示

始终向用户展示**完整的识别文本**。用户通常需要完整内容进行下游使用——截断会无声地丢失他们可能未注意到缺失的数据。

- 无论多长，都显示整个 `text` 字段
- 不要使用“这里是一份摘要”或“文本以...开头”等短语
- 除非文本确实超过合理显示限制（>10,000 字符），否则不要截断，使用“...”

**示例 - 正确**：

```
用户："从这张图像中提取文本"
代理："我已经从图像中提取了文本。以下是完整内容：

[在此处显示整个文本]
```

**示例 - 错误**：

```
用户："从这张图像中提取文本"
代理："我在图像中找到了一些文本。这里是预览：
"The quick brown fox..." (截断)
```

### 理解输出

脚本返回一个包含 `ok`、`text`、`result` 和 `error` 字段的 JSON 封装。使用 `text` 用于识别的内容；`result` 包含用于调试的原始 API 响应。

有关完整模式和字段级详细信息，请参阅 `references/output_schema.md`。

> 原始结果位置（默认）：脚本在 stderr 上打印的临时文件路径

### 替代方案：paddleocr CLI

此镜像将捆绑的 `scripts/ocr_caller.py` 作为默认路径。上游 PaddleOCR 项目（自 [PR #18090](https://github.com/PaddlePaddle/PaddleOCR/pull/18090)，2026-06-03）也提供了一个官方 CLI，直接调用相同的 API。如果安装了 `paddleocr` 包，您可以使用它作为即插即用的替代方案——无需 `uv run` 或本地脚本。

**安装**（一次性）：

```bash
pip install "paddleocr>=3.7.0"
```

**环境**：CLI 仅需要 `PADDLEOCR_ACCESS_TOKEN`。它内部解析 API 端点，因此使用 CLI 时 `PADDLEOCR_OCR_API_URL` **不是**必需的（脚本仍然需要 URL）。

**基本 OCR**：

```bash
# 从 URL
paddleocr api --model_type ocr --file_url "https://example.com/image.png"

# 从本地文件
paddleocr api --model_type ocr --file_path "./document.pdf"
```

**常见选项**：

```bash
# 特定模型
paddleocr api --model_type ocr --model PP-OCRv5 --file_path "./report.pdf"

# 禁用预处理（更快，适用于扁平/良好定向的图像）
paddleocr api --model_type ocr --file_path "./document.pdf" \
  --use_doc_unwarping False --use_doc_orientation_classify False

# 页面范围
paddleocr api --model_type ocr --file_path "./large.pdf" --page_ranges "1-5,10,15-20"

# 保存结果到文件
paddleocr api --model_type ocr --file_url "https://..." --output result.json
```

**CLI 输出格式**——**与脚本封装不同**：

```json
{
  "jobId": "job-xxx",
  "pages": [
    {
      "prunedResult": {
        "rec_texts": ["Line 1", "Line 2"],
        "rec_scores": [0.98, 0.95]
      },
      "ocrImageUrl": "https://..."
    }
  ]
}
```

CLI 将 `{jobId, pages:[...]}` 打印到 stdout。它**不**将响应封装在脚本的 `{ok, text, result, error}` 封装中，**不**自动保存到临时文件，并且**不**为您连接 `text`。如果您切换路径，请相应更新您的解析逻辑。

**脚本与 CLI**——一览：

| | 脚本（默认） | `paddleocr` CLI（替代） |
| --- | --- | --- |
| 安装 | `uv` 自动解析 PEP 723 内联依赖项 | `pip install "paddleocr>=3.7.0"` |
| 必需环境 | `PADDLEOCR_OCR_API_URL` + `PADDLEOCR_ACCESS_TOKEN` | `PADDLEOCR_ACCESS_TOKEN` 仅 |
| 入口 | `uv run scripts/ocr_caller.py ...` | `paddleocr api --model_type ocr ...` |
| 输出 | `{ok, text, result, error}` 封装，自动保存到临时文件 | stdout（或 `--output`） |
| 结果位置 | 脚本在 stderr 上打印的路径（或 `--output`/`--stdout`） | stdout（或 `--output`） |
| 最佳用于 | 技能运行时，离线友好，无需额外安装 | 已安装 `paddleocr`，希望使用上游规范流程 |

运行 `paddleocr api --help` 获取完整选项列表。

### 使用示例

**示例 1：URL OCR**

```bash
uv run scripts/ocr_caller.py --file-url "https://example.com/invoice.jpg" --pretty
```

**示例 2：本地文件 OCR**

```bash
uv run scripts/ocr_caller.py --file-path "./document.pdf" --pretty
```

**示例 3：带显式文件类型的 OCR**

```bash
uv run scripts/ocr_caller.py --file-url "https://example.com/input" --file-type 1 --pretty
```

- `--file-type 0`：PDF
- `--file-type 1`：图像
- 如果省略，则根据文件扩展名自动检测类型。对于本地文件，需要识别的扩展名（`.pdf`、`.png`、`.jpg`、`.jpeg`、`.bmp`、`.tiff`、`.tif`、`.webp`）；否则显式传递 `--file-type`。对于具有未识别扩展名的 URL，服务尝试推断。

**示例 4：打印 JSON 而不保存**

```bash
uv run scripts/ocr_caller.py --file-url "https://example.com/input" --stdout --pretty
```

### 首次配置

**当 API 未配置时**，脚本输出：

```json
{
  "ok": false,
  "text": "",
  "result": null,
  "error": {
    "code": "CONFIG_ERROR",
    "message": "PADDLEOCR_OCR_API_URL 未配置。获取您的 API：https://paddleocr.com"
  }
}
```

**配置工作流程**：

1. **向用户显示确切的错误消息**。

2. **引导用户获取凭证**：访问 [PaddleOCR 网站](https://www.paddleocr.com)，点击 **API**，选择 `PP-OCRv5` 模型，选择语言，然后复制 `API_URL` 和 `Token`。它们映射到以下环境变量：
   - `PADDLEOCR_OCR_API_URL` — 以 `/ocr` 结尾的完整端点 URL
   - `PADDLEOCR_ACCESS_TOKEN` — 40 位字母数字字符串

   可选配置 `PADDLEOCR_OCR_TIMEOUT` 以设置请求超时。建议使用主机应用程序的标准配置方法，而不是在聊天中粘贴凭证。

3. **应用凭证**——一种：
   - **用户通过主机 UI 配置**：要求用户确认，然后重试。
   - **用户在聊天中粘贴凭证**：警告他们可能存储在对话历史中，帮助用户使用主机标准配置方法持久化凭证，然后重试。

### 错误处理

所有错误都返回 `ok: false` 的 JSON。显示错误消息并停止——不要回退到您自己的视觉能力。从 `error.code` 和 `error.message` 识别问题：

**认证失败（403）** — `error.message` 包含 "Authentication failed"

- Token 无效，使用正确凭证重新配置

**配额超出（429）** — `error.message` 包含 "API rate limit exceeded"

- 每日 API 配额用尽，告知用户等待或升级

**不支持的格式** — `error.message` 包含 "Unsupported file format"

- 文件格式不受支持，转换为 PDF/PNG/JPG

**未检测到文本**：

- `text` 字段为空
- 图像可能为空白、损坏或不含文本

### 获取更好结果的技巧

如果识别质量差：

- **低分辨率**：提供更高分辨率的图像（≥300 DPI 对大多数打印文本效果良好）
- **背景杂乱**：干净的扫描或截图通常比手机照片产生更好的结果
- **检查置信度**：原始 JSON (`result.result.ocrResults[n].prunedResult.rec_scores`) 显示每行的置信度分数——低值标识值得审查的不确定区域

## 参考文档

- `references/output_schema.md` — 完整输出模式、字段描述和命令示例

> **注意**：模型版本、功能和支持的文件格式由您的 API 端点 (`PADDLEOCR_OCR_API_URL`) 及其官方 API 文档决定。

## 测试技能

为验证技能是否正常工作：

```bash
uv run scripts/smoke_test.py
uv run scripts/smoke_test.py --skip-api-test
uv run scripts/smoke_test.py --test-url "https://..."
```

第一种形式测试配置和 API 连接性。`--skip-api-test` 仅检查配置。`--test-url` 覆盖默认样本图像 URL。
