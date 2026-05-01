# WebModel

**通过智能 AI 技术接管网站。**

基于 Django 的 SEO 内容管理站点框架，从网页克隆、Django 动态化到 SEO 内容发布，全程无需手写代码。

**核心理念**：你不需要写一行代码，只需要三步——克隆网页 → 接入 Django → 发文章。

---

## 技术栈

- **后端**：Django 5.2 + SQLite3
- **前端**：Django 模板引擎 + HTML/CSS/JS
- **跨域**：django-cors-headers
- **日志**：loguru（DEBUG=True 时输出）
- **环境变量**：python-dotenv

---

## 安装教程

### 第 1 步：克隆项目

```bash
git clone https://github.com/<你的用户名>/WebModel.git
cd WebModel
```

### 第 2 步：创建虚拟环境并安装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

### 第 3 步：配置站点信息

打开项目根目录的 `.env` 文件，根据你的站点修改以下配置：

```env
# ===== 必须修改 =====
SITE_SLUG=yoursite              # 你的站点标识（英文小写，如 whatsapp / translatetool）
SITE_NAME=你的站点名称            # 站点显示名称（如 WhatsApp助手）
SITE_DESCRIPTION=你的站点描述      # SEO 描述

# ===== 按需修改 =====
SECRET_KEY=django-insecure-please-change-this-in-production  # 部署时务必替换
DEBUG=True                                                    # 部署时设为 False
ALLOWED_HOSTS=127.0.0.1                                       # 部署时改为你的域名（自动推导 SITE_URL）

ARTICLE_IMAGE_WATERMARK_TEXT=你的站点名  # 文章图片水印文字
ARTICLE_IMAGE_WATERMARK_POSITION=右下角  # 水印位置

EMAIL_HOST_USER=your-email@example.com   # Django Admin 密码重置用
EMAIL_HOST_PASSWORD=your-email-password
```

> **重要**：`SITE_URL` 不需要手动配置，由 `settings.py` 从 `ALLOWED_HOSTS` 自动推导：
> - `ALLOWED_HOSTS=127.0.0.1` → `http://127.0.0.1:8000`（本地开发）
> - `ALLOWED_HOSTS=example.com` → `https://example.com`（生产环境）

> **重要**：`SITE_SLUG` 决定了路由前缀、模板目录名和文章筛选。例如 `SITE_SLUG=yoursite` 则：
> - 访问地址：`/web/yoursite/`
> - 模板目录：`DZY_Web/templates/yoursite/`
> - 静态目录：`DZY_Web/static/yoursite/`

### 第 4 步：初始化数据库

```bash
python manage.py migrate
```

### 第 5 步：创建管理员账号

```bash
python manage.py createsuperuser
```

按提示输入用户名、邮箱、密码。

### 第 6 步：启动服务

```bash
python manage.py runserver 0.0.0.0:8000
```

此时访问 `http://127.0.0.1:8000/web/{你的SITE_SLUG}/` 会看到 404 页面——这是正常的，因为还没有网页模板。

---

## 三步搭建内容站点

项目提供了三个 AI 技能（位于 `.codebuddy/skills/` 目录），配合 CodeBuddy 使用，无需手动写代码：

### Step 1：克隆网页 → `web-clone` 技能

将目标网站的设计克隆为静态 HTML/CSS 文件。

**操作方式**：在 CodeBuddy 中输入：
```
用 web-clone 技能帮我克隆 https://目标网站.com
```

技能会自动：
- 抓取目标网页的完整 HTML/CSS
- 生成静态文件到 `DZY_Web/templates/{SITE_SLUG}/` 和 `DZY_Web/static/{SITE_SLUG}/`

### Step 2：接入 Django → `django-template-dynamic` 技能

将静态 HTML 转换为 Django 动态模板，实现数据驱动渲染。

**操作方式**：在 CodeBuddy 中输入：
```
用 django-template-dynamic 技能帮我把克隆的静态页面改成 Django 动态模板
```

技能会自动：
- 将静态 HTML 改造为 Django 模板语法（`{% for %}`、`{% url %}` 等）
- 对接 Article 模型和 API
- 创建列表页、详情页等动态页面

### Step 3：发布文章 → `article-creator` 或 `article-rewriter` 技能

**原创文章**（从零写）：
```
用 article-creator 技能帮我写一篇关于 XXX 的文章
```

**改写文章**（从 URL 抓取后改写）：
```
用 article-rewriter 技能帮我改写这篇文章 https://example.com/article
```

技能会自动：
- 生成 SEO 优化的原创内容
- 下载并添加水印到图片
- 调用 API 创建文章
- 返回文章访问地址

---

## 站点功能一览

完成三步后，你的站点自动拥有以下功能：

| 页面 | URL | 说明 |
|------|-----|------|
| 首页 | `/web/{SITE_SLUG}/` | 展示最新 6 篇文章 |
| 新闻列表 | `/web/{SITE_SLUG}/news/` | 分页展示所有文章 |
| 文章详情 | `/web/{SITE_SLUG}/news/<id>/` | 文章内容 + 上下篇导航 |
| FAQ | `/web/{SITE_SLUG}/faq/` | 常见问题 |
| 站点地图 | `/sitemap.xml` | XML sitemap（搜索引擎用） |
| 访问日志 | `/web/{SITE_SLUG}/access-log/` | 请求监控面板（密码保护） |

| API | URL | 说明 |
|-----|-----|------|
| 创建文章 | `/api/article/create/` | POST，必填：title, slug, html_content |
| 文章详情 | `/api/article/detail/` | POST，必填：id |
| 更新文章 | `/api/article/update/` | POST，必填：id |
| 删除文章 | `/api/article/delete/` | POST，必填：id |
| 文章列表 | `/api/article/list/` | POST，可选：page, page_size |

| 后台 | URL | 说明 |
|------|-----|------|
| Django Admin | `/admin/` | 文章管理、用户管理 |

---

## 项目结构

```
WebModel/
├── WebModel/              # 项目配置（settings / urls / wsgi）
├── DZY_API/               # 后端 API 层（POST-only，严格分层）
│   ├── models.py          # Article 数据模型
│   ├── admin.py           # 后台管理配置
│   └── apis/article/      # 文章 CRUD 模块
│       ├── request.py     # 视图层（HTTP 入口，零业务逻辑）
│       ├── service.py     # 业务层（纯数据处理）
│       ├── utils.py       # 工具层（统一响应封装）
│       └── status_codes.py # 模块专属状态码
├── DZY_Web/               # 前端页面层（Django 模板渲染）
│   ├── templates/         # HTML 模板（按站点分目录）
│   ├── static/            # 静态资源（按站点分目录）
│   ├── views/             # 页面视图 + 路由
│   └── context_processors.py # 全局模板变量注入
├── media/                 # 媒体文件（文章 HTML、图片等）
├── utils/                 # 工具插件
│   ├── 模块文件数据库/     # 插件源码（纯 Python，不依赖 Django）
│   ├── 模块文档/          # 插件使用教程
│   └── 插件开发规范.md     # 新插件开发指南
├── document/              # 项目文档
│   ├── API开发规范.md
│   └── 状态码.md
└── .codebuddy/skills/     # AI 技能
    ├── web-clone/         # 网页克隆
    ├── django-template-dynamic/ # Django 动态化
    ├── article-creator/   # 原创文章
    └── article-rewriter/  # 改写文章
```

---

## 部署

### 生产环境配置清单

1. 修改 `.env`：
   ```env
   SECRET_KEY=你的随机长密钥
   DEBUG=False
   ALLOWED_HOSTS=你的域名.com
   ```
   `SITE_URL` 会自动从 `ALLOWED_HOSTS` 推导为 `https://你的域名.com`，无需手动配置。

2. 收集静态文件：
   ```bash
   python manage.py collectstatic --noinput
   ```

3. 使用 Gunicorn / uWSGI 启动，用 Nginx 反向代理

---

## 开发规范

详见项目文档：

- [API 开发规范](document/API开发规范.md) — 分层架构、五步流程、版本管理
- [状态码规范](document/状态码.md) — 全局状态码与模块专属码定义
- [插件开发规范](utils/插件开发规范.md) — 新插件开发指南

---

## 许可证

参见 [LICENSE](LICENSE) 文件。
