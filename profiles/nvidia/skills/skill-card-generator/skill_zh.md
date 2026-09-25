# 生成技能卡

**技能目录分析目标**: $ARGUMENTS

## 目的

为现有代理技能创建一份NVIDIA治理技能卡的草稿。该技能收集源信号，指导代理构建一个有据可查的JSON上下文，渲染一个确定的markdown卡片，并在提交前检查是否已移除人工审核标记。

在以下情况下使用：
- 已存在技能目录并需要新的治理卡片。
- 需要刷新已存在的技能卡片的技能已变更。
- 技能所有者在准备法律/安全审核材料。

不使用于：
- 解释、列举、比较或讨论技能或技能能力。
- 创建或重写源技能本身。
- 为非技能资产（如模型、数据集、容器或完整系统）生成卡片。
- 签署、发布或批准技能卡片。
- 替代所需的人工法律、安全或所有者审核。

## 前置条件

- 可用Python 3。
- 在运行 `render_card.py` 之前安装 `jinja2`。
- 目标路径是一个包含 `SKILL.md` 或 `skill.md` 的技能目录。
- 代理可以写入临时上下文JSON文件和渲染后的卡片输出。
- 运行时权限允许从 `target_skill_directory` 读取，以及读取此技能的 `references/` 和 `scripts/`，仅写入目标技能目录或 `/tmp/`，以及仅对下面列出的三个脚本执行shell操作。

## 操作步骤

1. 在运行任何脚本之前，请先完整阅读此 `SKILL.md`。
2. 从 `$ARGUMENTS` 解析目标技能目录；如果省略，则使用当前工作目录。
3. 确保在声明的权限范围内操作。不要读取 `.env`、凭证文件、隐藏的认证文件夹或不相关的仓库文件；不要在目标技能目录或 `/tmp/` 之外写入。
4. 对目标运行 `scripts/discover_assets.py`。首先使用结构化信号摘要；如果输出被截断，则只读取目标文件或小段内容。
5. 首先从结构化信号摘要构建上下文JSON文件，仅在需要时才从提取的文件内容构建。
6. 用仅包含两个字段 `requires_api_key_or_credential` 和 `credential_types` 来填充 `credential_requirements`。以 `SKILL.md` 的散文文档为基础进行分类，而不是仅依赖脚本检查。对于 `credential_types`，使用 `references/style-guide.md` 中的受控词汇。永远不要包含凭证值、分配或原始环境变量名。
7. 遵循 `references/style-guide.md` 为每个上下文字段提供指导。仅在无源支持真实值时使用 `HUMAN-REQUIRED`。
8. 使用 `scripts/render_card.py` 渲染卡片，并在继续之前修复任何模式错误。
9. 手动审查卡片，移除已解决的 VERIFY 和 SELECT 标记，然后运行 `scripts/validate_submission.py`。
10. 完成前，确认渲染的卡片中没有任何未渲染的 `{{ ... }}` 或 `{% ... %}` 模板片段。

## 可用脚本

| 脚本 | 目的 | 参数 |
| --- | --- | --- |
| `scripts/discover_assets.py` | 提取技能文件、仓库信号、风格指南和模板到一个发现报告中。 | `<skill_directory>` |
| `scripts/render_card.py` | 验证上下文JSON并从Jinja模板渲染技能卡片。 | `--context <context.json> --template <skill-card.md.j2> --out <output.md>` |
| `scripts/validate_submission.py` | 如果渲染的卡片仍包含 VERIFY 或 SELECT 审核标记，则失败。 | `<rendered-card.md>` |

## 示例

为目标技能发现信号：

```text
run_script("scripts/discover_assets.py", args=["/path/to/target-skill"])
```

从完成的上下文渲染卡片：

```text
run_script(
  "scripts/render_card.py",
  args=[
    "--context", "/tmp/target-skill-context.json",
    "--template", "references/skill-card.md.j2",
    "--out", "/path/to/target-skill/target-skill-card.md"
  ]
)
```

提交前验证已审核的卡片：

```text
run_script("scripts/validate_submission.py", args=["/path/to/target-skill/target-skill-card.md"])
```

## 限制

- 生成的卡片是草稿，必须由人工所有者审核。
- 发现仅限于从目标路径可见的本地文件和仓库元数据。
- 渲染器验证所需上下文形状，而不是字段值的法律或安全正确性。
- 现成的限制和风险目录是起点；移除不相关的条目。

## 故障排除

| 错误 | 原因 | 解决方案 |
| --- | --- | --- |
| `directory not found` | 目标路径错误或未在工作空间中挂载。 | 使用技能目录的绝对路径重新运行发现。 |
| `jinja2 not installed` | 渲染器依赖缺失。 | 安装 `jinja2`，然后重新运行 `render_card.py`。 |
| `Context validation failed` | 缺少必需字段或类型错误。 | 使用 `references/style-guide.md` 修复上下文JSON。 |
| 未解析标记失败 | 审核后仍有 VERIFY 或 SELECT 标记。 | 确认每个标记字段，修剪目录条目，然后重新运行 `validate_submission.py`。 |

## 此技能中的文件

- `SKILL.md` - 此文件（编排）
- `references/style-guide.md` - 每个上下文字段的指导
- `references/skill-card.md.j2` - 精确卡片布局
- `references/Skill Card Generator License.txt` - 此技能包的许可证文本
- `references/catalog/limitations.json` - 现成的技术限制目录
- `references/catalog/risks.json` - 现成风险管理目录
- `scripts/discover_assets.py` - 发现和信号提取
- `scripts/render_card.py` - 带上下文验证的Jinja渲染器
- `scripts/validate_submission.py` - 提交前标记验证器
