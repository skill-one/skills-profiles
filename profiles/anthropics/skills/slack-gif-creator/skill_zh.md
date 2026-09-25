# Slack GIF 创建工具

一个提供用于创建 Slack 优化的动画 GIF 的工具包，包含工具和知识。

## Slack 要求

**尺寸：**
- 表情符号 GIF：128x128（推荐）
- 消息 GIF：480x480

**参数：**
- FPS：10-30（越低文件越小）
- 颜色数：48-128（越少文件越小）
- 持续时间：表情符号 GIF 保持在 3 秒以内

## 核心工作流程

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

# 1. 创建构建器
builder = GIFBuilder(width=128, height=128, fps=10)

# 2. 生成帧
for i in range(12):
    frame = Image.new('RGB', (128, 128), (240, 248, 255))
    draw = ImageDraw.Draw(frame)

    # 使用 PIL 基本元素绘制动画
    # （圆形、多边形、线条等）

    builder.add_frame(frame)

# 3. 优化保存
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## 绘制图形

### 处理用户上传的图像
如果用户上传了图像，考虑他们是否想要：
- **直接使用**（例如，“动画化这个”，“把这个分割成帧”）
- **作为灵感**（例如，“制作类似这个的东西”）

使用 PIL 加载和处理图像：
```python
from PIL import Image

uploaded = Image.open('file.png')
# 直接使用，或仅作为颜色/样式的参考
```

### 从零开始绘制
当从零开始绘制图形时，使用 PIL ImageDraw 基本元素：

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(frame)

# 圆形/椭圆
draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)

# 星形、三角形、任何多边形
points = [(x1, y1), (x2, y2), (x3, y3), ...]
draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)

# 线条
draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)

# 矩形
draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
```

**不要使用：** 表情符号字体（跨平台不可靠）或假设存在预打包的图形。

### 使图形看起来更好

图形应该看起来精致且富有创意，而不是基础。以下是如何做到：

**使用更粗的线条** - 始终设置 `width=2` 或更高用于轮廓和线条。细线（width=1）看起来断断续续且业余。

**增加视觉深度**：
- 使用渐变背景（`create_gradient_background`）
- 通过叠加多个形状增加复杂性（例如，一个内部有较小星星的星星）

**使形状更有趣**：
- 不要只画一个普通的圆形 - 添加高光、光环或图案
- 星星可以有光晕（在后面绘制更大的半透明版本）
- 结合多个形状（星星+火花，圆形+光环）

**注意颜色**：
- 使用鲜艳的互补色
- 添加对比（深色轮廓在浅色形状上，浅色轮廓在深色形状上）
- 考虑整体构图

**对于复杂形状**（心形、雪花等）：
- 使用多边形和椭圆的组合
- 小心计算点以实现对称
- 添加细节（心形可以有高光曲线，雪花有复杂的分支）

发挥创意并注重细节！一个好的 Slack GIF 应该看起来精致，而不是像占位符图形。

## 可用工具

### GIFBuilder (`core.gif_builder`)
组装帧并针对 Slack 优化：
```python
builder = GIFBuilder(width=128, height=128, fps=10)
builder.add_frame(frame)  # 添加 PIL Image
builder.add_frames(frames)  # 添加帧列表
builder.save('out.gif', num_colors=48, optimize_for_emoji=True, remove_duplicates=True)
```

### 验证器 (`core.validators`)
检查 GIF 是否符合 Slack 要求：
```python
from core.validators import validate_gif, is_slack_ready

# 详细验证
passes, info = validate_gif('my.gif', is_emoji=True, verbose=True)

# 快速检查
if is_slack_ready('my.gif'):
    print("Ready!")
```

### 缓动函数 (`core.easing`)
平滑运动而不是线性：
```python
from core.easing import interpolate

# 从 0.0 到 1.0 的进度
t = i / (num_frames - 1)

# 应用缓动
y = interpolate(start=0, end=400, t=t, easing='ease_out')

# 可用：linear, ease_in, ease_out, ease_in_out,
#       bounce_out, elastic_out, back_out
```

### 帧辅助 (`core.frame_composer`)
用于常见需求的便利函数：
```python
from core.frame_composer import (
    create_blank_frame,         # 固色背景
    create_gradient_background,  # 垂直渐变
    draw_circle,                # 圆形辅助函数
    draw_text,                  # 简单文本渲染
    draw_star                   # 5 角星
)
```

## 动画概念

### 抖动/震动
使用振荡偏移对象位置：
- 使用 `math.sin()` 或 `math.cos()` 与帧索引
- 添加小的随机变化以获得自然感
- 应用于 x 和/或 y 位置

### 脉动/心跳
以节奏性缩放对象大小：
- 使用 `math.sin(t * frequency * 2 * math.pi)` 以获得平滑脉动
- 对于心跳：两个快速脉动然后暂停（调整正弦波）
- 缩放在基础大小的 0.8 到 1.2 之间

### 弹跳
对象下落并弹起：
- 使用 `interpolate()` 并设置 `easing='bounce_out'` 以实现落地
- 使用 `easing='ease_in'` 下落（加速）
- 每帧通过增加 y 速度应用重力

### 旋转/转动
围绕中心旋转对象：
- PIL: `image.rotate(angle, resample=Image.BICUBIC)`
- 对于摇晃：使用正弦波代替线性来设置角度

### 淡入/淡出
逐渐出现或消失：
- 创建 RGBA 图像，调整 alpha 通道
- 或使用 `Image.blend(image1, image2, alpha)`
- 淡入：alpha 从 0 到 1
- 淡出：alpha 从 1 到 0

### 滑动
将对象从屏幕外移动到位置：
- 起始位置：超出帧边界
- 结束位置：目标位置
- 使用 `interpolate()` 并设置 `easing='ease_out'` 以实现平滑停止
- 对于超调：使用 `easing='back_out'`

### 放大
缩放和定位以实现放大效果：
- 放大：缩放从 0.1 到 2.0，裁剪中心
- 缩小：缩放从 2.0 到 1.0
- 可以添加运动模糊以增强戏剧性（PIL 滤镜）

### 爆炸/粒子爆发
创建向外辐射的粒子：
- 生成具有随机角度和速度的粒子
- 更新每个粒子：`x += vx`, `y += vy`
- 添加重力：`vy += gravity_constant`
- 随时间淡出粒子（减少 alpha）

## 优化策略

仅在要求减小文件大小时，实施以下几种方法：

1. **减少帧数** - 降低 FPS（10 而不是 20）或缩短持续时间
2. **减少颜色数** - `num_colors=48` 而不是 128
3. **减小尺寸** - 128x128 而不是 480x480
4. **删除重复帧** - `remove_duplicates=True` 在保存时
5. **表情符号模式** - `optimize_for_emoji=True` 自动优化

```python
# 最大程度优化表情符号
builder.save(
    'emoji.gif',
    num_colors=48,
    optimize_for_emoji=True,
    remove_duplicates=True
)
```

## 哲学

此技能提供：
- **知识**：Slack 的要求和动画概念
- **工具**：GIFBuilder、验证器、缓动函数
- **灵活性**：使用 PIL 基本元素创建动画逻辑

它不提供：
- 刚性的动画模板或预制的函数
- 表情符号字体渲染（跨平台不可靠）
- 预打包的图形库

**关于用户上传**：此技能不包括预构建的图形，但如果用户上传了图像，请使用 PIL 加载并处理它 - 根据他们的请求解释他们是否想要直接使用或仅作为灵感。

发挥创意！结合概念（弹跳+旋转，脉动+滑动等），并使用 PIL 的全部功能。

## 依赖项

```bash
pip install pillow imageio numpy
```
