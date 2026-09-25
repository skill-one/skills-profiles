<!-- 
SPDX-文件版权声明: 版权所有 (c) 2026 NVIDIA CORPORATION & AFFILIATES。保留所有权利。
SPDX-许可标识符: Apache-2.0
-->

# 临床语音识别飞轮 — 第一阶段（设置）

> **代理：此文件是完整的第一阶段程序。** 不要调用 `find`、`ls`、`rg` 或 `grep` 来寻找安装程序或隐藏配置——没有这样的东西。下面的四个部分（出站数据披露、编号检查、兄弟交接）都是必读内容；不要跳过任何一部分。功能 ID、环境变量约定和冒烟测试门禁将在下文内联——从实际写入的内容中回答，而不是从先前的 Riva/NVCF 熟悉程度中回答。

第一阶段只有一个任务：证明用户可以使用他们当前持有的 `NVIDIA_API_KEY` 到达 NVIDIA 托管的语音堆栈。一旦单个临床句子通过 Magpie TTS → Parakeet/Nemotron ASR 成功往返，用户就有资格进入 `/digital-health-clinical-asr-build`。

四阶段飞轮的存在是为了降低**KER（关键词错误率）**在临床实体（药物、程序、解剖结构、病症、实验室、角色）上的错误。WER 平均值会掩盖对临床有影响的失败；KER 是第三阶段将用来评估你的指标。

在这个技能的任何地方都没有**安装脚本**——不是 `install.sh`，不是 `setup.py`，没有任何隐藏的。第一阶段 *就是* 下面三个步骤：验证密钥、安装 Python 依赖项、运行冒烟测试。第一阶段之后的所有内容都是由兄弟技能（`/data-designer`、`/riva-tts`、内联的第三阶段 ASR 配方、`/riva-asr-custom`）组成的。如果用户问“什么脚本安装所有内容？”，请从这段话中回答；不要去寻找。

## 出站数据流——在发送任何文本或音频之前显示

在这个飞轮期间，有两个外部端点接收数据。用户必须在第二阶段开始之前确认这两个端点，以符合其组织强制执行的数据治理政策。**请逐字渲染下面的表格在你的响应中——释义不满足披露要求；字面表达才是关键。**

| 服务 | 发送什么 | 何时 | 由谁托管 |
|---|---|---|---|
| **NVIDIA NVCF** (`grpc.nvcf.nvidia.com`) | 您合成的临床句子（文本），以及您转录的 WAV 文件（音频） | 每个第二阶段 TTS 调用和每个第三阶段 ASR 调用 | NVIDIA，受 build.nvidia.com 条款约束 |
| **Merriam-Webster** (`dictionaryapi.com` JSON API **或** 公开的 `merriam-webster.com` HTML 网站) | 单个临床术语（药物名称、解剖结构、程序），每个术语一个 HTTP 请求 | 第二阶段 IPA 标记——见下文“两条 MW 路径”以确定适用哪个端点 | Merriam-Webster，受其 API 或网站条款约束 |

数据是**按设计合成的**——飞轮根据用户编辑的术语列表制造句子和音频，而不是从真实的患者会话中。话虽如此：**不要通过任何阶段输入真实的患者转录、录制的临床音频或任何 PHI。** 如果术语列表本身包含敏感材料（代号药物、未发布的 产品名称），用户应在继续之前咨询其组织的外部 API 政策。可以关闭任一端点：

- **完全跳过 Merriam-Webster：** 将 `DICTIONARY_API_KEY` 不设置，并且不运行一个抓取器。第二阶段会回退到 Magpie G2P，它仍然可以工作，但对长尾临床术语的覆盖范围较弱。
- **跳过 NVCF：** 这是一个硬停止。Magpie TTS + Parakeet/Nemotron ASR *是* 工作负载；没有它们，这个技能系列是错误的工具——您需要的是一个自托管的 ASR/TTS 管道。

建议将此通知的副本放置在用户的 `README.md` 工作区中；如果它不在那里，请在第一次调用时将其提前。

## 目的

为第二阶段准备一个新鲜的环境。有三个事情要确认：密钥存在、依赖项可以干净地导入、托管堆栈实际上可以响应。以命名要运行的下一个技能结束。

四个 `digital-health-clinical-asr-*` 技能是**自包含的**——每个 TTS、ASR、IPA 标记和评分配方都生活在它们内部；运行飞轮端到端不需要安装其他代理技能。

这个技能对工作区布局不持任何意见。用户决定他们的周期工件在哪里存放；`data/eval_sets/cycle<N>/` 不会被强加。

## 何时使用此技能

在以下用户短语激活时：

- "设置临床语音识别飞轮"
- "初始化临床-asr 评估"
- "我想评估临床术语上的 ASR——我从哪里开始？"
- "为飞轮引导我的环境"
- "在运行飞轮之前我需要安装什么？"

**不要**在以下情况下激活：

- 用户已经有一个清单并想要评分 → `/digital-health-clinical-asr-eval`
- 用户已经设置了环境并想要管理术语 → `/digital-health-clinical-asr-build`
- 用户正在询问关于第四阶段微调 NGC/Docker 设置的特定问题 → 那些内容在 `/digital-health-clinical-asr-finetune` 内部涵盖

## 前提条件

| 要求 | 是否必需 | 原因 | 如何 |
|---|---|---|---|
| `NVIDIA_API_KEY` (`nvapi-…`) | **必需** | 通过 NVCF 托管的 Magpie TTS + Parakeet/Nemotron ASR | 在 <https://build.nvidia.com> 上签发；在 shell 中 `export NVIDIA_API_KEY=...` |
| Python ≥ 3.10 | **必需** | NeMo 客户端、评分、清单工具 | `python3 --version` |
| `nvidia-riva-client`, `pandas`, `soundfile`, `requests` | **必需** | TTS + ASR 客户端、清单 I/O、MW 查找 | `pip install nvidia-riva-client pandas soundfile requests` |
| `DICTIONARY_API_KEY` | 可选 | 通过 JSON API 查找 Merriam-Webster 医学词典（构建技能中的路径 A——推荐） | 免费密钥在 <https://dictionaryapi.com>。构建技能中的路径 B（对 `merriam-webster.com` 的 HTML 抓取，无需密钥，易碎）也在构建技能中记录，如果您无法获得密钥。没有任一路径，第二阶段会回退到 Magpie G2P，对长尾临床术语的覆盖范围较弱。 |
| `jiwer` | 可选 | 与内联的 Levenshtein 实现的参考 WER/CER 对比 | `pip install jiwer` — 评估技能包含纯 Python 降级 |
| (仅限第四阶段) `NGC_API_KEY` + CUDA 主机 + NeMo 容器 | 可选、延迟 | 微调工作负载 | 在 `/digital-health-clinical-asr-finetune` 内设置；直到评估显示 KER > 0.3 才延迟 |

## 说明

**范围。** 此技能执行**只读环境检查**：确认密钥已导出（仅长度检查）、Python 版本、库可以导入、托管堆栈对单个冒烟测试往返做出响应。它**不**安装系统包、修改 shell rc 文件、在 `.venv/` 之外写入磁盘，或尝试使用真实的密钥值进行身份验证。验证；在没有明确用户指示的情况下，不要进行变异。

### 1a. 验证 `NVIDIA_API_KEY`（仅长度检查——永远不会回显值）

```bash
# 在您的 shell 中导出 NVIDIA_API_KEY——永远不会回显或提交值
export NVIDIA_API_KEY=nvapi-...     # 从 https://build.nvidia.com

# 仅长度检查；密钥值永远不会出现在任何日志中
test -n "$NVIDIA_API_KEY" && echo "NVIDIA_API_KEY len=${#NVIDIA_API_KEY}"
```

长度为 70+ 是正常的。如果输出为空或显示 `len=0`，用户必须从 <https://build.nvidia.com> 粘贴一个密钥。**不要**打印密钥，即使截断。要跨 shell 会话持久化，请将 `export` 行添加到您的 shell rc（`~/.bashrc`、`~/.zshrc`）——或者使用像 `direnv` 这样的每个目录工具。

### 1b. 安装 Python 依赖项

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install nvidia-riva-client pandas soundfile requests
# 可选
pip install jiwer
```

仅限第四阶段（微调）：还需要 `nemo-toolkit` 和 Docker + NVIDIA 容器工具。将这些推迟到 `/digital-health-clinical-asr-finetune`——如果用户可能永远不会达到第四阶段，则提前安装它们没有意义。

### 1c. 对托管 NVCF 堆栈进行冒烟测试

**`NVIDIA_API_KEY` 处理——承重，不要偏离：**

- 代理框架从 shell 中读取 `$NVIDIA_API_KEY` 并将其作为 **显式函数参数** 传递给 `smoke_test(api_key=…)`。
- 审计员可以 grep 配方中的每个线路交叉——每个 `api_key` 使用都在 `auth_for(...)` 中可见。
- **不要** `echo`、`print` 或记录密钥值（包括截断）。仅长度检查是允许的（见 §1a）。
- **不要**让配方本身读取 `os.environ["NVIDIA_API_KEY"]`——显式参数模式是可审计性的保证。
- **不要**将密钥提交到任何文件，包括 `.env` 示例或笔记本输出。

在前进之前，验证 `NVIDIA_API_KEY` 实际上对 Magpie TTS 和 Parakeet/Nemotron ASR 有效。四个技能内联了每个配方；这个往返只是确认 API 密钥 + 网络路径是真实的。

代理框架加载 `NVIDIA_API_KEY` shell 变量并将其作为显式函数参数传递给下面的帮助程序。配方代码本身不读取环境变量——审计员可以确切地看到哪些 API 密钥跨越线路。

```python
import wave, tempfile
import riva.client

NVCF_HOST = "grpc.nvcf.nvidia.com:443"
MAGPIE_FUNCTION_ID    = "877104f7-e885-42b9-8de8-f6e4c6303969"   # Magpie TTS
PARAKEET_FUNCTION_ID  = "d3fe9151-442b-4204-a70d-5fcc597fd610"   # Parakeet TDT 0.6B v2 (离线 ASR)

def auth_for(function_id: str, api_key: str) -> riva.client.Auth:
    return riva.client.Auth(
        use_ssl=True, uri=NVCF_HOST,
        metadata_args=[
            ["function-id", function_id],
            ["authorization", f"Bearer {api_key}"],
        ],
    )

def smoke_test(api_key: str) -> str:
    """调用者传递 api_key（代理框架在 shell 中读取 $NVIDIA_API_KEY；
    此代码永远不会触及环境）。返回 ASR 转录。"""

    # 1. TTS: "The patient was prescribed cefazolin."
    tts = riva.client.SpeechSynthesisService(auth_for(MAGPIE_FUNCTION_ID, api_key))
    pcm = b"".join(c.audio for c in tts.synthesize_online(
        text="The patient was prescribed cefazolin.",
        voice_name="Magpie-Multilingual.EN-US.Mia",
        language_code="en-US", sample_rate_hz=16000,
    ))
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(pcm)
        wav_path = f.name

    # 2. ASR: 转录我们刚刚合成的 WAV。
    asr = riva.client.ASRService(auth_for(PARAKEET_FUNCTION_ID, api_key))
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()
    config = riva.client.RecognitionConfig(
        encoding=riva.client.AudioEncoding.LINEAR_PCM,
        sample_rate_hertz=16000, language_code="en-US",
        max_alternatives=1, enable_automatic_punctuation=True,
    )
    response = asr.offline_recognize(audio_bytes, config)
    transcript = response.results[0].alternatives[0].transcript if response.results else ""
    print(f"TTS:  The patient was prescribed cefazolin.")
    print(f"ASR:  {transcript}")
    return transcript

# 从代理调用（api_key 由框架提供，不是由此代码提供）：
# smoke_test(api_key="<NVIDIA_API_KEY value>")
```

**运行冒烟测试——不要推迟它。** 这是证明第二阶段至第四阶段可以到达托管堆栈并使用用户当前密钥的门禁。 “我可以稍后运行它”不是第一阶段完成的可接受方式；要么现在调用 `smoke_test(api_key=…)`，要么如果用户明确选择退出，请在关闭摘要中记录延迟，以便他们知道他们缺少什么。

如果转录与输入在 ~1 个标记内匹配，则托管堆栈是可访问的，用户可以进入第二阶段。如果任何调用失败：

- `401 Unauthorized` / `PERMISSION_DENIED` → `NVIDIA_API_KEY` 是错误的、过期的或在此 shell 中未导出。重新导出并重新测试。
- `404` / `INVALID_ARGUMENT: function not found` → 功能 ID 已过时。在 <https://build.nvidia.com> 查找当前 ID 并更新上面的常量。
- `RESOURCE_EXHAUSTED` → NVCF 速率限制。30 秒后重试；在负载下这是正常的。
- 网络/TLS 错误 → 企业代理或 DNS 问题。首先测试 `curl https://build.nvidia.com`。

### 1d. （可选）验证 Merriam-Webster 查找

两条路径在第二阶段产生一个带有 `merriam-webster`-标记的清单行。选择一个（或两个都不选——Magpie G2P 回退是一个有效的立场）：

- **路径 A — JSON API + 密钥。** 推荐用于此技能的独立使用。检查密钥是否设置：

  ```bash
  test -n "$DICTIONARY_API_KEY" && echo "DICTIONARY_API_KEY len=${#DICTIONARY_API_KEY}" \
    || echo "DICTIONARY_API_KEY not set — Path A is off"
  ```

  免费密钥立即在 <https://dictionaryapi.com> 上出现问题。

- **路径 B — HTML 抓取。** 无需 API 密钥；可达性是唯一前提条件。对 MW 网站HTML更改易碎；构建技能的 `references/pronunciation-pipeline.md` 中内联了配方。

  ```bash
  curl -fsS -o /dev/null -w "merriam-webster.com reachable, HTTP %{http_code}\n" \
    https://www.merriam-webster.com/medical/cefazolin
  ```

  如果您不想维护一个抓取器，请使用路径 A 代替。

记住顶部的数据披露注释：在任一路径下，您种子列表中的每个临床术语都会作为 HTTP 请求发送到 Merriam-Webster 端点。

## 示例

**全新的 shell，以前从未运行过。** 用户说类似“我想开始飞轮”的话 → 首先引用披露表格，然后按顺序逐步完成 1a → 1b → 1c。在绿色的冒烟测试后，将他们指向 `/digital-health-clinical-asr-build` 并明确指出 KER 是第三阶段将用来评估他们的指标。

**返回用户，环境已准备就绪。** 用户说“我已经有了环境，只是确认我准备好了”。→ 跳过 venv + `pip install`（1b）。仅运行长度检查（1a）和冒烟测试（1c）。绿色通过后继续。

## 生成的工件

- 在用户的 shell 中导出的 `NVIDIA_API_KEY`
- 一个已激活的虚拟环境，包含 `nvidia-riva-client`、`pandas`、`soundfile`、`requests`
- 在一个临床句子上的 TTS→ASR 往返确认（证明托管堆栈工作）

在此阶段不生成任何清单、音频或模型工件——那些将在第二阶段至第四阶段生成。

## 故障排除

- **长度检查显示为空或 `len=0`** → `NVIDIA_API_KEY` 在此 shell 中未导出。运行 `export NVIDIA_API_KEY=nvapi-...` 并重新检查。
- **变量在一个 shell 中设置但在另一个 shell 中未设置** → 导出不会跨会话持久化。将 `export` 行添加到您的 shell rc（`~/.bashrc`、`~/.zshrc`），或者使用像 `direnv` 这样的每个目录加载器。
- **冒烟测试出现 `401 Unauthorized`** → 密钥值错误或过期。在 <https://build.nvidia.com> 重新签发。
- **`grpc.RpcError: function not found`** → 内联功能 ID 需要针对当前的 NVCF 目录进行更新。在 <https://build.nvidia.com> 检查，并编辑 1c 中的常量。评估技能（`/digital-health-clinical-asr-eval`）在其第三阶段 a “其他目录选项”列表中提供了当前功能 ID 的目录。
- **`StatusCode.INVALID_ARGUMENT` 与 `CUDA error: an illegal memory access was encountered`** → NVCF 端的特定功能 ID 后端故障（Triton/PyTorch 在 NVCF 上，不是您的环境）。要么稍后重试，要么临时指向另一个离线 ASR NIM——Whisper Large v3 功能 ID `b702f636-f60c-4a3d-a6f4-f3568c13bd7d` 是最接近的即插即用（也是离线的；将 `language_code="en"` 替换为 `"en-US"`）。对于常规评估周期，最好等待 Parakeet 后端恢复，以便第三阶段基线和第四阶段 SFT 基线保持一致。
- **`TypeError: Auth.__init__() got an unexpected keyword argument 'ssl_cert'`** → 您正在使用 `nvidia-riva-client >= 2.x`，其中参数名称已更改为 `ssl_root_cert`（并且不再需要用于托管 NVCF）。从您本地配方副本中删除 `ssl_cert=None,` 行。
- **`ModuleNotFoundError: riva.client`** → 步骤 1b 被跳过或未激活虚拟环境。`source .venv/bin/activate && pip install nvidia-riva-client`。

## 限制

- **范围仅限于环境就绪检查。** 用户术语列表或发音覆盖是否合理是在 `/digital-health-clinical-asr-build` 中决定的，而不是在这里。
- **Magpie en-US 假设。** 下游 IPA 验证依赖于 Magpie 的英语音素库存；其他地区需要完全不同的音素集。
- **假设托管 NVCF 是部署。** 运行自托管 Riva NIMs 是可能的，但该设置位于 `/digital-health-clinical-asr-finetune` 第四阶段 d 中。
- **仅合成数据。** 此技能系列是为从编辑的术语列表生成的基准测试而构建的。真实患者转录和录制的音频不得通过任何阶段。

## 下一步

**成功时强制关闭：** 完成第一阶段响应，通过**明确指向 `/digital-health-clinical-asr-build`** 并**命名 KER（关键词错误率）作为标题指标**，他们将在第三阶段看到。两个指针都是必需的，不是可选的——它们将用户置于四阶段飞轮中。

- **默认前进路线：** `/digital-health-clinical-asr-build` — 专业访谈、术语管理、IPA 标记、NeMo 清单合成。
- **直接跳至第三阶段**（仅当用户正在带来他们自己的 NeMo 格式清单，带有 `term` / `entity_category` / `ipa_source` 字段时）：`/digital-health-clinical-asr-eval`。

## 参考

- [`references/dependency-ownership.md`](references/dependency-ownership.md) — 技能拥有的边界与同伴拥有的责任。
