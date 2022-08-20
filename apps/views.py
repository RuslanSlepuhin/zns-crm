import datetime
import random
import string

import time
from parsing_tg_chat import TgChat

from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from django.http import StreamingHttpResponse

import jwt

import psycopg2
from psycopg2 import OperationalError

from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication

from taggit.models import Tag

from .models import ContactsGF, ContactsUser, NewPerson, TelegramChatsView
from .serializers import ContactsUserSerializer, GetNewTokenSerializer, NewPersonSerializer, RegisterSerializer, \
    SetPullFromFrontendSerializer, UserAllSerializer, UserSerializer, ParsingTelegramSerializer, GetTelegramSerializer, \
    GiveNewTokenUserFaceBook

User = get_user_model()

li_seria = ["ContactsUserSerializer", "NewPersonSerializer", "RegisterSerializer", "UserSerializer"]


class NewQueryView(APIView):

    def post(self, request):
        dic_user = request.data  # получаем запрос в виде словаря
        name_class = ''
        for k, v in dic_user.items():  # проходим по словарю и достаем название таблицы
            if k == 'type' and v in li_seria:
                name_class = v
        # ищем созданную модель в models.py,
        # если есть сериализуем и добавляем в созданную таблицу
        if name_class:
            type_serial = eval(name_class)  # приводим строку к классу и подставляем в сериализатор
            serializer = type_serial(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User created',
                             'user': serializer.data})
        else:  # если нет в models  моделей, подключаемся к БД напрямую
            name_field = {}
            name_table = ''
            name_fielf_for_found = []
            list_fields_names = []
            for key, val in dic_user.items():
                if key == 'type':
                    name_table = val
                else:
                    if key != 'type':
                        # name_field[key] = name_field.get(key,'VARCHAR(100) UNIQUE')  # формируем и добавляем уникальные поля
                        name_field[key] = name_field.get(key, 'VARCHAR(100)')  # формируем и добавляем уникальные поля
                        name_fielf_for_found.append(key)
                        list_fields_names.append(val)  # формируем и добавляем значения ключа
            list_fields_names = tuple(list_fields_names)  # переводим в картеж для отправки в БД
            name_field['date'] = 'timestamp DEFAULT NOW()'
            now_time = datetime.datetime.now()
            list_fields_names = list_fields_names + (str(now_time),)

            def create_connection(db_name, db_user, db_password, db_host, db_port):  # подключаемся к БД
                connection = None
                try:
                    connection = psycopg2.connect(
                        database=db_name,
                        user=db_user,
                        password=db_password,
                        host=db_host,
                        port=db_port,
                    )
                    print('Connection to PosrgresQL DB successfull')
                except OperationalError as e:
                    print(f"The error '{e}' occurred")
                return connection

            # con = create_connection("ZNS", "postgres", "root", "127.0.0.1", "5432")
            con = create_connection("d12sstgavm83i7", "bfapmpbmvrnmvq",
                                    "70e2121db263e6c51275b817555daa63da3639fb415b29f96f269cee76ddc36e",
                                    "ec2-3-248-121-12.eu-west-1.compute.amazonaws.com", "5432")

            def check_name_db(connection):
                cursor = connection.cursor()
                # connection.autocommit = True
                # отправляем запрос в БД на получение всех таблиц
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')")
                find_name_inbd = ''
                for x in cursor:
                    if name_table in x:  # ищем таблицу в БД, если есть добавляем в find_name_inbd, если нет создаем новую
                        find_name_inbd = name_table
                print(f" DB {find_name_inbd} exists")
                if find_name_inbd:  # если таблица есть в БД, добавляем значения
                    try:
                        users = list_fields_names
                        result_field_update = ', '.join(f'{keys}' for keys, value in name_field.items())
                        user_records = ", ".join(["%s"] * len(users))
                        insert_query = (
                            f"INSERT INTO {name_table} ({result_field_update}) VALUES ({user_records})"
                        )
                        cursor.execute(insert_query, users)
                        connection.commit()
                        name_fielf_for_found_d = ', '.join(name_fielf_for_found)
                        insert_query_del = (f" DELETE FROM {name_table} WHERE id IN (SELECT id FROM"
                                            f" (SELECT id, ROW_NUMBER() OVER ("
                                            f" PARTITION BY {name_fielf_for_found_d} ORDER BY  id DESC)"
                                            f" AS rn FROM {name_table}) t"
                                            f" WHERE t.rn > 1)")

                        cursor.execute(insert_query_del)
                        connection.commit()
                        return Response({'message': 'Informations added'})
                    except OperationalError as e:
                        print(f"The error '{e}' occurred")
                else:  # если таблицы в БД нет, создаем новую и сразу запалняем ее значениями
                    try:
                        result_field = ', '.join(f'{keys} {value}' for keys, value in name_field.items())
                        query = f"CREATE TABLE IF NOT EXISTS {name_table} (id SERIAL PRIMARY KEY, {result_field})"
                        cursor.execute(query)
                        connection.commit()
                        users = list_fields_names
                        result_field_update = ', '.join(f'{keys}' for keys, value in name_field.items())
                        user_records = ", ".join(["%s"] * len(users))
                        insert_query = (
                            f"INSERT INTO {name_table} ({result_field_update}) VALUES ({user_records})"
                        )
                        cursor.execute(insert_query, users)
                        connection.commit()
                        return Response({'message': f' Table {name_table} created, informations added'})
                    except OperationalError as e:
                        print(f"The error '{e}' occurred")
                    finally:
                        if connection:
                            cursor.close()
                            connection.close()
                            return f"Соединение с PostgreSQL закрыто"

            check_name_db(con)
            return Response({'complete': f'Informations added'})


class DashboardUserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        if IsAuthenticated:
            id_user = User.objects.get(id=self.request.user.id)
            return User.objects.filter(email=id_user)


class ContactsUsersView(viewsets.ModelViewSet):
    serializer_class = ContactsUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        if IsAuthenticated:
            id_user = User.objects.get(id=self.request.user.id)
            return ContactsUser.objects.filter(iduserCreator=id_user)


class TagDetailView(generics.ListAPIView):
    serializer_class = ContactsUserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        if IsAuthenticated:
            id_user = User.objects.get(id=self.request.user.id)
            tag_slug = self.kwargs['tag_slug'].lower()
            tag = Tag.objects.get(slug=tag_slug)
            return ContactsUser.objects.filter(iduserCreator=id_user, tags=tag)


def main(request):
    return HttpResponse("It's work")


class NewPersonViewsets(viewsets.ModelViewSet):
    queryset = NewPerson.objects.all().order_by('first_name')
    serializer_class = NewPersonSerializer
    lookup_field = 'first_name'


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # user = serializer.save()
        return Response({
            # "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно создан",
            'data': serializer.data
        })


class AllUsersViewsets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ------------- to view all contacts from google and facebook ----------
# url/view/  show all contacts from table ContactsGF
class AllContactsGFView(APIView):
    serializer_class = UserAllSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = ContactsGF.objects.filter()
        return Response({'all users': UserAllSerializer(queryset, many=True).data})


# -------------add contacts from google and facebook -----------
# <url>/contacts-google-facebook/
class ContactsGoogleFacebookView(APIView):
    queryset = ContactsGF.objects.all()
    serializer_class = SetPullFromFrontendSerializer
    permission_classes = [permissions.AllowAny]

    # def get(self, request):
    #     queryset = ContactsGF.objects.all()
    #     return Response({'all contacts': SetPullFromFrontendSerializer(queryset, many=True).data})

    def post(self, request):
        serializer = SetPullFromFrontendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_email = request.data['id_email']
        contacts = request.data['contacts']
        type_contact = request.data['type_contact']

        if type_contact not in ['google', 'facebook']:  # проверка на валидность поля из запроса
            return Response({"error type": "type of contact must be 'google' or 'facebook'"})

        get_user_model()
        user = User.objects.filter(email=id_email)  # проверка существует ли такой user

        if user:
            id_queryset_user = User.objects.values('id').get(email=id_email)['id']  # id user'a по email

            # получить все контакты у этого user'а по type из request'а
            contacts_list = ContactsGF.objects.filter(
                id_user_creator_id=id_queryset_user,
                type_contact=type_contact,
            ).values_list('contacts')

            for i in contacts_list:  # проверка на совпадение contacts из request с существующими contacts
                if contacts in i:
                    return Response({'message': 'contact exists already'})

            new_post = ContactsGF.objects.create(
                id_user_creator_id=id_queryset_user,
                contacts=contacts,
                type_contact=type_contact
            )
            return Response({'new post': SetPullFromFrontendSerializer(new_post).data})

        else:
            return Response({'message': f'user {id_email} does not exist'})


# ------- issue token for user from google -----------------
class GetGoogleTokenView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def getRandomNumKey(self):
        num = 9
        a = string.ascii_letters + string.digits  # Источник данных: a-z, A-Z, 0-9
        key = random.sample(a, num)
        keys = "".join(key)
        return keys

    def post(self, request, *args, **kwargs):

        token = request.data["token"]
        decoded = jwt.decode(token, options={"verify_signature": False})
        email = decoded['email']
        username = decoded['name']
        
        try:
            password = decoded['sid']
        except Exception:
            password = self.getRandomNumKey()
            
        new_user = {
            'username': username,
            'email': email,
            'password': password
        }

        user = User.objects.filter(email=new_user['email'])

        if not user:

            serializer = self.get_serializer(data=new_user)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                "message": "Пользователь успешно создан",
                'data': serializer.data
            })

        else:

            user = User.objects.get(email=new_user['email'])

            return Response(
                {
                    'message': 'User exists already, use an pair token below',
                    'data': GetNewTokenSerializer(user).data
                }
            )


# --------------- Telegram parsing BeautifulSoup ------------------
class ParsingTelegramView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ParsingTelegramSerializer

    def get(self, request):

        start_time = time.time()

        while True:
            data = []
            content = TgChat()
            get_topics = content.get_content(number_of_page=6)

            print('number of articles = ', len(get_topics))

            # i = 1
            for item in get_topics:

                queryset = TelegramChatsView.objects.filter(title=str(item['title']))

                if not queryset:
                    serializer = self.get_serializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    data.append(serializer.data)
                # else:
                #     print(i, 'QuerySet exist already', f'\n{item["title"]}')
                #     i += 1
                # StreamingHttpResponse({'data': data})
            # return Response({'data': data})

            time.sleep(7200.0 - ((time.time() - start_time) % 7200.0))


class GetTelegramView(viewsets.ModelViewSet):
    queryset = TelegramChatsView.objects.all()
    serializer_class = GetTelegramSerializer
    permissions = [permissions.AllowAny]


class GetTokenFaceBook(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        email = decoded['email']
        password = 'secretId'
        new_user = {
            'email': email,
            'password': password
        }
        check_user_in_bd = User.objects.filter(email=email)
        if not check_user_in_bd:
            serializer = self.get_serializer(data=new_user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "message": "Пользователь успешно создан",
                'data': serializer.data
            })
        else:
            user = User.objects.get(email=new_user['email'])
            serializer = GiveNewTokenUserFaceBook(user)
            return Response({
                "message": "User exist already",
                'data': serializer.data
            })
