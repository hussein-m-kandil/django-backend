from django.core.management.base import BaseCommand
from django.utils import timezone as tz
from faker import Faker

from monotext.models import Comment, Like, Post, User, UserPicture

POST_COUNT = 50

fake = Faker()


def fakeDate(i: int):
    from_limit = f'{-60 - i}d'
    to_limit = f'{-30 - i}d'
    date = tz.make_aware(fake.date_time_between(from_limit, to_limit))
    return date


class Command(BaseCommand):
    help = 'Seeds the monotext app with data.'

    def handle(self, *args, **options):
        # Users
        queen_username = 'Queen'
        king_username = 'King'
        password = 'django123'
        date_joined = fakeDate(POST_COUNT * 2)
        queen_queryset = User.objects.filter(username=queen_username)
        king_queryset = User.objects.filter(username=king_username)
        queen = (
            queen_queryset.get()
            if queen_queryset.exists()
            else User.objects.create_user(
                username=queen_username, password=password, email=''
            )
        )
        User.objects.filter(pk=queen.pk).update(date_joined=date_joined)
        UserPicture.objects.get_or_create(user=queen, picture_path=0)
        king = (
            king_queryset.get()
            if king_queryset.exists()
            else User.objects.create_user(
                username=king_username, password=password, email=''
            )
        )
        User.objects.filter(pk=king.pk).update(date_joined=date_joined)
        UserPicture.objects.get_or_create(user=king, picture_path=1)
        users = [queen, king]
        # Posts
        self.stdout.write('Seeding Monotext', ending='')
        for n in range(POST_COUNT):
            self.stdout.write('.', ending='' if n < POST_COUNT - 1 else '\n')
            created_at = fakeDate(POST_COUNT - n) # Update created object to bypass `auto_now`
            author = fake.random_element(users)
            viewer = next(filter(lambda u: u.pk != author.pk, users))
            post = Post.objects.create(
                title=fake.sentence(fake.random_int(2, 5))[:-1],
                text=' '.join(fake.sentences(fake.random_int(1, 10))),
                owner=author,
            )
            Post.objects.filter(pk=post.pk).update(created_at=created_at, updated_at=created_at)
            comment = Comment.objects.create(
                text=' '.join(fake.sentences(fake.random_int(1, 3))),
                owner=viewer,
                post=post,
            )
            Comment.objects.filter(pk=comment.pk).update(created_at=created_at, updated_at=created_at)
            like = Like.objects.create(owner=viewer, post=post)
            Like.objects.filter(pk=like.pk).update(created_at=created_at, updated_at=created_at)
        self.stdout.write(
            self.style.SUCCESS(
                f'Monotext successfully seeded with {POST_COUNT} post{"" if POST_COUNT == 1 else "s"}.'
            )
        )
