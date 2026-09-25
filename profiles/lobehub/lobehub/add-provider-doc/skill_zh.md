# 添加新 AI 提供商文档说明

添加新 AI 提供商文档的完整工作流程。

## 概述

1.  创建使用文档（英文 + 中文）
2.  添加环境变量文档（英文 + 中文）
3.  更新 Docker 配置文件
4.  更新 .env.example
5.  准备图片资源

## 第 1 步：创建提供商使用文档

### 必要文件

- `docs/usage/providers/{provider-name}.mdx`（英文）
- `docs/usage/providers/{provider-name}.zh-CN.mdx`（中文）

### 关键要求

- 5-6 张截图展示流程
- 提供商封面图
- 实际注册和仪表盘 URL
- 价格信息提示
- **绝不能包含真实 API 密钥** - 使用占位符

参考：`docs/usage/providers/fal.mdx`

## 第 2 步：更新环境变量文档

### 要更新的文件

- `docs/self-hosting/environment-variables/model-provider.mdx`（英文）
- `docs/self-hosting/environment-variables/model-provider.zh-CN.mdx`（中文）

### 内容格式

```markdown
### `{PROVIDER}_API_KEY`

- 类型：必需
- 描述：来自 {Provider Name} 的 API 密钥
- 示例：`{api-key-format}`

### `{PROVIDER}_MODEL_LIST`

- 类型：可选
- 描述：控制模型列表。使用 `+` 添加，`-` 隐藏
- 示例：`-all,+model-1,+model-2=显示名称`
```

## 第 3 步：更新 Docker 文件

在 ENV 部分的**末尾**更新所有 Dockerfile：

- `Dockerfile`
- `Dockerfile.database`
- `Dockerfile.pglite`

```dockerfile
# {新提供商}
{PROVIDER}_API_KEY="" {PROVIDER}_MODEL_LIST=""
```

## 第 4 步：更新 .env.example

```bash
### {Provider Name} ###
# {PROVIDER}_API_KEY={prefix}-xxxxxxxx
```

## 第 5 步：图片资源

- 封面图
- 3-4 张 API 仪表盘截图
- 2-3 张 LobeHub 配置截图
- 在 LobeHub CDN 上托管：`hub-apac-1.lobeobjects.space`

## 检查清单

- [ ] 英文 + 中文使用文档
- [ ] 英文 + 中文环境变量文档
- [ ] 所有 3 个 Dockerfile 已更新
- [ ] .env.example 已更新
- [ ] 所有图片已准备
- [ ] 文档中无真实 API 密钥
