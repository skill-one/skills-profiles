# 华为云资源查询

> **⚠️ 执行方法（必读）：该技能通过本地Python脚本执行查询。禁止使用hcloud、openstack或其他CLI工具或直接API调用。**
>
> - 查询脚本位于技能目录`scripts/<服务类别>/`下（例如，`scripts/as/list_scaling_groups.py`）
> - 所有脚本和环境检查脚本都在技能包内。**你必须使用`skill action=exec`来执行它们。不要在shell中直接运行。**
> - 关于具体脚本路径和参数，请参考`references/<服务>/guide.md`
> - **不要尝试hcloud、openstack、curl IAM或其他CLI/API方法。该技能不依赖于这些工具。**
> - **所有路径都是相对于技能目录的，即这个SKILL.md所在的目录。**

## 概述

该技能是一个独立的只读查询技能，通过调用华为云Python SDK的本地Python脚本查询华为云资源、可用规格和现有资源信息。

该技能适用于以下场景：

1. 查询特定区域的可用云资源规格
2. 查询某个操作系统可用的镜像
3. 查询云硬盘类型和现有云硬盘信息
4. 查询现有资源及其关键属性
5. 查询通过Terraform或其他IaC工具未创建的资源
6. 为自动化配置、资源验证或环境清单准备真实参数
7. 获取可重用信息，如资源ID、名称、规格、镜像、网络和硬盘

该技能不负责：

1. 创建资源
2. 修改资源
3. 删除资源
4. 推测或编造未查询过的信息

---

## 能力范围

该技能通过scripts目录中的分类脚本提供查询能力，并通过references目录中的分类指南提供使用说明。
该技能提供的能力包括：

1. 查询资源列表
2. 查询单个资源详情
3. 查询可用规格、镜像和硬盘类型等选择信息
4. 查询现有资源的关键标识符和依赖关系

---

## 使用原则

重要提示：在该技能中执行的脚本路径都是技能目录下的相对路径，即这个SKILL.md所在的目录。

1. 该技能仅执行查询，不执行任何写操作
2. 优先使用用户明确指定的信息，如区域、项目、AZ、资源名称、资源ID等
3. 查询结果必须基于实际API响应；不要根据经验推断
4. 返回结果应优先保留后续可重用的关键字段
5. 当结果集较大时，先通过区域、名称、id、状态、标签等条件缩小范围
6. 如果当前资源类型没有对应的脚本或指南，明确说明不支持；不要返回不可靠的结果
7. 如果用户未提供必要的范围信息，且环境中没有默认值，执行查询前先与用户确认
8. 直接按照guide.md执行；不要查看scripts目录中的脚本内容
9. 当输出较大时缓存结果
10. 执行每个脚本前必须运行`-h`查看使用说明
11. 不要编造脚本名称。按照guide.md中的脚本名称执行。如果脚本名称不在guide.md中，则表示不支持

---

## 前置条件

**你必须先运行环境检查脚本，以一次性完成环境验证和依赖安装：**

- Linux / macOS: `skill action=exec: bash skill://scripts/check_env.sh`
- Windows: `skill action=exec: powershell -ExecutionPolicy Bypass -File skill://scripts/check_env.ps1`

> Windows注意：不要使用`&&`连接命令（PowerShell 5.x不支持）。如果需要先更改目录，请使用分号。

脚本将按顺序检查：Python >= 3.6 → 安装依赖 → 验证SDK → 验证凭证 → 验证服务可用性。如果环境检查失败，请在继续其他脚本前修复问题。

**环境变量：**

| 变量 | 必填 | 描述 |
|------|------|------|
| HW_ACCESS_KEY | 是 | 华为云AK |
| HW_SECRET_KEY | 是 | 华为云SK |
| HW_REGION_NAME | 否 | 默认cn-north-4 |
| HW_PROJECT_ID | 否 | 项目ID（未设置时通过IAM API自动获取） |
| HW_SECURITY_TOKEN | 否 | 使用临时AK/SK时需要 |

**不要输出上述环境变量的值。** 其他资源脚本所需的额外参数（可用区、企业项目等），请参考相应的guide.md。

---

## 执行流程

**当该技能被调用时，你必须按照以下步骤操作。不要等待用户再次提示：**

### 第一步：环境准备

运行环境检查脚本以确保依赖已安装和凭证已配置：

- Linux / macOS: `skill action=exec: bash skill://scripts/check_env.sh`
- Windows: `skill action=exec: powershell -ExecutionPolicy Bypass -File skill://scripts/check_env.ps1`

如果环境检查失败，请按提示修复问题并重新运行，直到通过。

### 第二步：识别并执行查询脚本

1. 根据用户的查询意图，读取`references/<服务>/guide.md`以确定要执行的脚本路径和参数
2. 首先运行`-h`查看脚本使用说明：
   - Linux / macOS: `skill action=exec: skill://.venv/bin/python3 skill://scripts/<服务>/<脚本>.py -h`
   - Windows: `skill action=exec: skill://.venv/Scripts/python3.exe skill://scripts/<服务>/<脚本>.py -h`
3. 根据用户需求组装参数并执行脚本：
   - Linux / macOS: `skill action=exec: skill://.venv/bin/python3 skill://scripts/<服务>/<脚本>.py <参数>`
   - Windows: `skill action=exec: skill://.venv/Scripts/python3.exe skill://scripts/<服务>/<脚本>.py <参数>`
4. 格式化结果并返回给用户

**重要提示：**

- 所有脚本和环境检查脚本都在技能包内。**你必须使用`skill action=exec`来执行它们。不要在shell中直接运行。**
- check_env脚本会自动创建venv。在Linux/macOS上，Python位于`.venv/bin/python3`；在Windows上，位于`.venv/Scripts/python3.exe`
- 不要直接用`python3`执行脚本
- 不要读取scripts目录中的脚本源代码；只需遵循guide.md中的说明
- 当输出较大时缓存结果
- `--project_id`参数是可选的；未提供时，会根据区域通过IAM API自动获取

---

## 目录结构

目录规范如下（所有路径都是相对于技能目录的）：

1. `scripts/<资源类别>/`包含相应的Python查询脚本。无需阅读脚本内容；只需按照guide.md中的说明执行脚本
2. `references/<资源类别>/guide.md`包含相应资源的使用指南
3. 每个脚本负责一个清晰的单个查询动作
4. 每个资源类别必须至少维护一个guide.md来记录脚本能力、参数和使用说明

---

## 参数确认

执行查询脚本前，确认以下参数：

| 参数 | 必填 | 描述 |
|------|------|------|
| region | 是 | 华为云区域，例如cn-north-4 |
| --project_id | 否 | 项目ID；未提供时自动获取 |
| --availability_zone | 否 | 可用区；某些资源查询需要 |

脚本特定参数，请参考`references/<服务>/guide.md`。

---

## 输出格式

查询结果以JSON格式输出，并包含以下常见字段：

- `total`：匹配资源总数
- `items`：资源列表，每个资源包含id、名称、状态等关键字段
- 具体字段因资源类型而异；请参考每个guide.md了解详情

---

## 验证方法

1. 运行环境检查脚本以确认依赖和凭证可用
2. 使用`-h`参数查看脚本使用说明并确认参数正确
3. 对已知资源执行查询，并与控制台数据进行比较以验证结果准确性
4. 检查返回的`total`计数是否合理

---

## 最佳实践

1. 首先缩小查询范围（指定区域、可用区等）以避免返回过多数据
2. 使用`--help`查看脚本支持的所有参数列表
3. 当结果较大时，本地缓存查询结果以避免重复请求
4. 当需要多个资源信息时，按依赖顺序查询（例如，先查询VPC，再查询子网）
5. 当脚本执行失败时，首先检查环境变量和网络连接

---

## 参考文档

- 每个服务查询脚本的使用指南：`references/<服务>/guide.md`

---

## 注意事项

1. 该技能仅提供只读查询能力；不执行任何写操作
2. 不要输出环境变量（如HW_ACCESS_KEY和HW_SECRET_KEY）的值
3. 所有脚本必须通过`skill action=exec`执行；不要在shell中直接运行
4. 不要猜测脚本名称。严格按guide.md中的名称执行。如果脚本名称不在guide.md中，则表示不支持
5. 查询前必须运行环境检查脚本
6. 使用临时AK/SK时，需要设置HW_SECURITY_TOKEN
