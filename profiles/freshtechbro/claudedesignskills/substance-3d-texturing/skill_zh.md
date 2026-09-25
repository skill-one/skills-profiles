# Substance 3D 文本uring

## 概述

掌握面向网络和实时引擎的 PBR（基于物理的渲染）纹理创建和导出工作流程。这项技能涵盖了从 Substance 3D Painter 的材质创建到网络优化纹理导出的工作流程，并使用 Python 自动化进行批量处理和与 WebGL/WebGPU 引擎的集成。

**主要功能：**
- PBR 材质创作（金属/粗糙度工作流）
- 网络优化纹理导出（glTF, Three.js, Babylon.js）
- Python API 自动化批量导出
- 实时渲染的纹理压缩和优化

## 核心概念

### PBR 工作流

Substance 3D Painter 使用金属/粗糙度 PBR 工作流，其核心通道如下：

**基础纹理贴图：**
- `baseColor`（Albedo）- RGB 漫反射颜色，不含光照信息
- `normal` - RGB 法线贴图（切线空间）
- `metallic` - 灰度金属度（0 = 介电质，1 = 金属）
- `roughness` - 灰度表面粗糙度（0 = 光滑/光泽，1 = 粗糙/哑光）

**附加贴图：**
- `ambientOcclusion`（AO）- 灰度空腔/遮挡
- `height` - 灰度位移/高度
- `emissive` - RGB 自发光
- `opacity` - 灰度透明度

### 导出预设

Substance 3D Painter 包含针对常见引擎的内置导出预设：
- **PBR Metallic Roughness** - 标准 glTF/WebGL 格式
- **Unity HDRP/URP** - Unity 管道
- **Unreal Engine** - UE4/UE5 格式
- **Arnold (AiStandard)** - 渲染器特定

对于网络引擎，**PBR Metallic Roughness** 是通用标准。

### 纹理分辨率

网络（2 的幂次方）的常见分辨率：
- 512×512 - 低细节道具，移动设备
- 1024×1024 - 标准道具，角色
- 2048×2048 - 英雄资源，特写
- 4096×4096 - 展示质量（谨慎使用）

**网络优化规则：** 从 1024×1024 开始，仅在纹理细节可见时才缩放。

## 常见模式

### 1. 基础网络导出（Three.js/Babylon.js）

手动导出单个纹理集的工作流程：

**步骤：**
1. **文件 → 导出纹理**
2. **选择预设：** "PBR Metallic Roughness"
3. **配置导出：**
   - 输出目录：选择目标文件夹
   - 文件格式：PNG（8 位）用于网络
   - 填充：**"无限"**（防止接缝）
   - 分辨率：1024×1024（根据资源调整）
4. **导出**

**结果文件：**
```
MyAsset_baseColor.png
MyAsset_normal.png
MyAsset_metallicRoughness.png  // 压缩：R=无，G=粗糙度，B=金属度
MyAsset_emissive.png           // 可选
```

**Three.js 使用：**
```javascript
import * as THREE from 'three';

const textureLoader = new THREE.TextureLoader();

const material = new THREE.MeshStandardMaterial({
  map: textureLoader.load('MyAsset_baseColor.png'),
  normalMap: textureLoader.load('MyAsset_normal.png'),
  metalnessMap: textureLoader.load('MyAsset_metallicRoughness.png'),
  roughnessMap: textureLoader.load('MyAsset_metallicRoughness.png'),
  aoMap: textureLoader.load('MyAsset_ambientOcclusion.png'),
});
```

### 2. 使用 Python API 批量导出

自动化多个纹理集的导出：

```python
import substance_painter.export
import substance_painter.resource
import substance_painter.textureset

# 定义导出预设
export_preset = substance_painter.resource.ResourceID(
    context="starter_assets",
    name="PBR Metallic Roughness"
)

# 配置导出为所有纹理集
config = {
    "exportShaderParams": False,
    "exportPath": "C:/export/web_textures",
    "defaultExportPreset": export_preset.url(),
    "exportList": [],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "dithering": True,
            "paddingAlgorithm": "infinite",
            "sizeLog2": 10  // 1024×1024
        }
    }]
}

# 将所有纹理集添加到导出列表
for texture_set in substance_painter.textureset.all_texture_sets():
    config["exportList"].append({
        "rootPath": texture_set.name()
    })

# 执行导出
result = substance_painter.export.export_project_textures(config)

if result.status == substance_painter.export.ExportStatus.Success:
    for stack, files in result.textures.items():
        print(f"导出 {stack}: {len(files)} 纹理")
else:
    print(f"导出失败: {result.message}")
```

### 3. 按资源单独设置分辨率

为不同资源导出不同分辨率（例如，英雄与背景）：

```python
config = {
    "exportPath": "C:/export",
    "defaultExportPreset": export_preset.url(),
    "exportList": [
        {"rootPath": "HeroCharacter"},   # 将使用 2048（覆盖下方设置）
        {"rootPath": "BackgroundProp"}   # 将使用 512（覆盖下方设置）
    ],
    "exportParameters": [
        {
            "filter": {"dataPaths": ["HeroCharacter"]},
            "parameters": {"sizeLog2": 11}  # 2048×2048
        },
        {
            "filter": {"dataPaths": ["BackgroundProp"]},
            "parameters": {"sizeLog2": 9}   # 512×512
        }
    ]
}
```

### 4. 自定义导出预设（分离通道）

创建自定义预设以将金属度和粗糙度作为单独文件导出：

```python
custom_preset = {
    "exportPresets": [{
        "name": "WebGL_Separated",
        "maps": [
            {
                "fileName": "$textureSet_baseColor",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ]
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ]
            },
            {
                "fileName": "$textureSet_metallic",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8"}
            },
            {
                "fileName": "$textureSet_roughness",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8"}
            }
        ]
    }]
}

config = {
    "exportPath": "C:/export",
    "exportPresets": custom_preset["exportPresets"],
    "exportList": [{"rootPath": "MyAsset", "exportPreset": "WebGL_Separated"}]
}
```

### 5. 移动端优化导出

针对移动 WebGL 的激进压缩：

```python
mobile_config = {
    "exportPath": "C:/export/mobile",
    "defaultExportPreset": export_preset.url(),
    "exportList": [{"rootPath": texture_set.name()}],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "jpeg",        # JPEG 用于 baseColor（有损但更小）
            "bitDepth": "8",
            "sizeLog2": 9,               # 512×512 最大
            "paddingAlgorithm": "infinite"
        }
    }, {
        "filter": {"outputMaps": ["$textureSet_normal", "$textureSet_metallicRoughness"]},
        "parameters": {
            "fileFormat": "png"          # PNG 用于数据贴图（无损）
        }
    }]
}
```

**导出后：** 使用 `pngquant` 或 `tinypng` 等工具进一步压缩。

### 6. glTF/GLB 集成

为 glTF 2.0 格式导出纹理：

```python
gltf_config = {
    "exportPath": "C:/export/gltf",
    "defaultExportPreset": substance_painter.resource.ResourceID(
        context="starter_assets",
        name="PBR Metallic Roughness"
    ).url(),
    "exportList": [{"rootPath": texture_set.name()}],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10,              # 1024×1024
            "paddingAlgorithm": "infinite"
        }
    }]
}

# 导出后，在 glTF 中引用：
# {
#   "materials": [{
#     "name": "Material",
#     "pbrMetallicRoughness": {
#       "baseColorTexture": {"index": 0},
#       "metallicRoughnessTexture": {"index": 1}
#     },
#     "normalTexture": {"index": 2}
#   }]
# }
```

### 7. 事件驱动导出插件

使用 Python 插件在保存时自动导出：

```python
import substance_painter.event
import substance_painter.export
import substance_painter.project

def auto_export(e):
    if not substance_painter.project.is_open():
        return

    config = {
        "exportPath": substance_painter.project.file_path().replace('.spp', '_textures'),
        "defaultExportPreset": substance_painter.resource.ResourceID(
            context="starter_assets", name="PBR Metallic Roughness"
        ).url(),
        "exportList": [{"rootPath": ts.name()} for ts in substance_painter.textureset.all_texture_sets()],
        "exportParameters": [{
            "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
        }]
    }

    substance_painter.export.export_project_textures(config)
    print("自动导出完成")

# 注册事件
substance_painter.event.DISPATCHER.connect(
    substance_painter.event.ProjectSaved,
    auto_export
)
```

## 集成模式

### Three.js + React Three Fiber

在 R3F 中使用导出的纹理：

```jsx
import { useTexture } from '@react-three/drei';

function TexturedMesh() {
  const [baseColor, normal, metallicRoughness, ao] = useTexture([
    '/textures/Asset_baseColor.png',
    '/textures/Asset_normal.png',
    '/textures/Asset_metallicRoughness.png',
    '/textures/Asset_ambientOcclusion.png',
  ]);

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial
        map={baseColor}
        normalMap={normal}
        metalnessMap={metallicRoughness}
        roughnessMap={metallicRoughness}
        aoMap={ao}
      />
    </mesh>
  );
}
```

参考 **react-three-fiber** 技能以了解高级 R3F 材质工作流程。

### Babylon.js PBR 材质

```javascript
import { PBRMaterial, Texture } from '@babylonjs/core';

const pbr = new PBRMaterial("pbr", scene);
pbr.albedoTexture = new Texture("/textures/Asset_baseColor.png", scene);
pbr.bumpTexture = new Texture("/textures/Asset_normal.png", scene);
pbr.metallicTexture = new Texture("/textures/Asset_metallicRoughness.png", scene);
pbr.useRoughnessFromMetallicTextureAlpha = false;
pbr.useRoughnessFromMetallicTextureGreen = true;
pbr.useMetallnessFromMetallicTextureBlue = true;
```

参考 **babylonjs-engine** 技能以了解高级 PBR 工作流程。

### glTF 导出管道

1. 从 Substance 导出纹理（如上）
2. 使用 glTF 导出器从 Blender 导出模型
3. 在 `.gltf` JSON 中引用 Substance 纹理
4. 使用 `gltf-pipeline` 进行 Draco 压缩：

```bash
gltf-pipeline -i model.gltf -o model.glb -d
```

参考 **blender-web-pipeline** 技能以了解完整的 3D 资产管道。

## 性能优化

### 纹理大小预算

**桌面 WebGL：** 总纹理内存约 100-150MB
**移动 WebGL：** 总纹理内存约 30-50MB

**每个资源预算：**
- 背景/道具：512×512（每贴图 1MB × 4 贴图 = 4MB）
- 标准资源：1024×1024（每贴图 4MB × 4 贴图 = 16MB）
- 英雄资源：2048×2048（每贴图 16MB × 4 贴图 = 64MB）

### 压缩策略

1. **JPEG 用于 baseColor**（70-80% 质量）- PNG 的 10 倍小
2. **PNG-8 用于数据贴图**（无损要求）
3. **Basis Universal**（`.basis`）- GPU 纹理压缩（90% 更小）
4. **纹理图集** - 将多个资源合并为单个纹理

### 通道打包

将灰度贴图打包到 RGB 通道以减少纹理数量：

**打包的 ORM（遮挡-粗糙度-金属度）：**
- 红色：遮挡
- 绿色：粗糙度
- 蓝色：金属度

在 Substance 中导出：
```python
orm_map = {
    "fileName": "$textureSet_ORM",
    "channels": [
        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
        {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
        {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
    ]
}
```

### Mipmaps

在引擎中为远距离查看的纹理始终启用 Mipmaps：

```javascript
// Three.js（自动）
texture.generateMipmaps = true;

// Babylon.js
texture.updateSamplingMode(Texture.TRILINEAR_SAMPLINGMODE);
```

## 常见陷阱

### 1. baseColor 颜色空间错误

**问题：** baseColor 导出在线性空间中看起来发白。

**解决方案：** Substance 默认以 sRGB 导出 baseColor（正确）。确保引擎使用 sRGB：

```javascript
// Three.js
baseColorTexture.colorSpace = THREE.SRGBColorSpace;

// Babylon.js（自动为 albedoTexture）
```

### 2. 法线贴图烘焙问题

**问题：** 法线贴图显示反转或不正确的阴影。

**解决方案：**
- 验证切线空间法线格式（DirectX vs. OpenGL Y 反转）
- Substance 使用 OpenGL（Y+），与 glTF 标准一致
- 如果使用 DirectX 引擎，导出时翻转绿色通道

### 3. 金属度/粗糙度通道顺序

**问题：** 金属度/粗糙度纹理的通道顺序颠倒。

**解决方案：** Substance 默认导出：
- 蓝色通道 = 金属度
- 绿色通道 = 粗糙度
- 符合 glTF 2.0 规范

### 4. UV 接缝处的填充伪影

**问题：** UV 接缝处出现黑色或彩色线条。

**解决方案：** 在导出设置中将填充算法设置为 **"无限"**：
```python
"paddingAlgorithm": "infinite"
```

### 5. 网络的过大纹理

**问题：** 4K 纹理导致网络加载时间长和内存问题。

**解决方案：**
- 默认使用 1024×1024 用于网络
- 仅对近距离查看的英雄资源使用 2048×2048
- 实施多分辨率 LOD 系统以使用多个分辨率集

### 6. 引擎中缺少 AO 贴图

**问题：** AO 贴图导出但在引擎中不可见。

**解决方案：**
- Three.js：需要第二个 UV 通道（`geometry.attributes.uv2`）
- Babylon.js：设置 `material.useAmbientOcclusionFromMetallicTextureRed = true`
- 替代方案：在 Substance 中将 AO 烘焙到 baseColor

## 资源

参考捆绑资源以了解完整工作流程：

- **references/python_api_reference.md** - 完整 Substance Painter Python API
- **references/export_presets.md** - 内置和自定义导出预设目录
- **references/pbr_channel_guide.md** - 深入了解 PBR 纹理通道
- **scripts/batch_export.py** - 批量导出所有纹理集
- **scripts/web_optimizer.py** - 后处理纹理用于网络（调整大小，压缩）
- **scripts/generate_export_preset.py** - 创建自定义导出预设 JSON
- **assets/export_templates/** - 针对 Three.js、Babylon.js、Unity 的预配置导出预设

## 相关技能

- **blender-web-pipeline** - 完整 3D 模型 → 纹理 → 网络管道
- **threejs-webgl** - 在 Three.js 中加载和使用 PBR 纹理
- **react-three-fiber** - 使用 Substance 纹理的 R3F 材质工作流程
- **babylonjs-engine** - Babylon.js PBR 材质系统集成
