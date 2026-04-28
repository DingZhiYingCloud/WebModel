"""DZY_Web 上下文处理器 - 注入站点变量到所有模板"""

from django.conf import settings


def site_context(request):
    """
    将站点配置注入所有模板上下文，模板中可直接使用：
    - {{ site_slug }}: 站点标识，如 youdaotools / whatsapp
    - {{ site_name }}: 站点显示名称，如 有道翻译 / WhatsApp助手
    - {{ site_description }}: 站点SEO描述
    - {{ site_url }}: 站点公开URL（从 ALLOWED_HOSTS 自动推导）
    - {{ site_favicon_static }}: favicon 的 static 相对路径（配合 {% static %} 使用）
    - {{ site_css }}: 站点CSS的static路径（用于 {% static site_css %}）
    """
    slug = settings.SITE_SLUG
    return {
        'site_slug': slug,
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
        'site_url': settings.SITE_URL,
        # favicon 使用 {% static site_favicon_static %} 引用，不要用 /media/ 路径
        'site_favicon_static': f'{slug}/img/favicon.png',
        'site_css': f'{slug}/css/main.bundle.min.css',
    }
