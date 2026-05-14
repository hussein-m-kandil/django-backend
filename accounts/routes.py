from rest_framework.routers import SimpleRouter

from . import views

base = 'accounts'

router = SimpleRouter()

router.register(rf'{base}', views.UserViewSet)
