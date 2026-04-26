# 创建文章

## 接口信息
- **URL**: `/api/article/create/`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| title | string | 是 | - | 文章标题，最长200字符 |
| slug | string | 是 | - | 路径名称（唯一标识），同时作为磁盘文件名，最长200字符 |
| html_content | string | 是 | - | 文章 HTML 内容 |
| cover_image | string | 否 | - | 封面图 URL |

## 响应示例

### 成功 (code=0)
```json
{
    "code": 0,
    "message": "文章创建成功",
    "data": {
        "id": 1,
        "title": "有道翻译自定义模型微调入门",
        "slug": "custom-model-finetune",
        "cover_image": "https://example.com/cover.jpg",
        "word_count": 1520,
        "reading_time": 3,
        "created_at": "2026-04-26 20:00:00",
        "updated_at": "2026-04-26 20:00:00"
    }
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

### 失败 - 必填参数缺失 (code=1001)
```json
{
    "code": 1001,
    "message": "参数 title 缺失",
    "data": None
}
```

## 状态码说明

| code | 说明 |
|------|------|
| 0 | 成功 |
| 1001 | 必填参数缺失 |
| 2002 | 路径名称已存在 |
| 2003 | 文章创建失败（数据库异常） |
| 2006 | 文章文件保存失败 |

## 备注
- `word_count` 和 `reading_time` 由系统自动计算，无需传入
- HTML 内容将保存至 `media/articles/{slug}.html`
