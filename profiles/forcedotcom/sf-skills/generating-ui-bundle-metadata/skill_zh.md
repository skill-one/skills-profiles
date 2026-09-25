# UI Bundle Metadata

## 创建新的 UI Bundle

使用 `sf template generate ui-bundle` 命令创建新应用——不是 create-react-app、Vite 或其他通用脚手架。

**始终传递 `--template reactbasic**` 来创建基于 React 的 bundle。

**UI bundle 名称 (`-n`):** 仅允许字母数字——不能包含空格、连字符、下划线或特殊字符。

**示例:**
```bash
sf template generate ui-bundle -n CoffeeBoutique --template reactbasic
```

生成后：
1. 替换所有默认的样板代码——"React App"、"Vite + React"、默认 `<title>`、占位符文本
2. 用实际内容填充主页（着陆区域、横幅、英雄区域、导航）
3. 更新导航和占位符（参考 `building-ui-bundle-frontend` 技能）
4. **配置托管目标**——没有在元 XML 中指定 `<target>` 的 UI bundle 将不会在组织中可见。使用 `generating-ui-bundle-custom-app` 创建内部（App Launcher）应用，或使用 `generating-ui-bundle-site` 创建外部（体验站点）应用。

始终在运行 UI bundle 目录中的任何脚本之前安装依赖项。

---

## UIBundle Bundle

UIBundle bundle 存放在 `uiBundles/<AppName>/` 下，并且必须包含：

- `<AppName>.uibundle-meta.xml` — 文件名必须与文件夹名称完全匹配
- 一个构建输出目录（默认：`dist/`），其中至少包含一个文件

### 元 XML

必需字段：`masterLabel`、`version`（最大 20 个字符）、`isActive`（布尔值）。
可选：`description`（最大 255 个字符）、`target`。

#### Target 字段

`<target>` 元素指定 UI bundle 的托管位置：

| 值 | 用例 | 伴随元数据 |
|-------|----------|-------------------|
| `Experience` | 通过 Digital Experience 托管的对外网站 | Network、CustomSite、DigitalExperienceConfig、DigitalExperienceBundle |
| `CustomApplication` | 通过 Lightning App Launcher 托管的内部应用 | CustomApplication (`applications/*.app-meta.xml`) |

一个 `<target>` 对于应用在 Salesforce 组织中的可见性是**必需的**。没有指定目标的 UI bundle 部署后不会出现在任何地方——没有 App Launcher 条目，没有体验站点 URL。始终将 bundle 与以下之一配对：
- `generating-ui-bundle-site`（用于 `Experience` 目标）
- `generating-ui-bundle-custom-app`（用于 `CustomApplication` 目标）

**带有 Experience 目标的示例:**
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

**带有 CustomApplication 目标的示例:**
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

**约束条件:**
- 有效的 UTF-8 JSON，最大 100 KB
- 根必须是非空对象（永远不会是 `{}`、数组或原始值）

**路径安全**（适用于 `outputDir` 和 `routing.fallback`）：拒绝反斜杠、开头的 `/` 或 `\`、`..` 段、空控制字符、通配符（`*`、`?`、`**`）和 `%`。所有解析路径必须保持在 bundle 内部。

#### outputDir
非空字符串，引用子目录（不能是 `.` 或 `./`）。目录必须存在并且至少包含一个文件。

#### routing
如果存在，必须是非空对象。允许的键：`rewrites`、`redirects`、`fallback`、`trailingSlash`、`fileBasedRouting`。

- **trailingSlash**: `"always"`、`"never"` 或 `"auto"`
- **fileBasedRouting**: 布尔值
- **fallback**: 非空字符串满足路径安全；目标文件必须存在
- **rewrites**: 非空对象数组 `{ route?, rewrite }` — 例如，`{ "route": "/app/:path*", "rewrite": "/index.html" }`
- **redirects**: 非空对象数组 `{ route?, redirect, statusCode? }` — statusCode 必须是 301、302、307 或 308

#### headers
非空对象数组 `{ source, headers: [{ key, value }] }`。

**示例:**
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

**永远不要建议：** `{}` 作为根、空的 `"routing": {}`、空数组、`[{}]`、`"outputDir": "."`、`"outputDir": "./"`。

---

## CSP 受信任站点

Salesforce 强制执行内容安全策略 (CSP) 标头。任何未注册为 CSP 受信任站点的外部域名都将被阻止（图片无法加载、API 调用失败、字体缺失）。

### 创建时机

每当应用引用新的外部域名时：CDN 图片、外部字体、第三方 API、地图瓦片、iframe、外部样式表。

### 步骤

1. **识别外部域名** — 从代码中的每个外部 URL 中提取原点（协议 + 主机）
2. **检查现有注册** — 查看 `force-app/main/default/cspTrustedSites/`
3. **将资源类型映射到 CSP 指令：**

| 资源类型 | 指令字段 |
|--------------|----------------|
| 图片 | `isApplicableToImgSrc` |
| API 调用 (fetch, XHR) | `isApplicableToConnectSrc` |
| 字体 | `isApplicableToFontSrc` |
| 样式表 | `isApplicableToStyleSrc` |
| 视频/音频 | `isApplicableToMediaSrc` |
| iframe | `isApplicableToFrameSrc` |

始终将 `isApplicableToConnectSrc` 设置为 `true` 以处理预检/重定向。

4. **创建元数据文件** — 按照 `implementation/csp-metadata-format.md` 的 `.cspTrustedSite-meta.xml` 格式。放置在 `force-app/main/default/cspTrustedSites/`。
