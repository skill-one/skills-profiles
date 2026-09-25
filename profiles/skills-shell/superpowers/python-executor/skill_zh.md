> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Python 代码执行器

在安全、沙盒化的环境中执行 Python 代码，内置 100+ 预装库。

![Python 代码执行器](https://cloud.inference.sh/u/33sqbmzt3mrg2xxphnhw5g5ear/01k8d8b4mckh6z89dhtxh72dsz.png)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 运行 Python 代码
belt app run infsh/python-executor --input '{
  "code": "import pandas as pd\nprint(pd.__version__)"
}'
```

## 应用详情

| 属性 | 值 |
|------|----|
| 应用 ID | `infsh/python-executor` |
| 环境 | Python 3.10, 仅 CPU |
| 内存 | 8GB (默认) / 16GB (high_memory) |
| 超时 | 1-300 秒 (默认: 30) |

## 输入模式

```json
{
  "code": "print('Hello World!')",
  "timeout": 30,
  "capture_output": true,
  "working_dir": null
}
```

## 预装库

### 网络抓取与 HTTP
- `requests`, `httpx`, `aiohttp` - HTTP 客户端
- `beautifulsoup4`, `lxml` - HTML/XML 解析
- `selenium`, `playwright` - 浏览器自动化
- `scrapy` - 网络抓取框架

### 数据处理
- `numpy`, `pandas`, `scipy` - 数值计算
- `matplotlib`, `seaborn`, `plotly` - 可视化

### 图像处理
- `pillow`, `opencv-python-headless` - 图像操作
- `scikit-image`, `imageio` - 图像算法

### 视频 & 音频
- `moviepy` - 视频编辑
- `av` (PyAV), `ffmpeg-python` - 视频处理
- `pydub` - 音频操作

### 3D 处理
- `trimesh`, `open3d` - 3D 网格处理
- `numpy-stl`, `meshio`, `pyvista` - 3D 文件格式

### 文档 & 绘图
- `svgwrite`, `cairosvg` - SVG 创建
- `reportlab`, `pypdf2` - PDF 生成

## 示例

### 网络抓取

```bash
belt app run infsh/python-executor --input '{
  "code": "import requests\nfrom bs4 import BeautifulSoup\n\nresponse = requests.get(\"https://example.com\")\nsoup = BeautifulSoup(response.content, \"html.parser\")\nprint(soup.find(\"title\").text)"
}'
```

### 数据分析与可视化

```bash
belt app run infsh/python-executor --input '{
  "code": "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndata = {\"name\": [\"Alice\", \"Bob\"], \"sales\": [100, 150]}\ndf = pd.DataFrame(data)\n\nplt.bar(df[\"name\"], df[\"sales\"])\nplt.savefig(\"outputs/chart.png\")\nprint(\"Chart saved!\")"
}'
```

### 图像处理

```bash
belt app run infsh/python-executor --input '{
  "code": "from PIL import Image\nimport numpy as np\n\n# 创建渐变图像\narr = np.linspace(0, 255, 256*256, dtype=np.uint8).reshape(256, 256)\nimg = Image.fromarray(arr, mode=\"L\")\nimg.save(\"outputs/gradient.png\")\nprint(\"Image created!\")"
}'
```

### 视频创建

```bash
belt app run infsh/python-executor --input '{
  "code": "from moviepy.editor import ColorClip, TextClip, CompositeVideoClip\n\nclip = ColorClip(size=(640, 480), color=(0, 100, 200), duration=3)\ntxt = TextClip(\"Hello!\", fontsize=70, color=\"white\").set_position(\"center\").set_duration(3)\nvideo = CompositeVideoClip([clip, txt])\nvideo.write_videofile(\"outputs/hello.mp4\", fps=24)\nprint(\"Video created!\")",
  "timeout": 120
}'
```

### 3D 模型处理

```bash
belt app run infsh/python-executor --input '{
  "code": "import trimesh\n\nsphere = trimesh.creation.icosphere(subdivisions=3, radius=1.0)\nsphere.export(\"outputs/sphere.stl\")\nprint(f\"Created sphere with {len(sphere.vertices)} vertices\")"
}'
```

### API 调用

```bash
belt app run infsh/python-executor --input '{
  "code": "import requests\nimport json\n\nresponse = requests.get(\"https://api.github.com/users/octocat\")\ndata = response.json()\nprint(json.dumps(data, indent=2))"
}'
```

## 文件输出

保存到 `outputs/` 的文件会自动返回：

```python
# 这些文件将在响应中
plt.savefig('outputs/chart.png')
df.to_csv('outputs/data.csv')
video.write_videofile('outputs/video.mp4')
mesh.export('outputs/model.stl')
```

## 变体

```bash
# 默认 (8GB 内存)
belt app run infsh/python-executor --input input.json

# 高内存 (16GB 内存) 用于大型数据集
belt app run infsh/python-executor@high_memory --input input.json
```

## 应用场景

- **网络抓取** - 从网站提取数据
- **数据分析** - 处理和可视化数据集
- **图像操作** - 调整大小、裁剪、合成图像
- **视频创建** - 生成带文本覆盖的视频
- **3D 处理** - 加载、转换、导出 3D 模型
- **API 集成** - 调用外部 API
- **PDF 生成** - 创建报告和文档
- **自动化** - 运行任何 Python 脚本

## 重要提示

- **仅 CPU** - 无 GPU/ML 库 (使用专用 AI 应用)
- **安全执行** - 在隔离的子进程中运行
- **非交互式** - 使用 `plt.savefig()` 而不是 `plt.show()`
- **文件检测** - 输出文件自动检测并返回

## 相关技能

```bash
# AI 图像生成 (用于基于 ML 的图像)
npx skills add inference-sh/skills@ai-image-generation

# AI 视频生成 (用于基于 ML 的视频)
npx skills add inference-sh/skills@ai-video-generation

# LLM 模型 (用于文本生成)
npx skills add inference-sh/skills@llm-models
```

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [应用代码](https://inference.sh/docs/extend/app-code) - 理解应用执行
- [沙盒化代码执行](https://inference.sh/blog/tools/sandboxed-execution) - 代理的安全代码执行
