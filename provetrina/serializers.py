from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from . import models


class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.BigIntegerField(read_only=True, source='owner_id')
    username = serializers.CharField(source='owner.username', read_only=True)

    def validate_owner(self, owner):
        if self.Meta.model.objects.filter(owner=owner).exists():
            raise ValidationError('Profile already exists.')
        return owner

    class Meta:
        model = models.Profile
        fields = '__all__'


class CurrentProfileIdDefault:
    """Assuming the current user's profile shares same user's primary key."""

    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.pk


class SectionBaseSerializer(serializers.ModelSerializer):
    profile_id = serializers.HiddenField(default=CurrentProfileIdDefault())

    def validate(self, attrs):
        profile_id = attrs.get('profile_id', '')
        if (
            profile_id
            and not models.Profile.objects.filter(owner_id=profile_id).exists()
        ):
            raise ValidationError('Profile is missing.')
        return super().validate(attrs)

    class Meta:
        fields = '__all__'
        extra_kwargs = {'profile': {'read_only': True}}


class LinkSerializer(SectionBaseSerializer):
    class Meta(SectionBaseSerializer.Meta):
        model = models.Link


class EducationSerializer(SectionBaseSerializer):
    class Meta(SectionBaseSerializer.Meta):
        model = models.Education


class WorkExperienceSerializer(SectionBaseSerializer):
    class Meta(SectionBaseSerializer.Meta):
        model = models.WorkExperience
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['profile_id', 'company', 'position'],
                message='Work-Experience already exists.',
            )
        ]


class ProjectSerializer(SectionBaseSerializer):
    links = LinkSerializer(read_only=True, many=True)

    class Meta(SectionBaseSerializer.Meta):
        model = models.Project
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['profile_id', 'title'],
                message='Project already exists.',
            )
        ]


class CourseSerializer(SectionBaseSerializer):
    class Meta(SectionBaseSerializer.Meta):
        model = models.Course


class SkillSerializer(SectionBaseSerializer):
    class Meta(SectionBaseSerializer.Meta):
        model = models.Skill


class ReorderSerializer(serializers.Serializer):
    ordered_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False
    )
