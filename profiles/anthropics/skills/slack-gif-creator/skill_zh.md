# Slack GIF 创建器

一个为优化版 Slack 的动画 GIF 提供工具与知识的工具包。

## Slack 要求

**尺寸：**
- 表情 GIF：128x128（推荐）
- 消息 GIF：480x480

**参数：**
- FPS：10-30（越低文件越小）
- 颜色：48-128（越少文件越小）
- 时长：表情 GIF 需控制在 3 秒以内

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

    # 使用 PIL 原语绘制你的动画
    # (圆形、多边形、线条等)

    builder.add_frame(frame)

# 3. 使用优化进行保存
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## 绘制图形

### 处理用户上传的图像
如果用户上传了图像，请考虑他们是否想要：
- **直接使用**（例如“为这个动画”、“将此拆分为帧”）
- **作为灵感**（例如“制作类似这样的内容”）

使用 PIL 加载并处理图像：
```python
from PIL import Image

uploaded = Image.open('file.png')
# 直接使用，或仅作为颜色和样式的参考
```

### 从零绘制
从零绘制图形时，使用 PIL ImageDraw 原语：

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(frame)

# 圆形/椭圆
draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)

# 星星、三角形、任意多边形
points = [(x1, y1), (x2, y2), (x3, y3), ...]
draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)

# 线条
draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)

# 矩形
draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
```

**请勿使用：** 跨平台不可靠的表情字体，或假设本技能中存在预打包的图形。

### 让图形看起来更出色
图形应看起来精致且富有创意，而非基础的。以下是方法：

**使用较粗的线条** - 为轮廓和线条始终设置 `width=2` 或更高的值。细线条（`width=1`）看起来粗糙、不专业。

**增加视觉深度**：
- 为背景使用渐变（`create_gradient_background`）
- 叠加多个形状以增加复杂度（例如，一个带有内部小星星的星星）

**让形状更有趣**：
- 不要只绘制普通的圆形——添加高光、环或图案
- 星星可以添加光晕（在后方绘制更大、半透明的版本）
- 组合多个形状（星星+闪光、圆形+环）

**注意颜色**：
- 使用鲜艳、互补的颜色
- 增加对比度（浅色形状用深色轮廓，深色形状用浅色轮廓）
- 考虑整体构图

**对于复杂形状**（爱心、雪花等）：
- 使用多边形和椭圆的组合
- 仔细计算点以保证对称性
- 添加细节（爱心可以有一个高光曲线，雪花有复杂的分支）

发挥创意并做到详细！好的 Slack GIF 应该看起来精致，而不像占位图。

## 可用工具

### GIFBuilder（`core.gif_builder`）
组装帧并为 Slack 优化：
```python
builder = GIFBuilder(width=128, height=128, fps=10)
builder.add_frame(frame)  # 添加 PIL Image
builder.add_frames(frames)  # 添加帧列表
builder.save('out.gif', num_colors=48, optimize_for_emoji=True, remove_duplicates=True)
```

### Validators（`core.validators`）
检查 GIF 是否符合 Slack 要求：
```python
from core.validators import validate_gif, is_slack_ready

# 详细验证
passes, info = validate_gif('my.gif', is_emoji=True, verbose=True)

# 快速检查
if is_slack_ready('my.gif'):
    print("Ready!")
```

### Easing 函数（`core.easing`）
实现平滑运动而非线性运动：
```python
from core.easing import interpolate

# 进度从 0.0 到 1.0
t = i / (num_frames - 1)

# 应用缓动
y = interpolate(start=0, end=400, t=t, easing='ease_out')

# 可用：linear, ease_in, ease_out, ease_in_out,
#           bounce_out, elastic_out, back_out
```

### 帧辅助工具（`core.frame_composer`）
常见需求的便捷函数：
```python
from core.frame_composer import (
    create_blank_frame,         # 纯色背景
    create_gradient_background,  # 垂直渐变
    draw_circle,                # 圆形辅助工具
    draw_text,                  # 简单文本渲染
    draw_star                   # 五角星
)
```

## 动画概念

### 晃动/震动
通过振荡偏移对象位置：
- 使用带有帧索引的 `math.sin()` 或 `math.cos()`
- 添加小的随机变化以增强自然感
- 应用于 x 轴和/或 y 轴位置

### 脉冲/心跳
有节奏地缩放对象大小：
- 使用 `math.sin(t * frequency * 2 * math.pi)` 实现平滑脉冲
- 对于心跳：两次快速脉冲后暂停（调整正弦波）
- 在基础大小的 0.8 到 1.2 之间缩放

### 弹跳
对象下落并弹跳：
- 使用 `interpolate()` 并设置 `easing='bounce_out'` 处理落地
- 使用 `easing='ease_in'` 处理下落（加速运动）
- 通过在每一帧增加 y 轴速度来施加重力

### 旋转
围绕中心旋转对象：
- PIL：`image.rotate(angle, resample=Image.BICUBIC)`
- 对于摇摆效果：使用正弦波代替线性波动角度

### 淡入/淡出
逐渐出现或消失：
- 创建 RGBA 图像并调整 alpha 通道
- 或使用 `Image.bland(image1, image2, alpha)`
- 淡入：alpha 从 0 到 1
- 淡出：alpha 从 1 到 0

### 滑动
将对象从屏幕外移动到指定位置：
- 起始位置：超出帧边界
- 结束位置：目标位置
- 使用 `interpolate()` 并设置 `easing='ease_out'` 实现平滑停止
- 对于过冲效果：使用 `easing='back_out'`

### 缩放
缩放并定位以产生缩放效果：
- 放大：从 0.1 缩放到 2.0，裁剪中心部分
- 缩小：从 2.0 缩放到 1.0
- 可以添加动感模糊以增强戏剧效果（PIL 滤镜）

### 爆炸/粒子爆发
生成向外辐射的粒子：
- 使用随机角度和速度生成粒子
- 更新每个粒子：`x += vx`，`y += vy`
- 添加重力：`vy += gravity_constant`
- 随时间淡出粒子（减小 alpha）

## 优化策略

仅在要求减小文件大小时，实现以下几种方法：

1. **减少帧数** - 降低 FPS（如 10 而非 20）或缩短时长
2. **减少颜色** - 使用 `num_colors=48` 而非 128
3. **减小尺寸** - 使用 128x128 而非 480x480
4. **去除重复** - 在 `save()` 中使用 `remove_duplicates=True`
5. **表情模式** - `optimize_for_emoji=True` 自动优化

```python
# 为表情最大优化
builder.save(
    'emoji.gif',
    num_colors=48,
    optimize_for_emoji=True,
    remove_duplicates=True
)
```

## 理念

本技能提供：
- **知识**：Slack 的要求与动画概念
- **工具**：GIFBuilder、validators、缓动函数
- **灵活性**：使用 PIL 原语创建动画逻辑

本技能不提供：
- 固定的动画模板或预制的函数
- 跨平台不可靠的表情字体渲染
- 本技能内置的预打包图形库

**关于用户上传**：本技能不包含预构建的图形，但如果用户上传了图像，请使用 PIL 加载并处理该图像——根据他们的请求判断是需要直接使用，还是仅作为灵感。

发挥创意！结合概念（弹跳+旋转、脉冲+滑动等）并使用 PIL 的全部功能。

## 依赖

```bash
pip install pillow imageio numpy
```
