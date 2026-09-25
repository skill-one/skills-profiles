# Edge-TTS

使用 Microsoft Edge 的神经 TTS 服务通过 `uvx edge-tts` 命令生成高质量的文本转语音音频。
支持多种语言、声音、可调节的速度/音调以及字幕生成。

## 使用方法
```shell
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3

# 带字幕
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --write-subtitles -
```

## 调整速率（速度）、音量和音调
```shell
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --rate=+50%
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --volume=+50% --pitch=-50Hz
```

## 更换声音
```shell
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --voice zh-CN-XiaoxiaoNeural
```

## 可用的声音
```
名称                               性别    内容类别      声音个性
en-GB-LibbyNeural                  女性    通用                友好、积极
en-GB-RyanNeural                   男性      通用                友好、积极
en-GB-SoniaNeural                  女性    通用                友好、积极
en-GB-ThomasNeural                 男性      通用                友好、积极
en-HK-SamNeural                    男性      通用                友好、积极
en-HK-YanNeural                    女性    通用                友好、积极
en-US-AnaNeural                    女性    动画、对话  可爱
en-US-AndrewMultilingualNeural     男性      对话、Copilot  温暖、自信、真实、诚实
en-US-AndrewNeural                 男性      对话、Copilot  温暖、自信、真实、诚实
en-US-AriaNeural                   女性    新闻、小说            积极、自信
en-US-AvaMultilingualNeural        女性    对话、Copilot  表达力强、关心、愉快、友好
en-US-AvaNeural                    女性    对话、Copilot  表达力强、关心、愉快、友好
en-US-BrianMultilingualNeural      男性      对话、Copilot  亲切、随意、真诚
en-US-BrianNeural                  男性      对话、Copilot  亲切、随意、真诚
en-US-ChristopherNeural            男性    新闻、小说            可靠、权威
en-US-EmmaMultilingualNeural       女性    对话、Copilot  欢快、清晰、对话
en-US-EmmaNeural                   女性    对话、Copilot  欢快、清晰、对话
en-US-EricNeural                   男性    新闻、小说            理性
en-US-GuyNeural                    男性    新闻、小说            热情
en-US-JennyNeural                  女性    通用                友好、体贴、舒适
en-US-MichelleNeural               女性    新闻、小说            友好、愉快
en-US-RogerNeural                  男性    新闻、小说            活泼
en-US-SteffanNeural                男性    新闻、小说            理性
fr-FR-DeniseNeural                 女性    通用                友好、积极
fr-FR-HenriNeural                  男性    通用                友好、积极
zh-CN-XiaoxiaoNeural               女性    新闻、小说            温暖
zh-CN-YunjianNeural                男性      运动、小说         热情
zh-CN-liaoning-XiaobeiNeural       女性    方言                幽默
zh-CN-shaanxi-XiaoniNeural         女性    方言                明亮
zh-HK-HiuGaaiNeural                女性    通用                友好、积极
zh-HK-WanLungNeural                男性    通用                友好、积极
zh-TW-HsiaoChenNeural              女性    通用                友好、积极
zh-TW-YunJheNeural                 男性    通用                友好、积极
```

使用 Shell 命令获取所有可用声音：
```shell
uvx edge-tts --list-voices
```
