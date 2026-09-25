# WordPress Elementor

编辑 Elementor 页面并管理现有 WordPress 站点的模板。通过浏览器自动化（用于视觉/结构更改）或 WP-CLI（用于安全的文本替换）生成更新的页面内容。

## 前置条件

- 可用的 WP-CLI 连接或管理员访问权限（使用 **wordpress-setup** 技能）
- 安装并激活 Elementor：`wp @site plugin status elementor`

## 工作流程

### 第 1 步：识别页面

```bash
# 列出 Elementor 页面
wp @site post list --post_type=page --meta_key=_elementor_edit_mode --meta_value=builder \
  --fields=ID,post_title,post_name,post_status

# 编辑器 URL 格式：https://example.com/wp-admin/post.php?post={ID}&action=elementor
```

### 第 2 步：选择编辑方法

| 更改类型 | 方法 | 风险 |
|-------------|--------|------|
| 文本内容更新 | WP-CLI search-replace | 低（需备份） |
| 图片 URL 交换 | WP-CLI meta update | 低（需备份） |
| 组件样式 | 浏览器自动化 | 无 |
| 添加/删除区域 | 浏览器自动化 | 无 |
| 布局更改 | 浏览器自动化 | 无 |
| 模板应用 | 浏览器自动化 | 无 |

**经验法则**：如果仅更改现有组件中的文本或 URL，WP-CLI 更快。对于任何结构更改，使用浏览器中的视觉编辑器。

### 第 3 步 a：通过 WP-CLI 进行文本更新

**始终先备份**：

```bash
wp @site post meta get {post_id} _elementor_data > /tmp/elementor-backup-{post_id}.json
```

**预飞行检查清单**：

1. 备份 postmeta（上述操作）
2. 模拟替换
3. 验证模拟替换是否符合预期（替换数量正确）
4. 执行
5. 刷新 CSS 缓存
6. 可视化验证

**简单文本替换**：

```bash
# 模拟替换
wp @site search-replace "旧标题文本" "新标题文本" wp_postmeta \
  --include-columns=meta_value --dry-run --precise

# 执行（确认模拟替换正确后）
wp @site search-replace "旧标题文本" "新标题文本" wp_postmeta \
  --include-columns=meta_value --precise
```

**更新后**，清除 Elementor 的 CSS 缓存：

```bash
wp @site elementor flush-css
```

如果 `elementor` WP-CLI 命令不可用：

```bash
wp @site option delete _elementor_global_css
wp @site post meta delete-all _elementor_css
```

**安全替换的内容**：

| 安全 | 有风险 |
|------|-------|
| 标题文本 | HTML 结构 |
| 段落文本 | 组件 ID |
| 按钮文本和 URL | 区域/列设置 |
| 图片 URL（相同尺寸） | 布局属性 |
| 电话号码、电子邮件 | CSS 类 |
| 地址 | 组件排序 |

### 第 3 步 b：通过浏览器自动化进行视觉编辑

对于结构更改，使用浏览器自动化与 Elementor 的视觉编辑器交互。

**登录流程**（如果已通过 Chrome MCP 登录，可跳过）：

1. 导航到 `https://example.com/wp-admin/`
2. 输入用户名和密码
3. 点击“登录”
4. 等待仪表板加载

**打开编辑器**：

1. 导航到 `https://example.com/wp-admin/post.php?post={ID}&action=elementor`
2. 等待 Elementor 加载遮罩消失（可能需要 5-10 秒）
3. 当左侧边栏显示组件面板时，编辑器准备就绪

**编辑文本内容**：

1. 在页面预览中点击文本组件（右侧面板）
2. 组件被选中（蓝色边框）
3. 左侧边栏显示组件设置
4. 在“内容”选项卡下，在编辑器字段中编辑文本
5. 更改实时显示在预览中
6. 点击“更新”（左下角的绿色按钮）或 Ctrl+S

**编辑标题**：

1. 在预览中点击标题
2. 左侧边栏 > 内容选项卡 > “标题”字段
3. 编辑文本
4. 可选调整：HTML 标签（H1-H6）、对齐方式、链接
5. 保存

**更改图片**：

1. 在预览中点击图片组件
2. 左侧边栏 > 内容选项卡 > 点击图片缩略图
3. 打开媒体库
4. 选择新图片或上传
5. 点击“插入媒体”
6. 保存

**编辑按钮**：

1. 在预览中点击按钮
2. 左侧边栏 > 内容选项卡：文本（标签）、链接（URL）、图标（可选）
3. 样式选项卡：颜色、排版、边框、填充
4. 保存

**使用 playwright-cli**：

```bash
playwright-cli -s=wp-editor open "https://example.com/wp-admin/"
# 登录后，导航到 Elementor 编辑器
playwright-cli -s=wp-editor navigate "https://example.com/wp-admin/post.php?post={ID}&action=elementor"
```

或使用 Chrome MCP（如果使用用户的登录会话）。

### 第 4 步：管理模板

**列出保存的模板**：

```bash
wp @site post list --post_type=elementor_library --fields=ID,post_title,post_status
```

**通过浏览器导出模板**：

1. 导航到：`https://example.com/wp-admin/edit.php?post_type=elementor_library`
2. 悬停在模板上 > “导出模板”
3. 下载为 .json 文件

**通过浏览器导入模板**：

1. 导航到：`https://example.com/wp-admin/edit.php?post_type=elementor_library`
2. 点击顶部的“导入模板”
3. 选择文件 > 上传 .json
4. 模板出现在库中

**将模板应用到新页面**：

1. 创建页面：`wp @site post create --post_type=page --post_title="新页面" --post_status=draft`
2. 通过浏览器打开 Elementor
3. 点击文件夹图标（添加模板）
4. 从“我的模板”选项卡中选择
5. 点击“插入”
6. 自定义并保存

**通过 WP-CLI 复制现有页面**：

```bash
# 获取源页面的 Elementor 数据
SOURCE_DATA=$(wp @site post meta get {source_id} _elementor_data)
SOURCE_CSS=$(wp @site post meta get {source_id} _elementor_page_settings)

# 创建新页面
NEW_ID=$(wp @site post create --post_type=page --post_title="复制页面" --post_status=draft --porcelain)

# 复制 Elementor 数据
wp @site post meta update $NEW_ID _elementor_data "$SOURCE_DATA"
wp @site post meta update $NEW_ID _elementor_edit_mode "builder"
wp @site post meta update $NEW_ID _elementor_page_settings "$SOURCE_CSS"

# 重新生成 CSS
wp @site elementor flush-css
```

**通过 WP-CLI 在页面间应用模板**：

```bash
# 获取源数据
SOURCE=$(wp @site post meta get {source_id} _elementor_data)
SETTINGS=$(wp @site post meta get {source_id} _elementor_page_settings)

# 应用到目标
wp @site post meta update {target_id} _elementor_data "$SOURCE"
wp @site post meta update {target_id} _elementor_edit_mode "builder"
wp @site post meta update {target_id} _elementor_page_settings "$SETTINGS"

# 清除缓存
wp @site elementor flush-css
```

### 第 5 步：验证

```bash
# 检查页面状态
wp @site post get {post_id} --fields=ID,post_title,post_status,guid

# 获取实时 URL
wp @site post get {post_id} --field=guid
```

截图确认视觉更改：

```bash
playwright-cli -s=verify open "https://example.com/{page-slug}/"
playwright-cli -s=verify screenshot --filename=page-verify.png
playwright-cli -s=verify close
```

---

## 关键模式

### Elementor 数据格式

Elementor 将页面内容作为 JSON 存储在 `_elementor_data` postmeta 中。结构如下：

```
区域 > 列 > 组件
```

每个元素都有一个 `id`、`elType`、`widgetType` 和 `settings` 对象。直接操作此 JSON 是可能的，但容易出错——始终先备份，并优先使用 `search-replace` 而不是手动 JSON 编辑。

### CSS 缓存

任何 WP-CLI 对 Elementor 数据的更改后，都必须刷新 CSS 缓存。Elementor 从组件设置预先生成 CSS。过时的缓存 = 视觉更改不显示。

```bash
wp @site elementor flush-css
# 或如果 elementor CLI 不可用：
wp @site option delete _elementor_global_css
wp @site post meta delete-all _elementor_css
```

### 全局组件

全局组件跨页面共享。编辑一个会更新所有实例。

```bash
# 列出全局组件
wp @site post list --post_type=elementor_library --meta_key=_elementor_template_type \
  --meta_value=widget --fields=ID,post_title
```

**注意**：替换全局组件数据中的文本会影响所有使用它的页面。

### Elementor Pro 与 Free

| 功能 | Free | Pro |
|---------|------|-----|
| 基本组件 | 是 | 是 |
| 主题构建器 | 否 | 是 |
| 自定义字体 | 否 | 是 |
| 表单组件 | 否 | 是 |
| WooCommerce 组件 | 否 | 是 |
| 动态内容 | 否 | 是 |

主题构建器模板（页眉、页脚、存档）存储为 `elementor_library` post type，并具有特定元数据指示其显示条件。

### 常用 Elementor WP-CLI 命令

如果 Elementor CLI 扩展可用：

```bash
wp @site elementor flush-css          # 清除 CSS 缓存
wp @site elementor library sync       # 与模板库同步
wp @site elementor update db          # 版本更改后更新数据库
```
