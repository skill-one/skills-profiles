# CLI-Hub 元技能

CLI-Hub 是一个代理原生的命令行界面市场，它使专业软件能够被 AI 代理使用。

## 快速入门

```bash
# 安装 CLI Hub 包管理器
pip install cli-anything-hub

# 浏览所有可用的 CLI
cli-hub list

# 按类别或关键字搜索
cli-hub search image
cli-hub search "3d modeling"

# 安装一个 CLI
cli-hub install gimp

# 显示一个 CLI 的详细信息
cli-hub info gimp
```

## 工作流矩阵

单个 CLI 是一个工具。一个 **矩阵** 是一个打包为 能力 × 提供者 的工作流——例如 `video-creation` 将意图如 `text.transcribe` 或 `visual.generate` 映射到 harness CLIs、公共 CLIs、Python 库、原生二进制文件和云 API。当任务跨越多个工具时（制作视频、设计图像、构建游戏），请使用矩阵。

标准代理序列——**安装前进行预检**：

```bash
cli-hub matrix list                                   # 浏览所有矩阵
cli-hub can "transcribe audio"                        # 在矩阵中查找该能力
cli-hub matrix search "video subtitle"                # 搜索；显示匹配的能力
cli-hub matrix preflight video-creation --json        # 这里可以使用什么？(退出码 3 = 存在差距)
cli-hub matrix preflight video-creation -c text.transcribe --fix-hints   # 一个能力 + 安装提示
cli-hub matrix install video-creation --capability text.transcribe       # 仅安装任务所需的内容
# 安装后，矩阵的 SKILL.md 本地渲染，包含提供者选择规则——请阅读它。
```

限定每次安装的范围——不要为一个单一能力任务批量安装 14 个 CLI 的矩阵。使用 `--capability <id>`、`--recipe <id>` 或 `--only a,b`，以及 `--dry-run` 来预览计划，且无副作用。`--json` 在每个矩阵子命令中都可用；退出码是 `0` 正常 · `3` 部分或存在差距 · `1` 失败 · `2` 使用错误。使用 `cli-hub matrix install <name> --resume` 重试失败，使用 `cli-hub matrix doctor <name>` 审计安装。

## 活动目录

**URL**: [`https://reeceyang.sgp1.cdn.digitaloceanspaces.com/SKILL.md`](https://reeceyang.sgp1.cdn.digitaloceanspaces.com/SKILL.md)

目录自动更新，并提供：
- 按类别组织的可用 CLI 的完整列表
- 每个工具的 `cli-hub install` 一行命令
- 完整的描述和使用模式


## 你能做什么？

CLI-Hub 涵盖了广泛软件和代码库，使代理能够通过 CLI 执行复杂的工作流：

- **创意工作流**：图像编辑、3D 建模、视频制作、音频处理、乐谱编写
- **生产力工具**：办公套件、知识管理、直播
- **AI 平台**：本地 LLMs、图像生成、AI API、研究助手
- **通信**：视频会议和协作
- **开发**：图表绘制、浏览器自动化、网络管理
- **内容生成**：AI 驱动的文档和媒体创建

每个 CLI 提供状态操作、代理的 JSON 输出、REPL 模式，并与真实软件后端集成。

## 工作原理

`cli-hub` 是 `pip` 的轻量级包装器。当你运行 `cli-hub install gimp` 时，它会安装一个单独的 Python 包 (`cli-anything-gimp`)，并具有自己的 CLI 入口点 (`cli-anything-gimp`)。每个 CLI 都是一个独立的 pip 包——`cli-hub` 只是解析注册表中的名称并跟踪安装。

## 如何使用

1. **安装 cli-hub**：`pip install cli-anything-hub`
2. **查找你的工具**：`cli-hub search <keyword>` 或 `cli-hub list -c <category>`
3. **安装**：`cli-hub install <name>` (安装 `cli-anything-<name>` pip 包)
4. **运行**：`cli-anything-<name>` 用于 REPL，或 `cli-anything-<name> <command>` 用于一次性操作
5. **JSON 输出**：所有 CLI 支持 `--json` 标志以生成机器可读输出

## 示例工作流

```bash
# 安装中心
pip install cli-anything-hub

# 查找你需要的内容
cli-hub search video

# 安装它
cli-hub install kdenlive

# 使用 JSON 输出
cli-anything-kdenlive --json project create --name my-project
```

## 更多信息

- 活动目录：https://reeceyang.sgp1.cdn.digitaloceanspaces.com/SKILL.md
- Web 中心：https://clianything.cc
- 仓库：https://github.com/HKUDS/CLI-Anything
