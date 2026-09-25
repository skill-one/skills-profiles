# 文件元数据中的秘密

调查中最快的线索往往已经存在于文件内部：六位小数的GPS坐标、将四张"无关"照片关联到同一台相机的相机序列号、文档作者是一个真实员工、模板路径中包含公司共享名称。

初学者常犯两个错误。缺失的元数据并不可疑——这是任何经过社交平台的内容的正常状态。而存在的元数据也并非证据：每个标签都是**最后接触该文件的软件所编写的声明**，并且所有这些都可以用一条命令进行编辑。

## 根据你拥有的内容，首先去哪里查找

| 你拥有 | 寻找 | 因为 |
|---|---|---|
| 从社交平台下载的照片 | 不要抱有期望 | 传输管道会重新编码。使用 `find-the-original-image` 来获取未剥离的上游副本。 |
| 来自论坛、CMS或直接文件链接的照片 | 完整的 exiftool 报告 | 这些会返回你的字节。GPS 在这里比人们预期的存活率更高。 |
| 消息附件 | 完整的转储，并注意其发送方式 | 发送为照片通常会被重新编码；发送为文件通常不会被。 |
| 来自一个来源的文件夹 | `exiftool -r -csv` 筛选 | 你想要的是异常值，以及跨文件共享的标签。 |
| DOCX/XLSX/PPTX 文件 | exiftool，然后解压缩容器 | 跟踪更改、评论作者、修订标识符和带有完整 EXIF 的嵌入图像不会被 exiftool 显示。 |
| PDF 文件 | exiftool，然后使用结构解析器 | 生产者字符串、增量修订、嵌入文件和带有其自身元数据的嵌入图像。 |
| 媒体或机构照片 | IPTC 和 XMP 块 | 新闻室工作流程在那里写入标题、署名、人物和位置，并且当 EXIF 被删除时，它通常仍然存在。 |
| 直接从设备获取的 RAW 或 HEIC 文件 | 包含 MakerNotes 的完整转储 | 丰富案例：序列号、快门计数、镜头数据、亚秒级时间。 |
| 视频 | exiftool 加上 `ffprobe` | 容器创建时间、编码器字符串、每轨道元数据、嵌入的 GPS 轨迹。 |

## 正确使用 exiftool

```bash
exiftool -G1 -a -u -g1 file.jpg        # 所有内容，按部分分组——最佳用于阅读
exiftool -G -a -u -s file.jpg          # 所有内容，每行一个标签，真实标签名称
exiftool -time:all -G1 -a -s file.jpg  # 文件中任何地方的每个时间戳
exiftool -gps:all -n file.jpg          # GPS 作为原始带符号十进制数，准备好粘贴到地图中
```

默认设置丢失证据的原因：

- **`-G` / `-G1`** 为每个标签添加其组前缀（`[EXIF]`、`[XMP]`、`[IPTC]`、
  `[MakerNotes]`、`[File]`、`[Composite]`）。没有它，你无法区分设备写入的标签与 exiftool 计算的 `Composite` 值，或 EXIF 时间戳与文件系统时间戳。`-G1` 提供更精细的组。
- **`-a`** 保留重复标签而不是只显示最后一个。不一致之处存在于此处：同一个时间戳在两个不同的值中出现在两个块中意味着两个程序不一致，这意味着文件被编辑了。
- **`-u`** 显示 exiftool 没有名称的标签。供应商块通常是关键。
- **`-n`** 禁用美化打印——带符号十进制度而不是 `52 deg 22' 8.40" N`。
- **`-s`** 打印标签名称而不是描述，以便你可以再次查询它们。
- **`-ee`** 提取嵌入数据，包括视频流中的 GPS 轨迹。

批量筛选，然后查看 CSV，寻找哪些文件包含 GPS、重复的 `SerialNumber`、声称的时间窗口外的时间戳，以及 `Software` 不同的那个文件：

```bash
exiftool -r -csv -filename -createdate -datetimeoriginal -modifydate \
  -make -model -serialnumber -gpslatitude -gpslongitude -software DIR > triage.csv
exiftool -r -if '$gpslatitude' -p '$directory/$filename  $gpsposition' DIR
```

完整命令模式：[reference/exiftool-cookbook.md](reference/exiftool-cookbook.md)。

## 高价值字段的解读

**GPS。** 位置来自 `GPSLatitude`/`GPSLongitude` 及其 `Ref` 标签，高度来自 `GPSAltitude` 加上 `GPSAltitudeRef`。被遗忘的标签更重要：`GPSImgDirection` 是相机指向的**罗盘方位角**，这可以定位摄影师 *和* 或定向视图——在匹配街景图像时决定性。`GPSDestBearing` 是到主体的方位角。
`GPSHPositioningError` 是设备的自身精度估计，以米为单位，是你找到的诚实半径。`GPSDateStamp`/`GPSTimeStamp` 是 UTC，使它们成为文件中唯一可信的时钟。

**设备指纹。** `Make` 和 `Model` 提供设备类型。`SerialNumber`、`BodySerialNumber`、`InternalSerialNumber` 或 `CameraSerialNumber` 识别**一个物理主体**——文件中用于链接分析的最重要的标签，将跨账户、平台和年份的图像关联到单个相机。`LensSerialNumber` 对玻璃也起相同作用，而主体/镜头对更紧密。供应商快门计数和图像编号标签允许你按顺序排列设备的输出，并估计两次帧之间发生了多少拍摄。`OwnerName`、`CameraOwnerName` 和 `Artist` 是用户设置的，并且经常包含真实姓名。

**时间戳。** `DateTimeOriginal` 是快门释放的时间。`CreateDate` 是此数字文件创建的时间——在相机上相同，在扫描、导出或重新编码时不同。`ModifyDate` 是最后一次写入的时间；晚于 `DateTimeOriginal` 意味着处理。陷阱：**EXIF 时间戳不包含时区。** 除非 `OffsetTime`、`OffsetTimeOriginal` 或 `OffsetTimeDigitized` 存在，否则它们是设备本地时间。因此，与 UTC `GPSDateTime` 协调以推导出设备的偏移量——这本身告诉你设备是为哪个经度带设置的。永远不要引用 `FileModifyDate` 作为关于照片的证据；它属于你正在查看的文件系统，并且在复制时更改。

**缩略图与图像。** 马虎的编辑者会更新主图像而保留嵌入的预览不变，因此预览可以显示裁剪或修饰前的场景。

```bash
exiftool -b -ThumbnailImage file.jpg > thumb.jpg
exiftool -b -PreviewImage   file.jpg > preview.jpg
exiftool -ee -b -JpgFromRaw file.cr2 > embedded.jpg
```

不同的宽高比证明了裁剪。不同的内容是整个案件。

**编辑链。** `Software`、`ProcessingSoftware`、`HostComputer` 和 XMP 的 `CreatorTool` 名称接触过文件的内容。XMP 媒体管理标签更进一步：`DocumentID`、`OriginalDocumentID`、`InstanceID` 和 `DerivedFrom` 将导出的衍生文件链接回你从未见过的源文件，以及该源文件的其他兄弟衍生文件。

**新闻照片的 IPTC/XMP。** `By-line`、`Credit`、`Source`、`Caption-Abstract`、`Headline`、`DateCreated`、`City`、`Country-PrimaryLocationName`，加上 XMP 的人物图像和位置创建结构。在新闻照片中，这是一个关于谁、在哪里、何时的人为编写的完整答案——由编辑编写，因此将其视为有来源的声明，而不是传感器读取。

**文档。** `Author` 和 `LastModifiedBy` 是两个名称。`Company` 和 `Manager` 来自 Office 安装。`Template` 可以包含完整的 UNC 路径，暴露内部服务器和部门。`RevisionNumber` 和 `TotalEditTime` 显示文档是否被修改或一次性生成以看起来正式。`LastPrinted` 证明存在物理副本。然后打开容器，因为 exiftool 不会显示每位作者的跟踪更改身份：

```bash
unzip -o report.docx -d report_x
# docProps/core.xml, docProps/app.xml  — 属性
# word/document.xml                    — w:ins / w:del 携带 w:author 和 w:date
# word/comments.xml                    — 评论作者和首字母缩写
# word/settings.xml                    — 修订标识符，文档谱系指纹
# word/media/                          — 嵌入图像，每个图像都有完整的 EXIF
# word/_rels/, xl/externalLinks/       — 链接到内部路径和其他文档
```

嵌入图像在实践中是最被忽视的 GPS 来源：文档被清理了，粘贴到第 四页的照片没有被清理。

**PDF。** `Producer` 名称编写文件库或驱动程序，是一个强烈的线索——由文字处理器生成的“扫描”文档从未被扫描过。`Creator` 名称是作者应用程序。PDF 日期与 EXIF 不同，确实包含时区偏移量。PDF 支持增量更新，因此内容更早的修订版本仍然存在于文件中，并且它们可以携带附件和保留其自身元数据的图像。使用 `pdfimages -list` 和 `pdfdetach -list` 进行枚举，并在阅读之前使用 `qpdf --qdf` 扩展结构。

按格式标签目录：[reference/tag-catalogue.md](reference/tag-catalogue.md)。

## 哪里会出错

- **在进入时会发生剥离。** 机制：一个*重新编码*以生成交付版本的主机会丢弃 EXIF；一个服务你的原始字节的主机会保留它。大型社交平台会重新编码。许多论坛、自托管 CMS、对象存储桶、照片社区网站和邮件附件不会。CMS 是有趣的中等案例——页面上的缩放图像被剥离，而媒体目录中的原始上传是完整的，因此尝试到达原始路径。
- **缺失证明不了什么。** 不是文件被清理了，不是它是假的，不是上传者很小心。写“没有 EXIF 存在”，永远不要写“EXIF 被删除”，除非你能显示一个包含它的副本。
- **存在只能证明有人写了一个值。** 在依赖之前，使用 `geolocate-from-pixels` 可视化地确认位置，并使用太阳位置确认时间。
- **时钟可能不正确。** 相机时钟会漂移，在旅行后保持错误的时区，并忽略夏令时。一个裸的 EXIF 日期时间在锚定到 `GPSDateTime` 或帧中可见的日期事件之前可能偏差 ±小时。
- **Composite 标签是 exiftool 的算术，而不是文件的内容。** `GPSPosition`、`ImageSize` 和 `LensID` 是派生的。没有 `-G`，你会引用一个计算值，好像设备写了它。
- **屏幕截图携带截图设备的元数据**，而不是照片的。在构建理论之前检查 `Model` 是否是手机。
- **提取之前编辑是不可恢复的。** 旋转、裁剪，甚至在一些编辑器中打开都会重写标签。首先哈希并复制。
- **在线元数据查看器意味着将你的证据上传给陌生人。** 安装 exiftool；它是一个 Perl 发行版，可以离线运行。本地浏览器工具比服务器端工具更好，两者都不适用于受保护令、保密协议或活体刑事案件下的材料。假设上传的任何内容都会被保留并可能被索引。

## 置信度评级

- **已确认**——由非元数据证据 corroborated 的元数据声明：与同一帧的独立视觉地理位置匹配的 GPS；在两个未连接的来源中出现的相机序列号；文档作者与通过 `find-anyone` 找到的已知员工匹配。
- **可能**——来自一个合理设备的一致元数据，来自一个不会剥离的宿主，EXIF、XMP 和嵌入缩略图的时戳一致，并且没有编辑器在链中。
- **未确认**——一个没有可以检查的标签。你未通过视觉验证的每个 GPS 坐标都位于此处。如果标记了，那就没事。
- **矛盾**——不一致的时间戳、显示不同场景的缩略图、视觉证据排除的 GPS，或源否认使用的编辑工具。矛盾本身是一个发现，通常比原始标签更好。

## 实例分析

验证一个附加到保险索赔的 PDF“现场检查报告”，据称是在现场声明的日期编写的。

`exiftool -G1 -a -u -g1 report.pdf`：`Producer` 是文字处理器导出，而不是扫描器驱动程序。`CreationDate` 和 `ModDate` 相差十一分钟，两者都与现场的时区偏移三小时。`Author` 是首字母和姓氏。

`pdfimages -list` 显示四个嵌入的图像。提取它们并运行 exiftool——什么都没有。它们在插入时被重新编码。死胡同，这是一个常见的情况。

索赔电子邮件还携带了一个 DOCX。解压缩它：`docProps/app.xml` 给出 `TotalEditTime` 少于四分钟和一个 `Template` UNC 路径，其主机名属于第三方公司，而不是被保险人。`word/document.xml` 有一个第二作者的跟踪插入。`word/media/image2.jpeg` 仍然有完整的 EXIF——`DateTimeOriginal` 在声明的检查两个月前，GPS 存在，`Model` 是手机，`GPSHPositioningError` 九米。

作者姓名**可能**，要通过 `x-ray-a-company` 与公司核实。照片拍摄日期**矛盾**与报告声明的日期。照片位置**未确认**，交由 `geolocate-from-pixels` 使用九米声明的半径。

## 转折点

| 你拥有 | 发送到 |
|---|---|
| GPS 坐标，相机方位角 | `where-was-this-taken`，`geolocate-from-pixels` |
| 作者，所有者，艺术家，评论作者 | `find-anyone` |
| 公司，模板 UNC 路径，内部共享名称 | `x-ray-a-company`，`recon-a-domain-passively` |
| 连接多个文件的相机或镜头序列号 | `graph-the-network` |
| 暗示操作的软件链 | `is-this-photo-real` |
| 类似于用户名的编辑用户名 | `hunt-a-handle` |
| 需要一个未剥离的原始文件 | `find-the-original-image`，`read-deleted-pages` |

## 法律说明

你合法持有的文件中的元数据属于你，可以阅读。有两个约束条件。名称、精确位置和设备标识符在元数据中属于 GDPR 和类似法规下的个人数据，因此适用最小化、保留和目的限制——收集客观需要的标签，并且不要因为容易就保留一个完整的目标照片库的转储。并且，关于可识别个人的精确历史位置数据是这个技能中最敏感的材料：在尽职调查、欺诈和授权调查中合法，并且是跟踪的原始材料。如果提取 GPS 标签的唯一结果是知道一个私人个人的睡眠地点，请停止。参见 [../../ETHICS.md](../../ETHICS.md)。
