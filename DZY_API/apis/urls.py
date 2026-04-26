# 项目URL配置
from django.urls import path, include

# api/
urlpatterns = [
    path("article/", include("DZY_API.apis.article.urls")),
]
