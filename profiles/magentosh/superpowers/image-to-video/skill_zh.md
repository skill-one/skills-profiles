> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# 图像转视频

通过 [inference.sh](https://inference.sh) CLI 将静态图像转换为动画视频。

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 生成静态图像
belt app run falai/flux-dev-lora --input '{
  "prompt": "日落时分的宁静山湖，雪峰倒映在平静的水面，黄金时刻的光线，风景摄影",
  "width": 1248,
  "height": 832
}'

# 动画化它
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "湖面轻柔的涟漪，云朵缓慢飘动，温暖光线变化，远处飞鸟",
  "image": "path/to/lake-image.png"
}'
```

## 模型选择

| 模型 | App ID | 适合场景 | 运动风格 |
|------|--------|----------|---------|
| **Wan 2.5 i2v** | `falai/wan-2-5-i2v` | 真实运动，自然动作 | 照片级真实，微妙 |
| **WAN-I2V (Pruna)** | `pruna/wan-i2v` | 经济实惠，快速，480p/720p | 自然，高效 |
| **Seedance 2.0** | `bytedance/seedance-2-0` | 最高1080p，同步音频，所有输入类型 | 多功能，高质量 |
| **Seedance 2.0 Fast** | `bytedance/seedance-2-0-fast` | 快速变体，相同功能 | 多功能，快速 |
| **Fabric 1.0** | `falai/fabric-1-0` | 布料，织物，液体，流动材料 | 基于物理的流动 |
| **Grok Imagine Video** | `xai/grok-imagine-video` | 通用动画，文本引导 | 多功能 |

### 每个模型的使用场景

| 场景 | 最佳模型 | 原因 |
|------|---------|------|
| 带水域/云朵的风景 | **Wan 2.5 i2v** | 最擅长自然、真实的运动 |
| 带微妙表情的肖像 | **Wan 2.5 i2v** | 保持面部保真度 |
| 带布料/织物的产品 | **Fabric 1.0** | 专精于材料物理 |
| 拍挥动的旗帜，飘动的窗帘 | **Fabric 1.0** | 布料模拟 |
| 插画/艺术图像 | **Seedance 2.0** | 匹配风格化内容 |
| 通用“赋予生命” | **Seedance 2.0** | 全能型，最高1080p |
| 快速测试/迭代 | **Seedance 2.0 Fast** | 更快的生成 |

## 运动类型

### 摄像机运动

| 运动 | 提示关键词 | 效果 |
|------|-----------|------|
| 推近/前移 | "缓慢前移", "摄像机靠近" | 增加亲密感/聚焦 |
| 后退/拉远 | "摄像机后退", "缓慢拉远" | 揭示，提供背景 |
| 左右平移 | "摄像机缓慢向右平移" | 扫描，跟随 |
| 上下倾斜 | "摄像机向上倾斜" | 揭示高度 |
| 环绕 | "摄像机围绕主体旋转" | 3D探索 |
| 俯仰上升 | "摄像机向上上升" | 宏大揭示 |
| 静态 | (无摄像机运动提示) | 仅主体运动 |

### 主体运动

| 类型 | 提示示例 |
|------|---------|
| 自然元素 | "水面涟漪", "云朵飘动", "树叶在风中沙沙作响" |
| 头发/衣物 | "头发轻柔地随风飘动", "连衣裙布料流动" |
| 大气效果 | "雾气缓慢滚动", "光束中漂浮的尘埃" |
| 人物 | "人物缓慢转向摄像机", "轻微呼吸运动" |
| 机械 | "齿轮转动", "钟表指针移动" |
| 液体 | "咖啡蒸汽上升", "颜料滴落", "水倾倒" |

## 提示最佳实践

### 黄金法则：微妙 > 戏剧性

AI视频模型在**温和、微小的运动**下效果优于戏剧性动作。请求过多运动会导致失真和伪影。

```
❌ "人物跑过障碍物，同时摄像机旋转"
✅ "人物缓慢向前行走，轻柔微风，摄像机跟随"

❌ "爆炸，碎片四散飞溅"
✅ "蜡烛火焰轻柔闪烁，温暖环境光线变化"

❌ "快速推近眼睛，伴随剧烈摄像机抖动"
✅ "缓慢前移靠近主体，微妙焦点变化"
```

### 提示结构

```
[摄像机运动] + [主体运动] + [大气效果] + [情绪/节奏]
```

### 按场景示例

```bash
# 风景动画
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "缓慢向右平移，水面倒映移动的云朵，树木轻微随风摇曳，温暖金色光线，宁静缓慢",
  "image": "landscape.png"
}'

# 肖像动画
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "轻微呼吸运动，轻微转头，自然眨眼，头发轻柔移动，柔和环境光线变化",
  "image": "portrait.png"
}'

# 产品拍摄动画
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "缓慢360度环绕产品，轻柔聚光灯移动，微妙反射变化，高端产品展示，平滑运动",
  "image": "product.png",
  "generate_audio": true
}'

# 布料/织物动画
belt app run falai/fabric-1-0 --input '{
  "prompt": "织物在轻柔风中流动和涟漪，自然布料物理，轻柔运动",
  "image": "fabric-scene.png"
}'

# 建筑可视化
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "缓慢前移穿过入口，轻微摄像机向上倾斜，环境光线透过窗户，光束中尘埃",
  "image": "building-interior.png"
}'
```

## 时长指南

| 时长 | 质量 | 适用于 |
|------|------|--------|
| 2-3秒 | 最高质量 | GIF，循环背景，动态照片 |
| 4-5秒 | 高质量 | 社交媒体帖子，产品展示 |
| 6-8秒 | 良好质量 | 短视频，过渡 |
| 10秒+ | 质量显著下降 | 避免使用，除非拼接短片段 |

### 延长时长

对于长视频，生成多个短片段并拼接：

```bash
# 从同一图像生成3个带渐进运动的片段
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "缓慢向左平移，轻柔水面运动",
  "image": "scene.png"
}' --no-wait

belt app run falai/wan-2-5-i2v --input '{
  "prompt": "继续平移，云朵变化，光线变化",
  "image": "scene.png"
}' --no-wait

# 拼接
belt app run infsh/media-merger --input '{
  "media": ["clip1.mp4", "clip2.mp4"]
}'
```

## 完整工作流程

### 静态到最终视频流程

```bash
# 1. 生成源图像（最佳质量）
belt app run bytedance/seedream-4-5 --input '{
  "prompt": "电影感风景，黎明时分的雾气山峦，前景湖面，戏剧性云朵，黄金时刻，4K质量，专业摄影",
  "size": "2K"
}'

# 2. 动画化图像
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "轻柔雾气穿过山谷，湖面涟漪，云朵缓慢移动，远处飞鸟，温暖光线变化",
  "image": "landscape.png"
}'

# 3. 如需，视频升频
belt app run falai/topaz-video-upscaler --input '{
  "video": "animated-landscape.mp4"
}'

# 4. 添加环境音效
belt app run infsh/hunyuanvideo-foley --input '{
  "video": "animated-landscape.mp4",
  "prompt": "轻柔自然环境音，远处飞鸟，轻柔风声，水波声"
}'

# 5. 视频与音频合并
belt app run infsh/video-audio-merger --input '{
  "video": "upscaled-landscape.mp4",
  "audio": "ambient-audio.mp3"
}'
```

## 动态照片效果

动态照片是一张静态照片，其中只有一个元素在移动（例如，冻结场景中的瀑布移动）。要实现这一点：

1. 生成带有清晰运动元素的静态图像
2. 仅在特定元素中提示运动
3. 保持2-4秒以实现无缝循环

```bash
belt app run falai/wan-2-5-i2v --input '{
  "prompt": "只有瀑布在移动，其他所有东西都保持完美静止，水流平稳，场景其他部分冻结",
  "image": "waterfall-scene.png"
}'
```

## 常见错误

| 错误 | 问题 | 修复 |
|------|------|------|
| 请求过多运动 | 失真，伪影，扭曲 | 微妙 > 戏剧性，始终 |
| 内容类型模型错误 | 结果不佳 | 使用上方选择指南 |
| 片段过长（10秒+） | 质量显著下降 | 保持3-5秒，如需拼接 |
| 未指定摄像机运动 | 随机/不可预测运动 | 始终指定摄像机行为 |
| 冲突运动方向 | 混乱，不自然 | 一个主要运动方向 |
| 低分辨率源图像 | 低分辨率视频输出 | 从最高质量源开始 |
| 复杂动作场景 | 模型无法处理 | 保持简单自然运动 |

## 相关技能

```bash
npx skills add inference-sh/skills@ai-video-generation
npx skills add inference-sh/skills@ai-image-generation
npx skills add inference-sh/skills@p-video
npx skills add inference-sh/skills@video-prompting-guide
npx skills add inference-sh/skills@prompt-engineering
```

浏览所有应用：`belt app list`
