# 手动在 Flutter 中序列化 JSON

## 目录
- [核心指南](#核心指南)
- [工作流：实现可序列化模型](#工作流实现可序列化模型)
- [工作流：获取和解析 JSON](#工作流获取和解析json)
- [示例](#示例)

## 核心指南

- **导入 `dart:convert`**：使用 Flutter 的内置 `dart:convert` 库进行手动 JSON 编码（`jsonEncode`）和解码（`jsonDecode`）。
- **强制类型安全**：始终将 `jsonDecode()` 的 `dynamic` 结果转换为预期类型，通常为对象时为 `Map<String, dynamic>`，数组时为 `List<dynamic>`。
- **封装序列化逻辑**：定义包含与 JSON 结构对应的属性的普通模型类。在模型中实现 `fromJson` 工厂构造函数和 `toJson` 方法。
- **处理后台解析**：如果解析大型 JSON 文档（执行时间 > 16ms），使用 Flutter 的 `compute()` 函数将解析逻辑卸载到单独的 isolate 中，以防止 UI 卡顿。
- **失败时抛出异常**：在处理 HTTP 响应时，如果状态码不是成功状态（例如，不是 200 OK 或 201 Created），则抛出异常。不要返回 `null`。

## 工作流：实现可序列化模型

使用此清单来为数据模型实现手动 JSON 序列化。

**任务进度：**
- [ ] 定义带有 `final` 属性的普通模型类。
- [ ] 实现 `factory Model.fromJson(Map<String, dynamic> json)` 构造函数。
- [ ] 实现 `Map<String, dynamic> toJson()` 方法。
- [ ] 为两种序列化方法编写单元测试。
- [ ] 运行验证器 -> 审查类型不匹配错误 -> 修复类型转换逻辑。

1. **定义模型**：创建一个具有与 JSON 键匹配的属性的类。
2. **实现 `fromJson`**：从 `Map` 中提取值并将其转换为适当的 Dart 类型。使用模式匹配或显式转换。
3. **实现 `toJson`**：返回一个 `Map<String, dynamic>`，将类属性映射回它们的 JSON 字符串键。
4. **验证**：执行单元测试以确保类型安全、自动完成和编译时异常处理功能正常。

## 工作流：获取和解析 JSON

在从网络请求中检索和解析 JSON 时使用此条件工作流。

**任务进度：**
- [ ] 执行 HTTP 请求。
- [ ] 验证响应状态码。
- [ ] 确定解析策略（同步 vs. isolate）。
- [ ] 解码并将 JSON 映射到模型。

1. **执行请求**：使用 `http` 包执行网络调用。
2. **验证响应**：
   - 如果 `response.statusCode == 200`（或 201 for POST），则继续解析。
   - 如果状态码指示失败，则抛出 `Exception`。
3. **确定解析策略**：
   - 如果解析**小负载**（例如，单个对象），则在主线程上同步解析。
   - 如果解析**大负载**（例如，数千个对象组成的数组），则使用 `compute(parseFunction, response.body)` 在后台 isolate 中解析。
4. **解码和映射**：将解码后的 JSON 传递到模型的 `fromJson` 构造函数。

## 示例

### 高保真模型实现

```dart
import 'dart:convert';

class User {
  final int id;
  final String name;
  final String email;

  const User({
    required this.id,
    required this.name,
    required this.email,
  });

  // 用于反序列化的工厂构造函数
  factory User.fromJson(Map<String, dynamic> json) {
    return switch (json) {
      {
        'id': int id,
        'name': String name,
        'email': String email,
      } => 
        User(
          id: id,
          name: name,
          email: email,
        ),
      _ => throw const FormatException('Failed to load User.'),
    };
  }

  // 用于序列化的方法
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
    };
  }
}
```

### 同步解析（小负载）

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<User> fetchUser(http.Client client, int userId) async {
  final response = await client.get(
    Uri.parse('https://api.example.com/users/$userId'),
    headers: {'Accept': 'application/json'},
  );

  if (response.statusCode == 200) {
    // decode 返回 dynamic，转换为 Map<String, dynamic>
    final Map<String, dynamic> jsonMap = jsonDecode(response.body) as Map<String, dynamic>;
    return User.fromJson(jsonMap);
  } else {
    throw Exception('Failed to load user');
  }
}
```

### 后台解析（大负载）

```dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

// 顶层函数，compute() 所需
List<User> parseUsers(String responseBody) {
  final parsed = (jsonDecode(responseBody) as List<dynamic>).cast<Map<String, dynamic>>();
  return parsed.map<User>((json) => User.fromJson(json)).toList();
}

Future<List<User>> fetchUsers(http.Client client) async {
  final response = await client.get(
    Uri.parse('https://api.example.com/users'),
    headers: {'Accept': 'application/json'},
  );

  if (response.statusCode == 200) {
    // 将昂贵的解析卸载到后台 isolate
    return compute(parseUsers, response.body);
  } else {
    throw Exception('Failed to load users');
  }
}
```
