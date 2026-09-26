# 🪢 Agentspace

**随时随地查看你的智能体正在做什么。**

你的智能体持续生成日志、代码、输出内容。你只需打开一个链接，在浏览器中即可观察文件夹的演变过程。无需同步、无需压缩、无需账户。

1. 告知智能体共享任何本地文件夹或文件。
2. 智能体返回一个链接——任何人都可以在浏览器中打开它，无需注册。

[agentspace.so](https://agentspace.so/?utm_source=skills.sh&utm_medium=skill&utm_campaign=agentspace) · [GitHub](https://github.com/agentspace-so/skills) · [npm @agentspace-so/ascli](https://www.npmjs.com/package/@agentspace-so/ascli)

## 你可以共享的内容

文件夹、单个文件、生成代码、测试输出、构建日志、截图、PDF文件、报告、仪表盘、原型——任何本地工件。

## 工作原理

- 执行一条命令 (`ascli share <路径>`) 创建匿名工作区并返回链接。
- 任何人打开链接——直接在浏览器中阅读、评论或编辑。
- 匿名工作区持续24小时。一个电子邮件声明即可使其永久化。
- 部署在Cloudflare的边缘网络——链接在全球范围内快速加载。

## 数据处理

- 仅上传用户明确命名的路径。除非用户明确说明，否则不要默认当前工作目录。
- 所有网络流量仅发送至 `agentspace.so`。
- 该技能不会读取环境变量、shell历史记录或用户指定路径之外的文件。

## 选择CLI路径

1. 如果 `ascli` 已在 `PATH` 中，直接使用它。
2. 否则如果 `npm` 可用，使用 `npm install -g @agentspace-so/ascli@latest` 安装一次，或通过 `npx @agentspace-so/ascli@latest <命令>` 无需安装运行。
3. 如果 `ascli` 和 `npm` 都不可用，停止操作并提示用户先从 nodejs.org 安装Node.js。

不要将远程脚本管道到shell中安装。

## 共享路径

- 如果用户未明确指定要共享的文件夹或文件，询问用户。不要假设 `.`。
- 使用用户指定的路径运行 `ascli share <路径> --permission edit`。
- 如果用户要求仅查看权限，使用 `--permission view`。
- `share` 处理未绑定文件夹时，通过创建临时工作区、同步一次并返回链接——无需单独的 `sync` 步骤。
- 直接将分享链接返回给用户，与CLI打印的完全一致。

## 安全限制

- 不要自行创建声明URL、工作区URL或分享URL。仅返回CLI打印的内容。
- 如果 `npx` 已可用，不要要求全局安装。
- 不要仅为了使用 agentspace.so 将用户移入其他项目。
- 如果用户要求“共享此文件夹”但目标不明确，在运行前确认确切路径。
- 如果需要精确命令变体，请阅读 [references/commands.md](references/commands.md)。
