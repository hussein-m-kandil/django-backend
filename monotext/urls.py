from django.urls import path

from . import views

app_name = "monotext"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('search/', views.SearchView.as_view(), name="post_search"),
    path("profile/<username>", views.ProfileView.as_view(), name="profile"),
    path("post/add/", views.PostCreateView.as_view(), name="post_create"),
    path("profile/<username>/post/<int:post_pk>/delete/",
         views.PostDeleteView.as_view(), name="post_delete"),
    path("profile/<username>/post/<int:post_pk>/",
         views.PostDetailView.as_view(), name="post_detail"),
    path("comment/<int:post_pk>/add/",
         views.CommentView.as_view(), name="comment_create"),
    path("post/<int:post_pk>/comments/",
         views.PostCommentsView.as_view(), name="post_comments"),
    path("post/<int:post_pk>/likes/",
         views.PostLikesCountView.as_view(), name="post_likes"),
    path("post/<int:post_pk>/like/",
         views.PostLikeView.as_view(), name="post_like"),
    path("post/<int:post_pk>/dislike/",
         views.PostDislikeView.as_view(), name="post_dislike"),
    path("post/<int:post_pk>/like/list/",
         views.LikeListView.as_view(), name="post_like_list"),
    path("post/profile/pic/", views.UserPictureView.as_view(),
         name="profile_change_pic"),
]
