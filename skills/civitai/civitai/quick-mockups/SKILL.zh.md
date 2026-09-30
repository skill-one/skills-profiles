---
name: quick-mockups
description: 并行创建多个 UI 设计原型。在要求创建原型、线框图或设计变体时使用。使用 Mantine v7 + Tailwind 根据 Civitai 的设计系统创建 HTML 文件。
---

# 快速原型设计

使用 `design-mockup` 代理并行创建多个设计原型。

## 使用方法

当被要求为某个功能创建原型时：

1. **创建输出目录**（如果不存在）：
   ```
   docs/working/mockups/<功能名>/
   ```

2. **使用任务工具启动 3-5 个并行原型代理**，并设置 `subagent_type: design-mockup`

3. **每个代理创建一个独特的变体**，具有不同的：
   - 布局方法（网格、列表、马赛克、卡片）
   - 信息层级
   - 视觉重点
   - 交互模式

## 目录结构

```
docs/working/mockups/
├── crucible-discovery/
│   ├── v1-grid-cards.html
│   ├── v2-featured-hero.html
│   ├── v3-compact-list.html
│   └── v4-masonry.html
├── crucible-rating/
│   ├── v1-side-by-side.html
│   ├── v2-stacked.html
│   └── v3-swipe.html
└── [功能名]/
    └── [变体].html
```

## 启动代理时的提示

启动原型代理时，提供：
1. **功能名称** - 要设计哪个页面/组件
2. **关键需求** - 必须包含的内容
3. **变体重点** - 使此变体独特的原因
4. **参考上下文** - 如果有帮助，链接到现有的类似页面

代理的示例提示：
```
为 Crucible Discovery 页面创建原型。

需求：
- 将活跃 crucibles 列为卡片
- 显示：名称、奖池、剩余时间、参与人数
- 筛选/排序控件（按奖池、即将结束、最新）
- "创建 Crucible" 按钮

变体：网格布局，为精选 crucible 设置大型英雄卡片

输出到：docs/working/mockups/crucible-discovery/v1-featured-hero.html
```

## 创建原型后

1. 列出所有创建的原型文件
2. 总结每个变体的方法
3. 询问用户要选择哪个方向，或是否需要更多变体

## 小贴士

- 创建有意义的差异变体，而不仅仅是微调
- 至少在一个变体中考虑移动布局
- 显示真实内容（名称、数字、时间）
- 在相关位置包含空状态
- 使用 `.claude/agents/design-mockup.md` 中的 Civitai 设计模式
