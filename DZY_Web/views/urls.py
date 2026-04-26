"""DZY_Web 路由配置"""

from django.urls import path
from . import request

urlpatterns = [
    path('youdaotools/', request.youdaotools_index, name='youdaotools_index'),
    path('youdaotools/faq/', request.youdaotools_faq, name='youdaotools_faq'),
    path('youdaotools/news/', request.youdaotools_news, name='youdaotools_news'),
    path('youdaotools/news/<int:article_id>/', request.youdaotools_detail, name='youdaotools_detail'),
]
