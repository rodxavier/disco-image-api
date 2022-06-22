from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Plan, User

UserAdmin.list_display += ("plan",)
UserAdmin.fieldsets += (("Plan", {"fields": ("plan",)}),)


class PlanAdmin(admin.ModelAdmin):
    filter_horizontal = ["presets"]


admin.site.register(Plan, PlanAdmin)
admin.site.register(User, UserAdmin)
