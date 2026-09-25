# 将 TAO DAFT 数据集转换

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

## 快速入门

```bash
tao-daft convert <源格式> <目标格式> --path <输入路径> --output <输出路径>
```

源和目标是位置子命令；`--path` 和 `--output` 是标志。
从叶节点 `--help` 中发现支持的格式和每对标志（见下文“CLI 约定”）。

## 预检
```bash
python -c "import nvidia_tao_daft" 2>/dev/null || {
  echo "缺失：tao-daft 未安装。运行:"
  echo "  pip install nvidia-tao-daft"
  exit 1
}
```

## 快速入门

在选择格式缩写之前，先发现已安装的 CLI 界面，然后使用显式的 `--path` 和 `--output` 标志运行叶节点转换命令：

```bash
tao-daft --version
tao-daft convert --help
tao-daft convert <源格式> --help
tao-daft convert <源格式> <目标格式> --path /路径/to/daft --output /路径/to/转换
```

## 目的

驱动 `tao-daft convert` 将 DAFT 数据集（或其树状结构）在支持的格式之间进行转换。CLI 执行实际工作；技能选择正确的源/目标对和标志，然后解释结果。

触发条件：转换 DAFT 数据集、为 VLM 训练打包 DAFT QA / 摘要 / 时间任务、生成 `meta.json` 风格的训练集，或 `tao-daft convert` 命令。**不**触发非 DAFT → DAFT 转换（COCO、YOLO、Data Factory JSONL）— 重定向到上游 `nvidia-tao-daft` 仓库的转换技能。

如果用户输入模糊，请先运行几次 `--help` 命令。

## 前置条件

- 已安装 `nvidia-tao-daft`（仅 wheel，非源代码仓库）。
  使用 `tao-daft --version` 确认。
- 本地磁盘上有一个 DAFT 数据集，或包含许多数据集的父目录。

## 说明

### CLI 约定

`tao-daft` 是嵌套的 argparse 子命令。以下约定即使在格式名称或标志更改时也保持稳定，因此**始终从 `--help` 发现当前界面**，而不是依赖此文档碰巧提到的名称。

1. **源和目标都是位置子命令**，不是 `--from`/`--to`：`tao-daft convert <源> <目标> [标志]`。
   格式缩写是版本化的、小写的、点分隔的（`metropolis-v3.0`、`cosmos-reason-v1.0`、...）。
2. **路径和输出是标志** — `--path PATH`（源）、`--output OUTPUT`（目标）。在叶节点处两者都必需；按位置传递会失败。
3. **`--path` 接受两种粒度** — 单个场景/数据集或父目录；转换器会遍历树。
4. **每对标志位于叶节点** — 标志集因目标而异（例如媒体处理）。始终检查叶节点 `--help`。

**操作流程：**

1. `tao-daft --version` — 确认安装，在任何报告中固定版本。
2. `tao-daft convert --help` — 列出支持的源格式。
3. `tao-daft convert <源> --help` — 列出该源的有效目标。
4. 从布局推断源（与 `tao-validate-dataset-format` 技能的“格式推断”相同的目录标记）。如果您无法推断或目标未指定，请询问。
5. `tao-daft convert <源> <目标> --help` — 为用户的意图选择标志（任务子集、媒体复制 vs 引用、元数据）。
6. 执行，然后解释（见下文）。

### 读取输出

每个场景的进度打印到标准输出；失败时非零退出。转换后的数据集写入 `--output` 下 — 训练前使用 `tao-validate-dataset-format` 技能检查它。对于大型树，捕获完整输出并在巨大时进行部分读取。

## 限制

- 仅支持 DAFT 的源格式。对于非 DAFT 布局使用上游仓库的转换技能。
- 支持的对是安装版本 `--help` 报告的 — 不要传递未确认的对。
- 源和目标是位置；`--path` / `--output` 是标志。
- 仅 `convert` — `validate` 和 `info` 有自己的技能。
- 不要在 Python 中重新实现转换；CLI 是规范。

## 故障排除

- **`tao-daft: 命令未找到`** — wheel 未安装；`pip install nvidia-tao-daft`，使用 `tao-daft --version` 验证。
- **`error: 参数 --path/--output 是必需的`** — 按位置传递；移到标志后面。
- **`invalid choice: '<格式>'`** — 缩写在此版本中未配置。重新运行相关的 `--help`。
- **输出被 `tao-daft validate` 拒绝** — 通过叶节点 `--help` 重新检查每对标志（媒体处理、任务子集）；一个设置错误的标志通常会产生结构上有效但语义上错误的输出。
