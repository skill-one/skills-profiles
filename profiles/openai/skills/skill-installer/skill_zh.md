# 技能安装器

帮助安装技能。默认情况下，这些技能来自 https://github.com/openai/skills/tree/main/skills/.curated，但用户也可以提供其他位置。

根据任务使用辅助脚本：
- 当用户询问有哪些可用技能时，或者用户使用此技能但未指定要做什么时，列出技能。默认列出的是 `.curated`，但当用户询问实验性技能时，可以传递 `--path skills/.experimental`。
- 当用户提供技能名称时，从精选列表中安装。
- 当用户提供 GitHub 仓库/路径（包括私有仓库）时，从其他仓库安装。

使用辅助脚本安装技能。

## 沟通

列出技能时，输出大致如下，具体取决于用户请求的上下文。如果他们询问实验性技能，则从 `.experimental` 而不是 `.curated` 列出，并相应地标记来源：
"""
来自 {repo} 的技能：
1. skill-1
2. skill-2 (已安装)
3. ...
您希望安装哪些？
"""

安装技能后，告诉用户它们将在下一回合可用。

## 脚本

所有这些脚本都需要网络，因此在沙盒中运行时，在运行它们时请求提升权限。

- `scripts/list-skills.py`（打印带安装注释的技能列表）
- `scripts/list-skills.py --format json`
- 示例（实验性列表）：`scripts/list-skills.py --path skills/.experimental`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- 示例（实验性技能）：`scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

## 行为和选项

- 默认情况下，公共 GitHub 仓库直接下载。
- 如果下载因认证/权限错误失败，则回退到 git 稀疏检出。
- 如果目标技能目录已存在，则中止。
- 安装到 `$CODEX_HOME/skills/<skill-name>`（默认为 `~/.codex/skills`）。
- 多个 `--path` 值在一运行中安装多个技能，每个技能的名称来自路径的基本名称，除非提供 `--name`。

选项：`--ref <ref>`（默认 `main`），`--dest <path>`，`--method auto|download|git`。

## 注意事项

- 精选列表通过 GitHub API 从 `https://github.com/openai/skills/tree/main/skills/.curated` 获取。如果不可用，解释错误并退出。
- 可以通过现有的 git 凭据或可选的 `GITHUB_TOKEN`/`GH_TOKEN` 访问私有 GitHub 仓库进行下载。
- Git 回退首先尝试 HTTPS，然后是 SSH。
- https://github.com/openai/skills/tree/main/skills/.system 中的技能是预安装的，因此无需帮助用户安装这些。如果他们询问，只需解释这一点。如果他们坚持，可以下载并覆盖。
- 安装注释来自 `$CODEX_HOME/skills`。
