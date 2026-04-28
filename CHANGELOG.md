# 更新日志

> 作者：DingZhiYing

## v1.0.0

### WebModel 正式发布

WebModel v1.0.0 正式发布。目标：通过智能 AI 技术接管网站——从网页克隆、Django 动态化到 SEO 内容发布，全程无需手写代码。

## v0.1.1

### SITE_URL 由 ALLOWED_HOSTS 自动推导

移除 `.env` 中独立的 `SITE_URL` 配置项，改为 `settings.py` 从 `ALLOWED_HOSTS` 首条自动推导，消除重复配置。

### 站点地图插件上线

新增 `sitemap_generator` 插件，访问 `/web/{SITE_SLUG}/sitemap.xml` 动态生成当前站点全部文章的 XML sitemap。

### 项目初始化为纯净框架

清除 youdaotools 站点的全部模板、静态资源、媒体文件和数据库，重置 `.env` 为通用模板，合并迁移文件至 `0001_initial`。
