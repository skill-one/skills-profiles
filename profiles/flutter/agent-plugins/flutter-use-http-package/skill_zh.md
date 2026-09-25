# 实现Flutter网络功能

## 目录
- [配置与权限](#配置与权限)
- [请求执行与响应处理](#请求执行与响应处理)
- [后台解析](#后台解析)
- [工作流：执行网络操作](#工作流执行网络操作)
- [示例](#示例)

## 配置与权限

配置网络访问所需的运行环境和平台特定权限。

1. 通过终端添加`http`包依赖：
   ```bash
   flutter pub add http
   ```
2. 在Dart文件中导入包：
   ```dart
   import 'package:http/http.dart' as http;
   ```
3. 通过在`android/app/src/main/AndroidManifest.xml`中添加Internet权限来配置Android权限：
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```
4. 通过在`macos/Runner/DebugProfile.entitlements`和`macos/Runner/Release.entitlements`中添加网络客户端键来配置macOS权限：
   ```xml
   <key>com.apple.security.network.client</key>
   <true/>
   ```

## 请求执行与响应处理

执行HTTP操作并将响应映射到强类型的Dart对象。

*   **URI：** 始终使用`Uri.parse('your_url')`解析URL字符串。
*   **请求头：** 通过`headers`参数映射注入授权和内容类型头。使用`HttpHeaders.authorizationHeader`处理认证令牌。
*   **有效载荷：** 对于POST和PUT请求，使用`dart:convert`中的`jsonEncode()`编码请求体。
*   **状态验证：** 评估`response.statusCode`。将`200 OK`（GET/PUT/DELETE）和`201 CREATED`（POST）视为成功。
*   **错误处理：** 对于非成功状态码，抛出显式异常。失败时切勿返回`null`，因为这会阻止`FutureBuilder`触发其错误状态并导致无限加载指示器。
*   **反序列化：** 使用`jsonDecode(response.body)`解析原始字符串，并使用工厂构造函数（例如`fromJson`）将其映射到自定义Dart对象。

## 后台解析

将昂贵的JSON解析卸载到单独的Isolate中，以防止UI卡顿（帧丢失）。

*   导入`package:flutter/foundation.dart`。
*   使用`compute()`函数在后台Isolate中运行解析逻辑。
*   确保传递给`compute()`的解析函数是顶级函数或静态方法，因为闭包或实例方法不能跨Isolate传递。

## 工作流：执行网络操作

使用以下检查清单来实施和验证网络操作。

**任务进度：**
- [ ] 1. 定义具有`fromJson`工厂构造函数的强类型Dart模型。
- [ ] 2. 实现返回`Future<Model>`的网络请求方法。
- [ ] 3. 根据操作类型应用条件逻辑：
  - **如果获取数据（GET）：** 将查询参数附加到URI。
  - **如果修改数据（POST/PUT）：** 设置`'Content-Type': 'application/json; charset=UTF-8'`并附加`jsonEncode`的请求体。
  - **如果删除数据（DELETE）：** 成功时（`200 OK`）返回空模型实例。
- [ ] 4. 验证`statusCode`并在失败时抛出`Exception`。
- [ ] 5. 使用`FutureBuilder`将`Future`集成到UI中。
- [ ] 6. 处理`snapshot.hasData`、`snapshot.hasError`，并默认显示`CircularProgressIndicator`。
- [ ] 7. **反馈循环：** 运行应用 -> 触发网络请求 -> 查看控制台中的未处理异常 -> 修复解析或权限错误。

## 示例

### 高保真实现：后台获取与解析

```dart
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// 1. 用于Isolate的顶级解析函数
List<Photo> parsePhotos(String responseBody) {
  final parsed = (jsonDecode(responseBody) as List<Object?>)
      .cast<Map<String, Object?>>();
  return parsed.map<Photo>(Photo.fromJson).toList();
}

// 2. 带有后台解析的网络执行
Future<List<Photo>> fetchPhotos() async {
  final response = await http.get(
    Uri.parse('https://jsonplaceholder.typicode.com/photos'),
    headers: {
      HttpHeaders.authorizationHeader: 'Bearer your_token_here',
      HttpHeaders.acceptHeader: 'application/json',
    },
  );

  if (response.statusCode == 200) {
    // 将繁重的解析卸载到后台Isolate
    return compute(parsePhotos, response.body);
  } else {
    throw Exception('Failed to load photos. Status: ${response.statusCode}');
  }
}

// 3. 强类型模型
class Photo {
  final int id;
  final String title;
  final String thumbnailUrl;

  const Photo({
    required this.id,
    required this.title,
    required this.thumbnailUrl,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    return Photo(
      id: json['id'] as int,
      title: json['title'] as String,
      thumbnailUrl: json['thumbnailUrl'] as String,
    );
  }
}

// 4. UI集成
class PhotoGallery extends StatefulWidget {
  const PhotoGallery({super.key});

  @override
  State<PhotoGallery> createState() => _PhotoGalleryState();
}

class _PhotoGalleryState extends State<PhotoGallery> {
  late Future<List<Photo>> _futurePhotos;

  @override
  void initState() {
    super.initState();
    // 初始化Future以防止重建时重新获取
    _futurePhotos = fetchPhotos();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Photo>>(
      future: _futurePhotos,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final photos = snapshot.data!;
          return ListView.builder(
            itemCount: photos.length,
            itemBuilder: (context, index) => ListTile(
              leading: Image.network(photos[index].thumbnailUrl),
              title: Text(photos[index].title),
            ),
          );
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }
        
        // 默认加载状态
        return const Center(child: CircularProgressIndicator());
      },
    );
  }
}
```
