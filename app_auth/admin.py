from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import CustomUser

# Clean the admin interface by removing the default registration form
# could be needed in some configurations
# admin.site.unregister(User)

@admin.register(CustomUser)
class CustomUserAdmin(auth_admin.UserAdmin):
    """
    A customized Admin-Configuration for the CustomUser model.
    """
    # Fields for the edit and detail view of the CustomUser model.
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    # Fields for registration / new User
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password", "password2"),
            },
        ),
    )
    
    # Displayed fields in the list view
    list_display = ["email", "first_name", "last_name", "is_staff"]
    
    # Fields you can search by
    search_fields = ["email", "first_name", "last_name"]
    
    # Sorting standard
    ordering = ["email"]