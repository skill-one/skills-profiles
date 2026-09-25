# Agnes AI 生成

使用此技能通过 `https://apihub.agnes-ai.com` 调用 Agnes 文本、图像和视频生成 API。

## 快速入门

1. 当需要了解端点详情、参数或响应字段时，请阅读 `references/api.md`。
2. 使用 `scripts/agnes_api.py` 进行实际 API 调用，而不是手动编写 curl 命令。
3. 需要在 `AGNES_API_KEY`、`AGNES_API_TOKEN` 或 `APIHUB_AGNES_API_KEY` 中提供 API 密钥。切勿打印密钥。
4. 对于轻量级实时验证，运行 `smoke-test`；默认情况下它会避免创建视频。添加 `--include-image-edit` 用于图像到图像，添加 `--video-case <case>` 明确指定视频模式。只有当基本文本、文本流式传输、文本工具调用、文本到图像、图像到图像、文本到视频、图像到视频、多图像视频、关键帧视频和视频检索都返回成功响应时，才将技能视为完全测试通过。

## 命令

文本生成：

```bash
python scripts/agnes_api.py text --prompt "为 AI 助手编写一条简洁的产品标语。"
```

流式文本：

```bash
python scripts/agnes_api.py text --prompt "编写一段简短的产品介绍。" --stream
```

流式输出会进行标准化，并包含聚合的 `content`、`events`、`done` 和简短的 `raw_prefix`。

图像生成：

```bash
python scripts/agnes_api.py image --prompt "日出时分，一座发光的浮空城悬在雾蒙蒙的峡谷之上，电影级写实风格" --size 1024x768
```

图像到图像：

```bash
python scripts/agnes_api.py image --prompt "将场景转换为保留构图的下雨天赛博朋克之夜" --image https://example.com/input.png --size 1024x768
```

带轮询的文本到视频：

```bash
python scripts/agnes_api.py video --prompt "日落时分，一只猫在海滩上行走的电影级镜头" --poll
```

图像到视频：

```bash
python scripts/agnes_api.py video --prompt "制作微妙的摄像机运动和自然光照动画" --image https://example.com/image.png --poll
```

关键帧/多图像视频：

```bash
python scripts/agnes_api.py video --prompt "在两个关键帧之间创建平滑的电影级过渡" --image https://example.com/a.png --image https://example.com/b.png --mode keyframes --poll
```

检索视频任务：

```bash
python scripts/agnes_api.py video-get video_123456
```

轻量级实时烟雾测试：

```bash
python scripts/agnes_api.py smoke-test
```

图像编辑烟雾测试：

```bash
python scripts/agnes_api.py smoke-test --include-image-edit
```

单个视频烟雾测试：

```bash
python scripts/agnes_api.py smoke-test --video-case text-to-video
```

## 工作流程

- 优先使用 `agnes-2.0-flash` 进行文本聊天/补全。
- 不要使用 Agnes 响应 API 的多轮函数调用进行自主工具工作流。实时测试显示，提供者可能会返回 `function_call` 且 `overall status=completed`，提交 `function_call_output` 时可能会使用 `previous_response_id` 失败。使用此技能的聊天补全路径进行文本生成，并将工具调用视为最佳努力请求形状兼容性。
- 优先使用 `agnes-image-2.1-flash` 进行文本到图像、图像到图像和高信息密度图像生成。高密度生成是提示驱动的；包括主体层次结构、环境、次要细节、光照、构图和质量要求。
- 优先使用 `agnes-video-v2.0` 进行文本到视频、图像到视频、多图像视频、关键帧动画、基于提示的运动和场景控制、电影级输出、异步任务创建、基于轮询的结果检索和基于种子的可重复性。
- 对于图像和视频生成，在调用图像/视频 API 之前，将任何非英文用户提示转换为流畅的英文生成提示。英文提示对 Agnes 视频生成更稳定。在翻译过程中保留具体的视觉细节、风格、光照、构图、运动、摄像机指令和约束。
- 对于视频，请记住 API 是异步的：首先创建任务，然后在创建响应包含 `video_id` 时进行轮询或检索。当 `video_id` 缺失时，脚本会回退到传统的 `task_id` 查找。
- 脚本在发送请求前会验证图像尺寸、视频帧数、帧率和尺寸。`num_frames` 必须是 `8n + 1` 且 `<= 441`；`81` 或 `121` 是好的短值。
- 视频命令默认 `num_frames=121` 和 `frame_rate=24` 以获得更稳定的生成。视频烟雾测试默认 `num_frames=81` 和 `frame_rate=24`。
- 在进行昂贵或耗时长的实时视频生成之前，除非用户明确要求测试或生成视频，否则请警告用户。
- 使用 `smoke-test --video-case <case>` 逐个测试视频功能，以避免同时创建多个任务。支持的案例是 `text-to-video`、`image-to-video`、`multi-image` 和 `keyframes`。

## 当前验证说明

- 本地确认：技能元数据验证和 Python 语法。
- 通过实时 API 确认：基本文本、流式文本、工具调用请求形状、文本到图像、图像到图像、高信息密度文本到图像、图像/视频中文提示翻译、完成的文本到视频 URL 检索和完成的图像到视频 URL 检索。
- 注意：Agnes 可能会接受工具调用请求参数，但不一致地返回 `tool_calls`；当需要严格的工具调用验证时，使用 `smoke-test --strict-tools`。
- 注意：Agnes 响应 API 的多轮函数调用不适用于代理工具循环；不要依赖它进行 Codex/Claude 风格的自动工具延续。
- 脚本和烟雾测试选择器支持，但在最新通过中未重新运行端到端：多图像视频和关键帧动画。
- 尚未确认端到端：每个多图像视频和关键帧动画任务的完成 URL 检索。之前的文本到视频任务返回了提供者端的 `division by zero` 错误，因此请保持视频重试可见并清晰报告提供者错误。

## 输出处理

- 默认情况下直接返回生成的图像/视频 URL。除非用户明确要求本地文件或视觉检查，否则不要下载、保存、打开或检查生成的媒体。
- 对于图像响应，当 `extra_body.response_format` 为 `url` 时，预期结果为 URL 格式。
- 对于视频响应，当 `status` 为 `completed` 时，从 `video_url`、`url` 或 `remixed_from_video_id` 中提取 URL。
- 对于视频检索，优先使用 `GET /agnesapi?video_id=...&model_name=agnes-video-v2.0`；传统的 `GET /v1/videos/{task_id}` 仍然是一个回退方案。
- 如果请求失败，请报告 HTTP 状态和提供者错误正文，而不要暴露 API 密钥。
