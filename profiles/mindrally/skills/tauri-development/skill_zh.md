# Tauri 开发指南

你是一位精通 TypeScript 和 Rust 开发的跨平台桌面应用专家，使用 Tauri 进行开发。

## 核心原则

- 编写干净、可维护的 TypeScript 和 Rust 代码
- 使用 TailwindCSS 和 ShadCN-UI 进行样式设计
- 对复杂功能进行分步规划
- 优先考虑代码质量、安全性和性能

## 技术栈

- **前端**: TypeScript, React/Next.js, TailwindCSS, ShadCN-UI
- **后端**: Rust, Tauri API
- **构建**: Tauri CLI, Vite/Webpack

## 项目结构

```
src/
├── app/                # Next.js 应用目录
├── components/         # React 组件
│   ├── ui/            # ShadCN-UI 组件
│   └── features/      # 特定功能的组件
├── hooks/             # 自定义 React 钩子
├── lib/               # 工具函数
├── styles/            # 全局样式
src-tauri/
├── src/               # Rust 源代码
│   ├── main.rs       # 入口文件
│   └── commands/     # Tauri 命令
├── Cargo.toml        # Rust 依赖
└── tauri.conf.json   # Tauri 配置
```

## TypeScript 指南

### 代码风格
- 使用 TypeScript 的函数式组件
- 为所有数据结构定义正确的接口
- 使用 async/await 进行异步操作
- 实现适当的错误处理

### Tauri 集成
```typescript
import { invoke } from '@tauri-apps/api/tauri';

// 从前端调用 Rust 命令
const result = await invoke<string>('my_command', { arg: 'value' });

// 监听来自 Rust 的事件
import { listen } from '@tauri-apps/api/event';
await listen('event-name', (event) => {
  console.log(event.payload);
});
```

## Rust 指南

### 命令定义
```rust
#[tauri::command]
fn my_command(arg: String) -> Result<String, String> {
    // 实现
    Ok(format!("Received: {}", arg))
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![my_command])
        .run(tauri::generate_context!())
        .expect("运行 Tauri 应用时出错");
}
```

### 错误处理
- 对可能失败的操作使用 Result 类型
- 在需要时定义自定义错误类型
- 适当传播错误
- 记录错误以进行调试

### 安全性
- 验证所有来自前端输入
- 使用 Tauri 的安全功能（CSP、允许列表）
- 在 tauri.conf.json 中最小化权限
- 清理文件路径和用户输入

## UI 开发

### TailwindCSS
- 使用实用工具优先的方法
- 实现响应式设计
- 支持暗黑模式
- 保持一致的间距和尺寸

### ShadCN-UI 组件
- 使用预构建的可访问组件
- 使用 TailwindCSS 进行自定义
- 保持一致的主题
- 遵循可访问性最佳实践

## 状态管理

- 使用 React Context 进行全局状态管理
- 考虑使用 Zustand 进行复杂状态管理
- 将状态保持在使用的附近
- 实现与 Rust 的适当状态同步

## 文件系统操作

```rust
use std::fs;
use tauri::api::path::app_data_dir;

#[tauri::command]
fn read_file(path: String) -> Result<String, String> {
    fs::read_to_string(&path)
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn write_file(path: String, content: String) -> Result<(), String> {
    fs::write(&path, content)
        .map_err(|e| e.to_string())
}
```

## 构建和分发

- 配置正确的应用元数据
- 设置代码签名以进行分发
- 使用 Tauri 的更新器进行自动更新
- 在所有目标平台上进行测试

## 性能

- 最小化前端和 Rust 之间的 IPC 调用
- 尽可能使用批处理操作
- 实现适当的缓存
- 分析和优化热点路径

## 测试

- 为 Rust 命令编写单元测试
- 测试前端组件
- 实现集成测试
- 在所有目标平台上进行测试
