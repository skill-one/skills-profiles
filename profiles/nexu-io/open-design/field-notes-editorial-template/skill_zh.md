# 字段笔记编辑模板

生成一个包含在单个自包含HTML文件中的高级编辑数据报告。

## 资源映射

```text
field-notes-editorial-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 读取活跃的`DESIGN.md`并将调色板/字体映射到根CSS变量。
2. 将`assets/template.html`复制到`index.html`作为工作产物。
3. 保持编辑框架语言：
   - 纸张般的背景和微妙的柔焦效果
   - 衬线字体显示标题搭配干净的无衬线字体正文
   - 圆角柔和色系的度量/洞察卡片
   - 带图例和坐标标签的图表面板
4. 保持交互轻量且适合展示：
   - 页面视图切换器（度量/洞察/留存）
   - 关键度量的数字计数动画
   - 图表线显示动画
5. 在数据未知时使用诚实的占位符（`—`或中性标签）。
6. 在发布前与`references/checklist.md`进行验证。

## 输出合约

先有一句简短的定向语句，然后：

```xml
<artifact identifier="field-notes-editorial" type="text/html" title="字段笔记编辑报告">
<!doctype html>
<html>...</html>
</artifact>
```
