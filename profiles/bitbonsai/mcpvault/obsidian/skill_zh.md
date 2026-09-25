# Obsidian 技能

## 路由策略

使用与用户意图最匹配的后端：

1. **MCP（默认用于仓库数据操作）**
   - 读取/写入/修补/搜索笔记
   - 使用 `move_note` 移动/重命名笔记，然后显式修复反向链接
   - 前置字段和标签更新
   - 元数据和批量笔记操作

2. **Obsidian CLI/App 上下文（仅当需要 App 上下文时）**
   - 从 URI 在 Obsidian 中打开笔记
   - 触发 MCP 无法执行的 App/插件工作流

3. **CLI git（同步/备份工作流）**
   - 初始化仓库、配置远程、提交、拉取、推送
   - 定期或手动仓库备份/同步请求

当请求模糊不清时，优先选择 MCP，除非用户明确要求同步/备份/git/App 行为。

## 安全笔记重命名工作流

使用 MCP `move_note` 进行每个笔记的移动或重命名，即使 Obsidian 正在运行。不要自动调用 Obsidian CLI 的 `move` 命令：延迟的链接重写可能会将过时的字节偏移应用于移动开始后编辑的笔记，从而无声地损坏无关内容（[#176](https://github.com/bitbonsai/mcpvault/issues/176)）。仅在独立重新测试上游修复后，再考虑 CLI 移动。

反向链接保留是一个明确的、可验证的第二步：

1. 移动之前，使用其仓库相对路径和没有扩展名的文件名搜索旧 Wikilink 目标。如果 Obsidian 正在运行，其只读的 `backlinks` 命令可以补充发现，但它不能替代 MCP 搜索。
2. 使用 MCP `move_note` 移动笔记。
3. 读取每个引用笔记，并仅修补确切的 Wikilink 目标，包括嵌入和具有别名或片段的链接。在更改目标的同时保留显示文本（|别名）和 `#heading` / `#^block-id` 后缀。
4. 再次搜索旧路径和 basename。报告任何剩余的引用，而不是声称成功。
5. `search_notes` 返回最多 20 个结果。如果一个搜索达到该上限，或者旧 basename 不明确，告诉用户无法证明彻底的反向链接修复，并在继续更广泛的扫描之前询问。

分别报告移动和反向链接修复：移动了哪个笔记，有多少引用笔记被更改，以及任何剩余的过时引用。

## 注意事项

1. **`patch_note` 默认拒绝多匹配。** 使用 `replaceAll: false` 时，如果 `oldString` 出现多次，调用会失败并返回 `matchCount`。仅在您确实需要时设置 `replaceAll: true`，或者添加上下文使匹配唯一。

2. **`patch_note` 会匹配前置字段中的内容。** 替换针对包含 YAML 块的整个文件运行。像 `title:` 这样的通用字符串会匹配前置字段。包含足够的上下文以定位正确的出现。

3. **`patch_note` 禁止空字符串。** `oldString` 和 `newString` 必须非空且非空白。要删除文本，请使用带有单个空格的 `newString` 或使用 `write_note` 重新构建笔记。

4. **`search_notes` 返回最小化 JSON。** 字段被缩写：`p`（路径）、`t`（标题）、`ex`（摘要）、`mc`（匹配计数）、`ln`（行号）、`uri`（obsidianUri）。无论 `limit` 如何，硬性上限为 20 个结果。

5. **`search_notes` 多词查询会单独评分术语，并作为短语评分。** 每个术语都会被 OR 匹配，因此匹配任何术语的文档都会出现在结果中。完整短语会获得额外的评分提升。

6. **`write_note` 自动创建目录。** 父文件夹会递归创建。在 `append`/`prepend` 模式下，如果笔记不存在，则会创建。在 append/prepend 中合并前置字段（新键覆盖）；在 overwrite 中完全替换。

7. **`delete_note` 需要确切的路径确认。** `confirmPath` 必须与 `path` 字符串完全一致。没有规范化，没有尾随斜杠容忍。不匹配会静默失败，`success: false`。

8. **`move_file` 需要双重确认。** `confirmOldPath` 和 `confirmNewPath` 必须与它们的对应项完全匹配。使用 `move_note` 进行 Markdown 重命名（文本感知，无需确认）；仅用于二进制文件或需要二进制安全移动时使用 `move_file`。

9. **`manage_tags` 从两个来源读取，但写入到一个。** `list` 合并前置字段标签 + 内联 `#hashtags`。`add`/`remove` 仅修改前置字段 `tags` 数组。内联标签永远不会被修改。

10. **`read_multiple_notes` 永不拒绝。** 内部使用 `allSettled`。失败的文件出现在 `err` 数组中；成功的文件出现在 `ok` 中。始终检查两者。硬性上限为每个调用 10 个路径。

## 错误恢复

| 错误 | 下一步 |
|-------|-----------|
| `patch_note` "找到 N 个出现" | 向 `oldString` 添加周围的行以使其唯一，或设置 `replaceAll: true` |
| `delete_note` / `move_file` 确认不匹配 | 使用 `read_note` 或 `list_directory` 重新读取笔记路径，然后使用确切的字符串重试 |
| `search_notes` 返回 0 个结果 | 尝试使用单个关键词而不是短语，切换 `searchFrontmatter`，或使用部分术语扩展 |
| `read_multiple_notes` 部分错误 `err` | 使用 `list_directory` 验证失败路径，修复拼写错误或缺少扩展名，仅重试失败的路径 |

## Git 同步模式

当用户要求“同步”、“备份”或“使用 git 存储我的仓库”时，使用具有此行为的 CLI git：

1. 在更改任何内容之前运行 **预检**：
   - `git` 可用
   - 当前目录是一个 git 仓库（或在提示初始化）
   - `git config user.name` 和 `git config user.email` 已设置
   - 至少存在一个用于推送/拉取同步的远程

2. 如果预检不完整，请用一个带建议默认值的目标问题提问。
   - 使用 `askuserquestion` 提供实质性改变行为的决策。
   - 良好示例：
     - "未找到 git 仓库。现在在此仓库中初始化一个？(建议：是)"
     - "未配置远程。现在通过 gh 设置 GitHub 远程（如果可用），或提供远程 URL？(建议：通过 gh 设置)"
     - "本地和远程已分歧。现在尝试 `git pull --rebase`？(建议：是)"

3. 安全同步序列（默认情况下永不强制推送）：
   - `git add -A`
   - `git commit -m "vault sync: YYYY-MM-DD HH:mm"`（如果没有更改则跳过提交）
   - `git pull --rebase`
   - `git push`

4. `gh` 是可选的：
   - 仅在请求时用于远程引导（创建仓库 / 设置 origin）。
   - 一旦远程配置完成，无需 `gh` 即可进行正常同步。

5. 在冲突时停止并报告清晰的下一步操作。
   - 不要自动静默解决合并冲突。
   - 解释失败原因以及用户应运行的下一步操作。

## Obsidian CLI 模式

当用户要求 App 上下文操作（活动文件、在编辑器中打开、带模板的每日笔记、反向链接）时，直接通过 shell 命令使用 Obsidian CLI。

1. 在首次使用 CLI 之前运行 **预检**：
   - 使用以下候选者中的第一个匹配项解析 CLI 二进制文件：

     | 优先级 | macOS | Linux | Windows |
     |----------|-------|-------|---------|
     | 1 | `obsidian` (PATH) | `obsidian` (PATH) | `obsidian.exe` 或 `Obsidian.com` (PATH) |
     | 2 | `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli` | — | — |
     | 3 | `/Applications/Obsidian.app/Contents/MacOS/Obsidian` | — | — |

     > **Obsidian 1.12.7+ 安装程序** 包含一个专用的 `obsidian-cli` 二进制文件（比基于 Electron 的旧 CLI 快 10 倍：每个调用 ~25ms 对比 ~250ms）。在 macOS 上，安装 1.12.7+ 安装程序后，在设置 > 一般 > 高级中禁用然后重新启用 CLI 以更新 PATH 注册。这用指向 `obsidian-cli` 的 `/usr/local/bin/obsidian` 符号链接替换了旧的 `~/.zprofile` PATH 条目。
     >
     > 在 Linux 上，PATH 注册在 `/usr/local/bin/obsidian`（或作为备用 `~/.local/bin/obsidian`）创建符号链接。在 Windows 上，安装程序在 `Obsidian.exe` 旁边放置一个 `Obsidian.com` 终端重定向器。
     >
     > **注意：** 优先级表和陈旧的 PATH 检查仅在 macOS 上验证。Linux 和 Windows 也可能随 1.12.7+ 安装程序捆绑 `obsidian-cli`，但这尚未确认。欢迎通过问题或 PR 提交贡献。

   - **陈旧 PATH 检查（macOS）：** 如果优先级 1 通过 PATH 解析 `obsidian`，请检查它是否指向快速二进制文件或慢速 Electron 启动器：

     | 解析路径 | 含义 | 操作 |
     |---------------|---------|--------|
     | `/usr/local/bin/obsidian` → `obsidian-cli` | 1.12.7 符号链接注册 | 无 — 快速二进制 |
     | `/Applications/.../MacOS/obsidian` | 旧的 `~/.zprofile` 条目（预 1.12.7 注册或未重新注册的 1.12.7 安装程序） | 检查捆绑包中是否存在 `obsidian-cli` |

     如果 `obsidian` 解析到 macOS 目录（不是 `/usr/local/bin`）并且
     `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli` 存在，告诉用户：
     _"Obsidian 1.12.7+ 已安装，但 PATH 仍然指向较慢的 Electron 二进制。在 Obsidian 中，转到设置 > 一般 > 高级，禁用然后重新启用 CLI 以更新 PATH 注册。"_
     继续使用匹配的优先级 — 这是建议性的，不是阻塞性的。

   - 检查 Obsidian 是否正在运行：`pgrep -xiq obsidian`（macOS/Linux）或 `tasklist /FI "IMAGENAME eq Obsidian.exe" /NH`（Windows）
   - 如果任一失败，告诉用户并回退到 MCP 工具 + `obsidian://` URI

2. 仓库定位：`obsidian vault="VaultName" <command>`。如果 `OBSIDIAN_VAULT_NAME` 已设置，使用该显式值。否则运行 `obsidian vaults`，将 MCP 仓库路径匹配到已注册的仓库，并使用其注册名称。如果不存在唯一匹配，请询问用户。永远不要从文件夹 basename 推断注册名称。

3. 关键命令：
   ```bash
   # 读取当前活动文件
   obsidian read

   # 读取特定文件
   obsidian read file="My Note"

   # 在 Obsidian 中打开文件
   obsidian open path="Notes/example.md"

   # 打开今天的每日笔记
   obsidian daily

   # 追加到每日笔记
   obsidian daily:append content="- [ ] 新任务"

   # 搜索（Obsidian 自身的搜索，与 MCP 的 BM25 不同）
   obsidian search query="meeting notes" limit=10

   # 列出所有标签及其频率
   obsidian tags sort=count counts

   # 获取笔记的反向链接
   obsidian backlinks file="My Note"

   # 查找未解析的链接
   obsidian unresolved
   ```

   不要使用 `obsidian move`；遵循 **安全笔记重命名工作流**，使用 MCP `move_note` 和显式反向链接修复。

4. 运行 `obsidian help` 获取完整命令参考。CLI 随 Obsidian 发布而发展。

5. **何时使用 CLI 而不是 MCP：**
   - MCP 用于读取/写入/搜索/标签/前置字段和所有笔记移动/重命名（沙盒化、验证、可在无头模式下工作）
   - CLI 用于活动文件、带模板扩展的每日笔记、只读反向链接发现、在编辑器中打开，以及插件命令
   - 在 `move_note` 之后，使用 Safe Note Rename Workflow 显式修复和验证反向链接
   - 如果不确定，优先选择 MCP

## 资源

仅在需要时加载，而不是每次调用时都加载。

- [工具模式](resources/tool-patterns.md) - 当您需要工具的响应形状、模式详细信息或 move_note 与 move_file 的决策时，请阅读
- [Obsidian 规范](resources/obsidian-conventions.md) - 当您创建/编写笔记内容时（链接语法、前置字段、每日笔记格式、模板变量），请阅读
- [Git 同步](resources/git-sync.md) - 当用户要求使用 git/gh 进行备份/同步/存储仓库工作流时，请阅读
