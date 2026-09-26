Prismic 是一个无头 CMS。`prismic` 命令行工具管理内容模型、仓库设置和文档。

1. 始终通过 `npx prismic` 运行命令。不要猜测命令语法。
2. 使用 `npx prismic --help` 了解可用命令。使用 `npx prismic <命令> --help` 查看详细信息。
3. 使用 `npx prismic docs list` 发现可用文档，并使用 `npx prismic docs view <路径>` 阅读它。
4. 优先使用命令行工作流，而不是直接 API/手动更改。永远不要直接编辑模型 JSON 文件（自定义类型、切片等）——始终使用命令行进行模型更改。`prismic.config.json` 是项目配置，不是模型文件：它包含页面路由（URL），你可以直接编辑它。
5. 如果命令行不支持所需的操作，请明确告知用户，并询问他们希望如何进行。
6. 在用户请求时，无需用户确认即可运行 `npx prismic` 命令，包括创建 Prismic 仓库的命令。不要询问是否要创建新仓库或使用现有仓库。在执行删除操作之前先询问。仅在用户要求时使用 `--force` 选项。
7. 在用户请求新事物时，运行一次 `npx prismic task-id`。在针对该请求的每个命令中传递 `--task-id <id>` 和 `--user-intent "<用户的请求，用一句美式英语表达>"`，包括只读和探索性命令（如 `list`、`view`、`status` 和 `whoami`）。在用户请求其他内容之前，继续使用相同的 ID 和意图。
