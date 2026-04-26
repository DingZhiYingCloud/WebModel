"""DZY_Web 视图层 - 页面渲染"""

import os
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from DZY_API.models import Article


def youdaotools_index(request):
    """有道翻译首页 - 展示最新6篇文章"""
    articles = Article.objects.all()[:6]
    return render(request, 'youdaotools/index.html', {'articles': articles})


def youdaotools_news(request):
    """新闻列表页 - 分页展示所有文章"""
    article_list = Article.objects.all()
    paginator = Paginator(article_list, 9)  # 每页9篇
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'youdaotools/news.html', {
        'articles': page_obj.object_list,
        'page_obj': page_obj,
    })


def youdaotools_faq(request):
    """常见问题页面"""
    return render(request, 'youdaotools/faq.html')


def youdaotools_detail(request, article_id):
    """文章详情页"""
    article = get_object_or_404(Article, id=article_id)

    # 从磁盘读取 HTML 内容
    content = ""
    try:
        full_path = os.path.join(settings.MEDIA_ROOT, article.content_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        content = "<p>文章内容加载失败</p>"

    # 相关文章（最新6篇，排除当前文章）
    related_articles = Article.objects.exclude(id=article.id)[:6]

    # 上一篇（id 比当前小的，即更早创建的）
    prev_article = Article.objects.filter(id__lt=article_id).order_by('-id').first()

    # 下一篇（id 比当前大的，即更晚创建的）
    next_article = Article.objects.filter(id__gt=article_id).order_by('id').first()

    return render(request, 'youdaotools/news_detail.html', {
        'article': article,
        'content': content,
        'related_articles': related_articles,
        'prev_article': prev_article,
        'next_article': next_article,
    })
