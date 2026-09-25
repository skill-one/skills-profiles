# Gemini 笔记本自动化

使用 `notebooklm` CLI 进行代理工作流。优先使用 `--json` 和显式 ID，以便每个操作都可检查且在并发环境下安全。仅在用户请求应用程序代码或 CLI 无法表达工作流时使用类型化的异步 Python API。以下关于就绪状态、身份、授权和凭证处理规则适用于两个接口。

## 设置和认证

需要 Python 3.10 或更高版本。在用户现有的环境中安装该包；除非有要求，否则不要创建单独的环境：

```bash
pip install "notebooklm-py[browser]"
pip install "notebooklm-py[cookies]"  # 可选的浏览器 Cookie 提取
```

如果系统 `pip` 报告 `externally-managed-environment`，请不要使用 `--break-system-packages`。对于仅 CLI 使用，提供 `uv tool install "notebooklm-py[browser]"` 或等效的 `pipx` 命令；对于应用程序代码，使用用户的活动项目环境。

对于无人值守或无头工作，优先使用基于持久配置文件的 Master-Token 认证，而不是复制的 Cookie 快照。安装 `pip install "notebooklm-py[headless]"`；一次性自动 OAuth 捕获也需要 `[browser]`。在受信任的工作站上运行 `notebooklm login --master-token --account <email>`，然后部署 `master_token.json`，而不是 `storage_state.json` 到选定配置文件。`NOTEBOOKLM_HOME` 选择私有基本目录，`NOTEBOOKLM_PROFILE` 选择其配置文件；默认解析到 `~/.notebooklm/profiles/default/master_token.json`。

在 CI 中，`NOTEBOOKLM_MASTER_TOKEN_JSON` 是秘密传输约定，不是包直接读取的环境变量。将其确切值写入选定配置文件的 `master_token.json`，模式 `0600`，取消设置它，然后运行 `notebooklm auth refresh` 以生成 `storage_state.json`。兄弟 Master-Token 可以自动重新生成过期文件 Cookie。内联 `NOTEBOOKLM_AUTH_JSON` 仅是短期备用方案；它会绕过此恢复路径。

使用 PyPI 或发布标签，而不是未发布的 `main` 检出。当可用时，参考 [安装指南](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md)。

在工作流之前，验证真实认证，而不仅仅是解析 Cookie 文件：

```bash
notebooklm auth check --test --json
```

要求 `.status == "ok"` 和 `.checks.token_fetch == true`。如果验证失败：

- 有显示器时，运行 `notebooklm login` 并再次验证。
- 在无头环境中，安装 `[cookies]` 并使用 `notebooklm login --browser-cookies <browser>`。当账户选择不明确时，首先使用 `notebooklm auth inspect --browser <browser>`。
- 如果之前有效的 Cookie 变得陈旧，尝试 `notebooklm auth refresh`；登录浏览器后使用 `notebooklm auth refresh --browser-cookies <browser>`。

正常的 `--test` 预检可能会修复并持久化刷新的 Cookie。当检查必须是严格只读时，包括故障诊断工作流，添加 `--passive`。

`notebooklm status` 报告选定笔记本上下文，而不是认证。

将两个认证文件视为担保证书：永远不要打印、记录或提交它们。Master-Token 是一个持久的完整账户凭证，可以存活密码更改；使用专用账户，在秘密存储中保护它，并在磁盘上作为 `0600`，并在暴露时明确撤销它。

## 操作不变量

1. 使用 `--json` 进行发现和变异，然后保留返回的完整 UUID。重要信封包括从 `create` 获取的 `.notebook.id`、从 `source add` 获取的 `.source.id` 和从异步生成器获取的 `.task_id`。`generate mind-map` 返回 `mind_map`、`note_id` 和 `kind`；两种类型都返回无任务 ID 或单独 `artifact wait` 步骤的完成结果。
2. 在自动化或并发工作中，在每个笔记本范围命令上传递 `-n/--notebook <id>`。不要依赖 `notebooklm use`。对于每个并发运行，还设置唯一的 `NOTEBOOKLM_PROFILE=agent-<id>`，以便上下文和配置文件写入相互隔离。新配置文件没有凭证：将 `master_token.json` 的副本放在该配置文件中，并在使用前为其生成存储。永远不要跨代理共享一个可写的 `storage_state.json`。
3. 添加源后，保留每个 `.source.id`，然后在聊天或生成之前运行每个源的 `source wait`。添加信封没有状态。要求退出码为 0 和 `status == "ready"`；让等待器处理特定于媒体的临时 `error` 行。
4. 异步生成器返回任务/工件 ID 后，将其位置传递给 `-n <notebook_id>` 的 `artifact wait`。使用 `-a <artifact_id> -n <notebook_id>` 下载该确切工件；永远不要选择最新可见工件。Mind-map 生成直接返回其完成结果，不需要 `artifact wait`。
5. 对于重叠的研究运行，始终传递 `--run-id <research_run_id>`。
6. 仅当主机实际存在时才使用主机后台设施。将等待和依赖下载命令保持在同一顺序作业中，并在等待退出 0 后才下载。否则在前景中运行或将确切 ID 固定的命令返回给用户。

## 授权边界

安全检查和明确请求的创建、源添加、聊天和提示建议可以直接运行。在尝试恢复之前，使用只读命令诊断故障。

当操作未明确授权时，立即获得确认：

- 破坏性命令，如笔记本/源/笔记/工件/标签/配置文件删除、共享移除、注销、清除、研究取消和 `ask --new`；
- `language set`，因为默认模式更改账户全局输出语言（优先使用生成命令的 `--language` 覆盖）；
- 生成或长时间前景等待，这可能需要几分钟并受速率限制；
- 下载，它写入文件；
- `research wait --import-all`，它导入源；
- `ask --save-as-note` 和 `history --save`，它们创建笔记。

用户意图，而不是 CLI 提示的存在，是授权边界。授权后，在支持的地方传递 `--yes`/`-y`。大多数破坏性 JSON 命令在没有它的情况下拒绝提示，但一些命令，包括 `ask --new --json` 和 `share remove --json`，在提示时执行。永远不要将提示缺失视为同意。

`research cancel` 是即发即弃的。在授权取消后，使用 `notebooklm research status -n <notebook_id> --run-id <research_run_id> --json` 验证确切运行。

## 命令发现

使用安装的 CLI 的帮助作为匹配版本的权威来源，而不是猜测标志：

```bash
notebooklm --help
notebooklm source --help
notebooklm research --help
notebooklm generate --help
notebooklm artifact --help
notebooklm download --help
```

当其帮助与此技能不同时，也检查 `notebooklm --version` 并深入到确切命令，例如 `notebooklm generate audio --help`。

常见操作：

| 目标 | 命令 |
|---|---|
| 检查计算使用情况 | `notebooklm usage --json`；`notebooklm usage --categories` 用于类别可用性和估计成本 |
| 列出或创建笔记本 | `notebooklm list --json`；`notebooklm create "Title" --json` |
| 添加源并等待 | `notebooklm source add <input> -n <nb> --json`；`notebooklm source wait <src> -n <nb>` |
| 聊天 | `notebooklm ask "question" -n <nb> --json` |
| 研究 | `notebooklm source add-research "query" -n <nb> --mode fast --json` (`deep` 也受支持) |
| 列出或等待工件 | `notebooklm artifact list -n <nb> --json`；`notebooklm artifact wait <id> -n <nb>` |
| 生成 | `notebooklm generate <type> ... -n <nb> --json` |
| 下载 | `notebooklm download <type> <path> -n <nb> -a <artifact>` |

对于完整界面，参考安装的命令帮助或，当可用时，参考 [CLI 参考](https://github.com/teng-lin/notebooklm-py/blob/main/docs/cli-reference.md)。对于应用程序代码，使用以下基线，并在可用时参考 [Python API 指南](https://github.com/teng-lin/notebooklm-py/blob/main/docs/python-api.md)。

## 标准源到工件工作流

保留 `{notebook_id}`、每个 `{source_id}` 和 `{artifact_id}` 从 JSON 输出：

显式请求此完成工作流授权其正常先决条件等待、请求生成和请求输出文件。仅确认未由该请求授权的工作。

1. `notebooklm create "Research: topic" --json`
2. 对于每个输入，运行 `notebooklm source add <input> -n {notebook_id} --json`。
3. 一旦前景等待被授权，为每个捕获的源运行 `notebooklm source wait {source_id} -n {notebook_id} --timeout 600`。
4. 一旦生成被授权，生成请求的类型。对于音频：
   `notebooklm generate audio "instructions" -n {notebook_id} -s {source_id} --json`。
   重复 `-s` 对于每个选定的源，并捕获 `.task_id` 作为 `{artifact_id}`。
5. 一旦前景等待被授权，运行 `notebooklm artifact wait {artifact_id} -n {notebook_id} --timeout 1200`。
6. 一旦输出写入被授权，运行 `notebooklm download audio ./podcast.m4a -a {artifact_id} -n {notebook_id}`。

对于无生成分析，用仅在每个源准备后执行的 ID 固定聊天命令替换步骤 4-6：

```bash
notebooklm ask "Summarize the key arguments" -n {notebook_id} --json
```

## 深度研究

深度研究可能需要 15-30+ 分钟。以非阻塞方式启动并保留 `.poll_task_id // .task_id` 作为 `{research_run_id}`：

```bash
notebooklm source add-research "query" -n {notebook_id} --mode deep --no-wait --json
```

仅在明确授权后导入，并固定两个 ID：

```bash
notebooklm research wait -n {notebook_id} --run-id {research_run_id} \
  --import-all --timeout 1800 --json
```

使用 `--import-all`，`--timeout` 是轮询和导入重试的每个阶段预算，因此此示例可能消耗大约 3600 秒的主机墙时间。

保留从 `.imported_sources[].id` 的新创建的源 ID，并在后续聊天或生成之前等待就绪。

## Python API 基线

当完整的 API 指南不可用时，使用安装的类型化 API 和其 docstrings；不要猜测方法名。与 CLI 工作流保持相同的 ID 和就绪门：

```python
import asyncio

from notebooklm import NotebookLMClient


async def main(url: str) -> None:
    async with NotebookLMClient.from_storage() as client:
        notebook = await client.notebooks.create("Research: topic")
        source = await client.sources.add_url(notebook.id, url)
        await client.sources.wait_until_ready(notebook.id, source.id, timeout=600)

        answer = await client.chat.ask(
            notebook.id, "Summarize the key arguments", source_ids=[source.id]
        )
        print(answer.answer)

        task = await client.artifacts.generate_audio(
            notebook.id,
            source_ids=[source.id],
            instructions="Focus on the key arguments",
        )
        final = await client.artifacts.wait_for_completion(notebook.id, task.task_id, timeout=1200)
        if not final.is_complete:
            raise RuntimeError(f"Generation ended with {final.status}: {final.error}")
        await client.artifacts.download_audio(
            notebook.id, "./podcast.m4a", artifact_id=task.task_id
        )


asyncio.run(main("https://example.com"))
```

`NotebookLMClient.from_storage()` 是一个异步上下文管理器，并且不是被等待的。客户端在一个事件循环上可重新进入，但不是线程安全的；为每个事件循环创建一个客户端。公共命名空间包括 `notebooks`、`sources`、`chat`、`research`、`artifacts`、`mind_maps`、`notes`、`settings`、`sharing`、`labels` 和 `collections`。在运行状态改变、长时间运行或文件写入调用之前，应用上述授权边界。

## 生成说明

可用的生成器包括 `audio`、`video`、`slide-deck`、`infographic`、`report`、`mind-map`、`data-table`、`quiz` 和 `flashcards`。检查 `notebooklm generate <type> --help`，因为格式、样式、源选择、语言和重试支持因类型而异。

保留这些不明显区分：

- Mind map (`--kind interactive`，默认) 是一个异步工作室工件，但 CLI 会轮询它以完成，并返回 `{mind_map, note_id, kind}`；不要运行 `artifact wait`。
- Mind map (`--kind note-backed`) 是服务器同步的。两种类型都接受 `--instructions`；交互式可靠地应用它，而服务器可能会忽略它用于笔记背书的地图。
- `generate video --format cinematic` 忽略 `--style`，需要 Google AI Ultra，并且可能需要 30-40 分钟。
- 幻灯片没有方向标志。在描述中请求横向输出（例如，`9:16 portrait`）；幻灯片修订不能改变演示文稿的方向。
- 对于自定义报告，将提示作为位置描述与 `--format custom` 一起传递；`--append` 仅适用于内置报告格式。

对于提示太长或对 shell 引用不方便，在 `ask`、`source add-research` 和支持的生成器上使用 `--prompt-file PATH`。它包含提示文本；使用 `source add` 而不是上传源文档。

## 输出和引用

结构化地使用 JSON 而不是解析人类输出。常见的生命周期值是：

- 源：`unknown`/`preparing`/`processing` -> `ready` 或 `error`；仅在 `ready` 时继续；
- 工件：`pending`/`in_progress` -> `completed`、`failed` 或 `removed`；`not_found` 可能是简短列表的延迟。仅在 `completed` 时继续或下载。

聊天 JSON 包括 `answer`、`conversation_id` 和 `references[].source_id`。引用的 `start_char`/`end_char` 是 UTF-16 偏移量，指向结构化源文档，而不是扁平的 `SourceFulltext.content`。在 Python 中，使用
`from notebooklm import resolve_chat_reference_passage`，然后调用
`await resolve_chat_reference_passage(client, notebook_id, reference)`；它使用确切的文档范围，并在必要时回退到 `find_citation_context()`。

## 故障处理

在失败时，首先运行安全的只读诊断：

```bash
notebooklm auth check --test --passive --json
notebooklm list --json
notebooklm source list -n {notebook_id} --json
notebooklm artifact list -n {notebook_id} --json
notebooklm research status -n {notebook_id} --run-id {research_run_id} --json
```

仅检查与失败工作流相关的命令。在诊断期间不要修改状态。

- 退出码 0 表示成功。预期的命令失败使用退出码 1。`source wait` 超时使用退出码 2；`artifact wait` 和 `research wait` 超时使用退出码 1。
- 首先基于退出码分支。普通的处理 JSON 失败使用 `{error, code, message}`，而等待命令返回领域信封，例如 `{"status": "timeout", "error": "..."}`。
- 在认证失败时，重新验证 `checks.token_fetch`；仅在它不是 `true` 时登录。
- 在等待超时时，报告它并检查确切源、工件或研究运行。
- 生成由 Google 速率限制。保留任务 ID，检查状态，并在用户授权它时才重试；不要无限循环。对于现有的失败 Studio 工件，在原地重试之前，检查 `notebooklm artifact retry <artifact_id> -n {notebook_id} --help`。
- 在协议错误时，记录安装版本、确切命令、相关 ID 和脱敏错误。当存在网络访问时，检查项目的问题跟踪器；当不存在时，不要在没有时编造解决方案。

保持进度更新简短，并包括相关返回 ID。永远不要暴露凭证内容。

## 技能安装

如果此文件已经在代理技能目录中，则技能本身已安装。否则：

- `notebooklm skill install` 安装或更新支持的本地技能目标。
- `notebooklm skill package` 构建可上传的存档，用于沙盒代理环境。
- `notebooklm skill status --json` 报告已安装版本和 `content_mismatch`。
