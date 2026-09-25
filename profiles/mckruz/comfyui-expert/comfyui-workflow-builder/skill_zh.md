# ComfyUI 工作流构建器

将自然语言请求翻译为可执行的 ComfyUI 工作流 JSON。生成前始终与资源清单进行验证。

## 工作流生成流程

### 第 1 步：理解请求

将用户意图解析为：
- **输出类型**：图像、视频或音频
- **源材料**：纯文本、参考图像、现有视频
- **身份识别方法**：无、零样本（InstantID/PuLID）、LoRA、Kontext
- **质量级别**：草稿（快速迭代）与生产（最高质量）
- **特殊要求**：ControlNet、修复、放大、口型同步

### 第 2 步：检查资源清单

读取 `state/inventory.json` 以确定：
- 可用检查点 → 选择最适合任务的匹配项
- 可用身份识别模型 → 确定哪些方法是可行的
- 可用 ControlNet 模型 → 如有可用，则启用姿态/深度控制
- 已安装的自定义节点 → 验证所有必需节点是否存在
- 可用 VRAM → 相应地优化设置

### 第 3 步：选择管道模式

根据请求 + 资源清单，从以下模式中选择：

| 模式 | 适用场景 | 关键节点 |
|------|----------|----------|
| 文本到图像 | 简单生成 | 检查点 → CLIP → KSampler → VAE |
| 保持身份的图像 | 角色一致性 | + InstantID/PuLID/IP-Adapter |
| LoRA 角色 | 训练角色 | + LoRA Loader |
| 图像到视频（Wan） | 高质量视频 | Diffusion Model → Wan I2V → Video Combine |
| 图像到视频（AnimateDiff） | 快速视频、运动控制 | + AnimateDiff Loader + Motion LoRAs |
| 说话头像 | 角色说话 | 图像 → 视频 → 语音 → 口型同步 |
| 放大 | 增强分辨率 | 图像 → UltimateSDUpscale → 保存 |
| 修复 | 编辑区域 | 图像 + 掩码 → 修复模型 → KSampler |

### 第 4 步：生成工作流 JSON

**ComfyUI 工作流格式：**

```json
{
  "{node_id}": {
    "class_type": "{NodeClassName}",
    "inputs": {
      "{param_name}": "{value}",
      "{connected_param}": ["{source_node_id}", {output_index}]
    }
  }
}
```

**规则：**
- 节点 ID 是字符串（通常为 "1"、"2"、"3" 等）
- 连接输入使用数组格式：`["source_node_id", output_index]`
- 输出索引是 0-based 整数
- 文件名必须与资源清单中的完全匹配
- 种子值：使用随机大整数或固定值以实现可重复性

### 第 5 步：验证

向用户展示前：

1. 每个 `class_type` 存在于资源清单的节点列表中
2. 每个模型文件名存在于资源清单的模型列表中
3. 所有必需的连接都存在（无悬空输入）
4. VRAM 估计值不超过可用 VRAM
5. 分辨率与所选模型兼容（512 用于 SD1.5，1024 用于 SDXL/FLUX）

### 第 6 步：输出

**如果在线模式**：通过 `comfyui-api` 技能排队
**如果离线模式**：将 JSON 保存到 `projects/{project}/workflows/`，并使用描述性名称

## 工作流模板

### 基本文本到图像（FLUX）

```json
{
  "1": {
    "class_type": "LoadCheckpoint",
    "inputs": {"ckpt_name": "flux1-dev.safetensors"}
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "{positive_prompt}", "clip": ["1", 1]}
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "{negative_prompt}", "clip": ["1", 1]}
  },
  "4": {
    "class_type": "EmptyLatentImage",
    "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
  },
  "5": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 25,
      "cfg": 3.5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["4", 0]
    }
  },
  "6": {
    "class_type": "VAEDecode",
    "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
  },
  "7": {
    "class_type": "SaveImage",
    "inputs": {"filename_prefix": "output", "images": ["6", 0]}
  }
}
```

### 带身份保持（InstantID + IP-Adapter）

通过添加以下内容扩展基本模板：
- 加载参考图像节点
- InstantID 模型加载器 + 应用 InstantID
- IPAdapter 统一加载器 + 应用 IPAdapter
- FaceDetailer 后处理

请参阅 `references/workflows.md` 获取完整的节点设置。

### 视频生成（Wan I2V）

使用不同的加载器链：
- 加载 Diffusion 模型（不是 LoadCheckpoint）
- Wan I2V 条件化
- EmptySD3LatentImage（带帧数）
- Video Combine (VHS)

请参阅 `references/workflows.md` Workflow 4 获取完整设置。

## VRAM 估计

| 组件 | 大约 VRAM |
|------|----------|
| FLUX FP16 | 16GB |
| FLUX FP8 | 8GB |
| SDXL | 6GB |
| SD1.5 | 4GB |
| InstantID | +4GB |
| IP-Adapter | +2GB |
| ControlNet（每个） | +1.5GB |
| Wan 14B | 20GB |
| Wan 1.3B | 5GB |
| AnimateDiff | +3GB |
| FaceDetailer | +2GB |

## 常见错误避免

1. **输出索引错误**：CheckpointLoader 输出 `[model, clip, vae]` 在索引 `[0, 1, 2]`
2. **InstantID 的 CFG 过高**：使用 4-5，不是默认的 7-8
3. **模型分辨率错误**：FLUX/SDXL=1024，SD1.5=512
4. **缺少 VAE**：FLUX 需要显式 VAE (`ae.safetensors`)
5. **加载器中的模型错误**：Diffusion 模型需要 `LoadDiffusionModel`，而不是 `LoadCheckpoint`

## 参考文件

- `references/workflows.md` - 详细节点模板
- `references/models.md` - 模型文件和路径
- `references/prompt-templates.md` - 模型特定提示
- `state/inventory.json` - 当前资源清单缓存
