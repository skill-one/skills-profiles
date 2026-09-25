# 仓库上下文构建器

您通过检测项目、总结其架构，并将结果写入 `repo.md` 来收集仓库上下文。所有工作均由您自行完成——不要生成子代理或委托。

## 输入

从 `$ARGUMENTS`（键值对）中解析以下内容：
- **repo_path**: 仓库根目录的路径
- **cache_dir**: 缓存目录的路径（默认为 `~/.ghost/repos/<repo_id>/cache`）

$ARGUMENTS

如果未提供 `cache_dir`，则计算它：
```bash
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && cache_dir="$HOME/.ghost/repos/${repo_id}/cache" && echo "cache_dir=$cache_dir"
```

## 工具限制

不要使用 WebFetch 或 WebSearch。所有工作必须仅使用仓库中的本地文件。

## 设置

发现此技能自身的目录，以便您能够引用代理文件：
```bash
skill_dir=$(find . -path '*/skills/repo-context/SKILL.md' 2>/dev/null | head -1 | xargs dirname)
echo "skill_dir=$skill_dir"
```

---

## 首先检查缓存

检查 `<cache_dir>/repo.md` 是否已存在。如果存在，跳过所有步骤并返回：

```
仓库上下文位于：<cache_dir>/repo.md
```

如果不存在，运行 `mkdir -p <cache_dir>` 并继续。

---

## 工作流程

1. **检测项目** — 读取 `<skill_dir>/detector.md` 并按照其说明对 `<repo_path>` 进行操作。保存完整的检测输出（步骤 2 所需的项目详细信息）。如果检测未发现项目，则写入一个最小的 `repo.md` 并注明 "未检测到项目"，然后跳到步骤 4。

2. **总结每个项目** — 读取 `<skill_dir>/summarizer.md`。对于步骤 1 中检测到的每个项目，使用该项目的详细信息（id、类型、基础路径、语言、框架、依赖文件、扩展、证据）遵循总结器说明。收集每个项目的总结。如果某个项目的总结失败，则注明 "总结不可用" 并继续处理其余项目。

3. **写入 repo.md** — 使用 `<skill_dir>/template-repo.md` 中的格式，将检测和总结结果组合到 `<cache_dir>/repo.md` 中。对于每个项目，包括：
   - 检测：ID、类型、基础路径、语言、框架、依赖文件、扩展、证据
   - 总结：架构总结、敏感数据类型、业务关键性、组件映射、证据

4. **验证** — 读取 `<cache_dir>/repo.md` 并验证其是否包含来自 `<skill_dir>/template-repo.md` 的预期部分（例如，包含检测和总结字段的项目条目）。如果文件缺失或格式错误，则在报告错误之前重试一次写入。

5. **输出** — 返回：`Repository context is at: <cache_dir>/repo.md`
