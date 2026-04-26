# WebModel

基于 Django 的内容管理 Web 应用，服务于「有道工具」网站。

## 技术栈

- **后端**: Django 5.2 + SQLite3
- **前端**: Django 模板引擎 + HTML/CSS/JS
- **跨域**: django-cors-headers
- **日志**: loguru（DEBUG=True 时输出）
- **环境变量**: python-dotenv

## 项目结构

```
WebModel/
├── WebModel/          # 项目配置（settings/urls/wsgi/asgi）
├── DZY_API/           # 后端 API 层（POST-only，严格分层）
│   └── apis/
│       └── article/   # 文章 CRUD 模块
├── DZY_Web/           # 前端页面层（Django 模板渲染）
│   ├── templates/     # HTML 模板
│   └── views/         # 页面视图
├── document/          # 项目文档
│   ├── API开发规范.md
│   └── 状态码.md
├── media/             # 媒体文件（文章 HTML 等）
├── manage.py
└── requirements.txt
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/<你的用户名>/WebModel.git
cd WebModel
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 3. 配置环境变量

复制并编辑 `.env` 文件：

```bash
# Django 核心配置
SECRET_KEY=你的密钥
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# 邮箱配置
EMAIL_HOST_USER=你的邮箱
EMAIL_HOST_PASSWORD=你的邮箱授权码
```

### 4. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 启动服务

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/web/youdaotools/ 查看网站。

## API 接口

所有接口统一使用 POST 方法，基础路径 `/api/`。

| 模块 | 接口 | URL | 说明 |
|------|------|-----|------|
| article | 创建 | `/api/article/create/` | 创建文章 |
| article | 详情 | `/api/article/detail/` | 获取文章详情 |
| article | 更新 | `/api/article/update/` | 更新文章 |
| article | 删除 | `/api/article/delete/` | 删除文章 |
| article | 列表 | `/api/article/list/` | 文章列表（分页） |

统一响应格式：

```json
{
    "code": 0,
    "message": "成功",
    "data": {...}
}
```

## 页面路由

基础路径 `/web/`。

| 页面 | URL | 说明 |
|------|-----|------|
| 首页 | `/web/youdaotools/` | 展示最新6篇文章 |
| 新闻列表 | `/web/youdaotools/news/` | 分页展示所有文章 |
| 文章详情 | `/web/youdaotools/news/<id>/` | 文章内容+上下篇导航 |
| FAQ | `/web/youdaotools/faq/` | 常见问题 |

## 开发规范

详见 `document/` 目录：

- [API 开发规范](document/API开发规范.md) — 分层架构、五步流程、版本管理
- [状态码规范](document/状态码.md) — 全局状态码与模块专属码定义

## 许可证

参见 [LICENSE](LICENSE) 文件。
