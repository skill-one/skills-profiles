## 什么是 DOM 组件？

DOM 组件允许 Web 代码在原生平台的 webview 中逐字运行，同时在 Web 上原样渲染。这使得您可以在 Expo 应用中使用 Web 独有的库（如 `recharts`、`react-syntax-highlighter` 或任何 React Web 库），而无需修改。

## 何时使用 DOM 组件

当您需要以下功能时，请使用 DOM 组件：

- **Web 独有库** — 图表（recharts、chart.js）、语法高亮器、富文本编辑器或任何依赖 DOM API 的库
- **迁移 Web 代码** — 将现有的 React Web 组件迁移到原生而无需重写
- **复杂的 HTML/CSS 布局** — 当 React Native 中不可用 CSS 功能时
- **iframe 或嵌入** — 嵌入需要浏览器上下文的外部内容
- **Canvas 或 WebGL** — Web 图形 API 在原生环境中不可用

## 何时不使用 DOM 组件

避免使用 DOM 组件的情况：

- **原生性能至关重要** — Webview 会增加开销
- **简单 UI** — React Native 组件对于基本布局更高效
- **深度原生集成** — 使用本地模块以获取原生 API
- **布局路由** — `_layout` 文件不能是 DOM 组件

## 基本 DOM 组件

在文件顶部创建一个新的文件并添加 `'use dom';` 指令：

```tsx
// components/WebChart.tsx
"use dom";

export default function WebChart({
  data,
}: {
  data: number[];
  dom: import("expo/dom").DOMProps;
}) {
  return (
    <div style={{ padding: 20 }}>
      <h2>图表数据</h2>
      <ul>
        {data.map((value, i) => (
          <li key={i}>{value}</li>
        ))}
      </ul>
    </div>
  );
}
```

## DOM 组件规则

1. **必须在文件顶部有 `'use dom';` 指令**
2. **单个默认导出** — 每个文件一个 React 组件
3. **独立文件** — 不能内联定义或与原生组件组合
4. **仅支持可序列化属性** — 字符串、数字、布尔值、数组、普通对象
5. **在组件文件中包含 CSS** — DOM 组件在隔离的上下文中运行

## `dom` 属性

每个 DOM 组件都会接收到一个特殊的 `dom` 属性用于 webview 配置。请始终在您的属性中声明它：

```tsx
"use dom";

interface Props {
  content: string;
  dom: import("expo/dom").DOMProps;
}

export default function MyComponent({ content }: Props) {
  return <div>{content}</div>;
}
```

### 常见的 `dom` 属性选项

```tsx
// 禁用 body 滚动
<DOMComponent dom={{ scrollEnabled: false }} />

// 低于凹口（禁用安全区域填充）
<DOMComponent dom={{ contentInsetAdjustmentBehavior: "never" }} />

// 手动控制大小
<DOMComponent dom={{ style: { width: 300, height: 400 } }} />

// 组合选项
<DOMComponent
  dom={{
    scrollEnabled: false,
    contentInsetAdjustmentBehavior: "never",
    style: { width: '100%', height: 500 }
  }}
/>
```

## 将原生操作暴露给 webview

将异步函数作为属性传递以将原生功能暴露给 DOM 组件：

```tsx
// app/index.tsx (原生)
import { Alert } from "react-native";
import DOMComponent from "@/components/dom-component";

export default function Screen() {
  return (
    <DOMComponent
      showAlert={async (message: string) => {
        Alert.alert("来自 Web", message);
      }}
      saveData={async (data: { name: string; value: number }) => {
        // 保存到原生存储、数据库等
        console.log("保存:", data);
        return { success: true };
      }}
    />
  );
}
```

```tsx
// components/dom-component.tsx
"use dom";

interface Props {
  showAlert: (message: string) => Promise<void>;
  saveData: (data: {
    name: string;
    value: number;
  }) => Promise<{ success: boolean }>;
  dom?: import("expo/dom").DOMProps;
}

export default function DOMComponent({ showAlert, saveData }: Props) {
  const handleClick = async () => {
    await showAlert("来自 webview 的问候！");
    const result = await saveData({ name: "test", value: 42 });
    console.log("保存结果:", result);
  };

  return <button onClick={handleClick}>触发原生操作</button>;
}
```

## 使用 Web 库

DOM 组件可以使用任何 Web 库：

```tsx
// components/syntax-highlight.tsx
"use dom";

import SyntaxHighlighter from "react-syntax-highlighter";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";

interface Props {
  code: string;
  language: string;
  dom?: import("expo/dom").DOMProps;
}

export default function SyntaxHighlight({ code, language }: Props) {
  return (
    <SyntaxHighlighter language={language} style={docco}>
      {code}
    </SyntaxHighlighter>
  );
}
```

```tsx
// components/chart.tsx
"use dom";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

interface Props {
  data: Array<{ name: string; value: number }>;
  dom: import("expo/dom").DOMProps;
}

export default function Chart({ data }: Props) {
  return (
    <LineChart width={400} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
}
```

## DOM 组件中的 CSS

由于它们在隔离的上下文中运行，CSS 导入必须在 DOM 组件文件中：

```tsx
// components/styled-component.tsx
"use dom";

import "@/styles.css"; // 同一目录中的 CSS 文件

export default function StyledComponent({
  dom,
}: {
  dom: import("expo/dom").DOMProps;
}) {
  return (
    <div className="container">
      <h1 className="title">样式化内容</h1>
    </div>
  );
}
```

或者使用内联样式 / CSS-in-JS：

```tsx
"use dom";

const styles = {
  container: {
    padding: 20,
    backgroundColor: "#f0f0f0",
  },
  title: {
    fontSize: 24,
    color: "#333",
  },
};

export default function StyledComponent({
  dom,
}: {
  dom: import("expo/dom").DOMProps;
}) {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>样式化内容</h1>
    </div>
  );
}
```

## DOM 组件中的 Expo Router

expo-router 的 `<Link />` 组件和路由 API 可以在 DOM 组件内部工作：

```tsx
"use dom";

import { Link, useRouter } from "expo-router";

export default function Navigation({
  dom,
}: {
  dom: import("expo/dom").DOMProps;
}) {
  const router = useRouter();

  return (
    <nav>
      <Link href="/about">关于</Link>
      <button onClick={() => router.push("/settings")}>设置</button>
    </nav>
  );
}
```

### 需要属性的路由 API

这些钩子不能直接在 DOM 组件中工作，因为它们需要同步访问原生路由状态：

- `useLocalSearchParams()`
- `useGlobalSearchParams()`
- `usePathname()`
- `useSegments()`
- `useRootNavigation()`
- `useRootNavigationState()`

**解决方案**：在原生父组件中读取这些值，并将其作为属性传递：

```tsx
// app/[id].tsx (原生)
import { useLocalSearchParams, usePathname } from "expo-router";
import DOMComponent from "@/components/dom-component";

export default function Screen() {
  const { id } = useLocalSearchParams();
  const pathname = usePathname();

  return <DOMComponent id={id as string} pathname={pathname} />;
}
```

```tsx
// components/dom-component.tsx
"use dom";

interface Props {
  id: string;
  pathname: string;
  dom?: import("expo/dom").DOMProps;
}

export default function DOMComponent({ id, pathname }: Props) {
  return (
    <div>
      <p>当前 ID: {id}</p>
      <p>当前路径: {pathname}</p>
    </div>
  );
}
```

## 检测 DOM 环境

检查代码是否在 DOM 组件中运行：

```tsx
"use dom";

import { IS_DOM } from "expo/dom";

export default function Component({
  dom,
}: {
  dom?: import("expo/dom").DOMProps;
}) {
  return <div>{IS_DOM ? "运行在 DOM 组件中" : "原生运行"}</div>;
}
```

## 资产

优先使用 `require` 而不是使用公共目录：

```tsx
"use dom";

// 良好 - 随组件打包
const logo = require("../assets/logo.png");

export default function Component({
  dom,
}: {
  dom: import("expo/dom").DOMProps;
}) {
  return <img src={logo} alt="Logo" />;
}
```

## 从原生组件中使用

像普通组件一样导入和使用 DOM 组件：

```tsx
// app/index.tsx
import { View, Text } from "react-native";
import WebChart from "@/components/web-chart";
import CodeBlock from "@/components/code-block";

export default function HomeScreen() {
  return (
    <View style={{ flex: 1 }}>
      <Text>原生内容在上方</Text>

      <WebChart data={[10, 20, 30, 40, 50]} dom={{ style: { height: 300 } }} />

      <CodeBlock
        code="const x = 1;"
        language="javascript"
        dom={{ scrollEnabled: true }}
      />

      <Text>原生内容在下方</Text>
    </View>
  );
}
```

## 平台行为

| 平台 | 行为                            |
| -------- | ----------------------------------- |
| iOS      | 在 WKWebView 中渲染               |
| Android  | 在 WebView 中渲染                 |
| Web      | 原样渲染（无需 webview 包装） |

在 Web 上，`dom` 属性会被忽略，因为不需要 webview。

## 小贴士

- DOM 组件在开发过程中热重载
- 保持 DOM 组件聚焦 — 不要将整个屏幕放入 webview
- 使用原生组件进行导航铬，DOM 组件用于特殊内容
- 在所有平台上测试 — Web 渲染可能与原生 webview 略有不同
- 大型 DOM 组件可能会影响性能 — 如有必要请进行性能分析
- webview 有自己的 JavaScript 上下文 — 不能直接共享状态与原生

## 提交反馈
如果您在技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-dom" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能提供相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 `eval-candidate` 流程，而不是重复使用上面的命令。
