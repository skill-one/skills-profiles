# 开发者幻灯片技能

## 概述

该技能能够使用 **Slidev**（一个基于 Vue 的演示文稿框架）创建面向开发者的演示文稿。使用 Markdown 编写幻灯片，并包含实时代码演示、图表和组件。

## 如何使用

1. 描述您的技术演示需求
2. 我将生成具有正确语法的 Slidev Markdown
3. 包含代码块、图表和 Vue 组件

**示例提示：**
- "创建一个 Vue.js 工作坊演示文稿"
- "构建带有实时代码执行的幻灯片"
- "制作一个带有图表的技术演讲"
- "创建开发者入职幻灯片"

## 领域知识

### Slidev 基础

```markdown
---
theme: default
title: 我的演示文稿
---

# 欢迎

这是第一张幻灯片

---

# 第二张幻灯片

内容在此
```

### 幻灯片分隔符

```markdown
---   # 新的水平幻灯片

---   # 另一张幻灯片
layout: center
---

# 居中内容
```

### 布局

```markdown
---
layout: cover
---
# 标题幻灯片

---
layout: intro
---
# 介绍

---
layout: center
---
# 居中

---
layout: two-cols
---
# 左
::right::
# 右

---
layout: image-right
image: ./image.png
---
# 带有图片的内容
```

### 代码块

```markdown
# 代码示例

\`\`\`ts {all|1|2-3|4}
const name = 'Slidev'
const greeting = \`Hello, \${name}!\`
console.log(greeting)
// Outputs: Hello, Slidev!
\`\`\`

<!-- 步骤突出显示行 -->
```

### Monaco 编辑器（实时代码）

```markdown
\`\`\`ts {monaco}
// 可编辑的代码块
function add(a: number, b: number) {
  return a + b
}
\`\`\`

\`\`\`ts {monaco-run}
// 可运行的代码
console.log('Hello from Slidev!')
\`\`\`
```

### 图表（Mermaid）

```markdown
\`\`\`mermaid
graph LR
  A[开始] --> B{决策}
  B -->|是| C[操作 1]
  B -->|否| D[操作 2]
\`\`\`

\`\`\`mermaid
sequenceDiagram
  Client->>Server: 请求
  Server-->>Client: 响应
\`\`\`
```

### Vue 组件

```markdown
<Counter :count="10" />

<Tweet id="1390115482657726468" />

<!-- 自定义组件 -->
<MyComponent v-click />
```

### 动画

```markdown
<v-click>

点击时出现

</v-click>

<v-clicks>

- 项目 1
- 项目 2
- 项目 3

</v-clicks>

<!-- 或使用 v-click 指令 -->
<div v-click>动画内容</div>
```

### 前置元数据

```yaml
---
theme: seriph
background: https://source.unsplash.com/collection/94734566/1920x1080
class: text-center
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
css: unocss
---
```

## 示例

### 示例：API 工作坊
```markdown
---
theme: seriph
background: https://source.unsplash.com/collection/94734566/1920x1080
class: text-center
---

# REST API 工作坊

使用 Node.js 构建现代 API

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer">
    按空格键进入下一页 <carbon:arrow-right />
  </span>
</div>

---
layout: two-cols
---

# 我们将涵盖的内容

<v-clicks>

- RESTful 原则
- Express.js 基础
- 身份验证
- 错误处理
- 测试

</v-clicks>

::right::

\`\`\`ts
// 预览
const app = express()
app.get('/api/users', getUsers)
app.listen(3000)
\`\`\`

---

# 实时演示

\`\`\`ts {monaco-run}
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
]

console.log(JSON.stringify(users, null, 2))
\`\`\`

---
layout: center
---

# 提问？

[GitHub](https://github.com) · [文档](https://docs.example.com)
```

## 安装

```bash
npm init slidev@latest
```

## 资源

- [Slidev 文档](https://sli.dev/)
- [GitHub](https://github.com/slidevjs/slidev)
- [主题](https://sli.dev/themes/gallery.html)
