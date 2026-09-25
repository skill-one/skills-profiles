# Browserbase 函数

使用官方 `browse` CLI 部署无服务器浏览器自动化。

## 前置条件

从 https://browserbase.com/settings 获取 API 密钥

```bash
export BROWSERBASE_API_KEY="your_api_key"
```

## 创建函数项目

### 1. 初始化

```bash
browse functions init my-function
cd my-function
```

这会创建：
```
my-function/
├── package.json
├── index.ts        # 你的函数代码
└── .env            # 在这里添加凭证
```

### 2. 将凭证添加到 .env

```bash
echo "BROWSERBASE_API_KEY=$BROWSERBASE_API_KEY" >> .env
```

### 3. 安装依赖

```bash
pnpm install
```

## 函数结构

```typescript
import { defineFn } from "@browserbasehq/sdk-functions";
import { chromium } from "playwright-core";

defineFn("my-function", async (context) => {
  const { session, params } = context;

  // 连接浏览器
  const browser = await chromium.connectOverCDP(session.connectUrl);
  const page = browser.contexts()[0]!.pages()[0]!;

  // 你的自动化操作
  await page.goto(params.url || "https://example.com");
  const title = await page.title();

  // 返回 JSON 可序列化的结果
  return { success: true, title };
});
```

**关键对象：**
- `context.session.connectUrl` - 连接 Playwright 的 CDP 端点
- `context.params` - 调用时输入的参数

## 开发工作流

### 1. 启动开发服务器

```bash
browse functions dev index.ts
```

服务器运行在 `http://127.0.0.1:14113`

### 2. 本地测试

```bash
curl -X POST http://127.0.0.1:14113/v1/functions/my-function/invoke \
  -H "Content-Type: application/json" \
  -d '{"params": {"url": "https://news.ycombinator.com"}}'
```

### 3. 迭代

开发服务器会在文件更改时自动重新加载。使用 `console.log()` 进行调试 - 输出会显示在终端。

## 部署

```bash
browse functions publish index.ts
```

输出：
```
Function published successfully
Build ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Function ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**保存函数 ID** - 你需要它来调用。

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `browse functions init <name>` | 创建新项目 |
| `browse functions dev <file>` | 启动本地开发服务器 |
| `browse functions publish <file>` | 部署到 Browserbase |

有关调用示例、常见模式和故障排除信息，请参阅 [REFERENCE.md](REFERENCE.md)。
