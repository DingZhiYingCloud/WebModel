from django.db import models


class Article(models.Model):
    """文章模型 - HTML内容存磁盘文件，数据库存元数据"""

    title = models.CharField(max_length=200, verbose_name="文章标题")
    slug = models.CharField(max_length=200, unique=True, verbose_name="路径名称（唯一标识，同时作为磁盘文件名）")
    cover_image = models.URLField(max_length=500, blank=True, default="", verbose_name="封面图URL")
    content_path = models.CharField(max_length=500, verbose_name="HTML内容文件相对路径（相对于MEDIA_ROOT）")
    word_count = models.IntegerField(default=0, verbose_name="字数（自动计算）")
    reading_time = models.IntegerField(default=0, verbose_name="阅读时长/分钟（自动计算）")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "article"
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# 迁移命令
# python manage.py makemigrations
# python manage.py migrate
