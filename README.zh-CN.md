# skills-profiles

本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出
中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。
English: [README.md](README.md)

`skills/<id>/` 里是 skill 自己的 `SKILL.md` 和为它写的东西：domain 分类与
中文 `SKILL.zh.md` 页面（front matter 里带中文 description）；
`skills.jsonl` 是把它们连起来的清单。skills 旁边，`repos.jsonl` 存每个仓库的 GitHub 资料，
每个 owner 的头像在 `owners/<owner>.png`。

## 进度

- **domain**：8214 个里已标 8214 个（100.0%），覆盖镜像安装量的 100.0%
- **skill_zh**：8214 个里已有 8214 个中文页面（100.0%），覆盖镜像安装量的 100.0%
- **清单**：清单列出镜像全部 8214 个 skill；8214 个已有 description，其余在拉取前为 null
- **repos**：1044 个仓库里建了 1044 个资料（100.0%）
- **owners**：884 个 owner 里抓了 884 个头像（100.0%）
