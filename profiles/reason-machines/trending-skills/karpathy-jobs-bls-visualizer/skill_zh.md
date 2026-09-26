# karpathy/jobs — BLS就业市场可视化工具

> 技能数据由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

一个用于可视化探索劳工统计局 [职业展望手册](https://www.bls.gov/ooh/) 数据的研究工具，涵盖342种职业。交互式树状图根据就业规模（面积）和任意选择的指标（颜色）对矩形进行着色：BLS增长预期、中位数薪资、教育要求或LLM评分的AI接触程度。该流程完全可分支 — 编写新的提示词，重新运行评分，获得新的颜色层。

**在线演示:** [karpathy.ai/jobs](https://karpathy.ai/jobs/)

---

## 安装与设置

```bash
# 克隆仓库
git clone https://github.com/karpathy/jobs
cd jobs

# 安装依赖（使用uv）
uv sync
uv run playwright install chromium
```

创建一个 `.env` 文件，输入您的OpenRouter API密钥（仅用于LLM评分所需）：

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

---

## 完整流程 — 关键命令

按顺序运行这些命令以进行完整的全新构建：

```bash
# 1. 爬取BLS页面（非无头Playwright；BLS会封锁机器人）
#    结果缓存于html/ — 仅需运行一次
uv run python scrape.py

# 2. 将原始HTML转换为干净Markdown，存于pages/
uv run python process.py

# 3. 提取结构化字段 → occupations.csv
uv run python make_csv.py

# 4. 通过LLM评分AI接触程度（使用OpenRouter API，保存scores.json）
uv run python score.py

# 5. 合并CSV + 评分 → site/data.json供前端使用
uv run python build_site_data.py

# 6. 本地提供可视化服务
cd site && python -m http.server 8000
# 打开 http://localhost:8000
```

---

## 关键文件参考

| 文件 | 描述 |
|------|-------------|
| `occupations.json` | 342种职业的完整列表（标题、URL、类别、缩写） |
| `occupations.csv` | 摘要统计：薪资、教育、就业人数、增长预期 |
| `scores.json` | AI接触评分（0–10）+ 所有342种职业的推理 |
| `prompt.md` | 所有数据在一个约45K-token的文件中，用于粘贴到LLM |
| `html/` | 来自BLS的原始HTML页面（约40MB，事实依据） |
| `pages/` | 每个职业页面的干净Markdown版本 |
| `site/index.html` | 树状图可视化（单个HTML文件） |
| `site/data.json` | 前端使用的紧凑合并数据 |
| `score.py` | LLM评分流程 — 分支此文件以编写自定义提示词 |

---

## 编写自定义LLM评分层

最强大的功能：编写任何评分提示词，运行 `score.py`，获得新的树状图颜色层。

### 1. 编辑 `score.py` 中的提示词

```python
# score.py (简化结构)
SYSTEM_PROMPT = """
你正在评估未来10年内职业对拟人化机器人的接触程度。

对每个职业从0到10评分：
- 0 = 无意义接触（例如，需要精细社会判断、非物理性）
- 5 = 中度接触（某些任务可自动化，但人类仍居核心）
- 10 = 高度接触（重复性物理任务，可预测环境）

考虑：物理任务复杂度、环境可预测性、灵巧性要求，
机器人与人类的成本差异、监管障碍。

仅以JSON格式回复：{"score": <0-10的整数>, "rationale": "<1-2句话>"}
"""
```

### 2. 运行评分流程

```python
# 流程读取pages/中的每个职业Markdown，
# 发送到LLM，并将结果写入scores.json

# scores.json结构：
{
  "software-developers": {
    "score": 1,
    "rationale": "软件开发是数字和认知的；拟人化机器人不会带来优势。"
  },
  "construction-laborers": {
    "score": 7,
    "rationale": "物理性、重复性的户外任务是拟人化机器人应用的目标，尽管非结构化环境仍具挑战。"
  }
  // ... 共342种职业
}
```

### 3. 重建站点数据

```bash
uv run python build_site_data.py
cd site && python -m http.server 8000
```

---

## 数据结构

### `occupations.json` 条目

```json
{
  "title": "Software Developers",
  "url": "https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm",
  "category": "Computer and Information Technology",
  "slug": "software-developers"
}
```

### `occupations.csv` 列

```
slug, title, category, median_pay, education, job_count, growth_percent, growth_outlook
```

示例行：
```
software-developers, Software Developers, Computer and Information Technology,
130160, Bachelor's degree, 1847900, 17, Much faster than average
```

### `site/data.json` 条目（合并前端数据）

```json
{
  "slug": "software-developers",
  "title": "Software Developers",
  "category": "Computer and Information Technology",
  "median_pay": 130160,
  "education": "Bachelor's degree",
  "job_count": 1847900,
  "growth_percent": 17,
  "growth_outlook": "Much faster than average",
  "ai_score": 9,
  "ai_rationale": "AI正在深刻改变软件开发工作流程..."
}
```

---

## 前端树状图 (`site/index.html`)

可视化是一个自包含的HTML文件，使用D3.js。

### 颜色层（在UI中切换）

| 层级 | 显示内容 |
|-------|---------------|
| BLS Outlook | BLS预期增长类别（绿色=快速增长） |
| Median Pay | 年中位数工资（颜色渐变） |
| Education | 最少教育要求 |
| Digital AI Exposure | LLM评分的0–10 AI影响估计 |

### 为前端添加新的颜色层

```html
<!-- 在site/index.html中找到层级切换按钮 -->
<button onclick="setLayer('ai_score')">Digital AI Exposure</button>

<!-- 添加新的层级按钮 -->
<button onclick="setLayer('robotics_score')">Humanoid Robotics</button>
```

```javascript
// 在colorScale函数中，为新的字段添加case：
function getColor(d, layer) {
  if (layer === 'robotics_score') {
    // 评分0-10，蓝色=低接触，红色=高
    return d3.interpolateRdYlBu(1 - d.robotics_score / 10);
  }
  // ... 现有case
}
```

然后更新 `build_site_data.py` 以将新的评分字段包含在 `data.json` 中。

---

## 生成LLM准备提示文件

将342种职业+汇总统计打包为单个文件，用于LLM对话：

```bash
uv run python make_prompt.py
# 生成prompt.md (~45K tokens)
# 粘贴到Claude、GPT-4、Gemini等，进行数据驱动对话
```

---

## 爬取说明

BLS封锁自动化机器人，因此 `scrape.py` 使用**非无头**Playwright（真实可见浏览器窗口）：

```python
# scrape.py关键行为
browser = await p.chromium.launch(headless=False)  # 必须可见
# 页面保存到html/<slug>.html
# 已爬取页面被缓存
```

如果爬取失败或被限流：
- 确保 `scrape.py` 中 `headless=False`（默认已设置）
- 添加手动延迟；不要在CI中运行
- 仓库中的 `html/` 目录已包含缓存页面
- 可以跳过爬取，直接从 `process.py` 开始运行
- 如果重新爬取，请求间添加延迟以避免封锁

---

## 常见模式

### 仅重新评分缺失的职业

```python
import json, os

with open("scores.json") as f:
    existing = json.load(f)

with open("occupations.json") as f:
    all_occupations = json.load(f)

# 查找缺失项
missing = [o for o in all_occupations if o["slug"] not in existing]
print(f"缺失评分: {len(missing)}")
# 然后用过滤缺失缩写的参数运行score.py
```

### 手动解析单个职业页面

```python
from parse_detail import parse_occupation_page
from pathlib import Path

html = Path("html/software-developers.html").read_text()
data = parse_occupation_page(html)
print(data["median_pay"])     # e.g. 130160
print(data["job_count"])      # e.g. 1847900
print(data["growth_outlook"]) # e.g. "Much faster than average"
```

### 加载和查询 occupations.csv

```python
import pandas as pd

df = pd.read_csv("occupations.csv")

# 前十高薪职业
top_pay = df.nlargest(10, "median_pay")[["title", "median_pay", "growth_outlook"]]
print(top_pay)

# 筛选：高速增长+高薪
high_value = df[
    (df["growth_percent"] > 10) &
    (df["median_pay"] > 80000)
].sort_values("median_pay", ascending=False)
```

### 合并CSV与AI评分进行数据分析

```python
import pandas as pd, json

df = pd.read_csv("occupations.csv")

with open("scores.json") as f:
    scores = json.load(f)

df["ai_score"] = df["slug"].map(lambda s: scores.get(s, {}).get("score"))
df["ai_rationale"] = df["slug"].map(lambda s: scores.get(s, {}).get("rationale"))

# 高AI接触+高薪 — 重塑，而非消失
high_exposure_high_pay = df[
    (df["ai_score"] >= 8) &
    (df["median_pay"] > 100000)
][["title", "median_pay", "ai_score", "growth_outlook"]]
print(high_exposure_high_pay)
```

---

## 故障排除

**`playwright install` 失败**
```bash
uv run playwright install --with-deps chromium
```

**BLS爬取封锁/返回空页面**
- 确保 `scrape.py` 中 `headless=False`（默认已设置）
- 添加手动延迟；不要在CI中运行
- 仓库中的 `html/` 目录可直接使用

**`score.py` OpenRouter错误**
- 验证 `.env` 中 `OPENROUTER_API_KEY` 已设置
- 检查您的OpenRouter账户是否有积分
- 默认模型是Gemini Flash — 在 `score.py` 中更改 `model` 以使用不同LLM

**`site/data.json` 重新评分后未更新**
```bash
# 更改scores.json后始终重建站点数据
uv run python build_site_data.py
```

**树状图显示空白/无数据**
- 确认 `site/data.json` 存在且是有效的JSON
- 使用 `python -m http.server` 提供（不要用 `file://` — CORS会封锁本地JSON获取）
- 检查浏览器控制台是否有获取错误

---

## 重要注意事项（来自项目）

- **AI接触程度≠职业消失。** 评分9/10意味着AI正在*重塑*工作，而非减少需求。软件开发者评分9/10但需求在增长。
- **评分是粗略的LLM估计**（通过OpenRouter的Gemini Flash），而非严谨的经济预测。
- 该工具**不**考虑需求弹性、潜在需求、监管障碍或人类对劳动者的社会偏好。
- 这是一个**开发/研究工具**，而非经济出版物。
