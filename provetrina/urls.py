from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from provetrina.accounts.views import UserViewSet
from provetrina.profiles import views as prof_views

router = DefaultRouter()
router.register(r'accounts', UserViewSet)
router.register(r'profiles', prof_views.ProfileViewSet, 'profile')
router.register(r'projects', prof_views.ProjectViewSet, 'project')
router.register(r'courses', prof_views.CourseViewSet, 'course')
router.register(r'skills', prof_views.SkillViewSet, 'skill')
router.register(r'links', prof_views.LinkViewSet, 'link')
router.register(r'works', prof_views.WorkExperienceViewSet, 'work')
router.register(r'educations', prof_views.EducationViewSet, 'education')

api_urls = [
    path('', include(router.urls)),
    path('docs/', include('provetrina.docs.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


urlpatterns = [
    path('', TemplateView.as_view(template_name='provetrina/index.html')),
    path('auth/', include('rest_framework.urls')),
    path('api/', include(api_urls)),
    path('admin/', admin.site.urls),
]
