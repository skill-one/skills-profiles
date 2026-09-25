# 华为云OBS桶创建技能

## 概述

该技能用于在华为云对象存储服务（OBS）上创建桶。它提供了一种简单、交互式的桶创建流程，包括桶名验证、区域选择、访问权限配置以及其他高级选项。

**适用场景**：

- 在华为云OBS上创建新桶
- 设置桶访问权限和策略
- 配置桶区域和存储类别
- 验证桶名是否符合规范
- 批量创建多个桶

## 前置条件

### 1. 已安装华为云CLI工具

必需检查：华为云CLI（hcloud / KooCLI）>= 3.2.0

  ```bash
# 检查是否安装
hcloud version
```

如果未安装，或版本低于3.2.0，请参考 [cli-installation-guide.md](references/cli-installation-guide.md) 进行KooCLI安装。
KooCLI内置了obsutil工具，如果KooCLI版本检查通过，则可以跳过obsutil检查。

### 2. 已配置华为云凭证

- 有效的华为云OBS凭证（AK/SK模式）

```bash
# 查看配置
hcloud obs ls -s

# 配置文件位置 ~/.obsutilconfig
```

如果华为云凭证未配置，提示用户执行以下命令：

```bash
# 配置华为云凭证
hcloud OBS config -i="<您的AK>" -k="<您的SK>" -e="obs.<区域>.myhuaweicloud.com"
```

>**华为云OBS凭证不会继承自华为云凭证，需要单独设置。**

- **安全规则**：
  - 🚫 不要在明文直接输入AK/SK值。
  - 🚫 不要暴露AK/SK值，不要从hcloud配置文件中提取AK/SK。
  - ✅ 仅使用 `hcloud configure list` 检查凭证状态。

## 核心工作流

桶名 `bucket-name` 是创建OBS桶的必要条件。如果上下文未指定桶名，提示用户需要指定一个具体的桶名，无需其他文本提示。

### 第一步：验证桶名

桶名规则如下：
  > 1. 3-63个字符，以数字或字母开头，支持小写字母、数字、"-"、"."。
  > 2. 不允许IP地址格式。
  > 3. 不能以 "-" 或 "." 开头或结尾。
  > 4. 不允许两个相邻的 "."（例如，"my..bucket"）。
  > 5. 不允许相邻的 "." 和 "-"（例如，"my-.bucket" 和 "my.-bucket"）。"

如果桶名不符合规范。提醒用户重置桶名。

### 第二步：选择区域

从上下文中获取要创建的OBS桶的区域。如果未指定区域，则默认使用 ~/.obsutilconfig 文件中的 "endpoint" 参数作为区域。
返回提示文本：
>桶创建成功后，区域无法更改，请谨慎选择。您要创建桶的区域是 ${region}

### 第三步：创建桶

```bash
# 使用推荐配置创建
hcloud OBS mb obs://bucket-name [-acl=xxx] [-location=xxx] [-fs] [-az=xxx] [-sc=xxx]
```

```bash
# 批量创建多个桶。华为云CLI返回脚本退出代码6是正常行为，不是执行错误
./scripts/batch_create_buckets.sh <bucket-name-prefix> <regions>
```

### 第四步：验证成功（可选）

```bash
# 列出所有桶以确认创建成功
hcloud OBS ls

# 检查桶属性
hcloud OBS stat obs://bucket-name
```

如果桶列表包含本次创建的桶名，并且桶信息正常输出，提示创建成功并列出桶的基本信息。

## 核心命令

### 创建存储桶

```bash
hcloud OBS mb obs://bucket-name [-acl=xxx] [-location=xxx] [-fs] [-az=xxx] [-sc=xxx]
```

| 选项 | 描述 | 可能的值 |
|------|------|----------|
| `-acl=xxx` | 访问控制列表 | private, public-read, public-read-write |
| `-location=xxx` | 区域 | cn-north-4, cn-east-2, 等 |
| `-az=xxx` | 可用区 | multi-az |
| `-sc=xxx` | 默认存储类别 | standard, warm, cold, deep-archive |

### 列出存储桶

```bash
hcloud OBS ls
```

### 查看存储桶属性

```bash
hcloud OBS stat obs://${bucket-name}
```

## 参数确认

### 必选参数

- **bucket-name**：存储桶名称，必须符合OBS命名规范（3-63个字符，小写字母、数字、连字符、点，不能以连字符或点开头或结尾）

### 可选参数

- **region**：区域代码，例如 cn-north-4（华北-北京4），cn-east-2（华东-上海2）
- **acl**：访问权限，默认为private
- **storage-class**：存储类别，默认为standard
- **az**：可用区，默认为单可用区，可以设置为multi-az（多可用区）

## 最佳实践

1. **命名规范**：使用有意义的桶名，例如 `project-name-environment-purpose-20250527`
2. **区域选择**：选择离用户最近的区域以减少延迟，北京4（cn-north-4）是一个常用的区域
3. **访问控制**：默认使用private ACL，仅在需要时开放public-read
4. **存储类别**：根据访问频率选择：
   - 标准存储（standard）：频繁访问的数据
   - 低频访问存储（warm）：低频访问的数据
   - 归档存储（cold）：很少访问的数据
   - 深归档存储（deep-archive）：极少访问的数据
5. **批量创建**：使用 `batch_create_buckets.sh` 脚本批量创建多个桶
6. **版本控制**：考虑启用桶版本控制以防止意外删除

## 注意事项

1. **桶名唯一性**：桶名在华为云OBS中全局唯一，不能与其他用户重复
2. **区域不可变性**：创建后不能更改桶的区域
3. **成本**：存储桶免费，但存储数据、请求和流量会产生费用
4. **安全**：不要在脚本中硬编码AK/SK，使用环境变量或配置文件
5. **权限**：确保执行命令的用户具有足够的OBS权限
6. **网络**：确保网络可以访问华为云OBS服务端点
7. **配额**：检查账户的OBS桶数量配额
8. **删除保护**：重要桶可以启用删除保护以防止意外删除

## 参考资料

| 文档 | 描述 |
|------|------|
| [KooCLI安装指南](references/cli-installation-guide.md) | KooCLI安装指南 |
| [常见错误及解决方案](references/trouble-shooting.md) | 错误排查 |
