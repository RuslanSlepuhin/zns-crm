from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken

from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import ContactsGF, ContactsUser, NewPerson, OtherPerson, TelegramChatsView

User = get_user_model()


class ContactsUserSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    # id_user_creator = serializers.SlugRelatedField(
    # slug_field="id",
    # queryset=User.objects.all())
    id_user_creator = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ContactsUser
        fields = ('id', 'first_name', 'last_name', 'phone', 'email', 'photo', 'notes', 'id_user_creator', 'tags')
        # extra_kwargs = {"photo": {"read_only": True}}


class NewPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewPerson
        fields = ('id', 'first_name', 'last_name', 'email', 'work_experience')
        lookup_field = 'first_name'
        extra_kwargs = {
            'url': {'lookup_field': 'first_name'}
        }


class RegisterSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        read_only_fields = ['username']
        fields = [
            "email",
            "password",
            "token",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        if not password:
            raise serializers.ValidationError({"password": "Введите пароль"})
        user = User(email=email)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(TaggitSerializer, serializers.ModelSerializer):
    email = serializers.EmailField(required=True, trim_whitespace=True)
    tags = TagListSerializerField()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'second_name',
                  'phone',
                  'sub_phone',
                  'explanation_by_phone',
                  'email',
                  'sub_email',
                  'explanation_by_email',
                  'website',
                  'tags',
                  'event_birthday',
                  'location',
                  'life_work',
                  'education',
                  'soc_network',
                  )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['email', 'password']


# ------------- to view all contacts from google and facebook ----------
class UserAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsGF
        fields = '__all__'


# -------------add contacts from google and facebook -----------
class SetPullFromFrontendSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsGF
        fields = [
            # 'id_email',
            'contacts',
            'type_contact'
        ]

    def create(self, validated_data):
        get_user_model()
        return ContactsGF.objects.create(**validated_data)


class OtherPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherPerson
        fields = '__all__'


# -------Get token for existing user -----------
class GetNewTokenSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "token"
        ]

    def get_token(self, user):
        user = User.objects.get(email=user.email)
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# --------------- Telegram parsing BeautifulSoup ------------------
class ParsingTelegramSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChatsView
        fields = '__all__'
        #
        # def create(self, validated_data):
        #     # title = validated_data['title']
        #     # TelegramChats.objects.filter(title=title)
        #     # queryset = TelegramChats.objects.filter(title=title)
        #     # if not queryset:
        #     return TelegramChats.objects.create(**validated_data)


class GetTelegramSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChatsView
        fields = '__all__'


class GiveNewTokenUserFaceBook(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "token",
        ]

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
