# 希格斯场灵魂角色

训练一个面部忠实身份模型。可在所有基于灵魂的生成中复用。

## 第 0 步 — 引导

在任何其他命令之前：

1. 如果 `higgsfield` 不在 `$PATH` 中，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 失败并显示 `Session expired` / `Not authenticated`，请提示用户运行 `higgsfield auth login`（交互式）并等待确认。
3. 灵魂训练需要一个付费计划（Basic+）。如果 `higgsfield account status` 显示免费计划，请在提交前告知用户。

## 用户体验规则

1. 保持简洁。聊天中不要直接使用原始 ID。只需引用名称并说 "Soul ready"。
2. 检测语言并以该语言响应。CLI 标志保持英文。
3. 请求最小的输入集：名称 + 照片。选择一个合理的模型变体。
4. 检查状态是静默的——训练需要几分钟。不要重复状态更新。

## 工作流程

1. **获取名称。** 一个单词，用于后续引用。如果缺失，请询问。
2. **获取照片。** 5-20 张面部照片，角度和光照多样化。本地路径或已上传的 ID 都可以——`--image` 接受两者。
3. **选择变体。**
   - `--soul-2` — 用于图像生成（默认）
   - `--soul-cinematic` — 用于电影感/视频工作
   根据用户声明的下游用途选择。默认为 `--soul-2`。
4. **提交。**
   ```bash
   higgsfield soul-id create --name "<name>" --soul-2 --image ./photo1.png --image ./photo2.png ...
   higgsfield soul-id create --name "<name>" --soul-2 --image <upload_id> --image <upload_id> ...
   ```
   CLI 自动上传路径。捕获返回的引用 ID。
5. **等待。** `higgsfield soul-id wait <id>`。静默。默认超时 30 分钟。
6. **交付。** "Soul `<name>` ready. Use in generate with `--soul-id <id>`。"

## 使用灵魂

训练完成后，将其传递给 `higgsfield-generate`：

```bash
higgsfield generate create text2image_soul_v2 --prompt "..." --soul-id <ref_id> --quality 2k --wait
higgsfield generate create soul_cinematic --prompt "..." --soul-id <ref_id> --quality 2k --wait
```

## 列出现有的灵魂

```bash
higgsfield soul-id list                   # 所有引用
higgsfield soul-id get <id>               # 通过 ID 获取一个
```

## 错误

- `Minimum Basic plan required` — 用户使用免费计划；告知他们。
- `Training failed` — 检查照片质量（5+ 张独特的面部，光线充足）。
- `Session expired` → `higgsfield auth login`。

## 参考文档

- `references/photo-guide.md` — 最佳照片类型
- `references/troubleshooting.md` — 常见训练失败
