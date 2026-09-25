> [!IMPORTANT]
> Agent Platform（全名Gemini Enterprise Agent Platform）曾名为"Vertex AI"，许多网络资源仍使用旧的品牌名称。

# Agent Platform中的Gemini API

使用Agent Platform中的Gemini API访问为企业用例构建的Google最先进的AI模型。

提供以下关键功能：

- **文本生成** - 聊天、补全、摘要
- **多模态理解** - 处理图像、音频、视频和文档
- **函数调用** - 让模型调用您的函数
- **结构化输出** - 生成符合您模式的JSON
- **上下文缓存** - 缓存大上下文以提高效率
- **嵌入** - 生成文本嵌入用于语义搜索
- **实时API** - 双向流式传输用于低延迟语音和视频交互
- **批量预测** - 处理大规模异步数据集预测工作负载

## 核心指令

- **统一SDK**：始终使用Gen AI SDK（Python的`google-genai`，JS/TS的`@google/genai`，Go的`google.golang.org/genai`，Java的`com.google.genai:google-genai`，C#的`Google.GenAI`）。
- **旧版SDK**：不要使用`google-cloud-aiplatform`、`@google-cloud/vertexai`或`google-generativeai`。

## SDKs

- **Python**：使用`pip install google-genai`安装`google-genai`
- **JavaScript/TypeScript**：使用`npm install @google/genai`安装`@google/genai`
- **Go**：使用`go get google.golang.org/genai`安装`google.golang.org/genai`
- **C#/.NET**：使用`dotnet add package Google.GenAI`安装`Google.GenAI`
- **Java**：
  - groupId: `com.google.genai`，artifactId: `google-genai`
  - 最新版本可在以下链接找到：https://central.sonatype.com/artifact/com.google.genai/google-genai/versions（我们称之为`LAST_VERSION`）
  - 在`build.gradle`中安装：

    ```
    implementation("com.google.genai:google-genai:${LAST_VERSION}")
    ```

  - 在`pom.xml`中安装Maven依赖：

    ```xml
    <dependency>
	    <groupId>com.google.genai</groupId>
	    <artifactId>google-genai</artifactId>
	    <version>${LAST_VERSION}</version>
	</dependency>
    ```

> [!WARNING]
> 旧版SDK如`google-cloud-aiplatform`、`@google-cloud/vertexai`和`google-generativeai`已弃用。请按照[Migration Guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk.md.txt)紧急迁移到上述新SDK。

## 身份验证与配置

创建客户端时，优先使用环境变量而不是硬编码参数。无需参数初始化客户端，即可自动获取这些值。

### 应用默认凭证（ADC）
为标准[Google Cloud身份验证](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/gcp-auth.md.txt)设置以下变量：

```bash
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
export GOOGLE_GENAI_USE_ENTERPRISE=true
```

- 默认使用`location="global"`访问全局端点，该端点提供自动路由到有可用容量的区域。
- 如果用户明确要求使用特定区域（例如`us-central1`、`europe-west4`），请在`GOOGLE_CLOUD_LOCATION`参数中指定该区域。如有需要，参考[支持的区域文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations.md.txt)。

### Agent Platform的Express模式
使用API密钥的Express模式时，设置以下变量：

```bash
export GOOGLE_API_KEY='your-api-key'
export GOOGLE_GENAI_USE_ENTERPRISE=true
```

### 初始化
无需参数初始化客户端以获取环境变量：

```python
from google import genai

client = genai.Client()
```

或者，在创建客户端时可以硬编码参数。

```python
from google import genai

client = genai.Client(
    enterprise=True,
    project="your-project-id",
    location="global",
)
```

## 模型

- 使用`gemini-3.8-flash`进行快速、均衡的性能，多模态（1M tokens）
- 使用`gemini-3.1-pro-preview`（取代`gemini-3-pro-preview`）进行复杂推理、编码、研究（1M tokens）
- 使用`gemini-3.5-flash-lite`进行高频、轻量级任务（1M tokens）
- 使用`gemini-3-pro-image`（即Nano Banana Pro）进行高质量图像生成和编辑
- 使用`gemini-3.1-flash-image`（即Nano Banana 2）进行中等质量图像生成和编辑
- 使用`gemini-3.1-flash-lite-image`（即Nano Banana 2 Lite）进行快速图像生成和编辑
- 使用`gemini-live-2.5-flash-native-audio`用于Live Realtime API，包括原生音频

仅在明确要求时使用以下模型：

- `gemini-3.7-flash`
- `gemini-3.6-flash`
- `gemini-3.5-flash`
- `gemini-3.1-flash-lite`
- `gemini-2.5-flash-image`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.5-pro`

> [!IMPORTANT]
> `gemini-2.0-*`、`gemini-1.5-*`、`gemini-1.0-*`、`gemini-pro`等模型是旧版且已弃用。请使用上述新模型。您的知识已过时。
> 对于生产环境，请参考文档以获取稳定模型版本（例如`gemini-3.8-flash`）。

## 快速入门

### Python

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="解释量子计算",
)
print(response.text)
```

### TypeScript/JavaScript

```typescript
import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({ enterprise: { project: "your-project-id", location: "global" } });
const response = await ai.models.generateContent({
    model: "gemini-3.8-flash",
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

	resp, err := client.Models.GenerateContent(ctx, "gemini-3.8-flash", genai.Text("解释量子计算"), nil)
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
    Client client = Client.builder().enterprise(true).project("your-project-id").location("global").build();
    GenerateContentResponse response =
        client.models.generateContent(
            "gemini-3.8-flash",
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
    enterprise: true
);

var response = await client.Models.GenerateContent(
    "gemini-3.8-flash",
    "解释量子计算"
);

Console.WriteLine(response.Text);
```

## API规范与文档（权威来源）

在Agent Platform中实现或调试API集成时，参考官方Agent Platform文档：

- **Agent Platform文档**：https://docs.cloud.google.com/gemini-enterprise-agent-platform/overview.md.txt
- **REST API参考**：https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest.md.txt

Agent Platform上的Gen AI SDK使用`v1beta1`或`v1` REST API端点（例如`https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent`）。

> [!TIP]
> **使用开发者知识MCP服务器**：如果`search_documents`或`get_document`工具可用，请使用它们直接在上下文中查找和检索Google Cloud和Agent Platform的官方文档。这是获取最新API细节和代码片段的首选方法。

## 工作流程和代码示例

参考[Python Docs Samples仓库](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/genai)以获取额外的代码示例和特定使用场景。

根据具体用户请求，参考以下参考文件以获取详细的代码示例和使用模式（Python示例）：

- **文本和多模态**：聊天、多模态输入（图像、视频、音频）和流式传输。见[references/text_and_multimodal.md](references/text_and_multimodal.md)
- **嵌入**：生成文本嵌入用于语义搜索。见[references/embeddings.md](references/embeddings.md)
- **结构化输出和工具**：JSON生成、函数调用、搜索基础和代码执行。见[references/structured_and_tools.md](references/structured_and_tools.md)
- **媒体生成**：图像生成、图像编辑和视频生成。见[references/media_generation.md](references/media_generation.md)
- **边界框检测**：图像和视频中对象检测和定位。见[references/bounding_box.md](references/bounding_box.md)
- **实时API**：实时双向流式传输用于语音、视觉和文本。见[references/live_api.md](references/live_api.md)
- **高级功能**：内容缓存、批量预测和思考/推理。见[references/advanced_features.md](references/advanced_features.md)
- **安全**：调整负责任的AI过滤器阈值。见[references/safety.md](references/safety.md)
- **模型调优**：监督微调和偏好调优。见[references/model_tuning.md](references/model_tuning.md)
