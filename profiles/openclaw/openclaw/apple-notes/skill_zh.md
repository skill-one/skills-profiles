# Apple Notes CLI

使用 `memo notes` 从终端直接管理 Apple Notes。创建、查看、编辑、删除、搜索笔记，在文件夹间移动笔记，并导出为 HTML/Markdown 格式。

安装

- 安装（Homebrew）：`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- 手动（pip）：`pip install .`（克隆仓库后）
- 仅限 macOS；如果提示，请授予 Automation 对 Notes.app 的访问权限。

查看笔记

- 列出所有笔记：`memo notes`
- 按文件夹筛选：`memo notes -f "文件夹名称"`
- 搜索笔记（模糊）：`memo notes -s "查询"`

创建笔记

- 添加新笔记：`memo notes -a`
  - 打开交互式编辑器来编写笔记。
- 带标题快速添加：`memo notes -a "笔记标题"`

编辑笔记

- 编辑现有笔记：`memo notes -e`
  - 交互式选择要编辑的笔记。

删除笔记

- 删除笔记：`memo notes -d`
  - 交互式选择要删除的笔记。

移动笔记

- 将笔记移动到文件夹：`memo notes -m`
  - 交互式选择笔记和目标文件夹。

导出笔记

- 导出为 HTML/Markdown：`memo notes -ex`
  - 导出选定的笔记；使用 Mistune 进行 Markdown 处理。

限制

- 无法编辑包含图片或附件的笔记。
- 交互式提示可能需要终端访问权限。

备注

- 仅限 macOS。
- 需要可访问 Apple Notes.app。
- 对于自动化，请在“系统设置” > “隐私与安全” > “自动化”中授予权限。
