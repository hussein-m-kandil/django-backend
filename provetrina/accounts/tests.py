from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from provetrina.accounts.models import User


class TestUserModel(TestCase):
    def test_user_str_repr(self):
        username = 'test_user'
        user = User(username=username)
        self.assertEqual(str(user), '@' + username)


class TestAccountsListAction(APITestCase):
    url = reverse('user-list')

    def authenticate(self, superuser: bool):
        data = {'username': 'test_user', 'password': '123$Test', 'email': ''}
        user = (
            User.objects.create_superuser(**data)
            if superuser
            else User.objects.create_user(**data)
        )
        self.client.force_authenticate(user=user)  # type: ignore
        return user

    def test_accounts_listed_to_admin_user(self):
        self.authenticate(superuser=True)
        response = self.client.get(self.url)
        code = status.HTTP_200_OK
        self.assertContains(response, '"previous":', status_code=code)
        self.assertContains(response, '"results":', status_code=code)
        self.assertContains(response, '"next":', status_code=code)

    def test_account_not_listed_to_non_admin_user(self):
        self.authenticate(superuser=False)
        response = self.client.get(self.url)
        code = status.HTTP_403_FORBIDDEN
        self.assertContains(response, '"detail":', status_code=code)
        self.assertNotContains(response, '"previous":', status_code=code)
        self.assertNotContains(response, '"results":', status_code=code)
        self.assertNotContains(response, '"next":', status_code=code)

    def test_account_not_listed_to_anonymous_user(self):
        response = self.client.get(self.url)
        code = status.HTTP_401_UNAUTHORIZED
        self.assertContains(response, '"detail":', status_code=code)
        self.assertNotContains(response, '"previous":', status_code=code)
        self.assertNotContains(response, '"results":', status_code=code)
        self.assertNotContains(response, '"next":', status_code=code)


class TestAccountsRetrieveAction(APITestCase):
    base_url = reverse('user-list')
    user: User

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', password='123$Test'
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        return self.user

    def test_account_retrieved(self):
        user = self.authenticate()
        url1 = self.base_url + str(self.user.pk) + '/'
        url2 = self.base_url + 'me/'
        for url in [url1, url2]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, user.pk, 1)

    def test_account_not_retrieved_without_authentication(self):
        url1 = self.base_url + str(self.user.pk) + '/'
        url2 = self.base_url + 'me/'
        for url in [url1, url2]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )

    def test_account_not_retrieved_with_non_owner_authentication(self):
        non_owners = [
            User.objects.create_user(
                username='test_user_2', password='123@Test2'
            ),
            User.objects.create_superuser(
                username='test_user_3', password='123@Test3', email=''
            ),
        ]
        url = self.base_url + str(self.user.pk) + '/'
        for user in non_owners:
            self.client.force_authenticate(user=user)  # type: ignore
            with self.subTest(user=user):
                response = self.client.get(url)
                if user.is_staff:
                    self.assertContains(response, self.user.pk, 1)
                else:
                    self.assertEqual(
                        response.status_code, status.HTTP_403_FORBIDDEN
                    )


class TestAccountsCreateAction(APITestCase):
    url = reverse('user-list')
    data = {
        'username': 'test_user',
        'password': '123$Test',
        'password_confirmation': '123$Test',
    }

    def test_account_created(self):
        response = self.client.post(self.url, self.data)
        user = User.objects.get()
        self.assertContains(
            response, self.data['username'], 1, status.HTTP_201_CREATED
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, self.data['username'])
        self.assertGreater(len(user.password), len(self.data['password']))
        self.assertFalse(user.is_staff)

    def test_account_not_created_with_existing_username(self):
        User.objects.create_user(
            username=self.data['username'], password=self.data['password']
        )
        response = self.client.post(self.url, self.data)
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, '"username":', 1, status.HTTP_400_BAD_REQUEST
        )

    def test_account_not_created_without_required_field(self):
        required_fields = ['username', 'password', 'password_confirmation']
        for field in required_fields:
            data = self.data.copy()
            del data[field]
            response = self.client.post(self.url, data)
            with self.subTest(response=response):
                self.assertEqual(User.objects.count(), 0)
                self.assertContains(
                    response, f'"{field}":', 1, status.HTTP_400_BAD_REQUEST
                )

    def test_account_not_created_with_password_confirmation_mismatch(self):
        data = {**self.data, 'password_confirmation': '123@mismatch'}
        response = self.client.post(self.url, data)
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(
            response,
            '"password_confirmation":',
            1,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_account_not_created_with_weak_password(self):
        data = {
            **self.data,
            'password': 'weak',
            'password_confirmation': 'weak',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(
            response, '"password":', 1, status.HTTP_400_BAD_REQUEST
        )


class TestAccountsUpdateAction(APITestCase):
    base_url = reverse('user-list')
    data: dict[str, str]
    user: User
    url: str

    @classmethod
    def setUpTestData(cls):
        cls.data = {
            'username': 'test_user_update',
            'password': '123$Update',
            'password_confirmation': '123$Update',
        }

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', password='123$Test'
        )
        self.url = self.base_url + str(self.user.pk) + '/'

    def authenticate(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        return self.user

    def assert_refreshed_user_untouched(self):
        original_user_dict = model_to_dict(self.user)
        self.user.refresh_from_db()
        self.assertDictEqual(model_to_dict(self.user), original_user_dict)

    def test_account_updated(self):
        user = self.authenticate()
        response = self.client.put(self.url, self.data)
        user.refresh_from_db()
        self.assertContains(
            response, self.data['username'], 1, status.HTTP_200_OK
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, self.data['username'])
        self.assertGreater(len(user.password), len(self.data['password']))
        self.assertFalse(user.is_staff)

    def test_admin_user_account_updated(self):
        admin_user = User.objects.create_superuser(
            username='test_admin', password='123$Admin', email=''
        )
        self.client.force_authenticate(user=admin_user)  # type: ignore
        url = self.base_url + str(admin_user.pk) + '/'
        response = self.client.put(url, self.data)
        admin_user.refresh_from_db()
        self.assertContains(
            response, self.data['username'], 1, status.HTTP_200_OK
        )
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(admin_user.username, self.data['username'])
        self.assertGreater(
            len(admin_user.password), len(self.data['password'])
        )
        self.assertTrue(admin_user.is_staff)

    def test_account_not_updated_without_authentication(self):
        response = self.client.put(self.url, self.data)
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, '"detail":', 1, status.HTTP_401_UNAUTHORIZED
        )

    def test_account_not_updated_with_non_owner_authentication(self):
        non_owners = [
            User.objects.create_user(
                username='test_user_2', password='123@Test2'
            ),
            User.objects.create_superuser(
                username='test_user_3', password='123@Test3', email=''
            ),
        ]
        user_count = User.objects.count()
        for user in non_owners:
            self.client.force_authenticate(user=user)  # type: ignore
            response = self.client.put(self.url, self.data)
            with self.subTest(response=response, user_count=user_count):
                self.assert_refreshed_user_untouched()
                self.assertEqual(User.objects.count(), user_count)
                self.assertContains(
                    response, '"detail":', 1, status.HTTP_403_FORBIDDEN
                )

    def test_account_not_updated_with_existing_username(self):
        username = 'test_user_2'
        User.objects.create_user(username=username, password='123@Test2')
        self.authenticate()
        response = self.client.put(
            self.url, {**self.data, 'username': username}
        )
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 2)
        self.assertContains(
            response, '"username":', 1, status.HTTP_400_BAD_REQUEST
        )

    def test_account_not_updated_without_required_field(self):
        required_fields = ['username', 'password', 'password_confirmation']
        self.authenticate()
        for field in required_fields:
            data = self.data.copy()
            del data[field]
            response = self.client.put(self.url, data)
            with self.subTest(response=response, field=field):
                self.assert_refreshed_user_untouched()
                self.assertEqual(User.objects.count(), 1)
                self.assertContains(
                    response, f'"{field}":', 1, status.HTTP_400_BAD_REQUEST
                )

    def test_account_not_updated_with_password_confirmation_mismatch(self):
        data = {**self.data, 'password_confirmation': '123@mismatch'}
        self.authenticate()
        response = self.client.put(self.url, data)
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response,
            '"password_confirmation":',
            1,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_account_not_updated_with_weak_password(self):
        data = {
            **self.data,
            'password': 'weak',
            'password_confirmation': 'weak',
        }
        self.authenticate()
        response = self.client.put(self.url, data)
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, '"password":', 1, status.HTTP_400_BAD_REQUEST
        )


class TestAccountsPartialUpdateAction(APITestCase):
    base_url = reverse('user-list')
    user: User
    url: str

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', password='123$Test'
        )
        self.url = self.base_url + str(self.user.pk) + '/'

    def authenticate(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        return self.user

    def assert_refreshed_user_untouched(self):
        original_user_dict = model_to_dict(self.user)
        self.user.refresh_from_db()
        self.assertDictEqual(model_to_dict(self.user), original_user_dict)

    def get_dummy_request_data(self):
        self.user.refresh_from_db()
        return {'username': self.user.username + '_X'}

    def test_account_updated(self):
        updates = [
            ['username', {'username': 'test_user_update'}],
            [
                'password',
                {
                    'password': '123$Update',
                    'password_confirmation': '123$Update',
                },
            ],
        ]
        user = self.authenticate()
        for [field, data] in updates:
            response = self.client.patch(self.url, data)
            user.refresh_from_db()
            with self.subTest(response=response, field=field, data=data):
                self.assertEqual(User.objects.count(), 1)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                if field == 'password':
                    self.assertGreater(len(user.password), len(data[field]))
                    self.assertTrue(getattr(user, field))
                else:
                    self.assertEqual(getattr(user, field), data[field])
                self.assertFalse(user.is_staff)

    def test_admin_user_account_updated(self):
        admin_user = User.objects.create_superuser(
            username='test_admin', password='123$Admin', email=''
        )
        field = 'username'
        data = {field: 'test_user_update'}
        url = self.base_url + str(admin_user.pk) + '/'
        self.client.force_authenticate(user=admin_user)  # type: ignore
        response = self.client.patch(url, data)
        admin_user.refresh_from_db()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(getattr(admin_user, field), data[field])
        self.assertTrue(admin_user.is_staff)

    def test_account_not_updated_without_authentication(self):
        data = self.get_dummy_request_data()
        response = self.client.patch(self.url, data)
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, '"detail":', 1, status.HTTP_401_UNAUTHORIZED
        )

    def test_account_not_updated_with_non_owner_authentication(self):
        data = self.get_dummy_request_data()
        non_owners = [
            User.objects.create_user(
                username='test_user_2', password='123@Test2'
            ),
            User.objects.create_superuser(
                username='test_user_3', password='123@Test3', email=''
            ),
        ]
        user_count = User.objects.count()
        for user in non_owners:
            self.client.force_authenticate(user=user)  # type: ignore
            response = self.client.patch(self.url, data)
            with self.subTest(response=response, user_count=user_count):
                self.assert_refreshed_user_untouched()
                self.assertEqual(User.objects.count(), user_count)
                self.assertContains(
                    response, '"detail":', 1, status.HTTP_403_FORBIDDEN
                )

    def test_account_not_updated_with_existing_username(self):
        username = 'test_user_2'
        User.objects.create_user(username=username, password='123@Test2')
        self.authenticate()
        response = self.client.patch(self.url, {'username': username})
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 2)
        self.assertContains(
            response, '"username":', 1, status.HTTP_400_BAD_REQUEST
        )

    def test_account_password_not_updated(self):
        self.authenticate()
        password_fields = [
            ['password', {'password_confirmation': '123$TestUpdate'}],
            ['password_confirmation', {'password': '123$TestUpdate'}],
        ]
        for [field, data] in password_fields:
            response = self.client.patch(self.url, data)
            with self.subTest(response=response, field=field):
                self.assert_refreshed_user_untouched()
                self.assertEqual(User.objects.count(), 1)
                self.assertContains(
                    response, f'"{field}":', 1, status.HTTP_400_BAD_REQUEST
                )

    def test_account_not_updated_with_password_confirmation_mismatch(self):
        self.authenticate()
        data = {
            'password': '123$TestUpdate',
            'password_confirmation': '123@mismatch',
        }
        response = self.client.patch(self.url, data)
        field = 'password_confirmation'
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, f'"{field}":', 1, status.HTTP_400_BAD_REQUEST
        )

    def test_account_not_updated_with_weak_password(self):
        data = {'password': 'weak', 'password_confirmation': 'weak'}
        self.authenticate()
        response = self.client.patch(self.url, data)
        self.assert_refreshed_user_untouched()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, '"password":', 1, status.HTTP_400_BAD_REQUEST
        )


class TestAccountsDeleteAction(APITestCase):
    base_url = reverse('user-list')
    user: User
    url: str

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', password='123$Test'
        )
        self.url = self.base_url + str(self.user.pk) + '/'

    def authenticate(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        return self.user

    def test_account_deleted(self):
        user = self.authenticate()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(User.DoesNotExist, user.refresh_from_db)
        self.assertEqual(User.objects.count(), 0)

    def test_admin_user_account_deleted(self):
        admin_user = User.objects.create_superuser(
            username='test_admin', password='123$Admin', email=''
        )
        url = self.base_url + str(admin_user.pk) + '/'
        self.client.force_authenticate(user=admin_user)  # type: ignore
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(User.DoesNotExist, admin_user.refresh_from_db)
        self.assertEqual(User.objects.count(), 1)

    def test_account_not_deleted_without_authentication(self):
        response = self.client.delete(self.url)
        self.user.refresh_from_db()
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response, '"detail":', 1, status.HTTP_401_UNAUTHORIZED
        )

    def test_account_not_deleted_with_non_owner_authentication(self):
        non_owners = [
            User.objects.create_user(
                username='test_user_2', password='123@Test2'
            ),
            User.objects.create_superuser(
                username='test_user_3', password='123@Test3', email=''
            ),
        ]
        user_count = User.objects.count()
        for user in non_owners:
            self.client.force_authenticate(user=user)  # type: ignore
            response = self.client.delete(self.url)
            with self.subTest(response=response, user_count=user_count):
                self.user.refresh_from_db()
                self.assertEqual(User.objects.count(), user_count)
                self.assertContains(
                    response, '"detail":', 1, status.HTTP_403_FORBIDDEN
                )
