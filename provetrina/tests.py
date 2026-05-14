import random

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone as tz
from rest_framework import status
from rest_framework.test import APITestCase

from . import models


class TestProfileModel(TestCase):
    user: models.User

    def setUp(self):
        self.user = models.User.objects.create_user(username='superman')

    def test_profile_str_repr(self):
        name = 'Superman'
        profile = models.Profile(owner=self.user, name=name)
        assert str(profile) == 'Superman'


class TestProfiles(APITestCase):
    url = reverse('profile-list')
    user: models.User

    def setUp(self):
        self.user = models.User.objects.create_user(
            username='test_user', password='123$Test'
        )

    def authenticate(self, user: models.User | None = None):
        auth_user = user or self.user
        self.client.force_authenticate(user=auth_user)  # type: ignore
        return auth_user

    def test_profile_created(self):
        self.authenticate()
        data = {'name': 'Test Profile'}
        response = self.client.post(self.url, data)
        self.assertEqual(models.Profile.objects.count(), 1)
        self.assertContains(
            response, f'"id":{self.user.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(
            models.Profile.objects.get(owner=self.user).name, data['name']
        )

    def test_profile_not_created_without_authentication(self):
        data = {'name': 'Test Profile'}
        response = self.client.post(self.url, data)
        self.assertEqual(models.Profile.objects.count(), 0)
        self.assertContains(
            response, '"detail":', 1, status.HTTP_401_UNAUTHORIZED
        )

    def test_profile_not_created_twice(self):
        user = self.authenticate()
        models.Profile.objects.create(owner=user, name='Superman')
        data = {'name': 'Test Profile'}
        response = self.client.post(self.url, data)
        self.assertEqual(models.Profile.objects.count(), 1)
        self.assertContains(
            response, 'already exists', 1, status.HTTP_400_BAD_REQUEST
        )

    def test_public_profiles_listed(self):
        name = 'Test Profile'
        owner = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        profile = models.Profile.objects.create(
            owner=owner, name=name, public=True
        )
        for authenticated in [False, True]:
            with self.subTest(authenticated=authenticated):
                if authenticated:
                    self.authenticate()
                response = self.client.get(self.url)
                code = status.HTTP_200_OK
                self.assertContains(
                    response, '"previous":null', status_code=code
                )
                self.assertContains(response, '"results":[', status_code=code)
                self.assertContains(response, '"next":null', status_code=code)
                self.assertContains(response, '"count":1', status_code=code)
                self.assertContains(
                    response, f'"id":{profile.pk}', status_code=code
                )
                self.assertContains(
                    response, f'"name":"{name}"', status_code=code
                )
                self.assertContains(
                    response,
                    f'"username":"{owner.username}"',
                    status_code=code,
                )

    def test_private_profiles_not_listed(self):
        name = 'Test Profile'
        owner = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        models.Profile.objects.create(owner=owner, name=name, public=False)
        for authenticated in [False, True]:
            with self.subTest(authenticated=authenticated):
                if authenticated:
                    self.authenticate()
                response = self.client.get(self.url)
                code = status.HTTP_200_OK
                self.assertContains(
                    response, '"previous":null', status_code=code
                )
                self.assertContains(response, '"results":[]', status_code=code)
                self.assertContains(response, '"next":null', status_code=code)
                self.assertContains(response, '"count":0', status_code=code)

    def test_private_profile_not_listed_to_owner(self):
        name = 'Test Profile'
        owner = self.user
        models.Profile.objects.create(owner=owner, name=name, public=False)
        self.authenticate()
        response = self.client.get(self.url)
        code = status.HTTP_200_OK
        self.assertContains(response, '"previous":null', status_code=code)
        self.assertContains(response, '"results":[]', status_code=code)
        self.assertContains(response, '"next":null', status_code=code)
        self.assertContains(response, '"count":0', status_code=code)

    def test_public_profile_retrieved(self):
        name = 'Test Profile'
        owner = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        profile = models.Profile.objects.create(
            owner=owner, name=name, public=True
        )
        for user in [None, self.user, owner]:
            with self.subTest(authenticated=user):
                if user:
                    self.authenticate(user)
                for url in [
                    f'{self.url}{profile.pk}/',
                    f'{self.url}{owner.username}/',
                ]:
                    with self.subTest(url=url):
                        response = self.client.get(url)
                        code = status.HTTP_200_OK
                        self.assertContains(
                            response, f'"name":"{name}"', status_code=code
                        )
                        self.assertContains(
                            response, f'"id":{profile.pk}', status_code=code
                        )
                        self.assertContains(
                            response,
                            f'"username":"{owner.username}"',
                            status_code=code,
                        )

    def test_non_exist_profile_not_retrieved(self):
        user = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        for url in [f'{self.url}{777}/', f'{self.url}{user.username}/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND
                )

    def test_private_profile_not_retrieved_by_non_owner(self):
        name = 'Test Profile'
        owner = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        profile = models.Profile.objects.create(
            owner=owner, name=name, public=False
        )
        for user in [None, self.user, owner]:
            with self.subTest(authenticated=user):
                if user:
                    self.authenticate(user)
                for url in [
                    f'{self.url}{profile.pk}/',
                    f'{self.url}{owner.username}/',
                ]:
                    with self.subTest(url=url):
                        response = self.client.get(url)
                        if user is owner:
                            code = status.HTTP_200_OK
                            self.assertContains(
                                response, f'"name":"{name}"', status_code=code
                            )
                            self.assertContains(
                                response,
                                f'"username":"{owner.username}"',
                                status_code=code,
                            )
                            self.assertContains(
                                response,
                                f'"id":{profile.pk}',
                                status_code=code,
                            )
                        else:
                            self.assertEqual(
                                response.status_code, status.HTTP_404_NOT_FOUND
                            )

    def test_profile_updated(self):
        profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )
        self.authenticate()
        data = {'public': not profile.public}
        response = self.client.patch(f'{self.url}{profile.pk}/', data)
        profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.public, data['public'])

    def test_profile_not_updated_by_anonymous(self):
        profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )
        data = {'public': not profile.public}
        response = self.client.patch(f'{self.url}{profile.pk}/', data)
        profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(profile.public, data['public'])

    def test_profile_not_updated_by_non_owner(self):
        owner = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        profile = models.Profile.objects.create(
            owner=owner, name='Test Profile'
        )
        data = {'public': not profile.public}
        self.authenticate()
        response = self.client.patch(f'{self.url}{profile.pk}/', data)
        profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(profile.public, data['public'])

    def test_profile_deleted(self):
        profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )
        self.authenticate()
        response = self.client.delete(f'{self.url}{profile.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.Profile.objects.count(), 0)

    def test_profile_not_deleted_by_anonymous(self):
        profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )
        response = self.client.delete(f'{self.url}{profile.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(models.Profile.objects.count(), 1)

    def test_profile_not_deleted_by_non_owner(self):
        owner = models.User.objects.create_user(
            username='x', password='123@Xyz'
        )
        profile = models.Profile.objects.create(
            owner=owner, name='Test Profile'
        )
        self.authenticate()
        response = self.client.delete(f'{self.url}{profile.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(models.Profile.objects.count(), 1)


class Section:
    def __init__(
        self,
        model: type[models.AbstractSection],
        name: str,
        basename: str,
        data_list: list[dict],
    ):
        self.url = reverse(basename + '-list')
        self.data_list = data_list
        self.basename = basename
        self.model = model
        self.name = name

    def create_instance(self, profile: models.Profile, data: dict):
        return self.model.objects.create(profile=profile, **data)

    def __repr__(self):
        return '{"name": "' + self.name + '"}'

    def __str__(self):
        return self.name.capitalize() + ' Section'


class TestSections(APITestCase):
    now = tz.now()
    dates = {'start_date': now}
    sections = [
        Section(
            models.Education,
            'educations',
            'education',
            [
                {**dates, 'title': 'E1', 'order': 1},
                {**dates, 'title': 'E2', 'order': 2},
                {**dates, 'title': 'E3', 'order': 3},
            ],
        ),
        Section(
            models.WorkExperience,
            'works',
            'work',
            [
                {**dates, 'company': 'C1', 'position': 'P1', 'order': 1},
                {**dates, 'company': 'C2', 'position': 'P2', 'order': 2},
                {**dates, 'company': 'C3', 'position': 'P3', 'order': 3},
            ],
        ),
        Section(
            models.Project,
            'projects',
            'project',
            [
                {**dates, 'title': 'P1', 'order': 1},
                {**dates, 'title': 'P2', 'order': 2},
                {**dates, 'title': 'P3', 'order': 3},
            ],
        ),
        Section(
            models.Course,
            'courses',
            'course',
            [
                {**dates, 'name': 'C1', 'academy': 'A1', 'order': 1},
                {**dates, 'name': 'C2', 'academy': 'A2', 'order': 2},
                {**dates, 'name': 'C3', 'academy': 'A3', 'order': 3},
            ],
        ),
        Section(
            models.Skill,
            'skills',
            'skill',
            [
                {'name': 'S1', 'order': 1},
                {'name': 'S2', 'order': 2},
                {'name': 'S3', 'order': 3},
            ],
        ),
        Section(
            models.Link,
            'links',
            'link',
            [
                {'href': 'http://example.com/', 'order': 1},
                {'href': 'http://example.com/', 'order': 2},
                {'href': 'http://example.com/', 'order': 3},
            ],
        ),
    ]

    user: models.User
    profile: models.Profile

    def setUp(self):
        self.user = models.User.objects.create_user(
            username='test_user', password='123$Test'
        )
        self.profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )

    def authenticate(self, user: models.User | None = None):
        auth_user = user or self.user
        self.client.force_authenticate(user=auth_user)  # type: ignore
        return auth_user

    def deauthenticate(self):
        self.client.force_authenticate(user=None)  # type: ignore

    def create_user_profile_pair(self, public=True):
        user: models.User | None = None
        while user is None:
            username = f'x_{random.randint(1, 1000)}{random.randint(1, 1000)}'
            try:
                user = models.User.objects.create_user(
                    username=username, password=username
                )
            except IntegrityError:
                pass
        name = user.username.capitalize().replace('_', ' #')
        profile = models.Profile.objects.create(
            owner=user, name=name, public=public
        )
        return (user, profile)

    def test_created(self):
        self.authenticate()
        for section in self.sections:
            with self.subTest(section=section):
                response = self.client.post(section.url, section.data_list[0])
                self.assertContains(
                    response,
                    f'"profile":{self.user.pk}',
                    1,
                    status.HTTP_201_CREATED,
                )
                self.assertEqual(section.model.objects.count(), 1)

    def test_section_not_created_without_authentication(self):
        for section in self.sections:
            with self.subTest(section=section):
                response = self.client.post(section.url, section.data_list[0])
                self.assertContains(
                    response, '"detail":', 1, status.HTTP_401_UNAUTHORIZED
                )
                self.assertEqual(section.model.objects.count(), 0)

    def test_section_not_created_without_profile(self):
        user2 = models.User.objects.create_user(username='x', password='12@Xy')
        self.authenticate(user2)
        for section in self.sections:
            with self.subTest(section=section):
                response = self.client.post(section.url, section.data_list[0])
                self.assertContains(
                    response,
                    'Profile is missing',
                    1,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertEqual(section.model.objects.count(), 0)

    def test_section_listed(self):
        for section in self.sections:
            with self.subTest(section=section):
                user2, profile2 = self.create_user_profile_pair()
                instances = [
                    section.create_instance(self.profile, section.data_list[0])
                ] + [
                    section.create_instance(profile2, data)
                    for data in section.data_list[1:]
                ]
                query = f'profile_id={profile2.pk}'
                for user in [None, self.user, user2]:
                    with self.subTest(user=user):
                        if user:
                            self.authenticate(user)
                        response = self.client.get(
                            section.url, QUERY_STRING=query
                        )
                        self.assertEqual(
                            response.status_code, status.HTTP_200_OK
                        )
                        self.assertContains(response, '"previous":null')
                        self.assertContains(response, '"results":[')
                        self.assertContains(response, '"next":null')
                        self.assertContains(response, '"count":2')
                        for instance in instances[1:]:
                            self.assertContains(
                                response, f'"id":{instance.pk}'
                            )

    def test_private_profile_projects_not_listed(self):
        for section in self.sections:
            with self.subTest(section=section):
                user2, profile2 = self.create_user_profile_pair(public=False)
                instances = [
                    section.create_instance(self.profile, section.data_list[0])
                ] + [
                    section.create_instance(profile2, data)
                    for data in section.data_list[1:]
                ]
                query = f'profile_id={profile2.pk}'
                for user in [None, self.user, user2]:
                    with self.subTest(user=user):
                        if user:
                            self.authenticate(user)
                        response = self.client.get(
                            section.url, QUERY_STRING=query
                        )
                        self.assertEqual(
                            response.status_code, status.HTTP_200_OK
                        )
                        self.assertContains(response, '"previous":null')
                        self.assertContains(response, '"next":null')
                        if user is user2:
                            self.assertContains(response, '"results":[')
                            self.assertContains(response, '"count":2')
                            for instance in instances[1:]:
                                self.assertContains(
                                    response, f'"id":{instance.pk}'
                                )
                        else:
                            self.assertContains(response, '"results":[]')
                            self.assertContains(response, '"count":0')

    def test_public_profile_section_retrieved(self):
        for section in self.sections:
            with self.subTest(section=section):
                user2, profile2 = self.create_user_profile_pair()
                instance = section.create_instance(
                    profile2, section.data_list[0]
                )
                query = f'profile_id={profile2.pk}'
                for user in [None, self.user, user2]:
                    with self.subTest(authenticated=user):
                        if user:
                            self.authenticate(user)
                        response = self.client.get(
                            f'{section.url}{instance.pk}/', QUERY_STRING=query
                        )
                        code = status.HTTP_200_OK
                        self.assertContains(
                            response, f'"id":{instance.pk}', status_code=code
                        )

    def test_private_profile_section_not_retrieved_by_non_owner(self):
        for section in self.sections:
            with self.subTest(section=section):
                user2, profile2 = self.create_user_profile_pair(public=False)
                instance = section.create_instance(
                    profile2, section.data_list[0]
                )
                query = f'profile_id={profile2.pk}'
                for user in [None, self.user, user2]:
                    with self.subTest(user=user):
                        if user:
                            self.authenticate(user)
                        response = self.client.get(
                            f'{section.url}{instance.pk}/', QUERY_STRING=query
                        )
                        if user is user2:
                            code = status.HTTP_200_OK
                            self.assertContains(
                                response,
                                f'"id":{instance.pk}',
                                status_code=code,
                            )
                        else:
                            self.assertEqual(
                                response.status_code, status.HTTP_404_NOT_FOUND
                            )

    def test_section_updated_by_owner_only(self):
        for section in self.sections:
            with self.subTest(section=section):
                user2, profile2 = self.create_user_profile_pair()
                instance = section.create_instance(
                    profile2, section.data_list[0]
                )
                query = f'profile_id={profile2.pk}'
                for user in [None, self.user, user2]:
                    if user:
                        self.authenticate(user)
                    with self.subTest(user=user):
                        response = self.client.patch(
                            f'{section.url}{instance.pk}/',
                            section.data_list[1],
                            QUERY_STRING=query,
                        )
                        instance.refresh_from_db()
                        if user is user2:
                            self.assertEqual(
                                response.status_code, status.HTTP_200_OK
                            )
                        else:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_403_FORBIDDEN
                                if user
                                else status.HTTP_401_UNAUTHORIZED,
                            )
                    self.deauthenticate()

    def test_section_deleted(self):
        for section in self.sections:
            with self.subTest(section=section):
                instance = section.create_instance(
                    self.profile, section.data_list[0]
                )
                self.authenticate()
                query = f'profile_id={self.profile.pk}'
                response = self.client.delete(
                    f'{section.url}{instance.pk}/', QUERY_STRING=query
                )
                self.assertEqual(
                    response.status_code, status.HTTP_204_NO_CONTENT
                )
                self.assertEqual(section.model.objects.count(), 0)

    def test_section_not_deleted_by_anonymous(self):
        for section in self.sections:
            with self.subTest(section=section):
                instance = section.create_instance(
                    self.profile, section.data_list[0]
                )
                query = f'profile_id={self.profile.pk}'
                response = self.client.delete(
                    f'{section.url}{instance.pk}/', QUERY_STRING=query
                )
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )
                self.assertEqual(section.model.objects.count(), 1)

    def test_section_not_deleted_by_non_owner(self):
        for section in self.sections:
            with self.subTest(section=section):
                non_owner, _ = self.create_user_profile_pair()
                instance = section.create_instance(
                    self.profile, section.data_list[0]
                )
            self.authenticate(non_owner)
            query = f'profile_id={self.profile.pk}'
            response = self.client.delete(
                f'{section.url}{instance.pk}/', QUERY_STRING=query
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(section.model.objects.count(), 1)

    def test_section_action_not_performed_without_profile_id(self):
        for section in self.sections:
            with self.subTest(section=section):
                instance = section.create_instance(
                    self.profile, section.data_list[0]
                )
                url = f'{section.url}{instance.pk}/'
                data = {'end_date': self.now}
                self.authenticate()
                for method in ['get', 'put', 'patch', 'delete']:
                    with self.subTest(method=method):
                        response = getattr(self.client, method)(url, data)
                        instance.refresh_from_db()
                        self.assertEqual(
                            response.status_code, status.HTTP_404_NOT_FOUND
                        )

    def test_section_reordered(self):
        self.authenticate()
        for section in self.sections:
            instances = [
                section.create_instance(self.profile, section_data)
                for section_data in section.data_list
            ]
            request_data = {
                'ordered_ids': [
                    instance.pk for instance in reversed(instances)
                ]
            }
            with self.subTest(section=section):
                response = self.client.post(
                    f'{section.url}reorder/', request_data
                )
                for instance in instances:
                    instance.refresh_from_db()
                sorted_instances = sorted(instances, key=lambda i: i.order)
                ordered_ids = [srt_inst.pk for srt_inst in sorted_instances]
                self.assertEqual(request_data['ordered_ids'], ordered_ids)
                self.assertEqual(
                    response.status_code, status.HTTP_204_NO_CONTENT
                )

    def test_section_reordered_with_non_exits_ids(self):
        self.authenticate()
        data = {'ordered_ids': [7]}
        for section in self.sections:
            with self.subTest(section=section):
                response = self.client.post(f'{section.url}reorder/', data)
                self.assertEqual(
                    response.status_code, status.HTTP_204_NO_CONTENT
                )

    def test_section_not_reordered_without_profile(self):
        self.authenticate(
            models.User.objects.create_user(
                username='anonymous', password='123$anon'
            )
        )
        data = {'ordered_ids': [1]}
        for section in self.sections:
            with self.subTest(section=section):
                response = self.client.post(f'{section.url}reorder/', data)
                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND
                )

    def test_section_not_reordered_without_correct_data(self):
        self.authenticate()
        data_list = [None, [1], {}, {'ordered_ids': []}]
        for section in self.sections:
            for data in data_list:
                with self.subTest(section=section, data=data):
                    response = self.client.post(f'{section.url}reorder/', data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST
                    )

    def test_section_reorder_not_performed_without_authentication(self):
        for section in self.sections:
            with self.subTest(section=section):
                response = self.client.post(f'{section.url}reorder/', [])
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )


class TestProjects(APITestCase):
    now = tz.now()
    url = reverse('project-list')
    model = models.Project
    data = {'title': 'Test Project', 'order': 1, 'start_date': now}

    user: models.User
    profile: models.Profile

    def setUp(self):
        self.user = models.User.objects.create_user(
            username='test_user', password='123$Test'
        )
        self.profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )

    def authenticate(self, user: models.User | None = None):
        auth_user = user or self.user
        self.client.force_authenticate(user=auth_user)  # type: ignore
        return auth_user

    def test_project_created_twice_for_other_profile(self):
        user2 = models.User.objects.create_user(username='x', password='12@Xy')
        models.Profile.objects.create(owner=user2, name='X')
        self.authenticate()
        response = self.client.post(self.url, self.data)

        self.assertContains(
            response, f'"profile":{self.user.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(self.model.objects.count(), 1)
        self.authenticate(user2)
        response = self.client.post(self.url, self.data)
        self.assertContains(
            response, f'"profile":{user2.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(self.model.objects.count(), 2)

    def test_project_not_created_twice_for_same_profile(self):
        self.authenticate()
        response = self.client.post(self.url, self.data)

        self.assertContains(
            response, f'"profile":{self.user.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(self.model.objects.count(), 1)
        response = self.client.post(self.url, self.data)
        self.assertContains(
            response, 'already exists', 1, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(self.model.objects.count(), 1)

    def test_project_link(self):
        self.authenticate()
        project_data = {'profile': self.profile, **self.data}
        project = self.model.objects.create(**project_data)
        url = reverse('link-list')
        data = {'project': project.pk, 'href': 'http://foo.bar', 'order': 1}
        link_response = self.client.post(url, data)
        query = f'profile_id={self.profile.pk}'
        projects_response = self.client.get(self.url, QUERY_STRING=query)
        project_url = f'{self.url}{project.pk}/'
        project_response = self.client.get(project_url, QUERY_STRING=query)
        self.assertEqual(link_response.status_code, status.HTTP_201_CREATED)
        for res in [projects_response, project_response]:
            self.assertContains(
                res, f'"href":"{data["href"]}"', 1, status.HTTP_200_OK
            )


class TestWorkExperiences(APITestCase):
    now = tz.now()
    url = reverse('work-list')
    model = models.WorkExperience
    data = {'company': 'C1', 'position': 'P1', 'order': 1, 'start_date': now}

    user: models.User
    profile: models.Profile

    def setUp(self):
        self.user = models.User.objects.create_user(
            username='test_user', password='123$Test'
        )
        self.profile = models.Profile.objects.create(
            owner=self.user, name='Test Profile'
        )

    def authenticate(self, user: models.User | None = None):
        auth_user = user or self.user
        self.client.force_authenticate(user=auth_user)  # type: ignore
        return auth_user

    def test_work_experience_created_twice_for_other_profile(self):
        user2 = models.User.objects.create_user(username='x', password='12@Xy')
        models.Profile.objects.create(owner=user2, name='X')
        self.authenticate()
        response = self.client.post(self.url, self.data)

        self.assertContains(
            response, f'"profile":{self.user.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(self.model.objects.count(), 1)
        self.authenticate(user2)
        response = self.client.post(self.url, self.data)
        self.assertContains(
            response, f'"profile":{user2.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(self.model.objects.count(), 2)

    def test_work_experience_not_created_twice_for_same_profile(self):
        self.authenticate()
        response = self.client.post(self.url, self.data)

        self.assertContains(
            response, f'"profile":{self.user.pk}', 1, status.HTTP_201_CREATED
        )
        self.assertEqual(self.model.objects.count(), 1)
        response = self.client.post(self.url, self.data)
        self.assertContains(
            response, 'already exists', 1, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(self.model.objects.count(), 1)
