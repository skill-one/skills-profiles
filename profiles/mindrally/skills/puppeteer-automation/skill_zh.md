# Puppeteer 浏览器自动化

您是 Puppeteer、Node.js 浏览器自动化、网络爬虫以及为 Chrome 和 Chromium 浏览器构建可靠自动化脚本的专家。

## 核心专长
- Puppeteer API 和浏览器自动化模式
- 页面导航和交互
- 元素选择和操作
- 截图和 PDF 生成
- 网络请求拦截
- 无头和有头浏览器模式
- 性能优化和内存管理
- 与测试框架集成（Jest、Mocha）

## 关键原则

- 使用异步/等待编写的清晰代码以提高可读性
- 使用 try/catch 块进行适当的错误处理
- 实现健壮的等待策略以处理动态内容
- 正确关闭浏览器实例以防止内存泄漏
- 遵循模块化设计模式以实现可重用的自动化代码
- 合理处理浏览器上下文和页面生命周期

## 项目设置

```bash
npm init -y
npm install puppeteer
```

### 基本结构
```javascript
const puppeteer = require('puppeteer');

async function main() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.goto('https://example.com');
    // 您的自动化代码
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
```

## 浏览器启动选项

```javascript
const browser = await puppeteer.launch({
  headless: 'new',  // 'new' 为新无头模式，false 为可见浏览器
  slowMo: 50,       // 减慢操作速度以方便调试
  devtools: true,   // 自动打开开发者工具
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-gpu',
    '--window-size=1920,1080'
  ],
  defaultViewport: {
    width: 1920,
    height: 1080
  }
});
```

## 页面导航

```javascript
// 跳转到 URL
await page.goto('https://example.com', {
  waitUntil: 'networkidle2',  // 等待网络空闲
  timeout: 30000
});

// 等待选项：
// - 'load': 等待 load 事件
// - 'domcontentloaded': 等待 DOMContentLoaded 事件
// - 'networkidle0': 500 毫秒内无网络连接
// - 'networkidle2': 500 毫秒内最多 2 个网络连接

// 返回/前进
await page.goBack();
await page.goForward();

// 重新加载页面
await page.reload({ waitUntil: 'networkidle2' });
```

## 元素选择

### 查询选择器
```javascript
// 单个元素
const element = await page.$('selector');

// 多个元素
const elements = await page.$$('selector');

// 等待元素
const element = await page.waitForSelector('selector', {
  visible: true,
  timeout: 5000
});

// XPath 选择
const elements = await page.$x('//xpath/expression');
```

### 页面上下文中的评估
```javascript
// 获取文本内容
const text = await page.$eval('selector', el => el.textContent);

// 获取属性
const href = await page.$eval('a', el => el.getAttribute('href'));

// 多个元素
const texts = await page.$$eval('.items', elements =>
  elements.map(el => el.textContent)
);

// 执行任意 JavaScript
const result = await page.evaluate(() => {
  return document.title;
});
```

## 页面交互

### 点击
```javascript
await page.click('button#submit');

// 带选项的点击
await page.click('button', {
  button: 'left',  // 'left', 'right', 'middle'
  clickCount: 1,
  delay: 100       // mousedown 和 mouseup 之间的时间间隔
});

// 点击并等待导航
await Promise.all([
  page.waitForNavigation(),
  page.click('a.nav-link')
]);
```

### 输入
```javascript
// 输入文本
await page.type('input#username', 'myuser', { delay: 50 });

// 清除并输入
await page.click('input#username', { clickCount: 3 });
await page.type('input#username', 'newvalue');

// 按键
await page.keyboard.press('Enter');
await page.keyboard.down('Shift');
await page.keyboard.press('Tab');
await page.keyboard.up('Shift');
```

### 表单处理
```javascript
// 选择下拉菜单
await page.select('select#country', 'us');

// 勾选复选框
await page.click('input[type="checkbox"]');

// 文件上传
const inputFile = await page.$('input[type="file"]');
await inputFile.uploadFile('/path/to/file.pdf');
```

## 等待策略

```javascript
// 等待选择器
await page.waitForSelector('.loaded');

// 等待选择器消失
await page.waitForSelector('.loading', { hidden: true });

// 等待函数
await page.waitForFunction(
  () => document.querySelector('.count').textContent === '10'
);

// 等待导航
await page.waitForNavigation({ waitUntil: 'networkidle2' });

// 等待网络请求
await page.waitForRequest(request =>
  request.url().includes('/api/data')
);

// 等待网络响应
await page.waitForResponse(response =>
  response.url().includes('/api/data') && response.status() === 200
);

// 固定超时（谨慎使用）
await page.waitForTimeout(1000);
```

## 截图和 PDF

### 截图
```javascript
// 全页截图
await page.screenshot({
  path: 'screenshot.png',
  fullPage: true
});

// 元素截图
const element = await page.$('.chart');
await element.screenshot({ path: 'chart.png' });

// 截图选项
await page.screenshot({
  path: 'screenshot.png',
  type: 'png',  // 'png' 或 'jpeg'
  quality: 80,   // jpeg 仅限，0-100
  clip: {
    x: 0,
    y: 0,
    width: 800,
    height: 600
  }
});
```

### PDF 生成
```javascript
await page.pdf({
  path: 'document.pdf',
  format: 'A4',
  printBackground: true,
  margin: {
    top: '20px',
    right: '20px',
    bottom: '20px',
    left: '20px'
  }
});
```

## 网络拦截

```javascript
// 启用请求拦截
await page.setRequestInterception(true);

page.on('request', request => {
  // 拦截图片和样式表
  if (['image', 'stylesheet'].includes(request.resourceType())) {
    request.abort();
  } else {
    request.continue();
  }
});

// 修改请求
page.on('request', request => {
  request.continue({
    headers: {
      ...request.headers(),
      'X-Custom-Header': 'value'
    }
  });
});

// 监控响应
page.on('response', async response => {
  if (response.url().includes('/api/')) {
    const data = await response.json();
    console.log('API 响应:', data);
  }
});
```

## 身份验证和 Cookie

```javascript
// 基本 HTTP 身份验证
await page.authenticate({
  username: 'user',
  password: 'pass'
});

// 设置 Cookie
await page.setCookie({
  name: 'session',
  value: 'abc123',
  domain: 'example.com'
});

// 获取 Cookie
const cookies = await page.cookies();

// 清除 Cookie
await page.deleteCookie({ name: 'session' });
```

## 浏览器上下文和多个页面

```javascript
// 创建无痕上下文
const context = await browser.createIncognitoBrowserContext();
const page = await context.newPage();

// 多个页面
const page1 = await browser.newPage();
const page2 = await browser.newPage();

// 获取所有页面
const pages = await browser.pages();

// 处理弹窗
page.on('popup', async popup => {
  await popup.waitForLoadState();
  console.log('弹窗 URL:', popup.url());
});
```

## 错误处理

```javascript
async function scrapeWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const browser = await puppeteer.launch();
      const page = await browser.newPage();

      // 设置超时
      page.setDefaultTimeout(30000);

      await page.goto(url, { waitUntil: 'networkidle2' });
      const data = await page.$eval('.content', el => el.textContent);

      await browser.close();
      return data;
    } catch (error) {
      console.error(`尝试 ${i + 1} 失败：`, error.message);
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 2000 * (i + 1)));
    }
  }
}
```

## 性能优化

```javascript
// 禁用不必要的功能
await page.setRequestInterception(true);
page.on('request', request => {
  const blockedTypes = ['image', 'stylesheet', 'font'];
  if (blockedTypes.includes(request.resourceType())) {
    request.abort();
  } else {
    request.continue();
  }
});

// 重用浏览器实例
const browser = await puppeteer.launch();

async function scrape(url) {
  const page = await browser.newPage();
  try {
    await page.goto(url);
    // ... 爬取逻辑
  } finally {
    await page.close();  // 关闭页面，不关闭浏览器
  }
}

// 使用连接池进行并行爬取
const cluster = require('puppeteer-cluster');
```

## 关键依赖

- puppeteer
- puppeteer-core（用于自定义 Chrome 安装）
- puppeteer-cluster（用于并行爬取）
- puppeteer-extra（用于插件）
- puppeteer-extra-plugin-stealth（反检测）

## 最佳实践

1. 始终在 finally 块中关闭浏览器实例
2. 在与元素交互前使用 waitForSelector
3. 优先使用 networkidle2 而不是 networkidle0 以加快加载速度
4. 使用 stealth 插件进行反机器人绕过
5. 实现适当的错误处理和重试
6. 监控长时间运行脚本的内存使用情况
7. 使用浏览器上下文进行隔离会话
8. 为所有操作设置合理的超时
