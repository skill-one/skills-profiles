## 如何使用

阅读单个规则文件以获取详细说明和代码示例：

### 核心概念
- [rules/scenes.md](rules/scenes.md) - 场景结构、构造方法、场景类型
- [rules/mobjects.md](rules/mobjects.md) - Mobject类型、VMobject、组以及定位
- [rules/animations.md](rules/animations.md) - 动画类、播放动画以及时间控制

### 创建与变换
- [rules/creation-animations.md](rules/creation-animations.md) - 创建、写入、淡入、绘制边框然后填充
- [rules/transform-animations.md](rules/transform-animations.md) - 变换、替换变换、变形
- [rules/animation-groups.md](rules/animation-groups.md) - AnimationGroup、LaggedStart、Succession

### 文本与数学
- [rules/text.md](rules/text.md) - 文本Mobject、字体以及样式
- [rules/latex.md](rules/latex.md) - MathTex、Tex、LaTeX渲染以及公式着色
- [rules/text-animations.md](rules/text-animations.md) - 写入、逐字母添加文本、带光标的输入

### 样式与外观
- [rules/colors.md](rules/colors.md) - 颜色常量、渐变以及颜色操作
- [rules/styling.md](rules/styling.md) - 填充、描边、不透明度以及视觉属性

### 定位与布局
- [rules/positioning.md](rules/positioning.md) - move_to、next_to、align_to、shift方法
- [rules/grouping.md](rules/grouping.md) - VGroup、Group、排列以及布局模式

### 坐标系与绘图
- [rules/axes.md](rules/axes.md) - Axes、NumberPlane、坐标系
- [rules/graphing.md](rules/graphing.md) - 绘制函数、参数曲线
- [rules/3d.md](rules/3d.md) - ThreeDScene、3D坐标轴、曲面、相机方向

### 动画控制
- [rules/timing.md](rules/timing.md) - Rate函数、缓动、run_time、lag_ratio
- [rules/updaters.md](rules/updaters.md) - Updaters、ValueTracker、动态动画
- [rules/camera.md](rules/camera.md) - MovingCameraScene、缩放、平移、帧操作

### 配置与CLI
- [rules/cli.md](rules/cli.md) - 命令行界面、渲染选项、质量标志
- [rules/config.md](rules/config.md) - 配置系统、manim.cfg、设置

### 形状与几何
- [rules/shapes.md](rules/shapes.md) - 圆形、正方形、矩形、多边形以及几何基本元素
- [rules/lines.md](rules/lines.md) - Line、Arrow、Vector、DashedLine以及连接器

## 工作示例

展示常见模式的完整、已测试示例文件：

- [examples/basic_animations.py](examples/basic_animations.py) - 形状创建、文本、延迟动画、路径移动
- [examples/math_visualization.py](examples/math_visualization.py) - LaTeX方程式、着色数学、推导
- [examples/updater_patterns.py](examples/updater_patterns.py) - ValueTracker、动态动画、物理模拟
- [examples/graph_plotting.py](examples/graph_plotting.py) - 坐标轴、函数、区域、黎曼和、极坐标图
- [examples/3d_visualization.py](examples/3d_visualization.py) - ThreeDScene、曲面、3D相机、参数曲线

## 场景模板

复制并修改这些模板以开始新项目：

- [templates/basic_scene.py](templates/basic_scene.py) - 标准2D场景模板
- [templates/camera_scene.py](templates/camera_scene.py) - 带缩放/平移的MovingCameraScene
- [templates/threed_scene.py](templates/threed_scene.py) - 带曲面和相机旋转的3D场景

## 快速参考

### 基本场景结构
```python
from manim import *

class MyScene(Scene):
    def construct(self):
        # 创建Mobject
        circle = Circle()

        # 添加到场景（静态）
        self.add(circle)

        # 或者动画
        self.play(Create(circle))

        # 等待
        self.wait(1)
```

### 渲染命令
```bash
# 带预览的基本渲染
manim -pql scene.py MyScene

# 质量标志：-ql（低）、-qm（中）、-qh（高）、-qk（4k）
manim -pqh scene.py MyScene
```

### 与3b1b/ManimGL的主要区别

| 功能 | Manim社区 | 3b1b/ManimGL |
|------|----------|-------------|
| 导入 | `from manim import *` | `from manimlib import *` |
| CLI | `manim` | `manimgl` |
| 数学文本 | `MathTex(r"\pi")` | `Tex(R"\pi")` |
| 场景 | `Scene` | `InteractiveScene` |
| 包 | `manim` (PyPI) | `manimgl` (PyPI) |

### Jupyter Notebook支持

使用`%%manim`单元魔法：

```python
%%manim -qm MyScene
class MyScene(Scene):
    def construct(self):
        self.play(Create(Circle()))
```

### 常见陷阱避免

1. **版本混淆** - 确保使用`manim`（社区版），而不是`manimgl`（3b1b版本）
2. **检查导入** - `from manim import *`是ManimCE；`from manimlib import *`是ManimGL
3. **过时的教程** - 视频教程可能已过时；优先选择官方文档
4. **manimpango问题** - 如果文本渲染失败，检查manimpango安装要求
5. **PATH问题（Windows）** - 如果找不到`manim`命令，使用`python -m manim`或检查PATH

### 安装

```bash
# 安装Manim社区版
pip install manim

# 检查安装
manim checkhealth
```

### 有用命令

```bash
manim -pql scene.py Scene    # 预览低质量（开发）
manim -pqh scene.py Scene    # 预览高质量
manim --format gif scene.py  # 输出为GIF
manim checkhealth            # 验证安装
manim plugins -l             # 列出插件
```
