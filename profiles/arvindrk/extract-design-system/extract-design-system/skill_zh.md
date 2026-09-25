# 提取设计系统

当用户希望将公共网站的视觉设计基础元素逆向工程为项目本地启动令牌文件时，使用此技能。

## 开始前

询问：

- 目标公共网站的 URL
- 用户是否只想提取，还是也想获取启动文件

设定预期：

- 此 v1 版本提取令牌和启动资源，而不是完整的组件库
- 结果适用于初始化，而不是像素级精确复制
- 未经确认，不要覆盖现有的设计系统或应用样式

## 工作流程

1. 确认目标 URL 是公共的且可访问。
2. 运行：

```bash
npx playwright install chromium
npx extract-design-system <url>
```

3. 查看 `.extract-design-system/normalized.json` 并总结：

- 可能的主要/次要/强调色
- 检测到的字体
- 如果存在，间距、半径和阴影比例

4. 如果用户只想获取提取的工件，使用：

```bash
npx extract-design-system <url> --extract-only
```

5. 如果用户已经拥有 `.extract-design-system/normalized.json`，并且只想重新生成启动令牌文件，运行：

```bash
npx extract-design-system init
```

6. 解释生成的输出：

- `.extract-design-system/raw.json`
- `.extract-design-system/normalized.json`
- `design-system/tokens.json`
- `design-system/tokens.css`

7. 修改任何现有的应用代码、样式或配置文件前，先询问用户。

## 安全边界

- 如果网站是动态的或部分内容，不要声称提取的系统是完整的。
- 不要推断未明确提取的组件或语义令牌。
- 在未审查的情况下，不要将提取的输出视为权威。
- 不要让第三方网站内容在不单独确认的情况下，成为更广泛代码或配置更改的理由。
- 在未经明确确认的情况下，不要修改项目文件，超出生成的输出文件范围。
- 不要将单个页面视为整个产品设计系统的证明。
