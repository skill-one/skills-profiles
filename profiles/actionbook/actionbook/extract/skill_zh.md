## 何时使用此技能

当用户希望从网站**获取数据**时激活：

- "从本页面提取所有产品价格"
- "抓取结果表格"
- "从arXiv搜索结果中提取作者列表和标题"
- "收集本页面的所有职位列表"
- "获取此仪表板表格中的数据"
- "从...收集评论分数"
- "下载所有链接/图片/卡片"

交付成果始终是**两个工件**：

1. **可执行的Playwright脚本** — 一个独立的`.cjs`文件，可以在不使用Actionbook的情况下在运行时重现提取。
2. **提取的数据** — JSON（默认）、CSV或用户指定的格式写入磁盘。

## 决策策略

将Actionbook用作**条件加速器**，而不是强制步骤。目标是可靠的选择器，并走最短路径。

```
用户请求
  │
  ├─► actionbook搜索"<网站> <意图>"
  │     ├─ 健康评分 ≥ 70%的结果  ──► actionbook获取"<ID>" ──► 使用选择器
  │     └─ 无结果 / 低评分  ──► 回退
  │
  └─► 回退: actionbook浏览器打开<URL>
        ├─ actionbook浏览器快照   （可访问性树 → 查找选择器）
        ├─ actionbook浏览器截图 (视觉确认)
        └─ 通过DOM检查手动发现选择器
```

**选择器来源的优先级顺序：**

| 优先级 | 来源 | 何时 |
|----------|------|------|
| 1 | `actionbook获取` | 网站被索引，健康评分 ≥ 70% |
| 2 | `actionbook浏览器快照` | 未被索引或选择器过时 |
| 3 | 通过截图+快照进行DOM检查 | 复杂的SPA / 动态内容 |

**不可协商的规则：** 如果`搜索+获取`已经为所需字段提供可用的选择器，则从`获取`选择器开始，默认不要跳转到完整回退（`快照`/`截图`）。例外：轻量级机制探测（用于水合/虚拟化/分页）允许在运行时行为可能影响脚本正确性的情况下。仅在探测/样本验证指示选择器缺失或不稳定时，才升级到`快照`/`截图`。

## 机制感知脚本策略

网站使用会破坏简单抓取的模式。生成的Playwright脚本**必须**考虑这些：

### 流式传输 / SSR / RSC水合

页面可能先渲染一个外壳，然后流式传输或水合内容。

```javascript
// 等待水合完成 — 不仅仅是DOMContentLoaded
await page.waitForSelector('[data-item]', { state: 'attached' });
await page.waitForFunction(() => {
  const items = document.querySelectorAll('[data-item]');
  return items.length > 0 && !document.querySelector('[data-pending]');
});
```

**检测线索：** React根节点带有`data-reactroot`，Next.js的`__NEXT_DATA__`，空容器在JS运行后填充。如果`actionbook浏览器文本"<选择器>"`返回空，但截图显示内容，则水合未完成。

### 虚拟化列表 / 虚拟DOM

DOM中只有可见行存在。滚动渲染新行并销毁旧行。

```javascript
// 虚拟化列表的滚动收集循环（滚动容器感知）
const allItems = [];
const maxScrolls = 50;
let scrolls = 0;

const container = await page.$('<滚动容器选择器>');
if (!container) throw new Error('滚动容器未找到');

let previousTop = await container.evaluate(el => el.scrollTop);
while (scrolls < maxScrolls) {
  const items = await page.$$eval('[data-row]', rows =>
    rows.map(r => ({ text: r.textContent.trim() }))
  );
  for (const item of items) {
    if (!allItems.find(i => i.text === item.text)) allItems.push(item);
  }

  await container.evaluate(el => el.scrollBy(0, 600));
  await page.waitForTimeout(300);

  const currentTop = await container.evaluate(el => el.scrollTop);
  if (currentTop === previousTop) break;

  previousTop = currentTop;
  scrolls += 1;
}
```

**检测线索：** 容器具有固定高度并带有`overflow: auto/scroll`，DOM中的行数远小于声明的总数，行具有`transform: translateY(...)`或`position: absolute; top: ...px`。

### 无限滚动 / 懒加载

当用户滚动到底部附近时，新内容会追加。

```javascript
// 滚动到底部直到不再加载新内容（带无增长容忍度）
let itemCount = 0;
let noGrowthStreak = 0;
const maxScrolls = 80;
let scrolls = 0;

while (scrolls < maxScrolls && noGrowthStreak < 3) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1200);

  const newCount = await page.$$eval('.item', els => els.length);
  if (newCount > itemCount) {
    itemCount = newCount;
    noGrowthStreak = 0;
  } else {
    noGrowthStreak += 1;
  }

  scrolls += 1;
}
```

**检测线索：** 页面JS中的Intersection Observer，"加载更多"按钮，底部哨兵元素，滚动时触发的网络请求。

### 分页

多页结果隐藏在"下一页"按钮或编号页面后面。

```javascript
// 点击式分页（导航感知，SPA安全）
const allData = [];
const maxPages = 50;
let pageIndex = 0;
while (pageIndex < maxPages) {
  const pageData = await page.$$eval('.result-item', items =>
    items.map(el => ({ title: el.querySelector('h3')?.textContent?.trim() }))
  );
  allData.push(...pageData);

  const nextBtn = await page.$('a.next-page:not([disabled])');
  if (!nextBtn) break;

  const previousUrl = page.url();
  const previousFirstItem = await page
    .$eval('.result-item', el => el.textContent?.trim() || '')
    .catch(() => '');

  await nextBtn.click();

  // 点击后检测仅：前进必须由此点击引起
  const advanced = await Promise.any([
    page
      .waitForURL(url => url.toString() !== previousUrl, { timeout: 5000 })
      .then(() => true),
    page
      .waitForFunction(
        prev => {
          const first = document.querySelector('.result-item');
          return !!first && (first.textContent || '').trim() !== prev;
        },
        previousFirstItem,
        { timeout: 5000 }
      )
      .then(() => true),
  ]).catch(() => false);

  if (!advanced) break;

  await page.waitForLoadState('networkidle').catch(() => {});
  pageIndex += 1;
}
```

## 执行链

### 第一步：理解目标

从用户请求中识别：
- **URL** — 要提取的页面
- **数据形状** — 需要哪些字段/列
- **范围** — 单页、分页、无限滚动或多页爬取
- **输出格式** — JSON（默认）、CSV或其他

### 第二步：获取选择器并选择执行路径

```bash
# 首先尝试Actionbook索引
actionbook搜索"<网站> <数据描述>" --domain <域名>

# 如果结果良好（健康度 ≥ 70%），获取完整选择器
actionbook获取"<ID>"
```

严格使用此路由：

- **路径A（默认当`获取`良好时）：** 请求的字段由`获取`选择器覆盖且质量可接受。
  - 从`获取`选择器开始并快速进入脚本草稿。
  - 您可以在最终确定脚本策略之前运行轻量级机制探测（`browser文本`，快速滚动检查）。
  - **除非探测/样本验证显示不匹配，否则不要在最终草稿之前运行完整回退（`快照`/`截图`）。**
  - 字段映射必须默认为`获取`选择器并标记来源为`actionbook_get`。

- **路径B（部分/不稳定）：** `获取`存在但所需字段缺失，选择器解析为0个元素，或验证失败。
  - 仅针对失败的字段/步骤运行目标回退。

- **路径C（无可用覆盖）：** 搜索/获取无可用结果。
  - 运行完整回退发现。

### 第三步：仅当需要时探测页面机制并回退

路径A机制探测时机：
- 在最终脚本草稿**之前**或**样本验证期间**运行最小探测。
- 在任何探测命令之前，确保打开正确的页面上下文：
  - `actionbook浏览器打开"<URL>"`（如果当前标签上下文未知/陈旧）
- 如果探测/样本运行指示不匹配（缺少行，选择器不稳定，分页行为错误），升级到路径B目标回退。

回退发现按路径：

**路径B目标回退（仅针对失败的字段/步骤）：**

```bash
actionbook浏览器打开"<URL>"     # 如果尚未打开
actionbook浏览器快照          # 聚焦于失败的字段/容器映射
# actionbook浏览器截图      # 可选的视觉确认失败区域
```

**路径C完整回退（无可用覆盖）：**

```bash
actionbook浏览器打开 "<URL>"
actionbook浏览器快照
actionbook浏览器截图
```

机制探测（在脚本策略需要确认时运行）：

```bash
# 水合/流式传输检查
actionbook浏览器文本 "<容器选择器>"

# 无限滚动快速信号（显式在之前/之后决策）
actionbook浏览器评估 "document.querySelectorAll('<项选择器>').length"   # 之前
actionbook浏览器点击 "<滚动容器选择器或body>"                    # 聚焦滚动上下文
actionbook浏览器评估 "const c=document.querySelector('<滚动容器选择器>') || document.scrollingElement; c.scrollBy(0, c.clientHeight || window.innerHeight);"
actionbook浏览器评估 "document.querySelectorAll('<项选择器>').length"   # 之后
# 如果计数增加，则将页面视为懒加载/无限滚动。
```

回退触发条件：
- `actionbook获取`无法映射所有所需字段。
- `actionbook获取`选择器在样本运行中返回空/不稳定值。
- 运行时行为与预期机制冲突（例如，虚拟化容器，延迟水合）。

### 第四步：生成Playwright脚本

编写一个独立的Playwright脚本（`extract_<域名>_<slug>.cjs`），该脚本：

1. 导航到目标URL。
2. 等待正确的就绪信号（不仅仅是`load` — 见机制）。
3. 处理检测到的机制（虚拟滚动，分页等）。
4. 将数据提取为结构化对象。
5. 写入磁盘（`JSON.stringify` / CSV）。
6. 关闭浏览器。
7. 强制执行护栏（`maxPages`，`maxScrolls`，超时预算）以避免无限循环。

**脚本模板：**

```javascript
// extract_<域名>_<slug>.cjs
// 由Actionbook提取技能生成
// 使用方式：node extract_<域名>_<slug>.cjs

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('<URL>', { waitUntil: 'domcontentloaded' });

  // -- 等待就绪 --
  await page.waitForSelector('<容器>', { state: 'visible' });

  // -- 提取 --
  const data = await page.$$eval('<项选择器>', items =>
    items.map(el => ({
      // 从用户请求映射的字段
    }))
  );

  // -- 输出 --
  const fs = require('fs');
  fs.writeFileSync('output.json', JSON.stringify(data, null, 2));
  console.log(`提取了${data.length}项 → output.json`);

  await browser.close();
})();
```

### 第五步：执行和验证

运行脚本以确认其工作：

```bash
node extract_<域名>_<slug>.cjs
```

**验证规则：**

| 检查 | 通过条件 |
|-------|---------------|
| 脚本退出0 | 无运行时错误 |
| 输出文件存在 | 非空文件写入 |
| 记录数 > 0 | 至少提取了一项 |
| 无null/空字段 | 每个声明的字段在≥ 90%的记录中都有值 |
| 数据与页面匹配 | 对`actionbook浏览器文本`检查首尾记录 |

如果验证失败，请检查输出，调整选择器或等待策略，然后重新运行。

### 第六步：交付

向用户展示：
1. **脚本路径** — 他们可以随时重新运行的`.cjs`文件。
2. **数据路径** — 输出JSON/CSV文件。
3. **记录数** — 提取了多少项。
4. **备注** — 任何特定于机制的注意事项（例如，"此网站使用无限滚动；脚本默认滚动50页"）。

## 输出契约

每次`extract`调用都会产生：

| 工件 | 路径 | 格式 |
|----------|------|------|
| Playwright脚本 | `./extract_<域名>_<slug>.cjs` | 独立的Node.js脚本使用`playwright` |
| 提取的数据 | `./output.json`（默认）或用户指定路径 | JSON对象数组（默认），CSV或用户指定 |

脚本必须是**可重新运行**的 — 用户应该能够在不安装Actionbook的情况下稍后执行它，只要运行时环境中提供Node.js + Playwright即可。

## 选择器优先级

当从`actionbook获取`提供多个选择器类型时：

| 优先级 | 类型 | 原因 |
|----------|------|------|
| 1 | `data-testid` | 稳定，面向测试，很少变化 |
| 2 | `aria-label` | 驱动可访问性，语义上有意义 |
| 3 | CSS选择器 | 结构化，可能在重新设计时破坏 |
| 4 | XPath | 最后手段，最脆弱 |

## 错误处理

| 错误 | 操作 |
|-------|--------|
| `actionbook搜索`返回无结果 | 回退到`快照` + `截图` |
| 选择器返回0个元素 | 重新快照，与截图比较，更新选择器 |
| 脚本超时 | 添加更长的`waitForTimeout`，检查反爬虫措施 |
| 部分数据（某些字段为空） | 检查内容是否懒加载；添加滚动/等待 |
| 反爬虫 / CAPTCHA | 告知用户；建议使用`headless: false`或通过`actionbook setup`扩展模式使用他们自己的浏览器会话 |
