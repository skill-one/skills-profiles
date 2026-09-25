# 迁移到 Playwright

支持从 Cypress 或 Selenium 进行交互式迁移，并提供逐文件转换功能。

## 输入

`$ARGUMENTS` 参数可以是：
- `"from cypress"` — 迁移 Cypress 测试套件
- `"from selenium"` — 迁移 Selenium/WebDriver 测试
- 文件路径：转换特定的测试文件
- 空值：自动检测源框架

## 步骤

### 1. 检测源框架

使用 `Explore` 子代理扫描：
- `cypress/` 目录或 `cypress.config.ts` → Cypress
- `package.json` 依赖中的 `selenium`、`webdriver` → Selenium
- 带有 `selenium` 导入的 `.py` 测试文件 → Selenium (Python)

### 2. 评估迁移范围

统计文件并分类：

```
迁移评估：
- 总测试文件数：X
- Cypress 自定义命令：Y
- Cypress 固定文件：Z
- 预计工作量：[小|中|大]
```

| 规模 | 文件数 | 方法 |
|---|---|---|
| 小 (1-10) | 顺序转换 | 直接转换 |
| 中 (11-30) | 分组批量转换 (每组5个) | 使用子代理 |
| 大 (31+) | 使用 `/batch` | 并行转换 (`/batch`) |

### 3. 设置 Playwright (如果尚未配置)

如果 Playwright 未配置，请先运行 `/pw:pw-init`。

### 4. 转换文件

对每个文件应用适当的映射：

#### Cypress → Playwright

加载 `cypress-mapping.md` 获取完整参考。

关键转换：
```
cy.visit(url)           → page.goto(url)
cy.get(selector)        → page.locator(selector) 或 page.getByRole(...)
cy.contains(text)       → page.getByText(text)
cy.find(selector)       → locator.locator(selector)
cy.click()              → locator.click()
cy.type(text)           → locator.fill(text)
cy.should('be.visible') → expect(locator).toBeVisible()
cy.should('have.text')  → expect(locator).toHaveText(text)
cy.intercept()          → page.route()
cy.wait('@alias')       → page.waitForResponse()
cy.fixture()            → JSON 导入或测试数据文件
```

**Cypress 自定义命令** → Playwright 固定文件或辅助函数
**Cypress 插件** → Playwright 配置或固定文件
**`before`/`beforeEach`** → `test.beforeAll()` / `test.beforeEach()`

#### Selenium → Playwright

加载 `selenium-mapping.md` 获取完整参考。

关键转换：
```
driver.get(url)                    → page.goto(url)
driver.findElement(By.id('x'))     → page.locator('#x') 或 page.getByTestId('x')
driver.findElement(By.css('.x'))   → page.locator('.x') 或 page.getByRole(...)
element.click()                    → locator.click()
element.sendKeys(text)             → locator.fill(text)
element.getText()                  → locator.textContent()
WebDriverWait + ExpectedConditions → expect(locator).toBeVisible()
driver.switchTo().frame()          → page.frameLocator()
Actions                            → locator.hover(), locator.dragTo()
```

### 5. 升级定位器

在转换过程中，将选择器升级为 Playwright 最佳实践：
- `#id` → `getByTestId()` 或 `getByRole()`
- `.class` → `getByRole()` 或 `getByText()`
- `[data-testid]` → `getByTestId()`
- XPath → 基于角色的定位器

### 6. 转换自定义命令 / 工具

- Cypress 自定义命令 → 通过 `test.extend()` 转换为 Playwright 自定义固定文件
- Selenium 页面对象 → Playwright 页面对象 (保持结构，更新 API)
- 共享辅助工具 → TypeScript 工具函数

### 7. 验证每个转换后的文件

转换每个文件后：

```bash
npx playwright test <converted-file> --reporter=list
```

在处理下一个文件前，修复任何编译或运行时错误。

### 8. 清理

所有文件转换完成后：
- 从 `package.json` 中移除 Cypress/Selenium 依赖
- 移除旧配置文件 (`cypress.config.ts` 等)
- 更新 CI 工作流程以使用 Playwright
- 更新 README 中的新测试命令

在删除任何内容前请询问用户。

## 输出

- 转换摘要：已转换文件数，总迁移测试数
- 无法自动转换的测试 (需要手动干预)
- 更新后的 CI 配置
- 测试运行结果的对比 (转换前/后)
