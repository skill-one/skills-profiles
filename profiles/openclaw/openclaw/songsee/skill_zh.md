# songsee

从音频中生成频谱图 + 特征面板。

快速入门

- 频谱图：`songsee track.mp3`
- 多面板：`songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux`
- 时间切片：`songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg`
- 标准输入：`cat track.mp3 | songsee - --format png -o out.png`

常用标志

- `--viz` 列表（可重复或逗号分隔）
- `--style` 调色板（classic, magma, inferno, viridis, gray）
- `--width` / `--height` 输出尺寸
- `--window` / `--hop` FFT设置
- `--min-freq` / `--max-freq` 频率范围
- `--start` / `--duration` 时间切片
- `--format` jpg|png

备注

- WAV/MP3原生解码；其他格式若可用则使用ffmpeg。
- 多个`--viz`将渲染为网格。
