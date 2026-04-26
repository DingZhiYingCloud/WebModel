# 更新文章

## 接口信息
- **URL**: `/api/article/update/`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | string | 是 | - | 文章 ID |
| title | string | 否 | - | 新标题 |
| slug | string | 否 | - | 新路径名称（会同步重命名磁盘文件） |
| html_content | string | 否 | - | 新 HTML 内容（会重写磁盘文件并重新计算字数/阅读时长） |
| cover_image | string | 否 | - | 新封面图 URL |

> 注意：除 id 外，至少需要提供一个更新字段。

## 响应示例

### 成功 (code=0)
```json
{
    "code": 0,
    "message": "文章更新成功",
    "data": {
        "id": 1,
        "title": "更新后的标题",
        "slug": "updated-slug",
        "cover_image": "https://example.com/new-cover.jpg",
        "word_count": 2000,
        "reading_time": 5,
        "created_at": "2026-04-26 20:00:00",
        "updated_at": "2026-04-26 21:00:00"
    }
}
```

### 失败 - 无更新字段 (code=1002)
```json
{
    "code": 1002,
    "message": "至少需要提供一个更新字段",
    "data": None
}
```

### 失败 - 文章不存在 (code=2001)
```json
{
    "code": 2001,
    "message": "文章不存在",
    "data": None
}
```

### 失败 - 路径名称已存在 (code=2002)
```json
{
    "code": 2002,
    "message": "路径名称已存在",
    "data": None
}
```

## 状态码说明

| code | 说明 |
|------|------|
| 0 | 成功 |
| 1001 | 必填参数缺失 |
| 1002 | 参数不合法 / 无更新字段 |
| 2001 | 文章不存在 |
| 2002 | 路径名称已存在 |
| 2004 | 文章更新失败（数据库异常） |
| 2006 | 文章文件保存/重命名失败 |

## 更新逻辑说明
- 仅传入 `slug`（不改内容）：磁盘文件从 `old-slug.html` 重命名为 `new-slug.html`
- 仅传入 `html_content`（不改 slug）：覆盖原磁盘文件，重新计算字数和阅读时长
- 同时传入 `slug` + `html_content`：删除旧文件，以新 slug 保存新内容
- 传入 `title` 或 `cover_image`：仅更新数据库字段
