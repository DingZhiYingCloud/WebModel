# 项目URL配置
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('DZY_API.apis.urls')),
    path('web/', include('DZY_Web.views.urls')),

]
# 添加媒体文件URL配置
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)