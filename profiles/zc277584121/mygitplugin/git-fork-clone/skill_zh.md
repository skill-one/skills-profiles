# Git 分叉与克隆

将他人的 GitHub 仓库分叉并克隆到本地，自动配置官方远程仓库。

## 触发条件

当用户要求分叉他人的仓库并克隆到本地时使用此技能。

## 输入

用户需要提供目标仓库，格式为 `owner/repo`。

## 执行步骤

1. **分叉仓库**：使用 `gh repo fork <owner/repo> --clone=false` 将仓库分叉到 `zc277584121` 账号下。
2. **克隆仓库**：使用 `gh repo clone zc277584121/<repo>` 将分叉后的仓库克隆到本地。
3. **进入项目目录**：`cd <repo>`。
4. **添加官方远程仓库**：`git remote add official https://github.com/<original-owner>/<repo>.git`，用于跟踪上游仓库。
5. **验证远程仓库配置**：`git remote -v`，确认 origin 指向自己的分叉，official 指向原始仓库。

## 注意事项

- 如果分叉已存在，`gh repo fork` 会自动跳过分叉步骤。
- 始终使用 `official` 作为上游远程仓库名称（而非 `upstream`），以保持一致性。
- 克隆完成后向用户报告远程仓库配置结果。
