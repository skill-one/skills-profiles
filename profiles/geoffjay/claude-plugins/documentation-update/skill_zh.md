# 文档更新技能

该技能通过读取市场目录并应用 Jinja2 模板，自动重新生成 `docs/` 目录中的文档文件。

## 目的

通过以下方式维护同步文档：

- 生成代理参考文档
- 创建技能目录文档
- 构建插件目录
- 更新使用指南
- 确保所有文档的一致性

## 何时使用

在以下情况下使用此技能：

- 市场中添加了新插件
- 现有插件更新（添加/移除组件）
- 代理或技能元数据发生变化
- 需要重新生成文档
- 确保文档与市场状态匹配

## 文档文件

该技能生成四个主要文档文件：

### 1. agents.md

所有插件中所有代理的完整参考：

- 按插件组织
- 列出代理名称、描述和模型
- 包含指向代理文件的链接
- 显示代理功能和用例

### 2. agent-skills.md

具有渐进式披露详细信息的所有技能目录：

- 按插件组织
- 列出技能名称和描述
- 显示“何时使用”触发器
- 包含技能结构信息

### 3. plugins.md

市场中所有插件的目录：

- 按类别组织
- 显示插件名称、描述和版本
- 列出组件（代理、命令、技能）
- 提供安装和使用信息

### 4. usage.md

使用指南和命令参考：

- 入门说明
- 命令使用示例
- 工作流模式
- 集成指南

## 模板结构

模板使用 Jinja2 语法存储在 `assets/` 中：

```
assets/
├── agents.md.j2
├── agent-skills.md.j2
├── plugins.md.j2
└── usage.md.j2
```

### 模板变量

所有模板接收以下上下文：

```python
{
  "marketplace": {
    "name": "marketplace-name",
    "owner": {...},
    "metadata": {...},
    "plugins": [...]
  },
  "plugins_by_category": {
    "category-name": [plugin1, plugin2, ...]
  },
  "all_agents": [
    {
      "plugin": "plugin-name",
      "name": "agent-name",
      "file": "agent-file.md",
      "description": "...",
      "model": "..."
    }
  ],
  "all_skills": [
    {
      "plugin": "plugin-name",
      "name": "skill-name",
      "path": "skill-path",
      "description": "..."
    }
  ],
  "all_commands": [
    {
      "plugin": "plugin-name",
      "name": "command-name",
      "file": "command-file.md",
      "description": "..."
    }
  ],
  "stats": {
    "total_plugins": 10,
    "total_agents": 25,
    "total_commands": 15,
    "total_skills": 30
  }
}
```

## Python 脚本

该技能包含一个 Python 脚本 `doc_generator.py`，该脚本：

1. **加载 marketplace.json**

   - 读取市场目录
   - 验证结构
   - 构建组件索引

2. **扫描插件文件**

   - 读取代理/命令的前置内容
   - 提取技能元数据
   - 构建全面的组件列表

3. **准备模板上下文**

   - 按类别组织插件
   - 创建组件索引
   - 计算统计数据

4. **渲染模板**
   - 应用 Jinja2 模板
   - 生成文档文件
   - 写入到 docs/ 目录

### 使用方法

```bash
# 生成所有文档文件
python doc_generator.py

# 仅生成特定文件
python doc_generator.py --file agents

# 模拟运行（显示输出但不写入）
python doc_generator.py --dry-run

# 指定自定义路径
python doc_generator.py \
  --marketplace .claude-plugin/marketplace.json \
  --templates plugins/claude-plugin/skills/documentation-update/assets \
  --output docs
```

## 与命令的集成

`/claude-plugin:create` 和 `/claude-plugin:update` 命令应在市场更新后自动调用此技能：

### 工作流程

```
1. 插件操作完成（添加/更新/移除）
2. 市场place.json 更新
3. 调用文档更新技能
4. 重新生成文档文件
5. 准备提交更改
```

### 示例集成

```python
# 创建/更新插件后
print("正在更新文档...")

# 运行文档生成器
import subprocess
result = subprocess.run(
    ["python", "plugins/claude-plugin/skills/documentation-update/doc_generator.py"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ 文档已更新")
else:
    print(f"❌ 文档更新失败：{result.stderr}")
```

## 模板示例

### agents.md.j2

```jinja2
# 代理参考

本文件列出了市场中所有插件提供的代理。

{% for category, plugins in plugins_by_category.items() %}
## {{ category|title }}

{% for plugin in plugins %}
### {{ plugin.name }}

{{ plugin.description }}

**代理：**

{% for agent in all_agents %}
{% if agent.plugin == plugin.name %}
- **{{ agent.name }}** (`{{ agent.model }}`)
  - {{ agent.description }}
  - 文件：`plugins/{{ plugin.name }}/agents/{{ agent.file }}`
{% endif %}
{% endfor %}

{% endfor %}
{% endfor %}

---
*最后更新：{{ now }}*
*总代理数：{{ stats.total_agents }}*
```

### agent-skills.md.j2

```jinja2
# 代理技能参考

本文件列出了所有具有渐进式披露模式的技能。

{% for plugin in marketplace.plugins %}
## {{ plugin.name }}

{{ plugin.description }}

**技能：**

{% for skill in all_skills %}
{% if skill.plugin == plugin.name %}
### {{ skill.name }}

{{ skill.description }}

- **位置：** `plugins/{{ plugin.name }}/skills/{{ skill.path }}/`
- **结构：** SKILL.md + assets/ + references/

{% endif %}
{% endfor %}

{% endfor %}

---
*最后更新：{{ now }}*
*总技能数：{{ stats.total_skills }}*
```

## 错误处理

### 市场未找到

```
错误：未找到市场文件：.claude-plugin/marketplace.json
建议：确保存在 marketplace.json
```

### 模板未找到

```
错误：未找到模板文件：assets/agents.md.j2
建议：确保 assets/ 中存在所有模板文件
```

### 插件结构无效

```
警告：插件 'plugin-name' 缺少组件
建议：验证插件是否包含代理或命令
```

### 前置内容解析错误

```
警告：无法解析 agents/agent-name.md 中的前置内容
建议：检查 YAML 前置内容语法
```

## 最佳实践

1. **更改后始终重新生成**

   - 每次插件添加/更新/移除后运行
   - 确保文档保持同步
   - 与插件更改一起提交文档

2. **生成前验证**

   - 首先运行市场验证
   - 修复任何错误或警告
   - 确保所有文件存在

3. **审查生成输出**

   - 检查生成文件的正确性
   - 验证格式和链接
   - 测试任何代码示例

4. **模板维护**

   - 保持模板简洁易读
   - 使用一致的格式
   - 记录模板变量

5. **版本控制**
   - 提交文档更改
   - 包含在拉取请求中
   - 记录重大更改

## 模板定制

### 添加新部分

要向模板添加新部分：

1. **修改模板**

   ```jinja2
   ## 新部分

   {% for plugin in marketplace.plugins %}
   ### {{ plugin.name }}
   [此处填写内容]
   {% endfor %}
   ```

2. **更新上下文（如果需要）**

   - 在 doc_generator.py 中为模板上下文添加新数据
   - 处理额外元数据

3. **测试输出**
   - 使用模拟运行生成器
   - 验证格式
   - 检查错误

### 创建新模板

要添加新的文档文件：

1. **创建模板**

   - 添加 `assets/newdoc.md.j2`
   - 定义结构和内容

2. **更新脚本**

   - 将模板添加到 doc_generator.py
   - 定义输出路径

3. **测试生成**
   - 运行生成器
   - 验证输出
   - 提交模板和输出

## 文件结构

```
plugins/claude-plugin/skills/documentation-update/
├── SKILL.md                      # 此文件
├── doc_generator.py              # Python 实现
├── assets/                       # Jinja2 模板
│   ├── agents.md.j2
│   ├── agent-skills.md.j2
│   ├── plugins.md.j2
│   └── usage.md.j2
└── references/                   # 可选示例
    └── template-examples.md
```

## 要求

- Python 3.8+
- 无外部依赖（仅使用标准库）
- 可访问 `.claude-plugin/marketplace.json`
- 对插件目录的读取权限
- 对 `docs/` 目录的写入权限

## 成功标准

运行此技能后：

- ✓ 所有文档文件已生成
- ✓ 内容与市场状态匹配
- ✓ 所有链接有效
- ✓ 格式一致
- ✓ 统计数据准确
- ✓ 无模板渲染错误

## 维护

### 更新模板

当市场结构发生变化时：

1. **评估影响**

   - 确定受影响的模板
   - 确定所需更改

2. **更新模板**

   - 修改 Jinja2 模板
   - 使用当前数据测试

3. **更新脚本**

   - 如果需要，调整上下文准备
   - 添加新数据处理

4. **验证输出**
   - 重新生成所有文档
   - 审查更改
   - 测试链接和格式

### 版本兼容性

- 模板应优雅处理缺失字段
- 使用 Jinja2 默认过滤器处理可选数据
- 验证市场版本兼容性

## 示例输出

该技能生成全面、格式良好的文档：

- **agents.md**: 20-30 个代理的 500-1000 行
- **agent-skills.md**: 30-50 个技能的 300-600 行
- **plugins.md**: 10-20 个插件的 400-800 行
- **usage.md**: 200-400 行使用信息

所有文件包含：

- 清晰的结构和标题
- 适当处使用格式化表格
- 指向源文件的链接
- 统计数据和元数据
- 最后更新时间戳
