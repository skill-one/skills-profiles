# 架构化 Flutter 应用

## 目录
- [架构层](#架构层)
- [项目结构](#项目结构)
- [工作流：实现新功能](#工作流实现新功能)
- [示例](#示例)

## 架构层

通过将应用划分为不同的层来强制执行严格的关注点分离。永远不要将 UI 渲染与业务逻辑或数据获取混合。

### UI 层（表现层）
使用 MVVM（模型-视图-视图模型）模式来管理 UI 状态和逻辑。
*   **视图：** 编写可重用、精简的组件。将视图中的逻辑限制为与 UI 相关的操作（例如，动画、布局约束、简单路由）。从视图模型传递所有所需的数据。
*   **视图模型：** 管理视图状态并处理用户交互。扩展 `ChangeNotifier`（或使用 `Listenable`）以公开状态。向视图公开不可变状态快照。通过构造函数将仓库注入视图模型。

### 数据层
使用仓库模式来隔离数据访问逻辑并创建单一事实来源。
*   **服务：** 创建无状态类来包装外部 API（HTTP 客户端、本地数据库、平台插件）。返回原始 API 模型或 `Result` 包装器。
*   **仓库：** 消费一个或多个服务。将原始 API 模型转换为干净的领域模型。处理缓存、离线同步和重试逻辑。向视图模型公开领域模型。

### 逻辑层（领域 - 可选）
*   **用例：** 只有当应用程序包含复杂的业务逻辑，导致视图模型混乱，或者逻辑必须在多个视图模型之间重用时，才实现此层。将此逻辑提取到视图模型和仓库之间的专用用例（交互器）类中。

## 项目结构

使用混合方法组织代码库：按功能分组 UI 组件，按类型分组数据/领域组件。

```text
lib/
├── data/
│   ├── models/         # API 模型
│   ├── repositories/   # 仓库实现
│   └── services/       # API 客户端、本地存储包装器
├── domain/
│   ├── models/         # 干净的领域模型
│   └── use_cases/      # 可选的业务逻辑类
└── ui/
    ├── core/           # 共享组件、主题、排版
    └── features/
        └── [feature_name]/
            ├── view_models/
            └── views/
```

## 工作流：实现新功能

在向应用程序添加新功能时，请遵循此顺序工作流。将检查清单复制到跟踪进度。

### 任务进度
- [ ] **步骤 1：定义领域模型。** 使用 `freezed` 或 `built_value` 创建不可变数据类。
- [ ] **步骤 2：实现服务。** 创建或更新服务类以处理外部 API 通信。
- [ ] **步骤 3：实现仓库。** 创建仓库以消费服务并返回领域模型。
- [ ] **步骤 4：应用条件逻辑（领域层）。**
  - *如果功能需要复杂的数据转换或跨仓库逻辑：* 创建用例类。
  - *如果功能是简单的 CRUD 操作：* 跳到步骤 5。
- [ ] **步骤 5：实现视图模型。** 创建扩展 `ChangeNotifier` 的视图模型。注入所需的仓库/用例。公开不可变状态和命令方法。
- [ ] **步骤 6：实现视图。** 创建 UI 组件。使用 `ListenableBuilder` 或 `AnimatedBuilder` 来监听视图模型的变化。
- [ ] **步骤 7：注入依赖项。** 在依赖注入容器（例如，`provider` 或 `get_it`）中注册新的服务、仓库和视图模型。
- [ ] **步骤 8：运行验证器。** 执行视图模型和仓库的单元测试。
  - *反馈循环：* 运行测试 -> 审查失败 -> 修复逻辑 -> 重新运行，直到通过。

## 示例

### 数据层：服务和仓库

```dart
// 1. 服务（原始 API 交互）
class ApiClient {
  Future<UserApiModel> fetchUser(String id) async {
    // HTTP GET 实现...
  }
}

// 2. 仓库（单一事实来源，返回领域模型）
class UserRepository {
  UserRepository({required ApiClient apiClient}) : _apiClient = apiClient;
  
  final ApiClient _apiClient;
  User? _cachedUser;

  Future<User> getUser(String id) async {
    if (_cachedUser != null) return _cachedUser!;
    
    final apiModel = await _apiClient.fetchUser(id);
    _cachedUser = User(id: apiModel.id, name: apiModel.fullName); // 转换为领域模型
    return _cachedUser!;
  }
}
```

### UI 层：视图模型和视图

```dart
// 3. 视图模型（状态管理和表现逻辑）
class ProfileViewModel extends ChangeNotifier {
  ProfileViewModel({required UserRepository userRepository}) 
      : _userRepository = userRepository;

  final UserRepository _userRepository;

  User? _user;
  User? get user => _user;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  Future<void> loadProfile(String id) async {
    _isLoading = true;
    notifyListeners();

    try {
      _user = await _userRepository.getUser(id);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}

// 4. 视图（无状态 UI 组件）
class ProfileView extends StatelessWidget {
  const ProfileView({super.key, required this.viewModel});

  final ProfileViewModel viewModel;

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: viewModel,
      builder: (context, _) {
        if (viewModel.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        
        final user = viewModel.user;
        if (user == null) {
          return const Center(child: Text('User not found'));
        }

        return Column(
          children: [
            Text(user.name),
            ElevatedButton(
              onPressed: () => viewModel.loadProfile(user.id),
              child: const Text('刷新'),
            ),
          ],
        );
      },
    );
  }
}
```
