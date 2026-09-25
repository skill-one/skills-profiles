# Vega / Vega-Lite 可视化工具

**快速入门：** 将数据结构化为对象数组 → 选择标记类型（条形图/折线图/点图/面积图/弧形图/矩形图）→ 将编码（x, y, 颜色, 大小）映射到字段 → 设置数据类型（定量/名义/序数/时间）→ 用 ` ```vega-lite ` 或 ` ```vega ` 标签包裹。始终包含 `$schema`，使用有效的 JSON 并使用双引号，字段名区分大小写。**90% 的图表使用 Vega-Lite；仅使用 Vega 创建雷达图、词云和力导向图。**

---

## 关键语法规则

### 规则 1：始终包含模式
```json
"$schema": "https://vega.github.io/schema/vega-lite/v5.json"
```

### 规则 2：仅支持有效 JSON
```
❌ {field: "x",}     → 多余逗号、未加引号的键
✅ {"field": "x"}    → 正确的 JSON
```

### 规则 3：字段名必须与数据匹配
```
❌ "field": "Category"  当数据为 "category" 时
✅ "field": "category"  → 区分大小写的匹配
```

### 规则 4：类型必须有效
```
✅ quantitative | nominal | ordinal | temporal
❌ numeric | string | date
```

---

## 常见问题

| 问题 | 解决方案 |
|-------|----------|
| 图表未渲染 | 检查 JSON 有效性，验证 `$schema` |
| 数据未显示 | 字段名必须完全匹配 |
| 图表类型错误 | 将标记与数据结构匹配 |
| 颜色不可见 | 检查颜色尺度的对比度 |
| 双轴问题 | 添加 `resolve: {scale: {y: "independent"}}` |

---

## 输出格式

````markdown
```vega-lite
{...}
```
````

或用于完整 Vega：

````markdown
```vega
{...}
```
````

---

## 相关文件

> 对于高级图表模式和复杂可视化，请参考以下参考：

- [examples.md](references/examples.md) — 堆积条形图、分组条形图、多序列折线图、面积图、热力图、雷达图（Vega）、词云（Vega）和交互式图表示例
