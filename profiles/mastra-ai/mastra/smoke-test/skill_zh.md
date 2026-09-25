# 烟雾测试技能

使用 `create-mastra@<tag>` 创建新的 Mastra 项目，并在 Chrome 中对 Mastra Studio 进行烟雾测试。

**此技能适用于 Claude Code 配合 Chrome MCP 服务器。** 对于使用内置浏览器工具的 MastraCode，请使用 `mastracode-smoke-test`。

## 使用方法

```
/smoke-test --directory <路径> --name <项目名称> --tag <版本> [--pm <包管理器>] [--llm <提供者>]
/smoke-test -d <路径> -n <项目名称> -t <版本> [-p <包管理器>] [-l <提供者>]
```

## 参数

| 参数     | 短选项 | 描述                                                                  | 是否必需 | 默认值  |
| -------- | ------ | --------------------------------------------------------------------- | -------- | -------- |
| `--directory` | `-d`  | 项目将创建的父目录                                                   | **是**   | -        |
| `--name`  | `-n`  | 项目名称（将创建为子目录）                                           | **是**   | -        |
| `--tag`   | `-t`  | create-mastra 的版本标签（例如，`latest`，`alpha`，`0.10.6`）          | **是**   | -        |
| `--pm`    | `-p`  | 包管理器：`npm`，`yarn`，`pnpm` 或 `bun`                             | 否      | `npm`    |
| `--llm`   | `-l`  | LLM 提供者：`openai`，`anthropic`，`groq`，`google`，`cerebras`，`mistral` | 否      | `openai` |

## 示例

```sh
# 最简（仅必需参数）
/smoke-test -d ~/projects -n my-test-app -t latest

# 完整规格
/smoke-test --directory ~/projects --name my-test-app --tag alpha --pm pnpm --llm anthropic

# 使用短选项
/smoke-test -d ./projects -n smoke-test-app -t 0.10.6 -p bun -l openai
```

## 第 0 步：参数验证（必须首先运行）

**关键**：在进行下一步之前，解析 ARGUMENTS 字符串并验证：

1. **解析参数**：从上面提供的 ARGUMENTS 字符串中解析参数
2. **检查必需参数**：
   - `--directory` 或 `-d`：必需 - 如果缺失则失败
   - `--name` 或 `-n`：必需 - 如果缺失则失败
   - `--tag` 或 `-t`：必需 - 如果缺失则失败
3. **应用默认值**：为可选参数应用默认值：
   - `--pm` 或 `-p`：如果未提供，默认为 `npm`
   - `--llm` 或 `-l`：如果未提供，默认为 `openai`
4. **验证值**：
   - `pm` 必须是以下之一：`npm`，`yarn`，`pnpm`，`bun`
   - `llm` 必须是以下之一：`openai`，`anthropic`，`groq`，`google`，`cerebras`，`mistral`
   - `directory` 必须存在（或将被创建）
   - `name` 应该是一个有效的目录名称（不能有空格或特殊字符）

**如果验证失败**：停止并显示使用帮助，包括缺失/无效的参数。

**如果传递了 `-h` 或 `--help`**：显示此使用信息并停止。

## 前置条件

此技能需要 **Chrome MCP 服务器**（Chrome 中的 Claude）进行浏览器自动化。确保其已配置并正在运行。

Chrome MCP 服务器提供 `tabs_create_mcp`，`tabs_context_mcp`，`navigate_mcp`，`click_mcp`，`type_mcp` 和 `screenshot_mcp` 等工具。

## 执行步骤

### 第 1 步：创建 Mastra 项目

使用显式参数运行 create-mastra 命令以避免交互式提示：

```sh
# 对于 npm
npx create-mastra@<tag> <project-name> --no-git --llm <llmProvider> --timeout 120000

# 对于 yarn
yarn dlx create-mastra@<tag> <project-name> --no-git --llm <llmProvider> --timeout 120000

# 对于 pnpm
pnpm create mastra@<tag> <project-name> --no-git --llm <llmProvider> --timeout 120000

# 对于 bun
bunx create-mastra@<tag> <project-name> --no-git --llm <llmProvider> --timeout 120000
```

`-c/--components` 和 `-e/--example` 已被移除且不得使用。`-l/--llm` 仍然受支持，并是上面使用的标志。默认使用管理模板，`--empty` 用于故意创建空项目，或 `--template <template>` 用于特定模板。如果拒绝标志，请检查初始化程序的帮助而不是重试旧命令：`npm create mastra@<tag> -- --help`，`npx create-mastra@<tag> --help`，`pnpm create mastra@<tag> --help`，`yarn dlx create-mastra@<tag> --help` 或 `bunx create-mastra@<tag> --help`。

等待安装完成。这可能需要 1-2 分钟，具体取决于网络速度。

### 第 2 步：验证项目结构

创建后，验证项目是否具有：

- `package.json` 包含 Mastra 依赖项
- `src/mastra/index.ts` 导出一个 Mastra 实例
- `.env` 文件（可能需要创建）

### 第 2.5 步：添加用于浏览器测试的浏览器代理

要测试浏览器功能，请添加一个支持浏览器的代理：

1. **安装浏览器包**：

```sh
<pm> add @mastra/stagehand
# 或用于确定性浏览器自动化：
<pm> add @mastra/agent-browser
```

2. **在 `src/mastra/agents/` 中创建 `browser-agent.ts`**：

```typescript
import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';
import { StagehandBrowser } from '@mastra/stagehand';

export const browserAgent = new Agent({
  id: 'browser-agent',
  name: 'Browser Agent',
  instructions: `You are a helpful assistant that can browse the web to find information.`,
  model: '<provider>/<model>', // e.g., 'openai/gpt-4o'
  memory: new Memory(),
  browser: new StagehandBrowser({
    headless: false,
  }),
});
```

3. **更新 `index.ts` 以注册浏览器代理**：

```typescript
import { browserAgent } from './agents/browser-agent';

// 在 Mastra 配置中：
agents: { weatherAgent, browserAgent },
```

### 第 3 步：配置环境变量

根据选择的 LLM 提供者，检查所需的 API 密钥：

| 提供者  | 所需环境变量  |
| ------- | ------------ |
| openai  | `OPENAI_API_KEY`               |
| anthropic | `ANTHROPIC_API_KEY`            |
| groq    | `GROQ_API_KEY`                 |
| google  | `GOOGLE_GENERATIVE_AI_API_KEY` |
| cerebras | `CEREBRAS_API_KEY`             |
| mistral | `MISTRAL_API_KEY`              |

**按此顺序检查**：

1. **首先检查全局环境**：运行 `echo $<ENV_VAR_NAME>` 查看密钥是否已全局设置
   - 如果全局设置，项目将继承它 - 无需 `.env` 文件
   - 跳到第 4 步

2. **检查项目 `.env` 文件**：如果未全局设置，检查项目中是否存在 `.env` 文件并包含密钥

3. **如果需要，仅询问用户**：如果密钥未全局设置或存在于 `.env` 中：
   - 询问用户 API 密钥
   - 使用提供的密钥创建 `.env` 文件

**仅检查与所选提供者匹配的** **一个** **密钥** - 不要检查所有提供者。

### 第 4 步：启动开发服务器

进入项目目录并启动开发服务器：

```sh
cd <directory>/<project-name>
<packageManager> run dev
```

服务器通常在 `http://localhost:4111` 上启动。在继续之前等待服务器准备就绪。

### 第 5 步：测试 Studio

使用 Chrome 浏览器自动化工具测试 Mastra Studio。

#### 5.1 初始设置

1. 使用 `tabs_context_mcp` 获取浏览器上下文
2. 使用 `tabs_create_mcp` 创建新标签页
3. 导航到 `http://localhost:4111`

#### 5.2 测试清单

使用 Chrome 自动化工具执行以下烟雾测试：

**导航和基本加载**

- [ ] Studio 成功加载（页面包含 "Mastra Studio" 或显示代理列表）
- [ ] 对主页进行屏幕截图

**代理页面** (`/agents`)

- [ ] 导航到代理页面
- [ ] 验证至少列出了一个代理（来自 `--default` 的示例代理）
- [ ] 对页面进行屏幕截图

**代理详情** (`/agents/<agentId>/chat`)

- [ ] 点击代理查看详情
- [ ] 验证代理概览面板加载
- [ ] 验证模型设置面板可见
- [ ] 对页面进行屏幕截图

**代理聊天**

- [ ] 向代理发送测试消息（例如，"What's the weather in Tokyo?"）
- [ ] 等待响应
- [ ] 验证响应出现在聊天中
- [ ] 对对话进行屏幕截图

**浏览器代理** (`/agents/browser-agent/chat`)- 如果已添加浏览器代理

- [ ] 导航到浏览器代理
- [ ] 发送消息："Go to example.com and tell me what you see"
- [ ] 验证代理启动浏览器并提取内容
- [ ] 验证响应包含页面内容
- [ ] 对页面进行屏幕截图

**工具页面** (`/tools`)

- [ ] 导航到工具页面
- [ ] 验证工具列表加载（应显示 get-weather 工具）
- [ ] 对页面进行屏幕截图

**工具执行** (`/tools/get-weather`)

- [ ] 点击 get-weather 工具打开详情页面
- [ ] 找到城市输入字段并输入测试城市（例如，"Tokyo"）
- [ ] 点击提交按钮
- [ ] 等待执行完成
- [ ] 验证 JSON 输出出现并包含天气数据（温度、状况等）
- [ ] 对页面进行屏幕截图

**工作流页面** (`/workflows`)

- [ ] 导航到工作流页面
- [ ] 验证工作流列表加载（应显示 weather-workflow）
- [ ] 对页面进行屏幕截图

**工作流执行** (`/workflows/weather-workflow`)

- [ ] 点击 weather-workflow 打开详情页面
- [ ] 验证显示可视化图表（显示工作流步骤）
- [ ] 找到城市输入字段并输入测试城市（例如，"London"）
- [ ] 点击运行按钮
- [ ] 等待执行完成
- [ ] 验证步骤显示成功（绿色对勾）
- [ ] 点击查看 JSON 输出模态框
- [ ] 验证出现执行详情和计时
- [ ] 对页面进行屏幕截图

**设置页面** (`/settings`)

- [ ] 导航到设置页面
- [ ] 验证设置页面加载
- [ ] 对页面进行屏幕截图

**可观察性页面** (`/observability`)

- [ ] 导航到可观察性页面
- [ ] 验证跟踪列表显示最近的活动（来自之前的测试）
- [ ] 点击跟踪查看详情
- [ ] 验证时间线视图显示步骤和计时
- [ ] 对页面进行屏幕截图

**评分器页面** (`/evaluation?tab=scorers`)

- [ ] 导航到 `/evaluation?tab=scorers`（**不是** `/scorers` - 该路由不存在）
- [ ] 验证评分器列表加载（显示 3 个示例评分器）
- [ ] 对页面进行屏幕截图

**其他页面（仅验证加载）**

- [ ] 模板页面 (`/templates`) - 启动模板库
- [ ] 请求上下文页面 (`/request-context`) - JSON 编辑器
- [ ] 处理器页面 (`/processors`) - 空状态可以接受
- [ ] MCP 服务器页面 (`/mcps`) - 空状态可以接受

#### 5.3 报告结果

完成所有测试后，提供摘要：

- 通过/失败的测试总数
- 遇到的任何错误
- 捕获的屏幕截图
- 发现问题的建议

## 快速参考

| 步骤           | 操作                                                                |
| -------------- | --------------------------------------------------------------------- |
| 创建项目       | 在 `<directory>` 中使用 Step 1 的特定于包管理器的命令                 |
| 安装依赖       | 在创建过程中自动完成                                             |
| 设置环境变量   | 首先检查全局环境，然后检查 `.env`，仅在需要时询问用户                |
| 启动服务器     | `cd <directory>/<name> && <pm> run dev`                               |
| Studio URL     | `http://localhost:4111`                                               |

## 故障排除

**服务器无法启动**

- 验证 `.env` 包含必需的 API 密钥
- 检查端口 4111 是否可用
- 尝试 `<pm> install` 重新安装依赖项

**浏览器无法连接**

- 等待几秒钟让服务器完全启动
- 检查终端服务器就绪消息
- 验证没有防火墙阻止本地主机

**代理聊天失败**

- 验证 API 密钥有效
- 检查服务器日志中的错误
- 确保可以访问 LLM 提供者 API

**浏览器代理失败**

- 验证已安装并可以访问本地 Chromium 浏览器，例如 Google Chrome
- 检查没有其他浏览器实例阻止

## Studio 路由

| 功能         | 路由                     |
| ------------ | ------------------------- |
| 代理          | `/agents`                 |
| 工作流       | `/workflows`              |
| 工具          | `/tools`                  |
| 评估          | `/evaluation`             |
| 评分器         | `/evaluation?tab=scorers` |
| 可观察性   | `/observability/traces`   |
| 日志          | `/observability/logs`     |
| MCP 服务器     | `/mcps`                   |
| 处理器      | `/processors`             |
| 模板          | `/templates`              |
| 请求上下文 | `/request-context`        |
| 设置        | `/settings`               |

## 注意事项

- 管理默认模板构建了一个代理、工具和存储，这使得烟雾测试有意义；仅在需要不同起点时使用 `--empty` 或 `--template <template>`
- 如果用户未指定 LLM 提供者，默认为 OpenAI，因为它最常见
- 在每个主要步骤进行屏幕截图以用于文档/调试
- 在测试期间在后台保持开发服务器运行
- 传递显式标志 (`--llm`，`--no-git`，`--timeout`) 以保持创建非交互式；使用 Step 1 中记录的特定于包管理器的初始化器帮助命令，而不是假设旧标志
- 浏览器代理测试验证了新的浏览器自动化功能
- 运行代理或工作流后，可观察性跟踪会自动出现
