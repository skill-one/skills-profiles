# Sonilo 文本转音效

根据文本描述生成单个音效——无需视频。提示词即输入，因此直接描述动作和材料。生成任务在后台异步运行；该工具内部轮询并返回保存的文件。

> **设置：** 请参考 [设置API密钥](../setup-api-key) 技能。

> ⚠️ **费用：** 此工具会发起API调用，可能产生费用。仅在明确要求时调用。

> **需要将音效匹配到片段吗？** 使用 [视频转音效](../video-to-sfx) — 它可以读取剪辑并可以将音效固定到特定时刻，而文本提示词无法做到。

## 传输方式：MCP或CLI

会话开始时选择一种并保持使用。不要在单个任务中混合使用这两种方式，也不要宣布选择。

1. **本会话中可见的Sonilo MCP工具** (`text_to_sfx` 及相关工具) — 使用它们。这是推荐的方式：无需shell，并且是唯一能在长时间生成后仍然可用的方式。如果认证调用失败——而不是输入错误——则此会话中无法使用此传输方式：应选择2而不是重试。

2. **没有可用的Sonilo MCP工具，但 `sonilo account` 返回0** — 使用下面的CLI命令。相同的API，相同的账户，相同的凭证文件。使用 `sonilo account` 进行探测，而不是 `sonilo whoami`：即使未登录，`whoami` 也会返回0，因此它无法区分这两种状态。

3. **两者都不是** — 停止并运行 [设置API密钥](../setup-api-key) 技能。不要使用curl绕过 `api.sonilo.com` 进行调用；两种传输方式都处理上传、轮询和重试，而纯请求则不处理。

## 快速入门

### MCP工具调用（推荐）

```
text_to_sfx(
    prompt="远处雷声隆隆，伴有小雨",
    duration=6
)
```

### Python (`pip install sonilo`)

```python
from sonilo import Sonilo

client = Sonilo()  # 读取 SONILO_API_KEY

sfx = client.text_to_sfx.generate(prompt="远处雷声隆隆，伴有小雨", duration=6)
sfx.save("thunder.m4a")
```

### JavaScript / TypeScript (`npm install sonilo`)

```ts
import { SoniloClient } from "sonilo";

const client = new SoniloClient(); // 读取 SONILO_API_KEY

const sfx = await client.textToSfx.generate({
  prompt: "远处雷声隆隆，伴有小雨",
  duration: 6,
});
```

### CLI (`npm install -g sonilo-cli` 或 `pip install sonilo-cli`)

```bash
sonilo text-to-sfx --prompt "远处雷声隆隆，伴有小雨" --duration 6
```

底层始终异步运行——CLI会自动提交并轮询。`--format` 接受 `wav|mp3|aac|flac`。

### cURL（原始REST API，无MCP主机）

```bash
curl -X POST "https://api.sonilo.com/v1/text-to-sfx" \
  -H "Authorization: Bearer $SONILO_API_KEY" \
  --data-urlencode "prompt=远处雷声隆隆，伴有小雨" \
  --data-urlencode "duration=6"
# -> {"task_id": "..."}  轮询 GET /v1/tasks/{task_id} 直到状态为成功/失败
```

该端点返回 `{"task_id": ...}` (HTTP 202)，结果从 `GET /v1/tasks/{task_id}` 获取，一旦 `status` 为最终状态。MCP工具会自动进行轮询并直接返回保存路径——只有在调用超时的情况下才会看到 `task_id`（参见 [任务恢复](../task-recovery)）。

## 工具

| 工具 | 描述 |
|------|------|
| `text_to_sfx(prompt, duration?, audio_format?, output_directory?)` | 仅根据文本描述生成一个SFX片段。 |

## 参数

| 参数 | 类型 | 默认值 | 备注 |
|------|------|--------|------|
| `prompt` | string | — | 必填。1–2000字符。 |
| `duration` | number | Sonilo的默认值 | 可选，0.5–180秒。如果用户未指定长度，则省略它——不要自行假设。允许分数值：最短效果、锁存器或点击声，在1秒内运行良好。 |
| `audio_format` | string | `aac` (`.m4a`) | `wav`、`mp3`、`aac` 或 `flac`。 |
| `output_directory` | string | `SONILO_MCP_BASE_PATH` | 绝对路径，或相对于基本路径。 |

## 提示词

提示词是唯一输入——没有片段需要映射。直接描述动作和材料，并组合元素："雨点打在铁皮屋顶" 比 "雨" 更具体；"电影感的轰鸣，恐怖" 或 "8位复古跳跃音效" 用于风格化提示。与视频路径相同的材料词汇和音效包思维：[参考资料/sfx-prompting.md](../references/sfx-prompting.md)。

一次生成并迭代提示词，而不是重试——失败运行会自动退款，但您的重试会产生新费用。

## 工作流程提示

- **这是用于无视频上下文的单个片段**——界面提示音、呼啸声、您将自行叠加的音效元素。如果用户有片段，请使用 [视频转音效](../video-to-sfx)。

- **必须指定持续时间。** 不要猜测——如果用户未说明，请询问。

- **不要将其与音乐混淆。** 对于背景音乐或配乐，请使用 [文本转音乐](../text-to-music) 或 [视频转音乐](../video-to-music)。

## 恢复超时的调用

后台异步运行；长时间生成仍可能超过 `TIME_OUT_SECONDS`。如果超出，错误会携带 `task_id`——任务仍在运行（并且已经收费）。稍后调用 `get_sfx_task(task_id)`——托管服务器上的 `get_generation_task(task_id)`——以获取结果；参见 [任务恢复](../task-recovery)。

## 输出文件

以请求的 `audio_format` (`.wav`/`.mp3`/`.flac`，或 `aac` 默认的 `.m4a`) 保存，从提示词命名（转换为短链接）或 `sfx-<任务ID的前8个字符>`。

## 错误处理

常见错误：`401` 无效密钥，`402` 余额不足/试用用尽，`422` 无效参数（例如持续时间超出范围），`429` 速率限制。请参阅 [账户](../account) 技能。
