## playwright-scraper

### 目的
该技能使用 Playwright 进行网页抓取，Playwright 是一个用于浏览器自动化的 Node.js 库。它专注于处理动态内容、身份验证流程、分页、数据提取和截图，以可靠地抓取现代网站。

### 使用场景
用于抓取具有 JavaScript 渲染内容的网站（例如 React 或 Angular 应用）、需要登录的网站（例如仪表板）、处理多页结果（例如搜索结果）或捕获视觉数据（例如用于验证的截图）。避免用于静态 HTML 网站，这些网站可以使用更简单的工具（如 requests）。

### 主要功能
- 使用 Playwright 的浏览器控制动态加载和交互内容。
- 管理身份验证流程，例如通过表单或 API 令牌登录。
- 处理分页，通过导航页面、点击“下一页”按钮或解析 URL。
- 使用选择器提取数据，并可选择 JSON 输出或文件保存。
- 捕获截图或全页 PDF 用于调试或报告。
- 支持无头或可见浏览器模式，提供灵活性。

### 使用模式
始终首先初始化浏览器上下文，然后创建页面进行导航。使用异步模式以提高可靠性。对于需要身份验证的抓取，按上下文处理 cookie 或会话。结构化脚本以循环遍历页面进行分页，并使用 try-catch 处理不可靠的元素。通过 JSON 文件或环境变量传递配置，以提高可重用性。

### 常用命令/API
使用 Playwright 的 Node.js API。通过 `npm install playwright` 安装。关键方法包括：
- 启动浏览器：`const browser = await playwright.chromium.launch({ headless: true });`
- 导航页面：`const page = await browser.newPage(); await page.goto('https://example.com');`
- 处理身份验证：`await page.fill('#username', process.env.USERNAME); await page.fill('#password', process.env.PASSWORD); await page.click('#login');`
- 提取数据：`const data = await page.evaluate(() => document.querySelector('#target').innerText); console.log(data);`
- 分页：`while (await page.$('#next-button')) { await page.click('#next-button'); await page.waitForSelector('.item'); }`
- 拍摄截图：`await page.screenshot({ path: 'screenshot.png' });`
CLI 标志用于运行脚本：使用 `npx playwright test` 并配合标志，如 `--headed` 用于可见模式或 `--timeout 30000` 用于延长等待时间。

### 集成说明
通过在 Node.js 项目中导入 Playwright 进行集成。对于身份验证，使用环境变量（如 `$PLAYWRIGHT_USERNAME` 和 `$PLAYWRIGHT_PASSWORD`）以避免硬编码。配置格式：使用 JSON 文件设置，例如 `{ "url": "https://target.com", "selector": "#data-element" }`。通过脚本参数传递：`node scraper.js --config config.json`。对于更大的系统，可以与 Puppeteer（如果迁移）等工具链式使用，或通过 `page.evaluate` 结果将数据导出到数据库。确保与 Node.js 14+ 兼容，并使用 `browser.launch({ proxy: { server: 'http://myproxy.com:8080' } })` 处理代理设置。

### 错误处理
预见常见错误，如动态加载超时或选择器失败。使用 `page.waitForSelector` 并设置超时：`await page.waitForSelector('#element', { timeout: 10000 }).catch(err => console.error('Element not found:', err));`。对于网络问题，将 `page.goto` 包裹在 try-catch 中：`try { await page.goto(url, { waitUntil: 'networkidle' }); } catch (e) { console.error('Navigation failed:', e.message); await browser.close(); }`。通过检查错误元素处理身份验证失败：`if (await page.$('#error-message')) { throw new Error('Login failed'); }`。记录错误详情并使用循环最多重试 3 次。

### 具体使用示例
1. **抓取登录仪表板：** 首先设置环境变量：`export PLAYWRIGHT_USERNAME='user@example.com'` 和 `export PLAYWRIGHT_PASSWORD='securepass'`。然后运行：`const browser = await playwright.chromium.launch(); const page = await browser.newPage(); await page.goto('https://dashboard.com/login'); await page.fill('#username', process.env.PLAYWRIGHT_USERNAME); await page.fill('#password', process.env.PLAYWRIGHT_PASSWORD); await page.click('#submit'); const data = await page.evaluate(() => document.querySelector('#dashboard-data').innerText); console.log(data); await browser.close();` 这从受保护的页面中提取数据。
2. **处理搜索网站的分页：** 脚本：`const browser = await playwright.chromium.launch(); const page = await browser.newPage(); await page.goto('https://search.com?q=query'); let items = []; while (true) { items.push(...await page.$$eval('.result-item', elements => elements.map(el => el.innerText))); const nextButton = await page.$('#next-page'); if (!nextButton) break; await nextButton.click(); await page.waitForTimeout(2000); } console.log(items); await browser.close();` 这收集跨多页的结果。

### 图关系
- 相关于："selenium-automation"（另一种浏览器自动化工具）
- 依赖："node-runtime"（用于 Playwright 执行）
- 补充："data-extraction"（用于抓取数据的后处理）
- 集群："community"（与其他开源工具共享）
