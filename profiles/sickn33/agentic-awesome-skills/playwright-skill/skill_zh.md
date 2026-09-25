**重要提示 - 路径解析：**
此技能可以安装在不同的位置（插件系统、手动安装、全局或特定于项目的）。在执行任何命令之前，根据您加载此 SKILL.md 文件的位置确定技能目录，并在所有以下命令中使用该路径。将 `$SKILL_DIR` 替换为实际发现的路径。

常见的安装路径：

- 插件系统：`<plugin-root>/skills/playwright-skill`
- 手动全局：`<agent-home>/skills/playwright-skill`
- 特定于项目：`<project>/.agent/skills/playwright-skill`

# Playwright 浏览器自动化

通用浏览器自动化技能。我将为任何您请求的自动化任务编写自定义 Playwright 代码，并通过通用执行器执行它。

**关键工作流程 - 按顺序执行以下步骤：**

1. **自动检测开发服务器** - 对于本地主机测试，始终首先运行服务器检测：

   ```bash
   cd $SKILL_DIR && node -e "require('./lib/helpers').detectDevServers().then(servers => console.log(JSON.stringify(servers)))"
   ```

   - 如果 **找到 1 个服务器**：自动使用它，并通知用户
   - 如果 **找到多个服务器**：询问用户要测试哪一个
   - 如果 **未找到服务器**：请求 URL 或提供启动开发服务器的帮助

2. **将脚本写入 /tmp** - 绝对不要将测试文件写入技能目录；始终使用 `/tmp/playwright-test-*.js`

3. **默认使用可见浏览器** - 除非用户明确要求无头模式，否则始终使用 `headless: false`

4. **参数化 URL** - 始终通过环境变量或脚本顶部的常量使 URL 可配置

## 工作原理

1. 您描述要测试/自动化的内容
2. 我自动检测正在运行的开发服务器（或如果测试外部网站，则请求 URL）
3. 我在 `/tmp/playwright-test-*.js` 中编写自定义 Playwright 代码（不会污染您的项目）
4. 我通过执行它：`cd $SKILL_DIR && node run.js /tmp/playwright-test-*.js`
5. 结果实时显示，浏览器窗口可见以便调试
6. 测试文件由您的操作系统自动清理 /tmp

## 首次设置

```bash
cd $SKILL_DIR
npm run setup
```

这将安装 Playwright 和 Chromium 浏览器。只需执行一次。

## 执行模式

**步骤 1：检测开发服务器（用于本地主机测试）**

```bash
cd $SKILL_DIR && node -e "require('./lib/helpers').detectDevServers().then(s => console.log(JSON.stringify(s)))"
```

**步骤 2：将测试脚本写入 /tmp 并包含 URL 参数**

```javascript
// /tmp/playwright-test-page.js
const { chromium } = require('playwright');

// 参数化 URL（检测到的或用户提供的）
const TARGET_URL = 'http://localhost:3001'; // <-- 自动检测或来自用户

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto(TARGET_URL);
  console.log('页面加载:', await page.title());

  await page.screenshot({ path: '/tmp/screenshot.png', fullPage: true });
  console.log('📸 截图保存到 /tmp/screenshot.png');

  await browser.close();
})();
```

**步骤 3：从技能目录执行**

```bash
cd $SKILL_DIR && node run.js /tmp/playwright-test-page.js
```

## 常见模式

### 测试页面（多个视口）

```javascript
// /tmp/playwright-test-responsive.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // 自动检测

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  // 桌面测试
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto(TARGET_URL);
  console.log('桌面 - 标题:', await page.title());
  await page.screenshot({ path: '/tmp/desktop.png', fullPage: true });

  // 移动测试
  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: '/tmp/mobile.png', fullPage: true });

  await browser.close();
})();
```

### 测试登录流程

```javascript
// /tmp/playwright-test-login.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // 自动检测

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto(`${TARGET_URL}/login`);

  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // 等待重定向
  await page.waitForURL('**/dashboard');
  console.log('✅ 登录成功，重定向到仪表板');

  await browser.close();
})();
```

### 填写并提交表单

```javascript
// /tmp/playwright-test-form.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // 自动检测

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 50 });
  const page = await browser.newPage();

  await page.goto(`${TARGET_URL}/contact`);

  await page.fill('input[name="name"]', 'John Doe');
  await page.fill('input[name="email"]', 'john@example.com');
  await page.fill('textarea[name="message"]', '测试消息');
  await page.click('button[type="submit"]');

  // 验证提交
  await page.waitForSelector('.success-message');
  console.log('✅ 表单提交成功');

  await browser.close();
})();
```

### 检查损坏的链接

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('http://localhost:3000');

  const links = await page.locator('a[href^="http"]').all();
  const results = { working: 0, broken: [] };

  for (const link of links) {
    const href = await link.getAttribute('href');
    try {
      const response = await page.request.head(href);
      if (response.ok()) {
        results.working++;
      } else {
        results.broken.push({ url: href, status: response.status() });
      }
    } catch (e) {
      results.broken.push({ url: href, error: e.message });
    }
  }

  console.log(`✅ 工作中的链接: ${results.working}`);
  console.log(`❌ 损坏的链接:`, results.broken);

  await browser.close();
})();
```

### 带错误处理的截图

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3000', {
      waitUntil: 'networkidle',
      timeout: 10000,
    });

    await page.screenshot({
      path: '/tmp/screenshot.png',
      fullPage: true,
    });

    console.log('📸 截图保存到 /tmp/screenshot.png');
  } catch (error) {
    console.error('❌ 错误:', error.message);
  } finally {
    await browser.close();
  }
})();
```

### 测试响应式设计

```javascript
// /tmp/playwright-test-responsive-full.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // 自动检测

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const viewports = [
    { name: '桌面', width: 1920, height: 1080 },
    { name: '平板', width: 768, height: 1024 },
    { name: '移动设备', width: 375, height: 667 },
  ];

  for (const viewport of viewports) {
    console.log(
      `测试 ${viewport.name} (${viewport.width}x${viewport.height})`,
    );

    await page.setViewportSize({
      width: viewport.width,
      height: viewport.height,
    });

    await page.goto(TARGET_URL);
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: `/tmp/${viewport.name.toLowerCase()}.png`,
      fullPage: true,
    });
  }

  console.log('✅ 所有视口已测试');
  await browser.close();
})();
```

## 内联执行（简单任务）

对于快速一次性任务，您可以在不创建文件的情况下直接执行代码：

```bash
# 快速截图
cd $SKILL_DIR && node run.js "
const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();
await page.goto('http://localhost:3001');
await page.screenshot({ path: '/tmp/quick-screenshot.png', fullPage: true });
console.log('截图保存');
await browser.close();
"
```

**何时使用内联与文件：**

- **内联**：快速一次性任务（截图、检查元素是否存在、获取页面标题）
- **文件**：复杂测试、响应式设计检查、任何用户可能想要重新运行的任务

## 可用辅助函数

`lib/helpers.js` 中的可选实用函数：

```javascript
const helpers = require('./lib/helpers');

// 检测运行的开发服务器（关键 - 首先使用这个！）
const servers = await helpers.detectDevServers();
console.log('找到的服务器:', servers);

// 安全点击带重试
await helpers.safeClick(page, 'button.submit', { retries: 3 });

// 安全输入带清除
await helpers.safeType(page, '#username', 'testuser');

// 带时间戳的截图
await helpers.takeScreenshot(page, 'test-result');

// 处理 Cookie 横幅
await helpers.handleCookieBanner(page);

// 提取表格数据
const data = await helpers.extractTableData(page, 'table.results');
```

查看 `lib/helpers.js` 获取完整列表。

## 自定义 HTTP 头部

通过环境变量为所有 HTTP 请求配置自定义头部。适用于：

- 识别自动化流量到您的后端
- 获取 LLM 优化的响应（例如，纯文本错误而不是样式化的 HTML）
- 全局添加身份验证令牌

### 配置

**单个头部（常见情况）：**

```bash
PW_HEADER_NAME=X-Automated-By PW_HEADER_VALUE=playwright-skill \
  cd $SKILL_DIR && node run.js /tmp/my-script.js
```

**多个头部（JSON 格式）：**

```bash
PW_EXTRA_HEADERS='{"X-Automated-By":"playwright-skill","X-Debug":"true"}' \
  cd $SKILL_DIR && node run.js /tmp/my-script.js
```

### 工作原理

当使用 `helpers.createContext()` 时，会自动应用头部：

```javascript
const context = await helpers.createContext(browser);
const page = await context.newPage();
// 从此页面发出的所有请求都包含您的自定义头部
```

对于使用原始 Playwright API 的脚本，使用注入的 `getContextOptionsWithHeaders()`：

```javascript
const context = await browser.newContext(
  getContextOptionsWithHeaders({ viewport: { width: 1920, height: 1080 } }),
);
```

## 高级用法

有关 Playwright API 文档，请参阅 [API_REFERENCE.md](API_REFERENCE.md)：

- 选择器和定位器的最佳实践
- 网络拦截和 API 模拟
- 身份验证和会话管理
- 可视化回归测试
- 移动设备模拟
- 性能测试
- 调试技术
- CI/CD 集成

## 小贴士

- **关键：首先检测服务器** - 在为本地主机测试编写测试代码之前，始终运行 `detectDevServers()`
- **自定义头部** - 使用 `PW_HEADER_NAME`/`PW_HEADER_VALUE` 环境变量来识别自动化流量到您的后端
- **使用 /tmp 写入测试文件** - 写入 `/tmp/playwright-test-*.js`，绝对不要写入技能目录或用户的项目的任何地方
- **参数化 URL** - 将检测到的/提供的 URL 放在脚本顶部的 `TARGET_URL` 常量中
- **默认：可见浏览器** - 除非用户明确要求无头模式，否则始终使用 `headless: false`
- **无头模式** - 仅当用户明确要求“无头”或“后台”执行时，才使用 `headless: true`
- **放慢速度**：使用 `slowMo: 100` 使操作可见且易于跟踪
- **等待策略**：使用 `waitForURL`、`waitForSelector`、`waitForLoadState` 而不是固定超时
- **错误处理**：始终使用 try-catch 进行健壮的自动化
- **控制台输出**：使用 `console.log()` 跟踪进度并显示正在发生的事情

## 故障排除

**Playwright 未安装：**

```bash
cd $SKILL_DIR && npm run setup
```

**模块未找到：**
确保通过 `run.js` 包装器从技能目录运行

**浏览器未打开：**
检查 `headless: false` 并确保显示可用

**元素未找到：**
添加等待：`await page.waitForSelector('.element', { timeout: 10000 })`

## 示例用法

```
用户: "测试营销页面是否看起来良好"

Claude: 我将跨多个视口测试营销页面。让我先检测运行的服务器...
[运行: detectDevServers()]
[输出: 在端口 3001 上找到服务器]
我在 http://localhost:3001 上找到了您的开发服务器

[将自定义自动化脚本写入 /tmp/playwright-test-marketing.js 并参数化 URL]
[运行: cd $SKILL_DIR && node run.js /tmp/playwright-test-marketing.js]
[显示来自 /tmp 的结果和截图]
```

```
用户: "检查登录是否正确重定向"

Claude: 我将测试登录流程。首先，让我检查运行的服务器...
[运行: detectDevServers()]
[输出: 在端口 3000 和 3001 上找到服务器]
我找到了 2 个开发服务器。我应该测试哪一个？
- http://localhost:3000
- http://localhost:3001

用户: "使用 3001"

[将登录自动化写入 /tmp/playwright-test-login.js]
[运行: cd $SKILL_DIR && node run.js /tmp/playwright-test-login.js]
[报告: ✅ 登录成功，重定向到 /dashboard]
```

## 注意事项

- 每个自动化都是针对您的特定请求定制的
- 不限于预构建脚本 - 任何可能的浏览器任务都可以
- 自动检测运行的开发服务器以消除硬编码的 URL
- 测试脚本写入 `/tmp` 以自动清理（不会造成混乱）
- 通过 `run.js` 进行可靠的代码执行，具有正确的模块解析
- 逐步披露 - 仅在需要高级功能时加载 API_REFERENCE.md

## 何时使用
此技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必需的输入、权限、安全边界或成功标准，请停止并请求澄清。
