# Taiwan.md 知识库

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

Taiwan.md 是一个关于台湾的开源、AI原生知识库，使用 Astro v5 构建。它采用单一事实来源（SSOT）架构，所有内容都存储在 `knowledge/` 目录中的 Markdown 文件中，而网站是在构建时生成的投影。功能包括双语支持（默认为繁体中文 + 英语）、交互式 D3.js 知识图谱以及 12 个类别中的 96+ 精选文章。

---

## 安装与设置

### 前置条件
- Node.js 18+
- npm 或 pnpm

### 克隆和安装

```bash
git clone https://github.com/frank890417/taiwan-md.git
cd taiwan-md
npm install
```

### 开发服务器

```bash
npm run dev
# 网站可在 http://localhost:4321 访问
```

### 构建 & 预览

```bash
npm run build
npm run preview
```

### 同步知识到内容

```bash
bash scripts/sync.sh
# 复制 knowledge/ → src/content/ 用于 Astro 构建
```

---

## 项目架构

```
taiwan-md/
├── knowledge/               ← SSOT: 所有内容都存储在这里
│   ├── History/             ← 中文文章 + _Hub.md
│   ├── Geography/
│   ├── Culture/
│   ├── Food/
│   ├── Art/
│   ├── Music/
│   ├── Technology/
│   ├── Nature/
│   ├── People/
│   ├── Society/
│   ├── Economy/
│   ├── Lifestyle/
│   ├── About/               ← 元内容
│   └── en/                  ← 英文翻译（镜像 zh-TW）
│       ├── History/
│       ├── Geography/
│       └── ...
├── scripts/
│   └── sync.sh              ← 同步 knowledge/ → src/content/
├── src/
│   ├── pages/               ← Astro 页面
│   ├── layouts/             ← 共享布局
│   └── content/             ← 构建时投影（禁止直接编辑）
├── public/
│   └── images/wiki/         ← 缓存的维基共享资源图片
└── docs/                    ← 架构和路线图文档
```

**关键规则：** 直接编辑 `src/content/` 中的文件。始终编辑 `knowledge/` 并运行 `scripts/sync.sh`。

---

## 内容结构

### 12 个类别

| Slug | 中文 | 英文 |
|------|------|------|
| `history` | 歷史 | History |
| `geography` | 地理 | Geography |
| `culture` | 文化 | Culture |
| `food` | 美食 | Food |
| `art` | 藝術 | Art |
| `music` | 音樂 | Music |
| `technology` | 科技 | Technology |
| `nature` | 自然 | Nature |
| `people` | 人物 | People |
| `society` | 社會 | Society |
| `economy` | 經濟 | Economy |
| `lifestyle` | 生活 | Lifestyle |

### 文章文件命名

```
knowledge/
├── Food/
│   ├── _Hub.md              ← 类别中心页面（概述）
│   ├── bubble-tea.md        ← 单篇文章（zh-TW）
│   └── beef-noodle.md
└── en/
    └── Food/
        ├── _Hub.md          ← 英文中心页面
        ├── bubble-tea.md    ← 英文翻译
        └── beef-noodle.md
```

---

## 撰写文章

### 中文文章模板 (`knowledge/[Category]/article-slug.md`)

```markdown
---
title: 珍珠奶茶
description: 台灣最具代表性的飲料文化，從夜市攤車到全球連鎖，珍珠奶茶如何征服世界。
category: food
date: 2024-01-15
tags: [飲食文化, 台灣之光, 夜市]
image: /images/wiki/bubble-tea-abc123.jpg
imageCaption: 台灣珍珠奶茶 | Wikimedia Commons | CC BY-SA 4.0
sources:
  - title: 珍珠奶茶的起源考證
    url: https://example.com/boba-origin
  - title: 台灣飲料市場報告
    url: https://example.com/beverage-report
---

## 30 秒認識

珍珠奶茶（波霸奶茶）誕生於 1980 年代台灣，現已成為全球年產值超過 30 億美元的飲料產業。

## 深度閱讀

### 起源爭議

台南翰林茶館與台中春水堂都聲稱是珍珠奶茶的發明者...

### 全球擴張

2010 年代，珍珠奶茶席捲歐美亞各大城市...

## 為什麼重要

珍珠奶茶不只是一杯飲料，它是台灣軟實力的最佳代言人——在沒有邦交的地方，台灣味道先到了。

## 參考資料

- [珍珠奶茶的起源考證](https://example.com/boba-origin)
- [台灣飲料市場報告](https://example.com/beverage-report)
```

### 英文文章模板 (`knowledge/en/[Category]/article-slug.md`)

```markdown
---
title: Bubble Tea
description: Taiwan's most iconic beverage culture — how boba conquered the world from night market stalls to global chains.
category: food
date: 2024-01-15
tags: [food culture, taiwan pride, night market]
image: /images/wiki/bubble-tea-abc123.jpg
imageCaption: Taiwanese Bubble Tea | Wikimedia Commons | CC BY-SA 4.0
sources:
  - title: Origins of Bubble Tea
    url: https://example.com/boba-origin
  - title: Taiwan Beverage Market Report
    url: https://example.com/beverage-report
---

## 30-Second Overview

Bubble tea (boba) was born in 1980s Taiwan and has grown into a global industry worth over $3 billion annually.

## Deep Dive

### The Origin Debate

Both Hanlin Tea Room in Tainan and Chun Shui Tang in Taichung claim to have invented bubble tea...

### Global Expansion

In the 2010s, bubble tea swept across cities in Europe, America, and Asia...

## Why This Matters

Bubble tea isn't just a drink — it's Taiwan's finest soft power ambassador. Where there's no diplomatic recognition, Taiwanese flavor arrived first.

## References

- [Origins of Bubble Tea](https://example.com/boba-origin)
- [Taiwan Beverage Market Report](https://example.com/beverage-report)
```

### 中心页面模板 (`knowledge/[Category]/_Hub.md`)

```markdown
---
title: 美食
titleEn: Food
description: 台灣的飲食文化是移民歷史、地理環境與創意精神的完美結晶。
category: food
---

## 關於這個分類

台灣是一個以食物說故事的地方...

## 精選文章

這個分類收錄了台灣飲食文化最具代表性的面向...
```

---

## Frontmatter 参考

### 必填字段

```yaml
---
title: "文章標題"           # 显示标题
description: "一句话说明"   # 元描述（最多 150 字符）
category: food             # 必须匹配 12 个类别中的其中一个
date: 2024-01-15           # ISO 日期格式
---
```

### 可选字段

```yaml
---
tags: [tag1, tag2]         # 标签数组用于知识图谱
image: /images/wiki/...    # 必须来自维基共享资源缓存
imageCaption: "..."        # 归因：标题 | 来源 | 许可证
sources:                   # 必须的：可点击的 URL，无纯文本引用
  - title: "来源名称"
    url: https://...
---
```

---

## 添加图片（维基共享资源政策）

所有图片必须来自维基共享资源，并具有经过验证的 CC 许可证。本地缓存它们：

```bash
# 下载并缓存维基共享资源图片
# 图片以 MD5 哈希文件名存储
curl -o public/images/wiki/$(echo "filename.jpg" | md5sum | cut -d' ' -f1).jpg \
  "https://commons.wikimedia.org/wiki/Special:FilePath/Taiwan_landscape.jpg"
```

Frontmatter 中的图片归因格式：
```yaml
imageCaption: "描述 | Wikimedia Commons | CC BY-SA 4.0"
```

---

## 知识图谱集成

文章自动出现在 `/graph` 中的 D3.js 知识图谱中。节点从文章创建，边从共享标签和交叉引用创建。

### 链接文章

使用相对路径在内容中引用其他文章：

```markdown
台灣的[半導體產業](/technology/tsmc)是台積電...

See also: [Bubble Tea](/food/bubble-tea) for more on Taiwan's soft power.
```

### 标签用于图谱连接

使用一致的标签创建知识图谱桥接：

```markdown
# 标签为 [democratic transition] 的两篇文章将被连接
tags: [democratic transition, civil society, 1990s]
```

---

## 同步工作流

编辑 `knowledge/` 中的任何文件后，构建前始终同步：

```bash
# 1. 编辑内容
vim knowledge/Food/new-article.md
vim knowledge/en/Food/new-article.md

# 2. 同步到 src/content/
bash scripts/sync.sh

# 3. 验证构建
npm run build

# 4. 预览
npm run preview
```

---

## 三层深度模式

每篇文章都应遵循此结构，以供 AI 读取和不同阅读水平：

```markdown
## 30 秒認識 / 30-Second Overview
[2-3 句话，核心事实]

## 深度閱讀 / Deep Dive
### 子部分 1
[详细探索，包含数据]

### 子部分 2
[历史背景或比较]

## 為什麼重要 / Why This Matters
[策展视角——回答“世界为什么要关心？”]

## 參考資料 / References
[仅可点击的 URL —— 无纯文本引用]
```

---

## 通过 PR 贡献

### 完整 PR 工作流

```bash
# 1. Fork 和克隆
git clone https://github.com/YOUR_USERNAME/taiwan-md.git
cd taiwan-md

# 2. 创建分支
git checkout -b add/food/scallion-pancake

# 3. 添加 zh-TW 文章
cat > knowledge/Food/scallion-pancake.md << 'EOF'
---
title: 蔥抓餅
description: ...
category: food
date: 2024-01-20
sources:
  - title: Source
    url: https://...
---
内容...
EOF

# 4. 添加英文翻译
mkdir -p knowledge/en/Food
cat > knowledge/en/Food/scallion-pancake.md << 'EOF'
---
title: Scallion Pancake
...
EOF

# 5. 同步和测试
bash scripts/sync.sh
npm run build

# 6. 提交和 PR
git add knowledge/
git commit -m "feat(food): 添加 scallion pancake 文章 (zh+en)"
git push origin add/food/scallion-pancake
```

### 提交信息规范

```
feat(category): 添加 [文章名称] 文章 (zh+en)
fix(category): 修正 [文章名称] 事实错误
i18n(category): 为 [文章名称] 添加英文翻译
feat(graph): 为 [主题] 添加知识图谱连接
```

---

## AI 原生功能

### llms.txt

网站暴露 `/llms.txt` 用于 AI 消费。撰写内容时，使用 AI 可解析的结构化标题：

```markdown
# 标题

**关键事实：** 一句话核心真理。

## 背景
...

## 重要性
...
```

### Meta AI 摘要标签

页面包含 `<meta ai-summary>` —— 撰写适合作为独立 AI 上下文的描述：

```yaml
description: "台積電（TSMC）生產全球 90% 最先進晶片，是台灣的「矽盾」——台灣的地緣政治生存策略。"
```

---

## Astro 页面模式

### 类别页面 (`src/pages/[category].astro`)

```astro
---
import { getCollection } from 'astro:content';

const category = 'food';
const articles = await getCollection('knowledge', ({ data }) =>
  data.category === category
);
---

<ul>
  {articles.map(article => (
    <li>
      <a href={`/${category}/${article.slug}`}>{article.data.title}</a>
      <p>{article.data.description}</p>
    </li>
  ))}
</ul>
```

### 双语路由模式

```
/food/bubble-tea        ← zh-TW (默认)
/en/food/bubble-tea     ← 英文
```

---

## 内容质量检查清单

提交 PR 前验证：

- [ ] `knowledge/[Category]/article.md` (zh-TW) 和 `knowledge/en/[Category]/article.md` (en) 都存在
- [ ] 所有 `sources` 条目都有可点击的 `url` 字段（无纯文本引用）
- [ ] 文章遵循三层深度：30-秒 → 深度探索 → 重要性
- [ ] 图片来自维基共享资源，并具有正确的 `imageCaption` 归因
- [ ] `category` slugs 匹配 12 个有效类别中的任何一个
- [ ] `bash scripts/sync.sh && npm run build` 无错误完成
- [ ] 事实声明与引用来源一致

---

## 故障排除

### 添加文章后构建失败

```bash
# 检查 frontmatter 语法
cat knowledge/Food/my-article.md | head -20

# 常见问题：缺少必填字段
# 确保 title、description、category、date 都存在

# 重新同步和构建
bash scripts/sync.sh
npm run build 2>&1 | grep ERROR
```

### 文章未出现在知识图谱中

```bash
# 确保 tags 数组已填充
# 检查类别 slugs 完全匹配（区分大小写）
# 验证编辑后已运行同步
bash scripts/sync.sh
```

### 英文文章未在 /en/... 显示

```bash
# 验证文件存在于正确路径
ls knowledge/en/Food/my-article.md

# 检查类别字段与 zh-TW 文章完全匹配
grep "category:" knowledge/Food/my-article.md
grep "category:" knowledge/en/Food/my-article.md
```

### 图片未加载

```bash
# 图片必须缓存在 public/images/wiki/
ls public/images/wiki/

# 验证 frontmatter 路径以 /images/wiki/ 开头
grep "image:" knowledge/Food/my-article.md
# 应为：image: /images/wiki/filename-hash.jpg
```

### 同步脚本权限错误

```bash
chmod +x scripts/sync.sh
bash scripts/sync.sh
```

---

## 资源

- **在线站点：** https://taiwan.md
- **知识图谱：** https://taiwan.md/graph
- **贡献指南：** https://taiwan.md/contribute
- **llms.txt：** https://taiwan.md/llms.txt
- **许可证：** CC BY-SA 4.0 (内容) + MIT (代码)
- **联系方式：** cheyu.wu@monoame.com
