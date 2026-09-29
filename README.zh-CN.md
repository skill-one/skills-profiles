# skills-profiles

本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出
中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。
English: [README.md](README.md)

`skills/<id>/` 里是 skill 自己的 `SKILL.md` 和为它写的东西：domain 分类与
中文 `SKILL.zh.md` 页面（front matter 里带中文 description）；
`skills.jsonl` 是把它们连起来的清单。

## 进度

- **domain**：8228 个里已标 8228 个（100.0%），覆盖镜像安装量的 100.0%
- **skill_zh**：8228 个里已有 3216 个中文页面（39.1%），覆盖镜像安装量的 93.2%
- **清单**：清单列出镜像全部 8228 个 skill；8228 个已有 description，其余在拉取前为 null
