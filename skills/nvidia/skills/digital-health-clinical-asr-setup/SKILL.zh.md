---
name: digital-health-clinical-asr-setup
description: 临床 ASR 飞轮的第一阶段。在启动一个周期时使用：NVCF+MW 公开，NVIDIA_API_KEY 检查，依赖项安装，TTS+ASR 烟雾测试。
---

<!-- 
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# 临床语音识别飞轮 — 第一阶段（设置）

> **代理：此文件是第一阶段完整流程。** 不要调用 `find`、`ls`、`rg` 或 `grep` 寻找安装程序或隐藏配置——没有这些。下文中的四个部分（外发数据披露、编号检查、兄弟程序交接）都是必读内容；不要跳过任何部分。功能 ID、环境变量约定和冒烟测试门禁将在下文内联——从实际写入的内容中回答，而不是从先前的 Riva/NVCF 熟悉度中回答。

第一阶段只有一个任务：证明用户可以使用他们当前持有的 `NVIDIA_API_KEY` 连接到 NVIDIA 托管的语音堆栈。一旦单个临床句子通过 Magpie TTS → Parakeet/Nemotron ASR 成功往返，用户就获得权限进入 `/digital-health-clinical-asr-build`。

四阶段飞轮的存在是为了降低**关键词错误率 (KER)** 在临床实体上——药物、程序、解剖结构、病症、实验室检查、角色。WER 平均值会掩盖对临床有影响的失败；KER 是第三阶段将用来评估你的指标。

在这个技能的任何地方都没有**安装脚本**——不是 `install.sh`，不是 `setup.py`，什么都没有隐藏。第一阶段 *就是* 下面的三个步骤：验证密钥、安装 Python 依赖项、运行冒烟测试。第一阶段之后的所有内容都由兄弟技能 (`/data-designer`、`/riva-tts`、内联的第三阶段 ASR 配方、`/riva-asr-custom`) 组成。如果用户问“什么脚本安装所有内容？”，请从本段落回答；不要去搜索。

## 外发数据流——在发送任何文本或音频之前进行披露

在这个飞轮期间，有两个外部端点接收数据。用户必须在第二阶段开始之前确认这两个端点，以符合其组织强制执行的数据治理政策。**在您的回复中逐字渲染下表——释义不满足披露要求；字面表述才是关键。**

| 服务 | 发送的内容 | 时间 | 托管方 |
|---|---|---|---|
| **NVIDIA NVCF** (`grpc.nvcf.nvidia.com`) | 您合成的临床句子（文本），以及您转录的 WAV 文件（音频） | 每个第二阶段 TTS 调用和每个第三阶段 ASR 调用 | NVIDIA，受 build.nvidia.com 条款约束 |
| **Merriam-Webster** (`dictionaryapi.com` JSON API **或** 公开的 `merriam-webster.com` HTML 网站) | 单个临床术语（药物名称、解剖结构、程序），每个术语一个 HTTP 请求 | 第二阶段 IPA 标记——见下文“两条 MW 路径”以确定适用端点 | Merriam-Webster，受其 API 或网站条款约束 |

数据是**按设计合成的**——飞轮根据用户管理的术语列表制造句子和音频，永远不会从真实的患者就诊中获取。话虽如此：**不要通过任何阶段传输真实的患者转录文本、录制的临床音频或任何受保护的健康信息 (PHI)。** 如果术语列表本身包含敏感材料（代号药物、未发布的 产品名称），用户应在继续之前咨询其组织的外部 API 政策。可以关闭任一端点：

- **完全跳过 Merriam-Webster：** 设置 `DICTIONARY_API_KEY` 为空，并且不运行爬虫。第二阶段会回退到 Magpie G2P，这仍然有效，但对长尾临床术语的覆盖范围较弱。
- **跳过 NVCF：** 这是一个硬停止。Magpie TTS + Parakeet/Nemotron ASR *是* 工作负载；没有它们，这个技能系列是错误的工具——您需要的是自托管的 ASR/TTS 管道。

建议将此通知副本放置在用户的 `README.md` 工作区中；如果它尚未存在，请在第一次调用时将其提前。

## 目的

为第二阶段准备一个新鲜的环境。确认三件事：密钥存在、依赖项可以顺利导入、托管堆栈确实可以响应。以命名下一个要运行的技能结束。

四个 `digital-health-clinical-asr-*` 技能是**自包含的**——每个 TTS、ASR、IPA 标记和评分配方都包含在其中；运行飞轮端到端不需要安装其他代理技能。

此技能对工作区布局不持任何意见。用户决定他们的周期工件存放位置；`data/eval_sets/cycle<N>/` 不会被强加。

## 何时使用此技能

在以下用户短语激活时：

- "设置临床语音识别飞轮"
- "初始化临床-asr 评估"
- "我想对临床术语的 ASR 进行评估——我从哪里开始？"
- "为飞轮引导我的环境"
- "在运行飞轮之前我需要安装什么？"

**不要** 在以下情况下激活：

- 用户已经有一个清单并想对其进行评分 → `/digital-health-clinical-asr-eval`
- 用户已经设置好环境并想管理术语 → `/digital-health-clinical-asr-build`
- 用户正在询问关于第四阶段 NGC/Docker 设置的特定内容 → 那些内容在 `/digital-health-clinical-asr-finetune` 内部涵盖

## 前提条件

| 要求 | 是否必需 | 原因 | 如何 |
|---|---|---|---|
| `NVIDIA_API_KEY` (`nvapi-…`) | **必需** | 通过 NVCF 托管 Magpie TTS + Parakeet/Nemotron ASR | 在 <https://build.nvidia.com> 上申请；在 shell 中运行 `export NVIDIA_API_KEY=...` |
| Python ≥ 3.10 | **必需** | NeMo 客户端、评分、清单工具 | 运行 `python3 --version` |
| `nvidia-riva-client`、`pandas`、`soundfile`、`requests` | **必需** | TTS + ASR 客户端、清单 I/O、MW 查找 | 运行 `pip install nvidia-riva-client pandas soundfile requests` |
| `DICTIONARY_API_KEY` | 可选 | 通过 JSON API（构建技能中的路径 A，推荐）查找 Merriam-Webster 医学词典 | 在 <https://dictionaryapi.com> 上提供免费密钥。构建技能的 `references/pronunciation-pipeline.md` 中也记录了无 API 密钥的 HTML 抓取路径 B，如果无法获取密钥则使用。没有任一路径，第二阶段会回退到 Magpie G2P，对长尾临床术语的覆盖范围较弱。 |
| `jiwer` | 可选 | 与内联的 Levenshtein 实现进行参考 WER/CER 对比 | 运行 `pip install jiwer`——评估技能包含纯 Python 回退 |
| (仅第四阶段) `NGC_API_KEY` + CUDA 主机 + NeMo 容器 | 可选、延迟 | 微调工作负载 | 在 `/digital-health-clinical-asr-finetune` 内部设置；延迟到评估显示 KER > 0.3 |

## 说明

**范围。** 此技能执行**只读环境检查**：确认密钥已导出（仅长度检查）、Python 版本、库可以导入、托管 NVCF 堆栈对单个冒烟测试往返做出响应。它**不会**安装系统包、修改 shell rc 文件、在 `.venv/` 之外写入磁盘，或尝试使用真实的密钥值进行身份验证。验证；在没有明确用户指示的情况下，不要进行修改。

### 1a. 验证 `NVIDIA_API_KEY`（仅长度检查——永远不会显示值）

```bash
# 在您的 shell 中导出 NVIDIA_API_KEY——永远不会显示或提交值
export NVIDIA_API_KEY=nvapi-...     # 从 https://build.nvidia.com

# 仅长度检查；密钥值永远不会出现在任何日志中
test -n "$NVIDIA_API_KEY" && echo "NVIDIA_API_KEY len=${#NVIDIA_API_KEY}"
```

长度为 70+ 是正常的。如果输出为空或显示 `len=0`，用户必须从 <https://build.nvidia.com> 粘贴一个密钥。**不要** 打印密钥，即使截断。要跨 shell 会话持久化，请将 `export` 行添加到您的 shell rc (`~/.bashrc`、`~/.zshrc`)——或者使用像 `direnv` 这样的按目录工具。

### 1b. 安装 Python 依赖项

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install nvidia-riva-client pandas soundfile requests
# 可选
pip install jiwer
```

仅第四阶段（微调）需要：`nemo-toolkit` 和 Docker + NVIDIA 容器工具也是必需的。将这些延迟到 `/digital-health-clinical-asr-finetune`——如果用户可能永远不会达到第四阶段，提前安装它们没有意义。

### 1c. 冒烟测试托管 NVCF 堆栈

**`NVIDIA_API_KEY` 处理——承重关键，不要偏离：**

- 代理框架从 shell 读取 `$NVIDIA_API_KEY`，并将其作为显式函数参数传递给 `smoke_test(api_key=…)`.
- 审计员可以通过 `grep` 搜索配方中的每个数据传输——每个 `api_key` 使用都在 `auth_for(...)` 中可见。
- **不要** `echo`、`print` 或记录密钥值（包括截断）。仅长度检查是允许的（见 §1a）。
- **不要** 让配方读取 `os.environ["NVIDIA_API_KEY"]` 本身——显式参数模式是可审计性的保证。
- **不要** 将密钥提交到任何文件，包括 `.env` 示例或笔记本输出。

在进入下一阶段之前，验证 `NVIDIA_API_KEY` 实际上可以针对 Magpie TTS 和 Parakeet/Nemotron ASR 工作。四个技能内联了每个配方；这个往返只是确认 API 密钥 + 网络路径是真实的。

代理框架加载 `NVIDIA_API_KEY` shell 变量，并将其作为显式函数参数传递给下方的辅助程序。配方代码本身不会读取环境变量——审计员可以确切地看到哪些 API 密钥跨过数据线。

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
    此代码永远不会触及环境）。返回 ASR 转录文本。"""

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

    # 2. ASR: 转录我们刚刚合成的 WAV 文件。
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

# 从代理调用（api_key 由框架提供，不是此代码）：
# smoke_test(api_key="<NVIDIA_API_KEY value>")
```

**运行冒烟测试——不要延迟它。** 这是证明第二阶段至第四阶段可以携带用户的当前密钥到达托管堆栈的门禁。 “我可以稍后运行它” 不是第一阶段完成的可接受结果；要么现在调用 `smoke_test(api_key=…)`，要么如果用户明确选择退出，请在关闭摘要中记录延迟，以便他们知道他们缺少什么。

如果转录文本与输入在 ~1 个 token 内匹配，则托管堆栈是可访问的，用户可以进入第二阶段。如果任何调用失败：

- `401 Unauthorized` / `PERMISSION_DENIED` → `NVIDIA_API_KEY` 错误、过期或在此 shell 中未导出。重新导出并重新测试。
- `404` / `INVALID_ARGUMENT: function not found` → 功能 ID 已过时。在 <https://build.nvidia.com> 上查找当前 ID 并更新上面的常量。
- `RESOURCE_EXHAUSTED` → NVCF 速率限制。30 秒后重试；在负载下这是正常的。
- 网络/TLS 错误 → 企业代理或 DNS 问题。首先测试 `curl https://build.nvidia.com`。

### 1d. （可选）验证 Merriam-Webster 查找

两条路径会在第二阶段生成一个带有 `merriam-webster` 标签的清单行。选择一条（或两条都不选——Magpie G2P 回退是一个有效的立场）：

- **路径 A — JSON API + 密钥。** 推荐用于此技能的独立使用。检查密钥是否设置：

  ```bash
  test -n "$DICTIONARY_API_KEY" && echo "DICTIONARY_API_KEY len=${#DICTIONARY_API_KEY}" \
    || echo "DICTIONARY_API_KEY 未设置——路径 A 已关闭"
  ```

  免费密钥立即在 <https://dictionaryapi.com> 上出现问题。

- **路径 B — HTML 抓取。** 无需 API 密钥；唯一先决条件是可达性。对 MW 网站HTML更改很脆弱；构建技能的 `references/pronunciation-pipeline.md` 中也记录了此配方（如果无法获取密钥）。

  ```bash
  curl -fsS -o /dev/null -w "merriam-webster.com 可达，HTTP %{http_code}\n" \
    https://www.merriam-webster.com/medical/cefazolin
  ```

  如果您不想维护爬虫，请改用路径 A。

记住顶部的披露说明：在任一路径下，您种子列表中的每个临床术语都会作为 HTTP 请求发送到 Merriam-Webster 端点。

## 示例

**全新的 shell，以前从未运行过。** 用户说类似“我想开始飞轮”的话 → 首先引用披露表格，然后按顺序执行 1a → 1b → 1c。在绿色的冒烟测试后，将他们指向 `/digital-health-clinical-asr-build` 并明确指出 KER 是第三阶段将用来评估他们的指标。

**返回用户，环境已准备就绪。** 用户说“我已经有环境了，确认我可以开始”。→ 跳过 venv + `pip install`（1b）。仅运行长度检查（1a）和冒烟测试（1c）。绿色通过后，继续前进。

## 生成的工件

- 在用户的 shell 中导出的 `NVIDIA_API_KEY`
- 一个已激活的虚拟环境，包含 `nvidia-riva-client`、`pandas`、`soundfile`、`requests`
- 在临床句子上的 TTS→ASR 往返确认（证明托管堆栈可以工作）

在此阶段不会生成任何清单、音频或模型工件——那些会在第二阶段至第四阶段生成。

## 故障排除

- **长度检查显示为空或 `len=0`** → 此 shell 中未导出 `NVIDIA_API_KEY`。运行 `export NVIDIA_API_KEY=nvapi-...` 并重新检查。
- **在一个 shell 中设置变量，在另一个 shell 中未设置** → 导出不会跨会话持久化。将 `export` 行添加到您的 shell rc (`~/.bashrc`、`~/.zshrc`)，或者使用像 `direnv` 这样的按目录加载工具。
- **冒烟测试出现 `401 Unauthorized`** → 密钥值错误或过期。在 <https://build.nvidia.com> 上重新申请。
- **`grpc.RpcError: function not found`** → 内联功能 ID 需要针对当前的 NVCF 目录进行更新。检查 <https://build.nvidia.com> 并编辑 1c 中的常量。评估技能 (`/digital-health-clinical-asr-eval`) 在其 Step 3a “其他目录选项”列表中提供了当前功能 ID 的目录。
- **`StatusCode.INVALID_ARGUMENT` 与 `CUDA error: an illegal memory access was encountered`** → NVCF 端的特定功能 ID 后端故障（Triton/PyTorch 在 NVCF 上，不是您的环境）。要么稍后重试，要么临时指向另一个离线 ASR NIM——Whisper Large v3 功能 ID `b702f636-f60c-4a3d-a6f4-f3568c13bd7d` 是最接近的即插即用（也是离线的；将 `language_code="en"` 替换为 `"en-US"`）。对于常规评估周期，最好等待 Parakeet 后端恢复，以便第三阶段的基线和第四阶段 SFT 基线保持一致。
- **`TypeError: Auth.__init__() got an unexpected keyword argument 'ssl_cert'`** → 您使用的是 `nvidia-riva-client >= 2.x`，其中参数名称已更改为 `ssl_root_cert`（并且不再需要用于托管 NVCF）。从您本地复制的配方中删除 `ssl_cert=None,` 行。
- **`ModuleNotFoundError: riva.client`** → 跳过了步骤 1b 或未激活虚拟环境。`source .venv/bin/activate && pip install nvidia-riva-client`。

- **范围仅限于环境就绪。** 用户术语列表或发音覆盖是否合理，由 `/digital-health-clinical-asr-build` 决定，而不是在这里。
- **假设为 Magpie en-US。** 下游的 IPA 验证依赖于 Magpie 的英语音素库；其他地区需要完全不同的音素集。
- **假设为托管的 NVCF 部署。** 运行自托管 Riva NIMs 是可能的，但该设置的配置位于 `/digital-health-clinical-asr-finetune` 阶段 4d 内。
- **仅限合成数据。** 此技能系列是为从精选术语列表生成的基准测试而构建的。真实患者转录和录制音频不得在任何阶段中流转。

## 下一步

**成功后必须强制关闭：** 完成 Stage 1 响应，**明确将用户指向 `/digital-health-clinical-asr-build`** 并**将 KER（关键词错误率）命名为他们在 Stage 3 中看到的标题指标**。两个指向都是必需的，不是可选的——它们将用户置于四阶段飞轮内。

- **默认正向路由：`/digital-health-clinical-asr-build`** — 专业访谈、术语整理、IPA 标注、NeMo 元数据合成。
- **直接跳转到 Stage 3**（仅当用户携带自己的 NeMo 格式元数据，包含 `term` / `entity_category` / `ipa_source` 字段时）：`/digital-health-clinical-asr-eval`。

## 参考

- [`references/dependency-ownership.md`](references/dependency-ownership.md) — 技能拥有和伴生拥有责任之间的边界。
