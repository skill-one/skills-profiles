# 一页式发布说明文档技能

生成一个单页面的发布说明文档，使用HTML格式。

## 资源映射

```
release-notes-one-pager/
├── SKILL.md                    ← 此文件
├── example.html                ← 质量基准和样式参考
├── assets/
│   └── template.html           ← 本地种子文件，复制到项目index.html
└── references/
    ├── checklist.md            ← P0 / P1 / P2关卡
    └── layouts.md              ← 本地章节骨架
```

除非用户明确要求定制结构，否则不要从零开始编写CSS。

## 工作流程

### 第0步 — 预检查

1. 读取`assets/template.html`。
2. 读取`references/layouts.md`。
3. 读取活动的`DESIGN.md`，并将其映射到六个`:root`变量。

### 第1步 — 从共享种子开始

将`assets/template.html`复制到项目`index.html`。

更新：
- `<title>`
- 顶部导航栏logo文本
- 顶部导航栏链接标签（目标已预连接到`#added`、`#fixed`、`#upgrade-note`）
- 顶部导航栏CTA标签和`href`目标，如果不存在真实目标，则完全省略顶部导航栏CTA
- 确保顶部导航栏链接目标存在，通过添加匹配的章节`id`属性

### 第2步 — 构建发布说明结构

在`<main id="content">`内部，按此部分顺序编写：

1. 英雄版块（布局1或2）：版本、日期、一句话摘要。
2. 新增（使用布局7日志列表；章节根必须包含`id="added"`）。
3. 修复（使用布局7日志列表；章节根必须包含`id="fixed"`）。
4. 不兼容变更（使用布局7日志列表，或一行明确说明“无”；章节根必须包含`id="breaking-changes"`）。
5. 已知问题（布局7或卡片列表；章节根必须包含`id="known-issues"`）。
6. 升级说明（简短步骤列表或明确无操作声明；章节根必须包含`id="upgrade-note"`）。
7. 结束CTA条带（布局6）。

对于生成的HTML中的每个CTA（顶部导航栏、英雄版块、结束条带），用真实、安全的值替换可见标签和`href`目标。如果不存在真实目标，则完全省略CTA——不要使用占位符，如`href="#"`、误导性的页面锚点或`REPLACE_WITH_REAL_URL`。英雄CTA是可选的；只有存在真实目标时才添加。

### 第3步 — 缺失细节的诚实规则

如果用户未提供详细信息，不要凭空捏造。编写明确的占位符：

- 摘要：`未提供摘要。`
- 新增：`未提供新增内容`
- 修复：`未提供修复`
- 不兼容变更：`无`
- 已知问题：`未报告`
- 升级说明：`根据提供的信息无需执行升级操作`

如果发布版本或日期缺失，使用`—`并标记该字段，而不是猜测。

### 第4步 — 自检

运行`references/checklist.md`。每个P0必须通过。

### 第5步 — 输出工件

将输出包装为：

```
<artifact identifier="release-notes-one-pager" type="text/html" title="发布说明">
<!doctype html>
<html>...</html>
</artifact>
```

在工件之前的一句话。`</artifact>`之后不能有任何内容。
