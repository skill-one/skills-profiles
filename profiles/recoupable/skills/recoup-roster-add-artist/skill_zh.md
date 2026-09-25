# Recoup — 添加艺术家

将新艺术家引入系统中：创建账户、丰富信息，并搭建其工作空间。通过清单驱动，使长链可中断后继续。

## 8步引导链（从RECOUP.md清单驱动）

长链从文本步骤运行，因此**从`RECOUP.md`清单驱动**：
首先搭建它（frontmatter存储捕获的值；body存储未勾选的步骤），每步勾选后保存——文件即工作流状态，可从中断的第一个未勾选框继续。
不要在`agent+`账户下运行（数据会丢失）。8个调用：

1. `POST /api/artists {name, organization_id}` → 捕获`account_id`。
2. `GET /api/spotify/search` → 最佳匹配 → `id`, `external_urls.spotify`, `images[0]`。
3. 使用图片 + `profileUrls:{SPOTIFY}`（UPPERCASE键）`PATCH /api/artists/{id}`。
4. 结构化研究（重试瞬态缺失）：`/research/lookup?spotifyId=` → `songstats_artist_id`，然后`/research/profile|career|playlists` + `/research/web`。
5. Spotify目录（`topTracks`, `albums`, `album`）→ 每张专辑写`releases/{slug}/RELEASE.md` + `releases/top-tracks.md`。
6. 网络搜索社交账号（ig/tiktok/twitter/youtube）。
7. 使用发现的`profileUrls`（仅找到的平台）`PATCH /api/artists/{id}`。
8. 将`## 知识库`部分合成到`RECOUP.md`。

按顺序运行；遇到4xx/5xx错误时必须恢复才能继续。使用`recoup-platform-api-access`进行调用格式。

## 安全限制

- **文件即状态** — 每步勾选后保存，或重新开始会重做/跳过工作。
- **艺术家文件中无占位符数据** — 真实内容或删除该部分。
- **绝不凭空创建名单/艺术家** — 先通过`recoup-platform-api-access`确认；空文件系统不代表空名单。
