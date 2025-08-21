from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import CustomUser
from app_board.models import Board
from app_task.models import Task, TaskComment

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
        ("Login Details", {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("fullname",)}),
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
                "fields": ("email", "fullname", "password", "password2"),
            },
        ),
    )
    
    # Displayed fields in the list view
    list_display = ["email", "fullname", "is_staff"]
    
    # Fields you can search by
    search_fields = ["email", "fullname"]
    
    # Sorting standard
    ordering = ["email"]

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    ordering = ("id",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "status", "priority", "assignee", "reviewer", "due_date", "created_at", "updated_at")
    search_fields = ("title",)
    ordering = ("id",)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "task", "content")
    search_fields = ("author",)
    ordering = ("id",)
