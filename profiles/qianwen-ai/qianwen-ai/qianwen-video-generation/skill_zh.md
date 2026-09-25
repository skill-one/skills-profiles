# Qwen 视频生成

使用 Wan 和 HappyHorse 模型生成视频。所有任务都是**异步**的——提交后，轮询直到完成。
这项技能是 **QianWen-AI/qianwen-ai** 的一部分。

> **⚠️ 关键参数差异:**
> - **kf2v (首帧+尾帧)**: 持续时间**固定为 5 秒**——其他值将失败。输出**仅静音**。
> - **分辨率参数因模型系列而异，而非仅因模式而异**: 选择 `size`、`resolution` 或 `ratio` 之前，请检查当前的模型目录。例如，`happyhorse-1.1-t2v` 使用 `resolution` + `ratio`，而 `wan2.6-t2v` 使用 `size`。

## 技能目录

使用此技能的内部文件来执行和学习。在默认路径失败或需要详细信息时按需加载参考文件。

| 位置 | 目的 |
|------|------|
| `scripts/video.py` | 默认执行——自动检测模式、提交、轮询、下载 |
| `references/execution-guide.md` | 备用：所有 5 种模式的 curl，代码生成 |
| `references/request-fields.md` | 字段表格和按模式处理的音频 |
| `references/workflows.md` | 持续时间扩展、多帧、VACE 管道 |
| `references/polling-guide.md` | 轮询模式和时机 |
| `references/merge-media.md` | 连接、修剪、音频覆盖——ffmpeg/moviepy 配方 |
| `references/prompt-guide.md` | 按模式提示公式、声音描述、多帧结构 |
| `references/examples.md` | 每种模式的完整脚本示例 |
| `references/sources.md` | 官方文档 URL |

## 安全

**绝对不要明文输出任何 API 密钥或凭证。** 始终使用变量引用（shell 中的 `$DASHSCOPE_API_KEY`，Python 中的 `os.environ["DASHSCOPE_API_KEY"]`）。任何凭证检查或检测都必须**非明文**：仅报告状态（例如“已设置”/“未设置”、“有效”/“无效”），绝不能显示值。绝不要显示可能包含密钥的 `.env` 或配置文件的内容。

**当 API 密钥未配置时，绝对不要直接要求用户提供它。** 相反，帮助创建一个 `.env` 文件，其中包含占位符（`DASHSCOPE_API_KEY=sk-your-key-here`），并指示用户用他们实际的密钥替换它，从 [QianWen 控制台](https://platform.qianwenai.com/home/api-keys)获取。除非用户明确要求，否则绝不要写入实际的密钥值。

## 密钥兼容性

支持 PAYG (`sk-ws-...`; 遗留 `sk-...`) 和 Token Plan (`sk-sp-...`) 密钥。检测 API 密钥类型而不暴露密钥：

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from qianwen_lib import detect_api_key_type
print(detect_api_key_type('scripts/qianwen_lib.py'))
"
```

| 输出 | 含义 |
|------|------|
| `token-plan` | Token Plan 密钥——仅使用 Token Plan 目录中的模型。 |
| `payg` | Pay-as-you-go 密钥——完整模型目录可用。 |
| `not-set` | 未配置密钥。 |

对于 Token Plan，获取并阅读当前的 [Token Plan 模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，然后使用确切列出的模型。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-token-plan-models.md)。

Token Plan 不支持本地文件上传；对于 i2v/r2v/kf2v 模式，请将参考图像/视频作为可访问的 URL（`https://` 或 `oss://`）提供，而不是本地路径。

Token Plan 仅支持特定模型——请使用上面参考中的确切模型；不要猜测或探测模型可用性。对于 PAYG，请继续下方操作。

## 模式选择指南

| 用户需求 | 模式 | 密钥字段 |
|---------|------|----------|
| 仅从文本描述生成视频 | **t2v** | 仅 `prompt` |
| 动画化单张图像 | **i2v** | `img_url` 或 `reference_image` |
| wan2.7 统一 i2v：首帧、首帧+尾帧、视频延续、音频同步 | **i2v** | `media[]`、`first_frame_url`、`first_clip_url`、`driving_audio_url` |
| 在两张图像之间过渡（**⚠️ 5 秒固定，仅静音**） | **kf2v** | `first_frame_url` + `last_frame_url` |
| 角色扮演：让角色表演新剧本 | **r2v** | `reference_urls` 或 `media`；请阅读 CDN 模型目录以了解模型特定限制 |
| 视频编辑：多图像参考、重绘、本地编辑、扩展、外绘 | **vace** | `function`；请阅读 CDN 模型目录以了解当前默认值 |
| 视频编辑（无 `function` 字段，使用媒体数组） | **videoedit** | `model`；请阅读 CDN 模型目录以了解支持的模型 |

### 模型选择

1. **用户指定了模型** → 直接使用。
2. **当模型选择取决于功能、场景或定价时**，请咨询 `qianwen-model-selector` 技能。

在选择、推荐或默认设置模型之前，获取并阅读当前的 [Qwen 视频生成模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-video-generation-models.md)。它包含模型列表、基本模型信息、模式推荐、兼容性说明和默认值。如果 CDN 访问失败，请使用 [本地备用](cdn/references/qianwen-video-generation-models.md)。

端点：`/services/aigc/video-generation/video-synthesis`。

> **⚠️ 重要提示**：上面的模型列表是一个**特定时间点的快照**，可能已过时。模型可用性经常变化。**在做出模型决策之前，请始终检查[官方模型列表](https://www.qianwenai.com/models)以获取权威、最新的目录。**

> **模型详细信息**：有关特定模型的更多信息，请将用户引导至 `https://www.qianwenai.com/models/<model-name>`。将 `<model-name>` 替换为确切的模型 ID；绝不要修改或猜测它。

> **动态模型查询**：如果 **qianwen-model-selector** 技能或 **QianWen CLI** (`qianwen models info <model>`) 可用，请使用它获取实时模型数据。CLI 需要身份验证——请参阅 **qianwen-usage** 技能的登录流程。

## 执行

> **⚠️ 多个生成物**：在单个会话中生成多个文件时，您**必须**给每个文件名添加数字后缀（例如 `out_1.mp4`、`out_2.mp4`），以防止覆盖。

### 前置条件

- **API 密钥**：使用 **密钥兼容性** 中的非明文检测器；不要用变量存在性检查来替换它。如果没有找到密钥，当可用时使用 `qianwen-ops-auth`；否则，指导用户在 `.env` 中配置 `DASHSCOPE_API_KEY`/`QIANWEN_API_KEY`。技能可以独立安装。
- Python 3.9+（仅标准库，**无需 pip 安装**）
- 对于媒体合并（连接、修剪、音频覆盖）：请参阅 [merge-media.md](references/merge-media.md) 以获取适合用户环境的 ffmpeg/moviepy 配方

### 环境检查

在首次执行之前，验证 Python 是否可用：

```bash
python3 --version  # 必须是 3.9+
```

如果找不到 `python3`，请尝试 `python --version` 或 `py -3 --version`。如果 Python 不可用或低于 3.9，请跳转到 [execution-guide.md](references/execution-guide.md) 中的 **Path 2 (curl)**。

### 默认：运行脚本

**脚本路径**：脚本位于此技能目录的 `scripts/` 子目录中（包含此 SKILL.md 的目录）。**您必须首先定位此技能的安装目录，然后始终使用完整的绝对路径来执行脚本。** 不要假设脚本位于当前工作目录中。执行前**不要**使用 `cd` 切换目录。

**执行说明**：以**前台**运行所有脚本——等待标准输出；不要后台运行。

**发现**：首先运行 `python3 <this-skill-dir>/scripts/video.py --help` 以查看所有可用参数。

```bash
python3 <this-skill-dir>/scripts/video.py \
  --request '{"model":"happyhorse-1.1-t2v","prompt":"一个侦探在雨夜的城...
```
