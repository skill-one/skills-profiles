# 夜莺卡拉OK技能

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集。

夜莺是一款自包含的、基于机器学习的卡拉OK应用程序，使用Rust（Bevy引擎）编写。它会扫描本地音乐文件夹，使用UVR卡拉OK模型或Demucs分离人声和伴奏，使用WhisperX进行歌词转录并附带单词级别的时间戳，并同步播放高亮歌词、实时音调评分、玩家资料和GPU着色器/视频背景。所有内容——ffmpeg、Python、PyTorch、机器学习模型——在首次启动时自动引导。

---

## 安装

### 预构建二进制文件（推荐）

从[发布页面](https://github.com/rzru/nightingale/releases)下载适用于您平台的最新版本并运行它。

**macOS独有** — 解压后移除隔离：
```bash
xattr -cr Nightingale.app
```

### 从源代码构建

**先决条件：**
- Rust 1.85+（2024年版本）
- Linux还需要：`libasound2-dev libudev-dev libwayland-dev libxkbcommon-dev`

```bash
git clone https://github.com/rzru/nightingale
cd nightingale

# 开发构建
cargo build --release

# 直接运行
./target/release/nightingale
```

### 发布包制作

```bash
# Linux / macOS
scripts/make-release.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts/make-release.ps1
```

输出一个`.tar.gz`（Linux/macOS）或`.zip`（Windows）的版本，准备好分发。

---

## 首次启动 / 引导

首次运行时，夜莺会下载并配置：
- `ffmpeg`二进制文件
- `uv`（Python包管理器）
- 通过uv安装Python 3.10
- 在虚拟环境中安装PyTorch + WhisperX + audio-separator
- UVR卡拉OK ONNX模型和WhisperX `large-v3`模型

这需要**2-10分钟**，具体取决于网络速度。应用程序中会显示进度界面。

要强制重新引导，请：
```bash
./nightingale --setup
```

引导完成时，标记为`~/.nightingale/vendor/.ready`。

---

## 命令行标志

| 标志 | 描述 |
|---|---|
| `--setup` | 强制重新运行首次启动引导（重新下载供应商依赖） |

---

## 键盘与游戏手柄控制

### 导航

| 操作 | 键盘 | 游戏手柄 |
|---|---|---|
| 移动 | 箭头键 | D-pad / 左摇杆 |
| 确认 | Enter | A（南） |
| 返回 | Escape | B（东） / Start |
| 切换面板 | Tab | — |
| 搜索 | 输入以过滤 | — |

### 播放

| 操作 | 键盘 | 游戏手柄 |
|---|---|---|
| 暂停/继续 | Space | Start |
| 返回菜单 | Escape | B（东） |
| 切换引导人声 | G | — |
| 引导音量增减 | + / - | — |
| 循环背景 | T | — |
| 循环视频风格 | F | — |
| 切换麦克风 | M | — |
| 切换到下一个麦克风 | N | — |
| 切换全屏 | F11 | — |

---

## 配置

### 主配置

位于`~/.nightingale/config.json`。可以直接编辑或通过应用程序设置编辑。

```json
{
  "music_folder": "/home/user/Music",
  "separator": "uvr",
  "guide_vocal_volume": 0.3,
  "background_theme": "plasma",
  "video_flavor": "nature",
  "default_profile": "Alice"
}
```

**`separator`选项：** `"uvr"`（默认，保留伴唱） | `"demucs"`

**`background_theme`选项：** `"plasma"`, `"aurora"`, `"waves"`, `"nebula"`, `"starfield"`, `"video"`, `"source_video"`

**`video_flavor`选项：** `"nature"`, `"underwater"`, `"space"`, `"city"`, `"countryside"`

### 资料夹

位于`~/.nightingale/profiles.json`：

```json
{
  "profiles": [
    {
      "name": "Alice",
      "scores": {
        "blake3_hash_of_song": {
          "stars": 4,
          "score": 87250,
          "played_at": "2026-03-18T21:00:00Z"
        }
      }
    }
  ]
}
```

### Pixabay视频背景（开发）

API密钥嵌入在发布构建中。本地开发时，在项目根目录创建`.env`：

```bash
# .env
PIXABAY_API_KEY=$PIXABAY_API_KEY
```

发布脚本(`make-release.sh`)会自动引用`.env`。

---

## 数据存储布局

```
~/.nightingale/
├── cache/              # 每首歌曲的 stems、transcripts、歌词（按blake3哈希键值对）
├── config.json         # 应用设置
├── profiles.json       # 玩家资料和每首歌曲的评分
├── videos/             # 预下载的Pixabay视频背景
├── sounds/             # 音效
├── vendor/
│   ├── ffmpeg          # ffmpeg二进制文件
│   ├── uv              # uv二进制文件
│   ├── python/         # Python 3.10
│   ├── venv/           # 机器学习虚拟环境（WhisperX、Demucs、audio-separator）
│   ├── analyzer/       # Python分析脚本
│   └── .ready          # 引导完成标记
└── models/
    ├── torch/          # Demucs模型权重
    ├── huggingface/    # WhisperX large-v3权重
    └── audio_separator/ # UVR卡拉OK ONNX模型
```

缓存键是**源文件的blake3哈希**——只有文件更改或手动失效时才会触发重新分析。

---

## 支持的文件格式

**音频：** `.mp3`, `.flac`, `.ogg`, `.wav`, `.m4a`, `.aac`, `.wma`

**视频：** `.mp4`, `.mkv`, `.avi`, `.webm`, `.mov`, `.m4v`

视频文件：提取音频轨道、分离人声、自动播放原始视频作为背景。

---

## 硬件加速

PyTorch后端自动检测：

| 后端 | 设备 | 备注 |
|---|---|---|
| CUDA | NVIDIA GPU | 最快；~2-5分钟/首歌曲 |
| MPS | Apple Silicon | macOS；WhisperX对齐回退到CPU |
| CPU | 任何 | 总是可用；~10-20分钟/首歌曲 |

UVR卡拉OK模型自动使用ONNX Runtime与CUDA（NVIDIA）或CoreML（Apple Silicon）。

---

## 处理流程

```
音频/视频文件
       │
       ▼
 UVR卡拉OK (ONNX) 或 Demucs (PyTorch)
       │  vocals.ogg + instrumental.ogg
       ▼
 LRCLIB API  ──▶  同步歌词获取（如果可用）
       │
       ▼
 WhisperX large-v3  ──▶  转录 + 单词级别时间戳
       │
       ▼
 Bevy App (Rust)
   - 播放伴奏音频
   - 同步单词高亮
   - 实时音调检测与评分
   - GPU着色器/视频背景
   - 每个资料的计分板
```

---

## 代码模式

### 添加新背景主题（Bevy系统）

```rust
// 在您的Bevy插件中，注册一个新的背景变体
use bevy::prelude::*;

#[derive(Component)]
pub struct MyCustomBackground;

pub fn spawn_custom_background(mut commands: Commands) {
    commands.spawn((
        MyCustomBackground,
        // ... 您的背景组件
    ));
}

pub struct CustomBackgroundPlugin;

impl Plugin for CustomBackgroundPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(OnEnter(AppState::Playing), spawn_custom_background);
    }
}
```

### 扩展配置反序列化

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NightingaleConfig {
    pub music_folder: String,
    #[serde(default = "default_separator")]
    pub separator: StemSeparator,
    #[serde(default = "default_guide_volume")]
    pub guide_vocal_volume: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum StemSeparator {
    #[default]
    Uvr,
    Demucs,
}

fn default_guide_volume() -> f32 { 0.3 }
fn default_separator() -> StemSeparator { StemSeparator::Uvr }

// 加载配置
fn load_config() -> NightingaleConfig {
    let path = dirs::home_dir()
        .unwrap()
        .join(".nightingale/config.json");
    let raw = std::fs::read_to_string(&path).unwrap_or_default();
    serde_json::from_str(&raw).unwrap_or_default()
}
```

### 程序触发重新分析

```rust
use std::fs;
use std::path::PathBuf;

/// 删除歌曲的缓存 stems/transcript 以强制重新分析
fn invalidate_song_cache(song_hash: &str) {
    let cache_dir = dirs::home_dir()
        .unwrap()
        .join(".nightingale/cache")
        .join(song_hash);

    if cache_dir.exists() {
        fs::remove_dir_all(&cache_dir)
            .expect("Failed to remove cache directory");
        println!("Cache invalidated for {}", song_hash);
    }
}
```

### 计算歌曲的Blake3哈希（用于缓存查找）

```rust
use blake3::Hasher;
use std::fs::File;
use std::io::{BufReader, Read};

fn hash_file(path: &std::path::Path) -> String {
    let file = File::open(path).expect("Cannot open file");
    let mut reader = BufReader::new(file);
    let mut hasher = Hasher::new();
    let mut buf = [0u8; 65536];
    loop {
        let n = reader.read(&mut buf).unwrap();
        if n == 0 { break; }
        hasher.update(&buf[..n]);
    }
    hasher.finalize().to_hex().to_string()
}
```

### 资料夹评分更新模式

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub struct SongScore {
    pub stars: u8,
    pub score: u32,
    pub played_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Profile {
    pub name: String,
    pub scores: HashMap<String, SongScore>, // key = blake3哈希
}

fn update_score(profile: &mut Profile, song_hash: &str, stars: u8, score: u32) {
    profile.scores.insert(song_hash.to_string(), SongScore {
        stars,
        score,
        played_at: chrono::Utc::now().to_rfc3339(),
    });
}
```

---

## 故障排除

### 引导失败 / 卡在设置界面

```bash
# 强制重新引导
./nightingale --setup

# 或者手动删除供应商目录并重启
rm -rf ~/.nightingale/vendor
./nightingale
```

### 歌曲分析卡住或出错

```bash
# 检查分析器venv是否健康
~/.nightingale/vendor/venv/bin/python -c "import whisperx; print('ok')"

# 如果损坏，重新引导
./nightingale --setup
```

### macOS "应用程序损坏"错误

```bash
xattr -cr Nightingale.app
```

### GPU未被使用

- **NVIDIA：** 确保安装了CUDA驱动程序，`nvidia-smi`显示您的GPU。
- **Apple Silicon：** 在macOS上使用Apple Silicon自动使用MPS；WhisperX对齐回退到CPU（正常行为）。
- 检查`~/.nightingale/vendor`——如果PyTorch安装了纯CPU构建，安装CUDA驱动程序后重新引导。

### 缓存损坏 / 歌词错误

```bash
# 找到您的文件的blake3哈希（构建一个小工具或使用b3sum）
b3sum /path/to/song.mp3

# 删除该歌曲的缓存
rm -rf ~/.nightingale/cache/<hash>
```

然后重新在Nightingale中打开歌曲以重新分析。

### Linux音频播放问题

确保ALSA/PulseAudio/PipeWire正在运行。安装缺失的依赖：
```bash
sudo apt install libasound2-dev libudev-dev libwayland-dev libxkbcommon-dev
```

### 视频背景未加载

视频背景在设置期间通过Pixabay API预下载。开发构建中，确保`.env`包含有效的`PIXABAY_API_KEY`。如果发布构建中视频缺失，运行`--setup`以重新触发下载。

---

## 平台目标

| 平台 | 目标三元组 |
|---|---|
| Linux x86_64 | `x86_64-unknown-linux-gnu` |
| Linux aarch64 | `aarch64-unknown-linux-gnu` |
| macOS ARM | `aarch64-apple-darwin` |
| macOS Intel | `x86_64-apple-darwin` |
| Windows x86_64 | `x86_64-pc-windows-msvc` |

交叉编译：
```bash
rustup target add aarch64-unknown-linux-gnu
cargo build --release --target aarch64-unknown-linux-gnu
```

---

## 许可证

GPL-3.0-or-later。见[LICENSE](https://github.com/rzru/nightingale/blob/main/LICENSE)。
