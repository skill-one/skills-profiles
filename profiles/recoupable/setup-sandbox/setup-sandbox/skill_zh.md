# 沙盒设置

为连接的账户的组织和艺术家创建文件夹结构。

## 环境

- `RECOUP_ACCOUNT_ID` — 用于获取数据的账户 ID。仅在使用组织 API 密钥时需要。在使用个人 API 密钥时，请省略 `--account` 标志，CLI 将自动使用经过身份验证的账户。

## 步骤

1.  检查 `RECOUP_ACCOUNT_ID` 是否已设置。如果已设置，请在以下所有 CLI 命令中使用 `--account $RECOUP_ACCOUNT_ID`。如果未设置，请省略 `--account` 标志。
2.  运行 `recoup orgs list --json [--account $RECOUP_ACCOUNT_ID]` 获取所有组织。
3.  对于每个组织，运行 `recoup artists list --org {organization_id} --json [--account $RECOUP_ACCOUNT_ID]` 获取其艺术家。
4.  创建文件夹结构并在每个艺术家文件夹中创建一个 `RECOUP.md` 标记：
   - 使用 CLI 响应中的 `artistSlug` 作为确切的目录名——绝不能追加 UUID、ID 或后缀。
   - 如果 `orgs/{org}/artists/{artist-slug}/` 已存在，请跳过。
   - 对于每个新艺术家，运行 `mkdir -p orgs/{org}/artists/{artist-slug}`。
   - 使用以下模板编写 `RECOUP.md`。
5.  提交并推送：
   - `git add -A && git commit -m "setup: create org and artist folders" && git push origin main`

## `RECOUP.md`

每个艺术家目录在其根目录都有一个 `RECOUP.md`。这是**身份文件**——它将工作区连接到 Recoupable 平台。该文件的存在表示工作区处于活动状态。

用 CLI 响应中的数据填充它：

```markdown
---
artistName: {Artist Name}
artistSlug: {artist-slug}
artistId: {uuid-from-recoupable}
---
```

**字段：**

- `artistName` — CLI 中的显示名称（例如 `Gatsby Grace`）
- `artistSlug` — 小写连字符分隔的文件夹名称（例如 `gatsby-grace`）
- `artistId` — 来自 Recoup 的 UUID
