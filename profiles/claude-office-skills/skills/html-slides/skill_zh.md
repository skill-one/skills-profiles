# HTML 幻灯片技能

## 概述

该技能能够使用 **reveal.js**（网络最受欢迎的演示框架）创建令人惊叹的基于 HTML 的演示文稿。创建具有动画、代码高亮、演讲者笔记等功能的交互式、响应式幻灯片。

## 如何使用

1. 描述您想要创建的演示文稿
2. 指定主题、过渡效果和所需功能
3. 我将生成一个 reveal.js 演示文稿

**示例提示：**
- "创建关于我们产品的交互式演示文稿"
- "构建带有语法高亮的代码演示文稿"
- "制作带有演讲者笔记和计时器的演示文稿"
- "创建带有动画和过渡效果的幻灯片"

## 领域知识

### reveal.js 基础

```html
<!doctype html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/theme/black.css">
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <section>幻灯片 1</section>
            <section>幻灯片 2</section>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/reveal.js"></script>
    <script>Reveal.initialize();</script>
</body>
</html>
```

### 幻灯片结构

```html
<!-- 水平幻灯片 -->
<section>幻灯片 1</section>
<section>幻灯片 2</section>

<!-- 垂直幻灯片（嵌套） -->
<section>
    <section>垂直 1</section>
    <section>垂直 2</section>
</section>

<!-- Markdown 幻灯片 -->
<section data-markdown>
    <textarea data-template>
        ## 幻灯片标题
        - 要点 1
        - 要点 2
    </textarea>
</section>
```

### 主题

内置主题：`black`、`white`、`league`、`beige`、`sky`、`night`、`serif`、`simple`、`solarized`、`blood`、`moon`

```html
<link rel="stylesheet" href="reveal.js/dist/theme/moon.css">
```

### 过渡效果

```javascript
Reveal.initialize({
    transition: 'slide',  // none, fade, slide, convex, concave, zoom
    transitionSpeed: 'default',  // default, fast, slow
    backgroundTransition: 'fade'
});
```

### Fragments（动画）

```html
<section>
    <p class="fragment">首先出现</p>
    <p class="fragment fade-in">然后是这个</p>
    <p class="fragment fade-up">然后是这个</p>
    <p class="fragment highlight-red">高亮显示</p>
</section>
```

Fragment 样式：`fade-in`、`fade-out`、`fade-up`、`fade-down`、`fade-left`、`fade-right`、`highlight-red`、`highlight-blue`、`highlight-green`、`strike`

### 代码高亮

```html
<section>
    <pre><code data-trim data-line-numbers="1|3-4">
def hello():
    print("Hello")
    print("World")
    return True
    </code></pre>
</section>
```

### 演讲者笔记

```html
<section>
    <h2>幻灯片标题</h2>
    <p>内容</p>
    <aside class="notes">
        演讲者笔记放在这里。按 'S' 键查看。
    </aside>
</section>
```

### 背景

```html
<!-- 颜色背景 -->
<section data-background-color="#4d7e65">

<!-- 图片背景 -->
<section data-background-image="image.jpg" data-background-size="cover">

<!-- 视频背景 -->
<section data-background-video="video.mp4">

<!-- 渐变背景 -->
<section data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)">
```

### 配置

```javascript
Reveal.initialize({
    // 显示控制
    controls: true,
    controlsTutorial: true,
    progress: true,
    slideNumber: true,
    
    // 行为
    hash: true,
    respondToHashChanges: true,
    history: true,
    keyboard: true,
    overview: true,
    center: true,
    touch: true,
    loop: false,
    rtl: false,
    shuffle: false,
    
    // 时间
    autoSlide: 0,  // 0 = 禁用
    autoSlideStoppable: true,
    
    // 外观
    width: 960,
    height: 700,
    margin: 0.04,
    minScale: 0.2,
    maxScale: 2.0,
    
    // 插件
    plugins: [RevealMarkdown, RevealHighlight, RevealNotes]
});
```

## 示例

### 示例 1：技术讲座

```html
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>API 设计最佳实践</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/theme/night.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/plugin/highlight/monokai.css">
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <section data-background-gradient="linear-gradient(to bottom right, #1a1a2e, #16213e)">
                <h1>API 设计</h1>
                <h3>2024 年最佳实践</h3>
                <p><small>工程团队</small></p>
            </section>
            
            <section>
                <h2>议程</h2>
                <ol>
                    <li class="fragment">RESTful 原则</li>
                    <li class="fragment">身份验证</li>
                    <li class="fragment">错误处理</li>
                    <li class="fragment">文档</li>
                </ol>
            </section>
            
            <section>
                <section>
                    <h2>RESTful 原则</h2>
                </section>
                <section>
                    <h3>资源命名</h3>
                    <pre><code data-trim class="language-http">
GET /users           # 集合
GET /users/123       # 单个资源
POST /users          # 创建
PUT /users/123       # 更新
DELETE /users/123    # 删除
                    </code></pre>
                </section>
            </section>
            
            <section>
                <h2>有问题吗？</h2>
                <p>api-team@company.com</p>
            </section>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/reveal.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4/plugin/highlight/highlight.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            plugins: [RevealHighlight]
        });
    </script>
</body>
</html>
```

### 示例 2：产品发布

```html
<!doctype html>
<html>
<head>
    <title>产品发布</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/theme/white.css">
    <style>
        .reveal h1 { color: #2d3748; }
        .metric { font-size: 3em; color: #3182ce; }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <section data-background-color="#f7fafc">
                <h1>介绍</h1>
                <h2 style="color: #3182ce;">ProductX 2.0</h2>
            </section>
            
            <section>
                <h2>问题</h2>
                <p class="fragment">团队浪费 <span class="metric">20%</span> 的时间在手动任务上</p>
            </section>
            
            <section data-auto-animate>
                <h2>我们的解决方案</h2>
                <div data-id="box" style="background: #3182ce; padding: 20px;">
                    人工智能驱动的自动化
                </div>
            </section>
            
            <section data-auto-animate>
                <h2>我们的解决方案</h2>
                <div data-id="box" style="background: #38a169; padding: 40px; width: 400px;">
                    <p>人工智能驱动的自动化</p>
                    <p>90% 更快</p>
                </div>
            </section>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4/dist/reveal.js"></script>
    <script>Reveal.initialize();</script>
</body>
</html>
```

## 资源

- [reveal.js 文档](https://revealjs.com/)
- [GitHub 仓库](https://github.com/hakimel/reveal.js)
- [演示幻灯片](https://revealjs.com/demo/)
