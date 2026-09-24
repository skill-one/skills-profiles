# Higgsfield Soul 角色

训练面部高度一致的身份模型。可在所有 Soul 驱动的版本中复用。

## Step 0 — 引导

在任何其他命令之前：

1. 如果 `higgsfield` 不在 `$PATH` 中，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 因 `Session expired` / `Not authenticated` 而失败，请让用户运行 `higgsfield auth login`（交互式）并等待确认。
3. Soul 训练需要付费套餐（Basic+）。如果 `higgsfield account status` 显示免费套餐，请在提交前告知用户。

## UX 规则

1. 简洁明了。聊天中不要出现原始 ID。只需说“Soul 就绪”并附带名称引用。
2. 检测语言并用对应语言回应。CLI 参数保持英文。
3. 询问最少需要的信息：名称 + 照片。选择合适的模型版本。
4. 轮询为静默操作——训练需要几分钟。不要重复状态更新。

## 工作流程

1. **获取名称。** 一个词，供后续引用使用。如缺失则询问。
2. **获取照片。** 5–20 张面部照片，角度和光线多样。本地路径或已上传的 ID 均可使用——`--image` 均可接受。
3. **选择版本。**
   - `--soul-2` — 用于图像生成（默认）
   - `--soul-cinematic` — 用于电影感 / 视频工作
   根据用户所述下游用途选择。默认使用 `--soul-2`。
4. **提交。**
   ```bash
   higgsfield soul-id create --name "<name>" --soul-2 --image ./photo1.png --image ./photo2.png ...
   higgsfield soul-id create --name "<name>" --soul-2 --image <upload_id] --image <upload_id) ...
   ```
   CLI 自动上传路径。捕获返回的引用 ID。
5. **等待。** `higgsfield soul-id wait <id>`。静默操作。默认超时 30 分钟。
6. **交付。** “Soul `<name>` 就绪。在 generate 中使用 `--soul-id <id>`。”

## 使用 Soul

训练完成后，将其传递给 `higgsfield-generate`：

```bash
higgsfield generate create text2image_soul_v2 --prompt "..." --soul-id <ref_id] --quality 2k --wait
higgsfield generate create soul_cinematic --prompt "..." --soul-id <ref_id] --quality 2k --wait
```

## 列出已存在的 Soul

```bash
higgsfield soul-id list                   # 所有引用
higgsfield soul-id get <id]               # 通过 ID 查询单个
```

## 错误

- `Minimum Basic plan required` — 用户使用的是免费套餐；请告知他们。
- `Training failed` — 检查照片质量（5 张以上独特面部，光线充足）。
- `Session expired` → `higgsfield auth login`。

## 参考文档

- `references/photo-guide.md` — 哪些照片效果最佳
- `references/troubleshooting.md` — 常见的训练失败问题
