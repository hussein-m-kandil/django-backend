from django.contrib.humanize.templatetags.humanize import naturaltime
from django.test import TestCase
from django.urls import reverse

from ..forms import CommentModelForm, PostModelForm
from ..models import Comment, Like, Post, User, UserPicture


class IndexViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        Post.objects.create(
            title='Post #1',
            text='Blah...',
            owner=user,
        )
        Post.objects.create(
            title='Post #2',
            text='Blah blah...',
            owner=user,
        )
        Post.objects.create(
            title='Post #3',
            text='Blah blah blah...',
            owner=user,
        )
        Post.objects.create(
            title='Post #4',
            text='Blah blah blah blah...',
            owner=user,
        )

    def test_post_comment_forms_in_context(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(reverse('monotext:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            (
                'post_form' in response.context
                and 'comment_form' in response.context
            )
        )
        self.assertTrue(
            (
                isinstance(response.context['post_form'], PostModelForm)
                and isinstance(
                    response.context['comment_form'], CommentModelForm
                )
            )
        )
        self.client.logout()

    def test_posts_order_in_context(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(reverse('monotext:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['post_list']), 3)
        self.assertEqual(response.context['post_list'][0], Post.objects.last())
        self.client.logout()


class ProfileViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'
    username2 = 'Sparrow'
    password2 = 'pass321'

    def setUp(self):
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.user2 = User.objects.create_user(
            username=self.username2,
            password=self.password2,
        )
        Post.objects.create(
            title='user1 post #1',
            text='blah...',
            owner=self.user1,
        )
        Post.objects.create(
            title='user1 post #2',
            text='blah 2...',
            owner=self.user1,
        )
        Post.objects.create(
            title='user1 post #3',
            text='blah 3...',
            owner=self.user1,
        )
        Post.objects.create(
            title='user1 post #4',
            text='blah 4...',
            owner=self.user1,
        )
        Post.objects.create(
            title='user2 post #1',
            text='blah...',
            owner=self.user2,
        )
        Post.objects.create(
            title='user2 post #2',
            text='blah 2...',
            owner=self.user2,
        )
        Post.objects.create(
            title='user2 post #3',
            text='blah 3...',
            owner=self.user2,
        )
        Post.objects.create(
            title='user2 post #4',
            text='blah 4...',
            owner=self.user2,
        )
        self.user1_post_list = (
            Post.objects.filter(owner=self.user1)
            .select_related()
            .order_by('-created_at')
        )
        self.user2_post_list = (
            Post.objects.filter(owner=self.user2)
            .select_related()
            .order_by('-created_at')
        )

    def test_get_only_user1_profile_posts(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(
            reverse(
                'monotext:profile',
                kwargs={
                    'username': self.username,
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        len_post_list = len(response.context['post_list'])
        i = 0
        while i < len_post_list:
            self.assertEqual(
                response.context['post_list'][i],
                self.user1_post_list[i],
            )
            i += 1

    def test_get_only_user2_profile_posts(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(
            reverse(
                'monotext:profile',
                kwargs={
                    'username': self.username2,
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        len_post_list = len(response.context['post_list'])
        i = 0
        while i < len_post_list:
            self.assertEqual(
                response.context['post_list'][i],
                self.user2_post_list[i],
            )
            i += 1

    def test_pagination_3_posts_per_page(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        url = (
            reverse('monotext:profile', kwargs={'username': self.username})
            + '?page=1'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        len_post_list = len(response.context['post_list'])
        self.assertEqual(len_post_list, 3)
        i = 0
        while i < len_post_list:
            self.assertEqual(
                response.context['post_list'][i],
                self.user1_post_list[i],
            )
            i += 1
        self.assertTrue(response.context['page_obj'].has_next())


class PostDetailViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.post = Post.objects.create(
            title='Strong Post',
            text='These are strong words of the strong post.',
            owner=user,
        )

    def test_get_post_detail_page(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(
            reverse(
                'monotext:post_detail',
                kwargs={
                    'username': self.username,
                    'post_pk': self.post.pk,
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('post' in response.context)
        self.assertEqual(response.context['post'], self.post)
        self.client.logout()


class PostCreateViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.post = Post.objects.create(
            title='Strong Post',
            text='These are strong words of the strong post.',
            owner=user,
        )
        self.form = PostModelForm()

    def test_redirect_without_log_in(self):
        response = self.client.get(
            reverse('monotext:post_create'), follow=True
        )
        self.assertRedirects(
            response,
            '/accounts/login/?next=' + reverse('monotext:post_create'),
        )
        response = self.client.get(reverse('monotext:post_create'))
        self.assertRedirects(
            response,
            '/accounts/login/?next=' + reverse('monotext:post_create'),
        )
        self.client.logout()

    def test_json_errors_with_invalid_text_field(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        self.form.data['title'] = ''
        self.form.data['text'] = 'A'
        response = self.client.post(
            reverse('monotext:post_create'),
            self.form.data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertEqual(
            json_resp['text'][0], 'Post must have at least 2 characters!'
        )
        self.assertRaises(KeyError, lambda: json_resp['title'])
        self.client.logout()

    def test_redirect_with_valid_text_field(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        self.form.data['title'] = 'New Post'
        self.form.data['text'] = 'Nice post!'
        response = self.client.post(
            reverse('monotext:post_create'),
            self.form.data,
            follow=True,
        )
        self.post = Post.objects.last()
        self.assertRedirects(
            response,
            reverse(
                'monotext:post_detail',
                kwargs={
                    'username': self.username,
                    'post_pk': getattr(self.post, 'pk'),
                },
            ),
        )
        self.assertEqual(Post.objects.all().count(), 2)
        self.assertTrue(getattr(Post.objects.last(), 'title') == 'New Post')
        self.client.logout()


class CommentViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.post = Post.objects.create(
            title='Strong Post',
            text='These are strong words of the strong post.',
            owner=user,
        )
        self.form = CommentModelForm()

    def test_redirect_without_log_in(self):
        self.form.data['text'] = ''
        url = reverse(
            'monotext:comment_create',
            kwargs={'post_pk': self.post.pk},
        )
        response = self.client.post(url, self.form.data, follow=True)
        self.assertRedirects(
            response,
            '/accounts/login/?next=' + url,
        )
        response = self.client.get(url, self.form.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login') + '?next='))  # type: ignore
        self.client.logout()

    def test_json_errors_with_invalid_text_field(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        self.form.data['text'] = ''
        response = self.client.post(
            reverse(
                'monotext:comment_create', kwargs={'post_pk': self.post.pk}
            ),
            self.form.data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertEqual(json_resp['text'][0], 'This field is required.')
        self.client.logout()

    def test_redirect_with_valid_text_field(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        self.form.data['text'] = 'Nice post!'
        response = self.client.post(
            reverse(
                'monotext:comment_create', kwargs={'post_pk': self.post.pk}
            ),
            self.form.data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'monotext:post_detail',
                kwargs={
                    'username': self.username,
                    'post_pk': self.post.pk,
                },
            ),
        )
        self.client.logout()


class PostCommentsViewTest(TestCase):
    """NOTE: This tests assumes that the comments chunks are paginated by '2'"""

    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        """Create a post to put some comments on it."""
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        UserPicture.objects.create(picture_path=0, user=user)
        self.post = Post.objects.create(
            title='Strong Post',
            text='These are strong words of the strong post.',
            owner=user,
        )
        comments_text = [
            'This is a real strong post!',
            'String words!',
            'Nice post!',
            'Keep it up!',
            'Good job!',
        ]
        i = 0
        while i < 5:
            Comment.objects.select_related().create(
                text=comments_text[i],
                post=self.post,
                owner=user,
            )
            i += 1
        # Attributes for the post and its comments.
        self.post = Post.objects.first()
        self.comments_qs = (
            Comment.objects.filter(post=self.post)
            .select_related()
            .order_by('-created_at')
        )

    def test_first_comments_chunk_without_get_arg(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(
            reverse(
                'monotext:post_comments',
                kwargs={'post_pk': getattr(self.post, 'pk')},
            )
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        id = 1
        for comment_obj in json_resp['commentsChunk']:
            self.assertEqual(
                comment_obj['text'],
                self.comments_qs.get(id=comment_obj['id']).text,
            )
            self.assertTrue(
                self.comments_qs.get(id=comment_obj['id']),
            )
            id += 1
        self.assertTrue(json_resp['hasNext'])
        self.assertEqual(json_resp['commentsCount'], 5)
        self.client.logout()

    def test_first_comments_chunk_in_another_page(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(
            reverse(
                'monotext:post_comments',
                kwargs={'post_pk': getattr(self.post, 'pk')},
            )
            + '?page=1'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        id = 3
        for comment_obj in json_resp['commentsChunk']:
            self.assertEqual(
                comment_obj['text'],
                self.comments_qs.get(id=comment_obj['id']).text,
            )
            self.assertTrue(
                self.comments_qs.get(id=comment_obj['id']),
            )
            self.assertEqual(comment_obj['ownerPic'], 0)
            id += 1
        self.assertTrue(json_resp['hasNext'])
        self.client.logout()

    def test_second_comments_chunk(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        response = self.client.get(
            reverse(
                'monotext:post_comments',
                kwargs={'post_pk': getattr(self.post, 'pk')},
            )
            + '?page=2'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        id = 3
        for comment_obj in json_resp['commentsChunk']:
            self.assertEqual(
                comment_obj['text'],
                self.comments_qs.get(id=comment_obj['id']).text,
            )
            self.assertTrue(
                self.comments_qs.get(id=comment_obj['id']),
            )
            self.assertEqual(comment_obj['ownerPic'], 0)
            id += 1
        self.assertTrue(json_resp['hasNext'])
        self.client.logout()

    def test_first_comments_chunk(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        self.client.post(
            reverse('monotext:profile_change_pic'),
            data={'picture_path': 1},
            follow=True,
        )
        response = self.client.get(
            reverse(
                'monotext:post_comments',
                kwargs={'post_pk': getattr(self.post, 'pk')},
            )
            + '?page=3'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        id = 5
        for comment_obj in json_resp['commentsChunk']:
            self.assertEqual(
                comment_obj['text'],
                self.comments_qs.get(id=comment_obj['id']).text,
            )
            self.assertTrue(
                self.comments_qs.get(pk=comment_obj['id']),
            )
            self.assertEqual(comment_obj['ownerPic'], 1)
            id += 1
        self.assertFalse(json_resp['hasNext'])
        self.client.logout()

    def test_last_comments_chunk_with_page_number_beyond_range(self):
        is_logged_in = self.client.login(
            username=self.username,
            password=self.password,
        )
        self.assertTrue(is_logged_in)
        self.client.post(
            reverse('monotext:profile_change_pic'),
            data={'picture_path': 1},
            follow=True,
        )
        response = self.client.get(
            reverse(
                'monotext:post_comments',
                kwargs={'post_pk': getattr(self.post, 'pk')},
            )
            + '?page=4'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        id = 5
        for comment_obj in json_resp['commentsChunk']:
            self.assertEqual(
                comment_obj['text'],
                self.comments_qs.get(id=comment_obj['id']).text,
            )
            self.assertTrue(
                self.comments_qs.get(id=comment_obj['id']),
            )
            self.assertEqual(comment_obj['ownerPic'], 1)
            id += 1
        self.assertFalse(json_resp['hasNext'])
        self.client.logout()


class PostLikesAndPostDislikeViewsTest(TestCase):
    username1 = 'Jack'
    username2 = 'Sparrow'
    password1 = 'pass123'
    password2 = 'pass321'

    def setUp(self):
        self.user1 = User.objects.create_user(
            username=self.username1, password=self.password1
        )
        self.user2 = User.objects.create_user(
            username=self.username2, password=self.password2
        )
        self.post1 = Post.objects.create(text='Blah 1...', owner=self.user1)
        self.post2 = Post.objects.create(text='Blah 2...', owner=self.user2)
        Like.objects.create(post=self.post2, owner=self.user1)
        Like.objects.create(post=self.post2, owner=self.user2)

    def login_logic(self, username, password):
        return self.client.login(
            username=username,
            password=password,
        )

    def test_redirect_with_get_like(self):
        self.assertTrue(self.login_logic(self.username1, self.password1))
        response = self.client.get(
            reverse('monotext:post_like', kwargs={'post_pk': self.post1.pk})
        )
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'monotext:post_detail',
                kwargs={
                    'username': self.post1.owner.username,
                    'post_pk': self.post1.pk,
                },
            ),
        )

    def test_redirect_with_get_dislike(self):
        self.assertTrue(self.login_logic(self.username1, self.password1))
        response = self.client.get(
            reverse('monotext:post_dislike', kwargs={'post_pk': self.post2.pk})
        )
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'monotext:post_detail',
                kwargs={
                    'username': self.post2.owner.username,
                    'post_pk': self.post2.pk,
                },
            ),
        )

    def test_likes_count_before_any_likes(self):
        self.assertTrue(self.login_logic(self.username1, self.password1))
        response = self.client.get(
            reverse('monotext:post_likes', kwargs={'post_pk': self.post1.pk})
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertTrue('likes' in json_resp)
        self.assertEqual(json_resp['likes'], 0)
        self.client.logout()

    def test_likes_count_after_some_likes(self):
        # 'user1' like 'post1'
        self.assertTrue(self.login_logic(self.username1, self.password1))
        response = self.client.post(
            reverse('monotext:post_like', kwargs={'post_pk': self.post1.pk}),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('monotext:post_likes', kwargs={'post_pk': self.post1.pk}),
        )
        json_resp = response.json()
        self.assertTrue('likes' in json_resp)
        self.assertEqual(json_resp['likes'], 1)
        self.client.logout()
        # 'user2' like 'post1'
        self.assertTrue(self.login_logic(self.username2, self.password2))
        response = self.client.post(
            reverse('monotext:post_like', kwargs={'post_pk': self.post1.pk}),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('monotext:post_likes', kwargs={'post_pk': self.post1.pk}),
        )
        json_resp = response.json()
        self.assertTrue('likes' in json_resp)
        self.assertEqual(json_resp['likes'], 2)
        self.client.logout()

    def test_likes_count_after_some_dislikes(self):
        # User1 dislike post2
        self.assertTrue(self.login_logic(self.username1, self.password1))
        response = self.client.post(
            reverse(
                'monotext:post_dislike', kwargs={'post_pk': self.post2.pk}
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('monotext:post_likes', kwargs={'post_pk': self.post2.pk}),
        )
        json_resp = response.json()
        self.assertTrue('likes' in json_resp)
        self.assertEqual(json_resp['likes'], 1)
        self.client.logout()
        # 'user2' dislike 'post2'
        self.assertTrue(self.login_logic(self.username2, self.password2))
        response = self.client.post(
            reverse(
                'monotext:post_dislike', kwargs={'post_pk': self.post2.pk}
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('monotext:post_likes', kwargs={'post_pk': self.post2.pk}),
        )
        json_resp = response.json()
        self.assertTrue('likes' in json_resp)
        self.assertEqual(json_resp['likes'], 0)
        self.client.logout()


class PostDeleteViewTest(TestCase):
    username1 = 'Jack'
    username2 = 'Sparrow'
    password = 'pass123'

    def setUp(self):
        self.user1 = User.objects.create_user(
            username=self.username1,
            password=self.password,
        )
        self.user2 = User.objects.create_user(
            username=self.username2,
            password=self.password,
        )
        self.post = Post.objects.create(
            text='Blah...',
            owner=self.user1,
        )

    def login_logic(self, username, password):
        return self.client.login(
            username=username,
            password=password,
        )

    def test_redirect_to_login_if_not(self):
        response = self.client.post(
            reverse(
                'monotext:post_delete',
                kwargs={
                    'username': self.user1.username,
                    'post_pk': self.post.pk,
                },
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'monotext:post_delete',
                kwargs={
                    'username': self.user1.username,
                    'post_pk': self.post.pk,
                },
            ),
        )

    def test_redirect_to_post_detail_if_get_request(self):
        self.assertTrue(self.login_logic(self.username1, self.password))
        response = self.client.get(
            reverse(
                'monotext:post_delete',
                kwargs={
                    'username': self.user1.username,
                    'post_pk': self.post.pk,
                },
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'monotext:post_detail',
                kwargs={
                    'username': self.user1.username,
                    'post_pk': self.post.pk,
                },
            ),
        )

    def test_redirect_to_profile_if_not_post_owner(self):
        self.assertTrue(self.login_logic(self.username2, self.password))
        response = self.client.post(
            reverse(
                'monotext:post_delete',
                kwargs={
                    'username': self.user1.username,
                    'post_pk': self.post.pk,
                },
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'monotext:profile',
                kwargs={
                    'username': self.user2.username,
                },
            ),
        )

    def test_redirect_to_profile_after_delete_if_post_owner(self):
        self.assertTrue(self.login_logic(self.username1, self.password))
        self.assertTrue(Post.objects.get(pk=self.post.pk) == self.post)
        response = self.client.post(
            reverse(
                'monotext:post_delete',
                kwargs={
                    'username': self.user1.username,
                    'post_pk': self.post.pk,
                },
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'monotext:profile',
                kwargs={
                    'username': self.user1.username,
                },
            ),
        )
        self.assertRaises(
            Post.DoesNotExist,
            lambda: Post.objects.get(pk=self.post.pk),
        )


class SearchViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        Post.objects.create(
            title='Foo',
            text='....',
            owner=user1,
        )
        Post.objects.create(
            text='Bar...',
            owner=user1,
        )

    def test_redirect_to_index_with_empty_query(self):
        response = self.client.get(
            reverse('monotext:post_search') + '?q=',
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('monotext:index'),
        )
        response = self.client.get(
            reverse('monotext:post_search'),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('monotext:index'),
        )

    def test_get_right_search_result(self):
        query1 = 'fo'
        query2 = 'ba'
        response = self.client.get(
            reverse('monotext:post_search') + '?q=' + query1,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query'], query1)
        self.assertEqual(len(response.context['post_list']), 1)
        self.assertTrue(
            query1.lower() in response.context['post_list'][0].title.lower()
        )
        response = self.client.get(
            reverse('monotext:post_search') + '?q=' + query2,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query'], query2)
        self.assertEqual(len(response.context['post_list']), 1)
        self.assertTrue(
            query2.lower() in response.context['post_list'][0].text.lower()
        )


class UserPictureViewTest(TestCase):
    username = 'Jack'
    password = 'pass123'

    def setUp(self):
        User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def login_logic(self, username, password):
        return self.client.login(
            username=username,
            password=password,
        )

    def test_redirected_if_not_logged_in(self):
        next = '?next=' + reverse('monotext:profile_change_pic')
        response = self.client.get(reverse('monotext:profile_change_pic'))
        self.assertRedirects(response, reverse('login') + next)
        response = self.client.post(reverse('monotext:profile_change_pic'))
        self.assertRedirects(response, reverse('login') + next)

    def test_error_with_invalid_form_data(self):
        self.assertTrue(self.login_logic(self.username, self.password))
        vs = (-1, 2)
        for v in vs:
            response = self.client.post(
                reverse('monotext:profile_change_pic'),
                data={'picture_path': v},
                follow=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue('form' in response.context)
            form = response.context['form']
            self.assertTrue('picture_path' in form.data)
            self.assertTrue(form.errors['picture_path'])
            self.assertTrue(len(form.errors['picture_path']) > 0)
        self.client.logout()

    def test_redirected_to_profile_page_after_form_success(self):
        self.assertTrue(self.login_logic(self.username, self.password))
        vs = (0, 1)
        for v in vs:
            response = self.client.post(
                reverse('monotext:profile_change_pic'),
                data={'picture_path': v},
                follow=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertRedirects(
                response,
                reverse(
                    'monotext:profile', kwargs={'username': self.username}
                ),
            )
            last_model_obj = UserPicture.objects.last()
            self.assertEqual(last_model_obj.user.username, self.username)  # type: ignore
            self.assertEqual(last_model_obj.picture_path, v)  # type: ignore
        self.client.logout()


class LikeListViewTest(TestCase):
    usernames = ['Foo', 'Bar', 'Baz', 'Tar', 'Zee']
    password = 'pass123'
    users = []

    def setUp(self):
        # Fill the class's users list
        len_usernames = len(self.usernames)
        i = 0
        while i < len_usernames:
            user = User.objects.create_user(
                username=self.usernames[i],
                password=self.password,
            )
            self.users.append(user)
            UserPicture.objects.create(picture_path=(i % 2), user=user)
            i += 1
        # Create one post to put likes on it.
        self.post = Post.objects.create(
            title='Post For Likes',
            text='No one can move on without pressing the like button on this post :D.',
            owner=self.users[0],
        )
        # Put likes on the post using the class's users list
        i = 0
        while i < len_usernames:
            Like.objects.create(post=self.post, owner=self.users[i])
            i += 1

    def test_getting_liker_name(self):
        # Assert that getting the view without page argument will be ok
        response = self.client.get(
            reverse(
                'monotext:post_like_list', kwargs={'post_pk': self.post.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        # Assert that each page the view returns has the right data
        len_users = len(self.users)
        response = self.client.get(
            reverse(
                'monotext:post_like_list', kwargs={'post_pk': self.post.pk}
            )
            + '?page=1'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertTrue('likes' in json_resp)
        self.assertTrue('totalLikes' in json_resp)
        self.assertTrue('chunkSize' in json_resp)
        self.assertEqual(len(json_resp['likes']), json_resp['chunkSize'])
        self.assertTrue('ownerProfilePage' in json_resp['likes'][0])
        self.assertEqual(json_resp['totalLikes'], len_users)
        self.assertEqual(
            json_resp['likes'][0]['ownerName'],
            self.users[0].username,
        )
        self.assertEqual(
            json_resp['likes'][0]['ownerPic'],
            self.users[0].user_picture.picture_path,
        )
        self.assertEqual(
            json_resp['likes'][0]['ownerProfilePage'],
            reverse(
                'monotext:profile', kwargs={'username': self.users[0].username}
            ),
        )
        self.assertEqual(
            naturaltime(json_resp['likes'][0]['createdAt']),
            naturaltime(
                self.users[0]
                .liked_posts.through.objects.filter(
                    post=self.post, owner=self.users[0]
                )
                .select_related()[0]
                .created_at
            ),
        )
