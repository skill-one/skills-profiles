# image-ecommerce

在 Starchild 上使用此技能处理所有**电子商务产品摄影请求**。

涵盖：白色背景主图、生活方式产品场景、平面布置、细节/微距特写、包装/开箱照片、组合/系列展示、比例参考图像、季节性主题（春/夏/秋/冬）、360度视图、对比布局、信息图表风格的功能标注、以及针对 Amazon、Shopify、Taobao、Instagram、小红书、Etsy、eBay 优化的平台图像。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

**何时使用 image-ecommerce 而不是其他图像技能**：
- **image-ecommerce** → 用户需要电子商务产品照片、目录或营销
- **image-edit** → 用户需要编辑或转换现有图像（非产品特定）
- **image-portrait** → 用户需要保留其面部/身份肖像
- **image-create** → 用户需要从文本创建内容（非产品摄影）
- **image-tryon** → 用户需要在人身上试穿服装/配饰

---

## 1. 快速入门 — 单个产品照片（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 直接将其粘贴到 bash 命令中会导致 `语法错误 near unexpected token 'open'`。此外，`python3 -c` 中的 `exec(open(...))` 会因脚本使用 `__file__` 进行路径解析而失败为 `NameError: __file__`。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 并配合 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-ecommerce")
> from exports import product_photo
> result = product_photo(
>     product_path="uploads/product.jpg",
>     style="hero",
>     background="white",
> )
> print(result)
> EOF
> ```
>
> 她源文档 (`<<'EOF'`) 保留了所有引号和换行符 — 无需转义。

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/product.jpg",
    style="hero",
    background="white",
)
# result -> {"success": True, "images": [{"local_path": "output/images/..."}], ...}
```

脚本读取本地文件，将其 base64 编码，并作为数据 URI 发送到 fal.ai — 无需手动发布 URL。

## 2. 快速入门 — 公共 URL

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_url="https://example.com/product.jpg",
    style="lifestyle",
    background="natural",
)
```

## 3. 快速入门 — 文本到图像（无产品照片）

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    prompt="高端无线蓝牙耳机，磨砂黑表面，头戴式设计",
    style="hero",
    background="white",
)
```

当未提供 `product_path` 或 `product_url` 时，脚本使用文本到图像端点（无 `/edit` 后缀）。此模式下需要描述产品的 `prompt`。

## 4. 快速入门 — 平台优化

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/product.jpg",
    platform="amazon",
)
# 自动应用：style=hero, background=white, aspect_ratio=1:1
```

## 5. 快速入门 — 完整产品图像集

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo_set(
    product_path="uploads/product.jpg",
    prompt="高端皮革钱包",
    platform="amazon",
)
# 生成 7 张图像：hero, lifestyle, detail, scale, 替代角度, 包装, 平铺
```

### 将结果交付给用户 — 重要提示

**永远不要直接将原始 fal.media URL 交给用户。** fal 使用限制性 CSP 头部服务文件。唯一可靠的交付路径是**已下载的本地文件**：

1. 使用每个图像的 `local_path`（例如 `output/images/xxx.png`）— 脚本在成功时始终会下载。
2. 告知用户文件保存在 `output/images/` 中，可在工作区文件面板中查看。
3. 在 Web 渠道中，内嵌以供用户在聊天中预览：
   ```markdown
   ![product](output/images/<filename>.png)
   ```
4. 在 Telegram / 微信：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 6. 参数 — `product_photo()`

| 参数 | 必填 | 默认 | 描述 |
|-------|------|------|------|
| `product_path` | 否 | — | 产品图像的本地工作区文件路径 |
| `product_url` | 否 | — | 产品图像的公共 HTTPS URL |
| `prompt` | 否 | — | 描述产品或所需照片的自定义提示 |
| `style` | 否 | `"hero"` | 摄影风格预设（见 §7） |
| `background` | 否 | `"white"` | 背景类型（见 §8） |
| `model` | 否 | `"nanopro"` | 模型：`"nanopro"`（快速 ~25 秒）或 `"gpt"`（最佳质量 ~150 秒） |
| `count` | 否 | `1` | 生成图像的数量（1–8） |
| `aspect_ratio` | 否 | `"1:1"` | 输出比例：`1:1`，`3:4`，`4:3`，`9:16`，`16:9` |
| `platform` | 否 | — | 平台预设：`amazon`，`shopify`，`taobao`，`instagram`，`小红书`，`etsy`，`eBay` |

**图像输入规则**：
- 提供 `product_path` 或 `product_url` 以进行编辑模式（转换现有产品照片）。
- 如果两者都提供，`product_path` 优先。
- 两者都省略则进行纯文本到图像生成（需要 `prompt`）。

**提示优先级**：`prompt + style/background`（增强）> `style + background` 模板。

**平台预设**：当 `platform` 设置时，它会覆盖默认的 `style`、`background` 和 `aspect_ratio`，使用平台优化的值 — 除非您明确设置它们。

---

## 7. 摄影风格

### 核心产品照片

| 风格 | 关键 | 最适合 |
|------|------|------|
| 主图 | `hero` | 主要列表图像，杂志广告，主要产品展示 |
| 生活方式 | `lifestyle` | 产品在使用中，编辑，社交媒体 |
| 平铺 | `flat_lay` | Instagram，自上而下布置，目录 |
| 细节特写 | `detail` | 材质质量，纹理，工艺 |
| 包装 | `packaging` | 开箱体验，品牌包装 |
| 组合/系列 | `group` | 多个产品，变体，组合 |
| 比例参考 | `scale` | 尺寸对比，产品在手 |

### 营销 & 信息

| 风格 | 关键 | 最适合 |
|------|------|------|
| 360° 视图 | `360_view` | 多角度展示，转盘展示 |
| 对比 | `comparison` | 并列，前后，功能高亮 |
| 信息图表 | `infographic` | 功能标注，规格，尺寸 |

### 季节性活动

| 风格 | 关键 | 最适合 |
|------|------|------|
| 春季 | `seasonal_spring` | 樱花，新鲜绿色，淡雅 |
| 夏季 | `seasonal_summer` | 海滩，阳光，热带，度假 |
| 秋季 | `seasonal_autumn` | 落叶，金色调，丰收 |
| 冬季 | `seasonal_winter` | 雪，节日，节日，温馨 |

---

## 8. 背景类型

| 背景 | 关键 | 最适合 |
|------|------|------|
| 纯白色 | `white` | Amazon，电子商务标准，市场列表 |
| 渐变 | `gradient` | 主图，高级感，现代 |
| 工作室 | `studio` | 专业目录，受控照明 |
| 自然 | `natural` | 户外产品，有机品牌 |
| 生活方式 | `lifestyle` | 家庭/办公环境，使用场景 |
| 彩色 | `colored` | 品牌匹配，活力营销 |
| 纹理 | `textured` | 高端产品，大理石/木材表面 |
| 透明 | `transparent` | 产品抠图，用于设计使用的 PNG |

---

## 9. 平台预设

| 平台 | 纵横比 | 背景 | 风格 | 关键要求 |
|------|--------|------|------|----------|
| Amazon | 1:1 | white | hero | 纯白色背景 (RGB 255,255,255)，产品填充 85%+，无道具/文本/水印，最小 1000px (1600px+ 用于缩放) |
| Shopify | 1:1 | white | hero | 正方形格式，一致的目录风格，推荐 2048x2048 |
| Taobao | 1:1 | white | hero | 最小 800x800，白色背景为主图像 |
| Instagram | 1:1 | lifestyle | lifestyle | 1080x1080 信息流，生活方式背景，视觉吸引 |
| 小红书 | 3:4 | lifestyle | flat_lay | 1080x1440 垂直，美观平铺，文本覆盖空间 |
| Etsy | 4:3 | natural | lifestyle | 手工/匠人感，自然背景 |
| eBay | 1:1 | white | hero | 白色背景，清晰产品视图，最小 1600px 用于缩放 |

---

## 10. 模型选择指南

| 模型 | 关键 | 速度 | 质量 | 最适合 |
|------|------|------|------|------|
| NanoPro | `nanopro` | ~25s | 良好 | 默认所有请求。快速迭代。 |
| GPT Image 2 | `gpt` | ~150s | 最佳 | 用户明确要求“最高质量”或“最佳质量”。复杂场景。 |

**决策规则**：
1. **默认**：除非用户明确要求更高质量，否则始终使用 `nanopro`。
2. **使用 `gpt` 当**：用户说“最高质量”，“最佳质量”，“高端”，或场景非常复杂且有许多特定细节。
3. **使用 `nanopro` 当**：用户需要快速结果，正在迭代风格，或生成多个图像。

```python
# 默认（快速）
result = product_photo(product_path="product.jpg", style="hero")

# 高质量（用户请求）
result = product_photo(product_path="product.jpg", style="hero", model="gpt")
```

---

## 11. 意图识别指南

使用此表格将用户请求映射到正确的风格 + 背景：

### 产品列表图像

| 用户说 | 风格 | 背景 | 备注 |
|------|------|------|------|
| "产品照片", "列表图像", "主图" | `hero` | `white` | 默认电子商务 |
| "Amazon 列表", "亚马逊主图" | `hero` | `white` | 使用 `platform="amazon"` |
| "Shopify 产品", "独立站产品图" | `hero` | `white` | 使用 `platform="shopify"` |
| "淘宝主图", "天猫主图" | `hero` | `white` | 使用 `platform="taobao"` |
| "白色背景", "白底图" | `hero` | `white` | 标准包装照片 |
| "产品在白色背景上", "纯白背景" | `hero` | `white` | Amazon 风格 |

### 生活方式 & 环境

| 用户说 | 风格 | 背景 | 备注 |
|------|------|------|------|
| "生活方式照片", "场景图" | `lifestyle` | `lifestyle` | 产品在环境中 |
| "产品在使用中", "使用场景" | `lifestyle` | `lifestyle` | 展示产品正在使用 |
| "平铺", "俯拍", "平铺" | `flat_lay` | `textured` | 自上而下布置 |
| "Instagram 产品", "小红书产品" | `flat_lay` | `lifestyle` | 社交媒体优化 |

### 细节 & 技术

| 用户说 | 风格 | 背景 | 备注 |
|------|------|------|------|
| "特写", "细节照片", "细节图" | `detail` | `studio` | 微距/纹理 |
| "包装", "包装图", "开箱" | `packaging` | `studio` | 盒子 + 产品 |
| "尺寸对比", "尺寸对比" | `scale` | `studio` | 带参考物体 |
| "多个产品", "组合图" | `group` | `white` | 系列展示 |
| "360° 视图", "多角度" | `360_view` | `white` | 转盘风格 |
| "对比", "对比图" | `comparison` | `white` | 并列 |
| "信息图表", "功能标注" | `infographic` | `white` | 功能标注 |

### 季节性活动

| 用户说 | 风格 | 背景 | 备注 |
|------|------|------|------|
| "春季活动", "春季" | `seasonal_spring` | auto | 樱花，淡雅 |
| "夏季促销", "夏季" | `seasonal_summer` | auto | 海滩，热带 |
| "秋季/秋天", "秋季" | `seasonal_autumn` | auto | 金色叶子，温暖 |
| "冬季/节日", "冬季", "圣诞" | `seasonal_winter` | auto | 雪，节日 |

### 完整产品图像集

| 用户说 | 功能 | 备注 |
|------|------|------|
| "完整集", "全套产品图", "列表图像" | `product_photo_set()` | 7 张图像涵盖所有角度 |
| "Amazon 列表集", "亚马逊全套" | `product_photo_set(platform="amazon")` | 平台优化的集 |

---

## 12. 按场景使用示例

### Amazon 列表 — 白色背景主图

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/headphones.jpg",
    platform="amazon",
)
```

### 生活方式产品照片

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/coffee_mug.jpg",
    style="lifestyle",
    background="lifestyle",
    prompt="高端咖啡杯在乡村木桌上，旁边是一本书，清晨阳光",
)
```

### 产品细节特写

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/leather_bag.jpg",
    style="detail",
    background="studio",
    prompt="极端特写皮革缝线和纹理",
)
```

### 季节性活动 — 冬季节日

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/candle.jpg",
    style="seasonal_winter",
    prompt="高端香薰蜡烛在温馨节日环境中，有松枝和温暖光芒",
)
```

### 文本到图像 — 从描述生成产品

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    prompt="时尚简约智能手表，黑色硅胶带，显示时间的 OLED 显示屏",
    style="hero",
    background="gradient",
    model="gpt",
)
```

### 平铺用于 Instagram / 小红书

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/skincare_set.jpg",
    style="flat_lay",
    background="textured",
    platform="xiaohongshu",
)
```

### 多个图像 — 批量生成

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo(
    product_path="uploads/sneakers.jpg",
    style="hero",
    background="white",
    count=4,
)
# 生成 4 个主图变体
```

### 完整产品图像集

```python
exec(open('skills/image-ecommerce/product_photo.py').read())
result = product_photo_set(
    product_path="uploads/wallet.jpg",
    prompt="高端皮革双折钱包",
    platform="amazon",
)
# result -> {"success": True, "sets": [...], "total_images": 7, ...}
# 生成：hero, lifestyle, detail, scale, 替代角度, 包装, 平铺
```

---

## 13. 提示工程最佳实践

### 产品摄影提示结构

每个有效的产品摄影提示都应包含以下元素：

```
[产品描述], [摄影风格], [照明], [背景/表面], [构图], [质量修饰符]
```

### 关键原则（基于产品摄影、eachlabs-product-visuals、image-create 技能）

1. **产品保留至关重要** — 当编辑现有产品图像时：
   - 始终强调“保持产品完全不变”
   - 保留形状、颜色、品牌和细节
   - 仅更改背景/环境/照明

2. **照明特异性** — 始终指定照明类型：
   - 工作室：`"柔和的扩散工作室照明"`, `"均匀照明，无阴影"`
   - 戏剧性：`"戏剧性边缘照明"`, `"边缘光以获得高端感"`
   - 自然：`"自然窗户光"`, `"黄金时刻温暖光"`
   - 平面：`"平面均匀照明"`（用于电子商务白色背景）

3. **背景精确性** — 模糊的背景会产生不良结果：
   - ❌ "不错的背景"
   - ✅ "纯白色背景 #FFFFFF，无阴影"
   - ✅ "乡村木桌，晨光照射"
   - ✅ "从白色到浅灰色的渐变"

4. **构图规则**（来自产品摄影技能）
   - 主图：产品填充 80% 的画面，轻微 15-30° 角
   - 包装箱（Amazon）：产品居中，填充 85%+
   - 平铺：鸟瞰视图，整齐排列
   - 组合：奇数（3 或 5），三角形构图

5. **阴影类型很重要**：
   - 无阴影：Amazon/电子商务要求
   - 接触阴影：接地但干净
   - 落地阴影：增加深度，专业
   - 反射：科技感，高端

6. **材质和纹理** — 对于细节照片，指定：
   - `"可见皮革纹理和缝线"`
   - `"磨砂金属表面，有微妙反射"`
   - `"柔软织物纹理，可见线迹"`

7. **平台合规性** — 当针对特定平台时：
   - Amazon：纯白色 (RGB 255,255,255)，无道具/文本/水印
   - Instagram：生活方式背景，视觉吸引
   - 小红书：垂直格式，美观，文本覆盖空间

### 示例：构建自定义提示

用户请求："我需要一个用于 Amazon 的皮革钱包主图"

```python
result = product_photo(
    product_path="uploads/wallet.jpg",
    platform="amazon",
    prompt="高端皮革双折钱包，深棕色，轻微角度显示卡槽",
)
```

脚本自动构建：
```
将此产品图像转换为专业的电子商务照片。
保持产品完全不变 — 保留其形状、颜色、细节和品牌。
高端皮革双折钱包，深棕色，轻微角度显示卡槽。
摄影风格：专业产品主图，干净构图，工作室照明...
背景：纯白色背景 #FFFFFF，干净，电子商务标准，无阴影。
```

---

## 14. 电子商务图像集指南

完整的商品列表需要 7-9 张图像。使用 `product_photo_set()` 自动生成，或创建单个照片：

| 位置 | 图像类型 | 风格 | 背景 | 目的 |
|------|---------|------|------|------|
| 1 | Hero / 包装箱 | `hero` | `white` | 主要列表图像 |
| 2 | 生活方式 | `lifestyle` | `lifestyle` | 产品在使用中/环境 |
| 3 | 细节特写 | `detail` | `studio` | 材质质量，工艺 |
| 4 | 比例参考 | `scale` | `studio` | 手中尺寸或与已知物体对比 |
| 5 | 替代角度 | `hero` | `white` | 背面或侧面视图 |
| 6 | 包装 | `packaging` | `studio` | 开箱体验 |
| 7 | 平铺 | `flat_lay` | `textured` | 排列构图 |
| 8 | 信息图表 | `infographic` | `white` | 尺寸，规格，功能 |
| 9 | 季节性 | `seasonal_*` | auto | 活动特定 |

---

## 15. 错误处理

脚本返回结构化结果。始终检查 `success`：

```python
result = product_photo(product_path="uploads/product.jpg")
if result["success"]:
    for img in result["images"]:
        print(f"Saved: {img['local_path']}")
else:
    print(f"Error: {result.get('error')}")
```

常见错误：
- `"文件未找到"` — 检查 `product_path`
- `"不支持的图像格式"` — 使用 JPG、PNG 或 WebP
- `"图像太大"` — 最大 10 MB
- `"需要产品图像或提示"` — 提供 `product_path/product_url` 或 `prompt`
- `"未知风格/背景"` — 检查 §7/§8 中的可用预设
