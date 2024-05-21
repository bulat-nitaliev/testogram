<<<<<<< HEAD
from testogram.testogram.general.api.serializers import UserRegisterationSerializer, UserListSerializer
=======
from general.api.serializer import UserRegisterationSerializer, UserListSerializer, UserRetrieveSerializer
>>>>>>> 142fcf6ac955ded93cf01852eeba3fae528df3e0
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from general.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(CreateModelMixin,ListModelMixin,RetrieveModelMixin, GenericViewSet):
  queryset = User.objects.all().order_by('-id')
  permission_classes = [IsAuthenticated]

  
  @action(detail=False, methods=["get"], url_path="me")
  def me(self,request):
    isinstance = self.request.user
    serializer = self.get_serializer(isinstance)
    return Response(serializer.data)

  def get_serializer_class(self):
    if self.action == 'create':
      return UserRegisterationSerializer
    if self.action in ['retrieve', 'me']:
      return UserRetrieveSerializer
    return UserListSerializer

  def get_permissions(self):
    if self.action == 'create':
      self.permission_classes = [AllowAny]
    return super().get_permissions()