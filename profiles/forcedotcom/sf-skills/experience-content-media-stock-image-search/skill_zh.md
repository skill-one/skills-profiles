# 库存图片搜索

## 触发此技能的时机

立即触发——无需询问用户选择搜索方法——每当用户想要图片、照片或图片时。这包括以下两种情况：

- **查找现有图像：** "找一个库存图片"、"搜索X的照片"、"获取免版税图片"、"找一个符合道德的图片"、"编辑或新闻摄影"
- **以创建或生成方式提出的模糊请求：** "创建一个日落图像"、"生成一个团队会议图片"、"给我一张山脉图片"——将这些视为库存搜索请求；此技能搜索库存照片库，它不会生成图像。

在所有这些情况下，搜索库存库——这是获取图像的工具。**不要提供替代搜索方法**（混合搜索、用户提供的URL/路径等）和**不要要求用户选择。**

**不适用情况：**
- 搜索内部CMS / 数据云媒体（使用 `experience-search-coordinate`）
- 明确要求AI生成、合成或计算机生成图像的请求——此技能仅搜索许可的库存摄影，并且没有图像生成能力

---

## 第1步 — 搜索

**MCP工具：** `search_stock_images`（服务器：`media-management`）
**超时时间：** 30秒

| 参数      | 必填 | 默认值 | 备注                                                                                      |
|-----------|------|--------|------------------------------------------------------------------------------------------|
| `query`    | ✅ 是 | —      | 自然语言搜索短语（例如："日落海面"、"商务会议"），最大500个字符                     |
| `searchType` | 否   | `Creative` | `Creative`（免版税库存）、`Editorial`（授权新闻/事件图像）                         |
| `orientation`| 否   | _(无)_  | `Horizontal`、`Vertical`、`Square`、`PanoramicHorizontal`、`PanoramicVertical`          |
| `sortOrder` | 否   | `BestMatch` | `BestMatch`、`MostPopular`、`Newest`                                                   |
| `pageSize` | 否   | `5`     | 1–100                                                                                   |
| `page`     | 否   | `1`     | 1索引，必须 >= 1                                                                    |

**智能关键词提取：** 如果查询超过20个词或返回无结果，工具会自动通过LLM提取简短关键词短语并重试。响应中的`effectiveQuery`字段显示实际发送给搜索服务的内容（如果原始查询未更改，则为`null`）。

**响应字段：**

| 字段             | 备注                                                                                          |
|------------------|----------------------------------------------------------------------------------------------|
| `images[]`       | 结果列表（见下文项目字段）                                                                  |
| `totalCount`     | 跨所有页面的匹配总数                                                                       |
| `page`           | 当前页（1索引）                                                                             |
| `pageSize`       | 每页结果                                                                                   |
| `searchRequestId` | 内部关联ID。由服务器管理；不通过MCP下载工具传递。如果调试输出有用，可以安全地显示。             |
| `effectiveQuery` | 实际发送给搜索服务的关键词。如果原始查询未更改，则为`null`。                                     |
| `errorMessage`   | 如果搜索失败，则为非空                                                                      |

**每个`images[]`项目：**

| 字段          | 备注                                                                |
|---------------|----------------------------------------------------------------------|
| `assetId`     | 库存资产ID——下载时必需。如果有用，可以安全地与结果一起显示。             |
| `title`       | 图片标题                                                          |
| `caption`     | 图片描述                                                          |
| `thumbnailUrl`| 小型预览URL——用于网格显示                                           |
| `previewUrl`  | 较大的合成/预览URL——用于瓦片显示                                     |
| `width`       | 最大宽度（像素）                                                  |
| `height`      | 最大高度（像素）                                                   |
| `licenseModel`| 例如：`royaltyfree`、`rightsmanaged`                               |
| `artist`      | 贡献者/艺术家姓名                                                  |
| `collection`  | 收藏名称                                                          |

---

## 第2步 — 展示结果，然后停止

使用带内联缩略图的编号列表来渲染每个结果，使用`thumbnailUrl`作为图片，`previewUrl`作为点击链接（点击缩略图在浏览器中打开完整预览）：

```text
1. [![<title>](<thumbnailUrl>)](<previewUrl>)
   **<title>** — <artist>, <width>×<height>, <licenseModel>
2. ...
```

这是标准的Markdown图像链接语法（`[![alt](thumbnailUrl)](previewUrl)`）——它渲染实际的缩略图，而不仅仅是文本链接，点击它将导航到`previewUrl`。如果客户端不渲染Markdown图像，这将优雅地降级为链接标题。

仅在`effectiveQuery`非空且与用户原始查询不同时，才在列表前缀`Searched for: <effectiveQuery>`。

**在此处结束回合。不要自动下载，不要写文件，不要提出后续问题。** Agentforce注入自己的选择UI——一个问题或自动选择会导致重复"双重询问"。不要代表用户选择结果。

**非交互模式**（计划/无头，无用户存在）：从结果中挑选`images[0]`并报告自动选择。然后直接进入第3步。

---

## 第3步 — 下载（计费）

⚠️ **每次调用都会许可图像并消耗一个库存图片下载信用。仅在用户明确选择图像（或如上所述在非交互模式下）后调用。**

**在调用`download_stock_image`之前验证：**
- [ ] 用户已明确命名或编号他们想要的图像（或非交互模式已确认）
- [ ] 这不是对先前下载的自动重试

**MCP工具：** `download_stock_image`（服务器：`media-management`）
**超时时间：** 60秒

| 参数   | 必填 | 默认值 | 备注                                                                                              |
|--------|------|--------|----------------------------------------------------------------------------------------------------|
| `assetId` | ✅ 是 | —      | 来自先前`search_stock_images`结果的库存资产ID，最大50个字符                                           |
| `size`   | 否   | `comp` | `comp`（网络质量合成，默认值）、`medium_jpg`、`largest`（全分辨率，可能超过100 MB），最大50个字符 |

仅在用户明确要求全原始分辨率时使用`largest`。

**响应字段：**

| 字段                        | 备注                                                                 |
|----------------------------|-----------------------------------------------------------------------|
| `assetId`                    | 下载的库存资产ID                                                    |
| `managedContentBodyId`       | 存储图像字节的Salesforce记录ID                                       |
| `parentContentGenAiOutputId` | 跟踪下载请求的记录                                                  |
| `childContentGenAiOutputId`  | 将请求链接到持久化体的记录                                          |
| `byteCount`                  | 持久化图像的大小（字节）                                             |
| `format`                     | 解析的图像格式（例如：`jpg`、`png`、`eps`、`tiff`、`svg`）             |
| `url`                        | **持久化图像的URL**——用于下载或预览它                               |

---

## 第4步 — 下载到客户端并预览

在成功的`download_stock_image`调用后，将图像本地下载并在VS Code中打开。

**你必须使用`download-stock-image.py`。不要使用`curl`、`wget`或任何其他工具。**

```bash
python3 scripts/download-stock-image.py \
  --url "<url from download response>" \
  --id "<assetId>" \
  --format "<format from download response>" \
  --preview
```

该脚本通过`sf` CLI（`sf config get target-org`和`sf org auth show-access-token`）检索组织凭据，使用`Authorization: Bearer <accessToken>`下载图像到`stockimages/<assetId>.<format>`，如果传递`--preview`则在VS Code中打开。

传递`--output-dir <path>`以覆盖默认的`stockimages/`目录。

**永远不要调整或处理图像。** 使用CSS（`width`、`height`、`object-fit`）来控制显示尺寸。

**矢量/二进制格式（`eps`、`tiff`）：** 始终传递下载响应中返回的确切`format`——不要用`jpg`等格式来绕过验证错误；文件字节与扩展名不匹配，文件将显示为损坏。VS Code无法渲染`eps`/`tiff`预览，因此脚本会自动跳过`--preview`并报告保存路径。

---

## 第5步 — 报告回

在成功下载后，告诉用户：
- 图像标题和艺术家
- 保存图像的本地路径（由脚本打印）
- `managedContentBodyId`
- 署名：`{artist} · {collection}`（使用下载响应中返回的署名字符串，如果存在）

---

## 回退和错误

| 情况                          | 操作                                                                       |
|--------------------------------|------------------------------------------------------------------------------|
| `errorMessage` 在搜索中非空  | 显示它；建议更简单的查询或不同的`searchType`/`orientation`                   |
| `images` 为空                 | 建议更广泛的关键词；尝试切换`Editorial` vs `Creative`                      |
| `effectiveQuery` 不同         | 告知用户搜索服务实际接收的内容                                            |
| MCP工具不可用                | 直接使用下面的占位符URL——不要下载或保存                                  |
| 下载失败                     | 显示错误；不要自动重试——首先与用户确认（每次重试都会计费）                 |

---

## 占位符

如果`search_stock_images`和`download_stock_image`都不可用，直接将此URL用作`src`或CSS `url()`：

```text
https://cdn.scs.static.lightning.force.com/content/assets/d5222d4a11e6c2b735152d7eea824ce4/placeholder.svg
```

**占位符策略：** 只有一个占位符URL。不要下载它、修改它或使用Python、ImageMagick或任何其他工具生成替代占位符。如果用户要求特定大小或格式的占位符，告诉他们只有这个URL可用，并指导他们使用CSS在使用点进行缩放。
