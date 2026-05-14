from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.views import UserViewSet
from provetrina import views as prof_views

router = DefaultRouter()
router = DefaultRouter()
router.register(r'accounts', UserViewSet)
router.register(r'provetrina/profiles', prof_views.ProfileViewSet, 'profile')
router.register(r'provetrina/projects', prof_views.ProjectViewSet, 'project')
router.register(r'provetrina/courses', prof_views.CourseViewSet, 'course')
router.register(r'provetrina/skills', prof_views.SkillViewSet, 'skill')
router.register(r'provetrina/links', prof_views.LinkViewSet, 'link')
router.register(r'provetrina/works', prof_views.WorkExperienceViewSet, 'work')
router.register(
    r'provetrina/educations', prof_views.EducationViewSet, 'education'
)

api_urls = [
    path('', include(router.urls)),
    path('docs/', include('main.docs.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


urlpatterns = [
    path('', TemplateView.as_view(template_name='main/index.html')),
    path('auth/', include('rest_framework.urls')),
    path('api/', include(api_urls)),
    path('admin/', admin.site.urls),
]
