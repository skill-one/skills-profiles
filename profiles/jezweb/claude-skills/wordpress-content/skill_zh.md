# WordPress 内容管理

创建、更新和管理 WordPress 内容——文章、页面、媒体、分类、标签和菜单。通过 WP-CLI 或 REST API 在网站上生成实时内容。

## 前置条件

- 可用的 WP-CLI SSH 连接或 REST API 凭据（使用 **wordpress-setup** 技能）
- 来自 `wordpress.config.json` 或 `wp-cli.yml` 的站点配置

## 工作流程

### 第 1 步：确定操作

| 任务 | 最佳方法 |
|------|-------------|
| 创建/编辑单个文章或页面 | WP-CLI `wp post create/update` |
| 批量创建文章 | WP-CLI 循环或 REST API 批量 |
| 上传图片/媒体 | WP-CLI `wp media import` |
| 管理分类/标签 | WP-CLI `wp term` |
| 更新导航菜单 | WP-CLI `wp menu` |
| 定时发布文章 | WP-CLI 使用 `--post_date` |
| 复杂的 HTML 内容 | 写入临时文件，传递给 WP-CLI |
| 无法使用 SSH 访问 | 使用 REST API 和应用密码 |

### 第 2 步：创建内容

#### 博客文章

```bash
# 简单文章
wp @site post create \
  --post_type=post \
  --post_title="我的新博客文章" \
  --post_content="<p>文章内容。</p>" \
  --post_status=draft \
  --post_category=3,5

# 从 HTML 文件创建（适合长内容）
wp @site post create ./post-content.html \
  --post_type=post \
  --post_title="我的新博客文章" \
  --post_status=draft \
  --post_excerpt="文章的简短摘要。" \
  --post_category=3,5 \
  --tags_input="tag1,tag2"
```

**文章状态**：`draft`（草稿）、`publish`（发布）、`pending`（待审核）、`future`（定时）（使用时需配合 `--post_date`）

#### 页面

```bash
wp @site post create \
  --post_type=page \
  --post_title="关于我们" \
  --post_content="<h2>我们的故事</h2><p>内容...</p>" \
  --post_status=publish \
  --post_parent=0 \
  --menu_order=10
```

#### 定时发布文章

```bash
wp @site post create \
  --post_type=post \
  --post_title="定时发布文章" \
  --post_content="<p>这篇文章明天发布。</p>" \
  --post_status=future \
  --post_date="2026-02-23 09:00:00"
```

### 第 3 步：上传媒体

```bash
# 从 URL 上传
wp @site media import "https://example.com/image.jpg" \
  --title="产品照片" \
  --alt="产品正面视图" \
  --caption="我们最新的产品"

# 从本地文件上传（远程站点需要先使用 SCP）
scp ./image.jpg user@host:/tmp/image.jpg
wp @site media import /tmp/image.jpg --title="本地上传"

# 一步导入并设置为特色图片
wp @site media import "https://example.com/hero.jpg" \
  --title="Hero" --featured_image --post_id={id}

# 列出媒体
wp @site post list --post_type=attachment --fields=ID,post_title,guid

# 重新生成缩略图
wp @site media regenerate --yes
```

**在文章上设置特色图片**：

```bash
# 从导入输出中获取附件 ID，然后：
wp @site post meta update {post_id} _thumbnail_id {attachment_id}
```

### 第 4 步：管理分类法

#### 分类

```bash
# 列出分类
wp @site term list category --fields=term_id,name,slug,count

# 创建分类
wp @site term create category "新闻" --slug=news --description="公司新闻和更新"

# 创建子分类
wp @site term create category "产品新闻" --slug=product-news --parent=5

# 更新分类
wp @site term update category {term_id} --name="更新名称"

# 将分类分配给文章
wp @site post term add {post_id} category news
```

#### 标签

```bash
# 列出标签
wp @site term list post_tag --fields=term_id,name,slug,count

# 创建标签
wp @site term create post_tag "new-tag"

# 创建文章时添加标签
wp @site post create --post_title="..." --tags_input="seo,marketing,tips"

# 为现有文章添加标签
wp @site post term add {post_id} post_tag seo marketing tips
```

### 第 5 步：管理菜单

```bash
# 列出菜单
wp @site menu list --fields=term_id,name,slug,count

# 列出菜单中的项目
wp @site menu item list main-menu --fields=db_id,type,title,link,position

# 将页面添加到菜单
wp @site menu item add-post main-menu {page_id} --title="关于我们"

# 添加自定义链接
wp @site menu item add-custom main-menu "联系" "https://example.com/contact/"

# 添加分类存档到菜单
wp @site menu item add-term main-menu category {term_id}

# 重新排序（设置位置）
wp @site menu item update {item_id} --position=3

# 删除菜单项
wp @site menu item delete {item_id}
```

### 第 6 步：更新现有内容

```bash
# 更新文章标题和内容
wp @site post update {post_id} \
  --post_title="更新标题" \
  --post_content="<p>新内容。</p>"

# 从文件更新
wp @site post update {post_id} ./updated-content.html

# 搜索文章
wp @site post list --s="搜索词" --fields=ID,post_title

# 批量更新状态
wp @site post list --post_type=post --post_status=draft --field=ID | \
  xargs -I {} wp @site post update {} --post_status=publish

# 删除（移入回收站）
wp @site post delete {post_id}

# 永久删除
wp @site post delete {post_id} --force
```

### 第 7 步：文章元数据和自定义字段

```bash
# 获取文章的所有元数据
wp @site post meta list {post_id} --fields=meta_key,meta_value

# 获取特定元数据
wp @site post meta get {post_id} meta_key

# 设置元数据
wp @site post meta update {post_id} meta_key "meta_value"

# 添加元数据（允许重复）
wp @site post meta add {post_id} meta_key "meta_value"

# 删除元数据
wp @site post meta delete {post_id} meta_key
```

ACF 存储字段时，会同时存储字段值和引用键（`_field_name` -> `field_abc123`）。

### 第 8 步：搜索和替换

```bash
# 先执行干跑——总是
wp @site search-replace "旧文本" "新文本" --dry-run

# 执行
wp @site search-replace "旧文本" "新文本" --precise

# 限制到特定表
wp @site search-replace "旧" "新" wp_posts --precise

# 限制到特定列
wp @site search-replace "旧" "新" wp_posts post_content --precise
```

### 第 9 步：导出和导入

```bash
# 导出所有内容
wp @site export --dir=/tmp/

# 导出特定文章类型
wp @site export --post_type=post --dir=/tmp/

# 导入
wp @site import /path/to/file.xml --authors=mapping.csv
```

### 第 10 步：验证

```bash
# 检查文章
wp @site post get {post_id} --fields=ID,post_title,post_status,guid

# 获取实时 URL
wp @site post get {post_id} --field=guid

# 列出最近的文章
wp @site post list --post_type=post --posts_per_page=5 --fields=ID,post_title,post_status,post_date
```

提供管理 URL 和实时 URL：
- 管理：`https://example.com/wp-admin/post.php?post={id}&action=edit`
- 实时：`https://example.com/{slug}/`

---

## REST API 参考

当 WP-CLI 不可用时，使用带有应用密码认证的 WordPress REST API。

### 认证

```bash
# Base64 编码凭据
AUTH=$(echo -n "username:xxxx xxxx xxxx xxxx xxxx xxxx" | base64)

# 在请求中使用
curl -s https://example.com/wp-json/wp/v2/posts \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json"
```

### 端点

| 资源 | 端点 |
|----------|----------|
| 文章 | `/wp-json/wp/v2/posts` |
| 页面 | `/wp-json/wp/v2/pages` |
| 媒体 | `/wp-json/wp/v2/media` |
| 分类 | `/wp-json/wp/v2/categories` |
| 标签 | `/wp-json/wp/v2/tags` |

所有端点支持 GET（列表/单个）、POST（创建）、PUT（更新）、DELETE。

### 通过 REST 创建文章

```bash
curl -s https://example.com/wp-json/wp/v2/posts \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的新文章",
    "content": "<p>文章内容。</p>",
    "status": "draft",
    "categories": [3, 5],
    "tags": [10, 12],
    "excerpt": "简短摘要",
    "featured_media": 456
  }' | jq '{id, link, status}'
```

### 通过 REST 创建页面

```bash
curl -s https://example.com/wp-json/wp/v2/pages \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "关于我们",
    "content": "<h2>我们的故事</h2><p>内容...</p>",
    "status": "publish",
    "parent": 0
  }'
```

### 通过 REST 上传媒体

```bash
curl -s https://example.com/wp-json/wp/v2/media \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Disposition: attachment; filename=photo.jpg" \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg | jq '{id, source_url}'
```

### 通过 REST 创建分类

```bash
curl -s https://example.com/wp-json/wp/v2/categories \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d '{"name": "新闻", "slug": "news", "description": "公司更新"}'
```

### 查询参数

| 参数 | 目的 | 示例 |
|----------|----------|----------|
| `per_page` | 每页结果（最大 100） | `?per_page=50` |
| `page` | 分页 | `?page=2` |
| `search` | 搜索词 | `?search=keyword` |
| `status` | 按状态筛选 | `?status=draft` |
| `categories` | 按分类 ID 筛选 | `?categories=3` |
| `orderby` | 排序字段 | `?orderby=date` |
| `order` | 排序方向 | `?order=desc` |
| `_fields` | 限制响应字段 | `?_fields=id,title,link` |

**菜单**：导航菜单的 REST API 支持有限。FSE 主题中的块式导航存在 `/wp-json/wp/v2/navigation` 端点。经典菜单请使用 WP-CLI。

---

## 关键模式

### WP-CLI 中的 HTML 内容

对于超过一句话的内容，写入 HTML 到临时文件并传递：

```bash
cat > /tmp/post-content.html << 'EOF'
<h2>部分标题</h2>
<p>段落内容，包含 <strong>粗体</strong> 和 <a href="/link">链接</a>。</p>
<ul>
  <li>列表项一</li>
  <li>列表项二</li>
</ul>
EOF

wp @site post create /tmp/post-content.html --post_title="我的文章" --post_status=draft
```

`--post_content` 中的 Shell 引用对于复杂 HTML 是脆弱的。

### 批量操作

对于创建大量文章，使用带验证的循环：

```bash
while IFS=, read -r title slug content_file category; do
  wp @site post create "$content_file" \
    --post_type=post \
    --post_title="$title" \
    --post_name="$slug" \
    --post_category="$category" \
    --post_status=draft
  sleep 0.5
done < posts.csv
```

始终先创建为 `draft`，然后审核，再批量发布。
