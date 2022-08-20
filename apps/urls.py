from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from rest_framework_swagger.views import get_swagger_view  # django rest swagger

# from . import views
from .views import AllContactsGFView, AllUsersViewsets, ContactsGoogleFacebookView, ContactsUsersView, \
    DashboardUserView, GetGoogleTokenView, NewPersonViewsets, NewQueryView, RegisterView, TagDetailView, \
    ParsingTelegramView, main, GetTelegramView, GetTokenFaceBook

# ------------- yasg swagger -----------------
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# ---------- end yasg swagger -----------------


router = routers.DefaultRouter()
router.register('person', NewPersonViewsets, basename='person')
router.register('allusers', AllUsersViewsets, basename='allusers')
router.register('contact', ContactsUsersView, basename='contact')
router.register('dashboarduser', DashboardUserView, basename='dashboarduser')


# schema_view = get_schema_view(
#    openapi.Info(
#       title="Django API",
#       default_version='v1',
#       description="Test description",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="contact@snippets.local"),
#       license=openapi.License(name="ZNS License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )
#




urlpatterns = [
                  path('', include(router.urls)),
                  path("contact/tags/<slug:tag_slug>/", TagDetailView.as_view()),
                  # set contacts from request from google and facebook
                  path('contacts-google-facebook/', ContactsGoogleFacebookView.as_view()),
                  path('view/', AllContactsGFView.as_view()),  # view all users from google and facebook
                  path('auth/', include('djoser.urls')),  # auth by email
                  path('auth/', include('djoser.urls.jwt')),  # auth by email
                  path('auth/', include('rest_framework.urls')),
                  path('', main, name='main'),
                  path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
                  path('register/', RegisterView.as_view()),
                  path('test/', NewQueryView.as_view()),
                  path("ckeditor/", include('ckeditor_uploader.urls')),
                  path('gtoken/', GetGoogleTokenView.as_view()),  # обработать google token
                  path('gettokenfb/', GetTokenFaceBook.as_view()),
                  path('post-telegram-channel/', ParsingTelegramView.as_view()),  # записать новости из телеграм канала
                  path('get-telegram/', GetTelegramView.as_view({'get': 'list'})),  # просмотреть все записи из телеграм
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ----------------------- yasg swagger ----------------------
# url_swagger = [
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#     ]
# -------------------- end yasg swagger ----------------------
# ----------------------- django rest swagger ----------------------
schema_view2 = get_swagger_view(title='Pastebin API')

url_django_swagger = [
    path('swagger/', schema_view2),
]
# -------------------- end django rest swagger ----------------------

# urlpatterns += url_swagger
urlpatterns += url_django_swagger
