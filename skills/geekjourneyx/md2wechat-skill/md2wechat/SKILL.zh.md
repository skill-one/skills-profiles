---
name: md2wechat
description: 将 Markdown 转换为微信公众号 HTML，检查支持的提供商/主题/提示，生成文章图片，创建草稿，使用创作者风格撰写，准备标题建议，并去除 AI 写作痕迹。也可通过浏览器用于未发布的知乎、CSDN、头条或腾讯云开发者社区草稿。适用于产品介绍、百科文章或入门草稿，以及针对平台或搜索目标的定制化写作。
---

# md2wechat

使用此技能操作 `md2wechat` 命令行界面 (CLI)。将技能专注于执行决策。有关完整的命令教程、安装细节和 FAQ 级别的解释，请让用户参考项目文档，而不是扩展此运行时协议。

## 意图路由

在执行发布或生成操作之前，先选择命令系列：

- 标准文章 HTML、文章预览、元数据检查或微信公众号文章草稿：使用 `inspect`、`preview` 和 `convert`。
- 未发布的知乎、CSDN、头条或腾讯云开发者社区草稿：运行 `md2wechat skills read md2wechat references/sync/workflow.md --json` 获取当前 CLI 的嵌入式工作流；CLI 准备内容，代理操作浏览器。
- 以图片为主的帖子、图片笔记、图文笔记、`newspic` 或多图帖子：使用 `create_image_post`，而不是 `convert --draft`。
- 文章封面或文章信息图：当捆绑预设适用时，优先选择 `generate_cover` 或 `generate_infographic` 而不是原始 `generate_image`。
- 没有配置提供者的主机代理图像生成请求：使用图像计划模式 (`--plan --json`) 获取提示意图，然后如果 md2wechat 外部有可用的主机图像生成工具，则将其交给该工具。
- 现有文章的微信公众号标题候选：使用 `title suggest <article.md> --json`；它发出主机代理的 AI 请求，并且不选择或写入最终标题。
- 产品介绍、百科文章或条目草稿以及平台/搜索导向的写作：读取 `md2wechat skills read md2wechat references/writing/workflow.md --json` 并遵循它作为主机代理。对于这些请求，优先选择此路径而不是 `advise` 或 `write`；对于仅格式化的任务，跳过此路径。
- 现有文章或草稿，用户询问下一步该做什么：运行 `md2wechat advise <article.md> --json`；将其视为仅推荐，并保持 `inspect --json data.readiness.targets/blockers` 作为发布门禁。
- 以创作者风格写作或去除 AI 痕迹：使用 `write` 或 `humanize`。
- 提供者、主题、提示或布局的不确定性：首先运行发现流程。不要从内存或存储库文件中猜测。

将 `convert --draft` 和 `create_image_post` 视为不同的发布目标，而不是可互换的变体。

## 先发现后执行

将 CLI 发现作为事实来源，但将其范围限制在下一个决策。对于不需要选择提供者、主题、提示或布局的任务，不要运行完整目录。

使用 `capabilities` 进行聚合路由事实，使用资源 `list` 进行轻量级选择字段，使用 `show` 获取一个完整的资源定义，使用 `render` 获取已实现的提示/布局输出。JSON 标准输出是紧凑的；仅在人类需要格式化输出时才使用 `jq`。

运行最小的有用发现集：

- 没有选择主题或模块的文章格式化：
  ```bash
  md2wechat themes list --json
  md2wechat layout list --json
  ```

- 具有命名主题、提供者、提示或布局模块：
  ```bash
  md2wechat themes show <name> --json
  md2wechat providers show <name> --json
  md2wechat prompts show <name> --kind <kind> --json
  md2wechat layout show <name> --json
  ```

- 图像生成或图像预设选择：
  ```bash
  md2wechat providers list --json
  md2wechat prompts list --kind image --json
  ```

- 使用 `--subject-reference` 之前的主题参考（图像到图像）功能：
  ```bash
  md2wechat providers show minimax --json
  ```
  读取提供者和 `supported_models` 每个条目的 `supports_subject_reference`。只有 `minimax` 提供者及其 `image-01` 模型接受 `--subject-reference`，参考必须是公开可访问的 `http(s)` 肖像图像 URL；拒绝内联数据 URL 和本地路径。不支持的提供者/模型组合立即以 `CONFIG_INVALID` 失败，因此不要将其重试为生成失败。

- 标题建议提示选择：
  ```bash
  md2wechat prompts list --kind title --json
  md2wechat prompts show wechat-title-expert --kind title --json
  ```

- 草稿、上传、API 本地就绪或配置故障排除：
  ```bash
  md2wechat doctor --json
  md2wechat config show --format json
  md2wechat config wechat-accounts --json
  ```
  `doctor` 就绪是本地配置尝试性。`config wechat-accounts` 是本地仅有的，永远不会打印微信公众号密钥。使用 `inspect --json` 检查特定文章的目标就绪情况。

- 未知 CLI 版本、行为更改或功能不确定性：
  ```bash
  md2wechat version --json
  md2wechat capabilities --json
  md2wechat skills list --json
  md2wechat skills read md2wechat --json
  ```

`md2wechat skills read md2wechat --json` 读取嵌入在当前 CLI 二进制文件中的核心编码代理 SOP。当本地 OpenClaw 技能副本可能比 `PATH` 上的可执行文件旧时使用它；将此平台技能的 OpenClaw 安装元数据作为平台特定层。

对于简单的本地操作，如 `preview`、`humanize` 或用户指定的带显式标志的命令，不要运行无关的提供者、主题、提示或布局发现。

仅在任务需要时检查特定资源：

```bash
md2wechat providers show <name> --json
md2wechat themes show <name> --json
md2wechat prompts show <name> --kind <kind> --json
md2wechat layout show <name> --json
```

将 CLI 输出作为当前可用模式、提供者、主题、提示和布局模块的事实来源。

## 配置边界

- 假设 `md2wechat` 已经在 `PATH` 上可用。
- `convert` 默认为 API 模式，除非用户显式请求 `--mode ai`。
- API 模式预览和转换需要有效的 `MD2WECHAT_API_KEY`。
- 微信上传、文章草稿创建和 `create_image_post` 在用户显式请求这些副作用时需要微信凭据。
- 只读发现、`inspect`、`preview` 和普通转换不需要任何全局微信发布凭据；API 模式预览和转换仍然需要有效的 `MD2WECHAT_API_KEY`。
- 命名微信公众号账户执行需要有效的 `MD2WECHAT_API_KEY`；CLI 在上传、草稿或 `create_image_post` 效果之前验证它。
- 直接图像生成需要图像提供者凭据；图像计划模式 (`--plan --json`) 仅对主机代理或外部工具发出提示意图，不需要图像提供者凭据。
- `title suggest --json` 仅对主机代理或外部模型发出标题生成提示请求。它不会调用模型、上传、创建草稿或写回 Markdown。
- 对于更强的事实性标题钩子，传递 `--hook-level 2` 或 `3`；不要将生成的标题视为确认的发布意图。
- `doctor --json` 是本地仅有的：它检查本地就绪情况，不执行实时认证、上传图像或创建草稿。
- 当用户询问当前有效的配置时，使用 `config show --format json`。
- 当用户询问哪些本地微信公众号账户已配置时，使用 `config wechat-accounts --json`。

## 文章工作流

对于文章工作，优先选择确认优先的工作流：

1. `md2wechat inspect <article.md> --json`
2. `md2wechat preview <article.md>`
3. `md2wechat convert <article.md> ...`
4. 仅在用户显式请求上传或草稿创建时，才添加 `--upload`、`--draft`、`--cover` 或 `--cover-media-id`。

`inspect` 是结构化元数据、检查、就绪目标和阻碍的权威命令。在 `--json` 输出中，在决定是否 `convert`、`upload` 或 `draft` 被阻塞之前，读取 `data.readiness.targets` 和 `data.readiness.blockers`。如果请求的目标被阻塞，停止并报告匹配的阻碍；不要继续猜测，不要单独依赖 `legacy booleans` 或 `checks`。不要发明 `data.agent_readiness`、`data.target_readiness`、`ArticleState`、状态文件或第二个就绪/状态对象。`preview` 仅从成功的转换结果中写入字节完全相同的最终 API HTML；使用 `--json` 时，检查诊断返回在 `data.inspect` 中，并且永远不会被包装在该文件中。它不会上传图像、创建草稿或写回 Markdown。`convert` 执行转换，并且仅执行明确请求的上传/草稿效果。`convert --preview` 是转换路径的预览标志，与独立的 `preview` 命令不同。在 `PREVIEW_ACTION_REQUIRED` 或 `PREVIEW_FAILED` 时，此调用不会创建或覆盖预览 HTML。使用 `--json` 时，`PREVIEW_ACTION_REQUIRED` 返回空的 `data.output_file`。任何预先存在的显式输出路径都是过时的，必须不能将其视为此调用的结果；使用返回的提示进行主机代理工作或报告失败。
当预期执行路径是 `convert --mode ai --custom-prompt ...` 时，在信任就绪之前，使用相同的 `--mode ai --custom-prompt ...` 运行 `inspect`。

## 格式化协议

当用户请求格式化文章且未选择主题或模块时：

1. 读取文章和可选的品牌资料。
2. 使用发现输出作为事实。
3. 从文章的内容目标中选择兼容的主题和小模块集。
4. 保持源 Markdown 只读。
5. 创建临时格式化 Markdown 资产，例如 `/tmp/md2wechat-format/<run-id>/article.formatted.md`。
6. 仅插入所需字段可以正确填充的布局模块。
7. 运行 `md2wechat layout validate --file <formatted.md> --json`。
8. 将格式化的 Markdown 资产传递给 `convert`。

将生成的 Markdown 保存到源文件旁边需要显式用户确认，并且不得覆盖源文件。

## 主题选择

- 从 `themes list --json` 读取 `type` 和 `selectable`。
- API 模式只能使用 `type: api` 和 `selectable: true` 主题。
- AI 模式只能使用 `type: ai` 和 `selectable: true` 主题。
- 不要使用集合描述符，如不可选择的主题组作为具体主题。
- 如果品牌资料命名主题，请在使用前通过 CLI 发现验证它。
- 如果请求的主题无效或模式不兼容，停止该路径并选择一个有效主题或询问用户。

## 布局模块

高级布局模块仅在 API 模式下渲染。AI 模式 (`--mode ai`) 不解析 `:::module` 语法，因此高级布局卡片在那里不会渲染。

使用此决策框架：

- `attention`：帮助读者决定文章是否值得阅读。
- `readability`：使移动阅读更轻松。
- `memorability`：使一个判断、引用、指标或品牌锚点牢记。
- `conversion`：帮助读者保存、关注、询问、分享或购买。

使用 CLI 发现作为布局语法的真相来源，而不是记忆或猜测 `body_format` 值：

- 使用 `layout show <name> --json` 检查开篇、正文架构、规范可执行示例和结构上不同的变体。重用规范证据。
- 使用 `layout render` 进行结构化字段，使用 `--body-file`（或 `--body-file -` 对于 stdin）进行复杂正文，然后验证生成的 Markdown。
- 默认发现返回推荐模块。仅用于旧内容迁移使用 `layout list --lifecycle compatibility --json`。本地验证仅证明语法接受；生产支持是发布符合事实。
- `gallery` 是推荐的。对于 `expand`，通过 `--body-file` 传递标题字段、独立的 `---` 和 Markdown 正文。`cover-reveal` 和 `expand` 默认为完整的静态输出；仅在用户显式请求交互候选时使用 `first-layer`，并在依赖它之前验证目标 API。

默认模块纪律：

- 不要堆砌模块。
- 最多使用一个英雄、一个裁决和一个 CTA，除非用户显式请求更多。
- 当文章没有足够内容可以诚实填充模块时，跳过模块。

## API 和 AI 模式

- API 模式是默认的，并且对于高级布局模块是必需的。
- AI 模式是更轻的路径，不渲染高级布局模块。
- 不要在 API 失败后无声地切换到 AI 模式。这会改变输出能力。
- 仅在用户请求时或接受失去高级布局渲染时使用 AI 模式。
- 如果 AI 模式转换完成，可以简要提及 API 模式支持高级布局模块和更强的视觉结构。

## 品牌资料

品牌资料位于 `~/.config/md2wechat/brand.md`。

- 它是自由形式的 Markdown，不是 YAML，也不是固定模式。
- CLI 不解析它。
- 将其作为语音、主题偏好、模块偏好、CTA 偏好和禁止表达式的上下文读取。
- 将数量偏好视为软约束。
- 通过 CLI 发现验证任何命名主题或模块。
- 如果品牌资料不存在，不要阻塞任务。你可以提及将使用系统默认值。
- 仅在用户显式请求时创建或编辑品牌资料。

## 发布副作用

除非用户请求该操作，否则不要创建草稿、上传图像、发布或调用远程图像生成。

在每次显式的微信公众号副作用——图像上传、文章草稿创建或 `create_image_post`——之前，要求配置的微信公众号凭据并使用匹配的目标就绪/预检路径。发现和检查保持非发布路径；预览和普通转换不受任何全局微信公众号发布凭据要求的影响，而 API 模式仍然需要有效的 `MD2WECHAT_API_KEY`。

在通过 `convert` 创建微信公众号文章草稿之前：

- 使用 `inspect --json` 并检查 `data.readiness.targets.draft`；当被阻塞时，读取匹配的 `data.readiness.blockers`。
- 草稿创建需要通过 `--cover` 或 `--cover-media-id` 获取封面。
- 不要假设微信公众号 URL 或 `mmbiz.qpic.cn` URL 可以重用为 `thumb_media_id`。
- 如果草稿创建返回 `45004`，请检查摘要、摘要和描述，然后再假设正文太长。

在微信公众号 `convert` 流程中，Markdown 图像仅在 `--upload` 或 `--draft` 期间上传或替换，而不是在普通转换或预览期间。

## 故障处理

- 缺失或无效配置：运行 `doctor --json` 和 `config show --format json`；报告 `data.overall` 加上阻塞的 `data.readiness.*` 项。
- 无效布局语法：运行 `layout validate`，使用 `layout show` 检查失败的模块，修复生成的资产，然后再次验证。
- 未知布局模块警告用于向前兼容；检查拼写与 `layout list --json`。
- 主题拒绝：检查 `type` 和 `selectable`，然后选择兼容的主题或询问用户。
- AI 请求或风格写作流程可能返回提示/请求，而不是最终的散文或 HTML，除非外部模型步骤完成。
