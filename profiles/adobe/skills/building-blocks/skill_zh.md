# 基础组件

本技能将指导您按照既定模式和最佳实践实现 AEM Edge Delivery 组件。组件通过 JavaScript 装饰和 CSS 样式将编写的內容转换为丰富的交互式体验。

**重要提示：**此技能**仅**应在内容驱动开发技能在步骤 5（实现）期间被调用。

如果您尚未遵循内容驱动开发流程，请停止并首先调用**内容驱动开发**技能。

## 相关技能

- **内容驱动开发**：在使用此技能之前**必须**调用，以确保内容和内容模型已准备就绪
- **da-auth**：如果需要在实现开始前将测试內容推送到 DA，请获取有效的 Adobe IMS 令牌
- **组件收集与共享**：用于查找类似组件以供模式使用
- **测试组件**：在步骤 5 自动调用，用于全面测试

## 何时使用此技能

此技能由**内容驱动开发**在步骤 5（实现）期间自动调用。它处理：

**组件开发：**
- 创建新的组件文件和结构
- 实现JavaScript装饰
- 添加CSS样式

**核心功能：**
- Scripts.js修改（装饰、工具、自动组件化）
- 全局样式（styles.css、lazy-styles.css）
- 延迟功能（delayed.js）
- 配置更改

**组合：**
- 具有支持性核心更改的组件（工具、全局样式等）

先决条件（由CDD验证）：
- ✅ 存在测试內容（在CMS或本地草稿中）
- ✅ 内容模型已定义/文档化（如适用）
- ✅ 可用测试內容URL
- ✅ 开发服务器正在运行

## 组件实现工作流

跟踪您的进度：
- [ ] 步骤 1：查找类似组件以供模式使用（如果是新组件或重大更改）
- [ ] 步骤 2：创建或修改组件结构（文件和目录）
- [ ] 步骤 3：实现JavaScript装饰（如果是纯CSS则跳过）
- [ ] 步骤 4：添加CSS样式
- [ ] 步骤 5：测试实现（调用测试组件技能）

**注意：**如果您的更改需要核心修改（scripts.js中的工具、全局样式等），请先进行这些更改，测试后再返回此工作流。见“修改核心文件时”下方内容。

## 步骤 1：查找类似组件

**何时使用：**创建新组件或进行重大结构修改

**跳过此步骤的情况：**对现有组件进行次要修改（CSS微调、小装饰更改）

**快速入门：**

1. 在代码库中搜索类似组件：
   ```bash
   ls blocks/
   ```

2. 使用**组件收集与共享**技能查找参考实现

3. 审查类似组件的模式：
   - DOM操作策略
   - CSS架构
   - 变体处理
   - 性能优化

## 步骤 2：创建或修改组件结构

### 对于新组件：

1. 创建组件目录和文件：
   ```bash
   mkdir -p blocks/{block-name}
   touch blocks/{block-name}/{block-name}.js
   touch blocks/{block-name}/{block-name}.css
   ```

2. 基本JavaScript结构：
   ```javascript
   /**
    * 装饰组件
    * @param {Element} block 组件
    */
   export default async function decorate(block) {
     // 您的装饰逻辑在此处
   }
   ```

3. 基本CSS结构：
   ```css
   /* 所有选择器都作用域到组件 */
   main .{block-name} {
     /* 组件样式 */
   }
   ```

### 对于现有组件：

1. 定位组件目录：`blocks/{block-name}/`
2. 审查当前实现：
   ```bash
   # 从服务器查看初始HTML结构
   curl http://localhost:3000/{test-content-path}
   ```
3. 理解现有的装饰逻辑和样式

## 步骤 3：实现JavaScript装饰

**基本模式 - 重用现有DOM元素：**

```javascript
export default async function decorate(block) {
  // 平台将图像作为 <picture> 元素和 <source> 标签交付
  const picture = block.querySelector('picture');
  const heading = block.querySelector('h2');

  // 创建新结构，重用现有元素
  const figure = document.createElement('figure');
  figure.append(picture);  // 重用picture元素

  const wrapper = document.createElement('div');
  wrapper.className = 'content-wrapper';
  wrapper.append(heading, figure);

  block.replaceChildren(wrapper);

  // 仅在变体影响装饰逻辑时检查变体
  // 像dark、wide这样的纯CSS变体不需要JS
  if (block.classList.contains('carousel')) {
    // Carousel变体需要不同的DOM结构/行为
    setupCarousel(block);
  }
}
```

**有关完整的JavaScript指南，包括：**
- 高级DOM操作模式
- 获取数据和加载模块
- 性能优化技术
- aem.js中的辅助函数
- 代码风格和代码检查规则

**阅读 [references/js-guidelines.md](references/js-guidelines.md)**

## 步骤 4：添加CSS样式

**基本模式 - 作用域、响应式、使用自定义属性：**

```css
/* 所有选择器必须作用域到组件 */
main .my-block {
  /* 使用CSS自定义属性以保持一致性 */
  background-color: var(--background-color);
  color: var(--text-color);
  font-family: var(--body-font-family);
  max-width: var(--max-content-width);

  /* 移动优先样式（默认） */
  padding: 1rem;
  flex-direction: column;
}

main .my-block h2 {
  font-family: var(--heading-font-family);
  font-size: var(--heading-font-size-m);
}

main .my-block .item {
  display: flex;
  gap: 1rem;
}

/* 平板和以上 */
@media (width >= 600px) {
  main .my-block {
    padding: 2rem;
  }
}

/* 桌面和以上 */
@media (width >= 900px) {
  main .my-block {
    flex-direction: row;
    padding: 4rem;
  }
}

/* 变体 - 大多数是纯CSS */
main .my-block.dark {
  background-color: var(--dark-color);
  color: var(--clr-white);
}
```

**有关完整的CSS指南，包括：**
- 所有可用的CSS自定义属性
- 现代CSS特性（网格、逻辑属性等）
- 性能优化
- 命名约定
- 常见模式和反模式

**阅读 [references/css-guidelines.md](references/css-guidelines.md)**

**关于迭代验证的说明：**在构建过程中，您可以在浏览器中逐步测试更改（加载测试內容URL，检查控制台，验证布局和功能）。有关全面测试指南，包括浏览器测试技术、响应式测试和验证方法，请参阅在步骤 5 调用的测试组件技能。

## 步骤 5：测试实现

**实现完成后，调用测试组件技能。**

测试组件技能将指导您完成：
- 浏览器测试（功能、跨视口的响应式行为）
- 代码检查和修复问题
- 为逻辑密集型工具编写单元测试（如果需要）
- 截图捕获以进行验证
- 性能验证

**向测试组件技能提供：**
- 正在测试的组件名称
- 测试內容URL（来自CDD流程步骤 4）
- 需要测试的任何变体
- 现有实现/设计/草图的截图以进行验证
- 验证的标准（来自CDD流程步骤 2）

**测试完成后，返回CDD工作流。**

---

## 修改核心文件时

如果您的更改需要修改核心文件（scripts.js、styles.css、delayed.js），请遵循以下原则：

**常见核心文件：**
- **scripts.js** - 装饰工具、自动组件化逻辑、页面加载
- **styles.css** - 全局样式（立即加载）、CSS自定义属性
- **lazy-styles.css** - 全局样式（延迟加载）
- **delayed.js** - 营销、分析、第三方集成

**关键原则：**

1. **先进行核心更改**（在依赖于它们的组件更改之前）
2. **独立测试核心更改**，使用现有內容，然后再在组件中使用
3. **考虑影响** - 核心更改会影响多个组件/页面
4. **彻底测试** - 验证现有功能没有回归
5. **保持最小化** - 只添加必要的内容
6. **用代码注释进行文档化** - 大多数核心更改不需要单独文档

**测试核心更改：**
- 使用受影响的现有內容URL进行测试
- 对于自动组件化：测试应该/不应该触发它的页面
- 对于全局样式：跨多个组件和页面进行测试
- 检查控制台错误
- 验证响应式行为

**有关详细模式：**
- JavaScript：见 [references/js-guidelines.md](references/js-guidelines.md)
- CSS：见 [references/css-guidelines.md](references/css-guidelines.md)

---

## 参考材料

- [references/js-guidelines.md](references/js-guidelines.md) - 完整的JavaScript模式和最佳实践
- [references/css-guidelines.md](references/css-guidelines.md) - 完整的CSS模式和最佳实践
