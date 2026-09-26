# CorridorKey 绿幕抠像

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集。

CorridorKey 是一个神经网络，用于解决绿幕视频中的颜色*分离*问题。对于每个像素（包括运动模糊、头发或失焦边缘产生的半透明像素），它预测真实的直（未预乘）前景颜色和干净的线性alpha通道。它支持读写16位和32位EXR文件，用于VFX流程集成。

## 工作原理

每帧需要两个输入：
1. **RGB绿幕图像** — sRGB或线性伽马，sRGB/REC709色域
2. **Alpha提示** — 粗糙的黑白掩码（不需要精确）

模型根据提示填充细节；它是在模糊/侵蚀的掩码上训练的。

## 安装

### 前置条件
- [uv](https://docs.astral.sh/uv/) 包管理器（自动处理Python）
- NVIDIA GPU驱动程序支持CUDA 12.8+（用于GPU），或Apple M1+（用于MLX），或CPU回退

### Windows
```bat
# 双击或从终端运行：
Install_CorridorKey_Windows.bat

# 可选的重量级模块：
Install_GVM_Windows.bat
Install_VideoMaMa_Windows.bat
```

### Linux / macOS
```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖项 — 选择一个：
uv sync                  # CPU / Apple MPS（通用）
uv sync --extra cuda     # NVIDIA GPU（Linux/Windows）
uv sync --extra mlx      # Apple Silicon MLX

# 下载所需模型 (~300MB)
mkdir -p CorridorKeyModule/checkpoints
# 放置下载的 CorridorKey_v1.0.pth：
# CorridorKeyModule/checkpoints/CorridorKey.pth
```

模型下载：https://huggingface.co/nikopueringer/CorridorKey_v1.0/resolve/main/CorridorKey_v1.0.pth

### 可选的Alpha提示生成器
```bash
# GVM（自动，~80GB VRAM，适合个人使用）
uv run hf download geyongtao/gvm --local-dir gvm_core/weights

# VideoMaMa（需要掩码提示，社区优化后<24GB VRAM）
uv run hf download SammyLim/VideoMaMa \
  --local-dir VideoMaMaInferenceModule/checkpoints/VideoMaMa

uv run hf download stabilityai/stable-video-diffusion-img2vid-xt \
  --local-dir VideoMaMaInferenceModule/checkpoints/stable-video-diffusion-img2vid-xt \
  --include "feature_extractor/*" "image_encoder/*" "vae/*" "model_index.json"
```

## 关键CLI命令

```bash
# 在准备好的片段上运行推理
uv run python main.py run_inference --device cuda
uv run python main.py run_inference --device cpu
uv run python main.py run_inference --device mps   # Apple Silicon

# 列出可用的片段/镜头
uv run python main.py list

# 交互式设置向导
uv run python main.py wizard
uv run python main.py wizard --win_path /path/to/ClipsForInference
```

## Docker (Linux + NVIDIA GPU)

```bash
# 构建
docker build -t corridorkey:latest .

# 运行推理
docker run --rm -it --gpus all \
  -e OPENCV_IO_ENABLE_OPENEXR=1 \
  -v "$(pwd)/ClipsForInference:/app/ClipsForInference" \
  -v "$(pwd)/Output:/app/Output" \
  -v "$(pwd)/CorridorKeyModule/checkpoints:/app/CorridorKeyModule/checkpoints" \
  corridorkey:latest run_inference --device cuda

# Docker Compose
docker compose build
docker compose --profile gpu run --rm corridorkey run_inference --device cuda
docker compose --profile gpu run --rm corridorkey list

# 固定到特定GPU（多GPU系统）
NVIDIA_VISIBLE_DEVICES=0 docker compose --profile gpu run --rm corridorkey run_inference --device cuda
```

## 目录结构

```
CorridorKey/
├── ClipsForInference/          # 输入镜头放在这里
│   └── my_shot/
│       ├── frames/             # 绿幕RGB帧（PNG/EXR）
│       ├── alpha_hints/        # 粗糙的alpha掩码（灰度）
│       └── VideoMamaMaskHint/  # 可选：VideoMaMa的手绘提示
├── Output/                     # 处理后的结果
│   └── my_shot/
│       ├── foreground/         # 直RGBA EXR帧
│       └── alpha/              # 线性alpha通道帧
├── CorridorKeyModule/
│   └── checkpoints/
│       └── CorridorKey.pth     # 所需模型权重
├── gvm_core/weights/           # 可选GVM权重
└── VideoMaMaInferenceModule/
    └── checkpoints/            # 可选VideoMaMa权重
```

## Python使用示例

### 基本推理流程
```python
import torch
from pathlib import Path
from CorridorKeyModule.model import CorridorKeyModel  # 调整为实际模块路径
from CorridorKeyModule.inference import run_inference

# 加载模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CorridorKeyModel()
model.load_state_dict(torch.load("CorridorKeyModule/checkpoints/CorridorKey.pth"))
model.to(device)
model.eval()

# 在一个镜头文件夹上运行推理
run_inference(
    shot_dir=Path("ClipsForInference/my_shot"),
    output_dir=Path("Output/my_shot"),
    device=device,
)
```

### 读取/写入EXR文件
```python
import cv2
import numpy as np
import os

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

# 读取32位线性EXR帧
frame = cv2.imread("frame_0001.exr", cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYCOLOR)
# frame是float32，线性光，BGR通道顺序

# 转换BGR -> RGB用于处理
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# 写出输出EXR（直RGBA）
# 假设`foreground`是float32 HxWx4（RGBA，线性，直alpha）
foreground_bgra = cv2.cvtColor(foreground, cv2.COLOR_RGBA2BGRA)
cv2.imwrite("output_0001.exr", foreground_bgra.astype(np.float32))
```

### 使用OpenCV生成粗糙Alpha提示
```python
import cv2
import numpy as np

def generate_chroma_key_hint(image_bgr: np.ndarray, erode_px: int = 5) -> np.ndarray:
    """
    CorridorKey输入的快速绿色屏幕提示。
    返回灰度掩码（0=背景，255=前景）。
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # 根据你的特定绿幕调整这些范围
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    foreground_mask = cv2.bitwise_not(green_mask)

    # 侵蚀以将掩码与边缘拉开（CorridorKey处理边缘细节）
    kernel = np.ones((erode_px, erode_px), np.uint8)
    eroded = cv2.erode(foreground_mask, kernel, iterations=2)

    # 可选：轻微模糊以柔化提示
    blurred = cv2.GaussianBlur(eroded, (15, 15), 5)
    return blurred


# 使用
frame = cv2.imread("greenscreen_frame.png")
hint = generate_chroma_key_hint(frame, erode_px=8)
cv2.imwrite("alpha_hint.png", hint)
```

### 批量处理帧
```python
from pathlib import Path
import cv2
import numpy as np
import os

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

def prepare_shot_folder(
    raw_frames_dir: Path,
    output_shot_dir: Path,
    hint_generator_fn=None
):
    """
    从原始绿幕帧准备CorridorKey镜头文件夹。
    """
    frames_out = output_shot_dir / "frames"
    hints_out = output_shot_dir / "alpha_hints"
    frames_out.mkdir(parents=True, exist_ok=True)
    hints_out.mkdir(parents=True, exist_ok=True)

    frame_paths = sorted(raw_frames_dir.glob("*.png")) + \
                  sorted(raw_frames_dir.glob("*.exr"))

    for frame_path in frame_paths:
        frame = cv2.imread(str(frame_path), cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYCOLOR)

        # 复制帧
        cv2.imwrite(str(frames_out / frame_path.name), frame)

        # 生成提示
        if hint_generator_fn:
            hint = hint_generator_fn(frame)
        else:
            hint = generate_chroma_key_hint(frame)

        hint_name = frame_path.stem + ".png"
        cv2.imwrite(str(hints_out / hint_name), hint)

    print(f"准备了{len(frame_paths)}帧在{output_shot_dir}")


prepare_shot_folder(
    raw_frames_dir=Path("raw_footage/shot_01"),
    output_shot_dir=Path("ClipsForInference/shot_01"),
)
```

### 使用clip_manager.py Alpha提示生成器
```python
# GVM（自动 — 无需额外输入）
from clip_manager import generate_alpha_hints_gvm

generate_alpha_hints_gvm(
    shot_dir="ClipsForInference/my_shot",
    device="cuda"
)

# VideoMaMa（首先在VideoMamaMaskHint/中放置粗糙掩码）
from clip_manager import generate_alpha_hints_videomama

generate_alpha_hints_videomama(
    shot_dir="ClipsForInference/my_shot",
    device="cuda"
)

# BiRefNet（轻量级选项，无需大VRAM）
from clip_manager import generate_alpha_hints_birefnet

generate_alpha_hints_birefnet(
    shot_dir="ClipsForInference/my_shot",
    device="cuda"
)
```

## Alpha提示最佳实践

```python
# 良好：侵蚀的、略微模糊的提示 — 拉开边缘
# 模型根据提示填充边缘细节
kernel = np.ones((10, 10), np.uint8)
good_hint = cv2.erode(raw_mask, kernel, iterations=3)
good_hint = cv2.GaussianBlur(good_hint, (21, 21), 7)

# 差：扩展/膨胀的提示 — 模型在减去时表现更差
# 不要将掩码向外推过真实主体边界
bad_hint = cv2.dilate(raw_mask, kernel, iterations=3)  # 避免这样做

# 可接受：原始二值色键
# 即使硬二值掩码也有效 — 只是不要扩展
acceptable_hint = raw_chroma_key_mask  # 无膨胀
```

## 输出集成（Nuke / Fusion / Resolve）

CorridorKey输出**直（未预乘）RGBA EXR**，线性光：

```python
# 在Nuke中：读取EXR，设置色彩空间为"linear"
# Alpha已经干净 — 无需Unpremult节点
# 连接到带有背景底板的Merge（合并）节点

# 验证输出是直alpha（未预乘）：
import cv2, numpy as np, os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

result = cv2.imread("Output/shot_01/foreground/frame_0001.exr",
                    cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYCOLOR)
# result[..., 3] = alpha通道（线性0.0–1.0）
# result[..., :3] = 直颜色（未乘以alpha）

# 检查半透明像素
h, w = result.shape[:2]
sample_alpha = result[h//2, w//2, 3]
sample_color = result[h//2, w//2, :3]
print(f"Alpha: {sample_alpha:.3f}, Color: {sample_color}")
# 颜色值在alpha < 1.0时应为全强度（直alpha）
```

## 故障排除

### CUDA未检测到 / 回退到CPU
```bash
# 检查CUDA版本要求：驱动程序必须支持CUDA 12.8+
nvidia-smi  # 显示最大支持的CUDA版本

# 带显式CUDA额外重新安装
uv sync --extra cuda

# 验证PyTorch看到GPU
uv run python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

### OpenEXR读取/写入失败
```bash
# 必须在导入cv2之前设置环境变量
export OPENCV_IO_ENABLE_OPENEXR=1
uv run python your_script.py

# 或在Python中（必须在导入cv2之前）
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
import cv2
```

### VRAM不足
```bash
# 使用CPU回退
uv run python main.py run_inference --device cpu

# 或减少批处理大小/使用分块推理（如果支持）
# 引擎动态扩展到2048x2048分块 — 对于4K，
# 确保至少有6-8GB VRAM

# Apple Silicon：使用MPS
uv run python main.py run_inference --device mps
```

### 模型文件未找到
```bash
# 验证确切文件名和位置：
ls CorridorKeyModule/checkpoints/
# 必须命名为：CorridorKey.pth
# 不是：CorridorKey_v1.0.pth

mv CorridorKeyModule/checkpoints/CorridorKey_v1.0.pth \
   CorridorKeyModule/checkpoints/CorridorKey.pth
```

### Docker GPU直通失败
```bash
# 测试NVIDIA容器工具包
docker run --rm --gpus all nvidia/cuda:12.6.3-runtime-ubuntu22.04 nvidia-smi

# 如果失败，安装/重新配置nvidia-container-toolkit：
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# 然后重启Docker守护进程
sudo systemctl restart docker
```

### 抠像结果不佳
- **提示过于扩展**：更多地侵蚀你的Alpha提示 — CorridorKey在添加边缘细节方面比移除不需要的掩码区域更擅长
- **错误色彩空间**：确保输入是sRGB/REC709色域；不要直接传递log编码的镜头
- **绿色溢出**：模型处理颜色分离，但源中的极端绿色溢出可能会降低结果；考虑在推理前进行去溢出处理
- **静态主体**：GVM对人物效果最佳；尝试使用VideoMaMa并手动绘制提示用于道具/物体

## 社区与资源

- **Discord**：https://discord.gg/zvwUrdWXJm（Corridor Creates — 分享结果、分支、想法）
- **易用界面**：[EZ-CorridorKey](https://github.com/edenaion/EZ-CorridorKey) — 艺术家友好界面
- **模型权重**：https://huggingface.co/nikopueringer/CorridorKey_v1.0
- **GVM项目**：https://github.com/aim-uofa/GVM
- **VideoMaMa项目**：https://github.com/cvlab-kaist/VideoMaMa
