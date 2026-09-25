# 编写 Remotion 文档

文档位于 `packages/docs/docs` 目录下，以 `.mdx` 文件形式存储。

## 添加新页面

1. 在 `packages/docs/docs` 目录下创建一个新的 `.mdx` 文件
2. 将文档添加到 `packages/docs/sidebars.ts` 文件中
3. 按照以下指南编写内容
4. 在 `packages/docs` 目录下运行 `bun render-cards.ts` 以生成社交预览卡片

**面包屑 (`crumb`)**: 如果一个文档页面属于某个包，请在文档的前置内容中添加 `crumb: '@remotion/package-name'`。这将在标题上方显示包名称作为面包屑。

```md
---
image: /generated/articles-docs-my-package-my-api.png
title: '<MyComponent>'
crumb: '@remotion/my-package'
---
```

**每页一个 API**: 每个函数或 API 都应该有自己独立的文档页面。不要将多个 API（例如 `getEncodableVideoCodecs()` 和 `getEncodableAudioCodecs()`）合并到同一个页面。

**仅文档化公共 API**: 文档仅用于公共 API。不要提及、引用或与内部/私有 API 或实现细节进行比较。

**在正文中使用 API 名称**: 将 API 名称放在反引号中，如果存在对应的文档页面，请将其链接化。函数和钩子名称应包含 `()`，例如 [`useVideoConfig()`](/docs/use-video-config)，而不是 `useVideoConfig` 或 useVideoConfig。组件应包含尖括号，例如 [`<Player>`](/docs/player/player) 或 [`<Audio>`](/docs/media/audio)。

**使用标题表示所有字段**: 在文档化 API 选项或返回值时，每个属性都应为其自己的标题。使用 `###` 表示顶层属性，使用 `####` 表示选项对象中的嵌套属性。不要使用项目符号表示单个字段。

**版本指示器**: 如果某个 API、功能、参数或行为是在特定版本中添加的，请在读者首次需要了解该信息的地方添加 `<AvailableFrom>`。例如：`# prefetch()<AvailableFrom v="4.0.0" />`。

**兼容性表格**: API 页面最好包含一个 `## 兼容性` 部分并在 `## 参考文档` 之前使用 `<CompatibilityTable>`。

**侧边栏顺序**: 在添加或移动 `packages/docs/sidebars.ts` 中的文档时，检查周围的条目并匹配已使用的排序逻辑。如果某个部分是按字母顺序排列的，请按字母顺序放置新条目；如果它是按工作流程或重要性分组排列的，请与该分组一致地放置。不要让新的添加项成为孤立的例外。

## 语言指南

- **保持简洁**: 开发者不喜欢阅读。多余的词语会导致信息丢失。
- **链接到术语表**: 使用 [术语表](/docs/terminology) 页面来处理 Remotion 特有的术语。
- **不要加粗术语**: 将术语作为普通文本、代码跨度或链接来书写，根据需要使用。不要使用加粗格式来引入术语。
- **避免情绪化**: 删除填充词，如 "太棒了！让我们继续..." - 它不提供任何信息。
- **分段**: 将长段落拆分成多个段落。
- **使用 "你"**: 不要使用 "我们"。
- **不要责怪用户**: 说法 "输入无效" 而不是 "你提供了错误的输入"。
- **不要假设它很简单**: 避免使用 "简单地" 和 "只是" - 初学者可能会遇到困难。

## 代码片段

基本语法高亮：

````md
```ts
const x = 1;
```
````

### 类型安全的片段（推荐）

使用 `twoslash` 来检查 TypeScript 代码片段：

````md
```ts twoslash
import {useCurrentFrame} from 'remotion';
const frame = useCurrentFrame();
```
````

### 隐藏导入

使用 `// ---cut---` 来隐藏设置代码 - 只显示以下内容：

````md
```ts twoslash
import {useCurrentFrame} from 'remotion';
// ---cut---
const frame = useCurrentFrame();
```
````

### 添加标题

始终为显示示例用法的代码片段添加 `title`：

````md
```ts twoslash title="MyComponent.tsx"
console.log('Hello');
```
````

## 特殊组件

### 步骤

每行保持一个 `<Step>`，并在 `</Step>` 后面添加一个空格。当连续的步骤应该出现在单独的行上时，使用显式的换行符 (`<br/>` 或 `<br />`)。不要仅为了用 `<ul>` 包裹步骤而添加 Markdown 项目符号。

```md
<Step>1</Step> 第一步<br />
<Step>2</Step> 第二步
```

### 实验性徽章

```md
<ExperimentalBadge>
<p>此功能是实验性的。</p>
</ExperimentalBadge>
```

### 交互式演示

```md
<Demo type="rect"/>
```

演示必须在 `packages/docs/components/demos/index.tsx` 中实现。有关添加新演示的详细信息，请参阅 `docs-demo` 技能。

### AvailableFrom

用于指示功能或参数何时被添加。无需导入 - 它是全局可用的。

**对于页面级别的版本指示器**，使用一个 `# h1` 标题，并将 `<AvailableFrom>` 内联，以便它出现在标题旁边（而不是以下面）。使用 `&lt;` 和 `&gt;` 来转义组件名称中的尖括号：

```md
# &lt;MyComponent&gt;<AvailableFrom v="4.0.123" />
```

```md
# @remotion/my-package<AvailableFrom v="4.0.123" />
```

对于章节标题：

```md
## 保存到其他云<AvailableFrom v="3.2.23" />
```

### CompatibilityTable

用于指示组件或 API 支持哪些运行时和环境。无需导入。将其放置在 `## 兼容性` 部分中，并在 `## 参考文档` 之前。

可用的布尔属性：`chrome`、`firefox`、`safari`、`player`、`studio`、`clientSideRendering`、`serverSideRendering`。设置为 `true`（支持）或 `{false}`（不支持）。

对于前端 API，设置为空字符串 `""`：`nodejs=""`、`bun=""`、`serverlessFunctions=""`。
使用 `hideServers` 来隐藏 Node.js/Bun/serverless 行，如果这是前端 API。

```md
## 兼容性

<CompatibilityTable chrome firefox safari nodejs="" bun="" serverlessFunctions="" clientSideRendering={false} serverSideRendering player studio hideServers />
```

### 可选参数

在 API 文档中为可选参数：

1. **在标题中添加 `?`** - 这表示参数是可选的
   --> 如果它是 CLI 标志（以 `--` 开头） - CLI 标志总是可选的 - 不要这样做
2. **不要添加 `_optional_` 文本** - `?` 后缀就足够了
3. **在描述中包含默认值** - 自然地提及它

```md
### onError?

当发生错误时被调用。默认：抛出错误。
```

**不要这样做：**

```md
### onError?

_optional_

当发生错误时被调用。
```

### 结合可选和 AvailableFrom

当参数既是可选的，又是在特定版本中添加的：

```md
### onError?<AvailableFrom v="4.0.50" />

当发生错误时被调用。
```

### "可选自"模式

如果参数在特定版本中变为可选（以前是必需的）：

```md
### codec?

可选自 <AvailableFrom v="5.0.0" inline />。以前是必需的。
```

## 生成预览卡片

添加或编辑页面后，生成社交媒体预览卡片：

```bash
cd packages/docs && bun render-cards.ts
```

## 简化现有文档

在要求审核或简化文档时，扫描以下内容：

- 缺少 `<AvailableFrom>` 指示器的 API、功能、选项、参数或行为，这些是在特定版本中引入的
- 未按代码跨度格式化或链接到其文档页面的 API 名称
- 缺少 `()` 的函数和钩子引用
- 应该包含 `## 兼容性` 部分和 `<CompatibilityTable>` 的 API 页面
- 易碎或损坏的 `<Step>` 格式
