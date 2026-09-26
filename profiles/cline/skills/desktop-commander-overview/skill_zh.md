# 桌面命令行 MCP

桌面命令行为代理提供对用户实际计算机的访问能力——文件、文件夹、终端、进程、结构化文档以及通过 SSH 可达的远程机器。这些工具的详细架构（参数、返回形状、特定格式的行为）都存储在 MCP 本身中；本技能解释了它们的功能以及它们如何组合成常见的工作流程。

## MCP 为代理提供的内容

**持久的 Shell 会话。** 桌面命令行在工具调用之间保持已启动的进程或会话处于活动状态。在单个长生命周期的 Shell、REPL 或 SSH 会话中，状态会持续传递——环境变量、工作目录、激活的虚拟环境、打开的连接、REPL 变量——因此代理可以在许多轮次之后，无需重新设置即可 `cd`、激活一个 venv，然后向同一个会话发送命令或代码。（注意：单独的 `start_process` 调用会打开单独的会话，并且它们之间**不**共享 Shell 状态；持久性是在单个会话内部，而不是跨会话。） 

**长时间运行的进程。** 在后台启动开发服务器、监视器、构建、训练运行或测试套件，然后继续工作。MCP 返回一个代理可以在多轮次中尾随、交互或终止的进程句柄。长时间运行的命令不需要阻塞工作流程等待前景命令退出。

**超出 IDE 工作区的文件系统访问。** 读取、写入、移动、列出和检查用户已授予范围的任何文件——下载、文档、IDE 外部的项目文件夹或任何其他授予权限的文件夹。适用于组织清理任务、批量文档工作以及任何不适合在 IDE 沙盒内处理的“查看我同事刚刚发给我的文件”请求。

**对现有文件进行精确编辑。** `edit_block` 工具执行精确字符串查找和替换，并内置安全功能：歧义匹配会大声失败而不是无声地覆盖错误的内容，并且 `expected_replacements` 计数可以防止部分匹配灾难。比根据你偶然读取的切片重写整个文件具有更低的数据丢失风险——尽管错误的 `old_string` 或错误的 `expected_replacements` 仍然可能损坏内容，因此在考虑编辑完成之前，请先查看更改后的内容。

**二进制和结构化文件由 MCP 直接处理。** Excel、DOCX 和 PDF 是一等公民——通过特定格式的机制进行读取和修改，而不是仅文本的近似值：Excel 通过单元格范围 JSON，DOCX 通过原始-XML 编辑，PDF 通过在新输出文件上对页面级操作。结果是原始格式的真实文件，而不是重新生成的近似文件。图像和 PDF 返回为代理可查看的内容。

**大规模搜索。** 基于 ripgrep 的流式搜索，跨越整个项目或文件夹树。代理在文件名搜索和文件内容搜索之间进行选择，逐步分页查看结果而不会淹没上下文，并且在查询模糊时运行多个并发搜索。

**通过 SSH 访问远程机器。** 在持久 Shell 内部的长生命 SSH 会话将代理变成一个真正的运维工具：连接一次，然后多次轮次中尾随日志、运行诊断、部署或调试，而无需每一步都重新连接。

**进程管理。** 列出、检查、尾随和终止可访问的进程（受操作系统权限限制）。适用于清理先前会话中遗留的开发服务器以及诊断 CPU / 内存问题。

## 示例工作流程

每个示例都命名了实际的工具序列。下面的调用使用伪代码简写（`tool_name("arg", flag=value)`）；实际工具接受对象形状的参数。工具描述和完整参数集存储在 MCP 本身中。

### "调试这个生产问题"

在运行可能影响生产环境的 SSH 命令之前，当风险不小时，解释预期操作并获取用户确认。

`start_process("ssh user@prod.example.com", timeout_ms=...)` 打开一个长生命 SSH 会话并返回一个 PID。`interact_with_process(pid, "tail -f /var/log/app.log\n")` 开始流式传输日志。后续轮次：`read_process_output(pid, offset=-50)` 查看最后 50 行内容，`interact_with_process(pid, "...")` 在同一会话中运行诊断命令。`force_terminate(pid)` 完成时关闭会话——对于由 `start_process` 打开的会话，`force_terminate` 是正确的清理工具；`kill_process` 用于任意通过 `list_processes` 找到的操作系统 PID。

### "将这个部署到预发布环境"

在部署、重启、迁移或其他更改环境的命令之前，总结操作并确认，除非用户已经明确要求执行该确切操作。

`start_process` 用于部署命令（可以是脚本、SSH 管道命令或 `kubectl`/`gh` 等）。`read_process_output` 跟踪输出并暴露错误。如果部署需要交互式确认，`interact_with_process(pid, "yes\n")`。会话保持活动状态，同时代理等待完成或回滚。

### "运行开发服务器并迭代 API"

`start_process("npm run dev", timeout_ms=...)` 保持服务器运行。代理然后循环：`edit_block` 在路由文件上，`read_process_output(pid, offset=-30)` 查看服务器的重新加载，`start_process("curl -s http://localhost:3000/api/...")` 进行一次性测试，重复。代码更改之间开发服务器无需重启。

### "跨这个单体仓库重构"

`start_search(pattern="oldFunctionName", path=repo_root, searchType="content")` 范围内每个调用位置。`get_more_search_results(sessionId)` 分页查看。`read_multiple_files(paths=[...])` 在上下文中确认歧义命中。`edit_block(file_path, old_string, new_string)` 每个位置，当相同的子字符串在单个文件中确实出现多次时，设置 `expected_replacements`。通过在旧名称上重新运行 `start_search` 并使用 `get_more_search_results(sessionId)` 分页查看结果，直到运行完成——只有到那时才能确认零个剩余命中。

### "更新这个电子表格中的 Q3 数据并在报告中调整摘要"

`read_file(path="/.../q3.xlsx", sheet="Revenue", range="A1:F50")` 返回现有数据为 JSON 2D 数组。`edit_block(file_path="/.../q3.xlsx", range="Revenue!C12:C24", content=[[12345], ...])` 原地更新单元格。对于报告，DOCX 编辑是两读流程：首先 `read_file(path="/.../report.docx")`（偏移量 0）返回文档的提纲（标题 + 段落文本），以便您可以定位摘要部分。然后 `read_file(path="/.../report.docx", offset=N, length=...)` 并使用 **`N > 0`** 返回该部分周围的原始底层 XML——非零偏移量会切换读取模式为 XML 模式。从该输出中复制一个 XML 片段作为 `old_string`，并调用 `edit_block(file_path, old_string, new_string)` 并使用重写的 XML。用户会收到真实的 `.xlsx` 和 `.docx` 文件，而不是重新生成的近似文件。

### "将 Q3 报告生成 PDF"

组合 markdown 内容（标题、表格、通过嵌入式 HTML 的图表），然后调用 `write_pdf` 将其渲染到新的 PDF 文件。MCP 的 `write_pdf` 工具描述指定了确切的参数和文件名规则——请遵循这些。

### "将封面页插入这个 PDF"

`write_pdf` 也支持通过操作数组（插入 / 删除页面）修改现有 PDF。用于生成新 PDF 的现有 PDF 编辑——添加封面页、删除部分、合并来自其他文件的内容。查看 `write_pdf` 工具描述以了解操作形状和参数规则。

### "分析这个 200MB CSV"

`start_process("python3 -i", timeout_ms=...)` 打开 Python REPL 并返回一个 PID。`interact_with_process(pid, "import pandas as pd; df = pd.read_csv('/abs/path.csv')")` 加载一次。每个后续问题——`df.describe()`，`df.groupby('col').size()`，绘制图表——都在同一个已加载的 REPL 中运行。库不需要重新导入，数据框不需要重新加载。MCP 本身建议此工作流程用于任何本地数据文件分析。

### "运行一个快速 Node 脚本"

`start_process("node:local", timeout_ms=...)` 在 MCP 服务器本身上打开无状态的 Node 执行模式——支持 ES 导入。`start_process` 打开运行器；每段 JS 都通过 `interact_with_process(pid, "<your JS here>")` 发送并独立运行（调用之间没有共享状态）。适用于一次性转换，其中保持长时间运行的 REPL 活着不值得。不要尝试将代码放入 `start_process` 命令参数——只有运行器类型（`node:local`）放在那里。

### "解释这个代码库"

`list_directory(path=repo_root, depth=3)` 查看结构。`start_search(pattern="export ", path=repo_root, searchType="content")` 查找公共表面。`read_multiple_files(paths=[entrypoints])` 查看实际代码。代理可以不断缩小范围，而无需重新询问用户在哪里查找。

### "整理我的下载文件夹"

首先解析绝对路径（例如，`/Users/<user>/Downloads`，而不是 `~/Downloads`）。然后 `list_directory(path="/Users/<user>/Downloads", depth=1)` 查看里面有什么。`start_search(pattern="*.pdf", path="/Users/<user>/Downloads", searchType="files")` 以及其他类似类型。`create_directory` 用于新文件夹。逐项 `move_file`。在执行破坏性操作之前预览移动计划。

### "带我入职——上一次会话发生了什么？"

`get_recent_tool_calls(maxResults=200)` 返回最近的活动中带有参数和输出的活动。`list_sessions` 显示仍在运行的终端会话。`list_searches` 显示正在进行的搜索。`list_processes` 显示仍在运行的内容。它们一起重建工作，而无需用户回忆。

### "为什么 REPL 没有响应？"

`list_sessions`——如果 `Blocked: true`，REPL 正在等待输入而不是卡住。`read_process_output(pid, offset=-100)` 查看它上次打印的内容（通常是提示符）。`interact_with_process(pid, "<the input it's waiting for>\n")` 解锁它。

## 核心工具清单

最常被代理使用的工具分组索引。不完整——MCP 还暴露了此列表之外的额外配置 / 诊断 / 反馈工具。每个工具的详细参数和返回形状在 MCP 自己的工具描述中。

- **进程 / Shell:** `start_process`, `interact_with_process`, `read_process_output`, `list_processes`, `list_sessions`, `kill_process`, `force_terminate`
- **文件（读取/写入）:** `read_file`, `read_multiple_files`, `write_file`, `edit_block`, `write_pdf`
- **文件系统:** `list_directory`, `get_file_info`, `move_file`, `create_directory`
- **搜索:** `start_search`, `get_more_search_results`, `list_searches`, `stop_search`
- **诊断 / 配置:** `get_recent_tool_calls`, `get_config`

## 规范

**优先使用绝对路径。** 相对路径可能会根据工作目录失败，并且波浪号路径（`~/...`）可能不会在某些上下文中展开。绝对路径是最可靠的；尽可能传递它们。

**允许目录范围。** 文件操作仅在用户的配置 `allowedDirectories` 内部工作。预期 `list_directory` 输出中的 `[DENIED]` 标记和路径超出范围时 `read_file` / `write_file` 的拒绝。将拒绝的路径暴露给用户——不要重试。

**在 macOS 上运行时：** 默认 Shell 是 zsh。使用 `python3` 而不是 `python`。一些 GNU 工具具有前缀名称（`gsed` 用于 GNU sed）。`brew` 是典型的包管理器。`open` 从终端打开文件 / 应用，`mdfind` 是通过 Spotlight 进行精确文件名搜索的最快路径。在假设任何上述内容之前，通过 `get_config`（或通过检查 `process.platform` / `uname` 从 Shell）检测主机平台——Windows 和 Linux 主机行为不同。

**分页。** 长输出（文件读取、进程输出、搜索结果）都支持 `offset` 和 `length`。负偏移量从末尾读取（尾随模式）。使用这些而不是将巨大的结果倒入上下文。
