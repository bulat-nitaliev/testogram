from general.api.serializers import (UserRegisterationSerializer, 
                                     UserListSerializer, 
                                     UserRetrieveSerializer, 
                                     PostCreateUpdateSerializer, 
                                     PostListSerializer, 
                                     PostRetrieveSerializer,
                                     CommentSerializer)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from general.models import User, Post, Comment
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(CreateModelMixin,ListModelMixin,RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]


    @action(detail=False, methods=["get"], url_path="me")
    def me(self,request:Request):
        isinstance = self.request.user
        serializer = self.get_serializer(isinstance)
        print(serializer)
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

    @action(detail=True, methods=["get"])
    def friends(self, request, pk=None):
        user = self.get_object()
        queryset = self.filter_queryset(
          self.get_queryset().filter(friends=user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serilizer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serilizer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related('friends').order_by("-id")
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_friend(self,request, pk=None):
        user = self.get_object()
        request.user.friends.add(user)

        return Response(f'Friend {user} added')
    
    @action(detail=True, methods=['post'])
    def remove_friend(self,request, pk=None):
        user = self.get_object()
        request.user.friends.remove(user)

        return Response(f'Friend {user} removed')


class PostViewSet(ModelViewSet):
    
    queryset = Post.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated,]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostRetrieveSerializer
        return PostCreateUpdateSerializer
    
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого поста.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого поста.")
        instance.delete()


class CommentsViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = Comment.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post__id']

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого комментария.")
        instance.delete()