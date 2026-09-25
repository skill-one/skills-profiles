# 测试模块

本技能将指导您在 AEM Edge Delivery Services 项目中测试代码更改。测试遵循价值与成本原则：当测试带来的价值超过其创建和维护成本时，才创建和维护测试。

**关键：浏览器验证是强制性的。您必须提供在真实浏览器环境中进行功能测试的证据，才能完成此技能。**

## 相关技能

- **content-driven-development**：CDD 阶段创建的内容测试作为测试的基础
- **building-blocks**：在步骤 5 中调用此技能进行综合测试
- **block-collection-and-party**：可能提供来自类似模块的参考测试模式

## 何时使用此技能

使用此技能：
- ✅ 实施或修改模块后
- ✅ 核心脚本更改后（scripts.js、delayed.js、aem.js）
- ✅ 样式更改后（styles.css、lazy-styles.css）
- ✅ 影响功能的配置更改后
- ✅ 在打开任何包含代码更改的拉取请求之前

此技能通常由 **building-blocks** 技能在步骤 5（测试实施）中调用。

## 测试工作流

跟踪您的进度：

- [ ] 步骤 1：运行代码检查并修复问题
- [ ] 步骤 2：执行浏览器验证（强制）
- [ ] 步骤 3：确定是否需要单元测试（可选）
- [ ] 步骤 4：运行现有测试并验证它们通过

## 步骤 1：运行代码检查

**首先运行代码检查以捕获代码质量问题：**

```bash
npm run lint
```

**如果代码检查失败：**
```bash
npm run lint:fix
```

**手动修复自动修复无法处理的剩余问题。**

**成功标准：**
- ✅ 代码检查通过且无错误
- ✅ 代码遵循项目标准

**完成时：** `npm run lint` 通过且无错误

---

## 步骤 2：浏览器验证（强制）

**关键：您必须在真实浏览器中测试并提供证据。**

### 要测试的内容

在浏览器中加载测试内容 URL 并验证：
- ✅ 模块/功能正确渲染
- ✅ 响应式行为（移动端、平板、桌面视图）
- ✅ 无控制台错误
- ✅ 视觉外观符合要求/验收标准
- ✅ 交互行为正常工作（如适用）
- ✅ 所有变体正确渲染（如适用）

### 如何测试

**根据您可用的工具选择最合适的方法：**

**选项 1：浏览器/Playwright MCP（推荐）**

如果您有 MCP 浏览器或 Playwright 工具，直接使用它们：
- 导航到测试内容 URL
- 拍摄可访问性快照以检查渲染内容（交互性首选）
- 在不同视图下拍摄截图进行视觉验证
  - 考虑全页截图和模块特定元素的截图
- 根据需要与元素交互
- 对于有工具访问权限的代理来说最有效

**选项 2：Playwright 自动化**

编写一个（或多个）临时测试脚本来使用 playwright 验证功能并捕获快照/截图以供检查和验证。

```javascript
// test-my-block.js（临时 - 不要提交）
import { chromium } from 'playwright';

async function test() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  // 导航并等待模块
  await page.goto('http://localhost:3000/path/to/test');
  await page.waitForSelector('.my-block');

  // 检查可访问性树（验证结构有用）
  const accessibilityTree = await page.accessibility.snapshot();
  console.log('可访问性树:', JSON.stringify(accessibilityTree, null, 2));
  
  // 可选地保存到文件以便于分析
  await require('fs').promises.writeFile(
    'accessibility-tree.json',
    JSON.stringify(accessibilityTree, null, 2)
  );

  // 测试视图并拍摄截图
  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: 'mobile.png', fullPage: true });
  await page.locator('.my-block').screenshot({ path: 'mobile-block.png' });

  await page.setViewportSize({ width: 768, height: 1024 });
  await page.screenshot({ path: 'tablet.png', fullPage: true });
  await page.locator('.my-block').screenshot({ path: 'tablet-block.png' });

  await page.setViewportSize({ width: 1200, height: 800 });
  await page.screenshot({ path: 'desktop.png', fullPage: true });
  await page.locator('.my-block').screenshot({ path: 'desktop-block.png' });

  // 检查控制台错误
  page.on('console', msg => console.log('浏览器:', msg.text()));

  await browser.close();
}

test().catch(console.error);
```

运行：`node test-my-block.js` 然后删除脚本并分析结果文件。

**选项 3：手动浏览器测试**

使用标准浏览器和开发者工具：
1. 导航到测试内容：`http://localhost:3000/path/to/test/content`
2. 使用浏览器开发者工具响应式模式测试视图：
   - 移动端：<600px（例如 375px）
   - 平板：<600-900px（例如 768px）
   - 桌面端：>900px（例如 1200px）
3. 每个视图下检查控制台错误
4. 拍摄截图作为证据（浏览器截图工具或开发者工具）

### 与验收标准的验证

**如果提供验收标准（来自 CDD 步骤 2）：**
- 审查每个标准
- 测试提到的特定场景
- 验证所有标准都满足

**如果提供设计/模型截图：**
- 将实现与设计进行比较
- 验证视觉对齐
- 记录任何有意偏离

### 测试证据

**您必须提供：**
- ✅ 浏览器中测试内容的截图（至少一个视图）
- ✅ 确认无控制台错误
- ✅ 确认满足验收标准（如果提供）

**成功标准：**
- ✅ 所有测试内容加载并正确渲染
- ✅ 跨视图验证响应式行为
- ✅ 无控制台错误
- ✅ 拍摄截图作为证据
- ✅ 验证验收标准（如果提供）

**完成时：** 浏览器测试完成并附有截图作为证据

---

## 步骤 3：单元测试（可选）

**确定此更改是否需要单元测试。**

**编写单元测试时：**
- ✅ 逻辑密集型函数（计算、转换）
- ✅ 跨多个模块使用的工具函数
- ✅ 数据处理或 API 集成
- ✅ 复杂的业务逻辑

**跳过单元测试时：**
- ❌ 简单的 DOM 操作
- ❌ 仅 CSS 更改
- ❌ 简单的装饰逻辑
- ❌ 浏览器中易于验证的更改

**有关要测试内容的指导：** 参考 [references/testing-philosophy.md](references/testing-philosophy.md)

**如果需要单元测试：**

```bash
# 验证测试设置（未配置时参考 references/vitest-setup.md）
npm test

# 为工具函数编写测试
# test/utils/my-utility.test.js
import { describe, it, expect } from 'vitest';
import { myUtility } from '../../scripts/utils/my-utility.js';

describe('myUtility', () => {
  it('should transform input correctly', () => {
    expect(myUtility('input')).toBe('OUTPUT');
  });
});
```

**有关详细的单元测试指导：** 参考 [references/unit-testing.md](references/unit-testing.md)

**成功标准：**
- ✅ 为逻辑密集型代码编写单元测试
- ✅ 测试通过：`npm test`
- ✅ 或确定不需要单元测试

**完成时：** 单元测试编写并通过，或确定不需要

---

## 步骤 4：运行现有测试

**验证您的更改不会破坏现有功能：**

```bash
npm test
```

**如果测试失败：**
1. 仔细阅读错误消息
2. 运行单个测试以隔离：`npm test -- path/to/test.js`
3. 修复代码或更新测试（如果预期已更改）
4. 重新运行完整测试套件

**成功标准：**
- ✅ 所有现有测试通过
- ✅ 未引入回归

**完成时：** `npm test` 通过且无失败

## 故障排除

有关详细的故障排除指南，请参考 [references/troubleshooting.md](references/troubleshooting.md)。

**常见问题：**

### 测试失败
- 仔细阅读错误消息
- 运行单个测试：`npm test -- path/to/test.js`
- 修复代码或更新测试

### 代码检查失败
- 运行 `npm run lint:fix`
- 手动修复剩余问题

### 浏览器测试失败
- 验证开发服务器正在运行：`aem up --html-folder drafts`
- 检查测试内容是否存在于 `drafts/tmp/`
- 验证 URL 使用 `/tmp/` 路径：`http://localhost:3000/drafts/tmp/my-block`
- 添加等待：`await page.waitForSelector('.block')`

## 资源

- **单元测试：** [references/unit-testing.md](references/unit-testing.md) - 编写和维护单元测试的完整指南
- **故障排除：** [references/troubleshooting.md](references/troubleshooting.md) - 常见测试问题的解决方案
- **Vitest 设置：** [references/vitest-setup.md](references/vitest-setup.md) - 一次性配置指南
- **测试哲学：** [references/testing-philosophy.md](references/testing-philosophy.md) - 关于测试什么和如何测试的指南

## 与 Building Blocks 技能的集成

**building-blocks** 技能在步骤 5（测试实施）中调用此技能。

**从 building-blocks 接收的输入：**
- 正在测试的模块名称
- 测试内容 URL（来自 CDD 步骤 4）
- 需要测试的任何变体
- 验证现有实现/设计/模型截图（如果提供）
- 验证验收标准（来自 CDD 步骤 2）

**预期返回给 building-blocks 的输出：**
- ✅ 确认所有测试步骤完成
- ✅ 浏览器测试截图作为证据
- ✅ 确认代码检查通过
- ✅ 确认测试通过
- ✅ 发现并解决的任何问题
