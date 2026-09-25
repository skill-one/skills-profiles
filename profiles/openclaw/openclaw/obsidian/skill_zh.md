# Obsidian

使用官方的 `obsidian` 命令行界面 (CLI) 进行 Obsidian 库工作。库文件是纯 Markdown 格式，因此当更安全/更快时，仍然可以手动编辑文件。

## 要求

- 已安装 Obsidian 1.12.7 或更高版本。
- 设置 -> 常规 -> 启用命令行界面。
- `obsidian` 已注册到 PATH 环境变量中。
- Obsidian 应用程序正在运行；CLI 连接到正在运行的应用程序。

检查：

```bash
obsidian version
obsidian help
```

macOS 注册会在 `/usr/local/bin/obsidian` 创建一个指向捆绑在应用程序中的 CLI 的链接。Linux 注册会将二进制文件复制到 `~/.local/bin/obsidian`。

## 库模型

- 笔记：`*.md`。
- 配置：`.obsidian/`；除非被要求，否则避免编辑。
- 画布：`*.canvas` JSON 文件。
- 附件：库配置的文件夹。
- 多个库很常见；当存在歧义时，传递 `vault="<名称>"`。

Obsidian 桌面版在此处跟踪库：

- `~/Library/Application Support/obsidian/obsidian.json`

## 命令模式

```bash
obsidian <命令> [名称=值] [标志]
obsidian vault="Notes" search query="meeting notes" format=json
```

带空格的参数值需要使用引号。在需要时添加 `--copy` 以复制输出。

## 常用命令

打开/读取：

```bash
obsidian open file=Recipe
obsidian open path="Inbox/Idea.md" newtab
obsidian read
obsidian read file=Recipe
```

搜索：

```bash
obsidian search query="TODO" matches
obsidian search query="status::active" format=json
obsidian search:open query="project notes"
```

创建/修改：

```bash
obsidian create name="New Note"
obsidian create path="Inbox/Idea.md" content="# Idea"
obsidian append file=Note content="New line"
obsidian prepend file=Note content="After frontmatter"
```

移动/删除：

```bash
obsidian move file=Note to=Archive/
obsidian move path="Inbox/Old.md" to="Projects/New.md"
obsidian delete file=Note
```

日常/任务：

```bash
obsidian daily
obsidian daily:read
obsidian daily:append content="- [ ] Review inbox"
obsidian tasks all todo
obsidian task file=Note line=8 done
```

属性/链接：

```bash
obsidian tags all counts
obsidian property:read file=Note name=status
obsidian property:set file=Note name=status value=done
obsidian backlinks file=Note
obsidian unresolved verbose counts
```

开发/调试：

```bash
obsidian plugin:reload my-plugin
obsidian dev:errors
obsidian dev:screenshot file=shot.png
obsidian eval "app.vault.getFiles().length"
```

## 注意事项

- `file=<名称>` 使用 Obsidian 风格的文件解析；`path=<库相对路径.md>` 是精确的。
- 优先使用 CLI 的移动/删除/属性命令以进行 Obsidian 感知的更新。
- 定位到库路径后，优先直接编辑 Markdown 文件进行批量文本更改。
- 除非用户明确要求，否则不要依赖第三方 `obsidian-cli`。
