# 预览导入

在本地开发服务器中打开并验证导入的内容。

## 何时使用此技能

使用此技能当：
- 您已生成 HTML 文件（来自 generate-import-html）
- 准备在浏览器中预览并验证渲染效果
- 需要与传统页面结构进行比较

**由以下技能触发：** page-import 技能（步骤 5）

## 前置条件

从之前的技能中，您需要：
- ✅ 正确路径下的 HTML 文件（来自 generate-import-html）
- ✅ 同一目录下的图片文件夹
- ✅ scrape-webpage 生成的 screenshot.png（用于比较）
- ✅ metadata.json 中的 documentPath（用于构建 URL）

## 相关技能

- **page-import** - 调用此技能的协调器
- **generate-import-html** - 提供预览的 HTML 文件
- **scrape-webpage** - 提供用于比较的截图

## 预览工作流程

### 第 1 步：使用 HTML 文件夹标志启动开发服务器

**确定 metadata.json 中的文件夹：**
- 查看 metadata.json 中的 `paths.dirPath`（例如，`/us`）
- 这是包含您导入的 HTML 文件的根文件夹

**命令：**
```bash
aem up --html-folder {dirPath}
```

**基于导入内容位置的示例：**

| HTML 文件位置 | 命令 | 预览 URL |
|-------------------|---------|-------------|
| `us/en.plain.html` | `aem up --html-folder us` | `http://localhost:3000/us/en` |
| `products/widget.plain.html` | `aem up --html-folder products` | `http://localhost:3000/products/widget` |
| `blog/2024/post.plain.html` | `aem up --html-folder blog` | `http://localhost:3000/blog/2024/post` |

**为何需要此操作：**
- 没有 `--html-folder`，AEM CLI 会将请求代理到远程服务器
- 远程服务器没有您本地导入的内容
- 结果：出现 404 "页面未找到" 错误

---

### 第 2 步：在浏览器中导航

**对于大多数文件，直接使用文档路径：**
```
http://localhost:3000${documentPath}
```

示例：
- HTML 文件：`us/en/about.plain.html`
- URL：`http://localhost:3000/us/en/about`

**重要提示：** 对于索引文件，使用 `/` 而不是 `/index`：
```
如果文件是：index.plain.html
预览在：http://localhost:3000/
而不是：http://localhost:3000/index
```

**注意：** 如果您使用了 `--html-folder` 标志（例如，`aem up --html-folder drafts`），请将此文件夹添加到 URL 前面：
```
文件：drafts/test.plain.html
URL：http://localhost:3000/drafts/test
```

使用 metadata.json 中的 `paths.documentPath`，但对于索引文件确保路径是 `/` 而不是 `/index`

---

### 第 3 步：验证渲染效果

**检查以下内容：**
- ✅ 块以正确的样式渲染
- ✅ 布局与传统页面结构匹配（与 screenshot.png 比较）
- ✅ 图片加载（或显示适当的占位符）
- ✅ 没有可见的原始 HTML
- ✅ 页面源代码中显示元数据（查看源代码，检查 `<meta>` 标签）
- ✅ 正确应用了区域样式

---

### 第 4 步：与传统页面比较

**并排比较：**
1. 在浏览器预览旁边打开 `./import-work/screenshot.png`
2. 检查内容结构是否匹配
3. 验证块是否正确装饰
4. 确认区域边界是否对齐
5. 验证样式一致性

---

## 故障排除

**块渲染不正确：**
- 检查 HTML 结构是否与预期格式匹配
- 验证块名称是否完全匹配（区分大小写）
- 查看 [../content-driven-development/references/html-structure.md](../content-driven-development/references/html-structure.md) 获取格式指导

**图片未加载：**
- 验证图片文件夹是否与 HTML 文件在同一目录
- 检查图片路径是否为 `./images/...` 格式
- 确保图片已从 `./import-work/images/` 正确复制

**可见原始 HTML：**
- 块名称可能与项目中现有的块不匹配
- 检查浏览器控制台是否有 JavaScript 错误
- 验证块是否存在于 `blocks/` 目录

**页面源代码中无元数据：**
- 检查元数据块是否位于 HTML 文件的末尾
- 查看页面源代码并在 `<head>` 中搜索 `<meta>` 标签
- 验证元数据属性是否与预期格式匹配

**开发服务器未运行：**
- 使用 `aem up` 启动服务器
- 检查端口冲突（默认 3000）
- 验证您是否在正确的项目目录

**页面未找到（404）：**
- **最常见原因：** 缺少 `--html-folder` 标志 - 重新启动服务器使用 `aem up --html-folder {dirPath}`
- 验证 HTML 文件是否存在于预期路径
- 检查 metadata.json 中的 documentPath 是否与 URL 匹配
- 对于索引文件，使用 `/` 而不是 `/index`
- 检查终端输出是否确认 "Serving HTML files from folder: {folder}"

---

## 输出

此技能提供：
- ✅ 与传统页面结构匹配的验证预览
- ✅ 正确渲染的视觉确认
- ✅ 验证的块装饰
- ✅ 确认的元数据存在

**当所有验证点通过时，导入完成。**
