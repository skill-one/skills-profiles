# 技能设计器

## 概述

从结构化的技能想法规范生成一个完整的 Claude CLI 提示。该提示指示 Claude 创建一个符合仓库规范的完整技能目录：包含 YAML 前置文本的 SKILL.md、参考文档、辅助脚本和测试脚手架。

## 使用场景

- 技能自动生成流水线从积压队列中选择一个想法，并需要为 `claude -p` 准备设计提示
- 开发者希望从一个 JSON 想法规范启动一个新的技能
- 生成的技能质量审查需要了解评分标准

## 前置条件

- Python 3.9+
- 无需外部 API 密钥
- 参考文件必须存在于 `references/` 目录下

## 工作流程

### 第一步：准备想法规范

接受一个包含以下内容的 JSON 文件 (`--idea-json`)：
- `title`：人类可读的想法名称
- `description`：技能的功能描述
- `category`：技能类别（例如，trading-analysis、developer-tooling）

接受一个标准化的技能名称 (`--skill-name`)，它将用作目录名称和 YAML 前置文本 `name:` 字段。

### 第二步：构建设计提示

运行提示构建器：

```bash
python3 skills/skill-designer/scripts/build_design_prompt.py \
  --idea-json /tmp/idea.json \
  --skill-name "my-new-skill" \
  --project-root .
```

脚本执行：
1. 加载想法 JSON
2. 读取所有三个参考文件（结构指南、质量检查清单、模板）
3. 列出现有技能（最多 20 个）以防止重复
4. 将完整的提示输出到标准输出

### 第三步：将提示输入 Claude CLI

调用流水线将提示管道输入 `claude -p`：

```bash
python3 skills/skill-designer/scripts/build_design_prompt.py \
  --idea-json /tmp/idea.json \
  --skill-name "my-new-skill" \
  --project-root . \
| claude -p --allowedTools Read,Edit,Write,Glob,Grep
```

### 第四步：验证输出

Claude 创建技能后，验证：
- `skills/<skill-name>/SKILL.md` 存在且具有正确的前置文本
- 目录结构符合规范
- 双轴技能审查器评分达到阈值

## 输出格式

脚本将纯文本提示输出到标准输出。成功时退出码为 0，如果必需的参考文件缺失则退出码为 1。

## 资源

- `references/skill-structure-guide.md` -- 目录结构、SKILL.md 格式、命名规范
- `references/quality-checklist.md` -- 双轴审查器 5 类别检查清单（100 分）
- `references/skill-template.md` -- 包含 YAML 前置文本和标准部分的 SKILL.md 模板
- `scripts/build_design_prompt.py` -- 提示构建器脚本（CLI 接口）
