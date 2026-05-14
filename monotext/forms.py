from django.forms import ModelForm
from .models import Post, Comment


class PostModelForm(ModelForm):
    class Meta():
        model = Post
        fields = ["title", "text"]


class CommentModelForm(ModelForm):
    class Meta():
        model = Comment
        fields = ["text"]
