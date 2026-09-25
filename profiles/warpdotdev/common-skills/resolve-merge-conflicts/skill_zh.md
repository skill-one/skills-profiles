# 解决合并冲突

## 概述

无需打开完整文件即可解决冲突，除非紧凑视图不足以显示。先查看摘要，然后逐个检查冲突文件。

## 工作流程

1. 先查看摘要。

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py
```

使用摘要来识别哪些文件未解决、哪些索引阶段存在，以及每个文件包含多少文本块。

2. 查看单个文件。

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py --file path/to/file
```

优先使用此方法而不是阅读整个文件。脚本仅打印附近的上下文、每个块的 `ours` / `base` / `theirs` 部分，以及 `ours` 和 `theirs` 之间的紧凑统一差异。

3. 解决文件。

- 在适当的情况下，使用 `git checkout --ours -- path/to/file` 或 `git checkout --theirs -- path/to/file` 整体选择其中一方。
- 否则直接编辑文件并删除冲突标记。
- 只有当紧凑输出不足以决定正确合并时，才读取更多文件内容。

4. 重新检查未解决的文件。

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py
git diff --name-only --diff-filter=U
```

5. 验证解决方案。

- 确保没有未合并的路径。
- 确保解决后的文件中不再有 `<<<<<<<`、`=======` 或 `>>>>>>>` 标记。
- 对修改区域运行目标测试、构建或代码检查器。
- 将解决后的文件暂存。

## 命令

### 仅摘要

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py
```

### 单个文件的详细视图

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py --file path/to/file
```

### 所有冲突文件的详细视图

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py --all
```

### JSON输出

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py --file path/to/file --json
```

### 调整输出大小

```bash
python3 .agents/skills/resolve-merge-conflicts/scripts/extract_conflict_context.py \
  --file path/to/file \
  --context 3 \
  --max-lines 60
```

## 注意事项

- 在直接打开冲突文件之前使用脚本。
- 逐个解决文件以保持上下文较小。
- 预期基于标记的文本冲突和仅索引冲突（如添加/添加或修改/删除）。脚本会总结这两种情况，当工作树文件没有冲突标记时，会回退到索引阶段预览。
