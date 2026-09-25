# HuggingFace 最佳模型查找器

通过查询官方 HF 基准排行榜，根据任务查找最佳模型，并使用模型大小数据丰富结果，筛选出适合用户设备的模型，并返回包含基准分数的对比表格。

---

## 第 1 步：解析请求

从用户消息中提取：
- **任务**：用户希望模型执行的任务（编码、数学/推理、聊天、OCR、RAG/检索、语音识别、图像分类、多模态、代理等）
- **设备**：硬件限制（MacBook M系列 8/16/32/64GB 统一内存、带有 VRAM 的 RTX 显卡、仅 CPU、云/无限制等）

如果未提及设备，则完全跳过筛选，并返回最高性能的模型，无论大小如何。如果任务确实模糊不清，请提出一个澄清问题。

### 设备 → 最大参数预算

当指定设备时，提取其可用内存（Apple Silicon 的统一 RAM、独立 GPU 的 VRAM），并应用：

- **fp16 最大参数 (B)** ≈ 内存 (GB) ÷ 2
- **Q4 最大参数 (B)** ≈ 内存 (GB) × 2

示例：16GB → 8B fp16 / 32B Q4 — 24GB VRAM → 12B fp16 / 48B Q4 — 8GB → 4B fp16 / 16B Q4

---

## 第 2 步：查找相关基准数据集

获取官方 HF 基准数据集的完整列表：

```bash
curl -s -H "Authorization: Bearer $(cat ~/.cache/huggingface/token)" \
  "https://huggingface.co/api/datasets?filter=benchmark:official&limit=500" | jq '[.[] | {id, tags, description}]'
```

读取返回的列表，并选择与用户任务最相关的数据集——根据数据集 ID、标签和描述进行匹配。使用你的判断力；不要局限于 2-3 个。目标是全面覆盖：如果 5 个基准明确覆盖任务，则使用所有 5 个。

---

## 第 3 步：从排行榜获取顶级模型

对于每个选定的基准数据集：

```bash
curl -s -H "Authorization: Bearer $(cat ~/.cache/huggingface/token)" \
  "https://huggingface.co/api/datasets/<namespace>/<repo>/leaderboard" | jq '[.[:15] | .[] | {rank, modelId, value, verified}]'
```

收集所有基准中的模型 ID 和分数。如果排行榜返回错误（404、401 等），则跳过它并在输出中注明。

---

## 第 4 步：使用模型元数据丰富信息

对于前 10-15 个候选模型 ID，获取模型信息。

```bash
# REST API
curl -s -H "Authorization: Bearer $(cat ~/.cache/huggingface/token)" \
  "https://huggingface.co/api/models/org/model1" | jq '{safetensors, tags, cardData}'

# CLI (hf-cli)
hf models info org/model1 --json | jq '{safetensors, tags, cardData}'
```

从每个响应中提取：
- **参数**：`safetensors.total` → 转换为 B（例如，7_241_748_480 → "7.2B"）
- **许可证**：从模型卡片标签中获取（查找 `license:apache-2.0`、`license:mit` 等）
- 如果 `safetensors` 缺失，则从模型名称中解析大小（查找 "7b"、"8b"、"13b"、"70b"、"72b" 等）

---

## 第 5 步：筛选和排名

**如果指定了设备：**
1. 移除超出设备 fp16 参数预算的模型
2. 标记仅适用于 Q4 量化的模型（将预算乘以约 4 以获得 Q4 容量）
3. 如果一个高排名的模型略超预算，保留它并附上 "需要 Q4" 的注释——不要默默丢弃它

**如果未提及设备：** 跳过所有大小筛选——仅按基准分数排名。

然后：按基准分数（降序）排名，保留前 5-8 个模型。

如果排行榜上出现专有模型（GPT-4、Claude、Gemini），则包括它们，但标记为 "仅 API / 无法自托管"。如果用户明确要求仅本地/开源模型，则排除它们。

---

## 第 6 步：输出

### 对比表格

```markdown
| # | 模型 | 参数 | [基准 1] | [基准 2] | 许可证 | 设备上 |
|---|------|------|----------|----------|--------|--------|
| ⭐1 | [org/name](https://huggingface.co/org/name) | 7B | 85.2% | — | Apache 2.0 | 是 (fp16) |
| 2 | [org/name](https://huggingface.co/org/name) | 13B | 83.1% | 71.5% | MIT | 仅 Q4 |
| 3 | [org/name](https://huggingface.co/org/name) | 70B | 90.0% | 81.0% | Llama | 太大 |
```

- 将模型名称链接到 `https://huggingface.co/<model_id>`
- 对于模型未评估的基准，使用 `—`
- 用 ⭐ 标记推荐的顶级选择
- "设备上" 值：`是 (fp16)`、`仅 Q4`、`太大`、`仅 API`

### 后续操作

在展示表格后，询问用户："您希望运行 **[推荐的顶级模型]** 吗？"

如果他们回答是，询问他们是否希望：
- **本地运行**——如果尚未知道设备，则询问设备信息，然后给出适当的设置说明
- **在 HF Jobs 上运行**——将他们指向 HF Jobs 指南：https://huggingface.co/docs/huggingface_hub/en/guides/jobs

---

## 错误处理

- **排行榜未找到**：跳过，在输出中注明 "排行榜不可用"
- **模型在 hub_repo_details 中缺失**：回退到从模型名称解析大小
- **未找到任务的基准**：使用上述精选回退表格，或尝试 `hub_repo_search`，使用 `filters=["<task>"]` 并按 `trendingScore` 排序
- **所有排行榜失败**：回退到 `hub_repo_search`，查找标记有任务的热门模型，注明结果按流行度而非基准分数排序
