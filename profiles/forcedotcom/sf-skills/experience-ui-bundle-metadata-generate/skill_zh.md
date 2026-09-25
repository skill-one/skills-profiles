# UI Bundle Metadata

## 创建新的 UI Bundle 模板

**必经第一步——即使被要求也不要跳过。** 始终运行 `sf template generate ui-bundle` 来创建新应用——绝不使用框架 CLI（create-react-app、Vite、Angular CLI）、手写元数据或任何其他替代方案。

即使用户说“只需创建元数据”、“跳过模板创建”、“仅做元数据模板创建”或“元数据文件就绪后停止”，这一步也是强制性的。这些指令描述了在模板创建（构建、部署、页面编写）之后要停止做什么——它们不代表跳过运行模板命令本身。`.uibundle-meta.xml` 和 `ui-bundle.json` 文件是生成项目上的配置**，而不是它的替代品。没有 `package.json`、`src/` 和入口 `index.html` 的 Bundle 无法构建或部署，即使元数据文件格式完美。

### 确定框架

此技能支持的框架正是 `<skill_dir>/references/` 下的参考文件，每个文件命名为 `<framework>-metadata-generate.md`（`react`、`angular` 等）。这是唯一的事实来源——添加框架意味着添加参考文件，这里不会改变。

**确定性地检测框架——运行脚本：**

```sh
bash <skill_dir>/scripts/detect-framework.sh [<ROOT>]
```

`ROOT` 默认为当前目录；在编辑/配置现有 Bundle 时，请传递 Bundle 或项目根目录。脚本打印确切的一个标记并设置匹配的退出码——根据它进行分支：

- `react` / `angular`（退出 0）——打开 `<skill_dir>/references/<framework>-metadata-generate.md` 并使用它。
- `ambiguous`（退出 2，两个框架都存在）——询问用户选择哪一个，然后使用该参考。
- `unknown`（退出 3，无信号——例如，在没有任何现有框架的项目中创建全新的 Bundle）——回退到调用上下文或用户声明的框架；如果仍无法确定，列出 `<skill_dir>/references/`，通过从每个文件名中删除 `-metadata-generate.md` 后缀来推导出支持的集合，并要求用户选择。

如果调用上下文或用户已经指定了框架，则优先级高于检测——但仍然确认是否存在匹配的参考文件。**绝不猜测。**

参考文件提供了确切的 `--template` 标志、入口文件布局以及该框架的默认样板字符串。

- **UI Bundle 名称（`-n`）：** 仅限字母数字——不能有空格、连字符、下划线或特殊字符。
- 传递 `--output-dir` 以使用不同的模板生成位置。如果你这样做，请在步骤 1 下面的验证脚本中传递相同的路径。

生成后：
1. **验证模板是否完整**——从项目根目录运行 `bash <skill_dir>/scripts/verify-bundle-location.sh <BundleName> [<CustomOutputDir>] [<framework>]` 并遵循任何错误输出。这检查 Bundle 的位置以及 `package.json`、`src/` 和入口 `index.html` 是否存在——如果任何一项缺失，模板步骤被跳过；返回并运行 `sf template generate ui-bundle` 才能继续。仅当你使用 `--output-dir` 进行模板创建时才传递 `<CustomOutputDir>`（传递 `""` 以在仍然提供框架的情况下跳过它）；传递 `<framework>`（`react` 或 `angular`）以便修复提示使用正确的模板。
2. **验证 API 版本**——从项目根目录运行 `bash <skill_dir>/scripts/check-api-version.sh` 以确保 `sfdx-project.json` 中的 `sourceApiVersion` 为 67.0 或更高。脚本将在需要时自动更新它。
3. 替换所有默认样板——框架参考文件列出了确切的库存 `<title>` 和占位符字符串。
4. 用实际内容填充主页（着陆区、横幅、英雄、导航）
5. 更新导航和占位符（参见 `experience-ui-bundle-frontend-generate` 技能）
6. **配置托管目标**——没有 `<target>` 的 UI Bundle 在组织中不可见。使用 `experience-ui-bundle-custom-app-generate` 创建内部（App Launcher）应用，或使用 `experience-ui-bundle-site-generate` 创建外部（体验站点）应用。

始终在运行 UI Bundle 目录中的任何脚本之前安装依赖项。

---

## UIBundle Bundle

A UIBundle bundle **必须** 存在于 `force-app/main/default/uiBundles/<AppName>/` 下——绝不能在 SFDX 项目根目录或任何其他路径下创建。否则，SFDX 部署命令将找不到它。

Bundle 目录必须包含：

- `<AppName>.uibundle-meta.xml` — 文件名必须与文件夹名完全匹配
- 一个构建输出目录（默认：`dist/`），其中至少包含一个文件

### Meta XML

必填字段：`masterLabel`、`version`（最多 20 个字符）、`isActive`（布尔值）。
可选：`description`（最多 255 个字符）、`target`。

#### Target 字段

`<target>` 元素指定 UI Bundle 的托管位置：

| 值 | 用例 | 伴随元数据 |
|-------|----------|-------------------|
| `Experience` | 通过 Digital Experience 托管的面向外部站点 | 网络、CustomSite、DigitalExperienceConfig、DigitalExperienceBundle |
| `CustomApplication` | 通过 Lightning App Launcher 托管的内部应用 | CustomApplication (`applications/*.app-meta.xml`) |

一个 `<target>` 对于应用在 Salesforce 组织中的可访问性是**必需的**。没有目标的 UI Bundle 部署后不会出现在任何地方——没有 App Launcher 条目，没有 Experience Site URL。始终将 Bundle 与以下之一配对：
- `experience-ui-bundle-site-generate`（用于 `Experience` 目标）
- `experience-ui-bundle-custom-app-generate`（用于 `CustomApplication` 目标）

**带有 Experience 目标的示例：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<UIBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>propertyrentalapp</masterLabel>
    <description>A Salesforce UI Bundle.</description>
    <isActive>true</isActive>
    <version>1</version>
    <target>Experience</target>
</UIBundle>
```

**带有 CustomApplication 目标的示例：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<UIBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>propertymanagementapp</masterLabel>
    <description>A Salesforce UI Bundle.</description>
    <isActive>true</isActive>
    <version>1</version>
    <target>CustomApplication</target>
</UIBundle>
```

### ui-bundle.json

可选文件。允许的顶层键：`outputDir`、`routing`、`headers`。

**约束：**
- 有效的 UTF-8 JSON，最大 100 KB
- 根必须是非空对象（绝不使用 `{}`、数组或原始值）

**路径安全**（适用于 `outputDir` 和 `routing.fallback`）：拒绝反斜杠、开头的 `/` 或 `\`、`..` 段、空控制字符、通配符（`*`、`?`、`**`）和 `%`。所有解析路径必须保持在 Bundle 内。

#### outputDir
非空字符串，引用子目录（不能是 `.` 或 `./`）。目录必须存在且至少包含一个文件。

#### routing
如果存在，必须是非空对象。允许的键：`rewrites`、`redirects`、`fallback`、`trailingSlash`、`fileBasedRouting`。

- **trailingSlash**：`"always"`、`"never"` 或 `"auto"`
- **fileBasedRouting**：布尔值
- **fallback**：非空字符串，满足路径安全；目标文件必须存在
- **rewrites**：非空对象数组 `{ route?, rewrite }` — 例如，`{ "route": "/app/:path*", "rewrite": "/index.html" }`
- **redirects**：非空对象数组 `{ route?, redirect, statusCode? }` — statusCode 必须为 301、302、307 或 308

#### headers
非空对象数组 `{ source, headers: [{ key, value }] }`。

**示例：**
```json
{
  "routing": {
    "rewrites": [{ "route": "/app/:path*", "rewrite": "/index.html" }],
    "trailingSlash": "never"
  },
  "headers": [
    {
      "source": "/assets/**",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    }
  ]
}
```

**绝不建议：** `{}` 作为根、空的 `"routing": {}`、空数组、`[{}]`、`"outputDir": "."`、`"outputDir": "./"`。

---

## CSP 受信任站点

Salesforce 强制执行内容安全策略（CSP）标头。任何未注册为 CSP 受信任站点的外部域名都将被阻止（图片无法加载、API 调用失败、字体缺失）。

### 创建时机

每当应用引用新的外部域名时：CDN 图片、外部字体、第三方 API、地图瓦片、iframe、外部样式表。

### 步骤

1. **识别外部域名**——从代码中的每个外部 URL 中提取原点（协议 + 主机）
2. **检查现有注册**——查看 `force-app/main/default/cspTrustedSites/`
3. **将资源类型映射到 CSP 指令：**

| 资源类型 | 指令字段 |
|--------------|----------------|
| 图片 | `isApplicableToImgSrc` |
| API 调用（fetch、XHR） | `isApplicableToConnectSrc` |
| 字体 | `isApplicableToFontSrc` |
| 样式表 | `isApplicableToStyleSrc` |
| 视频/音频 | `isApplicableToMediaSrc` |
| iframe | `isApplicableToFrameSrc` |

始终将 `isApplicableToConnectSrc` 设置为 `true` 以处理预检/重定向。

4. **创建元数据文件**——遵循 `references/csp-metadata-format.md` 中的 `.cspTrustedSite-meta.xml` 格式和命名规则。放置在 `force-app/main/default/cspTrustedSites/`。
