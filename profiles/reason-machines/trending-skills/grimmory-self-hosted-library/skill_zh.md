# Grimmory 自托管图书馆管理器

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集。

Grimmory 是一个自托管的应用程序（BookLore 的继任者），用于管理您的整个书籍收藏。它支持 EPUB、PDF、MOBI、AZW/AZW3 和漫画（CBZ/CBR/CB7），具有内置的浏览器阅读器、注释、Kobo/OPDS 同步、KOReader 进度同步、元数据丰富和多用户支持。

---

## 安装

### 要求
- Docker 和 Docker Compose

### 第一步：创建 `.env`

```ini
# 应用程序
APP_USER_ID=1000
APP_GROUP_ID=1000
TZ=Etc/UTC

# 数据库
DATABASE_URL=jdbc:mariadb://mariadb:3306/grimmory
DB_USER=grimmory
DB_PASSWORD=${DB_PASSWORD}

# 存储：LOCAL（默认）或 NETWORK
DISK_TYPE=LOCAL

# MariaDB
DB_USER_ID=1000
DB_GROUP_ID=1000
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_DATABASE=grimmory
```

### 第二步：创建 `docker-compose.yml`

```yaml
services:
  grimmory:
    image: grimmory/grimmory:latest
    # 备选镜像仓库：ghcr.io/grimmory-tools/grimmory:latest
    container_name: grimmory
    environment:
      - USER_ID=${APP_USER_ID}
      - GROUP_ID=${APP_GROUP_ID}
      - TZ=${TZ}
      - DATABASE_URL=${DATABASE_URL}
      - DATABASE_USERNAME=${DB_USER}
      - DATABASE_PASSWORD=${DB_PASSWORD}
      - DISK_TYPE=${DISK_TYPE}
    depends_on:
      mariadb:
        condition: service_healthy
    ports:
      - "6060:6060"
    volumes:
      - ./data:/app/data
      - ./books:/books
      - ./bookdrop:/bookdrop
    healthcheck:
      test: wget -q -O - http://localhost:6060/api/v1/healthcheck
      interval: 60s
      retries: 5
      start_period: 60s
      timeout: 10s
    restart: unless-stopped

  mariadb:
    image: lscr.io/linuxserver/mariadb:11.4.5
    container_name: mariadb
    environment:
      - PUID=${DB_USER_ID}
      - PGID=${DB_GROUP_ID}
      - TZ=${TZ}
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${DB_USER}
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - ./mariadb/config:/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mariadb-admin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10
```

### 第三步：启动

```bash
docker compose up -d

# 查看日志
docker compose logs -f grimmory

# 检查健康状态
curl http://localhost:6060/api/v1/healthcheck
```

打开 http://localhost:6060 并创建您的管理员账户。

---

## 卷布局

```
./data/          # 应用程序数据、缩略图、用户配置
./books/         # 您的书籍文件（挂载在 /books）
./bookdrop/      # 自动导入的放置区（挂载在 /bookdrop）
./mariadb/       # MariaDB 数据
```

---

## 环境变量参考

| 变量 | 描述 | 默认值 |
|---|---|---|
| `USER_ID` | 应用程序进程的 UID | `1000` |
| `GROUP_ID` | 应用程序进程的 GID | `1000` |
| `TZ` | 时区字符串 | `Etc/UTC` |
| `DATABASE_URL` | JDBC 连接字符串 | 必填 |
| `DATABASE_USERNAME` | 数据库用户名 | 必填 |
| `DATABASE_PASSWORD` | 数据库密码 | 必填 |
| `DISK_TYPE` | `LOCAL` 或 `NETWORK` | `LOCAL` |

---

## 支持的书籍格式

| 类别 | 格式 |
|---|---|
| 电子书 | EPUB, MOBI, AZW, AZW3 |
| 文档 | PDF |
| 漫画 | CBZ, CBR, CB7 |

---

## BookDrop（自动导入）

将文件拖放到主机上的 `./bookdrop/`。Grimmory 会监控该文件夹，从 Google Books 和 Open Library 提取元数据，并将书籍排队以供审核。

```
./bookdrop/
  my-novel.epub        ← 拖放到此处
  another-book.pdf     ← 拖放到此处
```

流程：
1. **监控** — Grimmory 持续监控 `/bookdrop`
2. **检测** — 新文件被拾取并解析
3. **丰富** — 从 Google Books / Open Library 获取元数据
4. **导入** — 在 UI 中审核，如有需要则调整，确认导入

`docker-compose.yml` 中需要卷映射：
```yaml
volumes:
  - ./bookdrop:/bookdrop
```

---

## 网络存储模式

对于 NFS、SMB 或其他网络挂载的文件系统，设置 `DISK_TYPE=NETWORK`。这将禁用破坏性 UI 操作（删除、移动、重命名）以保护共享挂载，同时保持阅读、元数据和同步功能完全可用。

```ini
# .env
DISK_TYPE=NETWORK
```

---

## Java 后端 — 关键模式

Grimmory 是一个 Java 应用程序（Spring Boot + MariaDB）。在贡献或扩展时：

### 项目结构（典型的 Spring Boot 布局）

```
src/main/java/
  com/grimmory/
    config/          # Spring 配置类
    controller/      # REST API 控制器
    service/         # 业务逻辑
    repository/      # JPA 仓库
    model/           # JPA 实体
    dto/             # 数据传输对象
```

### REST API — 基础路径

所有端点都在 `/api/v1/` 下：

```bash
# 健康检查
GET http://localhost:6060/api/v1/healthcheck

# 书籍
GET http://localhost:6060/api/v1/books
GET http://localhost:6060/api/v1/books/{id}
POST http://localhost:6060/api/v1/books
PUT http://localhost:6060/api/v1/books/{id}
DELETE http://localhost:6060/api/v1/books/{id}

# 书架
GET http://localhost:6060/api/v1/shelves
POST http://localhost:6060/api/v1/shelves

# OPDS 目录（用于兼容的阅读器应用程序）
GET http://localhost:6060/opds
```

### 示例：使用 Java（OkHttp）查询 API

```java
import okhttp3.*;
import com.fasterxml.jackson.databind.ObjectMapper;

public class GrimmoryClient {

    private final OkHttpClient http = new OkHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();
    private final String baseUrl;
    private final String token;

    public GrimmoryClient(String baseUrl, String token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }

    public String getBooks() throws Exception {
        Request request = new Request.Builder()
            .url(baseUrl + "/api/v1/books")
            .header("Authorization", "Bearer " + token)
            .build();

        try (Response response = http.newCall(request).execute()) {
            return response.body().string();
        }
    }
}
```

### 示例：Spring Boot 控制器模式

```java
@RestController
@RequestMapping("/api/v1/books")
@RequiredArgsConstructor
public class BookController {

    private final BookService bookService;

    @GetMapping
    public ResponseEntity<Page<BookDto>> getAllBooks(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String search) {
        return ResponseEntity.ok(bookService.findAll(page, size, search));
    }

    @GetMapping("/{id}")
    public ResponseEntity<BookDto> getBook(@PathVariable Long id) {
        return ResponseEntity.ok(bookService.findById(id));
    }

    @PostMapping
    public ResponseEntity<BookDto> createBook(@RequestBody @Valid CreateBookRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(bookService.create(request));
    }

    @PutMapping("/{id}/metadata")
    public ResponseEntity<BookDto> updateMetadata(
            @PathVariable Long id,
            @RequestBody @Valid UpdateMetadataRequest request) {
        return ResponseEntity.ok(bookService.updateMetadata(id, request));
    }
}
```

### 示例：JPA 实体模式

```java
@Entity
@Table(name = "books")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    private String author;
    private String isbn;
    private String format;  // EPUB, PDF, CBZ 等

    @Column(name = "file_path")
    private String filePath;

    @Column(name = "cover_path")
    private String coverPath;

    @Column(name = "reading_progress")
    private Double readingProgress;

    @ManyToMany
    @JoinTable(
        name = "book_shelf",
        joinColumns = @JoinColumn(name = "book_id"),
        inverseJoinColumns = @JoinColumn(name = "shelf_id")
    )
    private Set<Shelf> shelves = new HashSet<>();

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

### 示例：具有元数据丰富功能的 Service

```java
@Service
@RequiredArgsConstructor
public class MetadataService {

    private final GoogleBooksClient googleBooksClient;
    private final OpenLibraryClient openLibraryClient;
    private final BookRepository bookRepository;

    public BookDto enrichMetadata(Long bookId) {
        Book book = bookRepository.findById(bookId)
            .orElseThrow(() -> new BookNotFoundException(bookId));

        // 首先尝试 Google Books
        Optional<BookMetadata> metadata = googleBooksClient.search(book.getTitle(), book.getAuthor());

        // 如果失败则回退到 Open Library
        if (metadata.isEmpty()) {
            metadata = openLibraryClient.search(book.getIsbn());
        }

        metadata.ifPresent(m -> {
            book.setDescription(m.getDescription());
            book.setCoverUrl(m.getCoverUrl());
            book.setPublisher(m.getPublisher());
            book.setPublishedDate(m.getPublishedDate());
            bookRepository.save(book);
        });

        return BookDto.from(book);
    }
}
```

---

## OPDS 集成

使用以下方式连接任何 OPDS 兼容的阅读器应用程序（Kybook、Chunky、Moon+ Reader 等）：

```
http://<your-host>:6060/opds
```

在提示时使用您的 Grimmory 用户名和密码进行身份验证。

---

## Kobo / KOReader 同步

- **Kobo**：通过 Grimmory 设置中的设备同步功能连接。该应用程序提供了一个与 Kobo API 兼容的同步端点。
- **KOReader**：配置 KOReader 的同步插件以指向您的 Grimmory 实例 URL。

---

## 多用户与身份验证

### 本地身份验证
从管理面板（http://localhost:6060）创建用户。每个用户都有隔离的书架、阅读进度和偏好设置。

### OIDC 身份验证
通过环境变量配置（参考完整文档 https://grimmory.org/docs/getting-started 中的 OIDC 特定变量，如 `OIDC_ISSUER_URI`、`OIDC_CLIENT_ID`、`OIDC_CLIENT_SECRET`）。

---

## 从源代码构建

```bash
# 克隆仓库
git clone https://github.com/grimmory-tools/grimmory.git
cd grimmory

# 使用 Maven 构建
./mvnw clean package -DskipTests

# 或者本地构建 Docker 镜像
docker build -t grimmory:local .

# 在 docker-compose.yml 中使用本地构建
# 注释掉 'image' 并取消注释 'build: .'
```

---

## 常用 Docker 命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 查看应用程序日志
docker compose logs -f grimmory

# 查看数据库日志
docker compose logs -f mariadb

# 仅重新启动应用程序
docker compose restart grimmory

# 拉取最新镜像并重新部署
docker compose pull && docker compose up -d

# 在容器中打开 Shell
docker exec -it grimmory /bin/bash

# 数据库 Shell
docker exec -it mariadb mariadb -u grimmory -p grimmory
```

---

## 故障排除

### 容器无法启动 — DB 连接被拒绝
```bash
# 检查 MariaDB 健康状态
docker compose ps mariadb
# 应显示 "healthy"。如果不是：
docker compose logs mariadb
# 确保 DATABASE_URL 主机与服务名称匹配：mariadb:3306
```

### BookDrop 后书籍未出现
```bash
# 验证文件权限 — UID/GID 必须与 APP_USER_ID/APP_GROUP_ID 匹配
ls -la ./bookdrop/
# 检查应用程序日志以查看检测事件
docker compose logs -f grimmory | grep -i bookdrop
```

### ./books 或 ./data 权限被拒绝
```bash
# 设置所有权以匹配 APP_USER_ID / APP_GROUP_ID
sudo chown -R 1000:1000 ./books ./data ./bookdrop
```

### 阅读器应用程序无法访问 OPDS
```bash
# 确认从您的设备可达端口 6060
curl http://<host-ip>:6060/api/v1/healthcheck
# 如果在远程服务器上，请检查防火墙规则
```

### 内存使用过高
MariaDB 和 Grimmory 一起至少需要 ~512 MB 内存。对于大型图书馆（10k+ 本书），分配 1-2 GB。

### 元数据未丰富
Google Books 和 Open Library 需要从容器中获取出站互联网访问。验证 DNS 和网络：
```bash
docker exec -it grimmory curl -s "https://www.googleapis.com/books/v1/volumes?q=test"
```

---

## 贡献

在打开拉取请求之前：
1. 打开问题并获取维护者批准
2. 包括截图/视频证据和粘贴的测试输出
3. 遵循 `CONTRIBUTING.md` 中的后端和前端规范
4. 允许使用 AI 辅助代码，但您必须运行、测试和理解每一行

```bash
# 提交前运行测试
./mvnw test

# 检查代码风格
./mvnw checkstyle:check
```

---

## 链接

- **GitHub**: https://github.com/grimmory-tools/grimmory
- **Docker Hub**: https://hub.docker.com/r/grimmory/grimmory
- **GHCR**: `ghcr.io/grimmory-tools/grimmory`
- **Discord**: https://discord.gg/FwqHeFWk
- **文档**: https://grimmory.org/docs/getting-started
- **许可证**: AGPL-3.0
