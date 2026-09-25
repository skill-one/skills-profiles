# Shadertoy着色器开发

## 概述

Shadertoy是一个用于创建和分享在浏览器中通过WebGL运行的GLSL片段着色器的平台。这项技能为编写着色器提供了全面的指导，包括GLSL ES语法、常见模式、数学技术以及实时程序图形的最佳实践。

## 何时使用此技能

在以下情况下激活此技能：
- 编写或编辑`.glsl`着色器文件
- 创建程序图形、生成艺术或视觉特效
- 使用Shadertoy.com项目或WebGL片段着色器
- 实现光线步进、距离场或程序纹理
- 调试着色器代码或优化着色器性能
- 需要GLSL ES语法参考或Shadertoy输入变量

## 核心概念

### 着色器入口点

每个Shadertoy着色器都实现`mainImage`函数：

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    // fragCoord: 像素坐标（0到iResolution.xy）
    // fragColor: 输出颜色（RGBA，通常alpha = 1.0）

    vec2 uv = fragCoord / iResolution.xy;
    fragColor = vec4(uv, 0.0, 1.0);
}
```

### Shadertoy内置输入

着色器中始终可用的：

| 类型 | 名称 | 描述 |
|------|------|-------------|
| `vec3` | `iResolution` | 视口分辨率（x, y, 纵横比） |
| `float` | `iTime` | 当前时间（秒）（主要动画驱动器） |
| `float` | `iTimeDelta` | 渲染一帧的时间 |
| `int` | `iFrame` | 当前帧编号 |
| `vec4` | `iMouse` | 鼠标：xy = 当前位置，zw = 点击位置 |
| `sampler2D` | `iChannel0`-`iChannel3` | 输入纹理/缓冲区 |
| `vec3` | `iChannelResolution[4]` | 每个输入通道的分辨率 |
| `vec4` | `iDate` | 年、月、日、时间（秒）（.xyzw） |

### 坐标系设置

标准化坐标的标准模式：

```glsl
// 纵横比校正的UV以原点为中心（-1到1，保持纵横比）
vec2 uv = (fragCoord.xy - 0.5 * iResolution.xy) / min(iResolution.y, iResolution.x);

// 简洁形式：
vec2 uv = (fragCoord * 2.0 - iResolution.xy) / min(iResolution.x, iResolution.y);

// 简单标准化（0到1）
vec2 uv = fragCoord / iResolution.xy;
```

## 常见着色器模式

### 1. 程序化调色板

使用Inigo Quilez的余弦调色板创建平滑的颜色渐变：

```glsl
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}

// 示例用法：
vec3 col = palette(
    t,
    vec3(0.5, 0.5, 0.5),    // 基础
    vec3(0.5, 0.5, 0.5),    // 幅度
    vec3(1.0, 1.0, 0.5),    // 频率
    vec3(0.8, 0.90, 0.30)   // 相位
);
```

### 2. 哈希函数（伪随机）

用于噪声和随机性的简单2D哈希：

```glsl
float hash21(vec2 p) {
    p = fract(p * vec2(234.34, 435.345));
    p += dot(p, p + 34.23);
    return fract(p.x * p.y);
}
```

### 3. 光线步进

通过球面追踪进行3D渲染的标准模式：

```glsl
// 距离场函数
float map(vec3 p) {
    return length(p) - 1.0;  // 原点的球体，半径1
}

// 法线计算
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

// 光线步进循环
vec3 render(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < 100; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if (d < 0.001) {
            // 碰撞 - 计算光照
            vec3 n = calcNormal(p);
            return n * 0.5 + 0.5;  // 法线可视化
        }
        if (t > 10.0) break;
        t += d * 0.5;  // 步进（0.5因子用于安全）
    }
    return vec3(0.0);  // 未命中
}
```

### 4. 旋转

2D旋转：
```glsl
mat2 rot2d(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}
// 使用：p.xy *= rot2d(iTime);
```

3D轴角旋转（原地修改）：
```glsl
void rot(inout vec3 p, vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle), c = cos(angle), oc = 1.0 - c;
    mat3 m = mat3(
        oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,
        oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,
        oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c
    );
    p = m * p;
}
```

### 5. 域重复和折叠

创建分形状结构：

```glsl
vec3 foldRotate(vec3 p, float timeOffset) {
    for (int i = 0; i < 5; i++) {
        p = abs(p);  // 镜像折叠
        rot(p, vec3(0.707, 0.707, 0.0), 0.785);
        p -= 0.5;    // 平移
    }
    return p;
}
```

### 6. 后处理

暗角：
```glsl
float vignette(vec2 uv) {
    uv *= 1.0 - uv.yx;
    return pow(uv.x * uv.y * 15.0, 0.25);
}
```

胶片颗粒/抖动（减少色带）：
```glsl
float dither = hash21(fragCoord + iTime) * 0.001;
finalCol += dither;
```

伽马校正：
```glsl
finalCol = pow(finalCol, vec3(0.45));  // ~1/2.2
```

## 多通道渲染

对于需要时间反馈或多个渲染阶段复杂效果：

### 缓冲区A（计算）：
```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    // 生成或计算值
    fragColor = vec4(computedColor, 1.0);
}
```

### 缓冲区B（反馈/混合）：
```glsl
#define BUFFER_A iChannel0
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    vec4 current = texture(BUFFER_A, uv);
    vec4 previous = texture(iChannel1, uv);  // 自引用
    fragColor = mix(previous, current, 0.1);  // 时间混合
}
```

### 主（最终输出）：
```glsl
#define BUFFER_B iChannel1
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    fragColor = texture(BUFFER_B, uv);
}
```

## 关键GLSL ES规则

**始终遵循这些规则以避免编译错误：**

1. **无`f`后缀**：使用`1.0`，不要`1.0f`
2. **无`saturate()`**：使用`clamp(x, 0.0, 1.0)`代替
3. **保护pow/sqrt**：包装参数：`pow(max(x, 0.0), p)`，`sqrt(abs(x))`
4. **避免除以零**：检查分母或添加epsilon
5. **初始化变量**：不要假设默认值
6. **避免命名冲突**：不要将函数命名为变量
7. **无交互命令**：避免`find`，`grep` - 使用Glob/Grep工具

## 工作流程指南

### 创建新着色器

1. **设置坐标系** - 选择适当的UV标准化
2. **定义核心效果** - 实现主要视觉算法
3. **添加动画** - 使用`iTime`进行时间变化
4. **应用调色板** - 使用余弦调色板或自定义方案
5. **添加后处理** - 暗角、抖动、伽马校正
6. **优化** - 减少迭代次数、使用提前退出、最小化分支

### 常见任务

**可视化复数：**
- 使用`references/common-patterns.md`中的复数数学函数
- 使用`cx_log()`，`cx_pow()`或多项式评估绘图
- 通过调色板将复数结果映射到颜色

**光线步进3D场景：**
- 在`map()`函数中定义距离场
- 设置相机（光线原点`ro`，光线方向`rd`）
- 使用标准循环模式步进
- 使用四面体方法计算法线
- 应用光照和材质属性

**创建噪声/有机效果：**
- 使用`hash21()`获取随机值
- 实现`fbm()`（分形布朗运动）以实现自然变化
- 结合`sin()`/`cos()`创建结构化模式
- 应用域扭曲以实现有机变形

**多层合成：**
- 使用不同参数渲染多个通道
- 使用`mix()`或自定义混合模式混合层
- 通过比较层差异添加干涉图案
- 使用`smoothstep()`进行软过渡

### 调试策略

**可视化中间值：**
```glsl
fragColor = vec4(vec3(distanceField), 1.0);  // 显示距离
fragColor = vec4(normal * 0.5 + 0.5, 1.0);   // 显示法线
fragColor = vec4(fract(uv), 0.0, 1.0);       // 显示UV平铺
```

**逐步简化：**
- 注除后处理
- 减少迭代次数
- 用简单占位符替换复杂函数
- 逐步检查坐标变换

**检查NaN/Inf：**
- 添加保护：`if (isnan(value) || isinf(value)) return vec3(1.0, 0.0, 0.0);`
- 验证除法和开方

## 性能优化

1. **固定迭代次数** - 避免动态循环
2. **提前退出条件** - 达到阈值时退出
3. **步进乘数调整** - 平衡质量与速度（0.5到1.0）
4. **最小化纹理读取** - 缓存重复查找
5. **避免条件语句** - 使用`mix()`，`step()`，`smoothstep()`代替`if`
6. **减少精度** - 在适当位置使用`mediump`或`lowp`

## 命名规范

基于创意工作中的观察模式：

- **诗意/启发式命名** - "alien-water"，"heavenly-wisp"，"comprehension"
- **技术描述** - "complex-plot"，"noise-circuits"，"ray-marching-demo"
- **复合短语** - "coming-apart-at-the-seams"，"form-without-form"
- **小写带连字符** - `my-shader-name.glsl`

## 翻译和分支

在分支或混合着色器时：

```glsl
// "Original Name"的分支，作者名。https://shadertoy.com/view/XxXxXx
// 日期：YYYY-MM-DD
// 许可证：知识共享（CC BY-NC-SA 4.0）[或其他]
```

## 资源

### references/glsl-reference.md
完整的GLSL ES语法参考，包括：
- 内置函数（三角函数、数学、向量、矩阵、纹理）
- Shadertoy输入变量规范
- 类型转换和混用
- 常见陷阱和修正

搜索：`Read /references/glsl-reference.md`获取完整的语言参考。

### references/common-patterns.md
全面的模式库，包括：
- 复数数学（cx_mul，cx_div，cx_sin，cx_cos，cx_log，cx_pow）
- 调色板函数（余弦调色板，多层调色板）
- 哈希函数（hash21，PCG哈希）
- 光线步进模板（渲染循环，法线计算）
- 3D变换（旋转，域折叠）
- 距离场（球体，立方体，八面体）
- 噪声函数（单纯形，FBM）
- 后处理（暗角，模糊，胶片颗粒，伽马）
- 混合模式（软光，硬光，鲜艳光）
- 多通道渲染模式

搜索：`Grep "pattern" references/common-patterns.md`查找特定技术。

### references/example-compact-shader.glsl
参考实现，展示：
- 紧凑、算法化的着色器编码风格
- 最小代码中的高效光线步进
- 高级矩阵运算和变换
- 知识共享许可的示例

## 快速参考

```glsl
#define PI 3.1415926535897932384626433832795

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // 1. 标准化坐标
    vec2 uv = (fragCoord * 2.0 - iResolution.xy) / min(iResolution.x, iResolution.y);

    // 2. 计算效果
    float d = length(uv) - 0.5;  // 圆形距离场
    vec3 col = vec3(smoothstep(0.01, 0.0, d));  // 锐边

    // 3. 使用时间动画
    col *= 0.5 + 0.5 * sin(iTime + uv.xyx * 3.0);

    // 4. 应用调色板
    col = palette(col.x, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0));

    // 5. 后处理
    col = pow(col, vec3(0.45));  // 伽马
    col *= vignette(fragCoord / iResolution.xy);

    // 6. 输出
    fragColor = vec4(col, 1.0);
}
```

## 集合中常见的着色器类型

1. **数学可视化** - 复数绘图，函数图
2. **光线步进3D** - 距离场渲染，折叠几何体
3. **程序纹理** - 噪声图案，有机效果
4. **多通道效果** - 时间反馈，缓冲区合成
5. **粒子系统** - 基于点的模拟
6. **2D图案** - 几何图案，万花筒，干涉效果

## 创意编码技巧

- **从简单开始** - 获取基本结构工作，然后迭代
- **创意使用时间** - `sin(iTime)`，`mod(iTime, period)`，`smoothstep()`过渡
- **层叠效果** - 结合多种技术以增加丰富度
- **拥抱意外** - 错误往往导致有趣的视觉效果
- **学习参考** - 从现有着色器学习，理解技术
- **优化稍后** - 优先考虑视觉质量，然后性能
