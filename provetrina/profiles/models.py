from django.db import models

from provetrina.accounts.models import User


class Profile(models.Model):
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=150, default='', blank=True)
    location = models.CharField(max_length=255, default='', blank=True)
    metadata = models.CharField(max_length=511, default='', blank=True)
    theme = models.PositiveSmallIntegerField(default=0, blank=True)
    bio = models.CharField(max_length=511, default='', blank=True)
    tel = models.CharField(max_length=50, default='', blank=True)
    public = models.BooleanField(default=True, blank=True)
    email = models.EmailField(default='', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        default_related_name = 'profile'
        ordering = ['name']


class AbstractSection(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True
        ordering = ['order']


class AbstractOrderedSection(AbstractSection):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta(AbstractSection.Meta):
        abstract = True


class Education(AbstractOrderedSection):
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.title

    class Meta(AbstractOrderedSection.Meta):
        default_related_name = 'educations'


class WorkExperience(AbstractOrderedSection):
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default='', blank=True)
    summary = models.CharField(max_length=511, default='', blank=True)

    def __str__(self):
        return self.position + ' at ' + self.company

    class Meta(AbstractOrderedSection.Meta):
        default_related_name = 'work_experiences'
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'company', 'position'],
                name='unique_profile_work_experience',
            )
        ]


class Project(AbstractOrderedSection):
    title = models.CharField(max_length=255)
    href = models.URLField(default='', blank=True)
    summary = models.CharField(max_length=511, default='', blank=True)
    keywords = models.CharField(max_length=511, default='', blank=True)

    def __str__(self):
        return self.title

    class Meta(AbstractOrderedSection.Meta):
        default_related_name = 'projects'
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'title'], name='unique_profile_project'
            )
        ]


class Course(AbstractOrderedSection):
    name = models.CharField(max_length=255)
    academy = models.CharField(max_length=255)
    href = models.URLField(default='', blank=True)

    def __str__(self):
        return self.name + ' from ' + self.academy

    class Meta(AbstractOrderedSection.Meta):
        default_related_name = 'courses'


class Skill(AbstractSection):
    name = models.CharField(max_length=255)
    keywords = models.CharField(max_length=511, default='', blank=True)

    def __str__(self):
        return self.name

    class Meta(AbstractSection.Meta):
        default_related_name = 'skills'


class Link(AbstractSection):
    href = models.URLField()
    label = models.CharField(max_length=255, default='', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.href

    class Meta(AbstractSection.Meta):
        default_related_name = 'links'
