# Genkit JS

## 前置要求

确保 `genkit` CLI 可用。
-  运行 `genkit --version` 进行验证。所需最低 CLI 版本：**1.29.0**
-  若未找到或当前版本较旧（1.x < 1.29.0），请安装/升级：`npm install -g genkit-cli@^1.29.0`。

**新建项目**：如果您在新代码库中配置 Genkit，请遵循 [设置指南](references/setup.md)。

## 你好世界

```ts
import { z, genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

// 使用 Google AI 插件初始化 Genkit
const ai = genkit({
  plugins: [googleAI()],
});

export const myFlow = ai.defineFlow({
  name: 'myFlow',
  inputSchema: z.string().default('AI'),
  outputSchema: z.string(),
}, async (subject) => {
  const response = await ai.generate({
    model: googleAI.model('gemini-2.5-flash'),
    prompt: `Tell me a joke about ${subject}`,
  });
  return response.text;
});
```

## 关键：切勿信任内部知识

Genkit 近期经历了重大破坏性 API 变更。您的知识已过时。您 MUST 查阅文档。推荐：

```sh
genkit docs:read js/get-started.md
genkit docs:read js/flows.md
```

请参阅 [常见错误](references/common-errors.md) 中关于已弃用 API（例如 `configureGenkit`、`response.text()`、`defineFlow` 导入）及其 v1.x 替代方案的列表。

**务必使用 Genkit CLI 或提供的参考资料验证信息。**

## 错误故障排查协议

**当您遇到任何与 Genkit 相关的错误（ValidationError、API 错误、类型错误、404 错误等）时：**

1.  **强制性第一步**：阅读 [常见错误](references/common-errors.md)
2. 确认该错误是否匹配已知模式
3. 应用文档中记载的解决方案
4. 若在 common-errors.md 中未找到，则咨询其他来源（例如 `genkit docs:search`)

**切勿：**
- 基于假设或内部知识尝试修复
- 认为已知道修复方法，从而跳过阅读 common-errors.md
- 依赖 1.0 版本之前 Genkit 的模式

**此协议在错误处理方面是不可协商的。**

## 开发工作流

1.  **选择提供商**：Genkit 是提供商无关的（Google AI、OpenAI、Anthropic、Ollama 等）。
    -  若用户未指定提供商，默认使用 **Google AI**。
    -  若用户询问其他提供商，请使用 `genkit docs:search "plugins"` 查找相关文档。
2.  **检测框架**：检查 `package.json` 以识别运行时（Next.js、Firebase、Express）。
    - 查找 `@genkit-ai/next`、`@genkit-ai/firebase` 或 `@genkit-ai/google-cloud`。
    - 将实现适配到特定框架的模式。
3.  **遵循最佳实践**：
    - 参阅 [最佳实践](references/best-practices.md)，获取关于项目结构、模式定义和工具设计的指导。
    - **保持简洁**：仅指定与默认值不同的选项。不确定时，请查阅文档/源码。
4.  **确保正确性**：
    - 修改后运行类型检查（例如 `npx tsc --noEmit`)。
    - 若类型检查失败，在查找源码之前，请参阅 [常见错误](references/common-errors.md)。
5.  **处理错误**：
    - 遇到任何错误时：**第一步是阅读 [常见错误](references/common-errors.md)**
    - 将错误与文档中记载的模式进行匹配
    - 在尝试替代方案之前，应用文档中记载的修复方法

## 查找文档

使用 Genkit CLI 查找权威文档：

1.  **搜索主题**：`genkit docs:search <查询>`
    - 示例：`genkit docs:search "streaming"`
2.  **列出所有文档**：`genkit docs:list`
3.  **阅读指南**：`genkit docs:read <路径>`
    - 示例：`genkit docs:read js/flows.md`

## CLI 用法

`genkit` CLI 是您用于开发和文档的主要工具。
-  参阅 [CLI 参考](references/docs-and-cli.md)，获取常见任务、工作流程和命令使用说明。
-  使用 `genkit --help` 查看完整的命令列表。

## 参考资料

-   [最佳实践](references/best-practices.md): 模式定义、流程设计和结构的推荐模式。
-   [文档与 CLI 参考](references/docs-and-cli.md): 文档搜索、CLI 任务和工作流程。
-   [常见错误](references/common-errors.md): 关键的“注意事项”、迁移指南和故障排查。
-   [设置指南](references/setup.md): 新项目的手动设置说明。
-   [示例](references/examples.md): 最小可复现示例（基础生成、多模态、思考模式）。
