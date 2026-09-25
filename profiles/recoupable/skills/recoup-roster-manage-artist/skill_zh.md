# Recoup — 管理艺术家

在 `artists/{artist-slug}/` 路径下操作现有艺术家的工作空间。
`RECOUP.md`（元数据 `artistName`/`artistSlug`/`artistId`）是身份文件。

## 布局

`context/artist.md`（关于他们的信息 — 静态），`context/audience.md`（静态），
`context/images/face-guide.png`，`releases/{slug}/RELEASE.md`（发行主文档），
`songs/{slug}/{slug}.mp3`。没有任何内容是预先创建的 — 当实际内容到达时再添加文件；不要编写占位符标记。

## 静态与动态上下文

有意地更新 `artist.md`/`audience.md`（它们是其他技能读取的真相来源）；将研究/发行文档视为有时间限制的 — 过期时归档。
提交 `{what}: {why}`；git 日志是每个艺术家的进度日志。

## 指导原则

- **艺术家文件中不包含占位符数据** — 实际内容或删除该部分。
- **不要随意覆盖静态上下文** — `artist.md` 的更改是故意的演变；在提交中注明原因。
- **永远不要凭空编造一个阵容/艺术家** — 空的文件系统 ≠ 空的阵容；首先通过 `recoup-platform-api-access` 进行确认。
