# Recoup — 列出艺术家

盘点名单。艺术家目录位于 `artists/{artist-slug}/`；`RECOUP.md`
（前文 `artistName`/`artistSlug`/`artistId`）是身份文件。

## 流程

当它是真实的沙盒时，遍历文件系统（`ls -d artists/*/`,
`find artists -name RECOUP.md`）；如果 `artists/` 目录不存在/为空，则回退到
recoup-platform-api-access 轮廓发现（`GET /accounts/id` → `GET /organizations`
→ `GET /artists?org_id=…`）。

**永远不要从缺失的文件系统中报告空白的轮廓** — 空的 `artists/`
目录不等于空白的轮廓；首先与实时账户进行确认。

## 安全措施

- **永远不要凭空编造轮廓/艺术家** — 空的文件系统 ≠ 空白的轮廓。
- 报告名称 + 身份（slug/id），而不是原始的 JSON 倾倒。
