---
name: dev-browser
description: 使用 dev-browser CLI 实现持久化命名页面的浏览器自动化。当用户需要导航网站、填写表单、截取屏幕截图、提取网页数据、测试网页应用、登录网站或自动化浏览器工作流程时使用。触发短语包括“访问 [url]”、“点击”、“填写表单”、“截取屏幕截图”、“抓取”、“自动化”、“测试网站”、“登录”、“打开浏览器”或任何浏览器交互请求。
---

# dev-browser

用于控制真实 Chrome 的 CLI 工具，配合简短的 Puppeteer 脚本使用。一个预热守护进程；命名页面在多次运行间持久化。

```bash
npm install -g dev-browser   # bun add -g dev-browser 同样有效；首次运行时会下载二进制文件（如果安装脚本被阻止）
dev-browser install          # 仅当首次运行提示 "未找到 Chrome" 时需要执行
```

在执行非简单操作前，请先运行 `dev-browser --help`（完整指南；`dev-browser help <主题>` 用于查看单个章节）。快速入门：

```bash
dev-browser <<'EOF'
const page = await browser.getPage("main");        // 命名页面在多次运行间持久化
await page.goto("https://example.com");            // 默认 waitUntil: domcontentloaded
await page.snapshot({ interactive: true })         // ARIA 树形结构带引用；最后一个表达式会被打印
EOF
dev-browser -e 'const p = await browser.getPage("main"); await p.click("ref/e6"); await p.waitForLoad(); p.url()'
```

注意事项：行尾必须以分号结束（以 `(` 开头的行会延续上一行）；返回对象时使用 `({ a, b })`；`page.click` 从不等待（先用 `waitForSelector`）；页面名称是针对浏览器的（`--headless` 和非 `--headless` 是独立的 Chrome 和配置）；引用在导航后会重置 — 重新快照；文件路径相对于当前工作目录解析（`uploadFile`、`screenshot/pdf` 的 `path`）；不要对同一命名页面并行运行多个 `dev-browser` 调用。
