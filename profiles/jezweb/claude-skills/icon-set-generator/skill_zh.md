# 图标集生成器

生成符合特定项目需求的定制化、视觉一致的SVG图标集。每个图标集都基于共享的样式规范构建，确保每个图标看起来都属于同一系列——相同的描边粗细、相同的角落处理、相同的视觉密度。

## 这为何重要

通用的图标库（如Lucide、Heroicons）虽然很棒，但使用它们的每个网站看起来都相似。定制的图标集能为项目提供独特的视觉识别。难点在于一致性——单独绘制20多个图标会导致风格漂移。这项技能通过一次性定义样式规则并在每个图标中强制执行这些规则来解决这个问题。

## 工作流程

### 第1步：理解项目

了解项目信息。你需要足够的信息来建议图标并选择风格：

- 项目是什么业务/项目？（行业、名称、氛围）
- 任何品牌指南或调色板？（即使SVG使用currentColor，也会影响风格选择）
- 感觉如何？（现代、友好、企业级、极简、粗犷）
- 大约需要多少个图标？（典型小型网站：15-25个）

像“纽卡斯尔水管工，现代感”这样的简短描述就足够继续。不要过度访谈。

### 第2步：建议图标

阅读`references/industry-icons.md`获取行业特定建议。分组组织：

- **导航**——菜单、关闭、箭头、搜索
- **通信**——电话、电子邮件、位置、时钟
- **信任**——星星、盾牌、奖项、用户
- **操作**——下载、分享、日历、表单
- **行业特定**——该业务类型独有的图标

展示列表。让用户添加、删除或重命名后再生成。

### 第3步：定义样式规范

阅读`references/style-presets.md`获取完整的预设定义。选择一个作为起点：

| 预设 | 适用于 | 描边 | 大小/连接 | 角落 |
|------|--------|------|-----------|------|
| Clean | 大多数商业网站 | 1.5px | 圆形/圆形 | 2px |
| Sharp | 企业/技术 | 1.5px | 方形/斜接 | 0px |
| Soft | 友好/易接近 | 2px | 圆形/圆形 | 4px |
| Minimal | 优雅/编辑 | 1px | 圆形/圆形 | 0px |
| Bold | 高冲击/可访问 | 2.5px | 圆形/圆形 | 2px |

告诉用户你推荐哪个预设以及原因，然后确认。

### 第4步：生成图标

遵循下方的SVG规则生成每个图标。输出到项目根目录的`icons/`目录（或用户指定的位置）。

在生成前阅读`references/svg-examples.md`——它包含参考实现，展示正确的复杂程度以及如何处理常见图标形状。

分批生成，每批约5个。每批生成后，在继续之前进行视觉审查以确保一致性。所有图标完成后，创建预览页面和`style-spec.json`。

### 第5步：交付

输出结构：
```
icons/
├── style-spec.json
├── preview.html
├── home.svg
├── phone.svg
└── ...
```

首先展示`preview.html`，让用户看到完整的图标集。

---

## SVG规则

集合中的每个图标必须遵循所有这些规则。即使是很小的差异——描边宽度略有不同、某些角落圆润而其他角落尖锐——也会使图标集看起来业余。

### SVG模板

每个图标使用完全相同的 outer 结构：

```xml
<svg xmlns="http://www.w3.org/2000/svg"
  width="{grid}" height="{grid}"
  viewBox="0 0 {grid} {grid}"
  fill="none"
  stroke="currentColor"
  stroke-width="{strokeWidth}"
  stroke-linecap="{strokeLinecap}"
  stroke-linejoin="{strokeLinejoin}">
  <!-- 图标路径 -->
</svg>
```

### 严格规则

1. **仅使用`currentColor`**——不要硬编码颜色。SVG从CSS继承颜色。没有`fill="#000"`或`stroke="blue"`。如果形状需要填充，使用`fill="currentColor"`。

2. **相同的`viewBox`**——每个图标使用相同的`viewBox`。没有例外。

3. **相同的根描边属性**——`<svg>`元素的`stroke-width`、`stroke-linecap`、`stroke-linejoin`必须跨所有图标匹配。仅在真正必要时在单个元素上覆盖。

4. **根上无变换**——无`translate`、`rotate`、`scale`。将定位烘焙到坐标中。

5. **无ID或类**——保持SVG干净以供外部样式化。

6. **坐标精度**——最多2位小数。对半像素网格对齐（例如`12`、`12.5`，而不是`12.333`）。

7. **一致的内边距**——保持配置的从`viewBox`边缘的填充。对于24px网格和2px填充，在2-22坐标范围内绘制。

8. **最小元素**——最少的`<path>`、`<circle>`、`<rect>`、`<line>`元素。越简单=越小+渲染更快。

9. **视觉居中**——看起来视觉居中，而不仅仅是数学居中。向左的箭头稍微向右移动。带烟囱的房子会调整不对称性。

### 光学校正

微妙但对于专业结果至关重要：

- **曲线描边补偿**：曲线在相同描边宽度下看起来比直线细。对于主要为曲线的图标（电话、地球），使路径略微增大，而不是改变描边宽度。
- **尖端形状超伸**：箭头、斜角、三角形超出约0.5px，以保持与方形相同的大小。
- **视觉重量平衡**：简单图标（单个斜角）看起来比复杂图标（齿轮）轻。使简单图标在网格中略微更大，或使用略微更粗的路径。没有图标应该看起来明显比其他图标轻或重。

---

## style-spec.json

```json
{
  "name": "project-name-icons",
  "preset": "clean",
  "grid": 24,
  "strokeWidth": 1.5,
  "strokeLinecap": "round",
  "strokeLinejoin": "round",
  "cornerRadius": 2,
  "padding": 2,
  "opticalBalance": true,
  "iconCount": 20,
  "icons": ["home", "phone", "email"],
  "generated": "2026-02-15"
}
```

---

## 预览页面

生成一个自包含的HTML文件，展示所有图标以供视觉审查。阅读`references/preview-template.md`获取模板。要求：

- 所有图标以原生大小（24px）显示的网格，带标签
- 同样大小的2倍网格（48px）以供细节检查
- 深色背景部分（深色上的白色）以供对比检查
- 顶部显示样式规范摘要
- 内联CSS，无依赖——只需在浏览器中打开
- 直接将所有SVG内联到HTML中（不要引用外部文件）

---

## 质量检查清单

交付前验证每项：

- [ ] 所有SVG具有相同的`viewBox`、`stroke-width`、`stroke-linecap`、`stroke-linejoin`
- [ ] 所有SVG仅使用`currentColor`
- [ ] 集合中视觉重量平衡
- [ ] 内边距一致（无接触`viewBox`边缘）
- [ ] 所有图标视觉居中
- [ ] 文件名小写连字符形式（`arrow-right.svg`）
- [ ] 预览HTML正确渲染所有图标
- [ ] `style-spec.json`准确并列出所有图标

---

## 参考文件

生成前阅读：

- `references/style-presets.md` — 详细的预设定义和选择指南
- `references/industry-icons.md` — 行业特定图标建议
- `references/preview-template.md` — 预览页面的HTML模板
- `references/svg-examples.md` — 展示不同复杂程度正确构建的示例SVG
