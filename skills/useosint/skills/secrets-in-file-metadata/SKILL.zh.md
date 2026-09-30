---
name: secrets-in-file-metadata
description: 使用 exiftool 提取并解析嵌入文件元数据——EXIF GPS 坐标、相机品牌、型号和序列号、DateTimeOriginal 和 CreateDate 时间戳、XMP 和 IPTC 字段，以及 Office 和 PDF 属性（如作者、公司、最后修改者、模板路径和修订次数）。适用于从照片读取 EXIF 信息、确认文档的真正作者、确定文件日期、识别相机或手机型号、或调查 JPEG、HEIC、RAW、MP4、DOCX、XLSX 或 PDF 文件的来源。适用于文档来源纠纷、内部泄露归属、证据处理和出版前脱敏检查。参考 useosint.com/skills/secrets-in-file-metadata。
---

# 文件元数据中的秘密

调查中最快的线索往往已经存在于文件内部：六位小数的GPS坐标、能将四张"无关"照片关联到同一台相机的相机序列号、文档作者确为真实员工、模板路径中包含的公司共享名。

初学者常犯两处错误。元数据缺失并不可疑——这是任何经过社交平台的内容的正常状态。而元数据存在也并非证据：每个标签都是**最后接触该文件的软件所书写的声明**，且所有内容均可通过一条命令进行编辑。

## 根据现有条件，首先查找何处

| 你拥有 | 寻找 | 原因 |
|---|---|---|
| 从社交平台下载的照片 | 不要抱有期待 | 传输管道会重新编码。使用`find-the-original-image`来获取未剥离的上游副本。 |
| 来自论坛、CMS或直接文件链接的照片 | 完整的exiftool转储 | 这些会返回你的字节。GPS在这里比人们预期的存活率更高。 |
| 消息附件 | 完整转储，并注意其发送方式 | 以照片形式发送通常会被重新编码；以文件形式发送通常不会。 |
| 来自一个来源的文件夹 | `exiftool -r -csv`分拣 | 你需要的是异常值，以及跨文件共享的标签。 |
| DOCX/XLSX/PPTX文件 | exiftool，然后解压缩容器 | 跟踪更改、评论作者、修订标识符和带有完整EXIF的嵌入图像不会被exiftool显示。 |
| PDF文件 | exiftool，然后使用结构解析器 | 生产者字符串、增量修订、嵌入文件及其元数据。 |
| 媒体或机构照片 | IPTC和XMP块特定 | 新闻室工作流程在此处写入标题、署名、人物和位置，且当EXIF被删除时通常能存活。 |
| 直接从设备获取的RAW或HEIC文件 | 包含MakerNotes的完整转储 | 最丰富的案例：序列号、快门次数、镜头数据、亚秒级时间。 |
| 视频 | exiftool加上`ffprobe` | 容器创建时间、编码器字符串、每轨道元数据、嵌入的GPS轨迹。 |

## 正确使用exiftool

```bash
exiftool -G1 -a -u -g1 file.jpg        # 所有内容，按部分分组——最佳用于阅读
exiftool -G -a -u -s file.jpg          # 所有内容，每行一个标签，真实标签名
exiftool -time:all -G1 -a -s file.jpg  # 文件中任何位置的每个时间戳
exiftool -gps:all -n file.jpg          # 原始带符号十进制GPS，可直接粘贴到地图中
```

默认设置为何会丢失证据：

- **`-G` / `-G1`** 为每个标签添加其分组前缀（`[EXIF]`、`[XMP]`、`[IPTC]`、
  `[MakerNotes]`、`[File]`、`[Composite]`）。没有它，你无法区分设备写入的标签与exiftool计算的`Composite`值，或EXIF时间戳与文件系统时间戳。`-G1`提供更精细的分组。
- **`-a`** 保留重复标签，而不是只显示最后一个。不一致之处在此处：同一时间戳在两个不同值中存在意味着两个程序存在分歧，这意味着文件被编辑过。
- **`-u`** 显示exiftool没有命名的标签。供应商块通常是关键点。
- **`-n`** 禁用美化打印——带符号十进制度数而不是`52 deg 22' 8.40" N`。
- **`-s`** 打印标签名而不是描述，以便再次查询它们。
- **`-ee`** 提取嵌入数据，包括视频流中的GPS轨迹。

批量分拣，然后查看CSV文件，寻找哪些文件包含GPS、重复的`SerialNumber`、声称时间窗口外的时戳，以及`Software`不同的那个文件：

```bash
exiftool -r -csv -filename -createdate -datetimeoriginal -modifydate \
  -make -model -serialnumber -gpslatitude -gpslongitude -software DIR > triage.csv
exiftool -r -if '$gpslatitude' -p '$directory/$filename  $gpsposition' DIR
```

完整命令模式：[参考/exiftool-cookbook.md](参考/exiftool-cookbook.md)。

## 高价值字段的解读

**GPS。** 位置来自`GPSLatitude`/`GPSLongitude`及其`Ref`标签，高度来自`GPSAltitude`加上`GPSAltitudeRef`。被遗忘的标签更为重要：`GPSImgDirection`是相机指向的**罗盘方位**，这能定位摄影师*和*或定向视角——在匹配街景图像时具有决定性作用。`GPSDestBearing`是到主体的方位。
`GPSHPositioningError`是设备的自身精度估计，以米为单位，是你找到的诚实半径。`GPSDateStamp`/`GPSTimeStamp`为UTC，是文件中唯一可信的时钟。

**设备指纹。** `Make`和`Model`提供设备类型。`SerialNumber`、`BodySerialNumber`、`InternalSerialNumber`或`CameraSerialNumber`识别**一个物理机身**——在链接分析中，这是文件中最有价值的标签，可将跨账户、平台和年份的照片关联到同一台相机。`LensSerialNumber`对镜头也起相同作用，机身/镜头组合更为精确。供应商快门计数和图像编号标签可让你按设备输出排序，并估计两次快门之间拍摄了多少内容。`OwnerName`、`CameraOwnerName`和`Artist`是用户设置的，经常包含真实姓名。

**时间戳。** `DateTimeOriginal`是快门启动时。`CreateDate`是此数字文件创建时——在相机上相同，在扫描、导出或重新编码时不同。`ModifyDate`是最后一次写入时；晚于`DateTimeOriginal`意味着处理过。陷阱：**EXIF时间戳不包含时区。** 除非存在`OffsetTime`、`OffsetTimeOriginal`或`OffsetTimeDigitized`，否则它们是设备本地时间。因此，与UTC `GPSDateTime`进行核对以推算设备的时区——这本身就能告诉你设备是为哪个经度带设置的。永远不要将`FileModifyDate`作为照片证据；它属于你正在查看的文件系统，并且在复制时会改变。

**缩略图与图像。** 马虎的编辑者会更新主图像而保留嵌入预览不变，因此预览可以显示裁剪或修饰前的场景。

```bash
exiftool -b -ThumbnailImage file.jpg > thumb.jpg
exiftool -b -PreviewImage   file.jpg > preview.jpg
exiftool -ee -b -JpgFromRaw file.cr2 > embedded.jpg
```

不同的宽高比证明进行了裁剪。不同的内容是整个案件。

**编辑链。** `Software`、`ProcessingSoftware`、`HostComputer`和XMP的`CreatorTool`命名了接触过文件的内容。XMP媒体管理标签更进一步：`DocumentID`、`OriginalDocumentID`、`InstanceID`和`DerivedFrom`将导出的衍生文件链接回你从未见过的源文件，以及该源文件的兄弟衍生文件。

**新闻照片的IPTC/XMP。** `By-line`、`Credit`、`Source`、`Caption-Abstract`、`Headline`、`DateCreated`、`City`、`Country-PrimaryLocationName`，加上XMP的人物图像和位置创建结构。在新闻照片中，这是对谁、何地、何时——由编辑书写的完整人工回答——当EXIF被删除时，它通常能存活。将其视为有来源的声明，而不是传感器读数。

**文档。** `Author`和`LastModifiedBy`是两个名字。`Company`和`Manager`来自Office安装。`Template`可能包含完整的UNC路径，暴露内部服务器和部门。`RevisionNumber`和`TotalEditTime`显示文档是否被修改或一次性生成以看起来正式。`LastPrinted`证明存在物理副本。然后打开容器，因为exiftool不会显示每位作者的跟踪更改身份：

```bash
unzip -o report.docx -d report_x
# docProps/core.xml, docProps/app.xml  — 属性
# word/document.xml                    — w:ins / w:del携带w:author和w:date
# word/comments.xml                    — 评论作者和首字母缩写
# word/settings.xml                    — 修订标识符，文档谱系指纹
# word/media/                          — 嵌入图像，每个图像都有完整的EXIF
# word/_rels/, xl/externalLinks/       — 链接到内部路径和其他文档
```

嵌入图像在实践中是最被忽视的GPS来源：文档被清理过，粘贴到第四页的照片没有被清理。

**PDF。** `Producer`命名了写入文件的库或驱动程序，是一个强烈的线索——由文字处理器生成的"扫描"文档从未被扫描过。`Creator`命名了作者应用程序。PDF日期与EXIF不同，确实包含时区偏移。PDF支持增量更新，因此内容更早的修订版本可能仍然在文件中，并且它们可以携带保留自身元数据的附件和图像。使用`pdfimages -list`和`pdfdetach -list`进行枚举，并在阅读前使用`qpdf --qdf`扩展结构。

按格式标签目录：[参考/tag-catalogue.md](参考/tag-catalogue.md)。

## 此处可能出错的地方

- **在传入过程中会发生剥离。** 机制：一个*重新编码*以生成交付版本的主机会丢弃EXIF；一个服务你的原始字节的主机会保留它。大型社交平台会重新编码。许多论坛、自托管CMS、对象存储桶、照片社区网站和邮件附件不会。CMS是有趣的中等案例——页面上的缩略图像被剥离，而媒体目录中的原始上传完整无损，因此尝试到达原始路径。
- **缺失证明不了任何事。** 不是文件被清理，不是它是伪造的，不是上传者很小心。写"EXIF不存在"，而不是"EXIF被删除"，除非你能证明一个包含它的副本。
- **存在仅证明有人写了一个值。** 在依赖位置与`geolocate-from-pixels`和太阳位置进行时间核对之前，先进行视觉和时间的佐证。
- **时钟可能错误。** 相机时钟会漂移，在旅行后设置错误的时区，并忽略夏令时。裸EXIF日期时间在锚定`GPSDateTime`或帧中可见的日期事件之前可能偏差±小时。
- **Composite标签是exiftool的算术，不是文件内容。** `GPSPosition`、`ImageSize`和`LensID`是派生的。没有`-G`，你会将计算值当作设备写入的值来引用。
- **截图携带截图设备的元数据**，而不是照片的。在构建理论之前，检查`Model`是否是手机。
- **提取前编辑是不可恢复的。** 旋转、裁剪，甚至在一些编辑器中打开都会重写标签。先哈希并复制。
- **在线元数据查看器意味着将证据上传给陌生人。** 安装exiftool；它是一个Perl发行版，可以离线运行。浏览器本地工具优于服务器端工具，两者在受保护令状、保密协议或活体刑事案件中都不被接受。假设上传的任何内容都会被保留并可能被索引。

## 置信度评级

- **确认**——由非元数据证据佐证的元数据声明：与同一帧的独立视觉地理位置匹配的GPS；在两个不相关的来源中出现的相机序列号；与通过`find-anyone`找到的已知员工匹配的文档作者。
- **可能**——来自可信设备的一致内部元数据，来自不会剥离的文件主机，EXIF、XMP和嵌入缩略图的时戳一致，且没有编辑链。
- **未确认**——只有一个无法核实的标签。你未视觉验证的每个GPS坐标都位于此处。如果标记得当，这很好。
- **矛盾**——不一致的时间戳、显示不同场景的缩略图、视觉证据排除的GPS，或来源否认使用的编辑工具。矛盾本身就是一个发现，通常比原始标签更有价值。

## 实例分析

验证一个随保险索赔附带的PDF"现场检查报告"，声称是在现场声明的日期编写的。

`exiftool -G1 -a -u -g1 report.pdf`：`Producer`是一个文字处理器导出，而不是扫描驱动程序。`CreationDate`和`ModDate`相差11分钟，两者都与现场的时区相差3小时。`Author`是一个首字母和姓氏。

`pdfimages -list`显示四个嵌入照片。提取它们并运行exiftool——什么都没有。它们在插入时被重新编码。死胡同，这也是一个常见情况。

索赔电子邮件还携带了一个DOCX。解压缩它：`docProps/app.xml`显示`TotalEditTime`不到4分钟，且`Template` UNC路径的主机名属于第三方公司，而不是被保险人。`word/document.xml`在另一位作者下有不到一秒的跟踪插入。`word/media/image2.jpeg`仍然有完整的EXIF——`DateTimeOriginal`在声明的检查前两个月，GPS存在，`Model`是手机，`GPSHPositioningError`为9米。

作者姓名**可能**，需通过`x-ray-a-company`与公司进行核实。照片拍摄日期**矛盾**于报告声明的日期。照片位置**未确认**，交由`geolocate-from-pixels`处理，声明半径为9米。

## 关键点

| 你拥有 | 发送给 |
|---|---|
| GPS坐标、相机方位 | `where-was-this-taken`、`geolocate-from-pixels` |
| 作者、所有者、艺术家、评论作者 | `find-anyone` |
| 公司、模板UNC路径、内部共享名 | `x-ray-a-company`、`recon-a-domain-passively` |
| 链接多个文件的相机或镜头序列号 | `graph-the-network` |
| 暗示篡改的软件链 | `is-this-photo-real` |
| 类似于用户名的编辑用户名 | `hunt-a-handle` |
| 需要未剥离的原始文件 | `find-the-original-image`、`read-deleted-pages` |

## 法律注意事项

你合法持有的文件中的元数据属于你。有两个限制。姓名、精确位置和设备标识符在元数据中属于GDPR及类似法规下的个人数据，因此适用最小化、保留和目的限制——收集客观需要的标签，不要因为容易就保留一个完整的目标照片库的转储。并且，关于可识别个人的精确历史位置数据是这项技能中最敏感的材料：在尽职调查、欺诈和授权调查中合法，但却是跟踪的原始材料。如果提取GPS标签的唯一结果是知道一个私人个体的睡眠地点，请停止。参见[../../ETHICS.md](../../ETHICS.md)。
