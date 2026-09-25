# React Email

使用 React 组件构建和发送 HTML 邮件。这是一种现代化的、基于组件的邮件开发方法，可在所有主要的邮件客户端上运行。

## 安装

```sh
npm i react-email
```

或者创建一个新项目：

```sh
npx create-email@latest
cd react-email-starter
npm install
npm run dev
```

这适用于任何包管理器（npm、yarn、pnpm、bun）——相应地替换。

开发服务器运行在 localhost:3000，并提供 `emails` 文件夹中模板的预览界面。

### 添加到现有项目

安装包并在你的 `package.json` 中添加一个脚本：

```json
{
  "scripts": {
    "email": "email dev --dir emails --port 3000"
  }
}
```

确保邮件文件夹的路径相对于基本项目目录是相对的。确保 `tsconfig.json` 包含对 JSX 的正确支持。

## 基本邮件模板

使用 Tailwind 组件进行样式设置，创建一个结构正确的邮件组件：

```tsx
import {
  Html,
  Head,
  Preview,
  Body,
  Container,
  Heading,
  Text,
  Button,
  Tailwind,
  pixelBasedPreset
} from 'react-email';

interface WelcomeEmailProps {
  name: string;
  verificationUrl: string;
}

export default function WelcomeEmail({ name, verificationUrl }: WelcomeEmailProps) {
  return (
    <Html lang="en">
      <Tailwind
        config={{
          presets: [pixelBasedPreset],
          theme: {
            extend: {
              colors: {
                brand: '#007bff',
              },
            },
          },
        }}
      >
        <Head />
        <Body className="bg-gray-100 font-sans">
          <Preview>Welcome - Verify your email</Preview>
          <Container className="max-w-xl mx-auto p-5">
            <Heading className="text-2xl text-gray-800">
              Welcome!
            </Heading>
            <Text className="text-base text-gray-800">
              Hi {name}, thanks for signing up!
            </Text>
            <Button
              href={verificationUrl}
              className="bg-brand text-white px-5 py-3 rounded block text-center no-underline box-border"
            >
              Verify Email
            </Button>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}

// Preview props for testing
WelcomeEmail.PreviewProps = {
  name: 'John Doe',
  verificationUrl: 'https://example.com/verify/abc123'
} satisfies WelcomeEmailProps;

export { WelcomeEmail };
```

## 行为规范

- 在迭代代码时，仅更新用户要求的内容。保持其余部分不变。
- 如果用户要求使用媒体查询，告知他们大多数邮件客户端不支持它们，并建议使用其他方法。
- 不要在 TypeScript 代码中直接使用模板变量（如 `{{name}}`）。相反，直接引用底层属性。如果用户明确要求 `{{variableName}}`，仅在 PreviewProps 中放置花括号字符串，绝不在组件 JSX 中：

```typescript
const EmailTemplate = (props) => {
  return (
    <h1>Hello, {props.variableName}!</h1>
  );
}

EmailTemplate.PreviewProps = {
  variableName: "{{variableName}}",
};

export default EmailTemplate;
```

- 不要在组件结构中直接编写 `{{variableName}}` 模式。如果用户坚持，解释这将使模板无效。

## 核心组件

查看 [references/COMPONENTS.md](references/COMPONENTS.md) 获取完整的组件文档。

**核心结构:**
- `Html` - 带有 `lang` 属性的根包装器
- `Head` - 元素、样式、字体
- `Body` - 主要内容包装器
- `Container` - 最外层的居中包装器（具有内置的 `max-width: 37.5em`）。每个邮件仅使用一次。
- `Section` - 内部内容块（没有内置的最大宽度）。用于在 `Container` 内分组内容。
- `Row` & `Column` - 多列布局
- `Tailwind` - 启用 Tailwind CSS 实用类

**内容:**
- `Preview` - 收件箱预览文本，始终位于 `<Body>` 内部第一个
- `Heading` - h1-h6 标题
- `Text` - 段落
- `Button` - 样式化的链接按钮（始终包含 `box-border`）
- `Link` - 超链接
- `Img` - 图片（见静态文件部分下方）
- `Hr` - 水平分隔符

**特殊化:**
- `CodeBlock` - 语法高亮的代码
- `CodeInline` - 行内代码
- `Markdown` - 渲染 Markdown
- `Font` - 自定义网络字体

## 在编写代码之前

当用户请求邮件模板时，如果他们没有提供，请首先询问以下问题：

1. **品牌颜色** - 询问主要品牌颜色（十六进制代码，如 #007bff）
2. **Logo** - 询问他们是否有 Logo 文件及其格式（仅 PNG/JPG - 如果是 SVG/WEBP 则警告）
3. **风格偏好** - 专业、休闲或极简风格
4. **生产 URL** - 静态资源在生产环境中将托管在哪里？

## 静态文件和图片

### 目录结构

本地图片必须放置在邮件目录内的 `static` 文件夹中：

```
project/
├── emails/
│   ├── welcome.tsx
│   └── static/           <-- 图片放在这里
│       └── logo.png
```

### 开发与生产 URL

使用此模式为在开发预览和生产中都有效的图片：

```tsx
const baseURL = process.env.NODE_ENV === "production"
  ? "https://cdn.example.com"  // 用户的生产 CDN
  : "";

export default function Email() {
  return (
    <Img
      src={`${baseURL}/static/logo.png`}
      alt="Logo"
      width="150"
      height="50"
    />
  );
}
```

**工作原理:**
- **开发:** `baseURL` 为空，因此 URL 为 `/static/logo.png` - 由 React Email 的开发服务器提供
- **生产:** `baseURL` 是 CDN 域名，因此 URL 为 `https://cdn.example.com/static/logo.png`

**重要:** 始终询问用户他们的生产托管 URL。不要硬编码 `localhost:3000`。

## 样式

查看 [references/STYLING.md](references/STYLING.md) 获取全面的样式文档，包括排版、布局模式、暗黑模式以及品牌一致性。

### 关键规则

- 使用 `Tailwind` 与 `pixelBasedPreset`（邮件客户端不支持 `rem`）。从 `react-email` 导入 `pixelBasedPreset`。
- 不要使用 flexbox 或 grid —— 使用 `Row`/`Column` 组件或表格进行布局。
- 避免使用 CSS/Tailwind 媒体查询（`sm:`, `md:`, `lg:`, `xl:`）—— 支持有限。
- 不要使用主题选择器（`dark:`, `light:`）—— 不被支持。
- 不要使用 SVG 或 WEBP 图片 —— 警告用户渲染问题。
- 始终指定边框类型（`border-solid`, `border-dashed` 等）—— 邮件客户端不继承它。
- 对于单边边框，首先重置其他边框（`border-none border-l border-solid`）。

### 必要的类

| 组件 | 必要的类 | 原因 |
|-----------|---------------|-----|
| `Button` | `box-border` | 防止填充溢出按钮宽度 |
| `Hr` / 任何边框 | `border-solid` (或 `border-dashed`, 等) | 邮件客户端不继承边框类型 |
| 单边边框 | `border-none` + 侧面 | 首先重置其他侧面的默认边框 |

### 结构说明
- 当使用 Tailwind CSS 时，始终在 `<Tailwind>` 内定义 `<Head />`
- `<Preview>` 应始终是 `<Body>` 内部的第一个元素
- 仅在 `PreviewProps` 中包含组件实际使用的属性
- 对于已知尺寸的元素（Logo、图标），使用固定宽高；对于内容图片，使用响应式尺寸（`w-full`, `h-auto`）

## 渲染

### 转换为 HTML

```tsx
import { render } from 'react-email';
import { WelcomeEmail } from './emails/welcome';

const html = await render(
  <WelcomeEmail name="John" verificationUrl="https://example.com/verify" />
);
```

### 转换为纯文本

```tsx
const text = await render(<WelcomeEmail name="John" verificationUrl="https://example.com/verify" />, { plainText: true });
```

## 发送

React Email 支持使用任何邮件服务提供商发送。查看 [references/SENDING.md](references/SENDING.md) 获取完整的发送文档，包括 Resend、Nodemailer 和 SendGrid 示例。

快速使用 Resend SDK 的示例：

```tsx
import { Resend } from 'resend';
import { WelcomeEmail } from './emails/welcome';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: 'Acme <onboarding@resend.dev>',
  to: ['user@example.com'],
  subject: 'Welcome to Acme',
  react: <WelcomeEmail name="John" verificationUrl="https://example.com/verify" />
});
```

Resend Node SDK 自动处理 HTML 和纯文本渲染。

## CLI 命令

`react-email` 包提供了一个可通过 `email` 命令访问的 CLI：

| 命令 | 描述 |
|---------|-------------|
| `email dev --dir <path> --port <port>` | 启动预览开发服务器（默认：`./emails`，端口 3000） |
| `email build --dir <path>` | 构建预览应用以进行生产部署 |
| `email start` | 运行构建的预览应用 |
| `email export --outDir <path> --pretty --plainText --dir <path>` | 将模板导出为静态 HTML 文件 |
| `email resend setup` | 通过 API 密钥将 CLI 连接到您的 Resend 账户 |
| `email resend reset` | 删除存储的 Resend API 密钥 |

## 国际化

查看 [references/I18N.md](references/I18N.md) 获取完整 i18n 文档。React Email 支持三个库：next-intl、react-i18next 和 react-intl。

## 邮件编辑器

React Email 包括一个可视化编辑器（`@react-email/editor`），可以嵌入到您的应用中。它基于 TipTap/ProseMirror，并生成邮件就绪的 HTML。

查看 [references/EDITOR.md](references/EDITOR.md) 获取完整文档，包括：
- `EmailEditor` — 带有气泡菜单、斜杠命令和主题的完整功能组件
- `StarterKit` — 35+ 邮件感知扩展（标题、列表、表格、列、按钮等）
- `Inspector` — 用于编辑样式的上下文侧边栏
- `EmailTheming` — 内置主题（`basic`、`minimal`）以及可定制的 CSS 属性
- `composeReactEmail` — 导出编辑器内容为邮件就绪的 HTML 和纯文本
- 通过 `EmailNode` 和 `EmailMark` 的自定义扩展

快速示例：

```tsx
import { EmailEditor, type EmailEditorRef } from '@react-email/editor';
import '@react-email/editor/themes/default.css';
import { useRef } from 'react';

export function MyEditor() {
  const ref = useRef<EmailEditorRef>(null);

  return (
    <EmailEditor
      ref={ref}
      content="<p>Start typing...</p>"
      theme="basic"
    />
  );
}
```

## 常见模式

查看 [references/PATTERNS.md](references/PATTERNS.md) 获取完整示例，包括：
- 密码重置邮件
- 带产品列表的订单确认邮件
- 带代码块的通知邮件
- 多列布局
- 团队邀请邮件

## 邮件最佳实践

1. **跨邮件客户端测试** - Gmail、Outlook、Apple Mail、Yahoo Mail
2. **保持响应式** - 最大宽度约为 600px，在手机上测试
3. **使用绝对图片 URL** - 在可靠的 CDN 上托管
4. **编写有意义的 alt 文本** - 描述内容图片的目的和细节；对于装饰性图片使用 `alt=""`（间隔、分隔符、背景装饰）。React Email 的 `<Img>` 默认为 `alt=""`。
5. **提供纯文本版本** - 可访问性要求
6. **保持文件大小小于 102KB** - Gmail 会裁剪较大的邮件
7. **添加正确的 TypeScript 类型** - 为所有邮件属性定义接口
8. **包含预览属性** - 添加 `.PreviewProps` 以进行开发测试
9. **使用验证过的域名** - 用于生产 `from` 地址

### 可访问性

React Email 处理结构默认值；其余是内容。

**React Email 免费为您提供:**
- `<Html>` 设置 `lang` 和 `dir`（默认：`lang="en" dir="ltr"` — 每个区域设置覆盖）
- `<Img>` 默认为 `alt=""`，因此装饰性图片被屏幕阅读器跳过
- `<Markdown>` 渲染带有 `role="presentation"` 的布局表格
- `<Preview>` 还会发出一个 `<title>` 标签

升级 `npm install react-email@latest` 获取这些默认值。

**您仍然需要做（内容选择）:**
- 以 `<Heading as="h1">` 开头，按顺序嵌套副标题，不要跳过级别（非常短的短信式邮件可能完全跳过标题）
- 设置有意义的图片的描述性 `alt`；在装饰性图片上传递显式的 `alt=""` — 绝不省略属性
- **链接图片永远不会是装饰性的。** 当 `<Img>` 位于 `<Link>` 或 `<Button>` 内部时，`alt` 必须描述链接的目的地 — 链接图片上的 `alt=""` 会留下没有可访问名称的链接
- 编写描述目的地的链接文本（`<Button>Read the report</Button>`，而不是 `click here`）
- 达到 4.5:1 文本对比度（WCAG AA）；在暗黑模式下预览
- 对于您手动构建的布局表格（在 `<Markdown>` 外部），添加 `role="presentation"`
- 对于非英文邮件，传递区域设置：`<Html lang={locale} dir={isRTL ? 'rtl' : 'ltr'}>`（见 [I18N.md](references/I18N.md)）

有关完整规则集、严重性排名和编写清单，请参阅 `email-best-practices` 技能中的 [accessibility reference](https://github.com/resend/email-best-practices/blob/main/references/accessibility.md)。

## 其他资源

- [React Email 文档](https://react.email/docs/llms.txt)
- [React Email GitHub](https://github.com/resend/react-email)
- [Resend 文档](https://resend.com/docs/llms.txt)
- [邮件客户端 CSS 支持](https://www.caniemail.com)
- 组件参考：[references/COMPONENTS.md](references/COMPONENTS.md)
- 样式指南：[references/STYLING.md](references/STYLING.md)
- 邮件编辑器：[references/EDITOR.md](references/EDITOR.md)
- 发送指南：[references/SENDING.md](references/SENDING.md)
- 国际化指南：[references/I18N.md](references/I18N.md)
- 常见模式：[references/PATTERNS.md](references/PATTERNS.md)
