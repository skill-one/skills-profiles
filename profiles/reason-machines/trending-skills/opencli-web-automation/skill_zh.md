# OpenCLI Web Automation

> 技能来自 [ara.so](https://ara.so) — 每日 2026 技能合集。

OpenCLI 通过复用 Chrome 的登录浏览器会话，将任何网站转换为命令行界面。它开箱即支持 19 个网站和 80+ 命令，并允许您通过将 TypeScript 或 YAML 文件放入 `clis/` 文件夹来添加新的适配器。

---

## 安装

```bash
# 通过 npm 全局安装
npm install -g @jackwener/opencli

# 一次性设置：发现 Playwright MCP 令牌并分发给所有工具
opencli setup

# 验证一切是否正常工作
opencli doctor --live
```

### 前置条件

- Node.js >= 18.0.0
- Chrome 浏览器 **正在运行并已登录目标网站**
- 安装了 Chrome 中的 [Playwright MCP Bridge](https://chromewebstore.google.com/detail/playwright-mcp-bridge/mmlmfjhmonkocbjadbfplnigmagldckm) 扩展

### 从源代码安装（开发）

```bash
git clone git@github.com:jackwener/opencli.git
cd opencli
npm install
npm run build
npm link
```

---

## 环境配置

```bash
# 必须在运行 opencli setup 后设置在 ~/.zshrc 或 ~/.bashrc 中
export PLAYWRIGHT_MCP_EXTENSION_TOKEN="<从 setup 获取的您的令牌>"
```

MCP 客户端配置（Claude/Cursor/Codex `~/.config/*/config.json`）:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--extension"],
      "env": {
        "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "$PLAYWRIGHT_MCP_EXTENSION_TOKEN"
      }
    }
  }
}
```

---

## 主要 CLI 命令

### 发现与注册

```bash
opencli list                        # 显示所有注册的命令
opencli list -f yaml                # 以 YAML 格式输出注册表
opencli list -f json                # 以 JSON 格式输出注册表
```

### 运行内置命令

```bash
# 公共 API 命令（无需浏览器登录）
opencli hackernews top --limit 10
opencli github search "playwright automation"
opencli bbc news

# 浏览器命令（必须在 Chrome 中登录网站）
opencli bilibili hot --limit 5
opencli twitter trending
opencli zhihu hot -f json
opencli reddit frontpage --limit 20
opencli xiaohongshu search "TypeScript"
opencli youtube search "browser automation"
opencli linkedin search "senior engineer"
```

### 输出格式

所有命令都支持 `--format` / `-f`:

```bash
opencli bilibili hot -f table     # 丰富的终端表格（默认）
opencli bilibili hot -f json      # JSON（管道传输到 jq）
opencli bilibili hot -f yaml      # YAML
opencli bilibili hot -f md        # Markdown
opencli bilibili hot -f csv       # CSV 导出
opencli bilibili hot -v           # 详细模式：显示管道调试步骤
```

### AI 代理工作流（创建新命令）

```bash
# 1. 深入探索网站 — 发现 API、认证、功能
opencli explore https://example.com --site mysite

# 2. 从探索工件合成 YAML 适配器
opencli synthesize mysite

# 3. 一次性：探索 → 合成 → 在一个命令中注册
opencli generate https://example.com --goal "hot posts"

# 4. 策略级联 — 自动探测 PUBLIC → COOKIE → HEADER 认证
opencli cascade https://api.example.com/data
```

探索工件保存在 `.opencli/explore/<site>/`:
- `manifest.json` — 网站元数据
- `endpoints.json` — 发现的 API 端点
- `capabilities.json` — 推断的命令功能
- `auth.json` — 认证策略

---

## 添加新适配器

### 选项 1：YAML 声明式适配器

将 `.yaml` 文件放入 `clis/` — 在下次运行时自动注册:

```yaml
# clis/producthunt.yaml
site: producthunt
commands:
  - name: trending
    description: 获取 Product Hunt 上的热门产品
    args:
      - name: limit
        type: number
        default: 10
    pipeline:
      - type: navigate
        url: https://www.producthunt.com
      - type: waitFor
        selector: "[data-test='post-item']"
      - type: extract
        selector: "[data-test='post-item']"
        fields:
          name:
            selector: "h3"
            type: text
          tagline:
            selector: "p"
            type: text
          votes:
            selector: "[data-test='vote-button']"
            type: text
          url:
            selector: "a"
            attr: href
      - type: limit
        count: "{{limit}}"
```

### 选项 2：TypeScript 适配器

```typescript
// clis/producthunt.ts
import type { CLIAdapter } from "../src/types";

const adapter: CLIAdapter = {
  site: "producthunt",
  commands: [
    {
      name: "trending",
      description: "获取 Product Hunt 上的热门产品",
      options: [
        {
          flags: "--limit <n>",
          description: "结果数量",
          defaultValue: "10",
        },
      ],
      async run(options, browser) {
        const page = await browser.currentPage();
        await page.goto("https://www.producthunt.com");
        await page.waitForSelector("[data-test='post-item']");

        const products = await page.evaluate(() => {
          return Array.from(
            document.querySelectorAll("[data-test='post-item']")
          ).map((el) => ({
            name: el.querySelector("h3")?.textContent?.trim() ?? "",
            tagline: el.querySelector("p")?.textContent?.trim() ?? "",
            votes:
              el
                .querySelector("[data-test='vote-button']")
                ?.textContent?.trim() ?? "",
            url:
              (el.querySelector("a") as HTMLAnchorElement)?.href ?? "",
          }));
        });

        return products.slice(0, Number(options.limit));
      },
    },
  ],
};

export default adapter;
```

---

## 常见模式

### 模式：认证 API 提取（Cookie 注入）

```typescript
// 当网站暴露 JSON API 但需要登录 Cookie 时
async run(options, browser) {
  const page = await browser.currentPage();

  // 首先导航以确保 Cookie 处于活动状态
  await page.goto("https://api.example.com");

  const data = await page.evaluate(async () => {
    const res = await fetch("/api/v1/feed?limit=20", {
      credentials: "include", // 复用浏览器 Cookie
    });
    return res.json();
  });

  return data.items;
}
```

### 模式：Header 令牌提取

```typescript
// 从浏览器存储中提取用于 API 调用的认证令牌
async run(options, browser) {
  const page = await browser.currentPage();
  await page.goto("https://example.com");

  const token = await page.evaluate(() => {
    return localStorage.getItem("auth_token") ||
           sessionStorage.getItem("token");
  });

  const data = await page.evaluate(async (tok) => {
    const res = await fetch("/api/data", {
      headers: { Authorization: `Bearer ${tok}` },
    });
    return res.json();
  }, token);

  return data;
}
```

### 模式：带等待的 DOM 提取

```typescript
async run(options, browser) {
  const page = await browser.currentPage();
  await page.goto("https://news.ycombinator.com");

  // 等待动态内容加载
  await page.waitForSelector(".athing", { timeout: 10000 });

  return page.evaluate((limit) => {
    return Array.from(document.querySelectorAll(".athing"))
      .slice(0, limit)
      .map((row) => ({
        title: row.querySelector(".titleline a")?.textContent?.trim(),
        url: (row.querySelector(".titleline a") as HTMLAnchorElement)?.href,
        score:
          row.nextElementSibling
            ?.querySelector(".score")
            ?.textContent?.trim() ?? "0",
      }));
  }, Number(options.limit));
}
```

### 模式：分页

```typescript
async run(options, browser) {
  const page = await browser.currentPage();
  const results = [];
  let pageNum = 1;

  while (results.length < Number(options.limit)) {
    await page.goto(`https://example.com/posts?page=${pageNum}`);
    await page.waitForSelector(".post-item");

    const items = await page.evaluate(() =>
      Array.from(document.querySelectorAll(".post-item")).map((el) => ({
        title: el.querySelector("h2")?.textContent?.trim(),
        url: (el.querySelector("a") as HTMLAnchorElement)?.href,
      }))
    );

    if (items.length === 0) break;
    results.push(...items);
    pageNum++;
  }

  return results.slice(0, Number(options.limit));
}
```

---

## 维护命令

```bash
# 跨所有工具诊断令牌和配置
opencli doctor

# 测试实时浏览器连接
opencli doctor --live

# 交互式修复不匹配的配置
opencli doctor --fix

# 非交互式修复所有配置
opencli doctor --fix -y
```

---

## 测试

```bash
npm run build

# 运行所有测试
npx vitest run

# 单元测试仅
npx vitest run src/

# E2E 测试仅
npx vitest run tests/e2e/

# CI 的无头浏览器模式
OPENCLI_HEADLESS=1 npx vitest run tests/e2e/
```

---

## 故障排除

| 症状 | 解决方法 |
|---|---|
| `Failed to connect to Playwright MCP Bridge` | 确保 Chrome 中已启用扩展；安装后重启 Chrome |
| 空数据 / `Unauthorized` | 打开 Chrome，导航到网站，登录或刷新页面 |
| Node API 错误 | 升级到 Node.js >= 18 |
| 令牌未找到 | 运行 `opencli setup` 或 `opencli doctor --fix` |
| 陈旧的登录会话 | 在 Chrome 中访问目标网站并与其交互以证明人类存在 |

### 详细模式

```bash
# 查看完整的管道执行步骤
opencli bilibili hot -v

# 检查 explore 发现的内容
cat .opencli/explore/mysite/endpoints.json
cat .opencli/explore/mysite/auth.json
```

---

## 项目结构（适配器作者）

```
opencli/
├── clis/               # 将 .ts 或 .yaml 适配器放入此处（自动注册）
│   ├── bilibili.ts
│   ├── twitter.ts
│   └── hackernews.yaml
├── src/
│   ├── types.ts        # CLIAdapter、Command 接口
│   ├── browser.ts      # Playwright MCP 桥接器包装
│   ├── loader.ts       # 动态适配器加载器
│   └── output.ts       # table/json/yaml/md/csv 格式化器
├── tests/
│   └── e2e/            # 每个网站的 E2E 测试
└── CLI-EXPLORER.md     # 完整的 AI 代理探索工作流
```
