# 视频

在 Starchild 上使用此技能处理所有**视频生成请求**。

**核心原则**：调用提供的脚本。不要重新实现代理/计费/上传管道。

---

## 1. 文本转视频（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 直接将其粘贴到 bash 命令中会导致 `语法错误 near unexpected token 'open'`。
> 此外，`python3 -c` 内部的 `exec(open(...))` 会因使用 `__file__` 进行路径解析而失败，导致 `NameError: __file__`。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 并配合 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/video")
> from generate_video import generate_video
> result = generate_video(
>     prompt="日出时雪山的航拍电影镜头",
>     model="balanced",
>     duration=5,
> )
> print(result)
> EOF
> ```
>
> 她源文档 (`<<'EOF'`) 保留了所有引号和换行符 — 无需转义。
> 注意：视频技能没有 `exports.py` — 直接从 `generate_video` 导入。

```python
exec(open('skills/video/generate_video.py').read())
result = generate_video(
    prompt="日出时雪山的航拍电影镜头",
    model="balanced",   # "budget" | "balanced" | "premium"
    duration=5,
)
# result -> {"success": True, "cost": 0.70, "video_url": "...", "local_path": "output/videos/..."}
```

`generate_video` 自动：提交 → 汇报 → 获取结果 → 下载 mp4 到 `output/videos/`。

### 将结果交付给用户 — 重要

**绝对不要直接将原始 `video_url`（例如 `https://*.fal.media/.../*.mp4`）交给用户。** fal 以 `Content-Security-Policy: sandbox; default-src 'none'` 的方式提供这些文件，这意味着：

- 在浏览器中打开链接会显示**空白页面**（没有触发内联播放器）。
- 通过 `<video>` / `<iframe>` 嵌入被 CSP 阻止。
- 没有 `Content-Disposition: attachment` 头，因此浏览器不会自动下载。
- URL 端的调整（查询参数、`?download=1` 等）**无法修复此问题** — 只有服务器端头更改才能解决，而我们无法控制 fal 的 CDN。

唯一可靠的面向用户的交付路径是**已下载的本地文件**：

1. 使用 `result["local_path"]`（例如 `output/videos/xxx.mp4`）— `generate_video` 在成功时始终会下载。
2. 告知用户文件保存在 `output/videos/<filename>`，可在工作区文件面板/文件浏览器中查看。
3. 在 Web 渠道中，也内嵌它以便用户在聊天中预览：
   ```markdown
   ![video](output/videos/<filename>.mp4)
   ```
   （或链接为 `[video](output/videos/<filename>.mp4)` — 工作区会直接使用正确的头服务这些文件）。
4. 在 Telegram / WeChat：通过 `send_to_telegram(file_path="output/videos/...", message_type="video")` 或 `send_to_wechat(file_path="output/videos/...", message_type="video")` 发送文件。

如果下载以某种方式失败（`local_path` 缺失）— 重新获取：
```bash
curl -L -o output/videos/<filename>.mp4 "<video_url>"
```
然后交付本地路径。仍然**不要**将原始 fal URL 作为主要交付内容。

---

## 2. 图像转视频 / 视频转视频（参考资产）

fal.ai 需要参考资产作为**公开的 https URL**。fal 存储上传需要 Serverless 权限，而您的密钥目前没有此权限。可靠的路径是通过**发布的 Starchild 预览**暴露资产。

### 标准流程

1. **将或复制资产**到 `output/fal_assets/` 使用 `publish_asset.py`。
2. **确保运行并发布名为 `fal-assets` 的预览**（一次性设置，见 §3）。
3. **构建公共 URL**作为 `<preview_base>/<filename>`。
4. **调用 `generate_video(... image_url=public_url)`**。

```python
# 第 1 步：将本地图像发布到资产文件夹
exec(open('skills/video/publish_asset.py').read())
asset = publish_local('/path/to/your/photo.jpg')
# 或：publish_from_url('https://example.com/photo.jpg')

filename = asset['filename']

# 第 2 步：与预览的公共基础 URL 结合（见 §3）
public_url = f"https://community.iamstarchild.com/<user_slug>-fal-assets/{filename}"

# 第 3 步：图像转视频
exec(open('skills/video/generate_video.py').read())
result = generate_video(
    prompt="温柔的 cinematic 摄像机推进",
    model="balanced",
    duration=5,
    image_url=public_url,
)
```

`generate_video` 在提供 `image_url` 时自动将模型路径从 `*/text-to-video` 重写为 `*/image-to-video`。相同的方法适用于视频转视频模型 — 传递 mp4 URL 即可。

### 资产限制（由 `publish_asset.py` 强制）

- 图像：`.jpg .jpeg .png .webp .gif .bmp`，最大 **10 MB**
- 视频：`.mp4 .mov .webm .mkv .m4v`，最大 **100 MB**
- 任何超出这些范围的都会在发布前被拒绝

---

## 3. 一次性 `fal-assets` 公共预览设置

每个工作区运行一次。预览跨会话持续运行。

```python
# 3.1 确保资产文件夹存在并带有占位符索引
import os, pathlib
pathlib.Path('output/fal_assets').mkdir(parents=True, exist_ok=True)
if not os.path.exists('output/fal_assets/index.html'):
    open('output/fal_assets/index.html', 'w').write(
        '<!doctype html><html><body><h1>fal 资产主机</h1></body></html>'
    )

# 3.2 启动预览
preview(action='serve', dir='output/fal_assets', title='fal-assets')

# 3.3 发布到公共 URL
preview(action='publish', preview_id='<id from step 3.2>', slug='fal-assets', title='fal-assets')
# → 公共基础：https://community.iamstarchild.com/<user_slug>-fal-assets/
```

发布后，公共基础 URL 可用于所有未来的图像转视频 / 视频转视频任务。文件放入 `output/fal_assets/` 后立即可通过 `<base>/<filename>` 访问 — 无需重新发布。

验证：
```bash
curl -sI https://community.iamstarchild.com/<user_slug>-fal-assets/<filename>
# 预期：HTTP/2 200, content-type: image/* 或 video/*
```

如果 `preview(action='serve')` 返回 `No available ports in pool`，请询问用户哪个现有预览可以停止以释放端口 — 不要无声地终止。

---

## 4. 模型选择

| 等级 | 模型 | 每 5 秒成本 | 备注 |
|------|-------|-----------|-------|
| **budget** | `fal-ai/wan/v2.5/text-to-video` | $0.25 | 速度最快，最便宜；适合提示语迭代 |
| **balanced** | `alibaba/happy-horse/text-to-video` | $0.70 | 默认；最佳唇同步，大多数用例 |
| **premium** | `bytedance/seedance-2.0/fast/text-to-video` | $1.20 | 最佳动作 + 摄像机方向 |
| **mini** | `bytedance/seedance-2.0/mini/text-to-video` | $0.36 (480p) / $0.77 (720p) | 最便宜 Seedance；分辨率分层，无 1080p。**持续时间必须为字符串**（`"5"`，不是 `5` 或 `"5s"`）— 见下文陷阱 |
| **premium-25** | `bytedance/seedance-2.5/text-to-video` | token-based | 支持文本转视频、图像转视频和参考转视频。需要 `resolution` (`480p`/`720p`)，`aspect_ratio`（六种支持比例），以及 4–30 秒的整数 `duration`。使用 `estimate_cost(..., aspect_ratio=...)` 估算。 |
| — | `xai/grok-imagine-video/v1.5/image-to-video` | $0.41 (480p) / $0.71 (720p) 每 5 秒 | **仅图像转视频**（单个必需 `image_url`，无 `image_urls`）；包含 $0.01 输入图像附加费。⚠️ `resolution="1080p"` 在上游是模式有效的，但没有发布价格 — 代理会 400 fail-closed 拒绝 |
| — | `fal-ai/kling-video/v3/turbo/standard/text-to-video` | $0.56 每 5 秒 | Kling v3 Turbo Standard，每秒 $0.112，flat $0.112/s；`.../turbo/pro/...` = $0.14/s ($0.70/5s)；`.../v3/4k/...` = $0.42/s ($2.10/5s)。所有模型都有 i2v 变体 |
| — | `alibaba/happy-horse/v1.1/text-to-video` | $0.70 (720p) / $0.90 (1080p) 每 5 秒 | v1.1 有自己的 1080p 等级 **$0.18/s**（不是 v1.0 的 2× 规则）；也支持 `/image-to-video`，`/reference-to-video` |
| — | `fal-ai/minimax_h3/text-to-video` | 代理价格适用 | 支持文本转视频、图像转视频和参考转视频。传递 `image_urls=[...]` 进行参考转视频；有效载荷会被转换为上游 `reference_image_urls`。 |

⚠️ **Happy Horse 默认上游分辨率是 1080p**（v1.0 和 v1.1）：省略 `resolution` 会计费 1080p 等级（v1.1 5s = $0.90；v1.0 ref2v 5s = $1.40）。明确传递 `resolution="720p"` 以获取更便宜的价格。代理会 400 拒绝无效分辨率值。

**参考转视频**：传递 `image_urls=[...]`（1–9 个公共 HTTP(S) URL 列表）— 不是单个 `image_url` 参数。`generate_video()` 验证数量和 URL 方案。Happy Horse 和 Seedance 2.5 提交 `image_urls` 字段；MiniMax H3 (`fal-ai/minimax_h3/reference-to-video`) 提交上游的 `reference_image_urls` 字段。

**Seedance 2.5 示例**：
```python
result = generate_video(
    prompt="纸鹤展开的 cinematic 特写",
    model="bytedance/seedance-2.5/text-to-video",
    duration=5,
    resolution="720p",
    aspect_ratio="16:9",
)
```
使用 4–30 秒的整数 `duration`。`resolution` 必须是 `480p` 或 `720p`；`aspect_ratio` 必须是 `21:9`，`16:9`，`4:3`，`1:1`，`3:4`，`9:16`。代理会拒绝 `auto` 值，因为它们无法安全定价。

通过传递完整模型 ID 到 `generate_video(model=...)` 覆盖。图像转视频变体会自动将 `text-to-video` 替换为 `image-to-video`。

定价细节和模型注册表位于 `generate_video.py::estimate_cost`。对于尚未在此注册的模型，遗留回退只是一个粗略估计，可能与代理不同；不要用于预算新端点。

---

## 5. 汇报现有请求

```python
exec(open('skills/video/poll_status.py').read())
result = poll_video("019ded6c-d871-7290-bbf1-ddc6993f8958")
```

当先前的 `generate_video` 调用超时或您只有 `request_id` 时使用。

---

## 6. 提供的脚本

- `generate_video.py` — 提交 → 汇报 → 下载。处理文本转视频和图像转视频。
- `publish_asset.py` — 复制本地文件（或下载远程 URL）到 `output/fal_assets/` 以便 `fal-assets` 预览可以服务它们。
- `poll_status.py` — 通过 `request_id` 继续汇报，完成时下载结果。

---

## 7. 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `image_url must be a public HTTP(S) URL` | 使用 `publish_asset.py` + `fal-assets` 预览，然后传递公共 URL |
| `No available ports in pool` (preview serve) | 询问用户哪个预览可以停止；不要自动终止 |
| `downstream_service_error` after `COMPLETED` | 参考资产主机在渲染中途失败 — 重新编码/调整大小为 16:9，重新发布，重试 |
| `HTTP 402 insufficient_credits` | 充值余额；提交时预扣费用 |
| `HTTP 403 endpoint_not_allowed` | sc-proxy 仅允许批准的 fal 视频端点；从模型表中选择一个 |
| Generation `FAILED` upstream | 缩短提示语，删除不寻常的 token，更改模型前重试一次 |
| `HTTP 422 literal_error` on `duration` (Seedance Mini) | Mini 要求 `duration` 为字符串 (`"5"`，`"10"`，`"auto"`)，不是整数，也不是 `"5s"`。`generate_video()` 在 `model` 包含 `seedance-2.0/mini` 时自动编码此值 — 只有在您手动构建请求正文时才会遇到此问题。其他 Seedance 变体接受整数/`"5s"`，如之前所述。 |
| Seedance 2.5 拒绝 `auto` 或返回 `resolution_not_priceable` / `aspect_ratio_not_priceable` | 传递明确的 `resolution="480p"` 或 `"720p"`，一个明确支持 `aspect_ratio`，以及 4–30 秒的整数 `duration`。Seedance 2.5 使用 token-based 定价；调用 `estimate_cost(model, duration, resolution, aspect_ratio)` 获取本地估算。 |
| MiniMax H3 参考请求返回参数错误 | 使用 `image_urls=[...]` 与 `fal-ai/minimax_h3/reference-to-video` 模型。`generate_video()` 将其转换为上游 `reference_image_urls`；不要将 `image_urls` 发送到上游。 |
| Job stuck `IN_PROGRESS` >15 min | 保存 `request_id`，稍后使用 `poll_status.py` 继续汇报 |
| 用户报告 fal.media 链接 "显示为空" / "空白页面" | 预期 — fal 以 `CSP: sandbox; default-src 'none'` 服务。将本地文件交付给 `result["local_path"]` 而不是原始 URL（见 §1）。 |

---

## 8. 基础设施（参考）

- Caller → `sc-proxy` → `queue.fal.run`（和 `api.fal.ai`）→ fal 模型提供者
- 所有请求必须包含 `Authorization: Key fake-falai-key-12345`（代理注入真实 `FAL_KEY`）
- 提交时发生预扣。汇报/结果调用免费。
- 允许的端点：视频文本转视频 / 图像转视频 / 视频转视频 / 编辑视频（注册的模型）。任何其他内容返回 `403 endpoint_not_allowed`。
- 最终 mp4 位于 `https://*.fal.media/...` — 公共 CDN，下载无需认证。

---

## 9. 维护

- 添加新模型 → 在 `generate_video.py::estimate_cost` 和 `transparent-proxy/apis/falai.py::_VIDEO_PRICING` 中注册价格。
- 通过 fal 存储上传的资产托管**故意不**在此技能中使用：生产的 `FAL_KEY` 缺少 Serverless 权限。继续使用预览方法，直到情况改变。
