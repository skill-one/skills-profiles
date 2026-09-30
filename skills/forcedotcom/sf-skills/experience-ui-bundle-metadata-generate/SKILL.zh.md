---
name: experience-ui-bundle-metadata-generate
description: 在将前端 React UI 打包添加到现有项目或配置 UI 打包元数据和配置文件时使用此技能。触发条件为：在已存在的项目中添加或搭建新的 UI 打包；运行 `sf template generate ui-bundle`；编辑 `ui-bundle.json` 中的路由、标题或输出目录；处理 `*.uibundle-meta.xml` 文件；注册 CSP 受信任站点、解决被阻止的图像或字体或外部 API 调用；或编辑 `cspTrustedSites/*.cspTrustedSite-meta.xml` 文件。不触发条件为：从零创建全新的 Salesforce 项目，此时整个 SFDX 启动项目（包括 UI 打包、体验站点元数据和工具链）会一起生成（应使用 `experience-ui-bundle-project-generate`）。
---

# UI Bundle Metadata

## 新建 UI Bundle 模板

**第一步（必选）—— 即使被要求跳过，也绝对不能跳过。** 始终运行 `sf template generate ui-bundle` 来创建新应用——绝不使用 create-react-app、Vite、手写元数据或任何其他替代方案。

即使用户说“只需创建元数据”、“跳过模板”、“仅做元数据模板”或“元数据文件就绪后停止”，这一步也是强制性的。这些说明描述了在模板（构建、部署、编写页面）之后要停止做什么——它们并不意味着跳过运行模板命令本身。`.uibundle-meta.xml` 和 `ui-bundle.json` 文件是生成项目的**顶层**配置，而不是它的替代品。没有 `package.json`、`src/` 和 `index.html` 的 Bundle 无法构建或部署，即使元数据文件格式完美。

- **始终传递 `--template reactbasic`** 来创建基于 React 的 Bundle。
- **UI Bundle 名称 (`-n`):** 仅限字母数字——不能有空格、连字符、下划线或特殊字符。
- 传递 `--output-dir` 来使用不同的模板生成位置。如果你这样做，请在下面步骤 1 中将相同路径传递给验证脚本。

**示例：**
```bash
# 从 SFDX 项目根目录运行。CLI 将在 force-app/main/default/uiBundles/<AppName>/ 下创建 Bundle——继续之前请验证此路径。
sf template generate ui-bundle -n CoffeeBoutique --template reactbasic
```

生成后：
1. **验证模板是否完整**——从项目根目录运行 `bash <skill_dir>/scripts/verify-bundle-location.sh <BundleName> [<CustomOutputDir>]` 并遵循任何错误输出。这检查 Bundle 的位置以及 `package.json`、`src/` 和 `index.html` 是否存在——如果任何一项缺失，模板步骤被跳过了；返回并运行 `sf template generate ui-bundle` 再继续。仅当你使用 `--output-dir` 进行模板生成时才传递 `<CustomOutputDir>`；否则省略它。
2. **验证 API 版本**——从项目根目录运行 `bash <skill_dir>/scripts/check-api-version.sh` 以确保 `sfdx-project.json` 中的 `sourceApiVersion` 是 67.0 或更高。如果需要，脚本将自动更新它。
3. 替换所有默认的样板代码——"React App"、"Vite + React"、默认 `<title>`、占位符文本
4. 用真实内容填充主页（着陆区、横幅、英雄图、导航）
5. 更新导航和占位符（参见 `experience-ui-bundle-frontend-generate` 技能）
6. **配置托管目标**——没有 `<target>` 的 UI Bundle 元 XML 中的 Bundle 在组织中不可见。使用 `experience-ui-bundle-custom-app-generate` 为内部（App Launcher）应用，或使用 `experience-ui-bundle-site-generate` 为外部（体验站点）应用。

始终在运行 UI Bundle 目录中的任何脚本之前安装依赖项。

---

## UIBundle Bundle

UIBundle Bundle **必须**位于 `force-app/main/default/uiBundles/<AppName>/` 下——绝不能在 SFDX 项目根目录或任何其他路径下创建。否则 SFDX 部署命令将找不到它。

Bundle 目录必须包含：

- `<AppName>.uibundle-meta.xml` — 文件名必须与文件夹名完全匹配
- 一个构建输出目录（默认：`dist/`）且至少包含一个文件

### Meta XML

必需字段：`masterLabel`、`version`（最多 20 个字符）、`isActive`（布尔值）。
可选：`description`（最多 255 个字符）、`target`。

#### Target 字段

`<target>` 元素指定 UI Bundle 的托管位置：

| 值 | 用例 | 伴随元数据 |
|-------|----------|-------------------|
| `Experience` | 通过 Digital Experience 托管的面向外部站点 | Network、CustomSite、DigitalExperienceConfig、DigitalExperienceBundle |
| `CustomApplication` | 通过 Lightning App Launcher 托管的内部应用 | CustomApplication (`applications/*.app-meta.xml`) |

一个 `<target>` 对于应用在 Salesforce 组织中的可访问性是**必需**的。没有目标的 UI Bundle 部署后不会出现在任何地方——没有 App Launcher 条目，没有 Experience Site URL。始终将 Bundle 与以下之一配对：
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
- 根必须是非空对象（绝不可能是 `{}`、数组或原始值）

**路径安全**（适用于 `outputDir` 和 `routing.fallback`）：拒绝反斜杠、开头的 `/` 或 `\`、`..` 段、空控制字符、通配符（`*`、`?`、`**`）和 `%`。所有解析路径必须保持在 Bundle 内。

#### outputDir
非空字符串，引用子目录（不能是 `.` 或 `./`）。目录必须存在且至少包含一个文件。

#### routing
如果存在，必须是非空对象。允许的键：`rewrites`、`redirects`、`fallback`、`trailingSlash`、`fileBasedRouting`。

- **trailingSlash**: `"always"`、`"never"` 或 `"auto"`
- **fileBasedRouting**: 布尔值
- **fallback**: 非空字符串满足路径安全；目标文件必须存在
- **rewrites**: 非空对象 `{ route?, rewrite }` 数组——例如，`{ "route": "/app/:path*", "rewrite": "/index.html" }`
- **redirects**: 非空对象 `{ route?, redirect, statusCode? }` 数组——statusCode 必须是 301、302、307 或 308

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

Salesforce 强制执行内容安全策略（CSP）标头。任何未注册为 CSP 受信任站点的外部域名将被阻止（图片无法加载、API 调用失败、字体丢失）。

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
| 视频 / 音频 | `isApplicableToMediaSrc` |
| iframe | `isApplicableToFrameSrc` |

始终也将 `isApplicableToConnectSrc` 设置为 `true` 以处理预检/重定向。

4. **创建元数据文件**——遵循 `references/csp-metadata-format.md` 中 `.cspTrustedSite-meta.xml` 的格式和命名规则。放置在 `force-app/main/default/cspTrustedSites/`。
