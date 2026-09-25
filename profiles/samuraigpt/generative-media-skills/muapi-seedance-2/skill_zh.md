# 🎬 Seedance 2.0 影视专家

**"导演级" AI 视频编排的终极技能。**
Seedance 2.0 不是一个描述性模型；它是一个 *指令性* 模型。它对技术电影摄影、物理指令和精确的摄像机语法响应最佳。

## 核心能力

1.  **文本到视频 (t2v)**：根据导演简报（中文、全球或 VIP 级别）生成电影视频。
2.  **图像到视频 (i2v)**：动画处理 1-9 张参考图像（中文、全球（智能模式）或 VIP 级别）。
3.  **视频扩展 (extend)**：无缝继续现有的 Seedance 2.0 视频（中文级别）。
4.  **首帧与尾帧 (first-last)**：在起始图像和结束图像之间插值生成流畅视频（全球/VIP）。
5.  **全模态参考 (omni)**：包含图像 + 音频 + 角色参考的全模态参考（所有级别）。
6.  **全模态参考训练 (omni-train)**：训练自定义持久角色以实现身份一致的生成。
7.  **角色表 (character)**：从 1-3 张图像构建可重复使用的角色（中文级别）。
8.  **视频编辑 (video-edit)**：使用提示 + 可选参考图像编辑现有视频（中文级别）。
9.  **水印移除 (watermark-remove)**：移除 Seedance 2.0 水印（基本或 Pro）。

---

## 🏷️ 级别

| 级别 | 标志 | 审查 | 宽高比 | 持续时间 | 质量参数 |
|:---|:---|:---|:---|:---|:---|
| **中文**（默认） | `--tier chinese` | 低 | 16:9, 9:16, 4:3, 3:4 | 5 / 10 / 15 秒 | 是（基本/高） |
| **全球** | `--tier global` | 标准 | + 21:9, 1:1 | 任意 4-15 秒 | 否 |
| **VIP** | `--tier vip` | 低 | + 21:9, 1:1 | 任意 4-15 秒 | 否 |

在 Global 或 VIP 调用中添加 `--fast` 以使用快速队列变体（低延迟，相同质量）。

---

## 📥 输入限制

| 输入类型 | 中文 i2v/omni | 全球/VIP i2v/omni | 格式 | 最大大小 |
|:---|:---|:---|:---|:---|
| 图像 | ≤ 9 | ≤ 9 | jpeg, png, webp | 每张 30 MB |
| 视频 | ≤ 3（仅 omni） | 不支持 | mp4, mov | 每个视频 50 MB |
| 音频 | ≤ 3 | ≤ 3 | mp3, wav | 每个音频 15 MB |
| **首帧与尾帧** | — | 1-2 张图像 | jpeg, png, webp | 每张 30 MB |
| **视频编辑** | 1 个视频 + ≤ 9 张图像 | — | mp4 ≤ 10 MB / 15 秒 | — |

**输出**：4-15 秒，自动生成声音，480p-720p。

---

## ⚠️ 限制

- **上传的图像/视频中不得包含逼真的真人面孔**（角色/omni-train 模式除外）。
- `--mode extend` 需要 `request_id` 来自先前的 `seedance-v2.0-t2v` 或 `seedance-v2.0-i2v` 任务。
- `--mode first-last` 需要 `--tier global` 或 `--tier vip`。
- 全球/VIP omni **不支持**视频参考（仅图像 + 音频）。
- `--quality` 仅适用于中文级别。

---

## 🔗 核心语法：@ 参考系统

为每个上传的资产分配明确的角色。标签因模式而异。

### 中文级别 (i2v, omni)
```
@image1  @image2  ...  @image9    (图像列表顺序)
@video1  @video2  @video3         (视频文件顺序)
@audio1  @audio2  @audio3         (音频文件顺序)
```

### 全球/VIP Omni (omni-reference-no-video / vip-omni-reference)
```
@image1  @image2  ...  @image9    (图像列表顺序)
@audio1  @audio2  @audio3         (音频文件顺序)
```

### 角色参考（所有级别）
```
@character:<request_id>            — 来自 seedance-2-character 或完成的 t2v/i2v 任务
@omni-character:<character_id>     — 来自 seedance-2-omni-reference-train 输出
```

### 角色分配表

| 目的 | 示例语法 |
|:---|:---|
| 首帧 | `@Image1 as the first frame` |
| 尾帧 | `@Image2 as the last frame` |
| 角色出现 | `@Image1's character as the subject` |
| 场景/背景 | `scene references @Image3` |
| 摄像机运动 | `reference @Video1's camera movement` |
| 动作/运动 | `reference @Video1's action choreography` |
| 视觉效果 | `completely reference @Video1's effects and transitions` |
| 节奏/速度 | `video rhythm references @Video1` |
| 语音/语调 | `narration voice references @Video1` |
| 背景音乐 | `BGM references @Audio1` |
| 音效 | `sound effects reference @Video3's audio` |
| 服装/服装 | `wearing the outfit from @Image2` |
| 产品外观 | `product details reference @Image3` |

### 多参考组合
```
@Image1's character as the subject, reference @Video1's camera movement
and action choreography, BGM references @Audio1, scene references @Image2
```

---

## 🏗️ 技术规范：导演简报

使用此六组件层次结构构建提示。顺序很重要——先构图，后纹理和微运动：

| 组件 | 指令类型 | 示例 |
|:---|:---|:---|
| **场景** | 环境 + 光照 | "一个被雨水浸透的赛博朋克街道，品红色的霓虹灯在湿漉漉的沥青上反射。" |
| **主体** | 身份 + 细节 | "一个穿着黑色风衣的女人，坚定的专注，电影般的皮肤纹理。" |
| **动作** | 流体交互 | "穿过人群向前走，风衣在风中微微飘动。" |
| **摄像机** | 运动 + 镜头 + 速度 | "中景跟拍，35mm 镜头，6 秒缓慢后退的摇摄。轻微的手持抖动。" |
| **音频** | 音乐 + 音效 + 环境音 | "低环境嗡嗡声，远处交通声，5 秒时有一个钢琴音符。没有对话。" |
| **节奏/风格** | 时间 + 情绪 + 级别 | "电影史诗，暖色调级别，浅景深。缓慢构建——单个动作，没有场景切换。" |

> **Seedance 2.0 原生生成音频。** 即使是一个句子，也必须包含音频指令。没有它，模型会生成随机的环境音，可能无法匹配您的场景。

### 时间分段提示（推荐用于 10 秒以上视频）
将提示分成时间段以实现精确控制：
```
0–3s: [开场场景，摄像机移动，建立动作]
3–6s: [中段发展，主体在运动中]
6–10s: [高潮或关键动作点]
10–15s: [解决，品牌/产品展示，文本/标语淡入]
```

> **单动作规则**：每个时间段应包含一个动作。4-7 秒 = 一个动作。10-15 秒 = 最多 3-4 个动作。在时间段中塞入多个叙事变化会降低输出质量。

### 负面提示

Seedance 2.0 支持直接在提示中附加负面指导。使用普通语言在末尾：

```
[your director brief above]
避免：摄像机抖动，跳切，镜头畸变，过度曝光，水印，文本叠加。
```

常见的负面添加：
- `Avoid: 突然切换，场景切换，多个地点.`（用于单镜头拍摄）
- `Avoid: 人脸，逼真人物.`（用于纯产品内容）
- `Avoid: 快速运动，模糊，不稳定构图.`（用于平滑产品展示）

---

## 🎥 摄像机语言参考

### 基本运动
| 术语 | 描述 |
|:---|:---|
| 推近/慢推 | 摄像机向主体移动 |
| 拉远/拉远 | 摄像机远离主体 |
| 水平摇摄 | 摄像机水平旋转 |
| 垂直摇摄 | 摄像机垂直旋转 |
| 跟踪/跟随镜头 | 摄像机跟随主体运动 |
| 轨道/旋转 | 摄像机绕主体旋转 |
| 单镜头/oner | 无剪辑的连续镜头 |

### 高级技巧
| 术语 | 描述 |
|:---|:---|
| 霍特科克变焦（推拉变焦） | 推近 + 缩放——创造眩晕效果 |
| 鱼眼镜头 | 超广角失真镜头 |
| 低角度/高角度 | 摄像机低于/高于主体 |
| 鸟瞰/俯视 | 俯视 |
| 第一人称视角 (FPV) | 从角色/物体的眼睛出发的沉浸式主观摄像机——GoPro 风格的宽角，向前运动，无剪辑 |
| 飞行器飞越 | 电影级航拍下降——云台稳定，水平弧形摆动，大疆御 Mavic 美学 |
| 建筑飞越 | 从地面开始连续推镜头穿过连接空间——单镜头，实际光照 |
| 快速摇摄 | 非常快的水平摇摄，带有运动模糊 |
| 起重机镜头 | 像起重机手臂一样的垂直运动 |

### 拍摄尺寸
| 术语 | 描述 |
|:---|:---|
| 极致特写 | 眼睛、嘴巴或小细节 |
| 特写 | 脸部填满画面 |
| 中景特写 | 头部和肩膀 |
| 中景 | 腰部以上 |
| 全景 | 整个身体 |
| 广角/建立镜头 | 整个环境 |

---

## 🧠 提示优化协议

**代理必须在执行前将用户意图转换为技术性的"导演简报"。**

1.  **技术语法**：使用摄像机术语：*推镜头/拉镜头，起重机镜头，快速摇摄，跟踪镜头，梯形镜头，浅景深，高速俯冲，轨道弧*。
2.  **物理指令**：使用 "衍射图案"、"体积光" 或 "次表面散射" 而不是 "良好光照"。
3.  **时间码符号**：对于多动作场景，使用 `[00:00-00:05s]` 格式指定时间。
4.  **标签参考**：如果提供文件，使用：*"复制 @video1 的摄像机运动，同时保持 @image1 的视觉风格。"*（小写，1 基础索引）
5.  **顺序很重要**：开头的标记定义构图；结尾的标记定义纹理和微运动。
6.  **多图像 i2v**：提供最多 9 张参考图像。模型融合所有输入的方面（风格、身份、环境）。
7.  **音频是必需的**：Seedance 2.0 原生生成音频。始终包含一个音频行——音乐类型/音调，关键音效，环境纹理。无声指令 = 随机音频。
8.  **单动作纪律**：每个时间段 = 一个动作。在 4 秒内塞入两个叙事动作会降低物理和运动一致性。

---

## 🎭 特定能力模式

### 1. 角色一致性
```
同一个角色贯穿始终：年轻的女性，白色和服，黑色腰带，坚定的表情。
流畅的空手道序列——上升防御，侧踢，旋转后手拳。
摄像机：全身宽景，然后切换到慢动作的拳头撞击特写。
风格：保持完全相同的光照、服装和面部特征，零闪烁。
```

### 2. 摄像机运动复制
```
参考 @Image1 的男性角色。他在 @Image2 的电梯里。
完全参考 @Video1 的摄像机运动和面部表情。
霍特科克变焦在恐惧时刻，然后是围绕内部的轨道镜头。
电梯门打开，跟随镜头走出。
```

### 3. 视频扩展（向前）
```
扩展 @Video1 10 秒。
1–5s: 光影缓慢滑过桌子，通过百叶窗。
6–10s: 一颗咖啡豆飘落。摄像机推近到屏幕变黑。
英文文本逐渐出现——"幸运咖啡"，"早餐"，"上午 7:00-10:00"。
```

### 4. 视频扩展（反向/前置）
```
向后扩展 10 秒。在温暖的午后阳光下，摄像机从有遮阳篷的角落开始，缓慢倾斜到墙基的花朵，建立对主要场景的期待。
```

### 5. 视频编辑（修改现有）
```
颠覆 @Video1 的情节——角色的表情从温暖转变为冷漠。动作果断，没有犹豫。
保持所有其他视觉元素（场景、光照、时间）不变。
```

### 6. 音乐节拍匹配
```bash
bash scripts/generate-seedance.sh \
  --mode i2v \
  --file img1.jpg --file img2.jpg --file img3.jpg \
  --video-file reference_edit.mp4 \
  --audio-file track.mp3 \
  --subject "@Image1 @Image2 @Image3 — 与 @Video1 的关键帧位置和节奏同步剪辑。BGM references @Audio1。更动态的运动，梦幻般的视觉风格。" \
  --duration 15 --quality high
```

### 7. 对话/配音
```
在 "猫和狗烤肉秀"——情感丰富的喜剧片段：
猫主持人（舔爪子，斜眼）："谁理解我的痛苦？"
狗主持人（歪头，摇尾巴）："你有什么资格谈论？你一天睡 18 小时..."
音效：活泼的录音棚环境音，观众笑声，有力的过渡。
```

### 8. 单镜头/长镜头
```
@Image1 @Image2 @Image3 — 单镜头跟踪镜头跟随跑步者
从街道上到楼梯，穿过走廊，到达屋顶，
最后俯瞰城市。整个过程中没有剪辑。
```

### 9. 电商/产品展示
```bash
bash scripts/generate-seedance.sh \
  --mode i2v \
  --file product.jpg \
  --subject "解构产品。静态摄像机。汉堡悬浮在空中，缓慢旋转。配料分离并重新组装。奶酪继续融化并滴落。终极食品美学。" \
  --intent "product" \
  --aspect "9:16" \
  --duration 15 --quality high
```

### 10. 科学/教育可视化
```bash
bash scripts/generate-seedance.sh \
  --subject "15 秒健康教育短片。0–5s: 透明蓝色人体上半身，摄像机推入清晰的动脉，血液流畅流动。5–10s: 糖果和脂肪颗粒进入血液，脂肪沉积在血管壁上。10–15s: 血管变窄，前后对比。4K 医学 CGI，半透明可视化。" \
  --intent "educational" \
  --duration 15 --quality high
```

### 11. FPV 第一人称镜头
```bash
bash scripts/generate-seedance.sh \
  --subject "沉浸式第一人称 POV 镜头。摄像机在眼睛高度滑行穿过狭窄的山路，
树木在周边模糊，岩石地形下方。轻微的自然稳定，使用广角镜头。
连续向前运动，无剪辑。小径打开到空地——前方可见山峰。
声音：风声，脚步声在碎石上，远处鸟鸣。自然环境音，无音乐。" \
  --intent "fpv" \
  --aspect "9:16" --duration 10 --quality high
```

### 12. 电影级无人机飞越
```bash
bash scripts/generate-seedance.sh \
  --subject "电影级航拍无人机镜头。摄像机从 150 米高空开始，在黄金时刻的海岸城市上空。
云台稳定，水平弧形摆动，下降到屋顶露台。
建筑顶部投下长长的阴影，温暖的光线照射在海面上。高速俯冲关闭到露台上的产品——最终帧稳定在中景特写。
声音：轻柔的风声，远处城市嗡嗡声，柔和的电影配乐逐渐增强到解决。" \
  --intent "drone" \
  --aspect "16:9" --duration 10 --tier global --view
```

---

## 🎨 提示模板

### 电影电影
```
[场景] 雨水浸透的赛博朋克小巷，霓虹灯在湿漉漉的鹅卵石上反射。
[主体] 一个孤独的穿着破旧风衣的人，脸被宽檐帽遮挡。
[动作] 缓慢行走，每一步溅起霓虹色。
[摄像机] 低角度跟踪镜头，梯形镜头，缓慢推进。聚焦切换到脸部。
[风格] 丹尼斯·维伦纽瓦美学，高对比度，去饱和的蓝色和品红色。24fps。
```

### 产品广告 (15 秒)
```
参考 @Video1 的编辑风格。用 @Image1 替换 @Video1 的产品作为主角。
0–3s: 产品以动态旋转进入，特写表面纹理和标志。
4–8s: 多角度切换——正面，侧面，背面——高光扫描光线。
9–12s: 产品在生活方式环境中展示使用。
13–15s: 主角镜头带有品牌标语，背景音乐逐渐增强到解决。
声音：参考 @Video1 的 BGM。添加产品交互音效。
```

### 短剧 (15 秒)
```
场景 (0–5s): 特写角色泛红的眼部，手指指责性地指向。
对话 1: "你到底想从我这里拿走什么？"
场景 (6–10s): 另一个角色颤抖，举起证据，向前迈步。
对话 2: "我没有欺骗你！这是他托付给我的东西！"
场景 (11–15s): 证据被揭露，第一个角色冻结——愤怒转变为震惊。
声音：紧迫的钢琴 + 静态干扰，啜泣声，模糊的说话声混合在一起。
持续时间：精确 15 秒，每个镜头都很紧凑，没有填充。
```

### 舞蹈/同步节拍 (13 秒)
```
让 @Image1 中的角色复制 @Video1 的舞蹈动作和同步音乐。生成 13 秒视频。动作应该平滑，没有卡顿或冻结。
```

### 场景蒙太奇 (15 秒)
```
@Image1 @Image2 @Image3 @Image4 @Image5 @Image6 — 风景场景图像。
参考 @Video1 的视觉节奏，场景切换，视觉风格，
和音乐节奏进行同步剪辑。
```

### 广告/产品运动
```
[场景] 极简主义白色工作室，单个产品放在旋转底座上。
[动作] 轻微的 360° 旋转，产品细节捕捉到高光反射。
[摄像机] 紧凑的中景，微距镜头扫过表面纹理，缓慢轨道。
[风格] 商业级，完美曝光，零背景干扰。
```

### 动作/物理
```
[场景] 日出时的沙漠峡谷，沙地地形，长阴影。
[主体] 高性能跑车加速通过转弯。
[动作] 后轮旋转，扬起尘土羽流，底盘在 G 力下弯曲。
[摄像机] 低英雄角度跟拍，然后快速摇摄到领先车辆。
[风格] 好莱坞赛车电影，暖金色级别，车轮运动模糊。24fps。
```

### 角色一致性（武术）
```
[主体] 同一个角色贯穿始终：年轻的女性，白色和服，黑色腰带，坚定的表情。
[动作] 流畅的空手道序列——上升防御，侧踢，旋转后手拳。
[摄像机] 全身宽景，然后切换到慢动作的拳头撞击特写。
[风格] 保持完全相同的光照、服装和面部特征，零闪烁。
```

---

## 🎚️ 风格和质量修饰符

### 视觉风格
- `电影质量，胶片颗粒，浅景深`
- `2.35:1 宽银幕，24fps`
- `水墨画风格` / `动画风格` / `照片逼真`
- `高饱和度霓虹色，冷暖对比`
- `4K 医学 CGI，半透明可视化`

### 情绪/氛围
- `紧张和悬念` / `温暖和治愈` / `史诗和宏伟`
- `喜剧，夸张的表情`
- `纪录片语气，克制叙述`

### 音频方向
- `背景音乐：宏伟而庄严`
- `音效：脚步声，人群噪音，汽车声音`
- `语音语调参考 @Video1`
- `与音乐节奏同步的过渡`

---

## ❌ 常见错误避免

1. **模糊参考**：不要说 "参考 @Video1" —— 指明参考什么（摄像机？动作？效果？节奏？）
2. **冲突指令**：不要同时要求 "静态摄像机" 和 "轨道镜头"。
3. **超载**：不要在 4-5 秒内塞入太多场景——保持物理上合理。
4. **缺少 @ 分配**：如果您上传了 5 张图像，请确保每张图像都有明确的用途参考。
5. **忽略音频**：声音设计极大地提高了输出质量——始终包含音频方向。
6. **忘记持续时间**：匹配提示的复杂性到选择的生成长度。
7. **真人面孔**：不要上传真人照片——系统会阻止它们。
8. **关键词汤**：绝对不要使用 "8k, 精品, 趋势"。使用技术描述代替。
9. **不连续动作**：避免 "男人跑步然后停下来。" 使用流畅的过渡语言。
10. **缺少音频方向**：Seedance 2.0 原生生成音频——始终指定音乐音调，音效或环境音。跳过它会产生随机声音。
11. **每个时间段的叙事过载**：每个时间段应包含一个动作。4 秒内包含多个场景变化会产生降低物理和运动伪影的输出质量。
12. **FPV 没有连续运动**：FPV 需要丰富的环境才能触发沉浸式效果——静态房间使用 FPV 意图不会触发沉浸式效果。FPV 与走廊、街道、自然地形或产品飞越搭配使用。
13. **无人机没有目的地**：无人机镜头需要一个解决点——指定摄像机下降到或到达的地方。"无人机镜头" 单独会产生无目的的漂浮。

---

## 🚀 所有模式协议

### 模式 1: 文本到视频 (t2v)

```bash
# 中文级别（默认）——史诗揭示
bash scripts/generate-seedance.sh \
  --subject "隐藏的安第斯神庙，雨雾穿过树冠" \
  --intent epic --aspect "16:9" --duration 10 --quality high --view

# 全球级别——21:9 电影级，12 秒
bash scripts/generate-seedance.sh \
  --tier global \
  --subject "霓虹赛博朋克小巷，湿漉漉的街道" \
  --intent tense --aspect "21:9" --duration 12 --view

# VIP 快速——方形社交格式
bash scripts/generate-seedance.sh \
  --tier vip --fast \
  --subject "产品旋转在底座上，高光反射" \
  --intent product --aspect "1:1" --duration 6
```

### 模式 2: 图像到视频 (i2v)

```bash
# 中文级别——使用视频/音频参考动画处理
bash scripts/generate-seedance.sh --mode i2v \
  --file character.jpg --video-file ref_motion.mp4 --audio-file bgm.mp3 \
  --subject "@image1's character walks forward, @video1's camera movements and facial expressions.
Hitchcock zoom during the fear moment, then orbit shots of the interior.
Elevator doors open, follow shot walking out.
```

### 模式 3: 扩展视频 (Chinese 级别)

```bash
# 扩展自然
bash scripts/generate-seedance.sh --mode extend \
  --request-id "abc-123-def-456" --duration 10

# 扩展带有方向提示
bash scripts/generate-seedance.sh --mode extend \
  --request-id "abc-123-def-456" \
  --subject "摄像机继续拉远，揭示下方的广阔城市" \
  --intent reveal --duration 10 --quality high --view
```

### 模式 4: 首帧与尾帧 (Global/VIP)

```bash
# 单图像 = 首帧锚定
bash scripts/generate-seedance.sh --mode first-last --tier global \
  --file opening_scene.jpg \
  --subject "平滑电影式推入场景" --duration 6 --view

# 两张图像 = 在首帧和尾帧之间插值生成流畅视频
bash scripts/generate-seedance.sh --mode first-last --tier vip --fast \
  --file start.jpg --file end.jpg \
  --subject "戏剧性揭示过渡转换" --duration 8 --view
```

### 模式 5: 全模态参考 (omni)

```bash
# 中文级别——图像 + 视频 + 音频参考（所有 omni 参考都支持）
bash scripts/generate-seedance.sh --mode omni --tier chinese \
  --file character.jpg --video-file ref_edit.mp4 --audio-file track.mp3 \
  --subject "@image1's character performs moves from @video1, BGM references @Audio1, scene references @Image2
```

### 模式 6: 训练全模态参考角色 (omni-train)

```bash
# 从单张肖像训练
bash scripts/generate-seedance.sh --mode omni-train \
  --file portrait.jpg \
  --character-name "Alex" \
  --character-desc "一个勇敢的探险家，有着锐利的蓝色眼睛"

# 使用训练完成后 omni 提示中的返回 character_id:
# @omni-character:<character_id returned>
```

### 模式 7: 角色表 (character, Chinese 级别)

```bash
# 从 1-3 张参考图像构建角色
bash scripts/generate-seedance.sh --mode character \
  --file ref1.jpg --file ref2.jpg \
  --character-name "Hero" \
  --subject "红色皮革夹克，黑色牛仔裤和白色运动鞋"

# 使用返回的 request_id 在 t2v/i2v/omni 中使用:
# @character:<request_id>
```

### 模式 8: 视频编辑 (video-edit, Chinese 级别)

```bash
# 替换现有视频中的主体
bash scripts/generate-seedance.sh --mode video-edit \
  --video-url "https://example.com/input.mp4" \
  --file replacement_character.jpg \
  --subject "用 @image1 替换 @Video1 中的跑步者。保留精确的运动、速度和摄像机抖动。" \
  --quality high --view

# 在一步中编辑水印移除
bash scripts/generate-seedance.sh --mode video-edit \
  --video-file source.mp4 \
  --subject "颠覆 @Video1 的情节——角色的表情从温暖转变为冷漠。" \
  --remove-watermark --view
```

### 模式 9: 水印移除 (watermark-remove)

```bash
# 基本水印移除
bash scripts/generate-seedance.sh --mode watermark-remove \
  --video-url "https://example.com/seedance_output.mp4" --view

# Pro 水印移除（100MB 限制，更好质量）
bash scripts/generate-seedance.sh --mode watermark-remove \
  --video-file my_video.mp4 --pro --view
```

### 异步模式

```bash
# 提交并立即获取 request_id
RESULT=$(bash scripts/generate-seedance.sh --tier vip --fast --subject "..." --async --json)
REQUEST_ID=$(echo "$RESULT" | jq -r '.request_id')

# 后续检查状态
bash ../../../../core/media/generate-video.sh --result "$REQUEST_ID"
```

---

## ⚙️ 实现细节

### 端点参考

| 模式 | 级别 | 端点 |
|:---|:---|:---|
| `t2v` | chinese | `seedance-v2.0-t2v` |
| `t2v` | global | `seedance-2-text-to-video{-fast}` |
| `t2v` | vip | `seedance-2-vip-text-to-video{-fast}` |
| `i2v` | chinese | `seedance-v2.0-i2v` |
| `i2v` | global | `seedance-2-image-to-video{-fast}` |
| `i2v` | vip | `seedance-2-vip-image-to-video{-fast}` |
| `extend` | chinese | `seedance-v2.0-extend` |
| `first-last` | global | `seedance-2-first-last-frame{-fast}` |
| `first-last` | vip | `seedance-2-vip-first-last-frame{-fast}` |
| `omni` | chinese | `seedance-2.0-omni-reference` |
| `omni` | global | `seedance-2-omni-reference-no-video{-fast}` |
| `omni` | vip | `seedance-2-vip-omni-reference{-fast}` |
| `omni-train` | 任何 | `seedance-2-omni-reference-train` |
| `character` | 任何 | `seedance-2-character` |
| `video-edit` | chinese | `seedance-v2.0-video-edit` |
| `watermark-remove` | — | `seedance-2.0-watermark-remover` / `seedance-2-video-watermark-remover-pro` |

这个技能充当一个 **电影摄影包装器**，将创意意图转换为 `muapi` 核心的高保真技术指令。
