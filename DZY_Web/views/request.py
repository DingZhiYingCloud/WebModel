"""DZY_Web 视图层 - 动态站点页面渲染

所有模板路径和文章查询都基于 settings.SITE_SLUG 动态生成。
切换站点只需修改 .env 中的 SITE_SLUG，重启 Django 即可生效。
"""

import os
import sys
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings
from DZY_API.models import Article

# 加载 sitemap_generator 模块
sys.path.insert(0, os.path.join(settings.BASE_DIR, 'utils', '模块文件数据库'))
from sitemap_generator import SitemapGenerator


def _get_site_slug():
    """获取当前站点标识"""
    return settings.SITE_SLUG


def _get_template(name):
    """根据站点标识拼接模板路径

    例：_get_template('index.html') → 'youdaotools/index.html'
    """
    return f'{_get_site_slug()}/{name}'


def _get_site_articles():
    """获取当前站点的文章 QuerySet"""
    return Article.objects.filter(site=_get_site_slug())


def _build_article_full_path(relative_path):
    """构建文章绝对路径，兼容历史 content_path 中的反斜杠。"""
    normalized = str(relative_path or "").replace("\\", "/").lstrip("/")
    parts = [p for p in normalized.split("/") if p]
    return os.path.join(settings.MEDIA_ROOT, *parts)


def site_index(request):
    """站点首页 - 展示最新6篇文章"""
    articles = _get_site_articles()[:6]
    return render(request, _get_template('index.html'), {'articles': articles})


def site_news(request):
    """新闻列表页 - 分页展示当前站点文章"""
    article_list = _get_site_articles()
    paginator = Paginator(article_list, 9)  # 每页9篇
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, _get_template('news.html'), {
        'articles': page_obj.object_list,
        'page_obj': page_obj,
    })


def site_faq(request):
    """常见问题页面"""
    return render(request, _get_template('faq.html'))


def site_detail(request, article_id):
    """文章详情页"""
    article = get_object_or_404(Article, id=article_id, site=_get_site_slug())

    # 从磁盘读取 HTML 内容
    content = ""
    try:
        full_path = _build_article_full_path(article.content_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        content = "<p>文章内容加载失败</p>"

    # 相关文章（当前站点最新6篇，排除当前文章）
    related_articles = _get_site_articles().exclude(id=article.id)[:6]

    # 上一篇（当前站点内id比当前小的）
    prev_article = _get_site_articles().filter(id__lt=article_id).order_by('-id').first()

    # 下一篇（当前站点内id比当前大的）
    next_article = _get_site_articles().filter(id__gt=article_id).order_by('id').first()

    return render(request, _get_template('news_detail.html'), {
        'article': article,
        'content': content,
        'related_articles': related_articles,
        'prev_article': prev_article,
        'next_article': next_article,
    })


def site_sitemap(request):
    """站点地图 - 动态生成当前站点的 XML sitemap

    访问 /web/{SITE_SLUG}/sitemap.xml 即可获取。
    包含当前站点所有文章详情页的 <loc>、<lastmod> 等信息。
    SITE_URL 由 settings 从 ALLOWED_HOSTS 自动推导，无需手动配置。
    """
    site_slug = _get_site_slug()
    site_url = settings.SITE_URL

    # 查询当前站点所有文章（按更新时间排序）
    articles = _get_site_articles().order_by('-updated_at')

    # 构建文章列表数据
    article_data = []
    for article in articles:
        article_data.append({
            'loc': f'/web/{site_slug}/news/{article.id}/',
            'lastmod': article.updated_at.strftime('%Y-%m-%d'),
        })

    # 生成 sitemap XML
    gen = SitemapGenerator(base_url=site_url)
    xml_string = gen.generate(article_data)

    return HttpResponse(xml_string, content_type='application/xml')
