import typing

from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from . import models, serializers
from .permissions import (
    IsProfileOwnerOrReadOnlyPublicProfile,
    IsSectionOwnerOrReadOnlyPublicProfile,
)
from .resume import Resume


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProfileSerializer

    def get_queryset(self):  # type: ignore
        user = self.request.user
        query = Q(public=True)
        if self.action != 'list':
            query = query | Q(owner_id=user.pk)
        search = self.request.query_params.get('q')  # type: ignore
        if search:
            filtration_query = (
                Q(name__icontains=search)
                | Q(title__icontains=search)
                | Q(owner__username__icontains=search)
            )
            query = query & filtration_query
        return (
            models.Profile.objects.select_related('owner')
            .filter(query)
            .order_by('name', 'owner__username', 'title')
        )

    def get_permissions(self):
        permission_classes = [IsProfileOwnerOrReadOnlyPublicProfile]
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self):  # type: ignore
        pk = self.kwargs.get('pk')
        if not pk:
            return super().get_object()
        filters = {'owner__username': pk}
        try:
            filters = {'pk': int(pk)}
        except ValueError:
            pass
        obj = get_object_or_404(self.get_queryset(), **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=['get'])
    def resume(self, request: Request, pk: int | str):
        profile = self.get_object()  # get profile and check permissions
        resume = Resume(profile)
        return FileResponse(
            resume.file, as_attachment=True, filename=resume.filename
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            required=True,
            name='profile_id',
            type=OpenApiTypes.INT,
            style=OpenApiParameter.QUERY,
        ),
    ]
)
class SectionBaseModelViewSet(viewsets.ModelViewSet):
    serializer_class: type[ModelSerializer]

    def get_permissions(self):
        permission_classes = [
            IsAuthenticated,
            IsSectionOwnerOrReadOnlyPublicProfile,
        ]
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsSectionOwnerOrReadOnlyPublicProfile]
        return [permission() for permission in permission_classes]

    def get_profile_id(self):
        try:
            return int(self.request.GET.get('profile_id', '-1'))
        except ValueError:
            return -1

    def get_queryset(self):
        user = self.request.user
        profile_id = self.get_profile_id()
        return (
            self.serializer_class.Meta.model.objects.select_related('profile')  #  type: ignore
            .filter(profile_id=profile_id)
            .filter(Q(profile_id=user.pk) | Q(profile__public=True))
            .order_by('order')
        )

    @action(detail=False, methods=['post'])
    def reorder(self, request: Request):
        serializer = serializers.ReorderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                profile = models.Profile.objects.get(owner=request.user)
            except models.Profile.DoesNotExist:
                return Response(
                    {'detail': 'Profile not found.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            with transaction.atomic():
                model = self.serializer_class.Meta.model  # type: ignore
                model = typing.cast(models.AbstractSection, model)
                model_objects = model.objects.filter(profile=profile)
                ordered_ids = typing.cast(dict, serializer.validated_data)[
                    'ordered_ids'
                ]
                ordered_entries = model_objects.filter(id__in=ordered_ids)
                not_ordered_entries = model_objects.exclude(id__in=ordered_ids)
                order = 0
                for i, id in enumerate(ordered_ids):
                    try:
                        entry = ordered_entries.get(id=id)
                        order = i + 1
                        entry.order = order
                        entry.save()
                    except model.DoesNotExist:
                        pass
                for entry in not_ordered_entries:
                    order += 1
                    entry.order = order
                    entry.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LinkViewSet(SectionBaseModelViewSet):
    serializer_class = serializers.LinkSerializer


class EducationViewSet(SectionBaseModelViewSet):
    serializer_class = serializers.EducationSerializer


class WorkExperienceViewSet(SectionBaseModelViewSet):
    serializer_class = serializers.WorkExperienceSerializer


class ProjectViewSet(SectionBaseModelViewSet):
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('links')


class CourseViewSet(SectionBaseModelViewSet):
    serializer_class = serializers.CourseSerializer


class SkillViewSet(SectionBaseModelViewSet):
    serializer_class = serializers.SkillSerializer
