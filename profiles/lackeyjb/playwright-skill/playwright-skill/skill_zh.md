# Playwright 浏览器自动化

根据用户请求编写和执行聚焦的 Playwright 脚本。优先使用该技能的执行器和辅助工具，但在需要时使用完整的 Playwright API。

## 路径解析

此技能可以安装在多个位置，因此首先解析其目录。将 `SKILL_DIR` 设置为包含此 SKILL.md 文件的目录，然后按如下方式运行命令：

```bash
export SKILL_DIR=<包含此 SKILL.md 文件的绝对路径>
export TMP_DIR="$(node -p 'require("node:os").tmpdir()')"
```

如果命令之间的 shell 状态不持久化，则在每个命令中用字面路径替换 `$SKILL_DIR` 和 `$TMP_DIR`。

常见的安装路径：

- 插件系统：`~/.claude/plugins/marketplaces/playwright-skill/skills/playwright-skill`
- 手动全局：`~/.claude/skills/playwright-skill`
- 项目特定：`<项目>/.claude/skills/playwright-skill`

## 工作流程

1. 对于本地工作，在编写 URL 之前检测正在运行的服务：

   ```bash
   node -e "require('$SKILL_DIR/lib/helpers').detectDevServers().then(s => console.log(JSON.stringify(s)))"
   ```

   自动使用唯一结果。当有多个结果时，询问要使用哪个 URL。当不存在时，请求 URL 或提供启动服务。

2. 除非用户要求将它们保存在项目中，否则将可重用脚本写入 `$TMP_DIR/playwright-test-*.js`。使用 `PW_SCRIPT_DIR` 保留脚本。

3. 默认情况下使用可见浏览器。仅在请求时或环境没有显示器时使用 `headless: true`。

4. 将目标 URL 放在常量或环境变量中。

5. 使用 `node "$SKILL_DIR/run.js" <script.js>` 运行脚本。

6. 报告操作、失败和工件路径。在检查结果页面之前不要声称成功。

## 设置

运行一次：

```bash
cd "$SKILL_DIR" && npm run setup
```

这将安装 Playwright 和 Chromium。当需要 Firefox 或 WebKit 时，使用 `cd "$SKILL_DIR" && npm run install-all-browsers`。

## 最小示例

```javascript
const os = require('node:os');
const path = require('node:path');
const { chromium } = require('playwright');

const targetUrl = process.env.TARGET_URL || 'http://localhost:3000';
const artifactDir = process.env.PW_ARTIFACT_DIR || os.tmpdir();

(async () => {
  const browser = await chromium.launch({ headless: false });
  try {
    const page = await browser.newPage();
    await page.goto(targetUrl);
    console.log('Page loaded:', await page.title());
    await page.screenshot({ path: path.join(artifactDir, 'page.png'), fullPage: true });
  } finally {
    await browser.close();
  }
})();
```

运行它：

```bash
node "$SKILL_DIR/run.js" "$TMP_DIR/playwright-test-page.js"
```

对于简短的临时任务，使用内联执行：

```bash
node "$SKILL_DIR/run.js" -e "const browser = await chromium.launch({headless: false}); try { const page = await browser.newPage(); await page.goto('https://example.com'); console.log(await page.title()); } finally { await browser.close(); }"
```

`-e` 进程在代码片段稳定后立即退出，因此请在代码片段内关闭浏览器。

## 当前 Playwright 模式

优先使用描述用户所见内容的定位器，按以下顺序：

1. `page.getByRole()` 使用可访问名称
2. `page.getByLabel()` 用于表单控件
3. `page.getByText()` 用于可见内容
4. `page.getByTestId()` 当应用程序提供测试契约时

操作会自动等待可操作性。使用 Web 首先断言或定位器的 `waitFor()` 而不是 `waitForSelector()`、固定睡眠或 `networkidle`。

```javascript
await page.getByLabel('Email').fill('test@example.com');
await page.getByRole('button', { name: 'Sign in' }).click();
await page.waitForURL('**/dashboard');
await page.getByRole('heading', { name: 'Dashboard' }).waitFor();
```

## 常见任务

### 响应式检查

```javascript
{
  const os = require('node:os');
  const path = require('node:path');

  const artifactDir = process.env.PW_ARTIFACT_DIR || os.tmpdir();
  const viewports = [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'mobile', width: 390, height: 844 },
  ];

  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto(targetUrl);
    await page.screenshot({ path: path.join(artifactDir, `${viewport.name}.png`), fullPage: true });
  }
}
```

### 登录流程

使用用户提供的测试凭证。永远不要编造或暴露真实凭证。验证导航和登录后元素。

```javascript
await page.goto(`${targetUrl}/login`);
await page.getByLabel('Email').fill(process.env.TEST_EMAIL);
await page.getByLabel('Password').fill(process.env.TEST_PASSWORD);
await page.getByRole('button', { name: /sign in|log in/i }).click();
await page.waitForURL('**/dashboard');
await page.getByRole('heading', { name: /dashboard/i }).waitFor();
```

### 保存脚本和工件

```bash
PW_SCRIPT_DIR=./playwright-tests node "$SKILL_DIR/run.js" "$TMP_DIR/playwright-test-login.js"
PW_ARTIFACT_DIR=./playwright-artifacts node "$SKILL_DIR/run.js" "$TMP_DIR/playwright-test-page.js"
```

`PW_SCRIPT_DIR` 在执行前复制基于文件的脚本，并在文件名已存在时添加时间戳。`PW_ARTIFACT_DIR` 控制辅助工具生成的截图输出；默认是操作系统临时目录。

### 连接到现有 Chrome 会话

启动带有远程调试功能的 Chrome，然后使用 Playwright 连接：

```javascript
const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const page = browser.contexts()[0].pages()[0];
```

这会重用该会话中的 cookie 和扩展。除非用户明确要求，否则不要用它来处理秘密；连接的浏览器具有用户的访问权限。

## 辅助工具

```javascript
const helpers = require(`${process.env.PW_SKILL_DIR}/lib/helpers`);

const servers = await helpers.detectDevServers();
const browser = await helpers.launchBrowser('chromium');
const context = await helpers.createContext(browser);
const page = await context.newPage();
await helpers.handleCookieBanner(page);
await helpers.takeScreenshot(page, 'result');
```

可用的辅助工具是 `detectDevServers`、`getExtraHeadersFromEnv`、`launchBrowser`、`createContext`、`handleCookieBanner` 和 `takeScreenshot`。对于操作、等待、提取、认证、表格和重试，直接使用 Playwright 定位器和断言。

## 配置

- `PW_BROWSER`: `chromium`、`firefox` 或 `webkit` 用于 `launchBrowser()`。
- `PW_CHANNEL`: 安装的浏览器频道，例如 `chrome` 或 `msedge`。
- `PW_EXECUTABLE_PATH`: 显式的浏览器可执行路径。
- `PW_HEADLESS`: `true` 或 `false`；默认为可见模式。
- `SLOW_MO`: 操作延迟（毫秒）。
- `PW_HEADER_NAME` 和 `PW_HEADER_VALUE`: 一个额外的 HTTP 头。
- `PW_EXTRA_HEADERS`: 额外的 HTTP 头的 JSON 对象。
- `PW_SCRIPT_DIR`: 保留基于文件的脚本的目录。
- `PW_ARTIFACT_DIR`: 辅助工具生成的截图目录。

参见 [API_REFERENCE.md](API_REFERENCE.md) 了解网络拦截、API 模拟、认证状态、视频、视觉检查、设备模拟和 CI 模式。
