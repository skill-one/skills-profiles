# 在 GitHub 上创建仓库

在 GitHub 上创建新的仓库并克隆到本地。

## 触发条件

当用户要求创建一个新的 GitHub 仓库时使用此技能。

## 执行步骤

1. **创建仓库**：
   ```bash
   gh repo create <repo-name> --public --add-readme
   ```
   - 默认创建公开仓库（`--public`）。
   - 如果用户明确要求私有仓库，使用 `--private` 替代。
   - 默认添加 README 文件。

2. **克隆仓库**：
   ```bash
   gh repo clone zc277584121/<repo-name>
   ```

3. **确认结果**：进入项目目录，向用户报告仓库创建成功。

## 注意事项

- GitHub 账号为 `zc277584121`。
- 如果用户没有指定公开或私有，默认使用公开（`--public`）。
- 如果用户提供了描述，使用 `--description` 参数。
