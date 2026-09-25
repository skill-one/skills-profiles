# 华为云资源查询

> **⚠️ 执行方法（必读）：该技能通过本地 Python 脚本执行查询。禁止使用 hcloud、openstack 或其他 CLI 工具或直接 API 调用。**
>
> - 查询脚本位于技能目录 `scripts/<服务类别>/` 下（例如 `scripts/as/list_scaling_groups.py`）
> - 所有脚本和环境检查脚本都在技能包内。**你必须使用 `skill action=exec` 来执行它们；不要在 shell 中直接运行**
> - 关于具体脚本路径和参数，请参阅 `references/<服务>/guide.md`
> - **不要尝试 hcloud、openstack、curl IAM 或其他 CLI/API 方法；该技能不依赖这些工具**
> - **所有路径都是相对于技能目录的，即包含此 SKILL.md 的目录**

## 概述

该技能是一个独立的只读查询技能，通过调用华为云 Python SDK 的本地 Python 脚本查询华为云资源、可用规格和现有资源信息。

该技能适用于以下场景：

1. 查询指定区域的可用云资源规格
2. 查询特定操作系统的可用镜像
3. 查询云盘类型和现有云盘信息
4. 查询现有资源及其关键属性
5. 查询通过 Terraform 或其他 IaC 工具未创建的资源
6. 为自动化配置、资源验证或环境清单准备真实参数
7. 获取可重用信息，如资源 ID、名称、规格、镜像、网络和磁盘

该技能不处理以下内容：

1. 创建资源
2. 修改资源
3. 删除资源
4. 猜测或编造未查询的信息

---

## 能力范围

该技能通过 scripts 目录中的分类脚本提供查询能力，并通过 references 目录中的分类指南提供使用说明。
该技能提供的能力包括：

1. 查询资源列表
2. 查询单个资源详情
3. 查询可用规格、镜像和磁盘类型等选择信息
4. 查询现有资源的关键标识符和依赖关系

---

## 使用原则

重要提示：该技能内执行的脚本路径都相对于技能目录，即包含此 SKILL.md 的目录

1. 该技能仅执行查询，不执行任何写操作
2. 优先使用用户明确指定的信息，如区域、项目、AZ、资源名称和资源 ID
3. 查询结果必须基于实际 API 响应；不要根据经验推测
4. 返回结果应保留后续重用的关键字段
5. 当结果集较大时，优先通过区域、名称、id、状态和标签等条件缩小范围
6. 如果当前资源类型没有相应的脚本或指南，明确说明不支持；不要返回不可靠的结果
7. 如果用户未提供必要的范围信息，且环境中没有默认值，请在执行查询前确认信息
8. 直接根据 guide.md 执行；不要在 scripts 目录中读取脚本内容
9. 当输出较大时缓存结果
10. 每次执行脚本前都必须使用 `-h` 查看使用说明
11. 不要编造脚本名称；根据 guide.md 中的脚本名称执行。如果脚本名称不在 guide.md 中，则表示不支持

---

## 前置条件

**使用前，你必须运行环境检查脚本，以一次性完成环境验证和依赖安装：**

- Linux / macOS: `skill action=exec: bash skill://scripts/check_env.sh`
- Windows: `skill action=exec: powershell -ExecutionPolicy Bypass -File skill://scripts/check_env.ps1`

> Windows 注意：不要使用 `&&` 连接命令（PowerShell 5.x 不支持此功能）；如果需要先更改目录，请使用分号

脚本将按顺序检查：Python >= 3.6 → 安装依赖 → 验证 SDK → 验证凭证 → 验证服务可用性。如果环境检查失败，请在继续其他脚本前解决问题。

**环境变量：**

| 变量 | 是否必需 | 描述 |
|------|----------|-------|
| HW_ACCESS_KEY | 是 | 华为云 AK |
| HW_SECRET_KEY | 是 | 华为云 SK |
| HW_REGION_NAME | 否 | 默认 cn-north-4 |
| HW_PROJECT_ID | 否 | 项目 ID（如果未设置，则通过 IAM API 自动获取） |
| HW_SECURITY_TOKEN | 否 | 临时 AK/SK 所需 |

**不要输出上述环境变量的值。** 对于需要额外参数（可用区、企业项目等）的其他资源脚本，请参阅相应的 guide.md。

---

## 执行流程

**当该技能被调用时，你必须按照以下步骤操作；不要等待用户再次提示：**

### 第一步：环境准备

执行环境检查脚本，确保依赖已安装且凭证已配置：

- Linux / macOS: `skill action=exec: bash skill://scripts/check_env.sh`
- Windows: `skill action=exec: powershell -ExecutionPolicy Bypass -File skill://scripts/check_env.ps1`

如果环境检查失败，请按提示解决问题并重新执行，直到通过。

### 第二步：识别并执行查询脚本

1. 根据用户的查询意图，读取 `references/<服务>/guide.md` 以确定要执行的脚本路径和参数
2. 首先执行 `-h` 查看脚本使用说明：
   - Linux / macOS: `skill action=exec: skill://.venv/bin/python3 skill://scripts/<服务>/<脚本>.py -h`
   - Windows: `skill action=exec: skill://.venv/Scripts/python3.exe skill://scripts/<服务>/<脚本>.py -h`
3. 根据用户需求组装参数并执行脚本：
   - Linux / macOS: `skill action=exec: skill://.venv/bin/python3 skill://scripts/<服务>/<脚本>.py <参数>`
   - Windows: `skill action=exec: skill://.venv/Scripts/python3.exe skill://scripts/<服务>/<脚本>.py <参数>`
4. 格式化结果并返回给用户

**重要提示：**

- 所有脚本和环境检查脚本都在技能包内。**你必须使用 `skill action=exec` 来执行它们；不要在 shell 中直接运行**
- check_env 脚本会自动创建 venv。在 Linux/macOS 上，Python 位于 `.venv/bin/python3`；在 Windows 上，位于 `.venv/Scripts/python3.exe`
- 不要直接使用 `python3` 执行脚本
- 不要在 scripts 目录中读取脚本源代码；根据 guide.md 中的说明执行
- 当输出较大时缓存结果
- `--project_id` 参数是可选的；如果未提供，则根据区域通过 IAM API 自动获取

---

## 目录结构

目录规范如下（所有路径都相对于技能目录）：

1. scripts/<资源类别>/ 包含相应资源的 Python 查询脚本。你不需要阅读脚本内容；根据 guide.md 中的使用说明执行脚本
2. references/<资源类别>/guide.md 包含相应资源的使用指南
3. 每个脚本负责一个清晰的单个查询动作
4. 每个资源类别至少维护一个 guide.md，以描述脚本功能、参数和使用方法

---

## 参数确认

在执行查询脚本前，确认以下参数：

| 参数 | 是否必需 | 描述 |
|------|----------|-------|
| region | 是 | 华为云区域，例如 cn-north-4 |
| --project_id | 否 | 项目 ID；如果未提供，则自动获取 |
| --availability_zone | 否 | 可用区；某些资源查询需要 |

对于特定脚本的参数，请参阅 `references/<服务>/guide.md`。

---

## 输出格式

查询结果以 JSON 格式输出，包含以下常见字段：

- `total`: 匹配资源总数
- `items`: 资源列表，每个资源包含 id、name 和 status 等关键字段
- 具体字段因资源类型而异；请参阅各个 guide.md 文件了解详情

---

## 验证方法

1. 执行环境检查脚本，确认依赖和凭证可用
2. 使用 `-h` 参数查看脚本使用说明，确认参数正确
3. 对已知资源执行查询，并与控制台数据进行比较以验证结果准确性
4. 检查返回的 `total` 计数是否合理

---

## 最佳实践

1. 首先缩小查询范围（指定区域、可用区等），以避免返回过多数据
2. 使用 `--help` 查看脚本支持的完整参数列表
3. 当结果较大时，本地缓存查询结果以避免重复请求
4. 当需要多个资源信息时，按依赖顺序查询（例如，先查询 VPC，再查询子网）
5. 当脚本执行失败时，首先检查环境变量和网络连接

---

## 参考文档

- 每个服务的查询脚本使用指南：`references/<服务>/guide.md`

---

## 注意事项

1. 该技能仅提供只读查询能力；不执行任何写操作
2. 不要输出 HW_ACCESS_KEY 和 HW_SECRET_KEY 等环境变量的值
3. 所有脚本都必须通过 `skill action=exec` 执行；不要在 shell 中直接运行
4. 不要编造脚本名称；严格根据 guide.md 中的名称执行
5. 查询前必须运行环境检查脚本
6. 使用临时 AK/SK 时，需要设置 HW_SECURITY_TOKEN
