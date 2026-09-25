# TAO 技能库功能

> **是否需要独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

当用户询问 `tao-skill-bank` 能做什么、插件功能、有哪些可用应用程序或数据工作流、支持哪些模型或哪些模型支持 AutoML 时，请使用此技能。

## 快速入门

对于一般功能问题，请运行 `scripts/list_tao_capabilities.py`；对于模型/操作和 AutoML 支持问题，请运行 `scripts/list_tao_models.py`。

## 功能回答

对于一般功能回答，请运行打包好的辅助工具：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skill-bank}/scripts/list_tao_capabilities.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skill-bank} --format text
```

使用辅助工具的输出作为答案的来源，而不是手动从此技能或插件元数据中列举功能。包括：

- `applications/` 下每个顶级应用程序工作流及其功能。
- `data/` 下每个顶级数据工作流及其功能。
- 支持的执行平台，从已安装的平台技能（tao-run-on-docker / -slurm / -kubernetes / -brev，以及任何外部平台）；在仅显示核心路由技能的运行时环境中，请读取 `skills/platform/tao-run-on-*/SKILL.md` 的 frontmatter 部分。
- `models/` 下模型的微调/部署工作流覆盖范围：当打包的 schema manifest 中存在训练、评估、推理、导出和 TensorRT 引擎生成等操作时，包括这些功能。

AutoML 支持和每个操作的 AutoML schema 门控。

## 模型列表

当用户询问哪些 TAO 模型可用或模型能运行哪些操作时，请使用打包好的模型列表脚本，而不是手动扫描模型文件夹：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skill-bank}/scripts/list_tao_models.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skill-bank} --scope all --format text
```

模型列表来自 `skills/models/schemas.manifest.json`。

## AutoML 列表

当用户询问哪些模型支持 AutoML 时，请使用 AutoML 模式下的相同模型列表脚本或兼容性包装器：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skill-bank}/scripts/list_tao_models.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skill-bank} --scope automl --format text
```

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skill-bank}/scripts/list_automl_support.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skill-bank} --format text
```

当用户询问特定压缩操作时，请使用 `--action distill`、`--action prune` 或 `--action quantize`。

一个操作需要 `skills/models/<model_skill>/schemas/<action>.schema.json` 打包到插件中并成功解析为 JSON。如果该数据类 schema 缺失或无效，请不要描述模型/操作为支持 AutoML。
