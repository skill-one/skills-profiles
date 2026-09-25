# 设计系统模式

掌握设计系统架构，以创建跨网页和移动应用的、一致、可维护且可扩展的 UI 基础。

## 使用此技能的场景

- 创建颜色、排版、间距和阴影的设计令牌
- 使用 CSS 自定义属性实现亮/暗主题切换
- 构建多品牌主题系统
- 架构具有一致 API 的组件库
- 使用 Figma 令牌建立设计到代码的工作流程
- 创建语义令牌层级（原始、语义、组件）
- 设置设计系统文档和指南

## 核心能力

### 1. 设计令牌

- 原始令牌（原始值：颜色、尺寸、字体）
- 语义令牌（上下文含义：text-primary、surface-elevated）
- 组件令牌（特定用法：button-bg、card-border）
- 令牌命名规范和组织
- 多平台令牌生成（CSS、iOS、Android）

### 2. 主题基础设施

- CSS 自定义属性架构
- React 中的主题上下文提供者
- 动态主题切换
- 系统偏好检测（prefers-color-scheme）
- 持久化主题存储
- 减少动画和高对比度模式

### 3. 组件架构

- 复合组件模式
- 多态组件（as prop）
- 变体和尺寸系统
- 基于插槽的组合
- 无头 UI 模式
- 样式属性和响应式变体

### 4. 令牌管道

- Figma 到代码同步
- Style Dictionary 配置
- 令牌转换和格式化
- 令牌更新的 CI/CD 集成

## 快速入门

```typescript
// 使用 CSS 自定义属性的设计令牌
const tokens = {
  colors: {
    // 原始令牌
    gray: {
      50: "#fafafa",
      100: "#f5f5f5",
      900: "#171717",
    },
    blue: {
      500: "#3b82f6",
      600: "#2563eb",
    },
  },
  // 语义令牌（引用原始令牌）
  semantic: {
    light: {
      "text-primary": "var(--color-gray-900)",
      "text-secondary": "var(--color-gray-600)",
      "surface-default": "var(--color-white)",
      "surface-elevated": "var(--color-gray-50)",
      "border-default": "var(--color-gray-200)",
      "interactive-primary": "var(--color-blue-500)",
    },
    dark: {
      "text-primary": "var(--color-gray-50)",
      "text-secondary": "var(--color-gray-400)",
      "surface-default": "var(--color-gray-900)",
      "surface-elevated": "var(--color-gray-800)",
      "border-default": "var(--color-gray-700)",
      "interactive-primary": "var(--color-blue-400)",
    },
  },
};
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **按用途命名令牌**：使用语义名称（text-primary）而非视觉描述（dark-gray）
2. **维护令牌层级**：原始 > 语义 > 组件令牌
3. **记录令牌用法**：在令牌定义中包含使用指南
4. **版本化令牌**：将令牌变更视为 API 变更，使用 semver
5. **测试主题组合**：验证所有主题与所有组件兼容
6. **自动化令牌管道**：CI/CD 用于 Figma 到代码同步
7. **提供迁移路径**：逐步弃用令牌，并提供明确替代方案

## 常见问题

- **令牌蔓延**：缺乏清晰层级的大量令牌
- **命名不一致**：混合规范（camelCase vs kebab-case）
- **缺少暗黑模式**：不适应主题变化的令牌
- **硬编码值**：使用原始值而非令牌
- **循环引用**：令牌相互循环引用
- **平台缺失**：某些平台（如网页但非移动端）缺失令牌
