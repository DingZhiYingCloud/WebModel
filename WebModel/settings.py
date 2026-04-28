import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# 跨域设置
SECURE_CROSS_ORIGIN_OPENER_POLICY = "None"
# 跨域请求配置，允许所有源的跨域请求
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
# 允许使用标签内嵌页面
X_FRAME_OPTIONS = 'ALLOWALL'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders', # 跨域请求中间件
    'DZY_API.apps.DzyApiConfig', # api应用
    'DZY_Web.apps.DzyWebConfig', # web应用
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # 跨域请求中间件
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'WebModel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'DZY_Web.context_processors.site_context',  # 注入站点变量到所有模板
            ],
        },
    },
]

WSGI_APPLICATION = 'WebModel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans' # 中文简体

TIME_ZONE = 'Asia/Shanghai' # 上海时间

USE_I18N = True # 开启国际化

USE_TZ = False # 开启时区支持


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

# 开发服务器查找静态文件的源目录（DEBUG=True 时生效）
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'DZY_Web', 'static'),
]

# collectstatic 输出目录（部署时 DEBUG=False 使用）
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')





# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# 邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '18171759943@163.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = True  # 新增这行
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', '18171759943@163.com')


# ===== 站点配置 =====
# 当前启用的站点标识，用于动态路由前缀、模板目录、文章筛选
# 对应 .env 中的 SITE_SLUG/SITE_NAME/SITE_DESCRIPTION
SITE_SLUG = os.getenv('SITE_SLUG', 'youdaotools')
SITE_NAME = os.getenv('SITE_NAME', '有道翻译')
SITE_DESCRIPTION = os.getenv('SITE_DESCRIPTION', '')

# 站点公开 URL（自动从 ALLOWED_HOSTS 推导，无需手动配置）
# 规则：本地地址 → http://host:8000，外部域名 → https://host
# 示例：ALLOWED_HOSTS=127.0.0.1 → http://127.0.0.1:8000
#       ALLOWED_HOSTS=example.com → https://example.com
_host = ALLOWED_HOSTS[0] if ALLOWED_HOSTS else '127.0.0.1'
_is_local = _host in ('127.0.0.1', 'localhost', '0.0.0.0')
SITE_URL = f'http://{_host}:8000' if _is_local else f'https://{_host}'