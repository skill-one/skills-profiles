# Diffity 树形技能

您正在打开 diffity 文件树浏览器，以便用户可以在浏览器中浏览存储库文件。

## 说明

1. 确保 `diffity` 可用：运行 `which diffity`。如果未找到，请使用 `npm install -g diffity` 安装它。
2. 使用 Bash 工具并以 `run_in_background: true` 运行 `diffity tree`：
   - CLI 处理所有操作：如果此存储库已有正在运行的实例，则重用它并打开浏览器；否则，它将启动一个新服务器并打开浏览器。
   - 请勿使用 `&` 或 `--quiet` — 让 Bash 工具处理后台运行。
3. 等待 2 秒钟，然后运行 `diffity list --json` 获取端口。
4. 告知用户 diffity tree 正在运行。打印 URL 并保持简短 — 不要显示会话 ID、哈希或其他内部信息。示例：

   > Diffity tree 正在运行于 http://localhost:5391
   >
   > 准备好时：
   > - 在浏览器中对任何文件进行评论，然后运行 **/diffity-resolve-tree** 来修复它们
