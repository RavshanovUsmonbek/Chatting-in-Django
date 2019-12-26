from django.contrib import admin

# Register your models here.
from chat.models import UserProfile, Group, Contact, Message

admin.site.register(UserProfile)
admin.site.register(Group)
admin.site.register(Contact)
admin.site.register(Message)