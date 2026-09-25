# NV-Reason-CXR

## 目的
- 用于命令形状或实时 NV-Reason-CXR 胸部 X 光推理烟雾测试。不用于诊断或临床报告。
- 精确按照文档使用包装器；不要用手工编写的实现替换上游入口点。
- 配置文件 I/O：输入是 `chest_xray_image_or_fixture`；输出是 `result_json`。

## 说明
- 修改参数、副作用或验证门之前，请先阅读 `skill_manifest.yaml`。
- 通过以下文档中记录的命令运行 `scripts/run_nv_reason_cxr.py`；仅当生成固定装置或 harness 管理的工件目录时，才传递 `--out-dir`。
- 如果主机代理暴露 `run_script`，请使用 `run_script("scripts/run_nv_reason_cxr.py", args=[...])`；否则运行以下显示的 Bash/Python 命令。
- 在将运行视为证据之前，请检查发出的 JSON 和配对的验证器指导。
- 当报告完成的运行时，返回完整的包装器 JSON 或至少完整的 `output.response_text`，其完全按发出方式呈现，包括任何模型生成的 `<think>...</think>` 和 `<answer>...</answer>` 部分。除非用户明确要求摘要，否则不要将结果折叠为标签。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_nv_reason_cxr.py` | 由 skill_manifest.yaml 声明的首选入口点。 | `PATH_TO_CXR_OR_FIXTURE [--out-dir OUT_DIR] [--backend local\|hf-space-api] [--mock] [--check-setup]` |

## 前置条件
- 本地后端要求：当配置文件声明时需要 GPU/CUDA；Python 包列在 `runtime.side_effects.pip_packages` 中。
- API 后端要求：需要公共网络访问 [Hugging Face Space](https://huggingface.co/spaces/nvidia/nv-reason-cxr)；不需要本地 PyTorch、Transformers、CUDA、模型缓存或 Hugging Face 令牌。
- 副作用：在 stdout 上发出结果 JSON；可能会在调用者的 `--out-dir` 下写入生成的固定装置工件；可能会在 `~/.cache/huggingface/` 下缓存模型资产以进行本地推理；并且可能在 `--mock` 模式外联系 `https://huggingface.co`、`https://github.com` 或 `https://*.hf.space`。
- 从存储库根目录运行命令，除非以下现有部分另有说明。

## 限制
- 这是一个薄的包装器。图像预处理、模型推理和解码委托给 Hugging Face Transformers 和 NV-Reason-CXR-3B 模型。
- 输出不是诊断、临床报告、治疗建议或分诊决策。它是工程证据，在医疗用途之前必须由合格的专业人士审查。
- 模型可能会产生幻觉的发现、遗漏微妙的异常、误读支持设备或产生过度自信的文本。
- 已提交的固定装置使用生成的合成 PNG 和确定性模拟响应，以便 CI 可以在不下载模型权重的情况下验证包装器行为。模拟模式不能替代模型推理。
- `hf-space-api` 后端依赖于公共 Hugging Face Space 的可用性和 API 兼容性。
- 不用于临床部署、临床解释、自主诊断、治疗决策。

## 故障排除
| 错误 | 原因 | 修复 |
|---|---|---|
| 缺少依赖项或导入错误 | 从 `skill_manifest.yaml` 出现的运行时包漂移。 | 安装配置文件中声明的包或使用记录的设置命令。 |
| 从代理中不可用 CUDA，但在用户终端可用 | 代理沙盒、容器或作业包装器可能即使相同的 Python 环境中安装了 CUDA 能力的 PyTorch 也可能不暴露 NVIDIA 设备节点。 | 在代理上下文和用户终端中比较 `python -c "import torch; print(torch.cuda.is_available())"` 和 `nvidia-smi`。如果只有代理上下文失败，请重新运行以使用 GPU/设备访问，使用主机终端，或仅对于显式慢速 CPU 测试传递 `--device cpu --allow-cpu`。 |
| API 后端 HTTP 或架构错误 | 公共 Hugging Face Space 可能不可用、速率限制或已更改。 | 重新运行或当本地依赖项和 CUDA 可用时使用 `--backend local`。 |
| 空的或架构无效的输出 | 错误的输入路径、不支持的模态或上游失败。 | 使用已知固定装置重新运行并检查包装器 JSON 和 stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包并使用门消息来修复输入或包装器代码。 |

运行 NVIDIA-Medtech [`NV-Reason-CXR-3B`](https://github.com/NVIDIA-Medtech/NV-Reason-CXR/tree/83a4d51c9fbbff68156a5f01796f04e26519b6ad)
用于胸部 X 光图像解释，通过记录的本地 Hugging Face Transformers 推理路径或公共 Hugging Face Space API。
包装器不会重新实现模型、图像预处理或解码。

## 精确可运行表面

对于命令形状烟雾测试和 JSON 固定装置，请精确使用此存储库根目录包装器路径：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR_OR_FIXTURE --mock --out-dir OUT_DIR
```

对于本地实时图像推理，仅当用户要求实时模型推理时才省略 `--mock`。本地是默认后端：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR_OR_FIXTURE \
  --prompt "Find abnormalities and support devices." \
  --backend local
```

对于没有本地模型包的公共 API 推理，使用：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR_OR_FIXTURE \
  --prompt "Find abnormalities and support devices." \
  --backend hf-space-api
```

不要为普通用户运行发明 `Medical AI Skills run`、`eval_engine/run.py`、`infer.py` 或 `python -m nv_reason_cxr` 命令。

## 前提条件

对于 `--backend local`，在将运行技能的环境安装推理依赖项：

```bash
pip install torch==2.7.1 torchvision==0.22.1 transformers==4.56.1 Pillow
```

模型权重和远程模型代码通过 Transformers 从 `nvidia/NV-Reason-CXR-3B` 版本
`056bd0383b35226554da9dc5866e095df174ae19` 加载。它们可能在首次使用时下载到 Hugging Face 缓存。
仅在权重已经缓存后设置 `TRANSFORMERS_OFFLINE=1` 或传递 `--local-files-only`。

期望 CUDA 以进行实际推理。CPU 执行可能适用于小测试，但很慢，必须明确请求。

对于 `--backend hf-space-api`，不需要本地 PyTorch、Transformers、CUDA、模型缓存或 Hugging Face 令牌。后端将图像和提示发送到公共 `nvidia/nv-reason-cxr` Hugging Face Space。

在下载权重或运行推理之前检查本地环境：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py --check-setup
```

设置报告检查可导入的依赖项、CUDA 可见性、Hugging Face 缓存状态和建议的下一步。

操作环境变量：

| 变量 | 使用时机 |
|---|---|
| `MOCK_NV_REASON_CXR` | 设置为 `1` 以进行确定性命令形状烟雾测试，而无需模型推理。 |
| `NV_REASON_CXR_MODEL` | 仅用于兼容性探测时覆盖 Hugging Face 模型 ID。 |
| `HF_HOME` | 指向预填充的 Hugging Face 缓存。 |
| `HF_TOKEN` | 仅当本地环境需要时才用于本地模型下载；公共 API 后端不需要。 |
| `TRANSFORMERS_OFFLINE` | 仅在权重已经缓存后设置为 `1`。 |
| `HF_HUB_OFFLINE` | 仅在 Hugging Face 资产已经缓存后设置为 `1`。 |

## 提示路由

在运行包装器之前选择模型提示和面向用户的输出模式。路由顺序很重要：精确的模型提示请求首先使用传递/原始仅模式；否则报告生成请求优先于一般分析和特定问题路由。

仅当用户明确要求将精确提示发送到模型时（例如，“使用此提示精确调用模型：...”）使用传递/原始仅模式。仅传递该精确的模型提示作为 `--prompt`。

当用户要求分析、检查或找到胸部 X 光中的异常时，使用异常分析模式。将本地图像路径、上传的文件名、后端选择（例如“使用 API”或“使用本地”）、输出交付说明和其他代理编排文本视为包装器指令，而不是模型提示内容。除非用户明确要求将确切文本发送到模型，否则不要在 `--prompt` 中包含本地文件系统路径、后端名称或“使用 API”。对于普通的异常查找请求，使用记录的提示，通常是 `--prompt "Find abnormalities and support devices."`，以及请求的后端。

如果用户要求编写、创建或生成结构化报告、胸部 X 光报告、放射学报告或报告，请使用报告生成/两调用模式。如果已经具有足够的原始模型上下文用于相同图像，特别是来自 `Find abnormalities and support devices.` 的输出，则跳过上下文收集调用。否则，首先使用 `--prompt "Examine the chest X-ray."` 运行包装器以收集上下文，但不要显示第一个调用。然后再次运行包装器，使用多轮会话提示：

```text
User: Find abnormalities and support devices.

Assistant:
<raw model context>

User: Write a structured report.
```

将第二个调用视为完成的运行。

当用户询问关于发现的特定问题，例如存在、数量、位置或特征化，或混合一般分析与特定问题时，使用默认提示/上下文答案模式。使用 `--prompt "Find abnormalities and support devices."` 运行包装器，然后在纯文本前缀 `Answer:` 中回答原始问题。仅基于原始模型输出上下文和图像。

## 跟进处理

对于对话中已经分析的图像的后续问题，当它足够时重用先前的原始模型上下文。对于报告后续问题，使用报告生成/两调用模式，如果存在足够的上下文，则直接跳到第二个模型调用。如果先前的上下文不足，并且相同的图像路径或图像字节可用，请使用上述提示路由规则再次调用包装器。如果图像不再可用，请要求用户重新附加它。

对于包含先前的原始模型输出的长多轮提示，请优先使用引号 Bash here-doc 变量，以便保留 XML 类似标签、撇号、引号和换行符：

```bash
IFS= read -r -d '' prompt <<'PROMPT'
User: Examine the chest X-ray.

Assistant:
<raw model context>

User: Write a structured report.
PROMPT

python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR.png \
  --prompt "$prompt" \
  --backend hf-space-api
```

使用 `IFS= read -r -d '' prompt <<'PROMPT'`，而不是命令替换，用于长粘贴的会话。

## 许可证

上游存储库代码是 Apache-2.0。模型权重根据 NVIDIA OneWay 非商业许可证协议发布。用户在使用实时推理之前必须遵守模型权重条款。

## 用法

从 Medical AI Skills 存储库根目录：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR.png \
  --prompt "Find abnormalities and support devices." \
  --backend local
```

对于没有在本地安装模型包的公共 API 推理：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR.png \
  --prompt "Find abnormalities and support devices." \
  --backend hf-space-api
```

对于包含本地路径或后端指令的用户请求，请将这些指令从模型提示中排除：

```text
User request: find abnormalities in ~/Desktop/363.jpg (use API)
```

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py ~/Desktop/363.jpg \
  --prompt "Find abnormalities and support devices." \
  --backend hf-space-api
```

直接使用包装器脚本对于代理生成的命令。除非用户明确要求运行 eval harness，否则不要用 `eval_engine/run.py` 替换它。不要在生成的命令中使用 `>` 重定向 stdout：调用者和 eval harness 读取包装器 stdout JSON 以验证运行。直接可运行表面是：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR_OR_FIXTURE \
  --mock \
  --out-dir runs/nv_reason_cxr_case
```

`PATH_TO_CXR_OR_FIXTURE` 可以是 PNG/JPEG 图像或 JSON 固定装置。如果用户提供 JSON 请求，例如
`runs/.../synthetic_cxr_input.json`，请传递该确切 JSON 路径作为第一个参数。脚本将加载 `generated://synthetic_chest_xray` 固定装置，在输出目录下创建临时 PNG，并发出带有模型响应的 JSON。仅对于命令形状烟雾测试或请求模拟模式的固定装置使用 `--mock`；对于实时模型推理省略 `--mock`。

对于 JPEG 输入：

```bash
python skills/nv-reason-cxr/scripts/run_nv_reason_cxr.py PATH_TO_CXR.jpg \
  --prompt "Describe the chest X-ray findings." \
  --backend local
```

标志：

- `--backend local|hf-space-api` — 推理后端，默认 `local`。
- `--model-id` — Hugging Face 模型 ID，默认 `nvidia/NV-Reason-CXR-3B`。
- `--device auto|cuda|cpu` — 默认 `auto`，在可用时使用 CUDA。
- `--allow-cpu` — 对于实时 CPU 推理是必需的；CPU 运行可能非常慢。
- `--torch-dtype auto|float16|bfloat16|float32` — 默认 `auto`，在 CUDA 上使用 bfloat16，在 CPU 上使用 float32，匹配发布的 BF16 模型。
- `--max-new-tokens` — 生成限制，默认 2048。
- `--local-files-only` — 仅使用本地缓存的 Hugging Face 资产。
- `--mock` — 确定性干运行响应，用于 CI 和接线检查。
- `--prompt-preset findings|comprehensive|educational|structured` — 可选的已知良好提示预设，来自模型卡/演示行为。
- `--out-dir` — 可选的工件目录。对于生成的 JSON 固定装置是必需的；eval harness 明确传递它。

测试的本地实时路径使用：

- `AutoModelForImageTextToText.from_pretrained(..., dtype=torch.bfloat16).eval().to("cuda")`
- `AutoProcessor.from_pretrained(..., use_fast=True)`
- PNG/JPEG 图像输入加上一个文本提示
- `max_new_tokens=2048` 默认

脚本在 stdout 上发出 JSON，并写入没有临床报告文件。直接 PNG/JPEG 运行不会创建默认输出目录。生成的 JSON 固定装置需要 `--out-dir` 用于临时合成图像。结果 JSON 记录输入图像元数据、提示、模型 ID、运行时模式、响应文本和已知限制。如果 `runtime.truncated_by_max_new_tokens` 是 `true`，请使用更高的 `--max-new-tokens` 值重新运行。

报告提醒：对于 `local` 和 `hf-space-api` 后端，请遵循说明中的完成运行规则。

`hf-space-api` 后端调用固定的公共 Hugging Face Space at
`https://nvidia-nv-reason-cxr.hf.space`，HTTP 超时时间为 300 秒。

## 固定装置烟雾测试

已提交的固定装置使用生成的合成 PNG 和模拟模式，以便 eval harness 可以在不下载权重的情况下验证包装器：

```bash
python eval_engine/run.py skills/nv-reason-cxr \
  --fixture skills/nv-reason-cxr/fixtures/synthetic_cxr_input.json \
  --out runs/nv_reason_cxr_smoke
```

## 限制

这只是研究和工程工具。它未经过临床诊断、治疗决策、分诊、面向患者的报告或监管使用的验证。模型输出可能会产生幻觉、遗漏微妙的发现或过度声明不确定性。合格的专业人士必须审查在医疗工作流程中的任何使用。
