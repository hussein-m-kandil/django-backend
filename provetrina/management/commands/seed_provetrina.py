from django.core.management.base import BaseCommand
from django.utils import timezone as tz
from faker import Faker

from provetrina.models import (
    Course,
    Education,
    Link,
    Profile,
    Project,
    Skill,
    User,
    WorkExperience,
)

PROFILE_COUNT = 100

fake = Faker()


def fakeLocation():
    return f'{fake.city()}, {fake.country()}.'


def fakeDates(i: int):
    from_limit = f'{-5 - i}y'
    to_limit = f'{-1 - i}y'
    start_date = tz.make_aware(fake.date_time_between(from_limit, to_limit))
    end_date = tz.make_aware(fake.date_time_between(to_limit))
    return (
        start_date,
        end_date,
    )


class Command(BaseCommand):
    help = 'Seeds the provetrina app with dummy profiles.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Provetrina', ending='')
        for n in range(PROFILE_COUNT):
            self.stdout.write('.', ending='' if n < PROFILE_COUNT - 1 else '\n')
            first_name = fake.unique.first_name()
            last_name = fake.unique.last_name()
            username = f'{first_name}_{last_name}'
            name = f'{first_name} {last_name}'
            email = f'{username}@example.ex'
            user = User.objects.create_user(username, email, fake.password())
            profile = Profile.objects.create(
                owner=user,
                name=name,
                email=email,
                title=fake.job(),
                location=fakeLocation(),
                tel=fake.unique.phone_number(),
                bio=' '.join(fake.sentences(fake.random_int(1, 5))),
            )
            for i in range(fake.random_int(1, 2)):
                start_date, end_date = fakeDates(i)
                Education.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    profile=profile,
                    order=i + 1,
                    title=fake.sentence(fake.random_int(2, 5))[:-1],
                    summary=' '.join(fake.sentences(fake.random_int(1, 3))),
                )
            for i in range(fake.random_int(1, 3)):
                start_date, end_date = fakeDates(i)
                WorkExperience.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    profile=profile,
                    order=i + 1,
                    position=fake.job(),
                    company=fake.company(),
                    location=f'{fake.city()}, {fake.country()}.',
                    summary=' '.join(fake.sentences(fake.random_int(1, 3))),
                )
            for i in range(fake.random_int(3, 7)):
                start_date, end_date = fakeDates(i)
                Project.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    profile=profile,
                    order=i + 1,
                    href=fake.url(),
                    title=fake.sentence(fake.random_int(2, 5))[:-1],
                    summary=' '.join(fake.sentences(fake.random_int(1, 3))),
                    keywords=','.join(fake.words(7)),
                )
            for i in range(fake.random_int(1, 3)):
                start_date, end_date = fakeDates(i)
                Course.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    profile=profile,
                    order=i + 1,
                    href=fake.url(),
                    name=fake.sentence(fake.random_int(2, 5))[:-1],
                    academy=fake.company(),
                )
            for i in range(fake.random_int(3, 7)):
                start_date, end_date = fakeDates(i)
                Skill.objects.create(
                    profile=profile,
                    order=i + 1,
                    name=fake.sentence(fake.random_int(1, 3))[:-1],
                    keywords=','.join(fake.words(7)),
                )
            for i in range(fake.random_int(2, 5)):
                start_date, end_date = fakeDates(i)
                Link.objects.create(
                    profile=profile,
                    order=i + 1,
                    href=fake.url(),
                    label=fake.sentence(fake.random_int(1, 3))[:-1],
                )
        self.stdout.write(
            self.style.SUCCESS(
                f'Provetrina successfully seeded with {PROFILE_COUNT} profile{"" if PROFILE_COUNT == 1 else "s"}.'
            )
        )
