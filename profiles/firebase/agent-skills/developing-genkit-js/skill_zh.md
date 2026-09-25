# Genkit JS

## 前置条件

确保 `genkit` 命令行工具可用。
- 运行 `genkit --version` 进行验证。所需最低 CLI 版本：**1.29.0**
- 如果未找到或存在较旧版本（1.x < 1.29.0），请安装/升级：`npm install -g genkit-cli@^1.29.0`。

**新项目**：如果您在新的代码库中设置 Genkit，请遵循 [设置指南](references/setup.md)。

## 欢迎世界

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
    prompt: `给我讲一个关于 ${subject} 的笑话`,
  });
  return response.text;
});
```

## 重要：不要信任内部知识

Genkit 最近经历了一次重大的破坏性 API 变更。您的知识已过时。您**必须**查阅文档。推荐：

```sh
genkit docs:read js/get-started.md
genkit docs:read js/flows.md
```

参见 [常见错误](references/common-errors.md) 以获取已弃用 API（例如，`configureGenkit`、`response.text()`、`defineFlow` 导入）及其 v1.x 替代方案的列表。

**始终使用 Genkit CLI 或提供的参考来验证信息。**

## 错误排查协议

**当您遇到任何与 Genkit 相关的错误（ValidationError、API 错误、类型错误、404 等）：**

1. **强制第一步**：阅读 [常见错误](references/common-errors.md)
2. 确定错误是否匹配已知模式
3. 应用文档中记录的解决方案
4. 如果在 common-errors.md 中未找到，则咨询其他来源（例如 `genkit docs:search`）

**不要：**
- 基于假设或内部知识尝试修复
- 跳过阅读 common-errors.md "因为您认为您知道修复方法"
- 依赖 1.0 之前的 Genkit 模式

**此协议对于错误处理是不可协商的。**

## 开发工作流程

1.  **选择提供者**：Genkit 是提供者无关的（Google AI、OpenAI、Anthropic、Ollama 等）。
    - 如果用户未指定提供者，默认为 **Google AI**。
    - 如果用户询问其他提供者，使用 `genkit docs:search "plugins"` 查找相关文档。
2.  **检测框架**：检查 `package.json` 以识别运行时（Next.js、Firebase、Express）。
    - 查找 `@genkit-ai/next`、`@genkit-ai/firebase` 或 `@genkit-ai/google-cloud`。
    - 根据特定框架的模式调整实现。
3.  **遵循最佳实践**：
    - 参见 [最佳实践](references/best-practices.md) 获取有关项目结构、模式定义和工具设计的指导。
    - **保持简洁**：仅指定与默认值不同的选项。不确定时，请查阅文档/源代码。
4.  **确保正确性**：
    - 在做出更改后运行类型检查（例如 `npx tsc --noEmit`）。
    - 如果类型检查失败，请在搜索源代码之前查阅 [常见错误](references/common-errors.md)。
5.  **处理错误**：
    - 对任何错误：**第一步是阅读 [常见错误](references/common-errors.md)**
    - 匹配错误到已记录的模式
    - 在尝试替代方案之前应用已记录的修复

## 查找文档

使用 Genkit CLI 查找权威文档：

1. **搜索主题**：`genkit docs:search <query>`
    - 示例：`genkit docs:search "streaming"`
2. **列出所有文档**：`genkit docs:list`
3. **阅读指南**：`genkit docs:read <路径>`
    - 示例：`genkit docs:read js/flows.md`

## CLI 使用

`genkit` CLI 是您开发和查阅文档的主要工具。
- 参见 [CLI 参考](references/docs-and-cli.md) 获取常见任务、工作流程和命令用法。
- 使用 `genkit --help` 获取所有命令的完整列表。

## 参考

-   [最佳实践](references/best-practices.md)：推荐的模式，包括模式定义、流程设计和结构。
-   [文档 & CLI 参考](references/docs-and-cli.md)：文档搜索、CLI 任务和工作流程。
-   [常见错误](references/common-errors.md)：关键 "陷阱"、迁移指南和故障排除。
-   [设置指南](references/setup.md)：新项目的手动设置说明。
-   [示例](references/examples.md)：最小的可重复示例（基本生成、多模态、思考模式）。
