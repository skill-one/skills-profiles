# skills-profiles

本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出
中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。
English: [README.md](README.md)

`skills/<id>/` 是发布的 skill 原件：拷进 skills 目录就等于装上了。
`profiles/<id>/` 里是为它写的东西：domain 分类和中文 `description_zh`；`skills.jsonl` 是把它们连起来的清单。

## 进度

- **domain**：9007 个里已标 9006 个（100.0%），覆盖镜像安装量的 100.0%
- **快照**：`dist-2026-09-21`，2026-09-21T21:18:59Z -> 2026-09-21T21:49:08Z (30m09s)
- **可建**：9029 个里有 9007 个可读出 description；其余的永远不会被构建
