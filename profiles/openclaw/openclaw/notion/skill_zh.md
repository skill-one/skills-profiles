# Notion

推荐使用官方的 `ntn` 命令行工具。仅在 `ntn` 不可用或原始请求更清晰时使用 curl。

## 配置

```bash
npm install -g ntn
ntn --version
ntn login
```

脚本/无头认证：

```bash
export NOTION_API_TOKEN=secret_or_ntn_token
export NOTION_API_VERSION=2026-03-11
```

`ntn api` 会自动设置 `Authorization` 和 `Notion-Version`。默认使用 CLI 登录，或使用 `NOTION_API_TOKEN`。

## 检查

```bash
ntn doctor
ntn api ls
ntn api ls --json
ntn api v1/comments --help
ntn api v1/comments --spec -X POST
ntn api v1/comments --docs -X POST
```

## 页面

Markdown 优先辅助工具：

```bash
ntn pages get <page-id>
ntn pages get <page-id> --json
ntn pages create --parent page:<page-id> --content '# 标题\n\n正文'
ntn pages create --parent data-source:<data-source-id> < page.md
ntn pages update <page-id> --content '# 更新'
ntn pages update <page-id> < page.md
ntn pages trash <page-id> --yes
```

注意：

- `pages get` 会打印带有页面属性的 Markdown 作为 frontmatter。
- 内容输入：`--content`、stdin 或 TTY 中的编辑器。
- 父引用：`page:<id>`、`database:<id>`、`data-source:<id>`。
- 对于属性/模板/完整页面 API，使用 `ntn api v1/pages`。

## 数据源

```bash
ntn datasources resolve <database-id>
ntn datasources resolve <database-id> --json
ntn datasources query <data-source-id>
ntn datasources query <data-source-id> --limit 50 --json
ntn datasources query <data-source-id> --sort 'Date desc'
ntn datasources query <data-source-id> --filter '{"property":"Done","checkbox":{"equals":true}}'
```

有数据库 ID 时使用 `resolve`。查询需要数据源 ID。

## 原始 API

```bash
ntn api v1/users/me
ntn api v1/search query=roadmap page_size:=10
ntn api v1/pages 'parent[data_source_id]='"$DS_ID" 'properties[Name][title][0][text][content]=New item'
ntn api "v1/pages/$PAGE_ID" -X PATCH in_trash:=true
ntn api "v1/blocks/$PAGE_ID/children" -X PATCH \
  'children[0][type]=paragraph' \
  'children[0][paragraph][rich_text][0][text][content]=Hello'
```

输入语法：

- `path=value`：字符串体字段。
- `path:=json`：类型化 JSON 体字段。
- `name==value`：查询参数。
- `Header:Value`：请求头。
- `--data '<json>'` 或 stdin JSON 用于较大的体。
- 每个请求只能有一个体源。

## 文件

```bash
ntn files create < image.png
ntn files create --filename photo.png --content-type image/png < /tmp/photo
ntn files create --external-url https://example.com/photo.png
ntn files get <upload-id>
ntn files list
```

## 工作人员

```bash
ntn workers new
ntn workers deploy
ntn workers list --json
ntn workers runs list --json
ntn workers runs logs <run-id>
```

工作人员可能需要商业/企业计划和工作区启用。

## Curl 降级方案

```bash
curl -sS "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json"
```

## 版本说明

- 当前最新 API 版本：`2026-03-11`。
- 使用 `in_trash` 而不是 `archived`。
- 追加块定位使用 `position` 而不是扁平的 `after`。
- `transcription` 块重命名为 `meeting_notes`。
- 数据库可以包含多个数据源；页面父级通常使用 `data_source_id`。
