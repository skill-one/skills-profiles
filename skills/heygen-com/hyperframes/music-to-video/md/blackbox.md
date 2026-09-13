# music-to-video (`heygen-com/hyperframes/music-to-video`)

## blackbox

**function**: 把一首歌变成一支卡点视频 (MP4): 画面内容、切换时机全部跟着音乐的节奏和情绪走。

- input: 一个音乐文件 (如 bgm.mp3), 没有给任何图片, output: 一支完整的 MP4 视频: 用动态大字文案/歌词填满画面, 每次切换都踩在节拍上
- input: 一首歌 + 一批照片或短视频, output: 一支卡点幻灯片/混剪视频: 你的照片和片段被剪到同一个节拍网格上, 在鼓点上切换
- input: 一句氛围描述 (如「深夜开车的电子乐, 发个朋友圈」), output: 先按描述生成匹配的音乐, 再输出一支竖屏/横屏的完整成片 MP4, 自带封面帧
