from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.routes import router as accounts_router
from provetrina.routes import router as provetrina_router

router = DefaultRouter()
router.registry.extend(accounts_router.registry)
router.registry.extend(provetrina_router.registry)

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
    path('monotext/', include('monotext.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
