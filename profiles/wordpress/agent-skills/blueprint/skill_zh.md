# WordPress Playground 蓝图

## 概述

蓝图是一个 JSON 文件，用于声明性地配置 WordPress Playground 实例——安装插件/主题、设置选项、运行 PHP/SQL、操作文件等。

**核心原则**：蓝图是受信任的纯 JSON 声明。没有任意的 JavaScript。它们适用于网络、Node.js 和 CLI。

## 快速入门模板

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "landingPage": "/wp-admin/",
  "preferredVersions": { "php": "8.3", "wp": "latest" },
  "steps": [{ "step": "login" }]
}
```

## 顶层属性

所有属性都是可选的。仅允许文档中记录的键——模式会拒绝未知属性。

| 属性 | 类型 | 备注 |
|------|------|-------|
| `$schema` | string | 始终为 `"https://playground.wordpress.net/blueprint-schema.json"` |
| `landingPage` | string | 相对路径，例如 `/wp-admin/` |
| `description` | string | 已弃用的可选顶层描述。新蓝图请使用 `meta.description` |
| `meta` | object | `{ title, author, description?, categories? }` — 标题和作者为必需 |
| `preferredVersions` | object | `{ php, wp }` — 存在时两者都必需 |
| `features` | object | `{ networking?: boolean, intl?: boolean }` — 仅这两个键，其他键无效。Networking 默认为 `true` |
| `phpExtensionBundles` | any | 已弃用/不再使用；模式将值保留为不受约束，并建议从蓝图中移除它 |
| `extraLibraries` | array | `["wp-cli"]` — 当存在任何 `wp-cli` 步骤时自动包含 |
| `constants` | object | `defineWpConfigConsts` 的简写。值：字符串/布尔值/数字 |
| `plugins` | array | `installPlugin` 步骤的简写。字符串 = wp.org slugs |
| `siteOptions` | object | `setSiteOptions` 的简写 |
| `login` | boolean 或 object | `true` = 以管理员身份登录。对象 = `{ username?, password? }`（两者默认为 `"admin"`/`"password"`） |
| `steps` | array | 主要执行管道。在简写之后运行 |

### `preferredVersions` 值

- **php**：仅主版本号和次版本号：`"7.4"`，`"8.0"`，`"8.1"`，`"8.2"`，`"8.3"`，`"8.4"`，`"8.5"` 或 `"latest"`。补丁版本如 `"7.4.1"` 是无效的。请查看模式以获取当前支持的版本。
- **wp**：最近的版本，`"latest"`，`"beta"`，`"nightly"`/`"trunk"`，或指向自定义 zip 的 URL。模式也接受 PHP 仅 Playground 的 `false`；不要将 `wp: false` 与 `plugins`、`siteOptions`、`login` 或仅 WordPress 步骤等 WordPress 仅字段组合。

### 简写与步骤

简写（`login`、`plugins`、`siteOptions`、`constants`）会被展开并添加到 `steps` 中，顺序**未指定**。当执行顺序很重要时，请使用显式步骤。

## 资源引用

资源告诉 Playground 在哪里找到文件。用于 `installPlugin`、`installTheme`、`writeFile`、`writeFiles`、`importWxr` 等。

| 资源类型 | 必需字段 | 示例 |
|--------------|----------------|---------|
| `wordpress.org/plugins` | `slug` | `{ "resource": "wordpress.org/plugins", "slug": "woocommerce" }` |
| `wordpress.org/themes` | `slug` | `{ "resource": "wordpress.org/themes", "slug": "astra" }` |
| `url` | `url` | `{ "resource": "url", "url": "https://example.com/plugin.zip" }` |
| `git:directory` | `url`, `ref` | 见下文 |
| `literal` | `name`, `contents` | `{ "resource": "literal", "name": "file.txt", "contents": "hello" }` |
| `literal:directory` | `name`, `files` | 见下文 |
| `bundled` | `path` | 引用蓝图包中的文件（例如 `{ "resource": "bundled", "path": "/plugin.zip" }`） |
| `zip` | `inner` | 将另一个资源包装在 ZIP 中——当步骤期望 ZIP 但您的源不是 ZIP 时使用（例如包装指向原始目录的 `url` 资源） |

### `git:directory` — 从 GitHub 安装

```json
{
  "resource": "git:directory",
  "url": "https://github.com/WordPress/gutenberg",
  "ref": "trunk",
  "refType": "branch",
  "path": "/"
}
```

- 使用分支或标签名作为 `ref` 时，您**必须**设置 `refType` (`"branch"` | `"tag"` | `"commit"` | `"refname"`)。没有它，只有 `"HEAD"` 可靠地解析。
- `path` 选择子目录（默认为仓库根目录）。

### `literal:directory` — 内联文件树

```json
{
  "resource": "literal:directory",
  "name": "my-plugin",
  "files": {
    "plugin.php": "<?php /* Plugin Name: My Plugin */ ?>",
    "includes": {
      "helper.php": "<?php // helper code }}"
  }
}
```

- `files` 使用嵌套对象表示子目录——键是文件名或目录名，值是**普通字符串**（文件内容）或**对象**（子目录）。**不要**在键中使用路径分隔符（例如 `"includes/helper.php"` 是错误的——使用嵌套的 `"includes": { "helper.php": "..." }` 对象）。

## 步骤参考

每个步骤都需要 `"step": "<name>"`。任何步骤都可以选择性地包含 `"progress": { "weight": 1, "caption": "Installing..." }` 以提供 UI 反馈。

### 插件和主题安装

```json
{
  "step": "installPlugin",
  "pluginData": { "resource": "wordpress.org/plugins", "slug": "gutenberg" },
  "options": { "activate": true, "targetFolderName": "gutenberg" },
  "ifAlreadyInstalled": "overwrite"
}
```

```json
{
  "step": "installTheme",
  "themeData": { "resource": "wordpress.org/themes", "slug": "twentytwentyfour" },
  "options": { "activate": true, "importStarterContent": true },
  "ifAlreadyInstalled": "overwrite"
}
```

- 使用 `pluginData` / `themeData` — **不是**已弃用的 `pluginZipFile` / `themeZipFile`。
- `pluginData` / `themeData` 接受任何 `FileReference` 或 `DirectoryReference` — 一个 zip URL、`wordpress.org/plugins` slugs、`git:directory` 或 `literal:directory`（不需要 `zip` 包装器）。
- `options.activate` 控制激活。使用 `installPlugin`/`installTheme` 时不需要单独的 `activatePlugin`/`activateTheme` 步骤。
- `ifAlreadyInstalled`: `"overwrite"` | `"skip"` | `"error"`。

### 激活（独立）

仅当插件/主题已存在于磁盘上时需要（例如，在 `writeFile`/`writeFiles` 之后）：

```json
{ "step": "activatePlugin", "pluginPath": "my-plugin/my-plugin.php" }
```
```json
{ "step": "activateTheme", "themeFolderName": "twentytwentyfour" }
```

### 文件操作

```json
{ "step": "writeFile", "path": "/wordpress/wp-content/mu-plugins/custom.php", "data": "<?php // code" }
```

`data` 接受一个普通字符串（如上所示）或资源引用（例如 `{ "resource": "url", "url": "https://..." }`）。

```json
{
  "step": "writeFiles",
  "writeToPath": "/wordpress/wp-content/plugins/",
  "filesTree": {
    "resource": "literal:directory",
    "name": "my-plugin",
    "files": {
      "plugin.php": "<?php\n/*\nPlugin Name: My Plugin\n*/",
      "includes": {
        "helpers.php": "<?php // helpers"
      }
    }
  }
}
```

**`writeFiles` 需要一个 `DirectoryReference`** (`literal:directory` 或 `git:directory`) 作为 `filesTree` — 不是普通对象。

其他文件操作：`mkdir`、`cp`、`mv`、`rm`、`rmdir`、`unzip`。

### 运行代码

**`runPHP`**:
```json
{ "step": "runPHP", "code": "<?php require '/wordpress/wp-load.php'; update_option('key', 'value');" }
```
**注意**：您必须 `require '/wordpress/wp-load.php';` 才能使用任何 WordPress 函数。

**`wp-cli`**:
```json
{ "step": "wp-cli", "command": "wp post create --post_type=page --post_title='Hello' --post_status=publish" }
```
步骤名称是 `wp-cli`（带连字符），**不是** `cli` 或 `wpcli`。

**`runSql`**:
```json
{ "step": "runSql", "sql": { "resource": "literal", "name": "q.sql", "contents": "UPDATE wp_options SET option_value='val' WHERE option_name='key';" } }
```

### 网站配置

```json
{ "step": "setSiteOptions", "options": { "blogname": "My Site", "blogdescription": "A tagline" } }
```
```json
{ "step": "defineWpConfigConsts", "consts": { "WP_DEBUG": true } }
```
```json
{ "step": "setSiteLanguage", "language": "en_US" }
```
```json
{ "step": "defineSiteUrl", "siteUrl": "https://example.com" }
```

### 其他步骤

| 步骤 | 键属性 |
|------|-------|
| `login` | `username?`, `password?`（默认 `"admin"` / `"password"`） |
| `enableMultisite` | (无必需属性) |
| `importWxr` | `file` (FileReference) |
| `importThemeStarterContent` | `themeSlug?` |
| `importWordPressFiles` | `wordPressFilesZip`, `pathInZip?` — 从 zip 导入完整的 WordPress 目录 |
| `request` | `request: { url, method?, headers?, body? }` |
| `updateUserMeta` | `userId`, `meta` |
| `runWpInstallationWizard` | `options?` — 使用给定选项运行 WP 安装向导 |
| `resetData` | (无属性) |

## 常见模式

### 内联 mu 插件（快速自定义代码）

```json
{
  "step": "writeFile",
  "path": "/wordpress/wp-content/mu-plugins/custom.php",
  "data": "<?php\n// mu-plugins 自动加载——无需激活，无需 require wp-load.php\nadd_filter('show_admin_bar', '__return_false');"
}
```

### 内联带多个文件的插件

```json
{
  "step": "writeFiles",
  "writeToPath": "/wordpress/wp-content/plugins/",
  "filesTree": {
    "resource": "literal:directory",
    "name": "my-plugin",
    "files": {
      "my-plugin.php": "<?php\n/*\nPlugin Name: My Plugin\n*/\nrequire __DIR__ . '/includes/main.php';",
      "includes": {
        "main.php": "<?php // main logic"
      }
    }
  }
}
```

然后使用单独的步骤激活它：

```json
{ "step": "activatePlugin", "pluginPath": "my-plugin/my-plugin.php" }
```

### 从 GitHub 分支获取插件

```json
{
  "step": "installPlugin",
  "pluginData": {
    "resource": "git:directory",
    "url": "https://github.com/user/repo",
    "ref": "feature-branch",
    "refType": "branch",
    "path": "/"
  }
}
```

## 常见错误

| 错误 | 正确 |
|---------|---------|
| `pluginZipFile` / `themeZipFile` | `pluginData` / `themeData` |
| `"step": "cli"` | `"step": "wp-cli"` |
| 平面对象作为 `writeFiles.filesTree` | 必须是 `literal:directory` 或 `git:directory` 资源 |
| `files` 键中的路径分隔符 | 使用嵌套对象表示子目录 |
| `runPHP` 而没有 `wp-load.php` | 总是 `require '/wordpress/wp-load.php';` 以使用 WP 函数 |
| 发明的顶层键 | 仅工作于文档中记录的键——模式会拒绝未知属性 |
| 发明 GitHub 代理 URL | 使用 `git:directory` 资源类型 |
| 忽略分支/标签 `ref` 时的 `refType` | 必需的——没有它，只有 `"HEAD"` 可靠地工作 |
| `literal:directory` `files` 值中的资源引用 | 值必须是普通字符串（内容）或对象（子目录）——从不使用资源引用 |
| `features.debug` 或其他发明的功能键 | `features` 仅支持 `networking` 和 `intl` — 使用 `constants: { "WP_DEBUG": true }` 用于调试模式 |
| mu 插件代码中的 `require wp-load.php` | 仅在 `runPHP` 步骤中需要——mu 插件已在 WordPress 内运行 |
| 模式 URL 中的 `.org` 域名 | 必须是 `playground.wordpress.net`，不是 `playground.wordpress.org` |

## 完整参考

本指南涵盖了最常见的步骤和模式。有关完整 API，请参阅：

- **蓝图文档**：https://wordpress.github.io/wordpress-playground/blueprints
- **JSON 模式**：https://playground.wordpress.net/blueprint-schema.json

上述未涵盖的附加步骤：`runPHPWithOptions`（使用自定义 `ini` 设置运行 PHP）、`runWpInstallationWizard`，以及资源类型 `vfs` 和 `bundled`（用于高级嵌入场景）。

## 蓝图包

包是自包含的包，包含 `blueprint.json` 以及它引用的所有资源（插件、主题、WXR 文件等）。而不是将资源外部托管，请将蓝图与资源一起打包。

### 包结构

```
my-bundle/
├── blueprint.json          ← 必须在根目录
├── my-plugin.zip           ← 打包的插件目录
├── theme.zip
└── content/
    └── sample-content.wxr
```

插件和主题在打包前必须打包——`installPlugin` 期望的是 zip，而不是原始目录。要从插件目录创建 zip：

```bash
cd my-bundle
zip -r my-plugin.zip my-plugin/
```

### 引用打包资源

使用 `bundled` 资源类型引用包内的文件：

```json
{
  "step": "installPlugin",
  "pluginData": {
    "resource": "bundled",
    "path": "/my-plugin.zip"
  },
  "options": { "activate": true }
}
```

```json
{
  "step": "importWxr",
  "file": {
    "resource": "bundled",
    "path": "/content/sample-content.wxr"
  }
}
```

### 逐步创建包

1. 创建包目录并在其根目录添加 `blueprint.json`。
2. 在子目录中编写您的插件/主题源文件（例如 `my-plugin/my-plugin.php`）。
3. 打包插件目录：`zip -r my-plugin.zip my-plugin/`
4. 在 `blueprint.json` 中使用 `{ "resource": "bundled", "path": "/my-plugin.zip" }` 引用它。

完整示例——一个安装自定义插件的包：

```
dashboard-widget-bundle/
├── blueprint.json
├── dashboard-widget.zip        ← dashboard-widget/ 的 zip
└── dashboard-widget/           ← 插件源（保留以供编辑）
    └── dashboard-widget.php
```

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "landingPage": "/wp-admin/",
  "preferredVersions": { "php": "8.3", "wp": "latest" },
  "steps": [
    { "step": "login" },
    {
      "step": "installPlugin",
      "pluginData": { "resource": "bundled", "path": "/dashboard-widget.zip" },
      "options": { "activate": true }
    }
  ]
}
```

### 分发格式

| 格式 | 如何使用 |
|--------|-----------|
| ZIP 文件（远程） | 网站：`https://playground.wordpress.net/?blueprint-url=https://example.com/bundle.zip` |
| ZIP 文件（本地） | CLI：`npx @wp-playground/cli server --blueprint=./bundle.zip` |
| 本地目录 | CLI：`npx @wp-playground/cli server --blueprint=./my-bundle/ --blueprint-may-read-adjacent-files` |
| Git 仓库目录 | 将 `blueprint-url` 指向包含 `blueprint.json` 的仓库目录 |

**注意**：本地目录包始终需要 `--blueprint-may-read-adjacent-files` 才能让 CLI 读取打包资源。没有它，任何 `"resource": "bundled"` 引用都会因“文件未找到”错误而失败。ZIP 包不需要这个标志——所有文件都包含在存档中。

## 测试蓝图

### 内联蓝图（快速测试，无包）

压缩蓝图 JSON（无额外空白），使用 `encodeURIComponent()` 编码一次，在浏览器中打开 URL 前缀 `https://playground.wordpress.net/#`：

```
https://playground.wordpress.net/#%7B%22%24schema%22%3A%22https%3A%2F%2Fplayground.wordpress.net%2Fblueprint-schema.json%22%2C%22preferredVersions%22%3A%7B%22php%22%3A%228.3%22%2C%22wp%22%3A%22latest%22%7D%2C%22steps%22%3A%5B%7B%22step%22%3A%22login%22%7D%5D%7D
```

非常大的蓝图可能会超出浏览器 URL 长度限制；使用 CLI 或托管蓝图 URL 代替。有关分享链接的详细信息，请使用 `wp-playground/references/website.md`。

### 本地 CLI 测试

**交互式服务器**（保持运行，在浏览器中打开）:
```bash
# 目录包 — 需要 --blueprint-may-read-adjacent-files
npx @wp-playground/cli server --blueprint=./my-bundle/ --blueprint-may-read-adjacent-files

# ZIP 包 — 自包含，无需额外标志
npx @wp-playground/cli server --blueprint=./bundle.zip
```

**无头验证**（运行蓝图并退出）:
```bash
npx @wp-playground/cli run-blueprint --blueprint=./my-bundle/ --blueprint-may-read-adjacent-files
```

### 使用 WordPress Playground 测试

使用 `wp-playground` 技能进行本地或浏览器测试。对于 CLI 测试，请遵循 `wp-playground/references/cli.md` 并使用 `--blueprint=<path-or-url>`；对于目录包，传递 `--blueprint-may-read-adjacent-files`。
