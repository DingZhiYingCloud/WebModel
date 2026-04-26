# 获取文章详情

## 接口信息
- **URL**: `/api/article/detail/`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | string | 是 | - | 文章 ID |

## 响应示例

### 成功 (code=0)
```json
{
    "code": 0,
    "message": "获取文章详情成功",
    "data": {
        "id": 1,
        "title": "有道翻译自定义模型微调入门",
        "slug": "custom-model-finetune",
        "cover_image": "https://example.com/cover.jpg",
        "content": "<h1>正文HTML内容</h1><p>...</p>",
        "word_count": 1520,
        "reading_time": 3,
        "created_at": "2026-04-26 20:00:00",
        "updated_at": "2026-04-26 20:00:00"
    }
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

### 失败 - ID不合法 (code=1002)
```json
{
    "code": 1002,
    "message": "文章ID不合法",
    "data": None
}
```

## 状态码说明

| code | 说明 |
|------|------|
| 0 | 成功 |
| 1001 | 必填参数缺失 |
| 1002 | 参数不合法（ID非数字） |
| 2001 | 文章不存在 |
| 2007 | 文章文件读取失败 |

## data 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 文章 ID |
| title | string | 文章标题 |
| slug | string | 路径名称 |
| cover_image | string | 封面图 URL |
| content | string | HTML 正文内容（从磁盘文件读取） |
| word_count | int | 字数 |
| reading_time | int | 预计阅读时长（分钟） |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
