from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .forms import CommentModelForm, PostModelForm
from .models import Comment, Like, Post, UserPicture

# Create your views here.

User = get_user_model()


class IndexView(generic.ListView):
    model = Post
    template_name = "posts/index.html"
    paginate_by = 3

    def get_queryset(self):
        return super().get_queryset().order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_form"] = PostModelForm()
        context["comment_form"] = CommentModelForm()
        return context


class ProfileView(generic.View):
    def get(self, request, username):
        owner = get_object_or_404(User, username=username)
        post_list = (
            Post.objects
            .filter(owner=owner)
            .select_related().order_by("-created_at")
        )
        # Paginator
        paginator = Paginator(post_list, 3, allow_empty_first_page=True)
        # Page number
        page_number = request.GET.get("page", False)
        if (page_number):
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = paginator.get_page(1)
        return render(
            request=request,
            template_name="posts/profile.html",
            context={
                "owner": owner,
                "post_list": page_obj.object_list,
                "object_list": page_obj.object_list,
                "is_paginated": True,
                "page_obj": page_obj,
                "paginator": paginator,
            }
        )


class PostDetailView(generic.View):
    def get(self, request, username, post_pk):
        return render(
            request=request,
            template_name="posts/post_detail.html",
            context={
                "post": get_object_or_404(Post, pk=post_pk),
            },
        )


class PostCreateView(LoginRequiredMixin, generic.View):
    def post(self, request):
        post_form = PostModelForm(data=request.POST)
        if not post_form.is_valid():
            return JsonResponse(post_form.errors)
        # Add the post's owner before saving it
        post = post_form.save(commit=False)
        post.owner = self.request.user
        post.save()
        return redirect(reverse(
            "monotext:post_detail",
            kwargs={
                "username": self.request.user.username,
                "post_pk": post.pk,
            },
        ))


class CommentView(LoginRequiredMixin, generic.View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        return redirect(reverse("login") + "?next=" + reverse(
            "monotext:post_detail",
            kwargs={
                "username": post.owner.username,
                "post_pk": post_pk,
            },
        ))

    def post(self, request, post_pk):
        comment_form = CommentModelForm(data=request.POST)
        if not comment_form.is_valid():
            return JsonResponse(comment_form.errors)
        # Add the comment's post and owner before saving it
        comment = comment_form.save(commit=False)
        comment.post = get_object_or_404(Post, pk=post_pk)
        comment.owner = self.request.user
        comment.save()
        return redirect(reverse(
            "monotext:post_detail",
            kwargs={
                "username": comment.owner,
                "post_pk": post_pk,
            },
        ))


class PostCommentsView(generic.View):
    def get(self, request, post_pk):
        """ Get the queryset of comments and paginate it, then, return the requested page number """
        # QuerySet
        comments = Comment.objects.filter(
            post=get_object_or_404(Post, pk=post_pk),
        ).select_related().order_by("created_at")
        # Paginator
        paginator = Paginator(comments, 2, allow_empty_first_page=True)
        # Page number
        page_number = request.GET.get("page", False)
        if (page_number):
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = paginator.get_page(1)
        # Regroup the comments after manipulating its inner data
        comments_chunk = []
        len_comments_chunk = page_obj.object_list.count()
        i = 0
        while i < len_comments_chunk:
            comment = page_obj.object_list[i]
            comments_chunk.append({
                "id": comment.id,
                "text": comment.text,
                "postID": comment.post.id,
                "ownerName": comment.owner.username,
                "ownerPic": comment.owner.user_picture.picture_path,
                "createdAt": naturaltime(comment.created_at),
                "updatedAt": naturaltime(comment.updated_at),
            })
            i += 1
        return JsonResponse({
            "commentsChunk": comments_chunk,
            "hasNext": page_obj.has_next(),
            "pageNumber": page_obj.number,
            "commentsCount": paginator.count,
        })


class PostLikesCountView(LoginRequiredMixin, generic.View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        likes = post.likes.count()
        return JsonResponse({"likes": likes})


class PostLikeView(LoginRequiredMixin, generic.View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        return redirect(reverse("login") + "?next=" + reverse(
            "monotext:post_detail",
            kwargs={
                "username": post.owner.username,
                "post_pk": post_pk,
            },
        ))

    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        like_obj = Like(post=post, owner=self.request.user)
        like_obj.save()
        return redirect(reverse("monotext:post_likes", kwargs={"post_pk": post_pk}))


class PostDislikeView(LoginRequiredMixin, generic.View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        return redirect(reverse("login") + "?next=" + reverse(
            "monotext:post_detail",
            kwargs={
                "username": post.owner.username,
                "post_pk": post_pk,
            },
        ))

    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        get_object_or_404(Like, post=post, owner=self.request.user).delete()
        return redirect(reverse("monotext:post_likes", kwargs={"post_pk": post_pk}))


class PostDeleteView(LoginRequiredMixin, generic.View):
    def get(self, request, username, post_pk):
        return redirect(reverse("login") + "?next=" + reverse(
            "monotext:post_detail",
            kwargs={
                "username": username,
                "post_pk": post_pk,
            },
        ))

    def post(self, request, username, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        # Check whether the current logged in user is the owner
        if self.request.user == post.owner:
            username = post.owner.username  # To make sure it is back to it's profile
            post.delete()
            return redirect(reverse("monotext:profile", kwargs={"username": username}))
        return redirect(reverse("monotext:profile", kwargs={"username": self.request.user.username}))


class LikeListView(generic.View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        like_list = (Like.objects
                     .filter(post=post)
                     .select_related()
                     .order_by("created_at"))
        chunk_size = 1  # To paginate based on it.
        # Paginator
        paginator = Paginator(
            like_list,
            chunk_size,
            allow_empty_first_page=True
        )
        # Page number
        page_number = request.GET.get("page", False)
        if (page_number):
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = paginator.get_page(1)
        # Regroup the model object data
        likes = []
        len_like_list = page_obj.object_list.count()
        i = 0
        while i < len_like_list:
            like_obj = page_obj.object_list[i]
            likes.append({
                "ownerName": like_obj.owner.username,
                "ownerProfilePage": reverse("monotext:profile", kwargs={"username": like_obj.owner.username}),
                "ownerPic": like_obj.owner.user_picture.picture_path,
                "createdAt": naturaltime(like_obj.created_at),
            })
            i += 1
        return JsonResponse({
            "likes": likes,
            "totalLikes": like_list.count(),
            "chunkSize": chunk_size,
        })


class SearchView(generic.View):
    def get(self, request):
        query = request.GET.get('q', '')
        if 0 < len(query) < 2048:
            post_list = Post.objects.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            ).select_related().order_by("-created_at")
            # Paginator
            paginator = Paginator(post_list, 3, allow_empty_first_page=True)
            # Page number
            page_number = request.GET.get("page", False)
            if (page_number):
                page_obj = paginator.get_page(page_number)
            else:
                page_obj = paginator.get_page(1)
            return render(
                request=request,
                template_name="posts/index.html",
                context={
                    "query": query,
                    "post_list": page_obj.object_list,
                    "object_list": page_obj.object_list,
                    "is_paginated": True,
                    "page_obj": page_obj,
                    "paginator": paginator,
                }
            )
        return redirect(reverse("monotext:index"))


class UserPictureView(LoginRequiredMixin, generic.CreateView):
    model = UserPicture
    template_name = "posts/choose_picture_form.html"
    fields = ["picture_path"]

    def get_success_url(self):
        return reverse("monotext:profile", kwargs={
            "username": self.request.user.username,
        })

    # def form_valid(self, form):
    #     """ Save the model object manually to avoid 'Unique Constraint' issues. (1st solution)"""
    #     object, created = UserPicture.objects.get_or_create(
    #         user=self.request.user,
    #         defaults={"picture_path": form.instance.picture_path},
    #     )
    #     if not created:
    #         object.picture_path = form.instance.picture_path
    #         object.save()
    #     return HttpResponseRedirect(self.get_success_url())

    # I think this solution, to avoid 'Unique Constraint' issues, is more concise ;).
    def form_valid(self, form):
        """ Save the model object manually to avoid 'Unique Constraint' issues. (2nd solution) """
        UserPicture.objects.filter(user=self.request.user).delete()
        form.instance.user = self.request.user
        return super().form_valid(form)
