from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from users.serializers import (ChangePasswordSerializers, UserSerializer,
                               UserSubscriptionsSerializer)
from users.models import UserFollow

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=('get',),
        detail=False,
        serializer_class=(UserSubscriptionsSerializer,)
    )
    def subscriptions(self, request):
        """Возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты."""
        user = request.user
        sub = user.objects.all()
        serializer = self.get_serializer(sub, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=(UserSubscriptionsSerializer,)
    )
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя или отписаться."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':

            if user == author:
                raise ValidationError('Нельзя подписаться на самого себя!')

            if UserFollow.objects.filter(
                user_id=user, following_user_id=author
            ).exists():
                return ValidationError('Подписка уже оформлена!')
            UserFollow.objects.create(
                user_id=user, following_user_id=author
            )
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not UserFollow.objects.filter(
                user_id=user, following_user_id=author
            ).exists():
                return ValidationError('Такой подписки не существует!!')
            sub = get_object_or_404(
                UserFollow,
                user_id=user,
                following_user_id=author
            )
            sub.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def me(self, request):
        """Возвращает текущего пользователя."""
        return Response(request.user, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=(ChangePasswordSerializers,)
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        # user = request.user
        # serializer = ChangePasswordSerializers(data=request.data)
        serializer = self.get_serializer(data=request.data)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
