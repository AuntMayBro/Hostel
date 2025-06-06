from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "email", ]
    list_filter = []
    fieldsets = [
        ('User Credentials', {"fields": ["email", "password"]}),
        ("Permissions", {"fields": []}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email","password",],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, UserModelAdmin)