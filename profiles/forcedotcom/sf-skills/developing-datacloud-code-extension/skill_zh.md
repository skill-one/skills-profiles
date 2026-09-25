# 开发 Salesforce Data Cloud 代码扩展技能

## 概述

此技能为开发、测试和部署到 Salesforce Data Cloud 的自定义 Python 代码扩展提供了完整的工作流程。代码扩展允许您编写读取和写入数据湖对象 (DLO) 和数据模型对象 (DMO) 的 Python 转换。

## 使用场景

- 用户想要创建一个新的代码扩展项目
- 用户需要在本地测试代码扩展
- 用户想要扫描代码以获取所需的权限
- 用户需要将代码扩展部署到 Data Cloud
- 用户正在使用 Data Cloud 转换
- 用户想要以编程方式读取/写入 DLO 或 DMO 数据

## 前置条件检查

在执行任何代码扩展命令之前，请验证以下前置条件：

1. **已安装 SF CLI 插件**
   ```bash
   sf plugins --core | grep data-code-extension
   ```
   如果未安装：
   ```bash
   sf plugins install @salesforce/plugin-data-codeextension
   ```

2. **Python 3.11**
   ```bash
   python --version  # 应显示 3.11.x
   ```

3. **Data Cloud 自定义代码 SDK**
   ```bash
   pip list | grep salesforce-data-customcode
   ```
   如果未安装：
   ```bash
   pip install salesforce-data-customcode
   ```

4. **Docker 正在运行**（仅用于部署）
   ```bash
   docker ps
   ```

5. **已认证的组织**
   ```bash
   sf org display --target-org <org_alias> --json
   ```

## 技能工作流程

### 第一阶段：初始化项目

使用脚手架创建一个新的代码扩展项目。

**命令：**

对于 **基于脚本** 的代码扩展（批处理转换）：
```bash
sf data-code-extension script init --package-dir <directory>
```

对于 **基于函数** 的代码扩展（实时）：
```bash
sf data-code-extension function init --package-dir <directory>
```

**必需选项：**
- `--package-dir, -p` - 包含项目的目录路径

**创建的内容：**
```
my-transform/              # 项目根目录
├── payload/               # CRITICAL: 这是 --package-dir 必须指向的目录以进行部署
│   ├── entrypoint.py      # 主转换代码
│   └── config.json        # 代码扩展配置
├── requirements.txt       # Python 依赖项
└── README.md
```

## 工作流程期间的目录上下文

**IMPORTANT:** 理解目录结构对于成功部署至关重要。

**命令及其目录要求：**

| 命令 | 从何处运行 | 路径/文件参数 |
|-------|----------|-------------------|
| `init` | 父目录 | `<project-name>` 或 `.` |
| `scan` | 项目根目录 | `./payload/entrypoint.py` |
| `run` | 项目根目录 | `./payload/entrypoint.py` |
| `deploy` | 项目根目录 | `--package-dir ./payload` (**必需**) |

**CRITICAL: 部署命令中的 `--package-dir` 参数必须指向 `payload` 目录，而不是项目根目录。**

### 第二阶段：开发转换

编辑 `payload/entrypoint.py` 以添加转换逻辑。

**脚本示例（批处理）：**
```python
from datacustomcode import Client

client = Client()

# 从 DLO 读取
df = client.read_dlo('Employee__dll')

# 转换数据（将职位字段转换为大写）
df['position_upper'] = df['position'].str.upper()

# 写入输出 DLO
client.write_to_dlo('Employee_Upper__dll', df, 'overwrite')
```

**函数示例（实时）：**
```python
from datacustomcode import FunctionClient

def transform(event, context):
    client = FunctionClient(context)
    input_data = event['data']
    output = {
        'name': input_data['name'].upper(),
        'status': 'processed'
    }
    return output
```

**常见操作：**
- `client.read_dlo('DLO_Name__dll')` - 从 DLO 读取
- `client.read_dmo('DMO_Name')` - 从 DMO 读取
- `client.write_to_dlo('DLO_Name__dll', df, 'overwrite')` - 写入 DLO
- `client.write_to_dmo('DMO_Name', df, 'upsert')` - 写入 DMO

### 第三阶段：扫描权限

扫描入口文件以检测所需的权限并生成 config.json。

**命令：**
```bash
sf data-code-extension script scan --entrypoint ./payload/entrypoint.py
```

**检测内容：**
- DLO/DMO 的读取权限
- DLO/DMO 的写入权限
- Python 包依赖项
- 更新 `config.json` 和 `requirements.txt`

### 第四阶段：验证 DLO 模式（测试前检查）

**CRITICAL: 在本地运行测试之前，请验证代码中使用的所有 DLO 是否存在并具有预期的字段。**

#### 第 4a 步：从 config.json 提取 DLO

扫描后，查看生成的 `config.json` 以识别所有 DLO：

```bash
cat payload/config.json
```

#### 第 4b 步：验证每个 DLO 模式

**使用 `getting-datacloud-schema` 技能来验证 DLO 是否存在并检查字段名称。**

对于代码中引用的每个 DLO：

1. **验证 DLO 是否存在：**
   ```bash
   python3 scripts/get_dlo_schema.py <org_alias> <dlo_name>
   ```

2. **验证字段名称是否匹配** — 将 `entrypoint.py` 中使用的字段与 DLO 模式进行比较。

3. **检查所有 DLO：**
   - 验证所有 `read` 权限中的 DLO
   - 验证所有 `write` 权限中的 DLO
   - 检查字段名称是否完全匹配（区分大小写）
   - 验证数据类型是否与操作兼容

#### 第 4c 步：验证清单

在继续运行之前，请确保：

- [ ] config.json 中的所有 DLO 都存在于目标组织
- [ ] 代码中使用的所有字段都存在于 DLO 模式中
- [ ] 字段数据类型与您的转换逻辑匹配
- [ ] 主键字段已正确识别
- [ ] 写入目标 DLO 已创建并可访问

### 第五阶段：本地测试

验证 DLO 模式后，在您的 Data Cloud 组织上本地运行代码扩展。

**命令：**
```bash
sf data-code-extension script run --entrypoint <entrypoint_file> --target-org <org_alias> [options]
```

**选项：**
- `--target-org, -o` - SF CLI 组织别名（必需）
- `--config-file, -c` - 自定义配置文件路径

**如果出现错误：**
- 重新验证 DLO 模式
- 检查字段名称是否完全匹配
- 验证数据类型是否兼容
- 查看错误消息以了解字段/DLO 问题

### 第六阶段：部署到 Data Cloud

将代码扩展部署到 Data Cloud 以进行计划或按需执行。

**CRITICAL: 您必须指定 `--package-dir ./payload` 以指向 init 创建的 payload 目录。**

**命令：**
```bash
sf data-code-extension script deploy --target-org <org_alias> --name <name> --package-dir ./payload --package-version <version> --description <description> [options]
```

**必需选项：**
- `--target-org, -o` - SF CLI 组织别名
- `--name, -n` - 代码扩展部署的名称
- `--package-dir` - 包含 payload 的路径 (**必需** - 从项目根目录运行时必须为 `./payload`)
- `--package-version` - 版本字符串（默认：0.0.1）
- `--description` - 代码扩展的描述

**可选选项：**
- `--cpu-size` - CPU 大小：CPU_L、CPU_XL、CPU_2XL（默认）、CPU_4XL
- `--function-invoke-opt` - 函数调用选项（用于函数类型）
- `--network` - Docker 网络（默认：default）

**部署后：**
- 导航到 Salesforce UI 中的 Data Cloud
- 转到数据转换部分
- 按名称查找您的部署
- 点击“立即运行”以执行
- 计划定期执行

## 错误处理

### 常见问题和解决方案

| 错误 | 解决方案 |
|-------|----------|
| `command data-code-extension not found` | `sf plugins install @salesforce/plugin-data-codeextension` |
| `datacustomcode CLI not found` | `pip install salesforce-data-customcode` |
| `Python version mismatch` | 使用 pyenv: `pyenv install 3.11.0 && pyenv local 3.11.0` |
| `Cannot connect to Docker daemon` | 启动 Docker Desktop |
| `No org found for alias` | `sf org login web --alias <org_alias>` |
| `config.json not found` | `sf data-code-extension script scan --entrypoint ./payload/entrypoint.py` |
| `DLO not found` | 使用 `getting-datacloud-schema` 技能验证 DLO 是否存在，检查拼写和 `__dll` 后缀 |
| `Permission denied writing` | 重新运行扫描，验证目标 DLO 是否存在并可写入 |
| `Deploy fails - wrong directory` | 确保 `--package-dir` 指向 `payload/` 目录，而不是项目根目录 |

## 最佳实践

### 开发
1. 始终在测试前扫描 — 运行扫描后代码更改
2. 首先本地测试 — 在部署前使用 `run` 命令
3. 使用版本控制 — 每次成功测试后提交 git
4. 版本化部署 — 使用语义版本控制（1.0.0、1.1.0 等）
5. 从项目根目录使用 `--package-dir ./payload` 部署

### 性能
- **CPU_L**：小数据集（< 1M 条记录）
- **CPU_2XL**：中等数据集（1M-10M 条记录）
- **CPU_4XL**：大数据集（> 10M 条记录）

### 安全
1. 无硬编码凭证 — 仅使用 SF CLI 身份验证
2. 验证输入数据 — 检查空值和数据类型
3. 限制写入权限 — 仅授予必要的 DLO/DMO 访问权限

## 与其他技能的集成

**与 `getting-datacloud-schema` 技能（验证必需）一起使用：**

`getting-datacloud-schema` 技能对于在测试代码扩展之前验证 DLO 是**必需**的。

**与 Datakit 工作流一起使用：**
1. 通过代码扩展创建 DLO
2. 使用 datakit 工作流将 DLO 映射到 DMO
3. 在段和激活中使用 DMO

## 命令参考

| 命令 | 目的 | 必需参数 |
|---------|---------|---------------|
| `script init` | 创建新的脚本项目 | --package-dir |
| `function init` | 创建新的函数项目 | --package-dir |
| `script scan` | 生成配置 | entrypoint 文件 |
| `script run` | 本地测试 | entrypoint 文件, --target-org |
| `script deploy` | 部署到 Data Cloud | --target-org, --name, --package-dir, --package-version, --description |

## 资源

- SF CLI 插件：https://github.com/salesforcecli/plugin-data-code-extension
- Python SDK：https://github.com/forcedotcom/datacloud-customcode-python-sdk
- Data Cloud 文档：https://help.salesforce.com/s/articleView?id=sf.c360_a_intro.htm
- Python SDK PyPI：https://pypi.org/project/salesforce-data-customcode/

## 注意事项

- 代码扩展在隔离的 Python 3.11 环境中运行
- 仅部署时需要 Docker，本地测试不需要
- 仅使用 SF CLI 身份验证（无单独的凭证文件）
- 扫描命令自动检测代码中的权限
- 本地运行使用实际 Data Cloud 数据（非模拟）
- 部署版本化，可在 UI 中回滚
