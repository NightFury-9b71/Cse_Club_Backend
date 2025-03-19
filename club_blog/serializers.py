from rest_framework import serializers
from .models import Post, Comment, Like
from django.contrib.auth import get_user_model

User = get_user_model()

# Post serializer to create and retrieve posts
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at']


# Comment serializer to create and retrieve comments
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)  # Make post read-only
    parent_comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'parent_comment']


# Like serializer to like posts and comments
class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False, allow_null=True)
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'comment', 'created_at']

    def validate(self, data):
        if not data.get('post') and not data.get('comment'):
            raise serializers.ValidationError("A like must be associated with either a post or a comment.")
        if data.get('post') and data.get('comment'):
            raise serializers.ValidationError("A like cannot be associated with both a post and a comment.")
        return data