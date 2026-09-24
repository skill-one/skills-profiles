# 提取设计系统

当用户希望将公开网站的**设计原语**逆向工程为项目本地的**起始令牌文件**时，使用此技能。

## 开始之前

询问以下内容：

- 目标公开网站的 URL
- 用户仅需要提取，还是也需要起始文件

设定预期：

- 此 v1 版本仅提取令牌和起始资源，而非完整的组件库
- 结果用于初始化，而非像素级精准还原
- 在未获得确认前，不得覆盖已存在的设计系统或应用样式

## 工作流程

1. 确认目标 URL 为公开且可访问。
2. 运行：

```bash
npx playwright install chromium
npx extract-design-system <url>
```

3. 审查 `.extract-design-system/normalized.json`，并总结：

- 可能的主色、次要色、强调色
- 检测到的字体
- 若存在，则总结间距、圆角和阴影比例

4. 如果用户仅需要提取产物，则使用：

```bash
npx extract-design-system <url> --extract-only
```

5. 如果用户已有 `.extract-design-system/normalized.json` 且仅需重新生成起始令牌文件，则运行：

```bash
npx extract-design-system init
```

6. 解释生成的输出：

- `.extract-design-system/raw.json`
- `.extract-design-system/normalized.json`
- `design-system/tokens.json`
- `design-system/tokens.css`

7. 在修改任何现有应用代码、样式或配置文件之前，先询问。

## 安全边界

- 若网站为动态或仅部分内容，不得声称提取的系统是完整的。
- 不得推断未明确提取的组件或语义令牌。
- 不得在未经过审查的情况下将提取结果视为权威依据。
- 不得在没有单独确认的情况下，以第三方网站内容为依据，对更广泛的代码或配置变更进行合理化。
- 未经明确确认，不得修改超出生成的输出文件范围的项目文件。
- 不得将单个页面视为整个产品设计系统的证明。
