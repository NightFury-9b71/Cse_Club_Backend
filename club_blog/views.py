from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])  # Only allow authenticated users
def get_post_details(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Retrieve comments for the post
    comments = Comment.objects.filter(post=post, parent_comment__isnull=True)  # Top-level comments
    comment_data = CommentSerializer(comments, many=True).data
    
    # Add replies to each comment and like counts
    for comment in comment_data:
        # Get likes for the comment
        comment_likes = Like.objects.filter(comment_id=comment['id'])
        comment['like_count'] = comment_likes.count()  # Add like count for the comment
        
        replies = Comment.objects.filter(parent_comment_id=comment['id'])
        # Add replies and their like counts
        for reply in replies:
            reply_likes = Like.objects.filter(comment_id=reply.id)
            comment_replies = CommentSerializer([reply], many=True).data
            comment_replies[0]['like_count'] = reply_likes.count()
            if 'replies' not in comment:
                comment['replies'] = []
            comment['replies'].append(comment_replies[0])

    # Get likes for the post
    post_likes = Like.objects.filter(post=post)
    post_like_count = post_likes.count()

    # Prepare the response data for the post
    post_data = PostSerializer(post).data
    post_data['comments'] = comment_data
    post_data['post_likes'] = post_like_count  # Add post like count

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
