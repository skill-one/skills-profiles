# generating-visual-diagrams: Salesforce 视觉 AI 技能

当用户需要**渲染后的视觉图像**而不是文本图表时，使用此技能：实体关系图（ERD）、UI 模板、架构插图、适用于幻灯片的图像，或使用 Nano Banana Pro 进行的图像编辑。

## 范围

**在范围内：**
- PNG / SVG 风格的渲染图像输出
- 视觉 ERD 和架构图表
- LWC 或体验云模板/线框图
- 对先前生成的视觉图像进行编辑

**超出范围——转而委托：**
- Mermaid 或纯文本图表 → [generating-mermaid-diagrams](../generating-mermaid-diagrams/SKILL.md)
- ERD 的对象/字段元数据发现 → [generating-custom-object](../generating-custom-object/SKILL.md) 或 [generating-custom-field](../generating-custom-field/SKILL.md)
- 模板批准后的 LWC 实现 → [generating-lwc-components](../generating-lwc-components/SKILL.md)
- Apex 审查/实现 → [generating-apex](../generating-apex/SKILL.md)

---

## 硬性门槛：先检查先决条件

在使用技能之前运行先决条件检查：

```bash
scripts/check-prerequisites.sh
```

如果先决条件失败，停止并将用户引导至设置指南：
- [references/gemini-cli-setup.md](references/gemini-cli-setup.md)

---

## 必须的输入

在生成之前询问或推断：

| 输入 | 如果未提供，则默认值 |
|---|---|
| 图像类型 | ERD |
| 主题范围和关键实体/系统 | 询问用户 |
| 目标质量 | 草稿 (1K) |
| 偏好风格 | architect.salesforce.com 美学 |
| 宽高比 | 默认（不覆盖） |
| 快速模式或访谈模式 | 访谈模式 |

---

## 访谈优先工作流

除非用户要求**快速/简单/直接生成**，否则先使用 [references/interview-questions.md](references/interview-questions.md) 中的问题库进行澄清问题。

| 请求类型 | 询问关于 |
|---|---|
| ERD / 架构 | 对象、视觉风格、目的、附加内容 |
| UI 模板 | 组件类型、对象/上下文、设备/布局、风格 |
| 架构图像 | 系统、边界、协议、重点强调 |
| 图像编辑 | 保留什么、改变什么、输出质量 |

**快速模式默认值**（由 "quick"、"simple"、"just generate"、"fast" 触发）：
- 专业风格、1K 草稿、包含图例、先生成一张图像然后迭代

---

## 推荐工作流

### 1. 运行先决条件检查
运行 `scripts/check-prerequisites.sh` 并确认所有必需工具通过后再继续。

### 2. 收集输入
- 对象列表 / 元数据（如有需要，委托给 `generating-custom-object` / `generating-custom-field`）
- 目的：草稿与演示文稿与文档
- 所需美学——阅读 [references/architect-aesthetic-guide.md](references/architect-aesthetic-guide.md) 获取 ERD
- 宽高比 / 分辨率

### 3. 运行访谈或使用快速模式默认值
加载 [references/interview-questions.md](references/interview-questions.md) 以匹配请求类型（ERD、LWC、架构、代码审查）的问题集。

### 4. 构建具体提示
好的提示指定主题、构图、色彩处理、标签/图例和输出质量目标。

### 5. 生成 1K 快速草稿
```bash
gemini --yolo "/generate '您的提示'"
```
打开结果并审查布局，然后再投入高分辨率。

### 6. 使用编辑进行迭代
```bash
gemini --yolo "/edit '具体变更指令'"
```
使用 `/edit` 进行小调整——比重新生成更便宜。参见 [references/iteration-workflow.md](references/iteration-workflow.md)。

### 7. 使用 Python 脚本生成最终 2K/4K
当布局确认后运行 `scripts/generate_image.py`：
```bash
uv run scripts/generate_image.py -p "精炼提示" -f "output.png" -r 4K
```

### 8. 错误恢复
- 如果 `gemini --yolo` 返回无图像：重新运行一次；如果再次失败，则回退到 Python 脚本路径。
- 如果 Python 脚本因 `GEMINI_API_KEY not found` 失败：验证密钥是否导出到您的 shell 配置文件（macOS/zsh 上的 `~/.zshrc`、Linux 上的 `~/.bashrc`）并刷新终端会话。
- 如果扩展缺失：运行 `gemini extensions install nanobanana` 并重新运行先决条件检查。

---

## 默认风格指南

对于 ERD，除非用户要求否则默认使用 **architect.salesforce.com** 美学：
- 深色边框 + 浅色填充卡片
- 云特定强调色
- 干净的标签和关系线
- 适用于演示文稿的空白和层次结构

完整风格规范：[references/architect-aesthetic-guide.md](references/architect-aesthetic-guide.md)

---

## 常见模式

| 模式 | 默认方法 |
|---|---|
| 视觉 ERD | 如果有元数据，则先渲染草稿 |
| LWC 模板 | 加载 [assets/lwc/data-table.md](assets/lwc/data-table.md)、[assets/lwc/record-form.md](assets/lwc/record-form.md) 或 [assets/lwc/dashboard-card.md](assets/lwc/dashboard-card.md) 以匹配模板 |
| 架构插图 | 加载 [assets/architecture/integration-flow.md](assets/architecture/integration-flow.md)；强调系统和流程 |
| 图像细化 | 在重新生成之前使用 `/edit` 进行小更改 |
| 最终生产资产 | 通过 `scripts/generate_image.py` 切换到脚本驱动的 2K/4K 生成 |
| Apex / LWC 代码审查 | 加载 [assets/review/apex-review.md](assets/review/apex-review.md) 或 [assets/review/lwc-review.md](assets/review/lwc-review.md) 以获取审查提示模板 |

---

## 输出预期

此技能生成的可交付成果：

- **草稿图像** (`<name>.png`) — 1K 分辨率通过 `gemini --yolo "/generate ..."` 渲染用于布局审查
- **最终图像** (`<name>.png`) — 2K 或 4K 分辨率通过 `scripts/generate_image.py` 在构图批准后渲染
- **编辑迭代** (`<name>.png`) — 通过 `gemini --yolo "/edit ..."` 进行增量细化，无需完全重新生成

每次交付图像后：
- 在预览中打开文件或在会话中附加它以进行多模态审查
- 询问用户是否要在最终确定之前迭代布局、标签或颜色
- 只有在草稿构图确认后才能继续生成高分辨率输出

---

## 规则/约束

| 规则 | 理由 |
|---|---|
| 在任何生成之前始终运行先决条件检查 | 缺少工具会导致静默失败 |
| 在生成 4K 之前始终以 1K 草稿 | 成本和时间节省；高分辨率时的构图更改是浪费 |
| 使用 `/edit` 进行增量更改，而不是完全重新生成 | 对于小调整来说更便宜、更快 |
| 永远不要将 `GEMINI_API_KEY` 提交到版本控制 | 密钥是个人绑定的计费 |
| 将文本图表委托给 `generating-mermaid-diagrams` | 此技能仅拥有渲染图像 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| 编辑未正确应用 | 具体说明：通过名称引用现有元素；一次一个更改 |
| 4K 输出与 1K 草稿看起来不同 | 使用完全相同的提示文本；轻微变化是正常模型行为 |
| `gemini --yolo` 无声失败 | 检查 Nano Banana 扩展是否已安装：`gemini extensions list` |
| 图像尺寸错误 | 在 `scripts/generate_image.py` 中明确设置 `--aspect-ratio` 使用 `-a "16:9"` |
| RGBA 图像在 Python 脚本中导致错误 | 脚本自动将 RGBA→RGB；确保通过 `uv` 安装 Pillow |

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| Mermaid 初稿或文本图表 | [generating-mermaid-diagrams](../generating-mermaid-diagrams/SKILL.md) | 更快的结构化图表绘制 |
| 对象/字段发现用于 ERD | [generating-custom-object](../generating-custom-object/SKILL.md) / [generating-custom-field](../generating-custom-field/SKILL.md) | 准确的架构基础 |
| 将模板转换为真实的 LWC 组件 | [generating-lwc-components](../generating-lwc-components/SKILL.md) | 设计后的实现 |
| Apex 审查/实现 | [generating-apex](../generating-apex/SKILL.md) | 代码质量后续跟进 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|---|---|
| [references/gemini-cli-setup.md](references/gemini-cli-setup.md) | 先决条件失败——Gemini CLI / Nano Banana 设置指南 |
| [references/interview-questions.md](references/interview-questions.md) | 第 3 步——加载匹配请求类型的问题集 |
| [references/iteration-workflow.md](references/iteration-workflow.md) | 第 6 步——草稿到最终迭代的模式和成本提示 |
| [references/architect-aesthetic-guide.md](references/architect-aesthetic-guide.md) | 第 4 步——ERD 色彩调板、框样式、提示模板 |
| [references/examples-index.md](references/examples-index.md) | 第 4 步——ERD、LWC、架构、代码审查的示例提示 |
| [assets/erd/core-objects.md](assets/erd/core-objects.md) | 第 4 步——核心 CRM 对象（账户、联系人、机会、案例）的提示模板 |
| [assets/erd/custom-objects.md](assets/erd/custom-objects.md) | 第 4 步——自定义对象 ERD 的提示模板 |
| [assets/lwc/data-table.md](assets/lwc/data-table.md) | 第 4 步——lightning-datatable 模板提示 |
| [assets/lwc/record-form.md](assets/lwc/record-form.md) | 第 4 步——lightning-record-form 模板提示 |
| [assets/lwc/dashboard-card.md](assets/lwc/dashboard-card.md) | 第 4 步——仪表板卡片/指标瓦片模板提示 |
| [assets/architecture/integration-flow.md](assets/architecture/integration-flow.md) | 第 4 步——集成架构图表的提示模板 |
| [assets/review/apex-review.md](assets/review/apex-review.md) | 第 4 步——Apex 代码的 Gemini 审查提示模板 |
| [assets/review/lwc-review.md](assets/review/lwc-review.md) | 第 4 步——LWC 组件的 Gemini 审查提示模板 |
| [scripts/check-prerequisites.sh](scripts/check-prerequisites.sh) | 第 1 步——运行以验证所有必需工具是否已安装 |
| [scripts/generate_image.py](scripts/generate_image.py) | 第 7 步——用于 2K/4K 分辨率输出和具有分辨率控制的图像编辑运行 |
