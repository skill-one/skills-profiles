# 品牌

品牌标识、声音、信息传递、资产管理以及一致性框架。

## 使用场景

- 定义品牌声音和内容语气指导
- 视觉标识标准及风格指南开发
- 信息传递框架创建
- 品牌一致性审查和审计
- 资产组织、命名和审批
- 色彩调板管理和字体规范

## 脚本路径

本技能及其 `references/` 中的脚本路径相对于包含此 `SKILL.md` 的目录，而不是项目路径：`scripts/<文件>` 是本技能自有的 `scripts/` 文件夹，而 `../<技能>/scripts/<文件>` 是与其一同安装的兄弟子技能。从该目录（Claude Code 在技能加载时报告为技能的基本目录）构建完整路径，并将工作目录保持在项目根目录——脚本相对于它读取和写入项目文件，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 快速入门

**向提示注入品牌上下文：**
```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
```

**验证资产：**
```bash
node scripts/validate-asset.cjs <资产路径>
```

**提取/比较颜色：**
```bash
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <图像路径>
```

## 品牌同步工作流

```bash
# 1. 编辑 docs/brand-guidelines.md（或使用 /brand update）
# 2. 同步到设计调板
node scripts/sync-brand-to-tokens.cjs
# 3. 验证
node scripts/inject-brand-context.cjs --json | head -20
```

同步会在检测到现有调板文件、`:root` 自定义属性或常见 CSS 入口及其本地 CSS 导入中的 Tailwind v4 `@theme` 变量，或 Tailwind 主题颜色和预设时停止。在进行下一步操作前审查报告的源文件。如果检测到的文件是先前同步管理的 `assets/design-tokens.*` 输出，且替换它们是故意的，请使用 `--force` 重新运行。

**同步的文件：**
- `docs/brand-guidelines.md` → 真实来源
- `assets/design-tokens.json` → 调板定义
- `assets/design-tokens.css` → CSS 变量

## 子命令

| 子命令 | 描述 | 参考 |
|------------|-------------|-----------|
| `update` | 更新品牌标识并同步到所有设计系统 | `references/update.md` |

## 参考

| 主题 | 文件 |
|-------|------|
| 声音框架 | `references/voice-framework.md` |
| 视觉标识 | `references/visual-identity.md` |
| 信息传递 | `references/messaging-framework.md` |
| 一致性 | `references/consistency-checklist.md` |
| 指南模板 | `references/brand-guideline-template.md` |
| 资产组织 | `references/asset-organization.md` |
| 色彩管理 | `references/color-palette-management.md` |
| 字体 | `references/typography-specifications.md` |
| Logo 使用 | `references/logo-usage-rules.md` |
| 审批清单 | `references/approval-checklist.md` |

## 脚本

| 脚本 | 目的 |
|--------|---------|
| `scripts/inject-brand-context.cjs` | 提取用于提示注入的品牌上下文 |
| `scripts/sync-brand-to-tokens.cjs` | 同步 brand-guidelines.md → design-tokens.json/css |
| `scripts/validate-asset.cjs` | 验证资产命名、大小、格式 |
| `scripts/extract-colors.cjs` | 提取并比较与调板的颜色 |

## 模板

| 模板 | 目的 |
|----------|---------|
| `templates/brand-guidelines-starter.md` | 新品牌完整的起始模板 |

## 路由

1. 从 `$ARGUMENTS`（第一个单词）解析子命令
2. 加载对应的 `references/{子命令}.md`
3. 使用剩余参数执行
