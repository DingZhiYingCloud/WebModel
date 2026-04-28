"""DZY_Web 自定义错误页面视图

Django 的 handler404/handler500 必须是模块级函数，且接收 request 参数。
模板路径固定为 system/error/ 目录，不随 SITE_SLUG 变化（错误页面是通用的）。
"""

from django.shortcuts import render
from django.conf import settings


def custom_404(request, exception=None):
    """自定义 404 页面 - 页面走丢啦"""
    return render(
        request,
        'system/error/404.html',
        {
            'site_name': settings.SITE_NAME,
            'site_favicon': f'/media/system/{settings.SITE_SLUG}/favicon-16x16.png',
        },
        status=404,
    )


def custom_500(request):
    """自定义 500 页面 - 服务器开小差啦"""
    return render(
        request,
        'system/error/500.html',
        {
            'site_name': settings.SITE_NAME,
            'site_favicon': f'/media/system/{settings.SITE_SLUG}/favicon-16x16.png',
        },
        status=500,
    )
