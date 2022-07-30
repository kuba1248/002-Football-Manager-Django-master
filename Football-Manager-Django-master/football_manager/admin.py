from django.contrib import admin
from .models import User, Club, Player, Transfer, Transfer_Archived, UserManager, PlayerManager, TransferManager


# Register your models here.
admin.site.register(User)
admin.site.register(Club)
admin.site.register(Player)
admin.site.register(Transfer)
admin.site.register(Transfer_Archived)
