# Modly 图像转 3D 技能

> 技能由 [ara.so](https://ara.so) 提供 — 2026 每日技能集合。

Modly 是一款本地运行的、开源的桌面应用程序（Windows/Linux），它使用在您的 GPU 上完全运行的 AI 模型将照片转换为 3D 网格模型 — 无需云服务，无需 API 密钥。

---

## 架构概述

```
modly/
├── src/                    # Electron + TypeScript 前端
│   ├── main/               # Electron 主进程
│   ├── renderer/           # React UI (渲染进程)
│   └── preload/            # IPC 桥接
├── api/                    # Python FastAPI 后端
│   ├── generator.py        # 核心生成逻辑
│   └── requirements.txt
├── resources/
│   └── icons/
├── launcher.bat            # Windows 快速启动
├── launcher.sh             # Linux 快速启动
└── package.json
```

应用程序作为 Electron 容器运行在本地 Python FastAPI 服务器之上。扩展是 GitHub 仓库，包含 `manifest.json` + `generator.py`，它们可以接入扩展系统。

---

## 安装

### 快速启动（无需构建）

```bash
# Windows
launcher.bat

# Linux
chmod +x launcher.sh
./launcher.sh
```

### 开发环境设置

```bash
# 1. 克隆
git clone https://github.com/lightningpixel/modly
cd modly

# 2. 安装 JS 依赖
npm install

# 3. 设置 Python 后端
cd api
python -m venv .venv

# 激活（Windows）
.venv\Scripts\activate

# 激活（Linux/macOS）
source .venv/bin/activate

pip install -r requirements.txt
cd ..

# 4. 运行开发模式（启动 Electron + Python 后端）
npm run dev
```

### 生产构建

```bash
# 为当前平台构建安装程序
npm run build

# 输出目录为 dist/
```

---

## 关键 npm 脚本

```bash
npm run dev        # 以开发模式启动应用程序（热重载）
npm run build      # 打包应用程序以进行分发
npm run lint       # 运行 ESLint
npm run typecheck  # TypeScript 类型检查
```

---

## 扩展系统

扩展是 GitHub 仓库，包含：
- `manifest.json` — 元数据和模型变体
- `generator.py` — 实现了 Modly 扩展接口的生成逻辑

### manifest.json 结构

```json
{
  "name": "我的 3D 扩展",
  "id": "my-extension-id",
  "description": "使用 XYZ 模型生成 3D 模型",
  "version": "1.0.0",
  "author": "您的姓名",
  "repository": "https://github.com/yourname/my-modly-extension",
  "variants": [
    {
      "id": "model-small",
      "name": "小型（更快）",
      "description": "较轻的变体，用于更快生成",
      "size_gb": 4.2,
      "vram_gb": 6,
      "files": [
        {
          "url": "https://huggingface.co/yourorg/yourmodel/resolve/main/weights.safetensors",
          "filename": "weights.safetensors",
          "sha256": "abc123..."
        }
      ]
    }
  ]
}
```

### generator.py 接口

```python
# api/extensions/<extension-id>/generator.py
# 每个扩展都必须实现的必需接口

import sys
import json
from pathlib import Path

def generate(
    image_path: str,
    output_path: str,
    variant_id: str,
    models_dir: str,
    **kwargs
) -> dict:
    """
    所有 Modly 扩展的必需入口点。
    
    Args:
        image_path:  输入图像文件的路径
        output_path: 输出 .glb/.obj 应保存的路径
        variant_id:  要使用的模型变体
        models_dir:  存储下载模型权重的目录
    
    Returns:
        包含键的字典：
            success (bool)
            output_file (str) — 生成的网格路径
            error (str, 可选)
    """
    try:
        # 加载您的模型权重
        weights = Path(models_dir) / variant_id / "weights.safetensors"
        
        # 运行您的推理
        mesh = run_inference(str(weights), image_path)
        
        # 保存输出
        mesh.export(output_path)
        
        return {
            "success": True,
            "output_file": output_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 安装扩展（UI 流程）

1. 打开 Modly → 转到 **模型** 页面
2. 点击 **从 GitHub 安装**
3. 粘贴 HTTPS URL，例如 `https://github.com/lightningpixel/modly-hunyuan3d-mini-extension`
4. 安装后，点击所需模型变体的 **下载**
5. 选择已安装的模型并上传图像以生成

### 官方扩展

| 扩展 | 模型 |
|-------|-------|
| [modly-hunyuan3d-mini-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-extension) | Hunyuan3D 2 Mini |

---

## Python 后端 API (FastAPI)

后端在本地运行。Electron 前端使用的关键端点：

```python
# 典型的后端路由模式 (api/main.py 或类似)

# GET /extensions         — 列出已安装的扩展
# GET /extensions/{id}    — 获取扩展详情 + 变体
# POST /extensions/install — 从 GitHub URL 安装扩展
# POST /generate          — 触发 3D 生成
# GET /generate/status    — 查询生成进度
# GET /models             — 列出下载的模型变体
# POST /models/download   — 下载模型变体
```

### 从 Electron 调用后端（IPC 模式）

```typescript
// src/preload/index.ts — 将后端调用暴露给渲染器
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('modly', {
  generate: (imagePath: string, extensionId: string, variantId: string) =>
    ipcRenderer.invoke('generate', { imagePath, extensionId, variantId }),

  installExtension: (repoUrl: string) =>
    ipcRenderer.invoke('install-extension', { repoUrl }),

  listExtensions: () =>
    ipcRenderer.invoke('list-extensions'),
})
```

```typescript
// src/main/ipc-handlers.ts — 主进程处理
import { ipcMain } from 'electron'

ipcMain.handle('generate', async (_event, { imagePath, extensionId, variantId }) => {
  const response = await fetch('http://localhost:PORT/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_path: imagePath, extension_id: extensionId, variant_id: variantId }),
  })
  return response.json()
})
```

```typescript
// src/renderer/components/GenerateButton.tsx — UI 使用
declare global {
  interface Window {
    modly: {
      generate: (imagePath: string, extensionId: string, variantId: string) => Promise<{ success: boolean; output_file?: string; error?: string }>
      installExtension: (repoUrl: string) => Promise<{ success: boolean }>
      listExtensions: () => Promise<Extension[]>
    }
  }
}

async function handleGenerate(imagePath: string) {
  const result = await window.modly.generate(
    imagePath,
    'modly-hunyuan3d-mini-extension',
    'hunyuan3d-mini-turbo'
  )

  if (result.success) {
    console.log('网格保存到:', result.output_file)
  } else {
    console.error('生成失败:', result.error)
  }
}
```

---

## 编写自定义扩展

### 最小扩展仓库结构

```
my-modly-extension/
├── manifest.json
└── generator.py
```

### 示例：封装 HuggingFace 扩散模型

```python
# generator.py
import torch
from PIL import Image
from pathlib import Path

def generate(image_path, output_path, variant_id, models_dir, **kwargs):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    weights_dir = Path(models_dir) / variant_id

    try:
        # 加载模型（示例模式）
        from your_model_lib import ImageTo3DPipeline
        
        pipe = ImageTo3DPipeline.from_pretrained(
            str(weights_dir),
            torch_dtype=torch.float16
        ).to(device)

        image = Image.open(image_path).convert("RGB")
        
        with torch.no_grad():
            mesh = pipe(image).mesh

        mesh.export(output_path)

        return {"success": True, "output_file": output_path}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 配置与环境

Modly 完全本地运行 — 无需环境变量或 API 密钥。GPU/CUDA 由 PyTorch 在扩展中自动检测。

相关配置位于：

```
package.json          # Electron 应用程序元数据、构建目标
api/requirements.txt  # 后端 Python 依赖
```

如果您需要配置后端端口或扩展目录，请检查 Electron 主进程配置（通常为 `src/main/index.ts`）中的常量，如 `API_PORT` 或 `EXTENSIONS_DIR`。

---

## 常见模式

### 检查扩展中 CUDA 是否可用

```python
import torch

def get_device():
    if torch.cuda.is_available():
        print(f"使用 GPU: {torch.cuda.get_device_name(0)}")
        return "cuda"
    print("未找到 GPU，回退到 CPU（慢）")
    return "cpu"
```

### 从 generator.py 报告进度

```python
import sys
import json

def report_progress(percent: int, message: str):
    """将进度写入 stdout，以便 Modly 可以显示它。"""
    print(json.dumps({"progress": percent, "message": message}), flush=True)

def generate(image_path, output_path, variant_id, models_dir, **kwargs):
    report_progress(0, "加载模型...")
    # ... 加载模型 ...
    report_progress(30, "处理图像...")
    # ... 推理 ...
    report_progress(90, "导出网格...")
    # ... 导出 ...
    report_progress(100, "完成")
    return {"success": True, "output_file": output_path}
```

### 在渲染器中添加新页面（React）

```typescript
// src/renderer/pages/MyPage.tsx
import React, { useEffect, useState } from 'react'

interface Extension {
  id: string
  name: string
  description: string
}

export default function MyPage() {
  const [extensions, setExtensions] = useState<Extension[]>([])

  useEffect(() => {
    window.modly.listExtensions().then(setExtensions)
  }, [])

  return (
    <div>
      <h1>已安装的扩展</h1>
      {extensions.map(ext => (
        <div key={ext.id}>
          <h2>{ext.name}</h2>
          <p>{ext.description}</p>
        </div>
      ))}
    </div>
  )
}
```

---

## 故障排除

| 问题 | 解决方法 |
|-------|-------|
| `npm run dev` — Python 后端未启动 | 确保 venv 已设置：`cd api && python -m venv .venv && pip install -r requirements.txt` |
| CUDA 内存不足 | 使用较小的模型变体或关闭其他 GPU 进程 |
| 扩展安装失败 | 验证 GitHub URL 是否为 HTTPS，且仓库根目录包含 `manifest.json` |
| 生成卡住 | 检查您的 GPU 驱动程序和 CUDA 工具包是否与 `requirements.txt` 中的 PyTorch 版本匹配 |
| Linux 上应用程序无法启动 | 使 `launcher.sh` 可执行：`chmod +x launcher.sh` |
| 模型下载停滞 | 检查磁盘空间；大型模型（4–10 GB）需要足够的可用空间 |
| `torch` 在扩展中未找到 | 确保 PyTorch 在 `api/requirements.txt` 中，而不仅仅是扩展自己的依赖 |

### 验证 GPU 是否被检测到

```bash
cd api
source .venv/bin/activate   # 或 .venv\Scripts\activate 在 Windows 上
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU')"
```

---

## 资源

- **主页**：https://modly3d.app
- **发布**：https://github.com/lightningpixel/modly/releases/latest
- **官方扩展**：https://github.com/lightningpixel/modly-hunyuan3d-mini-extension
- **Discord**：https://discord.gg/FjzjRgweVk
- **许可证**：MIT（要求归因 — 在分支中致谢 Modly + Lightning Pixel）
