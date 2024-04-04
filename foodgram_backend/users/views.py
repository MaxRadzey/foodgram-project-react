from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from users.models import UserFollow
from users.serializers import (ChangePasswordSerializers, UserCreateSerializer,
                               UserSerializer, UserSubscriptionsSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserSerializer

    @action(
        methods=('get',),
        detail=False,
        serializer_class=UserSubscriptionsSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Возвращает подписки. В выдачу добавляются рецепты."""
        users = User.objects.filter(followers__user_id=request.user)
        users = self.paginate_queryset(users)
        serializer = UserSubscriptionsSerializer(
            users, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя или отписаться."""

    @subscribe.mapping.post
    def subscribe_post(self, request, pk=None):
        """Подписаться на пользователя."""
        user = request.user
        author_id = self.kwargs.get('pk')
        author = get_object_or_404(User, id=author_id)

        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя!')

        if UserFollow.objects.filter(
            user_id=user, following_user_id=author
        ).exists():
            raise ValidationError('Подписка уже оформлена!')
        UserFollow.objects.create(
            user_id=user, following_user_id=author
        )
        serializer = UserSubscriptionsSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        """Отписаться от пользователя."""
        user = request.user
        author_id = self.kwargs.get('pk')
        author = get_object_or_404(User, id=author_id)

        if not UserFollow.objects.filter(
            user_id=user, following_user_id=author
        ).exists():
            raise ValidationError('Такой подписки не существует!!')
        sub = get_object_or_404(
            UserFollow,
            user_id=user,
            following_user_id=author
        )
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Возвращает текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=ChangePasswordSerializers,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        user = request.user
        serializer = ChangePasswordSerializers(data=request.data)
        if serializer.is_valid():
            if not user.check_password(
                serializer.data.get('current_password')
            ):
                raise ValidationError('Неверный пароль!')
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
