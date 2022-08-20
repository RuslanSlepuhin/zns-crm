from django.contrib import admin

from .models import ContactsGF, ContactsUser, NewPerson, User, TelegramChatsView

admin.site.register(NewPerson)
admin.site.register(User)
admin.site.register(ContactsUser)
admin.site.register(ContactsGF)
admin.site.register(TelegramChatsView)
