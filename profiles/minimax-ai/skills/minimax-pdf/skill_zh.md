# minimax-pdf

三个任务。一项技能。

## 在进行任何 CREATE 或 REFORMAT 操作之前，请先阅读 `design/design.md`。

---

## 路由表

| 用户意图 | 路由 | 使用的脚本 |
|---|---|---|
| 从头开始生成一个新的 PDF | **CREATE** | `palette.py` → `cover.py` → `render_cover.js` → `render_body.py` → `merge.py` |
| 在现有的 PDF 中填写/完成表单字段 | **FILL** | `fill_inspect.py` → `fill_write.py` |
| 重新格式化/重新样式化现有文档 | **REFORMAT** | `reformat_parse.py` → 然后是完整的 CREATE 管道 |

**规则：** 在 CREATE 和 REFORMAT 之间不确定时，询问用户是否有现有文档作为起点。如果有 → REFORMAT。如果没有 → CREATE。

---

## 路由 A：CREATE

完整管道 — 内容 → 设计令牌 → 封面 → 正文 → 合并的 PDF。

```bash
bash scripts/make.sh run \
  --title "Q3 战略回顾" --type 提案 \
  --author "战略团队" --date "2025年10月" \
  --accent "#2D5F8A" \
  --content content.json --out report.pdf
```

**文档类型：** `报告` · `提案` · `简历` · `作品集` · `学术` · `通用` · `极简` · `条纹` · `对角线` · `框架` · `编辑` · `杂志` · `暗房` · `终端` · `海报`

| 类型 | 封面模式 | 视觉标识 |
|---|---|---|
| `报告` | `fullbleed` | 深色背景，点网格，Playfair Display |
| `提案` | `split` | 左侧面板 + 右侧几何图形，Syne |
| `简历` | `typographic` | 首字母超大，DM Serif Display |
| `作品集` | `atmospheric` | 近黑色，径向辉光，Fraunces |
| `学术` | `typographic` | 浅色背景，经典衬线，EB Garamond |
| `通用` | `fullbleed` | 深灰岩，Outfit |
| `极简` | `minimal` | 白色 + 单个 8px 强调条，Cormorant Garamond |
| `条纹` | `stripe` | 3 条粗水平色带，Barlow Condensed |
| `对角线` | `diagonal` | SVG 角切割，深色/浅色两半，Montserrat |
| `框架` | `frame` | 内嵌边框，角落装饰，Cormorant |
| `编辑` | `editorial` | 幽灵字母，全大写标题，Bebas Neue |
| `杂志` | `magazine` | 温暖米色背景，居中堆叠，英雄图像，Playfair Display |
| `暗房` | `darkroom` | 海军蓝背景，居中堆叠，灰度图像，Playfair Display |
| `终端` | `terminal` | 近黑色，网格线，等宽字体，霓虹绿色 |
| `海报` | `poster` | 白色背景，粗侧边栏，超大标题，Barlow Condensed |

封面额外功能（通过 `--abstract`，`--cover-image` 注入令牌）：
- `--abstract "text"` — 封面上的摘要文本块（杂志/暗房）
- `--cover-image "url"` — 英雄图像的 URL/路径（杂志，暗房，海报）

**颜色覆盖 — 始终根据文档内容选择：**
- `--accent "#HEX"` — 覆盖强调色；`accent_lt` 由向白色变亮自动导出
- `--cover-bg "#HEX"` — 覆盖封面背景色

**强调色选择指南：**

您对强调色有创作授权。从文档的语义上下文中选择它 — 标题、行业、目的、受众 — 而不是通用的“安全”选择。强调色出现在章节规则、强调条、表头和封面上：它承载了文档的视觉标识。

| 上下文 | 建议强调色范围 |
|---|---|
| 法律 / 合规 / 金融 | 深海军蓝 `#1C3A5E`，煤灰 `#2E3440`，石板 `#3D4C5E` |
| 医疗保健 / 医疗 | 青绿色 `#2A6B5A`，冷绿 `#3A7D6A` |
| 科技 / 工程 | 钢蓝 `#2D5F8A`，靛蓝 `#3D4F8A` |
| 环境 / 可持续发展 | 森林 `#2E5E3A`，橄榄 `#4A5E2A` |
| 创意 / 艺术 / 文化 | 紫红色 `#6B2A35`，紫罗兰 `#5A2A6B`，陶土 `#8A3A2A` |
| 学术 / 研究 | 深青 `#2A5A6B`，图书馆蓝 `#2A4A6B` |
| 企业 / 中性 | 石板 `#3D4A5A`，石墨 `#444C56` |
| 奢侈 / 高端 | 温暖黑色 `#1A1208`，深青铜 `#4A3820` |

**规则：** 选择一个深思熟虑的设计师会为这份特定文档选择的颜色 — 不是类型的默认值。柔和、去饱和的色调效果最佳；避免鲜艳的一级色。不确定时，选择更暗和更中性的颜色。

**content.json 块类型：**

| 块 | 用途 | 关键字段 |
|---|---|---|
| `h1` | 章节标题 + 强调规则 | `text` |
| `h2` | 子章节标题 | `text` |
| `h3` | 子子章节（粗体） | `text` |
| `body` | 两端对齐段落；支持 `<b>` `<i>` 标记 | `text` |
| `bullet` | 无序列表项（• 前缀） | `text` |
| `numbered` | 有序列表项 — 计数器在非数字块处自动重置 | `text` |
| `callout` | 带强调左侧条的突出显示见解框 | `text` |
| `table` | 数据表 — 强调表头，交替行色调 | `headers`，`rows`，`col_widths`？，`caption`？ |
| `image` | 嵌入式图像缩放到列宽 | `path`/`src`，`caption`？ |
| `figure` | 带自动编号“Figure N：”标题的图像 | `path`/`src`，`caption`？ |
| `code` | 带强调左侧边框的等宽代码块 | `text`，`language`？ |
| `math` | 展示数学 — LaTeX 语法通过 matplotlib mathtext | `text`，`label`？，`caption`？ |
| `chart` | 使用 matplotlib 渲染的条形图 / 线图 / 饼图 | `chart_type`，`labels`，`datasets`，`title`？，`x_label`？，`y_label`？，`caption`？，`figure`？ |
| `flowchart` | 带节点 + 边缘的流程图（通过 matplotlib） | `nodes`，`edges`，`caption`？，`figure`？ |
| `bibliography` | 带悬挂缩进的编号参考列表 | `items` [{id, text}], `title`？ |
| `divider` | 强调色全宽规则 | — |
| `caption` | 小型柔和标签 | `text` |
| `pagebreak` | 强制新页面 | — |
| `spacer` | 垂直空白 | `pt`（默认 12） |

**chart / flowchart 模式：**
```json
{"type":"chart","chart_type":"bar","labels":["Q1","Q2","Q3","Q4"],
 "datasets":[{"label":"收入","values":[120,145,132,178]}],"caption":"Q 结果"}

{"type":"flowchart",
 "nodes":[{"id":"s","label":"开始","shape":"oval"},
          {"id":"p","label":"处理","shape":"rect"},
          {"id":"d","label":"有效？","shape":"菱形"},
          {"id":"e","label":"结束","shape":"oval"}],
 "edges":[{"from":"s","to":"p"},{"from":"p","to":"d"},
          {"from":"d","to":"e","label":"是"},{"from":"d","to":"p","label":"否"}]}

{"type":"bibliography","items":[
  {"id":"1","text":"作者 (年份). 标题. 出版社."}]}
```

---

## 路由 B：FILL

在现有 PDF 中填写表单字段，而不改变布局或设计。

```bash
# 第 1 步：检查
python3 scripts/fill_inspect.py --input form.pdf

# 第 2 步：填写
python3 scripts/fill_write.py --input form.pdf --out filled.pdf \
  --values '{"FirstName": "Jane", "Agree": "true", "Country": "US"}'
```

| 字段类型 | 值格式 |
|---|---|
| `text` | 任何字符串 |
| `checkbox` | `"true"` 或 `"false"` |
| `dropdown` | 必须匹配检查输出中的选择值 |
| `radio` | 必须匹配单选值（通常以 `/` 开头） |

始终先运行 `fill_inspect.py` 获取确切的字段名称。

---

## 路由 C：REFORMAT

解析现有文档 → content.json → CREATE 管道。

```bash
bash scripts/make.sh reformat \
  --input source.md --title "我的报告" --type 报告 --out output.pdf
```

**支持的输入格式：** `.md` `.txt` `.pdf` `.json`

---

## 环境

```bash
bash scripts/make.sh check   # 验证所有依赖项
bash scripts/make.sh fix     # 自动安装缺失的依赖项
bash scripts/make.sh demo    # 构建一个示例 PDF
```

| 工具 | 由...使用 | 安装 |
|---|---|---|
| Python 3.9+ | 所有 `.py` 脚本 | 系统 |
| `reportlab` | `render_body.py` | `pip install reportlab` |
| `pypdf` | 填写，合并，重新格式化 | `pip install pypdf` |
| Node.js 18+ | `render_cover.js` | 系统 |
| `playwright` + Chromium | `render_cover.js` | `npm install -g playwright && npx playwright install chromium` |
