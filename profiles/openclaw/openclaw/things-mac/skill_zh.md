# Things 3 命令行工具

使用 `things` 命令读取本地 Things 数据库（收件箱/今天/搜索/项目/区域/标签），并通过 Things URL 方案添加/更新待办事项。

## 安装

- 推荐安装（Apple Silicon）：`GOBIN=/opt/homebrew/bin go install github.com/ossianhempel/things3-cli/cmd/things@latest`
- 如果数据库读取失败：授予调用应用**完全磁盘访问权限**（手动运行时为终端；网关运行时为 `OpenClaw.app`）。
- 可选：设置 `THINGSDB`（或传递 `--db`）指向你的 `ThingsData-*` 文件夹。
- 可选：设置 `THINGS_AUTH_TOKEN` 以避免在更新操作中传递 `--auth-token`。

## 只读（数据库）

- `things inbox --limit 50`
- `things today`
- `things upcoming`
- `things search "查询内容"`
- `things projects` / `things areas` / `things tags`

## 写入（URL 方案）

- 优先安全预览：`things --dry-run add "标题"`
- 添加：`things add "标题" --notes "..." --when today --deadline 2026-01-02`
- 将 Things 前置：`things --foreground add "标题"`

## 示例：添加待办事项

- 基本用法：`things add "买牛奶"`
- 带备注：`things add "买牛奶" --notes "2% + 香蕉"`
- 添加到项目/区域：`things add "预订航班" --list "旅行"`
- 添加到项目标题：`things add "打包充电器" --list "旅行" --heading "之前"`
- 带标签：`things add "联系牙医" --tags "健康,电话"`
- 复选框：`things add "旅行准备" --checklist-item "护照" --checklist-item "票证"`
- 从标准输入（多行 => 标题 + 备注）：
  - `cat <<'EOF' | things add -`
  - `标题行`
  - `备注行 1`
  - `备注行 2`
  - `EOF`

## 示例：修改待办事项（需要授权令牌）

- 首先：获取 ID（UUID 列）：`things search "牛奶" --limit 5`
- 授权：设置 `THINGS_AUTH_TOKEN` 或传递 `--auth-token <TOKEN>`
- 标题：`things update --id <UUID> --auth-token <TOKEN> "新标题"`
- 备注替换：`things update --id <UUID> --auth-token <TOKEN> --notes "新备注"`
- 备注追加/前置：`things update --id <UUID> --auth-token <TOKEN> --append-notes "..."` / `--prepend-notes "..."`
- 移动列表：`things update --id <UUID> --auth-token <TOKEN> --list "旅行" --heading "之前"`
- 标签替换/添加：`things update --id <UUID> --auth-token <TOKEN> --tags "a,b"` / `things update --id <UUID> --auth-token <TOKEN> --add-tags "a,b"`
- 完成/取消（类似软删除）：`things update --id <UUID> --auth-token <TOKEN> --completed` / `--canceled`
- 安全预览：`things --dry-run update --id <UUID> --auth-token <TOKEN> --completed`

## 删除待办事项？

- 目前 `things3-cli` 不支持（没有 "删除/移至回收站" 写入命令；`things trash` 是只读列表）。
- 选项：使用 Things UI 删除/移至回收站，或通过 `things update` 标记为 `--completed` / `--canceled`。

## 注意事项

- 仅限 macOS。
- `--dry-run` 打印 URL 但不打开 Things。
