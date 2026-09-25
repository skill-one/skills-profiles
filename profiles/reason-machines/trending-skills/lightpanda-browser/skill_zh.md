# Lightpanda — 用于 AI 与自动化 的无头浏览器

> 技能来源：[ara.so](https://ara.so) — 2026 日度技能合集

Lightpanda 是一款使用 Zig 语言从零构建的无头浏览器，专为 AI 代理、网络抓取和自动化而设计。它比 Chrome 无头浏览器内存使用量减少 9 倍，运行速度提升 11 倍。

**主要特点：**
- 基于 Chromium、Blink 或 WebKit — 纯 Zig 语言实现
- 通过 V8 引擎执行 JavaScript
- 兼容 CDP（Chrome 开发者工具协议）— 可与 Playwright、Puppeteer、chromedp 一起使用
- 通过 `--obey_robots` 标志尊重 `robots.txt`
- 处于测试阶段，积极开发中
- 许可证：AGPL-3.0

## 安装

### macOS (Apple Silicon)

```bash
curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-aarch64-macos
chmod a+x ./lightpanda
```

### Linux (x86_64)

```bash
curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux
chmod a+x ./lightpanda
```

### Docker

```bash
# 支持 amd64 和 arm64
docker run -d --name lightpanda -p 9222:9222 lightpanda/browser:nightly
```

## CLI 使用

### 获取 URL（导出渲染后的 HTML）

```bash
./lightpanda fetch --obey_robots --log_format pretty --log_level info https://example.com
```

### 启动 CDP 服务器

```bash
./lightpanda serve --obey_robots --log_format pretty --log_level info --host 127.0.0.1 --port 9222
```

这会启动一个基于 WebSocket 的 CDP 服务器，用于程序化控制。

### CLI 标志

| 标志 | 描述 |
|------|-------------|
| `--obey_robots` | 尊重 robots.txt 规则 |
| `--log_format pretty` | 人类可读的日志输出 |
| `--log_level info` | 日志详细程度：`debug`、`info`、`warn`、`error` |
| `--host 127.0.0.1` | CDP 服务器的绑定地址 |
| `--port 9222` | CDP 服务器的端口 |
| `--insecure_disable_tls_host_verification` | 禁用 TLS 验证（仅用于测试） |

## Playwright 集成

启动 CDP 服务器，然后将 Playwright 连接到它：

```javascript
import { chromium } from 'playwright-core';

const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const context = await browser.contexts()[0] || await browser.newContext();
const page = await context.newPage();

await page.goto('https://example.com', { waitUntil: 'networkidle' });
const title = await page.title();
const content = await page.content();

console.log(`Title: ${title}`);
console.log(`HTML length: ${content.length}`);

await browser.close();
```

## Puppeteer 集成

```javascript
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222',
});

const context = await browser.createBrowserContext();
const page = await context.newPage();

await page.goto('https://example.com', { waitUntil: 'networkidle0' });

const title = await page.title();
const text = await page.evaluate(() => document.body.innerText);

console.log(`Title: ${title}`);
console.log(`Body text: ${text.substring(0, 200)}`);

await page.close();
await browser.close();
```

## Go (chromedp) 集成

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/chromedp/chromedp"
)

func main() {
    allocCtx, cancel := chromedp.NewRemoteAllocator(context.Background(), "ws://127.0.0.1:9222")
    defer cancel()

    ctx, cancel := chromedp.NewContext(allocCtx)
    defer cancel()

    var title string
    err := chromedp.Run(ctx,
        chromedp.Navigate("https://example.com"),
        chromedp.Title(&title),
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Title:", title)
}
```

## Python 集成

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        await page.goto("https://example.com", wait_until="networkidle")
        title = await page.title()
        content = await page.content()

        print(f"Title: {title}")
        print(f"HTML length: {len(content)}")

        await browser.close()

asyncio.run(main())
```

## 网络抓取模式

### 批量页面获取

```javascript
import { chromium } from 'playwright-core';

const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const context = await browser.newContext();

const urls = [
  'https://example.com/page1',
  'https://example.com/page2',
  'https://example.com/page3',
];

for (const url of urls) {
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });

  const data = await page.evaluate(() => ({
    title: document.title,
    text: document.body.innerText,
    links: [...document.querySelectorAll('a[href]')].map(a => a.href),
  }));

  console.log(JSON.stringify(data, null, 2));
  await page.close();
}

await browser.close();
```

### 提取结构化数据

```javascript
const data = await page.evaluate(() => {
  const items = document.querySelectorAll('.product-card');
  return [...items].map(item => ({
    name: item.querySelector('h2')?.textContent?.trim(),
    price: item.querySelector('.price')?.textContent?.trim(),
    link: item.querySelector('a')?.href,
  }));
});
```

## Docker Compose（与您的应用一起使用）

```yaml
services:
  lightpanda:
    image: lightpanda/browser:nightly
    ports:
      - "9222:9222"
    restart: unless-stopped

  scraper:
    build: .
    depends_on:
      - lightpanda
    environment:
      - BROWSER_WS_ENDPOINT=ws://lightpanda:9222
```

## 支持的 Web API

Lightpanda 支持（部分，正在扩展）：
- DOM 树操作和查询
- JavaScript 执行（V8）
- XMLHttpRequest (XHR)
- Fetch API
- Cookie 管理
- 网络拦截
- 代理支持

## 配置

| 环境变量 | 描述 |
|---------------------|-------------|
| `LIGHTPANDA_DISABLE_TELEMETRY` | 设置为 `true` 以退出使用指标 |

## 性能比较

| 指标 | Lightpanda | Chrome 无头 |
|--------|-----------|-----------------|
| 内存 | ~9 倍减少 | 基准 |
| 速度 | ~11 倍更快 | 基准 |
| 二进制文件大小 | 小（Zig） | 大（Chromium） |
| 渲染 | 无视觉渲染 | 完整渲染引擎 |

## 何时使用 Lightpanda

**使用 Lightpanda 的情况：**
- 运行需要浏览网络的 AI 代理
- 大规模批量抓取（内存/CPU 节省很重要）
- 自动化表单提交和数据提取
- 在资源受限的容器中运行
- 需要兼容 CDP 但不需要完整视觉渲染

**使用 Chrome/Playwright 的情况：**
- 需要像素级精确截图或 PDF 生成
- 需要 Web API 完全覆盖（Lightpanda 仍然是部分）
- 视觉回归测试
- 测试浏览器特定的渲染行为

## 从源代码构建

需要：Zig 0.15.2、Rust、CMake、系统依赖。

```bash
# Ubuntu/Debian 依赖
sudo apt install xz-utils ca-certificates pkg-config libglib2.0-dev clang make curl

# 构建
git clone https://github.com/lightpanda-io/browser.git
cd browser
zig build

# 可选：预构建 V8 快照以加快启动速度
zig build snapshot_creator -- src/snapshot.bin
zig build -Dsnapshot_path=../../snapshot.bin
```

## 故障排除

**端口 9222 连接被拒绝：**
- 确保 `./lightpanda serve` 正在运行
- 如果从 Docker/远程连接，请检查 `--host 0.0.0.0`

**更新后 Playwright 脚本中断：**
- Lightpanda 处于测试阶段 — Playwright 的能力检测在不同版本中可能表现不同
- 固定您的 Lightpanda 版本或始终使用 nightly 版本

**缺少 Web API 支持：**
- 检查 [zig-js-runtime](https://github.com/lightpanda-io/zig-js-runtime) 仓库中的当前 API 覆盖情况
- 在 [lightpanda-io/browser](https://github.com/lightpanda-io/browser/issues) 处提交问题

## 链接

- GitHub: https://github.com/lightpanda-io/browser
- 运行时 API: https://github.com/lightpanda-io/zig-js-runtime
