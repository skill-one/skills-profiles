# sf-diagram-nanobananapro: Salesforce 视觉 AI 技能

当用户需要**渲染后的视觉图像**而不是文本图表时，使用此技能：实体关系图（ERD）、UI 模板、架构插图、适用于幻灯片的图像，或使用 Nano Banana Pro 进行的图像编辑。

## 硬性门槛：先完成先决条件检查

在使用技能之前，始终运行先决条件检查：

```bash
~/.claude/skills/sf-diagram-nanobananapro/scripts/check-prerequisites.sh
```

如果先决条件检查失败，停止并引导用户到以下设置指南：
- [references/gemini-cli-setup.md](references/gemini-cli-setup.md)

---

## 此技能负责的任务场景

当用户需要以下内容时，使用 `sf-diagram-nanobananapro`：
- PNG / SVG 风格的图像输出
- 渲染后的实体关系图或架构图表
- LWC 或体验云的模板/线框图
- 超越 Mermaid 的视觉美化
- 对先前生成的图像进行编辑

当用户需要以下内容时，将任务委托给其他技能：
- Mermaid 或纯文本图表 → [sf-diagram-mermaid](../sf-diagram-mermaid/SKILL.md)
- 实体关系图的元数据发现 → [sf-metadata](../sf-metadata/SKILL.md)
- 模板后的 LWC 实现 → [sf-lwc](../sf-lwc/SKILL.md)
- Apex 审查/实现 → [sf-apex](../sf-apex/SKILL.md)

---

## 首先收集必要的上下文

请求或推断：
- 图像类型：实体关系图、UI 模板、架构插图或图像编辑
- 主题范围和关键实体/系统
- 目标质量：草稿、演示文稿还是生产资源
- 偏好的风格和宽高比
- 用户是否希望快速模式或通过访谈构建提示

---

## 访谈优先工作流程

除非用户明确要求**快速/简单/直接生成**，否则先询问澄清问题。

### 最小问题集
| 请求类型 | 询问内容 |
|---|---|
| 实体关系图/架构图 | 对象、视觉风格、用途、附加内容 |
| UI 模板 | 组件类型、对象/上下文、设备/布局、风格 |
| 架构图像 | 系统、边界、协议、重点 |
| 图像编辑 | 保留什么、改变什么、输出质量 |

问题库：[references/interview-questions.md](references/interview-questions.md)

### 快速模式默认值
如果用户说“快速”、“简单”或“直接生成”，默认为：
- 专业风格
- 1K 草稿输出
- 在有帮助时包含图例
- 先生成一张图像，然后迭代

---

## 推荐工作流程

### 1. 收集输入
确定需要以下哪些内容：
- 对象列表/元数据
- 用途：草稿、演示文稿还是文档
- 期望的审美
- 宽高比/分辨率
- 这是全新渲染还是对现有图像的编辑

### 2. 构建具体提示
好的提示指定：
- 主题和范围
- 构成/布局
- 色彩处理
- 标签/图例/关系线
- 输出质量目标

### 3. 首先生成快速草稿
```bash
gemini --yolo "/generate '专业的 Salesforce 实体关系图，包含 Account、Contact、Opportunity；清晰的图例；白色背景；Salesforce 风格的配色'"
```

### 4. 在最终前迭代
使用自然语言编辑：
```bash
gemini --yolo "/edit '将 Account 移至中心，加粗关系线，在右下角添加图例'"
```

### 5. 使用 Python 脚本进行受控的最终输出
当需要更高分辨率或明确的编辑输入时，使用脚本：
```bash
uv run scripts/generate_image.py \
  -p "最终生产质量的 Salesforce 实体关系图，带图例和字段高亮" \
  -f "crm-erd-final.png" \
  -r 4K
```

完整迭代指南：[references/iteration-workflow.md](references/iteration-workflow.md)

---

## 默认风格指南

对于实体关系图，除非用户要求否则默认为 **architect.salesforce.com** 的美学：
- 深色边框+浅色填充卡片
- 云特定强调色
- 干净的标签和关系线
- 适用于演示文稿的空白和层次结构

风格指南：[references/architect-aesthetic-guide.md](references/architect-aesthetic-guide.md)

---

## 常见模式

| 模式 | 默认方法 |
|---|---|
| 视觉实体关系图 | 如果有元数据，先获取元数据，然后渲染草稿 |
| LWC 模板 | 使用组件模板+用户上下文+一次草稿迭代 |
| 架构插图 | 强调系统和流程，减少字段级细节 |
| 图像细化 | 使用 `/edit` 在重新生成前进行小修改 |
| 最终生产资源 | 切换到脚本驱动的 2K/4K 生成 |

示例：[references/examples-index.md](references/examples-index.md)

---

## 输出/审查指南

生成后，执行以下操作之一：
- 在预览中打开文件进行视觉检查
- 在编码会话中附加/阅读图像进行多模态审查
- 在最终确定前询问用户是否需要迭代布局、标签或颜色

保持第一遍低成本；只有在构图正确后才投入高分辨率输出。

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| Mermaid 初稿或文本图表 | [sf-diagram-mermaid](../sf-diagram-mermaid/SKILL.md) | 更快的结构化图表绘制 |
| 实体关系图的对象/字段发现 | [sf-metadata](../sf-metadata/SKILL.md) | 准确的架构基础 |
| 将模板转换为实际组件 | [sf-lwc](../sf-lwc/SKILL.md) | 设计后的实现 |
| 并行审查 Apex/触发代码 | [sf-apex](../sf-apex/SKILL.md) | 代码质量后续跟进 |

---

## 参考地图

### 从这里开始
- [references/gemini-cli-setup.md](references/gemini-cli-setup.md)
- [references/interview-questions.md](references/interview-questions.md)
- [references/iteration-workflow.md](references/iteration-workflow.md)

### 视觉风格/示例
- [references/architect-aesthetic-guide.md](references/architect-aesthetic-guide.md)
- [references/examples-index.md](references/examples-index.md)
- [assets/erd/](assets/erd/)
- [assets/lwc/](assets/lwc/)
- [assets/architecture/](assets/architecture/)
- [assets/review/](assets/review/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 70+ | 强大的图像提示/工作流程选择 |
| 55–69 | 可用的草稿，需要迭代 |
| 40–54 | 部分符合请求 |
| < 40 | 不匹配；重新访谈并重建提示 |
