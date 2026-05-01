"""DZY_Web 路由配置 - 动态站点路由

路由前缀从 settings.SITE_SLUG 读取，修改 .env 即可切换站点。
URL name 使用通用名称 site_xxx，模板中统一用 {% url 'site_index' %} 等。

示例：
  SITE_SLUG=youdaotools → /web/youdaotools/
  SITE_SLUG=whatsapp    → /web/whatsapp/
"""

from django.conf import settings
from django.urls import path
from . import request

# 从 .env 中读取当前站点标识，作为路由前缀
site_slug = settings.SITE_SLUG

urlpatterns = [
    path(f'{site_slug}/', request.site_index, name='site_index'),
    path(f'{site_slug}/faq/', request.site_faq, name='site_faq'),
    path(f'{site_slug}/news/', request.site_news, name='site_news'),
    path(f'{site_slug}/news/<int:article_id>/', request.site_detail, name='site_detail'),
    path(f'{site_slug}/sitemap.xml', request.site_sitemap, name='site_sitemap'),
    path(f'{site_slug}/access-log/', request.site_access_log, name='site_access_log'),
]
