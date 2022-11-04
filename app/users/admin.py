"""
Django admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('name_en', 'name_uk', 'email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


class ProfileAdmin(admin.ModelAdmin):
    """Define the admin pages for profiles."""
    ordering = ['id']
    list_display = ['get_user_email', 'bio', 'short_desc', 'image']
    fieldsets = (
        (
            None,
            {'fields': ('id', 'get_user_email', 'bio_en', 'bio_uk',
                        'short_desc_en', 'short_desc_uk', 'image'
                        )}
        ),

    )
    readonly_fields = ['id', 'get_user_email']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'email'


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
