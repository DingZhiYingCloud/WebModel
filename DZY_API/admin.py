from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """文章后台管理"""
    list_display = ["id", "title", "slug", "cover_image", "word_count", "reading_time", "created_at", "updated_at"]
    list_display_links = ["id", "title"]
    search_fields = ["title", "slug"]
    list_filter = ["created_at"]
    readonly_fields = ["word_count", "reading_time", "created_at", "updated_at"]
    ordering = ["-created_at"]
    
