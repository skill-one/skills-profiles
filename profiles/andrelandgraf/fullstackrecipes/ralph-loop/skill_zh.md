# Ralph Loop

自动化代理驱动的开发完整设置。将功能定义为具有可测试验收标准的用户故事，然后在循环中运行 AI 代理，直到所有故事都通过。

## 前置条件

按顺序完成以下配方：

### 代码健康、Linting & 格式化

配置 Prettier 进行格式化，TypeScript 进行类型检查，以及 Fallow 进行代码健康检查（死代码、重复、复杂度、架构漂移）。跳过 ESLint/Biome 以避免配置复杂性。

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/code-health-setup
```

### AI 编码代理配置

配置像 Cursor、GitHub Copilot 或 Claude Code 这样的 AI 编码代理，使用项目特定的模式、编码指南和 MCP 服务器，以实现一致的 AI 辅助开发。

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/agent-setup
```

## 烹饪书 - 按顺序完成这些配方

### 用户故事设置

创建一个结构化的格式来记录功能需求作为用户故事。带有可测试验收标准的 JSON 文件，AI 代理可以验证和跟踪。

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/user-stories-setup
```

### 使用用户故事

使用用户故事记录和跟踪功能实现。编写故事、构建功能和将验收标准标记为通过的工作流程。

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/using-user-stories
```

### Ralph 代理循环

使用 Ralph 设置自动化代理驱动的开发。在循环中运行 AI 代理来实施用户故事中的功能，验证验收标准，并记录下一个代理的进度。

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/ralph-setup
```
