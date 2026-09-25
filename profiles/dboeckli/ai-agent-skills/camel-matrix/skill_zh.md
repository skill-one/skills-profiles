# Camel Spring Boot 兼容性矩阵

运行 `scripts/camel-springboot-matrix.sh`（包含在此技能中）以相对于当前项目目录生成 `target/camel-springboot-matrix.md`。如果 `target/` 目录不存在，则会自动创建该目录。

## 参数

用户可以提供一个可选的版本范围：`$ARGUMENTS`

- 无参数：使用默认范围 `4.14.0` 到最新版本（见下文）
- 两个参数（例如 `4.0.0 4.15.0`）：仅处理该范围内的版本

## 步骤

1. 运行脚本。如果用户未提供版本范围，则默认将 `4.14.0` 作为最小值，并省略最大参数（因此脚本会获取到最新可用版本）：

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/camel-springboot-matrix.sh" ${ARGUMENTS:-4.14.0}
```

2. 完成后，报告：
   - 处理了多少个 Camel 版本
   - 在当前项目目录中创建了/更新了 `target/camel-springboot-matrix.md`
   - 生成的表格的最后 5 行，以便用户可以验证输出
