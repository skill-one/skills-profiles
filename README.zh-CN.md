# skills-profiles

本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出
中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。
English: [README.md](README.md)

`skills/<id>/` 是各角度共用的构建源；完整的 skill 在它自己的仓库里。
`profiles/<id>/` 里是为它写的东西：domain 分类、中文 `description_zh` 和
中文 `skill_zh` 页面；`skills.jsonl` 是把它们连起来的清单。

## 进度

- **domain**：9006 个里已标 8335 个（92.5%），覆盖镜像安装量的 90.2%
- **translate**：9006 个里已翻译 9006 个（100.0%），覆盖镜像安装量的 100.0%
- **skill_zh**：9006 个里已有 8670 个中文页面（96.3%），覆盖镜像安装量的 99.1%
- **快照**：`dist-2026-09-24`，2026-09-24T20:52:29Z -> 2026-09-24T21:22:24Z (29m54s)
- **清单**：镜像列出的 9028 个里 9006 个有 description；其余的不进清单
