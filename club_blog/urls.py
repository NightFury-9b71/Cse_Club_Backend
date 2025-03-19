from django.urls import path
from . import views

urlpatterns = [
    path('post/<int:post_id>/details/', views.get_post_details, name='post_details'),
    path('post/', views.create_post, name='create_post'),
    path('blog/post/<int:post_id>/update/', views.update_post, name='update-post'), 
    path('blog/post/<int:post_id>/delete/', views.delete_post, name='delete-post'),

    path('post/<int:post_id>/comment/', views.create_comment, name='create_comment'),
    path('blog/comment/<int:comment_id>/update/', views.update_comment, name='update-comment'),
    path('blog/comment/<int:comment_id>/delete/', views.delete_comment, name='delete-comment'),
    
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/unlike/', views.unlike_post, name='unlike_post'),
    
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/unlike/', views.unlike_comment, name='unlike_comment'),
]
