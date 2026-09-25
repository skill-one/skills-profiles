# 技能名称

技能的简要描述及其用途。

## 前置条件

列出任何设置要求：
- 需要的环境变量
- 需要的 API 密钥
- 依赖项（已在前面标题中列出）

示例设置：
```bash
export SKILL_API_KEY="your_api_key"
```

## 快速入门

如何快速使用该技能：

```bash
cd <技能目录>
python3 scripts/command.py --option value
```

## 使用示例

### 示例 1：基本使用

```bash
python3 scripts/script.py "输入"
```

输出：
```
此处为预期输出
```

### 示例 2：高级使用

```bash
python3 scripts/script.py "输入" --flag --option value
```

## 命令

所有命令均从技能目录运行。

### 命令 1
```bash
python3 scripts/script1.py --help
python3 scripts/script1.py "参数1" --option value
```

### 命令 2
```bash
python3 scripts/script2.py "参数1" "参数2"
```

## 脚本

- `script1.py` - 该脚本的描述
- `script2.py` - 该脚本的描述

## API 信息

- **基本 URL**： （如适用）
- **速率限制**： （如适用）
- **认证**： （认证方式）
- **文档**： 链接到官方文档

## 故障排除

### 问题 1

**症状**： 问题的描述

**解决方案**：
1. 步骤 1
2. 步骤 2

### 问题 2

**症状**： 问题的描述

**解决方案**：
1. 步骤 1
2. 步骤 2

## 示例

请查看 `examples/` 目录以获取完整工作流示例。

## 参考

- [官方文档](https://example.com)
- [API 参考](https://example.com/api)
- [相关技能](https://github.com/ReScienceLab/opc-skills/tree/main/skills/related-skill)

## 注意事项

- 重要提示 1
- 重要提示 2

---

## 前置标题指南

此文件顶部的 YAML 前置标题是必需的：

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | string | ✓ | 唯一标识符（连字符命名法） |
| `description` | string | ✓ | 技能的作用和使用时机。包含触发关键词和内联的 "使用场景..." 上下文。 |

## 创建您的技能

1. 将此模板复制到 `skills/your-skill-name/`
2. 更新 YAML 前置标题
3. 编写您的 SKILL.md 文档
4. 在 `scripts/` 中添加 Python/Shell 脚本
5. 在 `examples/` 中添加使用示例
6. 更新 `skills.json` 以添加您的技能条目
7. 在提交 PR 之前使用您的代理进行测试
