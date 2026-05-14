from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from provetrina.accounts.models import User
from provetrina.accounts.permissions import IsOwnerOrAdminUserReadOnly
from provetrina.accounts.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('username').all()
    serializer_class = UserSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            return permission_classes
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [
                IsAuthenticated,
                IsOwnerOrAdminUserReadOnly,
            ]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response(
            {'detail': 'Authentication credentials were not provided.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
