from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Plan, User

UserAdmin.list_display += ("plan",)
UserAdmin.fieldsets += (("Plan", {"fields": ("plan",)}),)


admin.site.register(Plan)
admin.site.register(User, UserAdmin)
