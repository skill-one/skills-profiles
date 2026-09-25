## 一般渲染策略

使用以下命令渲染视频：

```
npx remotion render
```

完整选项列表：https://www.remotion.dev/docs/cli/render.md

使用以下命令渲染静态图像：

```
npx remotion still
```

完整选项列表：https://www.remotion.dev/docs/cli/still.md

要一次性渲染多个帧为图像，使用 `render --frames`：

```
npx remotion render [composition-id] out/frames --frames=0,30,90 --image-format=png
```

更多选项请参考 https://www.remotion.dev/docs/cli/render.md#--frames。

## 透明视频

请参阅 [透明视频](./transparent-videos.md) 以渲染具有透明度的视频。
