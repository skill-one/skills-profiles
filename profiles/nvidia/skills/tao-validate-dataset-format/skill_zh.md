# 验证 TAO DAFT 数据集

> **是否需要独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

## 快速入门

```bash
tao-daft validate <格式> --路径 <数据集或父目录>
```

`<格式>` 是一个位置子命令（例如 `metropolis-v3.0`、`cosmos-reason-v1.0`）；
`--路径` 是必需的。通过 `tao-daft validate --help` 和叶节点 `--help`（见下文“CLI 约定”）发现支持的格式和每个格式的标志。

## 预检
```bash
python -c "import nvidia_tao_daft" 2>/dev/null || {
  echo "缺失：tao-daft 未安装。运行:"
  echo "  pip install nvidia-tao-daft"
  exit 1
}
```

## 快速入门

在选择格式缩写之前，先发现已安装的验证器格式，然后通过 `--路径` 传递目标运行验证：

```bash
tao-daft --version
tao-daft validate --help
tao-daft validate <格式> --help
tao-daft validate <格式> --路径 /路径/到/daft数据集
```

## 目的

对 DAFT 数据集（或其树状结构）运行 `tao-daft validate`。
CLI 是规范；技能选择子命令 + 标志并解释结果。

在用户提到“TAO DAFT”、“DAFT 格式”、“验证 DAFT 数据集”、模式/交叉引用错误或 `tao-daft validate` 时触发。
**不要** 对非 DAFT 布局（COCO、YOLO、Data Factory JSONL）或 `tao-daft info` / `tao-daft convert` 触发——这些有自己的技能。

如果用户的开启方式不明确，先运行几个 `--help` 命令来明确任务，然后再回来确认任务。

## 前置条件

- 已安装 `nvidia-tao-daft` (`pip install nvidia-tao-daft`；轮子即可，无需源代码库）。使用 `tao-daft --version` 确认。
- 本地磁盘上有 DAFT 数据集，或其父目录。

## 说明

### CLI 约定

`tao-daft` 是嵌套的 argparse 子命令。名称和标志会随版本变化，所以**从 `--help` 发现当前界面**，而不是信任此文档中的任何列表。

1. **格式是一个位置子命令**，不是 `--格式`：
   `tao-daft validate <格式> [标志]`。通过 `tao-daft validate --help` 列出当前格式；缩写看起来像 `metropolis-v3.0`、`cosmos-reason-v1.0`。
2. **目标是 `--路径 PATH`**，不是位置参数。它接受单个数据集/场景或父目录——验证器会遍历树。
3. **标志是按格式划分**的；在选择它们之前运行叶节点帮助，例如 `tao-daft validate metropolis-v3.0 --help`。
   不要假设一个格式的标志在另一个格式中也存在。

所以循环是：`tao-daft --version` → `tao-daft validate --help` →
选择格式（如果未指定则推断，见下文）→
`tao-daft validate <格式> --help` → 运行 → 解释。

### 格式推断

使用目录标记，而不是文件名：

- `meta.json` 靠近 `media/` 和 `text/` ⇒ `cosmos-reason-v1.0`。
- 包含 `contextual/` 的目录（或嵌套目录），通常与 `raw/` 和 `task/` 一起 ⇒ `metropolis-v3.0`。
- 没有标记 ⇒ 询问用户；不要猜测。

### 读取错误

CLI 在每次运行结束时都以 `验证结果` 块结束，然后是 `✅ 验证通过` 或 `❌ 验证失败`，并在失败时非零退出（脚本中安全串联）。

输出可能在大树中很大——将完整输出捕获到文件中，并分片读取，而不是逐行滚动。

## 限制

- 仅验证 DAFT。非 DAFT 布局（COCO、YOLO、Data Factory JSONL 等）属于上游转换技能。
- 支持的格式是 `tao-daft validate --help` 在安装版本中报告的任何格式；旧缩写可能已被淘汰。
- 仅涵盖 `validate`。对于 `tao-daft info` 和 `tao-daft convert`，委托给专用技能。
- 不要用 Python 重新实现验证；CLI 是规范。

## 故障排除

- **`tao-daft: 命令未找到`** — 轮子未在活动环境中安装。`pip install nvidia-tao-daft`；验证 `tao-daft --version`。
- **`error: 参数 --路径 是必需的`** — 路径按位置传递。将其放在 `--路径` 后面。
- **`invalid choice: '<格式>'`** — 缩写在此版本中未设置。重新运行 `tao-daft validate --help` 并从列表中选择。
- **自动检测（原始类型 / 上下文集）不正确** — 通过格式的范围限制标志覆盖；从叶节点 `--help` 发现名称。
- **CI 希望警告导致失败** — 添加 `--strict`。
