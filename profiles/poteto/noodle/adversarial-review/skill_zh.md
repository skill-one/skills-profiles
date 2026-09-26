# 对抗性评审

在**相反的模型**上生成评审者以挑战工作。评审者从基于大脑原理的不同视角发起攻击。交付成果是一个综合的裁决——**不要进行修改**。

**硬性约束**：评审者必须通过相反模型的CLI (`codex exec` 或 `claude -p`) 运行。**不要使用子代理、Agent工具或任何内部委派机制作为评审者**——这些运行在*你自己的*模型上，这会违背目的。

## 第1步 — 加载原理

阅读 `brain/principles.md`。遵循每一个 `[[wikilink]]` 并阅读每个链接的原理文件。这些原理指导评审者的判断。

## 第2步 — 确定范围和意图

从上下文（最近的差异、引用的计划、用户消息）中识别要评审的内容。

确定**意图**——作者试图实现的目标。这是关键：评审者挑战工作是否*很好地实现了意图*，而不是意图是否正确。在进行下一步之前，明确说明意图。

评估变更大小：

| 大小 | 阈值 | 评审者 |
|------|-----------|-----------|
| 小 | < 50行，1-2个文件 | 1 (怀疑论者) |
| 中 | 50-200行，3-5个文件 | 2 (怀疑论者 + 架构师) |
| 大 | 200+行或5+个文件 | 3 (怀疑论者 + 架构师 + 极简主义者) |

阅读 `references/reviewer-lenses.md` 获取视角定义。

## 第3步 — 检测模型并生成评审者

为评审者输出创建一个临时目录：

```sh
REVIEW_DIR=$(mktemp -d /tmp/adversarial-review.XXXXXX)
```

确定你是哪个模型，然后在相反的模型上生成评审者：

**如果你是Claude** —— 通过 `codex exec` 生成Codex评审者：

```sh
codex exec --skip-git-repo-check -o "$REVIEW_DIR/skeptic.md" "prompt" 2>/dev/null
```

如果评审者需要运行测试，仅使用 `--profile edit`。默认为只读。
使用 `run_in_background: true` 运行，通过 `TaskOutput` 并设置 `block: true, timeout: 600000` 进行监控。

**如果你是Codex** —— 通过 `claude` CLI 生成Claude评审者：

```sh
claude -p "prompt" > "$REVIEW_DIR/skeptic.md" 2>/dev/null
```

使用 `run_in_background: true` 运行。

将每个输出文件命名为对应的视角：`skeptic.md`、`architect.md`、`minimalist.md`。

使用 `references/reviewer-prompt.md` 中的模板构建每个评审者的提示。

## 第4步 — 验证并综合裁决

在阅读评审者输出之前，记录使用的CLI并确认输出文件存在：

```sh
echo "reviewer_cli=codex|claude"
ls "$REVIEW_DIR"/*.md
```

如果任何输出文件缺失或为空，在裁决中记录失败——不要无声地跳过某个评审者。

从 `$REVIEW_DIR/` 读取每个评审者的输出文件。合并重复的发现。
使用 `references/verdict-format.md` 中的格式生成单一裁决。

## 第5步 — 渲染判决

在综合评审者之后，应用你自己的判断。以声明的意图和大脑原理为框架，说明你会接受哪些发现，拒绝哪些发现——以及原因。评审者按设计是对抗性的；并非每个发现都值得行动。指出误报、过度推断以及将风格误认为实质的发现。

将主要判决部分附加到裁决中（参见 `references/verdict-format.md`）。
