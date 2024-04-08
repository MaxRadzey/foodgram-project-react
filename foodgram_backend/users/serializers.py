from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.serializers import RecipeForUserSerializer
from users.constants import EMAIL_MAX_LENGTH, USER_MAX_LENGTH

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(
                EMAIL_MAX_LENGTH,
                message='Длина почты не должна превышать 254 символов.'
            ),
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(
                USER_MAX_LENGTH,
                message='Длина имени не должна превышать 150 символов.'
            ),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Неверный формат имени.'
            )
        ]
    )
    first_name = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(
                USER_MAX_LENGTH,
                message='Длина имени не должна превышать 150 символов.'
            ),
        ]
    )
    last_name = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(
                USER_MAX_LENGTH,
                message='Длина фамилии не должна превышать 150 символов.'
            ),
        ]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[
            MaxLengthValidator(
                USER_MAX_LENGTH,
                message='Длина пароля не должна превышать 150 символов.'
            ),
        ]
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'id',

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя"""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.author_recipes.all()
        if limit:
            recipes = recipes[:int(limit)]

        return RecipeForUserSerializer(
            recipes,
            many=True,
        ).data

    def get_recipes_count(self, obj):
        return obj.author_recipes.count()

    def get_is_subscribed(self, obj):
        return True


class ChangePasswordSerializers(serializers.ModelSerializer):
    new_password = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                USER_MAX_LENGTH,
                message='Длина пароля не должна превышать 150 символов.'
            ),
        ]
    )
    current_password = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(
                USER_MAX_LENGTH,
                message='Длина пароля не должна превышать 150 символов.'
            ),
        ]
    )

    class Meta:
        model = User
        fields = (
            'new_password', 'current_password'
        )
