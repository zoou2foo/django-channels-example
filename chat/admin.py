from django.contrib import admin
from chat.models import Room, Message

# Register your models here.
# when registered, they are accessible from Django admin panel.


admin.site.register(Room)
admin.site.register(Message)