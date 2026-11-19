from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Log, Pass, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role Management", {"fields": ("role",)}),)
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")


@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ("pass_id", "user", "department", "out_time", "return_time", "status")
    list_filter = ("status", "department", "out_time")
    search_fields = ("pass_id", "user__username", "department", "purpose")
    readonly_fields = ("pass_id", "created_at", "updated_at")
    actions = ("approve_selected_passes", "reject_selected_passes")

    @admin.action(description="Approve selected passes")
    def approve_selected_passes(self, request, queryset):
        queryset.update(status=Pass.Status.APPROVED)

    @admin.action(description="Reject selected passes")
    def reject_selected_passes(self, request, queryset):
        queryset.update(status=Pass.Status.REJECTED)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("gate_pass", "entry_time", "exit_time", "created_at")
    search_fields = ("gate_pass__pass_id", "gate_pass__user__username")
    list_filter = ("created_at",)


admin.site.site_header = "Gate Pass Management Admin"
admin.site.site_title = "Gate Pass Admin"
admin.site.index_title = "Control Center"
