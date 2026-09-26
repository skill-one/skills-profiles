# Slug 字体渲染算法

> 技能来源：[ara.so](https://ara.so) — 2026每日技能集合。

Slug 是一种Slug字体渲染算法的参考实现——这是一种用于在任意比例下以高质量抗锯齿效果渲染矢量字体和字形的GPU加速技术。它通过将字形轮廓编码为二次贝塞尔曲线和线段的列表，然后在片段着色器中直接解析覆盖范围，而无需预渲染纹理来实现。

**论文：** [JCGT 2017 — Slug算法](https://jcgt.org/published/0006/02/02/)  
**博客（更新）：** [A Decade of Slug](https://terathon.com/blog/decade-slug.html)  
**许可证：** MIT — 专利已捐赠至公共领域。如分发需注明出处。

---

## Slug的功能

- 完全在GPU上渲染TrueType/OpenType字形
- 无需纹理集或预渲染
- 可在任何分辨率下无损缩放
- 使用贝塞尔数学按片段计算抗锯齿覆盖
- 适用于任何支持可编程着色器的渲染API（D3D11/12、Vulkan、Metal通过转换）

---

## 仓库结构

```
Slug/
├── slug.hlsl          # 核心片段着色器 — 覆盖计算
├── band.hlsl          # 基于带的优化用于字形渲染
├── curve.hlsl         # 二次贝塞尔和线段评估
├── README.md
```

---

## 安装 / 集成

Slug 是一个**参考实现**——你需要将HLSL着色器集成到自己的渲染管线中。

### 第一步：克隆仓库

```bash
git clone https://github.com/EricLengyel/Slug.git
```

### 第二步：包含着色器

将`.hlsl`文件复制到你的着色器目录，并在你的管线中包含它们：

```hlsl
#include "slug.hlsl"
#include "curve.hlsl"
```

### 第三步：在CPU上准备字形数据

你必须将字体轮廓（TrueType/OTF）预处理为Slug的曲线缓冲区格式：
- 将字形轮廓分解为二次贝塞尔段和线段
- 将曲线数据上传到GPU缓冲区（结构化缓冲区或纹理缓冲区）
- 预计算每个字形的"带"元数据用于带优化

---

## 核心概念

### 字形坐标系

- 字形轮廓位于**字体单位**中（通常为0–2048或0–1000每em）
- 片段着色器通过插值的顶点属性接收字形空间中的位置
- 覆盖通过计算Y方向上的符号曲线交叉次数（ winding number）来计算

### 曲线数据格式

GPU缓冲区中的每个曲线条目存储：

```hlsl
// 线段：p0, p1
// 二次贝塞尔：p0, p1（控制点），p2

struct CurveRecord
{
    float2 p0;   // 起始点
    float2 p1;   // 控制点（或线的终点）
    float2 p2;   // 终点（线段不使用 — 通过类型标记）
    // 类型/标记单独编码或在填充中
};
```

### 带优化

字形边界框被划分为水平**带**。每个带只存储与其相交的曲线，将每个片段的工作量从O（所有曲线）减少到O（局部曲线）。

---

## 关键着色器代码和模式

### 片段着色器入口点（概念性集成）

```hlsl
// 来自顶点着色器的输入
struct PS_Input
{
    float4 position  : SV_Position;
    float2 glyphCoord : TEXCOORD0;  // 字形/字体单位中的位置
    // 带索引或预计算带数据
    nointerpolation uint bandOffset : TEXCOORD1;
    nointerpolation uint curveCount : TEXCOORD2;
};

// 字形曲线数据缓冲区
StructuredBuffer<float4> CurveBuffer : register(t0);

float4 PS_Slug(PS_Input input) : SV_Target
{
    float coverage = ComputeGlyphCoverage(
        input.glyphCoord,
        CurveBuffer,
        input.bandOffset,
        input.curveCount
    );

    // 预乘alpha输出
    float4 color = float4(textColor.rgb * coverage, coverage);
    return color;
}
```

### 二次贝塞尔覆盖计算

算法的核心——从二次贝塞尔计算符号覆盖：

```hlsl
// 判断二次贝塞尔在点p处是否对覆盖有贡献
// p0: 起始点, p1: 控制点, p2: 终点
// 返回符号覆盖贡献
float QuadraticBezierCoverage(float2 p, float2 p0, float2 p1, float2 p2)
{
    // 转换到规范空间
    float2 a = p1 - p0;
    float2 b = p0 - 2.0 * p1 + p2;

    // 找到贝塞尔Y等于p.y的t值
    float2 delta = p - p0;
    
    float A = b.y;
    float B = a.y;
    float C = p0.y - p.y;

    float coverage = 0.0;

    if (abs(A) > 1e-6)
    {
        float disc = B * B - A * C;
        if (disc >= 0.0)
        {
            float sqrtDisc = sqrt(disc);
            float t0 = (-B - sqrtDisc) / A;
            float t1 = (-B + sqrtDisc) / A;

            // 对于每个有效的t在[0,1]中，计算x并检查winding
            if (t0 >= 0.0 && t0 <= 1.0)
            {
                float x = (A * t0 + 2.0 * B) * t0 + p0.x + delta.x;
                // ... 累加符号覆盖
            }
            if (t1 >= 0.0 && t1 <= 1.0)
            {
                float x = (A * t1 + 2.0 * B) * t1 + p0.x + delta.x;
                // ... 累加符号覆盖
            }
        }
    }
    else
    {
        // 退化到线性情况
        float t = -C / (2.0 * B);
        if (t >= 0.0 && t <= 1.0)
        {
            float x = 2.0 * a.x * t + p0.x;
            // ... 累加符号覆盖
        }
    }

    return coverage;
}
```

### 线段覆盖

```hlsl
// 线段从p0到p1的符号覆盖贡献
float LineCoverage(float2 p, float2 p0, float2 p1)
{
    // 检查Y范围
    float minY = min(p0.y, p1.y);
    float maxY = max(p0.y, p1.y);

    if (p.y < minY || p.y >= maxY)
        return 0.0;

    // 在p.y处插值X
    float t = (p.y - p0.y) / (p1.y - p0.y);
    float x = lerp(p0.x, p1.x, t);

    // winding: 如果p在左侧（内部），则为+1；如果右侧，则为-1
    float dir = (p1.y > p0.y) ? 1.0 : -1.0;
    return (p.x <= x) ? dir : 0.0;
}
```

### 使用部分覆盖进行抗锯齿

为了平滑边缘，使用到最近曲线的距离进行亚像素抗锯齿：

```hlsl
// 使用部分像素覆盖计算抗锯齿覆盖
// windingNumber: 覆盖通道的整数winding
// distToEdge: 到最近曲线的符号距离（以像素为单位）
float AntiAliasedCoverage(int windingNumber, float distToEdge)
{
    // 非零winding规则
    bool inside = (windingNumber != 0);
    
    // 在边缘处使用clamp平滑过渡
    float edgeCoverage = clamp(distToEdge + 0.5, 0.0, 1.0);
    
    return inside ? edgeCoverage : (1.0 - edgeCoverage);
}
```

---

## 顶点着色器模式

```hlsl
struct VS_Input
{
    float2 position   : POSITION;     // 字形四边形角在屏幕/世界空间
    float2 glyphCoord : TEXCOORD0;    // 对应的字形空间坐标
    uint   bandOffset : TEXCOORD1;    // 此字形的曲线缓冲区偏移
    uint   curveCount : TEXCOORD2;    // 带中的曲线数量
};

struct VS_Output
{
    float4 position   : SV_Position;
    float2 glyphCoord : TEXCOORD0;
    nointerpolation uint bandOffset : TEXCOORD1;
    nointerpolation uint curveCount : TEXCOORD2;
};

VS_Output VS_Slug(VS_Input input)
{
    VS_Output output;
    output.position   = mul(float4(input.position, 0.0, 1.0), WorldViewProjection);
    output.glyphCoord = input.glyphCoord;
    output.bandOffset = input.bandOffset;
    output.curveCount = input.curveCount;
    return output;
}
```

---

## CPU端数据准备（伪代码）

```cpp
// 1. 加载字体文件并提取字形轮廓
FontOutline outline = LoadGlyphOutline(font, glyphIndex);

// 2. 分解为二次贝塞尔（TrueType已经是二次的）
//    OTF立方曲线必须被近似/分割为二次曲线
std::vector<SlugCurve> curves = DecomposeToQuadratics(outline);

// 3. 计算带
float bandHeight = outline.bounds.height / NUM_BANDS;
std::vector<BandData> bands = ComputeBands(curves, NUM_BANDS, bandHeight);

// 4. 上传到GPU
UploadStructuredBuffer(curveBuffer, curves.data(), curves.size());
UploadStructuredBuffer(bandBuffer, bands.data(), bands.size());

// 5. 每个字形实例：存储每个带的bandOffset和curveCount
//    在顶点数据中，以便片段着色器可以直接索引
```

---

## 渲染状态要求

```hlsl
// 混合状态：预乘alpha
BlendState SlugBlend
{
    BlendEnable    = TRUE;
    SrcBlend       = ONE;           // 预乘
    DestBlend      = INV_SRC_ALPHA;
    BlendOp        = ADD;
    SrcBlendAlpha  = ONE;
    DestBlendAlpha = INV_SRC_ALPHA;
    BlendOpAlpha   = ADD;
};

// 深度：通常禁用写入用于文本叠加
DepthStencilState SlugDepth
{
    DepthEnable    = FALSE;
    DepthWriteMask = ZERO;
};

// 光栅化器：无背面剔除（字形四边形是2D）
RasterizerState SlugRaster
{
    CullMode = NONE;
    FillMode = SOLID;
};
```

---

## 常见模式

### 渲染字符串

```cpp
// 对于字符串中的每个字形：
for (auto& glyph : string.glyphs)
{
    // 发射一个覆盖字形边界框的四边形（2个三角形）
    // 每个顶点携带：
    //   - 屏幕位置
    //   - 字形空间坐标（相同的角在字体单位中）
    //   - bandOffset + curveCount供片段着色器使用

    float2 min = glyph.screenMin;
    float2 max = glyph.screenMax;
    float2 glyphMin = glyph.fontMin;
    float2 glyphMax = glyph.fontMax;

    EmitQuad(min, max, glyphMin, glyphMax,
             glyph.bandOffset, glyph.curveCount);
}
```

### 缩放文本

缩放完全在CPU端处理，通过变换屏幕空间四边形。字形空间坐标保持不变——片段着色器始终在字体单位中工作。

```cpp
float scale = desiredPixelSize / font.unitsPerEm;
float2 screenMin = origin + glyph.fontMin * scale;
float2 screenMax = origin + glyph.fontMax * scale;
```

---

## 故障排除

| 问题 | 原因 | 解决方法 |
|---|---|---|
| 字形看起来空心/反转 | 环绕顺序相反 | 检查轮廓方向；TrueType使用顺时针方向为外轮廓 |
| 锯齿边缘 | 未应用抗锯齿 | 确保计算了距离到边缘并用于最终覆盖 |
| 性能差 | 带优化未激活 | 验证每个片段的曲线计数较小（< ~20）；增加带数量 |
| 立方曲线未渲染 | OTF立方贝塞尔不支持原生 | 在CPU上将立方曲线分割为二次近似 |
| 字形重叠处出现伪影 | 曲线未剪裁到带 | 上传前将曲线Y范围剪裁到带边界 |
| 黑色框而不是字形 | 混合状态错误 | 使用预乘alpha混合（ONE, INV_SRC_ALPHA） |
| 缺失字形 | 带偏移不正确 | 验证bandOffset索引与缓冲区布局对齐 |

---

## 致谢与归属

根据许可证：如果你分发使用此代码的软件，**你必须注明出处**给Eric Lengyel和Slug算法。

建议的归属：
> 字体渲染使用Eric Lengyel（https://jcgt.org/published/0006/02/02/）的Slug算法

---

## 参考文献

- [Slug算法论文（JCGT 2017）](https://jcgt.org/published/0006/02/02/)
- [A Decade of Slug — 博客文章](https://terathon.com/blog/decade-slug.html)
- [GitHub仓库](https://github.com/EricLengyel/Slug)
