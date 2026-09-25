# AI元素

[AI元素](https://www.npmjs.com/package/ai-elements)是一个基于[shadcn/ui](https://ui.shadcn.com/)构建的组件库和自定义注册中心，旨在帮助您更快地构建AI原生应用程序。它提供了预构建的组件，如对话、消息等。

安装AI元素非常简单，可以通过以下几种方式完成。您可以使用专门的CLI命令进行快速设置，或者如果您已经采用了shadcn的工作流程，可以通过标准的shadcn/ui CLI进行集成。

> **重要提示**：请使用项目的包运行器执行所有CLI命令：`npx ai-elements@latest`、`pnpm dlx ai-elements@latest`或`bunx --bun ai-elements@latest`——具体取决于项目的`packageManager`。以下示例使用`npx ai-elements@latest`，但请根据项目替换正确的运行器。

## 前置条件

在安装AI元素之前，请确保您的环境满足以下要求：

- [Node.js](https://nodejs.org/en/download/)，版本18或更高
- 一个已安装[AI SDK](https://ai-sdk.dev/)的[Next.js](https://nextjs.org/)项目
- 在您的项目中安装了[shadcn/ui](https://ui.shadcn.com/)。如果您尚未安装，运行任何安装命令将自动为您安装
- 我们强烈建议使用[AI网关](https://vercel.com/docs/ai-gateway)，并将`AI_GATEWAY_API_KEY`添加到您的`env.local`中，这样您就不必使用来自每个提供商的API密钥。AI网关每月还提供5美元的使用额度，以便您可以尝试使用模型。您可以在[此处](https://vercel.com/d?to=%2F%5Bteam%5D%2F%7E%2Fai%2Fapi-keys&title=Get%20your%20AI%20Gateway%20key)获取API密钥。

## 安装组件

您可以使用AI元素CLI或shadcn/ui CLI来安装AI元素组件。两者都能达到相同的结果：将所选组件的代码以及任何必要的依赖项添加到您的项目中。

CLI将下载组件的代码并将其集成到您的项目目录中（通常在您的components文件夹下）。默认情况下，AI元素组件被添加到`@/components/ai-elements/`目录（或您在shadcn组件设置中配置的任何文件夹）。

运行命令后，您应该在终端中看到确认文件已添加的消息。然后，您可以继续在您的代码中使用该组件。

## 使用

安装AI元素组件后，您可以像使用任何其他React组件一样导入并使用它。这些组件作为您代码库的一部分添加（不会隐藏在库中），因此使用起来感觉非常自然。

## 示例

安装AI元素组件后，您可以像使用任何其他React组件一样在您的应用程序中使用它们。例如：

```tsx title="conversation.tsx"
"use client";

import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import { useChat } from "@ai-sdk/react";

const Example = () => {
  const { messages } = useChat();

  return (
    <>
      {messages.map(({ role, parts }, index) => (
        <Message from={role} key={index}>
          <MessageContent>
            {parts.map((part, i) => {
              switch (part.type) {
                case "text":
                  return (
                    <MessageResponse key={`${role}-${i}`}>
                      {part.text}
                    </MessageResponse>
                  );
              }
            })}
          </MessageContent>
        </Message>
      ))}
    </>
  );
};

export default Example;
```

在上面的示例中，我们从AI元素目录中导入`Message`组件，并将其包含在我们的JSX中。然后，我们使用`MessageContent`和`MessageResponse`子组件来组合该组件。您可以像编写自己的代码一样对组件进行样式化或配置——由于代码位于您的项目中，您甚至可以打开组件文件查看其工作原理或进行自定义修改。

## 可扩展性

所有AI元素组件都尽可能采用原始属性。例如，`Message`组件扩展了`HTMLAttributes<HTMLDivElement>`，因此您可以传递任何`div`支持的属性。这使得使用自己的样式或功能扩展组件变得非常容易。

## 定制

安装后无需额外设置。组件的样式（Tailwind CSS类）和脚本已经集成。您可以立即在应用程序中与组件进行交互。

例如，如果您希望移除`Message`的圆角，可以进入`components/ai-elements/message.tsx`并按照以下方式移除`rounded-lg`：

```tsx title="components/ai-elements/message.tsx" highlight="8"
export const MessageContent = ({
  children,
  className,
  ...props
}: MessageContentProps) => (
  <div
    className={cn(
      "flex flex-col gap-2 text-sm text-foreground",
      "group-[.is-user]:bg-primary group-[.is-user]:text-primary-foreground group-[.is-user]:px-4 group-[.is-user]:py-3",
      className
    )}
    {...props}
  >
    <div className="is-user:dark">{children}</div>
  </div>
);
```

## 故障排除

### 为什么我的组件没有样式？

请确保您的项目正确配置了shadcn/ui的Tailwind 4——这意味着需要有一个导入Tailwind并包含shadcn/ui基础样式的`globals.css`文件。

### 我运行了AI元素CLI，但项目没有任何变化

请确认：

- 您的当前工作目录是项目的根目录（`package.json`所在的目录）。
- 如果使用shadcn风格的配置，请确保您的`components.json`文件设置正确。
- 您正在使用最新版本的AI元素CLI：

```bash title="终端"
npx ai-elements@latest
```

如果以上方法都无效，请随时在GitHub上[打开一个问题](https://github.com/vercel/ai-elements/issues)。

### 主题切换无效——我的应用程序仍然处于浅色模式

请确保您的应用程序使用与shadcn/ui和AI元素预期的相同的数据主题系统。默认实现会在`<html>`元素上切换一个`data-theme`属性。请确保您的`tailwind.config.js`相应地使用类或数据选择器。

### 组件导入失败，提示“模块未找到”

请检查文件是否存在。如果存在，请确保您的`tsconfig.json`为`@/`设置了正确的路径别名，即：

```json title="tsconfig.json"
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### 我的AI编程助手无法访问AI元素组件

1. 验证您的配置文件语法是否为有效的JSON。
2. 检查您的AI工具的文件路径是否正确。
3. 在进行更改后重启您的编程助手。
4. 确保您有稳定的互联网连接。

### 仍然卡住？

如果以上方法都无效，请在GitHub上[打开一个问题](https://github.com/vercel/ai-elements/issues)，有人会乐意帮助您。

## 可用组件

请查看`references/`文件夹，以获取每个组件的详细文档。
