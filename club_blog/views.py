from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow any user to view posts
def list_posts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_details(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Retrieve comments with related data
    comments = Comment.objects.filter(post=post, parent_comment__isnull=True).prefetch_related(
        'author', 'likes', 'replies__author', 'replies__likes'
    )
    
    comment_data = CommentSerializer(comments, many=True).data
    
    # Add likes and replies to comments
    for comment in comment_data:
        # Get likes for the comment
        comment_likes = Like.objects.filter(comment_id=comment['id'])
        comment['like_count'] = comment_likes.count()  # Add like count for the comment
        
        # Add author info for the comment (access author attributes directly)
        comment_author = comment['author']
        comment['author_name'] = comment_author['name'] if isinstance(comment_author, dict) else comment_author.name
        comment['author_role'] = comment_author['role'] if isinstance(comment_author, dict) else comment_author.role
        comment['author_avatar_url'] = comment_author['avatar'].url if hasattr(comment_author, 'avatar') else None
        
        # Get replies for the comment and process them
        comment['replies'] = []
        for reply in comment.get('replies', []):
            reply_likes = Like.objects.filter(comment_id=reply['id'])
            reply['like_count'] = reply_likes.count()  # Add like count for the reply
            
            # Add author info for the reply (access author attributes directly)
            reply_author = reply['author']
            reply['author_name'] = reply_author['name'] if isinstance(reply_author, dict) else reply_author.name
            reply['author_role'] = reply_author['role'] if isinstance(reply_author, dict) else reply_author.role
            reply['author_avatar_url'] = reply_author['avatar'].url if hasattr(reply_author, 'avatar') else None
            
            comment['replies'].append(reply)
    
    # Get likes for the post
    post_likes = Like.objects.filter(post=post)
    post_like_count = post_likes.count()
    
    # Prepare the response data for the post
    post_data = PostSerializer(post).data
    post_data['comments'] = comment_data
    post_data['like_count'] = post_like_count
    
    # Add author info for the post
    post_author = post.author
    post_data['author_name'] = post_author.name
    post_data['author_role'] = post_author.role
    post_data['author_avatar_url'] = post_author.avatar.url if hasattr(post_author, 'avatar') else None
    
    return Response(post_data, status=status.HTTP_200_OK)


# Create a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only allow authenticated users
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save(author=request.user)  # Assuming the user is authenticated
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PostSerializer(post, data=request.data, partial=False)  # Full update
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    post.delete()
    return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Create a comment on a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user, post=post)  # Attach post and user to the comment
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CommentSerializer(comment, data=request.data, partial=False)  # Full update
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    comment.delete()
    return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Reply to a comment
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_to_comment(request, comment_id):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        parent_comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user, post=parent_comment.post, parent_comment=parent_comment)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to Like a Post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has already liked the post
    if Like.objects.filter(user=request.user, post=post).exists():
        return Response({"error": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a like for the post
    like = Like.objects.create(user=request.user, post=post)
    return Response({"message": "Post liked successfully"}, status=status.HTTP_201_CREATED)


# View to unlike a Post
@api_view(['DELETE'])
def unlike_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has liked the post
    like = Like.objects.filter(user=request.user, post=post).first()
    if not like:
        return Response({"error": "You have not liked this post"}, status=status.HTTP_400_BAD_REQUEST)

    # Delete the like
    like.delete()
    return Response({"message": "Post unliked successfully"}, status=status.HTTP_200_OK)


# View to like a Comment
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_comment(request, comment_id):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has already liked the comment
    if Like.objects.filter(user=request.user, comment=comment).exists():
        return Response({"error": "You have already liked this comment"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a like for the comment
    like = Like.objects.create(user=request.user, comment=comment)
    return Response({"message": "Comment liked successfully"}, status=status.HTTP_201_CREATED)


# View to Unlike a Comment
@api_view(['DELETE'])
def unlike_comment(request, comment_id):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has liked the comment
    like = Like.objects.filter(user=request.user, comment=comment).first()
    if not like:
        return Response({"error": "You have not liked this comment"}, status=status.HTTP_400_BAD_REQUEST)

    # Delete the like
    like.delete()
    return Response({"message": "Comment unliked successfully"}, status=status.HTTP_200_OK)
