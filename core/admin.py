from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TimeEntry, TimePeriod, PTOEntry, PTOPolicy, EntryCategory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "is_superuser"]
    list_filter = ["is_staff", "is_superuser"]
    search_fields = ["username", "email"]
    ordering = ["username"]
    filter_horizontal = []
    fieldsets = BaseUserAdmin.fieldsets + (("Profile", {"fields": ("timezone",)}),)


class TimePeriodInline(admin.TabularInline):
    model = TimePeriod
    extra = 0


@admin.register(EntryCategory)
class EntryCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "name", "color"]
    search_fields = ["name", "user__username"]
    raw_id_fields = ["user"]


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "category", "date", "description", "completed", "total_seconds", "created_at"]
    list_filter = ["date", "completed"]
    search_fields = ["description", "user__username"]
    raw_id_fields = ["user", "category"]
    inlines = [TimePeriodInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PTOEntry)
class PTOEntryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "date", "type", "notes", "created_at"]
    list_filter = ["type", "date"]
    search_fields = ["user__username", "notes"]
    raw_id_fields = ["user"]


@admin.register(PTOPolicy)
class PTOPolicyAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "vacation_days", "sick_days", "personal_days"]
    list_filter = ["year"]
