"""文章模块路由配置"""

from django.urls import path
from . import request

urlpatterns = [
    path("create/", request.create, name="article_create"),
    path("detail/", request.detail, name="article_detail"),
    path("update/", request.update, name="article_update"),
    path("delete/", request.delete, name="article_delete"),
    path("list/", request.article_list, name="article_list"),
]
