# 获取文章列表

## 接口信息
- **URL**: `/api/article/list/`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | string | 否 | 1 | 页码（从1开始） |
| page_size | string | 否 | 10 | 每页数量（最大50） |

## 响应示例

### 成功 (code=0)
```json
{
    "code": 0,
    "message": "获取文章列表成功",
    "data": {
        "total": 27,
        "page": 1,
        "page_size": 10,
        "articles": [
            {
                "id": 1,
                "title": "有道翻译自定义模型微调入门",
                "slug": "custom-model-finetune",
                "cover_image": "https://example.com/cover.jpg",
                "word_count": 1520,
                "reading_time": 3,
                "created_at": "2026-04-26 20:00:00",
                "updated_at": "2026-04-26 20:00:00"
            }
        ]
    }
}
```

### 失败 - 分页参数不合法 (code=1002)
```json
{
    "code": 1002,
    "message": "分页参数不合法",
    "data": None
}
```

## 状态码说明

| code | 说明 |
|------|------|
| 0 | 成功 |
| 1002 | 分页参数不合法 |

## data 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 文章总数 |
| page | int | 当前页码 |
| page_size | int | 每页数量 |
| articles | array | 文章列表（不含 HTML 内容） |

## articles 数组内字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 文章 ID |
| title | string | 文章标题 |
| slug | string | 路径名称 |
| cover_image | string | 封面图 URL |
| word_count | int | 字数 |
| reading_time | int | 预计阅读时长（分钟） |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

## 备注
- 列表接口不返回 HTML 内容，需通过 detail 接口获取
- 按 `created_at` 倒序排列（最新文章在前）
