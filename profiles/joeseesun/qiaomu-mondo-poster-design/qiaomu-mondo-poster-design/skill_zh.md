# Mondo 风格设计生成器

生成 AI 图像提示 **并** 创建具有 Mondo 独特另类美学的实际设计 - 以限量版丝网印刷海报、书籍封面和专辑艺术为特色，色彩大胆、构图极简、象征性叙事。

**这项技能可以：**
- 为任何主题生成详细的 Mondo 风格提示
- 通过 AI Gateway API 直接创建实际图像
- 设计电影海报、书籍封面、专辑封面、活动海报
- 提供针对特定类型和格式的模板

## 核心Mondo美学

Mondo海报的特点是：

1. **艺术再诠释** - 不是字面化的电影场景，而是概念性的视觉提炼
2. **丝网印刷美学** - 有限的调色板（2-5种颜色）、平面色块、半色调纹理
3. **极简象征主义** - 关键道具、剪影、人物面部的负空间
4. **大胆复古字体** - 手绘字母、压缩无衬线字体、装饰艺术影响
5. **复古调色板** - 高饱和度、复古双色调、大胆对比（橙色/蓝绿色、红色/奶油色等）

## 提示结构

生成Mondo风格提示时，使用此模板：

```
[主题] in Mondo poster style, [构图], [调色板],
丝网印刷美学, 限量版海报艺术, [关键视觉元素],
[纹理/效果], 极简设计, 复古电影海报, [情绪/基调]
```

### 必要组件

**风格锚点**（必须包含）：
- "Mondo poster style" 或 "alternative movie poster"
- "丝网印刷美学" 或 "silkscreen print"
- "限量版海报艺术"
- "复古[年代]电影海报"（60年代/70年代/80年代）

**构图技巧**（选择1-2个）：
- 中心对称构图
- 剪影对[颜色]背景
- 负空间叙事
- 几何框架（圆形、三角形、拱形）
- 前景/中景/背景的分层深度

**色彩策略**（明确指定）：
- 有限调色板： "3-color screen print: [颜色1], [颜色2], [颜色3]"
- 双色调："[暖色]和[冷色]双色调"
- 复古方案： "70年代调色板：焦橙色、芥末黄、棕色"
- 高对比度： "大胆[颜色]在[颜色]背景上"

**视觉元素**（象征性，非字面化）：
- 关键道具或物体（武器、交通工具、标志性物品）
- 剪影覆盖详细的面部
- 几何形状隐藏图像
- 环境氛围（雾、雨、阴影）
- 象征性动物或自然元素

**纹理与效果**（增加真实性）：
- "halftone dot texture"
- "risograph printing effect"
- "paper texture grain"
- "颜色层之间轻微错位"
- "复古印刷瑕疵"

## 艺术家特定变化

对于不同的Mondo艺术家风格，请参阅 [references/artist-styles.md](references/artist-styles.md)。

**快速参考：**
- **Tyler Stout风格**：密集的角色拼贴、复杂的细节、极简构图
- **Olly Moss风格**：超极简、巧妙的负空间、1-2种颜色
- **Martin Ansin风格**：装饰艺术影响、优雅的线条、柔和的复古色调

## 示例提示（针对简洁设计优化）

### 黑色电影（极简）
```
侦探剪影戴着费多拉帽 in Mondo poster style, 垂直9:16肖像,
中心单个人物, 3-color screen print: 深蓝色、奶油色、红色强调,
简洁极简构图, halftone texture, 复古1940年代美学
```

### 科幻（极简眼睛窗口）
```
宇航员头盔面罩反射外星行星 in Mondo poster style, 垂直9:16,
中心圆形构图, 3-color screen print: 橙色、蓝绿色、黑色, 单个焦点元素,
负空间叙事, 干净复古1970年代科幻美学
```

### 恐怖（象征性建筑）
```
维多利亚式宅邸单个亮灯窗户 in Mondo poster style, 垂直9:16肖像,
中心哥特式剪影, 3-color screen print: 黑色、酒红色、奶油色, 单个焦点,
简洁简单构图, 复古1970年代恐怖美学
```

## 高级负空间技巧

大师级的Mondo设计使用**图形-背景反转** - 其中负空间（没有油墨的区域）形成有意义的形状。这创造了双层视觉体验，带有隐藏的惊喜。

### 技巧1：巧妙的视觉双关（Olly Moss风格）
**一个元素承担双重作用：**
- 剪影包含负空间内的另一个场景
- 背景形状就是故事元素
- 未展示的比展示的更能说明问题

**示例结构：**
```
[主题剪影] in Mondo poster style, 垂直9:16, 负空间在剪影内揭示[隐藏元素], Olly Moss图形-背景反转, 2-color duotone: [颜色1]和[颜色2], 巧妙的双重图像, 未展示的讲述故事
```

**现实灵感：**
- 达斯·维达剪影与AT-ST战斗场景在负空间
- 侦探帽的负空间形成城市天际线
- 刀刃反射反派剪影

### 技巧2：比例对比戏剧性
**微小与巨大创造情感冲击：**
- 小型人类形象+巨大物体/生物
- 强调孤立、惊奇或威胁
- 使用70%的负空间留出空间

**示例结构：**
```
微小的[主题]与巨大的[对象]俯视 in Mondo poster style, 垂直9:16,
戏剧性比例对比, [主题]仅占底部20%, 上方广阔负空间
2-3 color screen print, 感觉[情绪：敬畏/孤立/危险]
```

### 技巧3：单一形状叙事
**一个标志性形状捕捉整个叙事：**
- 无杂乱，无多个元素
- 让一个完美的符号完成所有工作
- 30%图形，30%文本，40%空白空间（2024最佳实践）

**示例结构：**
```
单个[标志性物体/符号]在Mondo poster style中居中, 垂直9:16,
仅此一个元素, 周围是广阔的负空间, 2-color print: [颜色1]在[颜色2]背景上, Olly Moss超极简方法, 一个图像讲述完整故事
```

## 已验证的成功模式

基于成功的生成，这些模式始终能带来卓越的结果：

### 模式1：单一焦点（极简干净）
**关键原则：**
- 仅有一个中心元素（眼睛、物体、剪影）
- 垂直9:16格式
- 最多2-3种颜色
- 焦点周围的负空间
- 干净、无杂乱、标志性

**简化结构：**
```
[单一元素] in Mondo poster style, 垂直9:16, 中心单一焦点,
3-color screen print: [颜色1], [颜色2], [颜色3], 干净极简构图,
复古[年代]美学, 简洁且标志性
```

### 模式2：氛围单一主题（干净分层）
**关键原则：**
- 单一主要主题与简单背景
- 垂直9:16格式
- 3-4种颜色营造氛围
- 主题在前景，简单背景
- 干净构图，不杂乱

**简化结构：**
```
[主要主题] in Mondo poster style, 垂直9:16, 单一主题与[简单背景],
3-color screen print: [氛围色彩], 干净构图, 复古[年代]美学,
专注且简单
```

## 工作流程

1. **确定主题** - 电影、书籍、专辑、乐队、活动或概念
2. **选择象征性元素** - 哪个单一图像捕捉本质？
3. **选择构图模式** - 极简象征性或分层氛围
4. **选择调色板** - 最多2-4种颜色，高对比度，复古灵感
5. **添加纹理关键词** - 丝网印刷、半色调、risograph效果
6. **设定时代** - 指定60年代/70年代/80年代以获得时代准确的审美

## 获取最佳结果的技巧

**要：**
- 指定确切的颜色名称和数量（"3-color: 焦橙色、奶油色、海军蓝"）
- 使用几何构图术语（中心、对称、负空间）
- 参考特定年代以获得复古准确性
- 强调象征性而非字面元素
- 包含纹理/印刷过程关键词

**不要：**
- 使用照片写实或数字渐变术语
- 请求复杂的面部细节（使用剪影代替）
- 混合过多风格（保持专注于丝网印刷美学）
- 忘记复古时代背景（60年代-80年代是关键）
- 错过负空间机会

## 高级：针对特定格式的方案

针对详细格式和类型特定模板：
- [references/genre-templates.md](references/genre-templates.md) - 恐怖、科幻、西部、黑色电影等
- [references/composition-patterns.md](references/composition-patterns.md) - 布局策略和视觉层次
- [references/book-covers.md](references/book-covers.md) - 书籍封面设计模式和最佳实践
- [references/artist-styles.md](references/artist-styles.md) - Tyler Stout、Olly Moss、Martin Ansin等

## 🚀 增强功能（新功能！）

### 1. AI驱动的提示优化

让AI增强您的提示，同时**尊重您的原始意图**：

```bash
python3 scripts/generate_mondo_enhanced.py "银翼杀手" 电影 --ai-enhance
```

**工作原理：**
- 接收您的原始想法
- 添加一个完美的象征性元素
- 建议互补的颜色（您可以覆盖）
- 使用负空间技巧
- 保持干净和极简

**示例：**
```bash
# 您的输入: "盗梦空间电影"
# AI增强为: "旋转陀螺在Mondo poster style中，垂直9:16，单个标志性物体，
# 负空间揭示梦境层次，2-color duotone: 金色和深蓝色，Olly Moss极简方法"
```

### 2. 三列风格对比

生成三个不同风格并排显示以选择最佳：

```bash
python3 scripts/generate_mondo_enhanced.py "沙丘" 电影 --compare saul-bass,olly-moss,kilian-eng
```

**非常适合：**
- 探索不同的艺术方法
- 客户演示
- 为您的主题找到最佳风格

### 3. 图像到图像转换

将现有海报转换为Mondo风格：

```bash
python3 scripts/generate_mondo_enhanced.py "黑色电影惊悚片" 电影 --input original_poster.jpg --style saul-bass
```

**用例：**
- 将照片海报转换为插图风格
- 应用Mondo美学到现有设计
- 重新想象经典海报

### 4. 20位最伟大的海报艺术家

现在包括20位传奇艺术家风格：

**贝尔·艾波克先驱者：**
- `jules-cheret` - 明亮快乐的色彩，动态女性形象
- `toulouse-lautrec` - 平面色块，日本影响，大胆剪影
- `alphonse-mucha` - 新艺术流动曲线，装饰性花卉
- `steinlen` - 社会写实，表现性线条，猫主题
- `eugène-grasset` - 中世纪哥特式，彩色玻璃美学

**现代主义大师：**
- `saul-bass` - 极简几何抽象，视觉隐喻
- `cassandre` - 立方体平面，戏剧性透视，装饰艺术
- `milton-glaser` - 超现实波普艺术，创新字体
- `josef-muller-brockmann` - 瑞士网格，数学精确性
- `paul-rand` - 欢乐几何，巧妙的视觉双关

**电影传奇：**
- `drew-struzan` - 绘画现实主义，史诗电影，怀旧光泽
- `olly-moss` - 超极简负空间，隐藏图像
- `tyler-stout` - 极简主义拼贴，复杂细节
- `martin-ansin` - 装饰艺术优雅，精致复古
- `laurent-durieux` - 视觉双关，神秘氛围

**当代：**
- `kilian-eng` - 几何未来主义，精确技术线条
- `dan-mccarthy` - 超平面几何抽象
- `jock` - 粗糙表现性笔触，动态动作
- `shepard-fairey` - 宣传风格，半色调，政治
- `jay-ryan` - 民间风格，温暖纹理简单
- `paula-scher` - 字体极简主义，分层文本

**查看所有风格：**
```bash
python3 scripts/generate_mondo_enhanced.py --list-styles
```

### 5. 智能色彩建议

AI建议互补颜色，但您可以覆盖：

```bash
# 让AI建议颜色
python3 scripts/generate_mondo_enhanced.py "爵士音乐节" 活动 --style jules-cheret

# 或指定您自己的
python3 scripts/generate_mondo_enhanced.py "爵士音乐节" 活动 --style jules-cheret --colors "鲜艳黄色、深蓝色、红色"
```

## 与Claude的交互式使用

当通过Claude Code使用这项技能时，我可以指导您交互式地：

**我会问您简单的问题，例如：**
1. "您的主题是什么？"（电影/书籍/专辑名称）
2. "哪种风格感觉合适？"（显示3-4个选项和预览）
3. "有任何颜色偏好吗？"（或让AI建议）
4. "想要查看比较吗？"（生成3个版本）

这使得即使您不熟悉Mondo美学也很容易！

---

## 直接图像生成

这项技能可以使用捆绑的脚本直接生成图像：

### 增强版本（推荐）

**完整功能集：** AI增强、比较、图像到图像、20位艺术家

```bash
python3 scripts/generate_mondo_enhanced.py "主题" "类型" [选项]
```

**增强参数：**
- `主题`：要设计的内容
- `类型`：设计类型 - "电影"、"书籍"、"专辑"、"活动"
- `--style`：艺术家风格（20个选项，见--list-styles）
- `--ai-enhance`：让AI优化提示（尊重您的意图）
- `--compare`：生成3风格比较（例如，"saul-bass,olly-moss,jock"）
- `--input`：用于图像到图像转换的输入图像
- `--colors`：颜色偏好（例如，"橙色、蓝绿色、黑色"）
- `--aspect-ratio`：宽高比（默认：9:16）
- `--output`：自定义输出路径
- `--no-generate`：仅显示提示

**增强示例：**

AI优化生成：
```bash
python3 scripts/generate_mondo_enhanced.py "银翼杀手" 电影 --ai-enhance
```

3风格比较：
```bash
python3 scripts/generate_mondo_enhanced.py "阿基拉" 电影 --compare kilian-eng,saul-bass,jock
```

图像到图像与特定艺术家：
```bash
python3 scripts/generate_mondo_enhanced.py "赛博朋克黑色电影" 电影 --input poster.jpg --style saul-bass
```

带颜色偏好：
```bash
python3 scripts/generate_mondo_enhanced.py "爵士之夜" 活动 --style milton-glaser --colors "超现实橙色、紫色、黄色"
```

列出所有20位艺术家风格：
```bash
python3 scripts/generate_mondo_enhanced.py --list-styles
```

### 标准版本（简单快速）

**基本用法用于快速生成：**

```bash
python3 scripts/generate_mondo.py "主题" "类型" [选项]
```

**参数：**
- `主题`：要设计的内容（例如，"神经漫游者赛博朋克小说"，"爵士音乐节海报"）
- `类型`：设计类型 - "电影"、"书籍"、"专辑"、"活动"
- `--aspect-ratio` / `--ratio`：宽高比（默认：**9:16** 用于移动/社交媒体）
  - 常见比例：9:16（垂直移动），16:9（水平），1:1（方形），2:3，3:2，4:5
- `--style`：艺术家风格 - "olly-moss"、"tyler-stout"、"极简"、"氛围"（默认：自动）
- `--output`：自定义输出路径（默认：outputs/）
- `--no-generate`：仅创建提示而不生成图像

**为什么默认9:16？**
- 优化用于现代移动设备和社会媒体（Instagram故事、TikTok、Reels）
- 垂直构图更适合海报和书籍封面
- 最大化智能手机上的屏幕空间

**示例：**

电影海报（默认9:16垂直）：
```bash
python3 scripts/generate_mondo.py "阿基拉赛博朋克动画" "电影"
```

书籍封面极简风格（9:16）：
```bash
python3 scripts/generate_mondo.py "1984反乌托邦小说" "书籍" --style 极简
```

专辑封面（方形比例）：
```bash
python3 scripts/generate_mondo.py "平克·弗洛伊德 The Wall 前卫摇滚" "专辑" --aspect-ratio 1:1
```

水平影院海报：
```bash
python3 scripts/generate_mondo.py "西部电影塞尔乔·莱昂" "电影" --aspect-ratio 16:9
```

自定义比例用于印刷：
```bash
python3 scripts/generate_mondo.py "爵士音乐节海报" "活动" --ratio 2:3 --style 氛围
```

仅生成提示（不生成图像）：
```bash
python3 scripts/generate_mondo.py "沙丘科幻史诗" "电影" --no-generate
```

### 手动生成

如果您更喜欢手动生成提示并使用其他图像生成工具：

1. 使用这项技能生成Mondo风格提示
2. 将提示传递给：
   - `/generate-image` - AI Gateway API（推荐）
   - `/ai-image-generation` - FLUX、Gemini和其他模型
   - `/qiaomu-image-generator` - 用于文章/内容插图

**推荐设置：**
- 模型：`google/gemini-3.1-flash-image-preview`（最佳质量/速度平衡）
- 分辨率：2K或更高用于印刷质量
- 格式：带透明度支持的PNG
