# Diffity 差异比较功能

您正在打开 diffity 差异比较查看器，以便用户可以在浏览器中查看他们的更改。

## 参数

- `ref` (可选): Git 引用，用于比较 (例如 `main..feature`, `HEAD~3`) 或 GitHub PR URL (例如 `https://github.com/owner/repo/pull/123`)。默认为工作区更改。

## 操作说明

1. 检查 `diffity` 是否可用：运行 `which diffity`。如果未找到，请使用 `npm install -g diffity` 安装它。
2. 使用 Bash 工具以 `run_in_background: true` 运行 `diffity <ref>` (如果没有引用，则直接运行 `diffity`)：
   - CLI 处理所有操作：如果该仓库已有正在运行的实例，则重用它并打开浏览器；否则，它将启动一个新服务器并打开浏览器。
   - 请勿使用 `&` 或 `--quiet` — 让 Bash 工具处理后台运行。
3. 等待 2 秒钟，然后运行 `diffity list --json` 获取端口。
4. 告知用户 diffity 正在运行。打印 URL 并保持简短 — 不要显示会话 ID、哈希或其他内部信息。示例：

   > Diffity 正在运行于 http://localhost:5391
   >
   > 准备好时：
   > - 在浏览器中针对差异添加评论，然后运行 **/diffity-resolve** 来修复它们
   > - 或运行 **/diffity-review** 获取 AI 代码评审
