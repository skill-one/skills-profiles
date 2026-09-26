# Vertex AI 中的 Gemini API

使用 Vertex AI 中的 Gemini API 访问 Google 最先进的 AI 模型，这些模型是为企业用例构建的。

提供以下关键功能：

- **文本生成** - 聊天、补全、摘要
- **多模态理解** - 处理图像、音频、视频和文档
- **函数调用** - 让模型调用您的函数
- **结构化输出** - 生成符合您模式的 JSON
- **上下文缓存** - 缓存大型上下文以提高效率
- **嵌入** - 生成文本嵌入用于语义搜索
- **实时实时 API** - 双向流式传输用于低延迟语音和视频交互
- **批量预测** - 处理大规模异步数据集预测工作负载

## 核心指令

- **统一 SDK**：始终使用 Gen AI SDK（Python 的 `google-genai`，JS/TS 的 `@google/genai`，Go 的 `google.golang.org/genai`，Java 的 `com.google.genai:google-genai`，C# 的 `Google.GenAI`）。
- **旧版 SDK**：不要使用 `google-cloud-aiplatform`、`@google-cloud/vertexai` 或 `google-generativeai`。

## SDK

- **Python**：使用 `pip install google-genai` 安装 `google-genai`
- **JavaScript/TypeScript**：使用 `npm install @google/genai` 安装 `@google/genai`
- **Go**：使用 `go get google.golang.org/genai` 安装 `google.golang.org/genai`
- **C#/.NET**：使用 `dotnet add package Google.GenAI` 安装 `Google.GenAI`
- **Java**：
  - groupId: `com.google.genai`，artifactId: `google-genai`
  - 最新版本可以在以下位置找到：https://central.sonatype.com/artifact/com.google.genai/google-genai/versions（我们称之为 `LAST_VERSION`） 
  - 在 `build.gradle` 中安装：

    ```
    implementation("com.google.genai:google-genai:${LAST_VERSION}")
    ```

  - 在 `pom.xml` 中安装 Maven 依赖项：

    ```xml
    <dependency>
	    <groupId>com.google.genai</groupId>
	    <artifactId>google-genai</artifactId>
	    <version>${LAST_VERSION}</version>
	</dependency>
    ```

> [!WARNING]
> 旧版 SDK 如 `google-cloud-aiplatform`、`@google-cloud/vertexai` 和 `google-generativeai` 已弃用。请按照迁移指南尽快迁移到上述新 SDK。

## 身份验证和配置

在创建客户端时，优先使用环境变量而不是硬编码参数。无需参数初始化客户端即可自动获取这些值。

### 应用默认凭证 (ADC)
为标准 [Google Cloud 身份验证](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gcp-auth) 设置这些变量：
```bash
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
export GOOGLE_GENAI_USE_VERTEXAI=true
```
- 默认情况下，使用 `location="global"` 访问全局端点，该端点提供自动路由到具有可用容量的区域。
- 如果用户明确要求使用特定区域（例如 `us-central1`、`europe-west4`），请在 `GOOGLE_CLOUD_LOCATION` 参数中指定该区域。如有需要，参考 [支持的区域文档](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)。

### Vertex AI 的 Express 模式
在使用 API 密钥的 [Express 模式](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys?usertype=expressmode) 时设置这些变量：
```bash
export GOOGLE_API_KEY='your-api-key'
export GOOGLE_GENAI_USE_VERTEXAI=true
```

### 初始化
无需参数初始化客户端以获取环境变量：
```python
from google import genai
client = genai.Client()
```

或者，您可以在创建客户端时硬编码参数。

```python
from google import genai
client = genai.Client(vertexai=True, project="your-project-id", location="global")
```

## 模型

- 使用 `gemini-3.1-pro-preview` 进行复杂推理、编码、研究（1M 令牌）
- 使用 `gemini-3-flash-preview` 进行快速、平衡的性能、多模态（1M 令牌）
- 使用 `gemini-3-pro-image-preview` 进行 Nano Banana Pro 图像生成和编辑
- 使用 `gemini-live-2.5-flash-native-audio` 进行 Live Realtime API 包括原生音频

如果明确要求，请使用以下模型：

- 使用 `gemini-2.5-flash-image` 进行 Nano Banana 图像生成和编辑
- 使用 `gemini-2.5-flash`
- 使用 `gemini-2.5-flash-lite`
- 使用 `gemini-2.5-pro`

> [!IMPORTANT]
> `gemini-2.0-*`、`gemini-1.5-*`、`gemini-1.0-*`、`gemini-pro` 等模型是旧版且已弃用。请使用上述新模型。您的知识已过时。
> 对于生产环境，请参考 Vertex AI 文档以获取稳定模型版本（例如 `gemini-3-flash`）。

## 快速入门

### Python
```python
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="解释量子计算"
)
print(response.text)
```

### TypeScript/JavaScript
```typescript
import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({ vertexai: { project: "your-project-id", location: "global" } });
const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "解释量子计算"
});
console.log(response.text);
```

### Go
```go
package main

import (
	"context"
	"fmt"
	"log"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		Backend:  genai.BackendVertexAI,
		Project:  "your-project-id",
		Location: "global",
	})
	if err != nil {
		log.Fatal(err)
	}

	resp, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", genai.Text("解释量子计算"), nil)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(resp.Text)
}
```

### Java
```java
import com.google.genai.Client;
import com.google.genai.types.GenerateContentResponse;

public class GenerateTextFromTextInput {
  public static void main(String[] args) {
    Client client = Client.builder().vertexAi(true).project("your-project-id").location("global").build();
    GenerateContentResponse response =
        client.models.generateContent(
            "gemini-3-flash-preview",
            "解释量子计算",
            null);

    System.out.println(response.text());
  }
}
```

### C#/.NET
```csharp
using Google.GenAI;

var client = new Client(
    project: "your-project-id",
    location: "global",
    vertexAI: true
);

var response = await client.Models.GenerateContent(
    "gemini-3-flash-preview",
    "解释量子计算"
);

Console.WriteLine(response.Text);
```

## API 规范和文档（权威来源）

在实现或调试 Vertex AI 的 API 集成时，请参考官方 Google Cloud Vertex AI 文档：
- **Vertex AI Gemini 文档**：https://cloud.google.com/vertex-ai/generative-ai/docs/
- **REST API 参考**：https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest

Vertex AI 上的 Gen AI SDK 使用 `v1beta1` 或 `v1` REST API 端点（例如 `https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent`）。

> [!TIP]
> **使用开发者知识 MCP 服务器**：如果 `search_documents` 或 `get_document` 工具可用，请使用它们直接在上下文中查找和检索 Google Cloud 和 Vertex AI 的官方文档。这是获取最新 API 详细信息和代码片段的首选方法。

## 工作流程和代码示例

参考 [Python Docs Samples 仓库](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/genai) 获取额外的代码示例和特定使用场景。

根据具体的用户请求，参考以下参考文件以获取详细的代码示例和使用模式（Python 示例）：

- **文本和多模态**：聊天、多模态输入（图像、视频、音频）和流式传输。参见 [references/text_and_multimodal.md](references/text_and_multimodal.md)
- **嵌入**：生成文本嵌入用于语义搜索。参见 [references/embeddings.md](references/embeddings.md)
- **结构化输出和工具**：JSON 生成、函数调用、搜索基础和代码执行。参见 [references/structured_and_tools.md](references/structured_and_tools.md)
- **媒体生成**：图像生成、图像编辑和视频生成。参见 [references/media_generation.md](references/media_generation.md)
- **边界框检测**：在图像和视频中检测和定位对象。参见 [references/bounding_box.md](references/bounding_box.md)
- **实时 API**：用于语音、视觉和文本的实时双向流式传输。参见 [references/live_api.md](references/live_api.md)
- **高级功能**：内容缓存、批量预测和思考/推理。参见 [references/advanced_features.md](references/advanced_features.md)
- **安全**：调整负责任的 AI 过滤器和阈值。参见 [references/safety.md](references/safety.md)
- **模型调整**：监督微调和偏好调整。参见 [references/model_tuning.md](references/model_tuning.md)
