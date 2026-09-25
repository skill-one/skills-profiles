# Cargo CLI — 内容

工作区**知识**管理：上传和组织**文件**（PDF、CSV、文本），并将它们分组或同步到**库**中。这些是作为代理响应基础（检索增强生成，RAG）的二进制/分组知识资源。

> **新的顶级域名（CLI ≥ 1.0.19）。** 文件和库已从 `ai` 域移至 `content` 域 — `cargo-ai content file …` 和 `cargo-ai content library …`。旧的 `cargo-ai ai file …` 命令不再存在；`unknown command` 错误表示您仍在旧路径上。

> 要将文件或库**附加**到代理（通过发布 `resources` 数组），请使用 [`cargo-ai`](../cargo-ai/SKILL.md)。
> 要使用**文件夹**组织文件，请使用 [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) (`cargo-ai workspaceManagement folder …`)。
> 对于批量运行的**输入**文件（上传到驱动批量的 CSV），那是不同的界面 — `cargo-ai workspaceManagement file upload` — 在 [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) 中有说明。

> 参考 `references/examples/files.md` 获取端到端文件、库和附加到代理的示例。
> 参考 `references/response-shapes.md` 获取完整的 JSON 响应结构。
> 参考 `references/troubleshooting.md` 获取常见错误及其解决方法。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件代码登录，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批量的任何操作都是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌范围和仅管理员界面。

## 首先发现资源

```bash
cargo-ai content file list                 # 所有上传的文件 (uuid、名称、contentType、大小)
cargo-ai content library list              # 知识库 (本地或连接器支持)
```

## 文件

上传文件（PDF、CSV、文本），以便代理可以在其特定知识基础上进行响应。上传响应包含您在将文件附加到代理发布时引用的 `uuid`（参见 [`cargo-ai`](../cargo-ai/SKILL.md)）。

```bash
# 列出所有文件
cargo-ai content file list

# 获取单个文件
cargo-ai content file get <file-uuid>

# 上传文件（可选直接上传到文件夹）
cargo-ai content file upload --file ./knowledge-base.pdf
cargo-ai content file upload --file ./knowledge-base.pdf --folder-uuid <folder-uuid>

# 更新文件名称或文件夹
cargo-ai content file update --uuid <file-uuid> --name "Q1 Research Notes"
cargo-ai content file update --uuid <file-uuid> --folder-uuid <folder-uuid>

# 删除文件
cargo-ai content file remove <file-uuid>
```

> **从上下文沙盒读取内容文件。** 上传的内容文件也**只读**地位于上下文运行时沙盒的 `.files/` 下，因此在那里运行的命令可以消费它们 — 例如 `cargo-ai context runtime execute --command ls --args '["-1",".files"]'`。该目录位于提交的上下文树之外（从未推送，不可写）；要添加或更改文件，请在此处使用 `content file`。参考 [`cargo-context`](../cargo-context/SKILL.md)。

## 库

库将文件分组为一个代理可以引用的资源。有两种类型：

- **`native`** — 工作区管理的上传文件集合。
- **`connector`** — 通过非结构化数据提取器 (`--extractor-slug`) 从外部源（例如帮助中心或知识库）同步（获取 `connectorUuid` 从 [`cargo-connection`](../cargo-connection/SKILL.md)）。

```bash
# 列出库（按类型或连接器过滤）
cargo-ai content library list
cargo-ai content library list --kind native
cargo-ai content library list --kind connector --connector-uuid <connector-uuid>

# 获取单个库
cargo-ai content library get <library-uuid>

# 创建连接器支持的库
cargo-ai content library create \
  --name "Help Center" \
  --connector-uuid <connector-uuid> \
  --extractor-slug <extractor-slug> \
  --folder-uuid <folder-uuid> \
  --config '{}'

# 更新 / 删除
cargo-ai content library update --uuid <library-uuid> --name "Updated Name"
cargo-ai content library remove <library-uuid>
```

## 附加到代理

文件和库是知识**资源** — 它们在附加到代理的草稿发布 `resources` 数组并部署后才会起作用。这种连接存在于 [`cargo-ai`](../cargo-ai/SKILL.md) (`ai release update-draft --resources …` → `ai release deploy-draft`) 中。参考 `references/examples/files.md` 获取上传 → 附加 → 部署的顺序。

## 帮助

每个命令都支持 `--help`：

```bash
cargo-ai content file upload --help
cargo-ai content library create --help
```
