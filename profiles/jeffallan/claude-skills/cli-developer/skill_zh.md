# 命令行开发人员

## 核心工作流程

1. **分析用户体验** — 确定用户工作流程、命令层级、常用任务。在编写代码前，列出所有命令及其预期的 `--help` 输出进行验证。
2. **设计命令** — 规划子命令、标志、参数、配置。确认标志命名一致性，并确保不破坏现有签名。
3. **实现** — 使用适合语言的命令行框架构建（见下文参考指南）。连接命令后，运行 `<cli> --help` 验证帮助文本是否正确渲染，运行 `<cli> --version` 确认版本输出。
4. **完善** — 添加自动补全、帮助文本、错误消息、进度指示器。验证TTY检测以支持彩色输出和优雅的SIGINT处理。
5. **测试** — 运行跨平台冒烟测试；基准测试启动时间（目标：<50ms）。

## 参考指南

根据上下文加载详细指南：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 设计模式 | `references/design-patterns.md` | 子命令、标志、配置、架构 |
| Node.js 命令行 | `references/node-cli.md` | commander, yargs, inquirer, chalk |
| Python 命令行 | `references/python-cli.md` | click, typer, argparse, rich |
| Go 命令行 | `references/go-cli.md` | cobra, viper, bubbletea |
| 用户体验模式 | `references/ux-patterns.md` | 进度条、颜色、帮助文本 |

## 快速入门示例

### Node.js (commander)

```js
#!/usr/bin/env node
// npm install commander
const { program } = require('commander');

program
  .name('mytool')
  .description('示例命令行工具')
  .version('1.0.0');

program
  .command('greet <name>')
  .description('问候用户')
  .option('-l, --loud', '大写问候')
  .action((name, opts) => {
    const msg = `Hello, ${name}!`;
    console.log(opts.loud ? msg.toUpperCase() : msg);
  });

program.parse();
```

有关 Python (click/typer) 和 Go (cobra) 的快速入门示例，请参阅 `references/python-cli.md` 和 `references/go-cli.md`。

## 限制条件

### 必须做

- 保持启动时间在 50ms 以下
- 提供清晰、可操作的错误消息
- 支持 `--help` 和 `--version` 标志
- 使用一致的标志命名规范
- 优雅处理 SIGINT (Ctrl+C)
- 早期验证用户输入
- 支持交互式和非交互式模式
- 在 Windows、macOS 和 Linux 上进行测试

### 绝对不能做

- **不必要地阻塞同步 I/O** — 使用异步读取或流处理代替。
- **当输出将被管道传输时输出到 stdout** — 将日志/诊断信息写入 stderr。
- **在输出不是 TTY 时使用颜色** — 在应用颜色前进行检测：
  ```js
  // Node.js
  const useColor = process.stdout.isTTY;
  ```
  ```python
  # Python
  import sys
  use_color = sys.stdout.isatty()
  ```
  ```go
  // Go
  import "golang.org/x/term"
  useColor := term.IsTerminal(int(os.Stdout.Fd()))
  ```
- **破坏现有命令签名** — 将标志/子命令重命名视为破坏性变更。
- **在 CI/CD 环境中要求交互式输入** — 始终通过标志或环境变量提供非交互式回退。
- **硬编码路径或平台特定逻辑** — 使用 `os.homedir()` / `os.UserHomeDir()` / `Path.home()` 代替。
- **不提供 Shell 自动补全** — 上述三个框架都支持内置补全生成。

## 输出模板

实现 CLI 功能时，请提供：
1. 命令结构（主入口点、子命令）
2. 配置处理（文件、环境变量、标志）
3. 核心实现与错误处理
4. Shell 自动补全脚本（如适用）
5. 用户体验决策的简要说明

## 知识参考

命令行框架 (commander, yargs, oclif, click, typer, argparse, cobra, viper)、终端 UI (chalk, inquirer, rich, bubbletea)、测试 (快照测试、E2E)、分发 (npm, pip, homebrew, 发布)、性能优化

[文档](https://jeffallan.github.io/claude-skills/skills/devops/cli-developer/)
