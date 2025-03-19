from django.contrib import admin
from .models import Post, Comment, Like

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'created_at', 'likes_count', 'comments_count']
    search_fields = ['title', 'content']
    list_filter = ['created_at']
    inlines = [CommentInline]

    def likes_count(self, obj):
        return obj.likes.count()

    likes_count.short_description = 'Likes Count'

    def comments_count(self, obj):
        return obj.comments.count()

    comments_count.short_description = 'Comments Count'

admin.site.register(Post, PostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'created_at', 'likes_count']
    search_fields = ['content']
    list_filter = ['created_at']

    def likes_count(self, obj):
        return obj.likes.count()

    likes_count.short_description = 'Likes Count'

admin.site.register(Comment, CommentAdmin)

class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'comment', 'created_at']
    list_filter = ['created_at']

admin.site.register(Like, LikeAdmin)
