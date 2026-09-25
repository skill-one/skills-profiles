# bangumi-frames — Bilibili动漫帧与角色组织器

## 概述

提供一个Bilibili视频（一个bangumi `ep`链接、UP上传的`BV`链接/ID，或**本地视频文件**）；它将下载→提取场景变换关键帧→分割场景与角色帧→组织角色裁剪。**单次处理，两种模式：**

- **无`--ref`（聚类模式）** — 将每个角色裁剪按CCIP身份分组到`characters/char_NN/`。
- **带`--ref DIR`（一对一模式）** — 给定一个角色的参考文件夹，将视频中匹配该角色的所有裁剪拉入`matched/`，文件名前缀为距离（按距离从近到远），因此一个紧密阈值会产生一个纯净的集合。

模型是**动漫特定的**（deepghs动漫人物检测 + CCIP角色身份嵌入） — 它们不适用于真人实拍素材。

## 何时使用 / 何时不用

- **使用**当用户想要从Bilibili视频中收集/提取/组织动漫帧或截图 — 按角色、按场景，或提取出特定人物时。
- **不用**用于真人实拍视频（需要insightface类的面堆栈）、或用于通用视频编辑/裁剪/转码。

## 预装资源

| 资源 | 何时阅读 |
|---|---|
| `references/pipeline.md` | 调整阶段 — 下载(`--height`/`--prefer`)、提取(`--scene`/`--interval`/`--dedup`/`--skip`)、`--clean`（OCR+LaMa字幕/水印移除）、分类(`--conf`/`--min-area`）；特征缓存；CPU/CoreML规则；`--redo` |
| `references/modes.md` | 选择/调整两种模式 — 模式1聚类(`--eps`/`--min-samples`) vs 模式2一对一(`--ref-eps`，距离带直方图，压缩嵌入阈值逻辑）；完整输出布局 |
| `scripts/bangumi_frames.py` | 入口点（所有阶段+两种模式） |
| `scripts/remove_overlay.py` | 独立字幕/水印移除，作用于帧目录或单张图像 |

## 前置条件

1. `ffmpeg`在PATH中；`yt-dlp`在PATH中用于下载（本地文件输入会跳过下载）。
2. Python 3.9+，`pip install dghs-imgutils`（首次运行从HuggingFace拉取~300MB的模型，然后本地缓存）。
3. 一个Bilibili Cookie（Netscape `cookies.txt`）。解析顺序：
   `--cookies` > `$BILIBILI_COOKIES` > `~/bb_up/bb_cookies/www.bilibili.com_cookies.txt`。
   1080p+ / 会员专属集数需要带会员信息的Cookie；预览下载意味着Cookie无法访问该集数。本地文件输入无需Cookie。
4. **在CPU上运行CCIP步骤** — 不要设置`ONNX_MODE=CoreML`（CCIP崩溃；脚本在聚类/匹配前会弹出它）。人物检测可以在CoreML上正常工作。
5. （仅用于`--clean`）`pip install rapidocr-onnxruntime simple-lama-inpainting`。
6. （仅用于`--engine pyscenedetect`）`pip install scenedetect`。

## 使用方法

```bash
SKILL=skills/bangumi-frames/scripts/bangumi_frames.py

# 模式1 — 将所有人聚类到char_NN组
python3 $SKILL https://www.bilibili.com/video/BV15qVm68E2h --out ~/frames
python3 $SKILL ep1231575 --out ~/frames           # ep / BV ID也接受
python3 $SKILL ~/local.mp4 --out ~/frames          # 本地文件，跳过下载

# 模式2 — 提取一个角色（参考文件夹=约200个该角色的裁剪）
python3 $SKILL BV15qVm68E2h --ref ~/refs/紫灵 --ref-eps 0.04 --out ~/frames

# 可选：分析前移除烧入字幕+水印
python3 $SKILL ep1231575 --clean --out ~/frames
```

阶段是幂等的（当输出已存在时，阶段会被跳过；聚类/匹配总是重新运行，因为CCIP特征被缓存了）。对于每个标志，各阶段的权衡，以及阈值逻辑，请阅读上述两个参考文件。

**Agent原生输出：** `stdout`是一个单一的JSON信封（成功时为`{"ok", "data", "next", "meta"}`，失败时为`{"ok": false, "error"}` — 管道时为JSON，TTY上为人类摘要；用`--format`强制），`stderr`携带人类进度日志，退出码是稳定的（`0`成功 · `1`运行时 · `2`认证 · `3`验证）。使用`--dry-run`预览计划而不下载，`--schema`打印输出契约。详情在`references/pipeline.md`。

## 输出

```
<out>/<id>/                     # id = BV ID / ep ID / 本地文件名
├── frames/  frames.json        # 关键帧+时间戳
├── scenery/                    # 未检测到角色的帧
├── crops/  features.npy        # 角色裁剪+缓存的CCIP特征
├── detect.json                 # 帧->人物框/裁剪
├── characters/                 # 模式1: char_NN_crop/+char_NN_full/（配对），_unsorted/, _montage.png
├── matched/                    # 模式2: 0.012_<裁剪>.jpg（按距离前缀）+ index.json
├── matched_montage.png         # 模式2样本蒙太奇
└── index.json                  # 模式1: 角色组->{裁剪, 帧, 时间}
```

运行后，先查看`characters/_montage.png`（模式1）或`matched_montage.png`（模式2）判断质量，然后阅读`index.json`。分组/匹配失败时，参考`references/modes.md`调整。

## 限制

- 仅限动漫/2.5D渲染艺术；真人实拍需要不同的（人脸识别）堆栈。
- CCIP可能将一个角色的不同形态（服装/变身）分成不同组 — 通常对“按视觉外观分组”足够好；对于模式2，将每种形态放入参考文件夹。
- Bilibili上的1080p+需要会员Cookie；下载仅用于个人离线分析，不会上传任何内容。
