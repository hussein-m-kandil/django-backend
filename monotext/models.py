from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models

User = get_user_model()


class Post(models.Model):
    title = models.CharField(
        default="Untitled Post",
        blank=True,
        max_length=128,
        help_text="Your post's title...",
    )
    text = models.TextField(
        max_length=2048,
        help_text="Your post...",
        validators=[
            MinLengthValidator(2, "Post must have at least 2 characters!"),
        ],
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.ManyToManyField(
        User,
        through="Comment",
        related_name="posts_commented_on"
    )
    likes = models.ManyToManyField(
        User,
        through="Like",
        related_name="liked_posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_owner_pic(self):
        return UserPicture.objects.get(user=self.owner).picture_path

    def __str__(self):
        return self.title + " (" + str(self.pk) + ")"


class Comment(models.Model):
    text = models.TextField(
        max_length=2048,
        help_text="Comment...",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}, commented on '{self.post}'"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # https://docs.djangoproject.com/en/4.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ("post", "owner")

    def __str__(self):
        return self.owner.username + ", liked '" + self.post.title + "'"


class UserPicture(models.Model):
    picture_path = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(
                0, "Something wrong, negative values not allowed!"),
            MaxValueValidator(
                1, "Something wrong, greater than 1 values not allowed!"),
        ],
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_picture",
    )

    def __str__(self):
        return f"The picture's path for '{self.user.username}' is: {self.picture_path}"
