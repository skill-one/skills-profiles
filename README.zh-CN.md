# skills-profiles

本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出
中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。
English: [README.md](README.md)

`skills/<id>/` 是各角度共用的构建源；完整的 skill 在它自己的仓库里，清单的 `url`
指向它。`profiles/<id>/` 里是为它写的东西：domain 分类、中文 `description_zh` 和
中文 `skill_zh` 页面；`skills.jsonl` 是把它们连起来的清单。

## 进度

- **domain**：9007 个里已标 9006 个（100.0%），覆盖镜像安装量的 100.0%
- **translate**：9007 个里已翻译 8986 个（99.8%），覆盖镜像安装量的 99.9%
- **skill_zh**：9007 个里已有 242 个中文页面（2.7%），覆盖镜像安装量的 59.0%
- **快照**：`dist-2026-09-21`，2026-09-21T21:18:59Z -> 2026-09-21T21:49:08Z (30m09s)
- **可建**：9029 个里有 9007 个可读出 description；其余的永远不会被构建
