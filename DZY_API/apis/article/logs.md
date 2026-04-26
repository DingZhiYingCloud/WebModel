# article API 开发日志

## 项目概述

文章 CRUD 模块，HTML 内容存储在磁盘文件（`media/articles/{slug}.html`），数据库仅存元数据和文件路径。支持创建、详情、更新、删除、列表（分页）五个接口。

## 目录结构

```
DZY_API/apis/article/
├── __init__.py        # 包标识文件
├── request.py         # 视图层 —— HTTP 请求处理入口
├── urls.py            # 路由配置
├── utils.py           # 统一响应封装、参数获取辅助
├── service.py         # 业务逻辑层（文件操作 + CRUD）
├── status_codes.py    # 模块专属状态码（2000~2099）
├── logs.md            # 本文件
└── docs/              # 接口文档
    ├── create.md
    ├── detail.md
    ├── update.md
    ├── delete.md
    └── list.md
```

## 设计决策与约定

1. **内容存储**：HTML 存磁盘文件（`media/articles/{slug}.html`），数据库只存相对路径。理由：便于直接用 Nginx 静态托管大文件，数据库更轻量。
2. **字数/阅读时长**：自动计算，剥离 HTML 标签后统计纯文本字符数，阅读速度按 400 字/分钟。
3. **slug 即文件名**：路径名称同时作为磁盘文件名，保证唯一性（数据库 unique 约束）。
4. **物理删除**：同时删除磁盘文件和数据库记录，不可恢复。
5. **更新 slug 时文件重命名**：仅改 slug 不改内容时用 `os.rename`，同时改 slug 和内容时删除旧文件、创建新文件。
6. **权限**：开发阶段无鉴权，所有人可 CRUD。
7. **日志**：使用 loguru，仅在 `DEBUG=True` 时输出调试日志。

## 已实现接口清单

| 接口名 | URL | 功能 |
|--------|-----|------|
| create | `/api/article/create/` | 创建文章 |
| detail | `/api/article/detail/` | 获取文章详情 |
| update | `/api/article/update/` | 更新文章 |
| delete | `/api/article/delete/` | 删除文章 |
| list | `/api/article/list/` | 获取文章列表（分页） |

## 注意事项

1. **cover_image 清空**：当前 `get_param` 将空字符串视为"未提供"，无法通过 update 接口将 cover_image 清空为空字符串。如需此功能，需扩展 `get_param` 或新增辅助函数。
2. **文件一致性**：创建文章时如果数据库写入失败，会自动回滚已保存的磁盘文件。但极端情况（如进程崩溃）可能导致孤立文件。
3. **并发安全**：slug 的唯一性依赖数据库约束，高并发创建相同 slug 时有一个会失败，这是预期行为。
4. **HTML 内容大小**：无硬性限制，但过大的 HTML 可能导致 POST 请求超时，建议控制在 10MB 以内。

## 版本历史

### v1.0.0 (2026-04-26)
- [新增] 创建文章 CRUD 模块（create/detail/update/delete/list）
- [新增] 建立 utils / service 分层架构
- [新增] HTML 内容磁盘存储 + 元数据数据库存储
- [新增] 字数和阅读时长自动计算
- [新增] loguru 调试日志（DEBUG=True 时启用）
- [作者] AI-Assistant

## 后续待办（供参考）

- [ ] 接入用户认证系统后添加权限控制
- [ ] 支持 cover_image 清空
- [ ] 软删除选项
- [ ] 文章分类/标签
- [ ] 全文搜索
- [ ] 批量操作接口
